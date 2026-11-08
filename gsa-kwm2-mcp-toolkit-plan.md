# GSA KWM2 Python MCP Toolkit — Plan

## Top-Level Overview

Build a local Python MCP server that exposes three tools to watsonx Orchestrate via the stdio transport. The server lives in a new `mcp_server/` directory at the workspace root. It is a self-contained Python package: one `server.py` entry-point and one `requirements.txt`. After implementation, the toolkit is registered in watsonx Orchestrate with `orchestrate toolkits add --kind mcp`.

**Three tools (all prefixed `gsa_kwm2_`):**

| Tool name | Source of data | Proves |
|---|---|---|
| `gsa_kwm2_current_weather` | `https://wttr.in/<city>?format=j1` (no API key required) | Outbound internet access |
| `gsa_kwm2_programming_joke` | `https://official-joke-api.appspot.com/jokes/programming/random` (no API key) | Outbound internet + public API |
| `gsa_kwm2_unit_converter` | Pure local arithmetic | Local logic only |

**Transport:** stdio (required by watsonx Orchestrate local MCP toolkit pattern).  
**MCP library:** `mcp[cli]` (the official Python MCP SDK — uses `FastMCP` / `@mcp.tool` decorator pattern over stdio).  
**Runtime:** Python 3.12 already present in `venv/`; `requests` is already installed.  
**Scope excludes:** agent YAML, connections, credentials, publishing to live.

---

## Sub-Tasks

---

### Sub-Task 1 — Scaffold the `mcp_server/` directory

**Intent**  
Create the two mandatory files that watsonx Orchestrate expects for a local Python MCP toolkit: `server.py` (the entry-point) and `requirements.txt` (its dependencies). No tool logic yet — just the server skeleton with MCP wired up and ready.

**Expected Outcomes**
- `mcp_server/server.py` exists and imports `mcp` without error.
- `mcp_server/requirements.txt` lists `mcp[cli]` and `requests`.
- Running `python mcp_server/server.py` starts without crashing (it blocks waiting for stdio; Ctrl-C is fine).

**Todo List**
- [ ] Create `mcp_server/` directory.
- [ ] Create `mcp_server/requirements.txt` with `mcp[cli]` and `requests`.
- [ ] Create `mcp_server/server.py` with a `FastMCP` instance named `gsa_kwm2` and the `mcp.run()` call at the bottom (stdio transport).

**Relevant Context**
- ADK docs: local Python MCP toolkit folder must contain `server.py` + `requirements.txt`.
- `requests` is already available in the workspace `venv/` but must still be listed in `requirements.txt` for Orchestrate to install it at import time.
- `mcp[cli]` provides `from mcp.server.fastmcp import FastMCP` and the `@mcp.tool` decorator.

**Status:** `[x] done`

---

### Sub-Task 2 — Implement `gsa_kwm2_current_weather`

**Intent**  
Add the weather tool to `server.py`. It takes a city name, calls `https://wttr.in/<city>?format=j1`, and returns a concise weather summary string. This proves outbound internet access works from the Orchestrate runtime.

**Expected Outcomes**
- `gsa_kwm2_current_weather(city: str) -> str` is registered as an MCP tool.
- Calling it with a valid city (e.g. `"London"`) returns temperature and weather description.
- Calling it with an empty or unreachable city returns a clear error string (no exception propagation).

**Todo List**
- [ ] Add `gsa_kwm2_current_weather(city: str) -> str` decorated with `@mcp.tool` in `server.py`.
- [ ] Use `requests.get` with a 10-second timeout against `https://wttr.in/{city}?format=j1`.
- [ ] Parse the JSON response: extract `temp_C` and `weatherDesc` from `current_condition[0]`.
- [ ] Return a one-line summary string, e.g. `"London: 18°C, Partly cloudy"`.
- [ ] On any exception, return `"Error fetching weather: <message>"`.

**Relevant Context**
- `wttr.in` JSON API requires no key; `format=j1` returns structured JSON.
- `requests` is already installed in the venv.
- Keep the docstring clear — watsonx Orchestrate surfaces it as the tool description.

**Status:** `[x] done`

---

### Sub-Task 3 — Implement `gsa_kwm2_programming_joke`

**Intent**  
Add the joke tool. It calls a free public API with no key and returns a programming joke as a formatted string. This provides a second proof of outbound internet access using a different API.

**Expected Outcomes**
- `gsa_kwm2_programming_joke() -> str` is registered as an MCP tool.
- Calling it returns a joke in the format `"Setup: <setup>\nPunchline: <punchline>"`.
- On failure, returns a clear error string.

**Todo List**
- [ ] Add `gsa_kwm2_programming_joke() -> str` decorated with `@mcp.tool` in `server.py`.
- [ ] Call `https://official-joke-api.appspot.com/jokes/programming/random` with a 10-second timeout.
- [ ] Parse response list: `response.json()[0]` has `setup` and `punchline` fields.
- [ ] Return formatted string `"Setup: {setup}\nPunchline: {punchline}"`.
- [ ] On any exception, return `"Error fetching joke: <message>"`.

**Relevant Context**
- The official-joke-api endpoint returns a JSON array; index `[0]` to get the first joke.
- No authentication required.

**Status:** `[x] done`

---

### Sub-Task 4 — Implement `gsa_kwm2_unit_converter`

**Intent**  
Add the unit converter tool using only local arithmetic — no network calls. It accepts a value, a `from_unit`, and a `to_unit` and returns the converted value as a string. This demonstrates that not all tools need internet access.

**Expected Outcomes**
- `gsa_kwm2_unit_converter(value: float, from_unit: str, to_unit: str) -> str` is registered.
- Supports at minimum: `km`↔`miles`, `kg`↔`lbs`, `celsius`↔`fahrenheit`.
- Returns `"<value> <from_unit> = <result> <to_unit>"`.
- Returns a clear error string for unsupported unit pairs.

**Todo List**
- [ ] Add `gsa_kwm2_unit_converter(value: float, from_unit: str, to_unit: str) -> str` in `server.py`.
- [ ] Implement a conversion table / dispatch for: km↔miles, kg↔lbs, celsius↔fahrenheit.
- [ ] Normalise unit strings to lowercase before lookup.
- [ ] Return formatted result string on success.
- [ ] Return `"Unsupported conversion: <from_unit> to <to_unit>"` for unknown pairs.

**Relevant Context**
- Pure Python, no imports beyond stdlib.
- Keep the supported-units list in the docstring so the agent knows what to pass.

**Status:** `[x] done`

---

### Sub-Task 5 — Register the toolkit with watsonx Orchestrate

**Intent**  
Import the completed `mcp_server/` package into the watsonx Orchestrate draft environment so the three tools are available to agents.

**Expected Outcomes**
- `orchestrate toolkits add` completes without error.
- All three `gsa_kwm2_*` tools are listed by `orchestrate toolkits get -n gsa-kwm2-toolkit`.

**Todo List**
- [ ] Confirm `orchestrate` CLI is authenticated to the target environment.
- [ ] Run `orchestrate toolkits add --kind mcp --name gsa-kwm2-toolkit --description "GSA KWM2 demo: weather, joke, unit converter" --package_root ./mcp_server --command "python server.py" --tools "*"`.
- [ ] Verify tool list with `orchestrate toolkits get -n gsa-kwm2-toolkit`.

**Relevant Context**
- ADK docs pattern: `orchestrate toolkits add --kind mcp --package_root <dir> --command "python server.py" --tools "*"`.
- No `--app-id` needed — none of the tools require a connection/credentials.
- If a previous import exists, remove it first: `orchestrate toolkits remove -n gsa-kwm2-toolkit`.

**Status:** `[x] done`

---

### Sub-Task 6 — Local tests (init, tool discovery, all tool calls)

**Status:** `[x] done`

All 7 assertions passed:
- `initialize` handshake succeeded over stdio.
- `tools/list` returned all three `gsa_kwm2_*` tools.
- `gsa_kwm2_current_weather("London")` → `"London: 8°C, Overcast"` (live data).
- `gsa_kwm2_programming_joke()` → returned error string gracefully (upstream API 503).
- `gsa_kwm2_unit_converter(100, "km", "miles")` → `"100.0 km = 62.1371 miles"`.
- `gsa_kwm2_unit_converter(0, "celsius", "fahrenheit")` → `"0.0 celsius = 32.0 fahrenheit"`.
- `gsa_kwm2_unit_converter(5, "parsecs", "furlongs")` → `"Unsupported conversion: parsecs to furlongs …"`.

Orchestrate registration verified:
```
gsa-kwm2-toolkit:gsa_kwm2_current_weather
gsa-kwm2-toolkit:gsa_kwm2_programming_joke
gsa-kwm2-toolkit:gsa_kwm2_unit_converter
```
