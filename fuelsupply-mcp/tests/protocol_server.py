"""Synthetic subprocess integration fixture. NEVER use for market briefings."""

import httpx

from fuelsupply.app import main, mcp
from fuelsupply.eia_client import EIAClient
from fuelsupply.service import service
from tests.fuel_fixtures import FAKE_KEY, binding

metrics = [
    "production",
    "stocks",
    "product_supplied",
    "imports",
    "exports",
    "net_receipts",
    "stock_change",
    "other_supply",
    "other_disposition",
]
service.bindings = [
    binding(k, f, g)
    for k in metrics
    for f, g in [("weekly", "US"), ("monthly", "PADD1")]
]


def handler(request):
    end = request.url.params.get("end", "")
    if end == "2001-01-01":
        return httpx.Response(401, text=FAKE_KEY)
    if end == "2002-01-01":
        return httpx.Response(429, headers={"Retry-After": "60"}, text=FAKE_KEY)
    period = "2026-10" if request.url.params["frequency"] == "monthly" else "2026-11-06"
    if end in {"2003-01-01", "2004-01-01", "2005-01-01", "2006-01-01"}:
        period = (
            "2000-01" if request.url.params["frequency"] == "monthly" else "2000-01-07"
        )
    value = "W" if end == "2004-01-01" else "0" if end == "2005-01-01" else "100"
    # Synthetic series use a metric facet to select units.
    metric = request.url.params.get("facets[metric][]")
    if not end and metric == "exports":
        value = "110"
    units = "Thousand Barrels" if metric == "stocks" else "Thousand Barrels per Day"
    if end == "2006-01-01":
        units = "gallons"
    return httpx.Response(
        200,
        json={
            "response": {
                "total": 1,
                "data": [{"period": period, "value": value, "units": units}],
            }
        },
    )


for b in service.bindings:
    b.facets["metric"] = [b.internal_metric_id]
service.client = EIAClient(FAKE_KEY, httpx.MockTransport(handler))


@mcp.resource("test://request-count")
def request_count() -> str:
    return str(service.client.request_count)


main()
