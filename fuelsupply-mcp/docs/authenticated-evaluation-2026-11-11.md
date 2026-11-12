# FuelSupply authenticated discovery and evaluation

Completed locally on November 11, 2026 (America/New_York). The saved EIA_API_KEY authenticated successfully. The file has owner-only permissions (0600), is gitignored, and is loaded explicitly into the server environment. No credential value was displayed or copied into the evaluation evidence.

The project remains at `/Users/kenmurphy/Documents/Codex/2026-11-11/restore-this-fuelsupply-project-in-workspace-3/fuelsupply-mcp`. `/workspace` cannot be created on this Mac's read-only root filesystem. AGENTS.md and PLANS.md were read, prior work was preserved, and no deployment, submission, push, publication, tracing, or global Codex setting change occurred.

## Verified coverage

Registry 0.2.0 contains 29 mappings across five combinations: weekly U.S. distillate (5), finished motor gasoline (4), kerosene-type jet fuel (5); monthly U.S. distillate (7); monthly PADD1 distillate (8). Each series matched authenticated metadata/sample identity and independently retrieved EIA published-table values in two periods: 58 matched observations. Sanitized captures, source URLs, table titles and hashes are in `docs/sources/binding-verification.json` and `docs/sources/published-tables/`.

Weekly reviewed samples cover October 23–30, 2026; monthly samples cover July–August 2026. These are reviewed sample windows, not full-history coverage claims. The separate latest-period check queried live data without a pinned cutoff.

Finished-gasoline exports are excluded because the upstream series includes blending components despite the finished-gasoline facet. Weekly gasoline production uses adjusted net production. Monthly refinery/blender and biofuels production remain separately named components; no total production or missing accounting term is inferred. ULSD, avgas, blending components, other PADD combinations and utilization context remain unverified.

## Actual validation

| Check | Result |
| --- | --- |
| Unit/API tests | 79 passed, 0 failed |
| Ruff lint / formatting | Passed; 44 Python files formatted |
| Offline actual stdio MCP | 26/26 cases; 25/25 non-error responses schema-valid; 1 expected input-validation error |
| Latest-period authenticated service checks | 5/5 combinations passed; 29 upstream requests; 0 skipped |
| Authenticated actual stdio MCP | 18/18 cases passed; 209 observation/calculation checks |
| Published table matching | 29/29 series, 58/58 observations |
| Model-agent selection / answer quality | Not evaluated |

The authenticated MCP harness initializes the server, lists five tools, reads methodology, gets the briefing prompt, checks coverage, and invokes conditions, inventory and historical sourcing for each combination plus both monthly balance cases. It independently checks every returned observation against table-matched captures using Decimal/calendar arithmetic, checks inventory ratios, and verifies cache reuse and insufficient seasonal history. It does not measure a language model's tool selection or answer quality. The live service harness reports 29 requests; the stdio subprocess's HTTP request/retry totals are not separately instrumented.

## Reproduced custom inventory ratios

| Product | Geography | Frequency | Period | Custom ratio (days) |
| --- | --- | --- | --- | --- |
| distillate | PADD1 | monthly | 2026-08 | 20.146093 |
| distillate | US | monthly | 2026-08 | 28.727217 |
| distillate | US | weekly | 2026-10-30 | 22.360667 |
| finished_gasoline | US | weekly | 2026-10-30 | 1.582652 |
| kerosene_jet | US | weekly | 2026-10-30 | 24.179398 |

These divide stocks by product supplied and are not official EIA days of supply or depletion forecasts. For example, U.S. distillate on October 30 is 99,259 / 4,439 = approximately 22.36 days, while the separate official EIA days-of-supply observation is 23.8. Monthly ratios use monthly flow volumes divided by actual calendar days. Two sample periods do not establish a seasonal baseline.

## Fixes and limitations

Added explicit MBBL and MBBL/D conversions, preserving original units. Added four unit-code regression cases. Fixed the monthly balance path so a missing-key/no-observation error is not overwritten by partial status, with a regression case. Removed stale unsupported-coverage diagnostics that asserted a current credentials/network blocker. Versioned offline protocol expectations for the populated registry; empty-registry version 1 and prior evidence are preserved.

Monthly reconciliation remains partial / insufficient_components. Complete total-production and other supply/disposition accounting have not been independently established. No zero terms or residual reconciliation are fabricated. Public aggregate data cannot establish purchasable volumes, spare capacity, switching feasibility, supplier availability or forecasts. Observation cutoffs are period filters, not historical-publication-vintage controls.

Historical submission binaries still describe the offline milestone and were not regenerated. Python3.11, containers, remote CI and a model-client usability run remain unverified. Explicit PYTHONPATH pointing to this checkout's src directory was used for source evaluation and is documented in README; the restored editable environment did not resolve package imports without it. No global environment configuration was changed.

## Reproducibility and evidence

Python 3.13.1; locked dependencies installed with uv. Runtime source SHA256: `771171afa2b0f8bd724c3fdc9e8a844d1a47f10a4c370210cef8b883401c3a87`. Registry SHA256: `8e58a4c04ebcc5e31929518dba22d926f77033371e200e7670dc44c2293da15c`. Both offline and authenticated stdio runs used the same final runtime source hash.

Fresh evidence: `eval/results/pytest.txt`, `protocol.json`, `protocol-summary.json`, `live.json`, `live-protocol.json`. Commands and explicit private .env loading are in README. Earlier missing-key and network-blocked claims are historical and superseded by this run. A successful current authenticated EIA request resolves that blocker for this runtime.
