from datetime import date

from fuelsupply.analytics import inventory_coverage, reconcile, seasonal_comparison
from fuelsupply.eia_client import EIAClient, EIAError
from fuelsupply.models import Result
from fuelsupply.normalization import normalize, number, period_end
from fuelsupply.provenance import DEFINITIONS, LIMITATIONS
from fuelsupply.registry import load_registry


class SupplyService:
    def __init__(self, client=None, bindings=None):
        self.client = client or EIAClient()
        self.bindings = load_registry()[1] if bindings is None else bindings

    async def run(self, query, purpose="conditions"):
        out = Result(
            text="Market-level descriptive analysis",
            status="ok",
            geography=query.geography,
            limitations=LIMITATIONS.copy(),
            supported_follow_up_actions=[
                "discover_fuel_coverage",
                "Clarify exact product definition",
            ],
        )
        if query.fuel in {"diesel", "gasoline", "jet"}:
            out.status = "needs_clarification"
            out.text = {
                ("diesel"): (
                    "Choose broad distillate or ULSD; they are not interchangeable."
                ),
                "gasoline": "Choose finished_gasoline or gasoline_blending_components.",
                "jet": "Choose kerosene_jet or avgas; they are separate products.",
            }[query.fuel]
            return out
        out.resolved_product_definition = DEFINITIONS[query.fuel]
        if purpose == "balance" and query.frequency != "monthly":
            out.status, out.text = (
                "unsupported",
                "Regional balance requires monthly observations.",
            )
            return out
        selected = [
            b
            for b in self.bindings
            if (b.fuel_family, b.geography, b.frequency)
            == (query.fuel, query.geography, query.frequency)
        ]
        if len(selected) > 16:
            out.status, out.text = (
                "error",
                "Registry has too many metrics for one query.",
            )
            return out
        if not selected:
            out.status = "blocked" if not self.bindings else "unsupported"
            out.text = (
                "No verified mapping for this combination. Enable only after "
                "metadata and authenticated sample verification."
            )
            out.data_quality_diagnostics = [
                "No verified binding for the requested product/geography/frequency."
            ]
            return out
        definitions = {
            b.product_definition for b in selected if b.classification != "context"
        }
        if len(definitions) == 1:
            out.resolved_product_definition = next(iter(definitions))
        elif len(definitions) > 1:
            out.data_quality_diagnostics.append("incompatible_product_definitions")
        modes, periods, retrieved = set(), set(), []
        for b in selected:
            try:
                data = await self.client.fetch(
                    b, query.observation_cutoff, query.lookback_periods
                )
                modes.add(data["mode"])
                retrieved.append(data["retrieved_at"])
                observations = []
                for row in data["rows"]:
                    try:
                        end = period_end(row["period"], b.frequency)
                        if query.observation_cutoff and end > query.observation_cutoff:
                            continue
                        if row.get("units") != b.units:
                            out.data_quality_diagnostics.append(
                                "incompatible_units:" + b.internal_metric_id
                            )
                            continue
                        value, units, issue = normalize(
                            row.get(b.value_column),
                            b.units,
                            row["period"],
                            b.frequency,
                            b.classification,
                        )
                        if issue:
                            out.data_quality_diagnostics.append(
                                issue + ":" + b.internal_metric_id
                            )
                        observations.append(
                            {
                                "period": row["period"],
                                "value": value,
                                "units": units,
                                "original_value": number(row.get(b.value_column)),
                                "original_units": b.units,
                            }
                        )
                        periods.add(row["period"])
                        if (date.today() - end).days > (
                            21 if b.frequency == "weekly" else 120
                        ):
                            out.data_quality_diagnostics.append(
                                "stale_observation:" + row["period"]
                            )
                    except (ValueError, KeyError, TypeError):
                        out.data_quality_diagnostics.append("invalid_observation")
                out.metrics.append(
                    {
                        "metric": b.internal_metric_id,
                        "classification": b.classification,
                        "product_definition": b.product_definition,
                        "observations": observations,
                    }
                )
                out.source_bindings.append(b.model_dump(mode="json"))
            except EIAError as exc:
                out.data_quality_diagnostics.append(str(exc))
        out.observation_periods = sorted(periods, reverse=True)
        out.retrieval_timestamp = max(retrieved) if retrieved else None
        out.mode = "cached" if modes == {"cached"} else "live"
        out.data_quality_diagnostics.append(
            "retrieval_modes:" + ",".join(sorted(modes))
        )
        latest = {
            m["metric"]: m["observations"][0] for m in out.metrics if m["observations"]
        }
        if len({x["period"] for x in latest.values()}) > 1:
            out.data_quality_diagnostics.append(
                "unaligned_latest_periods: no synchronized balance"
            )
        if purpose == "inventory":
            s, d = latest.get("stocks"), latest.get("product_supplied")
            compatible = bool(
                s
                and d
                and s["period"] == d["period"]
                and s["units"] == "Thousand Barrels"
                and d["units"] == "Thousand Barrels per Day"
                and len(
                    {
                        b.product_definition
                        for b in selected
                        if b.internal_metric_id in {"stocks", "product_supplied"}
                    }
                )
                == 1
            )
            out.calculations.append(
                inventory_coverage(
                    s["value"] if s else None, d["value"] if d else None, compatible
                )
            )
            if s:
                stocks = next(m for m in out.metrics if m["metric"] == "stocks")
                out.calculations.append(
                    seasonal_comparison(
                        {x["period"]: x["value"] for x in stocks["observations"]},
                        s["period"],
                        query.frequency,
                    )
                )
        if purpose == "balance":
            aligned = (
                len({x["period"] for x in latest.values()}) == 1
                and len(definitions) == 1
            )
            flow = (
                {
                    k: x["value"]
                    for k, x in latest.items()
                    if x["units"] == "Thousand Barrels per Day"
                }
                if aligned
                else {}
            )
            out.calculations.append(reconcile(flow))
        required = {"production", "stocks", "product_supplied", "imports", "exports"}
        if purpose == "sourcing":
            required.add("net_receipts")
        if (
            not required <= latest.keys()
            or any(x["value"] is None for x in latest.values())
            or any(
                "unaligned" in x or "incompatible" in x or "upstream" in x
                for x in out.data_quality_diagnostics
            )
        ):
            out.status = "partial" if latest else "error"
        if (
            purpose == "balance"
            and out.status != "error"
            and out.calculations[0]["status"] != "reconciled"
        ):
            out.status = "partial"
        return out


service = SupplyService()
