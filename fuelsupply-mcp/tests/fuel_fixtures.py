"""SYNTHETIC data exclusively for testing; never installed as market mappings."""

from datetime import datetime, timezone

from fuelsupply.models import Binding

FAKE_KEY = "SYNTHETIC-SECRET-DO-NOT-LEAK"


def binding(metric="stocks", frequency="weekly", geography="US"):
    stock = metric == "stocks"
    return Binding(
        internal_metric_id=metric,
        fuel_family="distillate",
        product_definition="SYNTHETIC broad distillate",
        geography=geography,
        frequency=frequency,
        route="petroleum/test-only/data/",
        facets={"product": ["synthetic"]},
        units="Thousand Barrels" if stock else "Thousand Barrels per Day",
        classification="stock" if stock else "flow",
        period_convention="SYNTHETIC period end",
        observed_coverage=("2026-01", "2026-11"),
        verified_at=datetime.now(timezone.utc),
        source_url="https://www.eia.gov/",
        methodology_notes="SYNTHETIC TEST ONLY, NOT VERIFIED EIA MAPPING",
        verification_status="verified",
    )
