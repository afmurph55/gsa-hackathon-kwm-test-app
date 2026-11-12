# gsa-hackathon-kwm-test-app

## FuelSupply MCP

[FuelSupply](fuelsupply-mcp/README.md) provides read-only EIA petroleum analysis with 29 verified mappings and authenticated evaluation evidence. Start with its setup instructions and [current evaluation report](fuelsupply-mcp/docs/authenticated-evaluation-2026-11-11.md).

FuelSupply lives in its own directory alongside the existing MCP toolkit. Its inherited template attribution and MIT license are retained inside that directory. Historical submission artifacts are labeled as the earlier offline milestone; they have not been submitted or deployed.

Existing project planning remains in [gsa-kwm2-mcp-toolkit-plan.md](gsa-kwm2-mcp-toolkit-plan.md); the existing servers remain in mcp_server/ and toolkits/.

## Interactive FuelSupply dashboard

The [local dashboard](fuelsupply-mcp/dashboard/README.md) adds fuel and geography filters, inventory/production charts, source-linked observation tables, CSV export and PDF printing. It includes a saved EIA snapshot and an optional loopback-only server for authenticated refresh. The EIA key stays on the local server; this change does not deploy a hosted dashboard.
