# FuelSupply interactive dashboard

The local dashboard presents real EIA observations from FuelSupply's verified registry. It runs with the project's existing Python dependencies; no frontend package install or external chart library is needed.

From the FuelSupply project directory:

```bash
.venv/bin/python dashboard/serve.py
```

Open **http://127.0.0.1:8765** in Safari or Chrome. Keep Terminal open while using live refresh. Press Control-C to stop. Use `--port 8766` if the default port is occupied.

The launcher explicitly loads the private root `.env` into the local server environment. EIA_API_KEY is never sent to the browser, accepted as a tool input, embedded in a dashboard export, or logged. The server listens only on loopback. Refresh accepts only the five verified combinations and histories of 3, 12, 26 or 52 periods. Cross-origin requests, unexpected Host headers, extra request fields and arbitrary file paths are rejected. No deployment or GitHub update is performed by this launcher.

## Use

- Choose an exact fuel product, observation frequency and geography. Unverified combinations are disabled. Distillate is the broad product family, not ULSD.
- The cards show period-end stocks, product supplied and a custom inventory ratio for aligned periods. The ratio is not official EIA days of supply or a depletion forecast.
- The charts show stocks separately from production and implied demand. Legend buttons toggle the two flow series; hover or touch reveals observed values.
- Select a history and click **Refresh from EIA** to retrieve that selection. A successful refresh replaces that selection's saved observations and retrieval time. Other combinations keep their own retrieval dates. Shorter refresh histories replace a previously longer saved window.
- **Show all periods** expands the observation table. **Download CSV** exports all metrics across the selected saved history, with original values, units and source URLs.
- **Print / save PDF** opens the browser's print dialog for a report of the current selection. Choose Save as PDF if desired. The current table expansion state controls how many observation rows are printed.

Monthly production components remain separate, so the monthly chart shows refinery/blender production rather than total production. Full monthly reconciliation remains incomplete. Finished-gasoline exports are excluded because the upstream series includes blending components. Coverage notes, exact definitions and published EIA source links remain visible.

## Offline copy

```bash
.venv/bin/python dashboard/export_snapshot.py --output /absolute/path/FuelSupply-dashboard.html
```

Open the resulting HTML file in Safari or Chrome. It includes saved data, styling and charts, supports selection, CSV and printing, and needs no network for those features. Refresh is disabled when opened as a local file. Export again after refreshing the local dashboard to share a newer snapshot. The self-contained export is a saved view, not a hosted live service.

## Validation

The dashboard addition was checked with 82 unit/API tests (including three dashboard HTTP-boundary/persistence tests), 26 actual stdio MCP protocol cases, JavaScript syntax checking, lint and formatting. Browser QA covered product/frequency/geography/history selection, partial-coverage notes, table expansion, mobile layout and a successful real EIA refresh of the PADD1 monthly selection. The in-app browser's CSV download event could not be confirmed; the standard browser download control is included for Safari/Chrome. PDF export invokes the browser print dialog and was not automated.

The initial dashboard snapshot retrieved 12 periods for all five combinations with 29 authenticated upstream requests. The interactive refresh test subsequently replaced PADD1 monthly with three periods. Latest saved weekly observations ended October 30, 2026; latest monthly observations are August 2026. Retrieval date is shown separately; do not treat it as the observation date or historical publication vintage.
