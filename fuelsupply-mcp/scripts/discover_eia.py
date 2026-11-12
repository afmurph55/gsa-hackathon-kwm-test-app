"""Operator-only bounded metadata inspection; no catalog crawl or promotion."""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

from fuelsupply.config import settings

logging.getLogger("httpx").setLevel(logging.CRITICAL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "route",
        help="Exact petroleum metadata route discovered from parent; start petroleum/",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"petroleum/(?:[a-z0-9-]+/)*", args.route):
        parser.error("Only relative petroleum metadata routes are permitted")
    key = settings.eia_api_key.get_secret_value()
    if not key:
        print("BLOCKED: configure EIA_API_KEY in environment", file=sys.stderr)
        return 2
    try:
        with httpx.Client(timeout=20, follow_redirects=False) as client:
            response = client.get(
                "https://api.eia.gov/v2/" + args.route, params={"api_key": key}
            )
            if response.status_code != 200:
                print(
                    f"Metadata unavailable: HTTP {response.status_code}",
                    file=sys.stderr,
                )
                return 2
            # Discard API request echoes; never persist arbitrary upstream strings.
            data = response.json()["response"]

            def clean(value):
                if isinstance(value, dict):
                    return {
                        k: clean(v)
                        for k, v in value.items()
                        if k.lower() not in {"api_key", "request", "request_url"}
                    }
                if isinstance(value, list):
                    return [clean(v) for v in value[:500]]
                if isinstance(value, str):
                    return value.replace(key, "[REDACTED]")
                return value

            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(
                    {
                        "route": args.route,
                        "retrieved_at": datetime.now(timezone.utc).isoformat(),
                        "metadata": clean(data),
                    },
                    indent=2,
                )
            )
    except (httpx.HTTPError, ValueError, KeyError):
        print("Metadata retrieval failed; upstream details suppressed", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
