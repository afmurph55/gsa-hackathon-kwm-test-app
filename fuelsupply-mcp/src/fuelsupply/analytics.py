"""Deterministic calculations; no causal claims or market forecasts."""

from fuelsupply.normalization import number


def inventory_coverage(stock, demand, compatible):
    s, d = number(stock), number(demand)
    if not compatible or s is None or d is None or s < 0 or d <= 0:
        return {"status": "insufficient_components", "value": None}
    return {
        "status": "ok",
        "value": s / d,
        "units": "days",
        ("formula"): (
            "stocks (thousand barrels) / product supplied (thousand barrels/day)"
        ),
        "kind": "custom_calculation",
        "limitation": "Not official EIA days of supply or a countdown to running out.",
    }


def reconcile(components):
    required = {
        "production",
        "imports",
        "net_receipts",
        "exports",
        "stock_change",
        "product_supplied",
        "other_supply",
        "other_disposition",
    }
    if not required <= components.keys() or any(
        number(components[k]) is None for k in required
    ):
        return {"status": "insufficient_components", "residual": None}
    c = {k: number(components[k]) for k in required}
    residual = (
        c["production"]
        + c["imports"]
        + c["net_receipts"]
        + c["other_supply"]
        - c["exports"]
        - c["stock_change"]
        - c["product_supplied"]
        - c["other_disposition"]
    )
    return {
        "status": "reconciled" if abs(residual) < 1e-6 else "residual_present",
        "residual": residual,
        ("formula"): (
            "production + imports + net_receipts + other_supply - exports"
            " - stock_change - product_supplied - other_disposition"
        ),
        "kind": "calculation",
    }


def seasonal_comparison(observations, target_period, frequency):
    from datetime import date

    target = date.fromisoformat(
        target_period if frequency == "weekly" else target_period + "-01"
    )
    key = target.isocalendar().week if frequency == "weekly" else target.month
    samples, years = [], []
    for period, value in observations.items():
        d = date.fromisoformat(period if frequency == "weekly" else period + "-01")
        same = (d.isocalendar().week if frequency == "weekly" else d.month) == key
        v = number(value)
        if target.year - 5 <= d.year < target.year and same and v is not None:
            samples.append(v)
            years.append(d.year)
    return {
        "status": "ok" if len(set(years)) >= 3 else "insufficient_history",
        "baseline_years": sorted(set(years)),
        "sample_size": len(samples),
        "baseline_window": [target.year - 5, target.year - 1],
        "missing_years": sorted(set(range(target.year - 5, target.year)) - set(years)),
        "week_53_handling": "match ISO week 53 only; never merge into week 52",
        "mean": sum(samples) / len(samples) if len(set(years)) >= 3 else None,
        "kind": "custom_calculation",
    }
