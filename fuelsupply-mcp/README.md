# FuelSupply MCP
Local Dataset Access Server prototype for the GSA MCP Hackathon. Proposed users are government transportation, aviation, logistics and energy analysts; no agency adoption is claimed.

**Status: authenticated EIA discovery and live evaluation passed for a curated subset.** Registry 0.2.0 enables 29 mappings across five product/geography/frequency combinations, each checked against authenticated samples and independently published EIA tables. Monthly balances remain incomplete; finished-gasoline exports are intentionally excluded because the upstream series includes blending components. See docs/coverage.md and docs/evaluation.md. Historical submission binaries retain the earlier offline milestone and have not been regenerated.

## Setup and run
Python >=3.11; restored and tested here with Python 3.13.1. Follow the committed uv lockfile. Use the actual restored directory on this Mac; `/workspace` is read-only on this host.

```bash
cd fuelsupply-mcp
export UV_CACHE_DIR="$PWD/../work/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/../work/uv-python"
uv sync --locked --group dev --python "$(command -v python3)"
export PYTHONPATH="$PWD/src"
.venv/bin/pytest tests -q
.venv/bin/python eval/run_protocol_eval.py
```

Set EIA_API_KEY in the server process environment. The server does not automatically load .env. For the private, gitignored `.env` already saved on this Mac, explicitly load it for an evaluation:

```bash
.venv/bin/python -m dotenv -f .env run -- .venv/bin/python eval/run_live_checks.py
.venv/bin/python -m dotenv -f .env run -- .venv/bin/python eval/run_live_protocol_eval.py
```

The live check exits 2 if credentials or verified bindings are missing. The offline protocol harness intentionally removes the key and uses version-2 expectations for the populated registry; version 1 is preserved in eval/cases-v1-empty-registry.jsonl. Live protocol cases use pinned sample periods and independent Decimal arithmetic; they are deterministic SDK calls, not model-agent usability scores.

To launch the stdio server for a client, use `.venv/bin/python main.py` with this working directory, PYTHONPATH, and EIA_API_KEY in its environment. It waits for MCP input. Never put keys in command arguments, logs, registry files or committed files. No automatic key registration, deployment, submission, publication or tracing.

## Tools
Each analytical tool accepts a Pydantic `query` object with `fuel`, `geography` (`US`, `PADD1`–`PADD5`), `frequency` (`weekly`/`monthly`), optional `observation_cutoff`, bounded `lookback_periods` (1–260), and optional briefing context `text` (maximum 2,000 characters). Context does not expand data access permissions.

| Tool | Analyst goal |
| --- | --- |
| discover_fuel_coverage | Discover exact verified combinations and product ambiguities |
| assess_fuel_supply_conditions | Inspect production, stocks, implied demand and trade |
| compare_inventory_buffer | Inspect stock history, compatible custom coverage and seasonal evidence |
| explain_regional_supply_balance | Reconcile monthly components or expose missing components/residuals |
| assess_historical_sourcing | Inspect observed supply components with replacement-supply limits |

Example MCP arguments: `{"query":{"fuel":"distillate","geography":"US","frequency":"weekly","lookback_periods":12}}`. Expected here: `blocked`, no observations. Use `kerosene_jet` for jet fuel; `diesel`, `gasoline`, and `jet` request clarification. No automatic substitution of broad distillate for ULSD or finished gasoline for blending components.

Resource: `fuelsupply://methodology`. Prompt: `fuel_briefing`.

## Evidence and deliverables
- [Requirements matrix](docs/requirements-matrix.md), [coverage](docs/coverage.md), [methodology](docs/methodology.md), [security](docs/security.md)
- [Evaluation](docs/evaluation.md) and machine-readable results in `eval/results/`
- [Demo script](docs/demo-script.md), [Codex integration](docs/codex-integration.md)
- [Presentation](submission/presentation.pptx), [evaluation document](submission/evaluation-document.md), [submission checklist](docs/submission-checklist.md)

No public deployment, GitHub push, registry publication or submission has occurred. Inherited vendor deployment kits are educational references, not authorization or verified FuelSupply deployment paths. Optional prices/charts/dashboard are not implemented.

## Foundation and license
Adapted from [https://github.com/GSA-TTS/mcp-hackathon-template](https://github.com/GSA-TTS/mcp-hackathon-template) at `f39249f1768309e3ef8b31742390a4f3a656b5f3`. The original MIT [LICENSE](LICENSE), SECURITY policy, QUICKSTART, example package/tests, deployment references and attribution remain. Original README is preserved in `docs/sources/template-README.md`. FuelSupply entry points run only the FuelSupply tools. The inherited example package is retained for attribution/reference and its tests are reported separately.
