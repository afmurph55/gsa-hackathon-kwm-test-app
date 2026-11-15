# Observation conversion helpers: parse numeric values, resolve period ends,
# and normalize supported units without changing a series' product definition.
import calendar
import math
from datetime import date

MISSING = {"", "--", "NA", "W", "(s)", "null", "None"}


def number(value):
    # Missing, withheld and non-finite values stay unknown rather than becoming
    # zero, which would manufacture supply or distort a balance calculation.
    if value is None or str(value).strip() in MISSING:
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (ValueError, TypeError):
        return None


def period_end(period, frequency):
    # Monthly API labels omit the day; cutoffs apply to the full month's end.
    if frequency == "monthly":
        d = date.fromisoformat(period + "-01")
        return d.replace(day=calendar.monthrange(d.year, d.month)[1])
    return date.fromisoformat(period)


def normalize(value, units, period, frequency, classification):
    # Return (normalized value, display units, quality issue). The service keeps
    # original values too, allowing each conversion to be checked against EIA.
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
        # Only monthly flow totals become daily averages. Stock levels remain
        # period-end quantities, and already-daily flows are not divided again.
        return v / period_end(period, frequency).day, "Thousand Barrels per Day", None
    if units in {"Thousand Barrels", "Thousand Barrels per Day", "Percent"}:
        return v, units, None
    return None, units, "unsupported_units"
