"""Authenticated stdio MCP checks against independently table-matched samples.

The operator supplies EIA_API_KEY in the process environment. No key is accepted
as a command argument, loaded automatically, or persisted in evaluation output.
"""

import asyncio
import calendar
import hashlib
import json
import math
import os
from decimal import Decimal
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from fuelsupply.models import Result
from fuelsupply.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]


def references():
    evidence = json.loads((ROOT / "docs/sources/binding-verification.json").read_text())
    return {x["series"]: x for x in evidence["results"] if x["verified"]}


def verify_metrics(result, evidence, bindings):
    checked = 0
    for metric in result.metrics:
        binding = next(b for b in bindings if b.internal_metric_id == metric["metric"])
        series = binding.facets["series"][0]
        captured = {r["period"]: r for r in evidence[series]["rows"]}
        assert len(metric["observations"]) == 2
        for observation in metric["observations"]:
            row = captured[observation["period"]]
            expected = Decimal(row["value"])
            units = "Thousand Barrels"
            if row["units"] == "MBBL/D":
                units = "Thousand Barrels per Day"
            elif binding.frequency == "monthly" and binding.classification == "flow":
                year, month = map(int, row["period"].split("-"))
                expected /= calendar.monthrange(year, month)[1]
                units = "Thousand Barrels per Day"
            assert observation["units"] == units
            assert math.isclose(observation["value"], float(expected), rel_tol=1e-12)
            checked += 1
    return checked


async def main():
    key = os.environ.get("EIA_API_KEY", "")
    if not key:
        print("BLOCKED: EIA_API_KEY is missing")
        return 2
    _, bindings = load_registry()
    evidence = references()
    combinations = sorted({(b.fuel_family, b.geography, b.frequency) for b in bindings})
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    params = StdioServerParameters(
        command=str(ROOT / ".venv/bin/python"),
        args=[str(ROOT / "main.py")],
        cwd=str(ROOT),
        env=env,
    )
    cases, checks = [], 0

    async def call(client, tool, query, selected):
        nonlocal checks
        raw = await client.call_tool(tool, {"query": query})
        assert not raw.is_error
        payload = raw.structured_content
        if payload and "result" in payload:
            payload = payload["result"]
        result = Result.model_validate(payload)
        assert result.status in {"ok", "partial"}
        assert len(result.metrics) == len(selected)
        assert not any(
            "upstream" in x or "incompatible" in x
            for x in result.data_quality_diagnostics
        )
        count = verify_metrics(result, evidence, selected)
        checks += count
        cases.append(
            {
                "tool": tool,
                "query": query,
                "pass": True,
                "observation_checks": count,
                "response": result.model_dump(mode="json"),
            }
        )
        return result

    with (ROOT / "eval/results/live-protocol-stderr.log").open("w") as errors:
        async with stdio_client(params, errlog=errors) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                tools = await client.list_tools()
                assert len(tools.tools) == 5
                await client.read_resource("fuelsupply://methodology")
                await client.get_prompt(
                    "fuel_briefing", {"question": "Compare verified fuels"}
                )
                coverage = await client.call_tool("discover_fuel_coverage", {})
                payload = coverage.structured_content
                if payload and "result" in payload:
                    payload = payload["result"]
                covered = Result.model_validate(payload)
                assert covered.status == "ok" and len(covered.source_bindings) == len(
                    bindings
                )
                cases.append(
                    {
                        "tool": "discover_fuel_coverage",
                        "pass": True,
                        "binding_count": len(bindings),
                    }
                )
                for fuel, geo, frequency in combinations:
                    selected = [
                        b
                        for b in bindings
                        if (b.fuel_family, b.geography, b.frequency)
                        == (fuel, geo, frequency)
                    ]
                    query = {
                        "fuel": fuel,
                        "geography": geo,
                        "frequency": frequency,
                        "lookback_periods": 2,
                        "observation_cutoff": (
                            "2026-10-30" if frequency == "weekly" else "2026-08-31"
                        ),
                    }
                    supply = await call(
                        client, "assess_fuel_supply_conditions", query, selected
                    )
                    assert supply.mode == "live"
                    inventory = await call(
                        client, "compare_inventory_buffer", query, selected
                    )
                    assert inventory.mode == "cached"
                    latest = {
                        m["metric"]: m["observations"][0] for m in inventory.metrics
                    }
                    expected = (
                        latest["stocks"]["value"] / latest["product_supplied"]["value"]
                    )
                    assert math.isclose(
                        inventory.calculations[0]["value"], expected, rel_tol=1e-12
                    )
                    assert inventory.calculations[1]["status"] == "insufficient_history"
                    checks += 1
                    if frequency == "monthly":
                        balance = await call(
                            client, "explain_regional_supply_balance", query, selected
                        )
                        assert (
                            balance.calculations[0]["status"]
                            == "insufficient_components"
                        )
                        assert balance.status == "partial"
                    sourcing = await call(
                        client, "assess_historical_sourcing", query, selected
                    )
                    assert any(
                        "uncommitted purchasable" in x for x in sourcing.limitations
                    )

    result = {
        "status": "executed",
        "executed": len(cases),
        "passed": len(cases),
        "failed": 0,
        "observation_and_calculation_checks": checks,
        "registry_bindings": len(bindings),
        "registry_sha256": hashlib.sha256(
            (ROOT / "config/series_registry.json").read_bytes()
        ).hexdigest(),
        "agent_tool_selection_accuracy": None,
        "note": "Deterministic authenticated MCP client, not a model-agent evaluation. "
        "Pinned periods validate samples; cutoff is not publication vintage.",
        "cases": cases,
    }
    digest = hashlib.sha256()
    for path in sorted((ROOT / "src/fuelsupply").rglob("*.py")):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(path.read_bytes())
    result["source_sha256"] = digest.hexdigest()
    serialized = json.dumps(result, indent=2)
    assert key not in serialized
    (ROOT / "eval/results/live-protocol.json").write_text(serialized + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
