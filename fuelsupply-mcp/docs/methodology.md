# Analytical methodology

FuelSupply supports market-level descriptive briefings using public EIA petroleum data. It cannot establish purchasable quantities, supplier quotes, guaranteed delivery, airport availability, pipeline spare capacity, refinery switching feasibility, shortages or prices. This is a proposed government use case, not adopted agency software.

Product supplied is an accounting-based proxy for demand. It is not direct customer sales or an independent measurement suitable for manufacturing a “surplus.” No calculation defines available fuel as production minus product supplied. Stocks are quantities at a point in time; production, trade and demand are period flows. Weekly and monthly analyses stay separate.

## Definitions and normalization
Broad distillate is not ULSD. Finished motor gasoline excludes blending components. Kerosene-type jet fuel differs from avgas. Ambiguous aliases require explicit selection. A registry must state the exact EIA product definition for every metric; incompatible definitions suppress reconciliation/coverage.

Original units and numeric values accompany normalized observations. Missing, withheld, invalid, nonfinite values become null and diagnostics, never zero. Monthly totals in thousand barrels are divided by the actual calendar days in that observation month to obtain thousand barrels/day. Stock quantities are never divided by calendar days. Unsupported units are diagnosed, never guessed. Cutoffs include observations whose full period ends on or before the cutoff; monthly partial periods are excluded.

## Inventory
The custom ratio is `stocks (thousand barrels) / product supplied (thousand barrels/day)`. It is allowed only for matching product definitions, geography, frequency and period, valid nonnegative stocks and strictly positive demand. No national denominator is applied to PADD stocks. The ratio is explicitly labeled custom, not an official EIA days-of-supply series or a countdown to exhaustion.

Stock histories are returned as observed; gaps remain gaps. Custom seasonal comparison uses matching month or ISO week number in the previous five calendar years, requiring at least three distinct observed years before returning a mean. The output lists baseline window, observed years, sample count, missing years, and week-53 treatment (match week 53 only; never merge into week 52). This is a local descriptive baseline, not EIA's official historical range methodology. The bounded 260-period request may not provide all five full weekly years; missing history remains explicit.

## Monthly reconciliation
`production + imports + net_receipts + other_supply - exports - stock_change - product_supplied - other_disposition = residual`.

Positive stock change means inventory accumulation. All inputs must use the same product, month, geography and normalized flow units. Every term must be explicitly provided; missing “other” components are never assumed zero. A residual within 1e-6 thousand barrels/day is labeled reconciled (local numeric tolerance); otherwise residual_present. Missing terms/unaligned periods yield insufficient_components. Published rounding can produce residuals; no fabricated adjustment closes the balance.

Registry methodology must document whether production includes field, refinery/blender, biofuel production or relevant transfers; other supply/disposition must explicitly aggregate applicable published terms without double counting. EIA's monthly notes describe these accounting terms. The generic formula is implemented and tested, but no official EIA component set is currently verified.

## Interpretation and provenance
Each metric retains its periods, units, source binding and retrieval context. Overall retrieval timestamp is the latest successful retrieval. Different latest periods trigger an alignment diagnostic and prevent a synchronized balance. Source bindings supply observed coverage and original methodology; they are not historical publication vintages. Cutoffs do not establish what was known at a past date.

Staleness heuristics are local: over 21 days weekly, over 120 days monthly, relative to execution date. They are warnings, not official publication schedules; historical cutoffs naturally produce stale-to-today observations. Cache TTL is 300 seconds with original retrieval timestamps.

Historical movements are evidence of past sourcing. Net receipts cannot establish gross origin diversity or confirmed replacement supply. Utilization and historical yields cannot establish usable spare product capacity or future switching. Calculations are labeled explicitly; no causal mechanism is inferred from co-occurring series. No predictions, hypothetical flexibility score or automatic purchasing are implemented.

Sources: https://www.eia.gov/petroleum/supply/monthly/pdf/psmnotes.pdf ; https://www.eia.gov/petroleum/supply/weekly/pdf/appendixb.pdf ; https://www.eia.gov/opendata/documentation.php . Live mappings remain blocked.
