# FuelSupply evaluator code review

## Reading order

1. Start at `main.py`, then `src/fuelsupply/app.py`. FastMCP registers five tools, a methodology resource and a briefing prompt. The prompt supplies client guidance; it does not call a model.
2. Read `src/fuelsupply/tools/`. Each tool has its own registration module and existing model-facing description. Discovery reads the curated registry without a network request. The four analytical tools select a purpose in `SupplyService.run`.
3. Follow `src/fuelsupply/service.py`. It clarifies broad fuel labels, selects exact verified mappings, retrieves observations, preserves original values and units, and reports diagnostics alongside calculations. Unsupported coverage does not trigger a product or geography substitution.
4. Review `models.py`, `registry.py` and `eia_client.py` in that package. Pydantic validates query/binding structure. Registry entries supply verified routes and facets. The client fixes the EIA origin and bounds history, pagination, concurrency, response size and retries. It replaces upstream errors with safe diagnostics. Credentials come from server settings.
5. Read `normalization.py` and `analytics.py`. Monthly flow totals become daily averages; stocks remain levels. Missing observations remain unknown. Inventory coverage requires aligned evidence. Monthly reconciliation reports missing components or a residual. Seasonal comparisons need sufficient matching years.
6. Follow `dashboard/index.html`, `dashboard/app.js` and `dashboard/serve.py`. The browser starts from saved public-data results. Its refresh endpoint calls the same service directly, rather than using the MCP transport. The local server restricts Host/Origin, paths, request size and query combinations. It serializes refreshes and rejects upstream failures before saving refreshed observations.
7. Review `dashboard/export_snapshot.py`. It inlines saved observations and existing assets into offline HTML. CSV export and browser printing operate on the selected saved case. No browser asset includes the EIA credential.

The new inline comments explain these decisions at their implementation sites. Existing tool docstrings, schemas, calculations, registry mappings and dashboard behavior are unchanged. The dashboard's stock/flow charts retain their existing distinction, and monthly refinery/blender production remains a component rather than a fabricated total.

## Validation on November 14, 2026

Base: `afmurph55/gsa-hackathon-kwm-test-app` commit `7a54c069badfc798e1db18da4833c21a28bc003b`.

- Unit/API suite: **82 passed**, including the three local dashboard HTTP tests.
- Actual subprocess stdio MCP evaluation: **26/26 passed**, with 25 schema-valid non-error responses and one expected validation error. It exercised tool discovery, the methodology resource and the briefing prompt.
- Retrieval in this run: **72 synthetic HTTP requests, zero real upstream requests**. No new authenticated EIA or model-agent evaluation is claimed.
- Ruff lint and format checks, JavaScript syntax and `git diff --check` passed.
- Python ASTs and JavaScript/HTML content with comments removed matched the base implementation. Comments leave model-facing docstrings intact.

The protocol summary and pytest output are recorded under `eval/results/evaluator-comments-*`. Earlier authenticated evidence retains its original dates and files. Synthetic cases are test evidence only and do not appear as dashboard market observations.

## Reproduce

From `fuelsupply-mcp`, after installing the locked development environment:

```sh
uv sync --locked --group dev
PYTHONPATH=src uv run --no-sync pytest -q
PYTHONPATH=src uv run --no-sync python eval/run_protocol_eval.py
uv run --no-sync ruff check src/fuelsupply dashboard main.py
uv run --no-sync ruff format --check src/fuelsupply dashboard main.py
node --check dashboard/app.js
```

The protocol harness writes `eval/results/protocol.json` and its stderr logs. Save existing evidence before rerunning it if those files must be retained. These checks do not require an EIA key. The dashboard server can be reviewed locally with `PYTHONPATH=src uv run --no-sync python dashboard/serve.py` and `http://127.0.0.1:8765/`; a live refresh requires a server-side credential.

## Interpretation limits

This review update documents the existing implementation. Monthly accounting components remain incomplete, exact finished-gasoline exports remain excluded, and model-agent tool selection and answer quality remain unmeasured. Public EIA observations cannot establish purchasable fuel, spare capacity or forecasts. No deployment, publication or hackathon submission accompanies these local changes.
