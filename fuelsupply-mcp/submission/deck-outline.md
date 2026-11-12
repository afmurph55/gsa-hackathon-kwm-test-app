## FuelSupply MCP

Government fuel briefings, with evidence and limits

- Dataset Access Server | Local sandbox prototype
- Intended users: transportation, aviation, logistics and energy analysts
- Proposed use case; no agency adoption claimed
- Offline implementation tested. Live-data MVP blocked.

## The analyst's problem

One briefing, incompatible datasets

- Compare distillate, gasoline and kerosene-type jet fuel
- Understand inventories, implied demand and regional sourcing
- Preserve definitions, units, frequency and observation periods
- Public EIA data only; no procurement or operational files

## Tools follow analyst goals

Coverage → conditions → inventory → structure

- discover_fuel_coverage: choose exact product and supported scope
- assess_fuel_supply_conditions: production, stocks, demand, trade
- compare_inventory_buffer: compatible ratios and seasonal evidence
- explain_regional_supply_balance / assess_historical_sourcing

## Architecture

Client-independent MCP over stdio

- Pydantic models → one tool per file → orchestration
- Verified registry → fixed-origin EIA client → bounded cache
- Deterministic normalization, coverage and reconciliation
- Methodology resource and reusable briefing prompt

## Analytical safeguards

Make uncertainty visible

- Distillate ≠ ULSD; finished gasoline ≠ components; jet ≠ avgas
- Monthly totals use calendar days; stocks remain quantities
- Demand is product supplied, an accounting-based proxy
- Missing terms yield insufficient_components; never force a balance

## Security and reliability

Read-only behavior enforced in implementation

- Environment key; fixed EIA origin; validated routes; no redirects
- 2 concurrent fetches; 3 pages; 3 eligible attempts; 2 MiB response cap
- Timeouts, Retry-After handling, duplicate and missing-value checks
- Timestamped cache; stderr logs; no external tracing or deployment

## Demonstrated functionality

Actual local calls; synthetic data labeled

- Real MCP initialize, list tools, resource/prompt retrieval and calls
- Production: blocked coverage and product clarification work
- Synthetic: inventory ratio, monthly residual and upstream failures
- Real national briefing and East Coast data demo remain blocked

## Actual evaluation results

Evidence, not a claim of agent performance

- 74 pytest passes | 26/26 MCP cases pass | 25/25 structured results
- Local tool latency: n=26; median 3.35 ms; p95 12.05 ms
- Synthetic uncached n=9; cached n=2; 72 mock upstream requests
- 0 real EIA requests; Codex client initialization blocked

## What public data cannot establish

The boundary is part of the briefing

- How many gallons can we buy next week? EIA cannot establish that.
- No uncommitted quantity, quotes, airport availability or delivery guarantee
- Utilization is not spare product capacity; yields do not prove switching
- Historical receipts are not confirmed replacement supply

## Next steps and local deliverables

Verify live coverage before claiming MVP completion

- Configure key and EIA network access; verify curated metadata/samples
- Run live calculation checks, real-data demos and a model client
- Code + lockfile + CI + docs + PPTX + evaluation MD/DOCX prepared
- Official templates blocked; no push, publication or submission