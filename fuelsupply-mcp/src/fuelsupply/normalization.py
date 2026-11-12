import calendar
import math
from datetime import date

MISSING = {"", "--", "NA", "W", "(s)", "null", "None"}


def number(value):
    if value is None or str(value).strip() in MISSING:
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def period_end(period, frequency):
    if frequency == "monthly":
        d = date.fromisoformat(period + "-01")
        return d.replace(day=calendar.monthrange(d.year, d.month)[1])
    return date.fromisoformat(period)


def normalize(value, units, period, frequency, classification):
    v = number(value)
    if v is None:
        return None, units, "missing_or_withheld"
    # EIA API v2 uses codes; published tables spell out these same units.
    units = {
        "MBBL": "Thousand Barrels",
        "MBBL/D": "Thousand Barrels per Day",
    }.get(units, units)
    if (
        units == "Thousand Barrels"
        and classification == "flow"
        and frequency == "monthly"
    ):
        return v / period_end(period, frequency).day, "Thousand Barrels per Day", None
    if units in {"Thousand Barrels", "Thousand Barrels per Day", "Percent"}:
        return v, units, None
    return None, units, "unsupported_units"
