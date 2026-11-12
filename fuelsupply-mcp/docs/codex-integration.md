# Codex integration

Official reference: https://developers.openai.com/codex/extend/mcp . Inspected installed `codex --version`, `codex mcp --help`, `codex mcp add --help` and `codex exec --help`: codex-cli **0.167.0-alpha.4**. Local CLI is authenticated, but an actual ephemeral execution failed before initialization with `failed to initialize in-process app-server client: Read-only file system (os error 30)`. Evidence: `eval/results/agent-stderr.log`. No model run or tool selection succeeded. No global configuration was changed.

## Exact launch
Executable: `/workspace/fuelsupply-mcp/.venv/bin/fuelsupply-mcp`
Required setup/working directory: `/workspace/fuelsupply-mcp`. Registry/resource paths resolve relative to the installed source location, not tool-supplied paths. Run setup from README first.

Secure environment setup: configure `EIA_API_KEY` using managed secret settings or a secure shell prompt (do not put literal values in commands):

```bash
read -rsp 'EIA API key: ' EIA_API_KEY
export EIA_API_KEY
```

No automatic `.env` loading. Confirm only presence, not value. Grant EIA hosts through environment settings. Never use `codex mcp add --env EIA_API_KEY=literal-secret`, which could persist credentials.

## Transient configuration (no global write)

```bash
codex -c 'mcp_servers.fuelsupply.command="/workspace/fuelsupply-mcp/.venv/bin/fuelsupply-mcp"'   -c 'mcp_servers.fuelsupply.cwd="/workspace/fuelsupply-mcp"'   -c 'mcp_servers.fuelsupply.env_vars=["EIA_API_KEY"]'
```

In an initialized interactive client, inspect MCP tool availability and ask it to call `discover_fuel_coverage`, then call `assess_fuel_supply_conditions` with query `{"fuel":"distillate","geography":"US","frequency":"weekly","lookback_periods":12}`. Expect blocked coverage until live mappings are verified. Use `explain_regional_supply_balance` for monthly PADD questions and ask for explicit residual/missing components.

Persistent registration syntax supported by this CLI, **documented only; do not execute without user approval because it modifies global configuration**:

```bash
codex mcp add fuelsupply -- /workspace/fuelsupply-mcp/.venv/bin/fuelsupply-mcp
codex mcp list
codex mcp get fuelsupply
```

Global registration and secret inheritance require the user's deliberate setup. `mcp list/get` inspect registration, not successful tool calls. There is no `codex mcp call` subcommand in the inspected help. Use an interactive model client for calls, or the generic SDK evaluation below.

## Verified generic client
`/workspace/fuelsupply-mcp/.venv/bin/python /workspace/fuelsupply-mcp/eval/run_protocol_eval.py` launches actual stdio subprocesses, initializes sessions, lists tools/resources/prompts, calls tools, validates structured output and tests error paths. It resets EIA_API_KEY to empty for repeatable offline evaluation. This is protocol verification, not agent selection accuracy.

Troubleshooting: stdio waits silently for client input; stdout must contain only protocol messages. Missing key/registry returns blocked. Read-only Codex app-server initialization requires a supported writable client runtime; no permissions or global settings were changed to bypass it. Re-run agent evaluation there and record model/version/tool events. If API calls fail, inspect sanitized error codes and environment host policy, never paste secrets or raw upstream request URLs.
