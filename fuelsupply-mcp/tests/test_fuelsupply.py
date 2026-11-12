import json

import httpx
import pytest
from pydantic import ValidationError

from fuelsupply.analytics import inventory_coverage, reconcile, seasonal_comparison
from fuelsupply.cache import Cache
from fuelsupply.eia_client import EIAClient, EIAError
from fuelsupply.models import Query
from fuelsupply.normalization import normalize, number
from fuelsupply.service import SupplyService
from tests.fuel_fixtures import FAKE_KEY, binding


@pytest.mark.parametrize("value", [None, "W", "--", "NA", "NaN", "inf", "invalid", ""])
def test_missing_numeric(value):
    assert number(value) is None


def test_numeric_and_calendar_conversion():
    assert number("12.5") == 12.5
    assert normalize("290", "Thousand Barrels", "2024-02", "monthly", "flow") == (
        10,
        "Thousand Barrels per Day",
        None,
    )
    assert normalize("310", "Thousand Barrels", "2025-01", "monthly", "stock") == (
        310,
        "Thousand Barrels",
        None,
    )
    assert normalize(5, "gallons", "2025-01", "monthly", "stock")[0] is None


@pytest.mark.parametrize(
    "value,units,period,frequency,classification,expected",
    [
        (
            "99259",
            "MBBL",
            "2026-10-30",
            "weekly",
            "stock",
            (99259, "Thousand Barrels", None),
        ),
        (
            "4439",
            "MBBL/D",
            "2026-10-30",
            "weekly",
            "flow",
            (4439, "Thousand Barrels per Day", None),
        ),
        (
            "290",
            "MBBL",
            "2024-02",
            "monthly",
            "flow",
            (10, "Thousand Barrels per Day", None),
        ),
        ("310", "MBBL", "2025-01", "monthly", "stock", (310, "Thousand Barrels", None)),
    ],
)
def test_eia_api_unit_codes(value, units, period, frequency, classification, expected):
    assert normalize(value, units, period, frequency, classification) == expected


@pytest.mark.parametrize(
    "stock,demand,compatible",
    [(5, 0, True), (5, -1, True), (None, 2, True), (5, 2, False)],
)
def test_invalid_coverage(stock, demand, compatible):
    assert inventory_coverage(stock, demand, compatible)["value"] is None


def test_valid_coverage():
    assert inventory_coverage(100, 5, True)["value"] == 20


def test_balance_residual_and_missing():
    c = dict(
        production=100,
        imports=20,
        net_receipts=10,
        exports=5,
        stock_change=5,
        product_supplied=120,
        other_supply=0,
        other_disposition=0,
    )
    assert reconcile(c)["status"] == "reconciled"
    c["exports"] = 6
    assert reconcile(c)["residual"] == -1
    del c["other_supply"]
    assert reconcile(c)["status"] == "insufficient_components"


async def test_monthly_balance_does_not_hide_missing_credentials():
    service = SupplyService(
        bindings=[binding(frequency="monthly")], client=EIAClient(key="")
    )
    out = await service.run(Query(fuel="distillate", frequency="monthly"), "balance")
    assert out.status == "error"
    assert not out.observation_periods
    assert out.calculations[0]["status"] == "insufficient_components"
    assert any("missing_credentials" in x for x in out.data_quality_diagnostics)


def test_seasonal_history_and_week53():
    result = seasonal_comparison({"2020-12-31": 100}, "2026-12-31", "weekly")
    assert result["status"] == "insufficient_history"
    assert "53" in result["week_53_handling"]
    result = seasonal_comparison(
        {"2023-02": 100, "2024-02": 120, "2025-02": 110}, "2026-02", "monthly"
    )
    assert result["mean"] == 110 and result["sample_size"] == 3


@pytest.mark.parametrize(
    "update",
    [
        {"lookback_periods": 261},
        {"geography": "airport"},
        {"frequency": "daily"},
        {"observation_cutoff": "not-a-date"},
        {"url": "https://evil.invalid"},
    ],
)
def test_query_validation(update):
    with pytest.raises(ValidationError):
        Query.model_validate({"fuel": "distillate", **update})


@pytest.mark.parametrize(
    "route",
    [
        "https://evil.invalid/",
        "../data/",
        "petroleum/../data/",
        "petroleum/test/data/?key=secret",
    ],
)
def test_route_validation(route):
    with pytest.raises(ValidationError):
        binding().model_copy(update={"route": route}).__class__.model_validate(
            {**binding().model_dump(), "route": route}
        )


def test_cache_bounded_expiration_and_copy():
    c = Cache(capacity=1)
    c.put("a", {"x": 1})
    value = c.get("a")
    value["x"] = 9
    assert c.get("a")["x"] == 1
    c.put("b", {})
    assert c.get("a") is None
    c.ttl = 0
    assert c.get("b") is None


async def test_pagination_and_cache():
    requests = []

    def handler(request):
        requests.append(request)
        offset = int(request.url.params["offset"])
        count = 100 if offset == 0 else 20
        return httpx.Response(
            200,
            json={
                "response": {
                    "total": 120,
                    "data": [
                        {"period": f"p{n:03}", "value": "2"}
                        for n in range(offset, offset + count)
                    ],
                }
            },
        )

    c = EIAClient(FAKE_KEY, httpx.MockTransport(handler))
    b = binding()
    result = await c.fetch(b, limit=120)
    assert len(result["rows"]) == 120 and len(requests) == 2
    assert (await c.fetch(b, limit=120))["mode"] == "cached"
    assert FAKE_KEY not in json.dumps(result)


async def test_retry_rate_limit():
    statuses = iter([429, 503, 200])
    c = EIAClient(
        FAKE_KEY,
        httpx.MockTransport(
            lambda r: httpx.Response(
                next(statuses),
                headers={"Retry-After": "0"},
                json={"response": {"total": 0, "data": []}},
            )
        ),
    )
    await c.fetch(binding())
    assert c.request_count == 3


@pytest.mark.parametrize("status", [400, 401, 403, 302, 500])
async def test_no_retry_and_redaction(status):
    c = EIAClient(
        FAKE_KEY, httpx.MockTransport(lambda r: httpx.Response(status, text=FAKE_KEY))
    )
    with pytest.raises(EIAError) as error:
        await c.fetch(binding())
    assert FAKE_KEY not in str(error.value) and c.request_count == 1


async def test_long_retry_after():
    c = EIAClient(
        FAKE_KEY,
        httpx.MockTransport(
            lambda r: httpx.Response(429, headers={"Retry-After": "60"})
        ),
    )
    with pytest.raises(EIAError, match="retry_later"):
        await c.fetch(binding())
    assert c.request_count == 1


@pytest.mark.parametrize(
    "payload,expected",
    [
        (
            {"response": {"data": [{"period": "x"}, {"period": "x"}], "total": 2}},
            "duplicate",
        ),
        ({"error": "secret"}, "schema"),
        ({"response": {"data": [], "total": 10}}, "pagination"),
    ],
)
async def test_bad_response(payload, expected):
    c = EIAClient(
        FAKE_KEY, httpx.MockTransport(lambda r: httpx.Response(200, json=payload))
    )
    with pytest.raises(EIAError, match=expected):
        await c.fetch(binding())


async def test_missing_key():
    with pytest.raises(EIAError, match="missing_credentials"):
        await EIAClient("").fetch(binding())


@pytest.mark.parametrize("fuel", ["diesel", "gasoline", "jet"])
async def test_product_ambiguity(fuel):
    assert (
        await SupplyService(bindings=[]).run(Query(fuel=fuel))
    ).status == "needs_clarification"


async def test_empty_coverage_and_weekly_balance():
    s = SupplyService(bindings=[])
    assert (await s.run(Query(fuel="distillate"))).status == "blocked"
    assert (await s.run(Query(fuel="distillate"), "balance")).status == "unsupported"


async def test_alignment_missing_stale_and_units():
    class Client:
        async def fetch(self, b, *args):
            return {
                "mode": "live",
                "retrieved_at": "2026-11-11T00:00:00Z",
                "rows": [
                    {
                        "period": "2020-01-03"
                        if b.internal_metric_id == "stocks"
                        else "2020-01-10",
                        "value": "W" if b.internal_metric_id == "imports" else "20",
                        "units": b.units,
                    }
                ],
            }

    bindings = [binding(k) for k in ["stocks", "product_supplied", "imports"]]
    out = await SupplyService(Client(), bindings).run(
        Query(fuel="distillate"), "inventory"
    )
    assert out.status == "partial" and out.calculations[0]["value"] is None
    assert any("unaligned" in d for d in out.data_quality_diagnostics)
    assert any("stale" in d for d in out.data_quality_diagnostics)
    assert any("missing" in d for d in out.data_quality_diagnostics)


async def test_bounded_pagination():
    counter = 0

    def handler(request):
        nonlocal counter
        counter += 1
        return httpx.Response(
            200, json={"response": {"total": 10000, "data": [{"period": str(counter)}]}}
        )

    c = EIAClient(FAKE_KEY, httpx.MockTransport(handler))
    with pytest.raises(EIAError, match="pagination_limit"):
        await c.fetch(binding(), limit=260)
    assert c.request_count == 3


async def test_bounded_concurrency():
    import asyncio

    active = peak = 0

    async def handler(request):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        return httpx.Response(200, json={"response": {"total": 0, "data": []}})

    c = EIAClient(FAKE_KEY, httpx.MockTransport(handler))
    await asyncio.gather(*(c.fetch(binding(), limit=n) for n in range(1, 7)))
    assert peak == 2


async def test_retry_exhaustion_and_timeout_redaction():
    def handler(request):
        raise httpx.ReadTimeout(FAKE_KEY)

    c = EIAClient(FAKE_KEY, httpx.MockTransport(handler))
    with pytest.raises(EIAError) as error:
        await c.fetch(binding())
    assert c.request_count == 3 and FAKE_KEY not in str(error.value)


async def test_incompatible_units_and_cutoff():
    class Client:
        async def fetch(self, b, *args):
            return {
                "mode": "live",
                "retrieved_at": "2026-11-11T00:00:00Z",
                "rows": [{"period": "2026-11-06", "value": "100", "units": "gallons"}],
            }

    s = SupplyService(Client(), [binding()])
    out = await s.run(Query(fuel="distillate"))
    assert "incompatible_units:stocks" in out.data_quality_diagnostics
    assert not out.observation_periods
    out = await s.run(Query(fuel="distillate", observation_cutoff="2026-01-01"))
    assert not out.observation_periods


async def test_oversized_response_is_rejected():
    c = EIAClient(
        FAKE_KEY,
        httpx.MockTransport(
            lambda r: httpx.Response(200, content=b"x" * (2 * 1024 * 1024 + 1))
        ),
    )
    with pytest.raises(EIAError, match="too_large"):
        await c.fetch(binding())
