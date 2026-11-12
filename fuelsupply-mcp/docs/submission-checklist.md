# Local submission checklist

- [x] Separate local official-template-based project; license and commit attribution preserved.
- [x] Five analyst-oriented tools, Pydantic inputs/output envelope, resource and briefing prompt.
- [x] Fixed-origin EIA client, bounded pagination/cache/retries/timeouts, numeric parsing and deterministic analytics.
- [x] Unit/API and actual subprocess MCP evidence; versioned evaluation cases and raw results.
- [x] Local deck .pptx and evaluation .md/.docx, with implementation limits disclosed.
- [x] Setup, methodology, coverage, security, integration and demo documentation.
- [x] CI definition includes lint, format, pytest and protocol evaluation. Remote CI not run.
- [ ] EIA key and permitted EIA hosts; authenticated discovery and nonempty verified registry.
- [ ] MVP A real national weekly distillate/gasoline/jet metrics, exports and utilization coverage.
- [ ] MVP B real monthly US/published PADD component coverage and reconciliations.
- [ ] Real national and East Coast demo outputs, sanitized source captures and live cross-checks.
- [ ] Successful Codex/model client evaluation; selection accuracy and answer-boundary evaluation.
- [ ] Official PPTX/DOCX template comparison (binary downloads blocked).
- [x] All 10 slides rendered through LibreOffice and inspected; no visible clipping or overlap. Rendered files and PDF retained.
- [ ] Fresh-machine reproduction, Python3.11, container build and remote CI verification.
- [ ] Participant-specific instructions reviewed; no conflict resolved by assumption.
- [ ] User authorizes GitHub push/submission if desired; no push/deployment/submission has occurred.

Next smallest action: configure EIA_API_KEY in environment secret settings and allow api.eia.gov/www.eia.gov, then inspect just the petroleum metadata root with scripts/discover_eia.py. Do not paste the key into chat. These settings are not changed automatically.
