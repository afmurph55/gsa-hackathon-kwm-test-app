"""Bounded fixed-origin EIA access; never return upstream exception text."""

import asyncio
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from fuelsupply.cache import Cache
from fuelsupply.config import settings
from fuelsupply.models import Binding


# Only controlled diagnostic messages should cross this exception boundary.
class EIAError(Exception):
    pass


class EIAClient:
    # Network adapter: fetch one verified series at a time, with bounded work,
    # per-instance caching and no exposure of raw upstream errors to callers.
    def __init__(self, key=None, transport=None):
        # Optional transport/key injection supports synthetic tests without real
        # EIA traffic. Production takes the credential from server settings.
        self.key = settings.eia_api_key.get_secret_value() if key is None else key
        self.transport = transport
        self.cache = Cache()
        self.gate = asyncio.Semaphore(2)
        self.request_count = 0

    async def fetch(self, binding: Binding, cutoff=None, limit=12):
        # Return newest-first raw rows, retrieval time and live/cached mode.
        # Unit conversion and analytical interpretation belong to the service.
        if not 1 <= limit <= 260:
            raise EIAError("invalid_limit")
        # The verified binding supplies the route/facets; callers choose only
        # the observation cutoff and bounded history, never an arbitrary URL.
        params = {
            "frequency": binding.frequency,
            "data[0]": binding.value_column,
            "sort[0][column]": "period",
            "sort[0][direction]": "desc",
            "length": min(limit, 100),
        }
        for facet, values in binding.facets.items():
            params[f"facets[{facet}][]"] = values
        if cutoff:
            params["end"] = str(cutoff)
        # Include the binding and query window, but never credentials, in the
        # cache identity. Cache hits preserve the original retrieval timestamp.
        cache_key = json.dumps(
            [binding.model_dump(mode="json"), params, limit], sort_keys=True
        )
        cached = self.cache.get(cache_key)
        if cached:
            return {**cached, "mode": "cached"}
        if not self.key:
            raise EIAError("missing_credentials: configure EIA_API_KEY server-side")
        rows, seen, offset = [], set(), 0
        async with self.gate:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(20, connect=5),
                follow_redirects=False,
                transport=self.transport,
            ) as client:
                # At most three 100-row pages cover the 260-observation limit.
                # Duplicate periods are errors because one binding must resolve
                # to a single observation per period, not mixed series.
                for _ in range(3):
                    params["offset"] = offset
                    params["api_key"] = self.key
                    response = await self._request(client, binding.route, params)
                    try:
                        payload = response.json()["response"]
                        page = payload["data"]
                        total = int(payload["total"])
                        if not isinstance(page, list) or len(page) > 100 or total < 0:
                            raise ValueError()
                        for row in page:
                            period = row["period"]
                            if not isinstance(period, str) or len(period) > 10:
                                raise ValueError()
                            if period in seen:
                                raise EIAError("duplicate_observation")
                            seen.add(period)
                            rows.append(row)
                    except EIAError:
                        raise
                    except (KeyError, ValueError, TypeError):
                        raise EIAError("invalid_response_schema") from None
                    offset += len(page)
                    if len(rows) >= limit or offset >= total:
                        break
                    if not page:
                        raise EIAError("incomplete_pagination")
                else:
                    raise EIAError("pagination_limit_exceeded")
        result = {
            "rows": sorted(rows, key=lambda x: x["period"], reverse=True)[:limit],
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "mode": "live",
        }
        self.cache.put(cache_key, result)
        return result

    async def _request(self, client, route, params):
        # Issue one page request, applying transport retries and response bounds.
        # fetch() handles pagination; this method handles individual HTTP calls.
        # Revalidate even if an operator bypasses normal model construction.
        import re

        if not re.fullmatch(r"petroleum/(?:[a-z0-9-]+/)+data/", route):
            raise EIAError("invalid_route")
        for attempt in range(3):
            try:
                self.request_count += 1
                request = client.build_request(
                    "GET", "https://api.eia.gov/v2/" + route, params=params
                )
                streamed = await client.send(request, stream=True)
                # Stream with a size cap before JSON parsing to bound memory.
                body = bytearray()
                try:
                    async for chunk in streamed.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > 2 * 1024 * 1024:
                            raise EIAError("upstream_response_too_large")
                    response = httpx.Response(
                        streamed.status_code,
                        headers={
                            "Retry-After": streamed.headers.get("Retry-After", "0.1")
                        },
                        content=bytes(body),
                    )
                finally:
                    await streamed.aclose()
            except httpx.HTTPError:
                # HTTP exceptions can contain credential-bearing URLs. Replace
                # them with fixed diagnostics and suppress the exception chain.
                if attempt < 2:
                    await asyncio.sleep(0.1 * (2**attempt))
                    continue
                raise EIAError("upstream_transport_failure") from None
            # Retry only transient statuses, within three attempts and a local
            # wait budget. Honor short Retry-After values in either HTTP format.
            if response.status_code in (429, 502, 503, 504) and attempt < 2:
                retry = response.headers.get("Retry-After", "0.1")
                try:
                    delay = max(0, float(retry))
                except ValueError:
                    try:
                        delay = max(
                            0,
                            (
                                parsedate_to_datetime(retry)
                                - datetime.now(timezone.utc)
                            ).total_seconds(),
                        )
                    except (ValueError, TypeError, OverflowError):
                        delay = 0.1
                if delay > 5:
                    raise EIAError("retry_later: Retry-After exceeds local wait budget")
                await asyncio.sleep(delay)
                continue
            if response.status_code != 200:
                raise EIAError(
                    f"upstream_http_{response.status_code}: "
                    "check credentials or retry later"
                )
            return response
        raise EIAError("upstream_retry_exhausted")
