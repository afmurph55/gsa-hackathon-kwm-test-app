# Sandbox security and reliability

This is a local public-data prototype, without production security certification, agency authorization or compliance attestation. Only stdio is enabled by FuelSupply's entry point. Inherited example HTTP code and vendor deployment kits are reference material and are not registered by FuelSupply. No external tracing/telemetry SDK is initialized.

| Threat | Implemented control | Evidence / residual risk |
| --- | --- | --- |
| Agent-induced SSRF or credential exfiltration | fixed https://api.eia.gov/v2/ origin; validated petroleum data routes; no caller URL or route parameter; redirects disabled | route and 302 tests; operator registry and environment policy still trusted |
| Credentials in upstream failures or traces | environment SecretStr; generic error codes; HTTP loggers suppressed; upstream bodies/headers/URLs not returned | synthetic secret assertions in protocol and API tests; no real key present |
| Unbounded requests or denial of service | 1–260 periods; at most 16 metrics/query; 3 pages/metric; <=100 rows/page; 2 MiB response cap; semaphore 2 | pagination/concurrency/oversize tests; many separate callers could still cause load |
| Slow/rate-limited EIA | 5s connect/20s HTTP timeout; at most 3 attempts; eligible transient statuses 429/502/503/504 and transport errors; Retry-After <=5s honored, longer delays return retry_later | mock tests; no live latency claim; HTTP timeout is per network operation, not total tool deadline |
| Retry amplification or bad credentials | no retries for 400/401/403, redirects or other permanent statuses | request-count tests; operator fixes credentials without exposing value |
| Poisoned numeric observations | numeric/nonfinite/missing parsing; exact unit and period checks; duplicates rejected; mismatched products suppress calculations | deterministic tests; upstream remains authoritative but not infallible |
| Stale or misleading cache | in-memory LRU capacity 64, TTL300s, original retrieval times, cached mode | expiry/copy/eviction and protocol cached cases; no persistence or silent replay |
| Prompt injection in data | numeric observations only, validated periods; fixed limitations; upstream metadata not interpreted as instructions | human registry review required; model client must also treat output as data |
| Sensitive or procurement data misuse | no file read, shell, purchasing or arbitrary fetch tools; public-data-only origin | tool-list test; no operational or personal files read/exposed |

Environment HTTP proxy and CA trust are inherited to comply with this managed runtime. Unlike the starter's generic helper, FuelSupply does not disable the required managed proxy. Destination-policy denials remain in force. Fixed application origins and disabled redirects are additional controls, not a proxy bypass.

Operational limits: no rate limit shared across processes, no operator authentication service, no tamper-evident data store, no formal security audit. The registry is operator-controlled; its status field alone is not scientific verification. Test fixtures use fake credentials and synthetic definitions and must never be promoted into real coverage.
