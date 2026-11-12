# Requirements matrix

Sources: **event** = [official GSA page](https://www.gsa.gov/artificial-intelligence/ai-community-of-practice/events-and-training/mcp-server-and-ai-agent-government-hackathon); **template** = [official repository](https://github.com/GSA-TTS/mcp-hackathon-template) at `f39249f1768309e3ef8b31742390a4f3a656b5f3`. **user §N** refers to the numbered implementation brief in this chat. “Judged” is a published criterion, without an invented weight. Evidence paths are relative to this repository. “Met offline” does not imply live MVP acceptance.

| Requirement | Official source / additional instruction | Required versus recommended | Implementation artifact | Verification evidence | Status | Remaining gap |
| --- | --- | --- | --- | --- | --- | --- |
| Dataset Access Server track | event: application tracks | Required chosen track | src/fuelsupply/tools/ | protocol tool list | Partial | Live dataset access blocked |
| Public government data; sandbox; no deployment | event: Scope | Required | AGENTS.md; fixed EIA origin | No deployment/push; registry empty | Met locally | Maintain boundary |
| Readable code and separated concerns | event: Technical Quality 1 | Judged | models.py, eia_client.py, analytics.py, tools/ | ruff; file structure | Met locally | Review with domain expert |
| Performance and reliability setup/results | event: Technical Quality 2 | Required | eval/cases.jsonl; eval/results/protocol.json | 26 real protocol cases; 74 pytest cases | Partial | Live and agent results blocked |
| Pydantic inputs | event: Technical Quality 3 | Judged | models.Query; models.Result | invalid-lookback protocol case; validation tests | Met locally | None for offline scope |
| Precise agent tool descriptions | event: Technical Quality 3 | Judged | one file per tool | list_tools actual session | Partial | Model selection not measured |
| Goal-oriented tools | event: Technical Quality 3 | Judged | five tools; deterministic analytics | protocol invokes each analytical goal | Met locally | Live end-to-end demos |
| Mission alignment | event: Mission alignment | Judged | README.md; deck problem/use scenario | Document review | Prepared | No agency adoption claimed; user feedback unrun |
| Innovation | event: Innovation | Judged | definition/period compatibility gates; residual reporting | unit/protocol cases | Prepared | No external novelty score claimed |
| Presentation/demo | event: Presentation | Judged | submission/presentation.pptx; docs/demo-script.md | PPTX reopen, LibreOffice rendered slides; protocol evidence | Partial | Real data demos |
| Repository code deliverable | event: Deliverables 1 | Required | local project; lockfile; CI | pytest, lint, protocol | Prepared locally | No GitHub push authorized |
| Presentation deck deliverable | event: Deliverables 2 | Required | submission/presentation.pptx | PPTX reopen and LibreOffice render/visual QA | Partial | Official template unavailable |
| Evaluation documentation deliverable | event: Deliverables 3 | Required | submission/evaluation-document.md and .docx | Reopen DOCX; machine results | Partial | Official sample unavailable; live/agent gaps |
| Template foundation, license and commit | user §3; template README | Required by user | LICENSE; docs/sources/template-commit.txt | template commit and preserved original files | Met | None |
| Durable project rules and plan | user §3 | Required by user | AGENTS.md; PLANS.md | Files present | Met | Keep updated |
| Curated authenticated EIA metadata/series registry | user §5 | Required by user | config/series_registry.json and schema; scripts/discover_eia.py | zero enabled verified mappings | Blocked | EIA_API_KEY and EIA network access |
| Weekly production/stocks/demand/trade/utilization | user §4 MVP A | Required by user | service.py; coverage.md | synthetic weekly protocol; no EIA coverage | Blocked live | Verify every product/metric separately, including utilization context |
| Monthly US/PADD supply structure | user §4 MVP B | Required by user | analytics.reconcile; monthly tool | synthetic monthly residual protocol | Blocked live | Verify combinations and full applicable components |
| Exact fuel definitions; no silent substitutes | user §4,8 | Required by user | provenance.py; service.py | ambiguity and no-substitution protocol cases | Met offline | Exact EIA definitions await discovery |
| Calendar normalization; missing values; compatible ratios | user §8 | Required by user | normalization.py; analytics.py | formula/calendar/zero/withheld tests | Met offline | Live calculation cross-check |
| Period alignment and cutoff vintage caveat | user §7,8 | Required by user | service.py; LIMITATIONS | unaligned/cutoff tests; response limitations | Met offline | No vintage dataset |
| Seasonal comparison baseline and week 53 | user §8 | Required by user | analytics.seasonal_comparison | history/week-53 test; insufficient-history protocol | Met offline | Full historical coverage unverified |
| Monthly reconciliation/residual/missing components | user §7,8 | Required by user | analytics.reconcile | balanced/residual/missing tests | Met offline | Domain-approved component aggregation |
| Historical sourcing; no replacement or diversification inference | user §7,8 | Required by user | assess_historical_sourcing; LIMITATIONS | sourcing/boundary protocol | Met offline | No live sourcing history |
| Server-side key; fixed origin/routes; no redirects | user §9; template SECURITY | Required | config.py; eia_client.py | redaction, route, HTTP302 tests | Met locally | Production security not claimed |
| Timeouts/retries/concurrency/pagination/duplicates/cache | user §9 | Required | eia_client.py; cache.py | mock HTTP tests; protocol failure paths | Met locally | Actual EIA latency unknown |
| Bounded output and stderr logging; no arbitrary actions | user §7,9 | Required | Query limits; client limits; app.py | schema/validation; protocol transport | Met locally | Sandbox controls remain necessary |
| Unit and mock API evaluation | user §10 A/B | Required | tests/test_fuelsupply.py | eval/results/pytest.txt | Met | Template tests included separately |
| Real MCP protocol evaluation | user §10 C | Required | eval/run_protocol_eval.py | initialize/list/call/resource/prompt sessions | Met | Synthetic results are not market evidence |
| Live EIA evaluation | user §10 D | Required when credentials permit | eval/run_live_checks.py; results/live.json | 0 executed; blocked record | Blocked | Key, allowed hosts and verified registry |
| Agent usability and Codex client evaluation | user §10 E,12 | Conditional | agent-stderr.log; codex-integration.md | CLI attempt failed before model/tools | Blocked | Writable supported CLI runtime; rerun actual selection cases |
| Phoenix/LangChain harness | template eval/README and mcp-eval skill | Recommended option | docs/evaluation.md | Guide inspected; tracing not enabled | Not used | Optional; no authorized tracing service |
| Threat model and realistic limitations | user §9 | Required | docs/security.md | redaction/reliability tests | Prepared | No production/agency certification |
| Demo actual data and graceful failure | user §11 | Required | docs/demo-script.md; protocol.json | actual blocked/ambiguity responses; synthetic analytic workflow | Partial | Actual market-data workflows blocked |
| Codex integration commands and help | user §12 | Required | docs/codex-integration.md | CLI 0.167.0-alpha.4 help inspected | Prepared | Client run blocked; no global registration |
| Submission checklist/security/reproducibility | user §13 | Required | docs/submission-checklist.md; lockfile; CI | local final checks | Partial | Remote CI/container/Python3.11 unrun |
| Spot prices/charts | user §4 stretch | Optional after MVP | None | Not run | Deferred | MVP live verification first |

No participant-only rubric was present. Check those instructions before a consequential submission action; flag any conflict first. Nothing has been submitted or deployed.
