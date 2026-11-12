# Verified coverage — November 11, 2026

Registry **0.2.0**, **29 verified mappings**, five enabled combinations. Authentication succeeded with a server-side EIA_API_KEY. The key is in a private, gitignored local file and was not displayed or copied into evidence. Earlier missing-key/network-blocker statements describe the historical offline milestone and are superseded by this entry.

| Product | Geography | Frequency | Enabled metrics | Count |
| --- | --- | --- | --- | --- |
| Broad distillate fuel oil (not ULSD) | US | weekly | production, stocks, product supplied, imports, exports | 5 |
| Finished motor gasoline | US | weekly | adjusted net production, stocks, product supplied, imports | 4 |
| Kerosene-type jet fuel (not avgas) | US | weekly | production, stocks, product supplied, imports, exports | 5 |
| Broad distillate fuel oil | US | monthly | stocks, product supplied, imports, exports, stock change, refinery/blender production, biofuels production | 7 |
| Broad distillate fuel oil | PADD1 | monthly | same monthly metrics plus net receipts by pipeline, tanker, barge and rail | 8 |

## Evidence and decisions

Metadata was discovered from petroleum/ through returned child routes and explicit facets. Sanitized metadata and authenticated samples are under docs/sources. `binding-verification.json` records every enabled series, exact labels, two sample periods, matching independently retrieved published-table values, source URLs and SHA256 hashes. HTML evidence is in `published-tables/`. API and table units match: MBBL = Thousand Barrels; MBBL/D = Thousand Barrels per Day. Monthly flow volumes are divided by actual calendar days; stocks remain levels. Exact series facets prevent mixing daily averages and monthly volumes with the same period.

All 29 mappings matched both API and published-table values: 58 observations. Weekly verified sample coverage is October 23–30, 2026; monthly coverage is July–August 2026. Those windows describe reviewed samples, not the full history of the series. Latest-period live checks also succeeded separately.

Finished-gasoline exports are excluded: the EPM0F facet's export series is explicitly described as **Total Motor Gasoline**. The authenticated route metadata states that blending-component exports are included with total motor gasoline exports beginning June 2023. The exact-product definition takes precedence over the facet label. Weekly gasoline production uses the explicitly adjusted series, rather than the unadjusted refinery/blender component.

Monthly refinery/blender and biofuels production remain separately named components. No total-production mapping or unobserved balance term is fabricated. Complete reconciliation therefore returns `partial` / `insufficient_components`. National net receipts are not assumed zero. No refinery utilization or spare-capacity mapping is enabled.

ULSD, blending components, avgas, weekly regional coverage and other PADD monthly combinations remain unverified in this build. Unsupported coverage is not a claim that EIA lacks those data. Diesel, gasoline and jet aliases still require an explicit product choice.

## Evaluation and continuation

79 unit/API tests; 26/26 offline stdio cases; five latest-period live combinations; 18 authenticated stdio cases with 209 observation/calculation checks. See docs/evaluation.md for exact run evidence and limitations. Two-period samples cannot support a seasonal baseline; inventory comparisons correctly return insufficient_history. The custom stock/product-supplied ratio is not EIA's official days-of-supply series or a countdown to exhaustion.

Continue with a small curated metadata subset, authenticated samples and published-table checks for every additional mapping. Version expectations whenever enabled coverage changes. Never copy synthetic test bindings into the production registry. No replay mode, deployment or submission was enabled.
