"""
GSA KWM2 MCP Toolkit — stdio transport
Three tools:
  gsa_kwm2_current_weather   — live weather via wttr.in (proves outbound internet)
  gsa_kwm2_programming_joke  — joke via official-joke-api (second internet proof)
  gsa_kwm2_unit_converter    — pure local arithmetic (no network)
"""

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gsa_kwm2")


# ---------------------------------------------------------------------------
# Tool 1 — Current weather
# ---------------------------------------------------------------------------

@mcp.tool()
def gsa_kwm2_current_weather(city: str) -> str:
    """Return the current weather for a city.

    Calls the wttr.in public JSON API (no key required) to retrieve live
    weather conditions.  Proves outbound internet access from the Orchestrate
    runtime.

    Args:
        city: The name of the city to look up, e.g. "London" or "New York".

    Returns:
        A one-line summary such as "London: 18°C, Partly cloudy", or an
        error string if the request fails.
    """
    if not city or not city.strip():
        return "Error fetching weather: city name must not be empty"
    try:
        url = f"https://wttr.in/{city.strip()}?format=j1"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "gsa-kwm2-mcp/1.0"})
        resp.raise_for_status()
        data = resp.json()
        cond = data["current_condition"][0]
        temp_c = cond["temp_C"]
        desc = cond["weatherDesc"][0]["value"]
        return f"{city}: {temp_c}°C, {desc}"
    except Exception as exc:
        return f"Error fetching weather: {exc}"


# ---------------------------------------------------------------------------
# Tool 2 — Programming joke
# ---------------------------------------------------------------------------

@mcp.tool()
def gsa_kwm2_programming_joke() -> str:
    """Fetch a random programming joke from a public API.

    Calls the Official Joke API (no key required) to retrieve a joke.
    Proves outbound internet access via a different public endpoint.

    Returns:
        A two-line string "Setup: <setup>\\nPunchline: <punchline>", or an
        error string if the request fails.
    """
    try:
        url = "https://official-joke-api.appspot.com/jokes/programming/random"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        # API returns a list with one joke object
        joke = payload[0] if isinstance(payload, list) else payload
        setup = joke["setup"]
        punchline = joke["punchline"]
        return f"Setup: {setup}\nPunchline: {punchline}"
    except Exception as exc:
        return f"Error fetching joke: {exc}"


# ---------------------------------------------------------------------------
# Tool 3 — Unit converter (local logic only)
# ---------------------------------------------------------------------------

# Conversion table: (from_unit, to_unit) -> (factor, offset)
# result = value * factor + offset
_CONVERSIONS: dict[tuple[str, str], tuple[float, float]] = {
    ("km", "miles"):       (0.621371, 0.0),
    ("miles", "km"):       (1.60934, 0.0),
    ("kg", "lbs"):         (2.20462, 0.0),
    ("lbs", "kg"):         (0.453592, 0.0),
    ("celsius", "fahrenheit"): (9 / 5, 32.0),
    ("fahrenheit", "celsius"): (5 / 9, -160 / 9),
    ("meters", "feet"):    (3.28084, 0.0),
    ("feet", "meters"):    (0.3048, 0.0),
    ("liters", "gallons"): (0.264172, 0.0),
    ("gallons", "liters"): (3.78541, 0.0),
}


@mcp.tool()
def gsa_kwm2_unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a value from one unit to another using local arithmetic.

    No network calls are made — demonstrates pure local tool logic.

    Supported conversions (bidirectional):
      km <-> miles
      kg <-> lbs
      celsius <-> fahrenheit
      meters <-> feet
      liters <-> gallons

    Args:
        value:     The numeric value to convert.
        from_unit: The source unit (case-insensitive), e.g. "km", "celsius".
        to_unit:   The target unit (case-insensitive), e.g. "miles", "fahrenheit".

    Returns:
        A string such as "100.0 km = 62.14 miles", or an error string for
        unsupported unit pairs.
    """
    f = from_unit.strip().lower()
    t = to_unit.strip().lower()

    if f == t:
        return f"{value} {from_unit} = {value} {to_unit}"

    key = (f, t)
    if key not in _CONVERSIONS:
        supported = ", ".join(f"{a} -> {b}" for a, b in _CONVERSIONS)
        return (
            f"Unsupported conversion: {from_unit} to {to_unit}. "
            f"Supported pairs: {supported}"
        )

    factor, offset = _CONVERSIONS[key]
    result = value * factor + offset
    return f"{value} {from_unit} = {round(result, 4)} {to_unit}"


# ---------------------------------------------------------------------------
# Entry-point — STDIO transport (required by Orchestrate local MCP toolkit)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
