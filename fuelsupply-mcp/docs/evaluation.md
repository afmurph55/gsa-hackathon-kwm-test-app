# FuelSupply MCP evaluation document

## Current authenticated milestone — November 11, 2026

The prior missing-key/network-blocker milestone below is historical. EIA authentication now succeeds. Registry 0.2.0 enables 29 metadata/sample/table-verified mappings across five combinations (58 matched observations). Final verification: 79 unit/API tests, 26/26 offline stdio cases, 5/5 latest-period live combinations (29 requests), and 18/18 authenticated stdio cases with 209 observation/calculation checks. Key presence and owner-only storage were verified without displaying it. No deployment, submission, push, publication, tracing, or global settings change.

See `docs/authenticated-evaluation-2026-11-11.md` for complete current evidence, source/registry hashes and reproducible commands; `docs/coverage.md` defines exact enabled coverage. Monthly reconciliation is incomplete; finished-gasoline exports are intentionally excluded. Model-agent usability and official submission-template reconciliation remain outstanding. Historical submission binaries are stale and were not regenerated. The original /workspace path remains unavailable on this host; the project was restored into the chat's writable workspace.

## Historical offline milestone and restoration record

Status: offline implementation verified; live market-data MVP and agent evaluation blocked.

## Methodology and inputs
Versioned protocol dataset: eval/cases.jsonl (26 cases). Test-only synthetic observations are isolated in tests/protocol_server.py and tests/fuel_fixtures.py; none are verified EIA mappings. Production sessions use the actual launch entry point and empty registry. Each fixture launches a subprocess, initializes MCP, lists all five tools, reads methodology, gets the briefing prompt and invokes tools. The installed MCP SDK uses snake_case client fields; protocol serialization is SDK-owned.

Layer A/B: 74 pytest cases pass (48 FuelSupply unit/API cases; 26 inherited template/security cases). Formula, calendar, missing/nonfinite values, compatible ratios, validation, seasonal history, reconciliation, pagination, concurrency, rate limiting, permanent errors, redirects, key redaction, timeout retry exhaustion, oversized responses and cache behavior are tested. Incompatible periods are tested directly in service tests. Layer C: real stdio protocol sessions against production and synthetic upstream fixture. Synthetic requests are in-memory MockTransport HTTP requests, never network calls.

Layer D: live EIA checks blocked, zero executed; eval/results/live.json records one skipped live-check group. EIA_API_KEY is absent and EIA hosts are not in the enforced network allowlist. The production registry has zero enabled bindings. No API route/facet/product/units combination is verified.

Layer E: attempted installed Codex CLI 0.167.0-alpha.4 using transient MCP configuration, read-only sandbox and ephemeral execution. Client initialization failed with a read-only filesystem error before any model/tool call. Logs: eval/results/agent-stderr.log and agent-events.jsonl. CLI authentication alone does not establish agent evaluation access. Agent tests executed: zero; tool-selection accuracy and model-answer correctness: unmeasured. No model configuration can be reported as executed.

## Actual results
- Pytest: 74 passed, 0 failed, 0 skipped; recorded in eval/results/pytest.txt. No separate live pytest tests are implied.
- Protocol: 26 executed, 26 passed, 0 failed, 0 skipped. 15 production cases and 11 synthetic integration cases.
- Structured response validity: 25/25 non-error responses = 100%. One additional case deliberately triggers MCP input validation and is excluded from that denominator.
- Calculation checks: custom coverage 100/100 = 1 day in synthetic protocol data, insufficient seasonal history and monthly residual_present all pass; unit tests also verify a zero residual, -1 residual, leap-February conversion, invalid/zero denominator and incompatible periods. No live calculation cross-check has run.
- Error paths: unsupported/blocked coverage, aliases, input validation, fake credential 401, rate limit Retry-After, missing/withheld values, stale periods and units behave as asserted. All 26 protocol responses are checked for the fake secret string; none expose it.
- End-to-end tool-call latency (session initialization excluded), n=26: minimum 1.345 ms, median 3.349 ms, p95 reported by harness 12.050 ms, maximum 40.578 ms. These small local samples are descriptive, not a performance guarantee or official GSA target.
- Production live-requested/no-observation responses: n=14, median 1.467 ms. No upstream data were fetched. The validation error is excluded from mode groups.
- Synthetic uncached/live-requested responses (including error paths): n=9, median 5.535 ms. Synthetic cached responses: n=2, median 4.898 ms. Production cached measurements: n=0. These are not live EIA cold/cache benchmarks.
- Upstream request count: real EIA 0; synthetic HTTP transport 72. Request counts do not count internal MCP calls as EIA requests.

## Environment and reproducibility
Python 3.12.14; dependencies {"fastmcp": "4.0.11", "httpx": "0.28.1", "mcp": "2.3.0", "pydantic": "2.13.5"}. Registry 0.1.0. Base/template git revision f39249f1768309e3ef8b31742390a4f3a656b5f3; runtime source SHA256 d802dc71c0c3400e60b082b18c2f2275c6c54594c30b0154d5af97b8c391abb7. Working tree contains the implementation; base revision is not falsely described as an implementation commit. uv.lock captures the full dependency set. Raw per-case tool outputs, latency and initialization timings are in eval/results/protocol.json. CI is defined but not run remotely; Python3.11 and container reproduction are unverified.

From /workspace/fuelsupply-mcp:

```bash
export UV_CACHE_DIR=/tmp/fuelsupply-uv-cache
export UV_PYTHON_INSTALL_DIR=/tmp/fuelsupply-python
uv sync --locked --group dev --python "$(command -v python)"
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest tests -q
.venv/bin/python eval/run_protocol_eval.py
.venv/bin/python eval/run_live_checks.py
.venv/bin/python scripts/build_submission.py
```

Live-check exit 2 means blocked, not success. Protocol expectations intentionally target the empty production registry; version the dataset before enabling live coverage. The server launch is /workspace/fuelsupply-mcp/.venv/bin/fuelsupply-mcp and uses stdio independently of Codex.

## Security considerations
Fixed HTTPS EIA origin, relative-route validation and disabled redirects restrict outbound access. Server-side credentials are never tool inputs. Error bodies and request URLs are suppressed; numeric observations are sanitized. Timeouts, bounded concurrency/pages/retries, response-size cap and an expiring LRU limit resource use. Cache preserves retrieval timestamps and mode. No silent replay fallback, shell/file tool, purchasing operation or external tracing is enabled. Managed proxy trust is inherited. See docs/security.md for residual threats; no production, agency or compliance certification is claimed.

## Failures, lessons and recommendations
Initial protocol evaluation failed because the current SDK exposes snake_case client attributes; the harness was repaired against inspected SDK signatures. A fixture regenerated its verification timestamp between requests and accidentally bypassed the cache; it now reuses the same binding. Synthetic cutoff scenarios initially filtered their own test observations; the fixture was corrected to use periods preceding the cutoff. Initial failures remain in eval/results/initial-protocol-failures.json; final results supersede them.

The optional template Phoenix/LangChain guide was inspected; it is not an official mandatory harness. It would introduce model/tracing dependencies and was not enabled. Deterministic protocol testing does not replace agent usability testing.

Next: configure credentials and permitted EIA hosts, inspect a small metadata subset, validate each mapping and accounting component against authenticated responses/published tables, then run live protocol/calculation demos and an actual MCP-capable model client. Replace this deck with the official template after downloading it in a permitted environment. Do not deploy or submit without explicit authorization.

## Deliverable validation
A real local PPTX and DOCX are generated and reopened using their libraries. Rendering/visual QA is recorded separately in submission/artifact-validation.json; document reopen alone is not slide visual QA. Official PPTX/DOCX binary templates could not be downloaded here (proxy 403); local files do not claim template compliance. Requirements matrix and submission checklist list remaining gaps.

## Restoration and evaluation — November 11, 2026

Restored from `/Users/kenmurphy/fuelsupply-handoff.tar.gz` into `/Users/kenmurphy/Documents/Codex/2026-11-11/restore-this-fuelsupply-project-in-workspace-3/fuelsupply-mcp`. The requested `/workspace` cannot be created because the host root filesystem is read-only, even with filesystem permission granted. Git metadata and existing local changes were preserved. AGENTS.md and PLANS.md were read before evaluation. Original handoff evaluation evidence is preserved in `../work/handoff-eval-results`.

Installed the locked development environment with uv using host Python 3.13.1. Current checks: 74 pytest tests passed; Ruff lint passed; formatting passed for 43 files. Actual stdio MCP sessions: 26/26 cases passed, 25/25 non-error responses schema-valid, one expected validation error, 72 synthetic HTTP requests and zero real authenticated EIA requests. Protocol latency median 1.922 ms, p95 6.035 ms. Runtime source hash remains d802dc71c0c3400e60b082b18c2f2275c6c54594c30b0154d5af97b8c391abb7.

EIA_API_KEY is absent from the inherited environment; no credential was displayed. FuelSupply does not automatically load .env files. The archive has no credential .env file. Authenticated discovery exited 2 before sending a request. Live checks exited 2: blocked, 0 executed, 1 skipped group. Production registry remains empty. A separate unauthenticated request to the petroleum metadata endpoint received HTTP 403; this does not establish origin reachability, authenticated access, or a network allowlist diagnosis. This check is recorded separately in `eval/results/network-preflight.json` and is not counted as a live calculation or authenticated API request.

The earlier narrative and protocol harness contain historical blocking labels about network policy and the Codex agent runtime. Those labels are not fresh measurements; model-client usability evaluation was not rerun in this restoration. Use this dated entry for current restoration status. Historical submission binaries have not been regenerated and retain their original evidence.

Remaining: supply an existing secure credential location or configured runtime, run bounded authenticated petroleum metadata discovery, review metadata/sample/table evidence for every binding, enable only verified mappings, version production protocol expectations, and run live calculations and demos. Authenticated discovery and live evaluation cannot proceed without a credential. No deployment, submission, push, publication, external tracing, or global Codex settings changes were performed.
