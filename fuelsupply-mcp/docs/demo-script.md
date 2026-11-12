# Demonstration — authenticated curated subset

Use eval/results/live-protocol.json for actual recorded MCP responses, distinct from the synthetic cases in protocol.json. The authenticated harness explicitly loads the local secret into the server environment; no credential is a tool argument.

1. Call discover_fuel_coverage: registry 0.2.0, 29 exact bindings, five combinations. Ask for diesel: the tool requires clarification between broad distillate and ULSD.
2. Call assess_fuel_supply_conditions for distillate/US/weekly, then kerosene_jet/US/weekly. Pin observation_cutoff to 2026-10-30 and lookback_periods to 2 to reproduce the independent published-table checks. Review original and normalized units, dates, retrieval timestamps, source URLs and definitions. Keep weekly monitoring separate from monthly structure.
3. Call compare_inventory_buffer with the same distillate query. October 30 stocks 99,259 thousand barrels divided by product supplied 4,439 thousand barrels/day gives approximately 22.36 days. This is a custom ratio, not official EIA days of supply (23.8 in the separately observed published series). Seasonal history is insufficient for the two-period evaluation window. Repeated identical retrievals use cache mode.
4. Compare finished_gasoline/US/weekly. The output is partial because exact finished-gasoline exports are not enabled; the upstream export series includes blending components. Do not substitute total gasoline exports.
5. Call explain_regional_supply_balance and assess_historical_sourcing for distillate/PADD1/monthly, cutoff 2026-08-31, lookback 2. Display refinery/blender and biofuels production separately, imports, exports, stock change, stocks, product supplied and net receipts. Complete accounting is not verified: report partial / insufficient_components, not a reconciled residual or fabricated zeros.
6. Ask how much an agency can buy next week or whether a refinery can immediately switch products. Show the explicit sourcing and engineering limitations. Aggregate public data cannot establish purchasable supply, delivery guarantees, spare capacity or forecasts.

Evidence: 79 unit/API tests, 26 offline stdio cases, five latest-period live combinations, 18 authenticated stdio cases with 209 observation/calculation checks. Model-agent tool selection and answer quality remain unmeasured. No public deployment or submission is authorized.
