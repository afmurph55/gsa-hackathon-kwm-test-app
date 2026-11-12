"""Real stdio MCP testing; synthetic upstream results are never market evidence."""

import asyncio
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from fuelsupply.models import Result

ROOT = Path(__file__).resolve().parents[1]


def check(case, result):
    expected = case["expected_behavior"]
    assert result.is_error == expected.get("is_error", False), (
        "unexpected MCP error state"
    )
    raw = result.model_dump_json()
    assert "SYNTHETIC-SECRET-DO-NOT-LEAK" not in raw, "credential leak"
    if result.is_error:
        return False
    payload = result.structured_content
    if payload and "result" in payload:
        payload = payload["result"]
    out = Result.model_validate(payload)
    for key in ["status", "mode"]:
        if key in expected:
            assert getattr(out, key) == expected[key], key
    if expected.get("no_metrics"):
        assert not out.metrics
    if "period" in expected:
        assert expected["period"] in out.observation_periods
    if "metric_count" in expected:
        assert len(out.metrics) == expected["metric_count"]
    if "limitation" in expected:
        assert expected["limitation"] in " ".join(out.limitations)
    if "diagnostic" in expected:
        assert any(expected["diagnostic"] in x for x in out.data_quality_diagnostics)
    if "coverage_value" in expected:
        assert out.calculations[0]["value"] == expected["coverage_value"]
    if "seasonal_status" in expected:
        assert out.calculations[1]["status"] == expected["seasonal_status"]
    if "balance_status" in expected:
        assert out.calculations[0]["status"] == expected["balance_status"]
    return True


async def main():
    cases = [
        json.loads(line)
        for line in (ROOT / "eval/cases.jsonl").read_text().splitlines()
    ]
    results = []
    synthetic_requests = 0
    for fixture in ["production", "synthetic"]:
        env = {k: v for k, v in os.environ.items() if k != "EIA_API_KEY"}
        env["EIA_API_KEY"] = ""
        args = (
            [str(ROOT / "main.py")]
            if fixture == "production"
            else ["-m", "tests.protocol_server"]
        )
        params = StdioServerParameters(
            command=str(ROOT / ".venv/bin/python"), args=args, cwd=str(ROOT), env=env
        )
        started = time.perf_counter()
        with (ROOT / f"eval/results/{fixture}-stderr.log").open("w") as errors:
            async with stdio_client(params, errlog=errors) as (read, write):
                async with ClientSession(read, write) as client:
                    await client.initialize()
                    tools = await client.list_tools()
                    names = {x.name for x in tools.tools}
                    assert names == {
                        "discover_fuel_coverage",
                        "assess_fuel_supply_conditions",
                        "compare_inventory_buffer",
                        "explain_regional_supply_balance",
                        "assess_historical_sourcing",
                    }
                    startup_ms = (time.perf_counter() - started) * 1000
                    resources = await client.list_resources()
                    assert resources.resources
                    await client.read_resource("fuelsupply://methodology")
                    prompts = await client.list_prompts()
                    assert prompts.prompts
                    await client.get_prompt(
                        "fuel_briefing", {"question": "Compare distillate and jet"}
                    )
                    for case in [c for c in cases if c["fixture"] == fixture]:
                        start = time.perf_counter()
                        response = await client.call_tool(case["tool"], case["input"])
                        elapsed = (time.perf_counter() - start) * 1000
                        try:
                            schema_valid = check(case, response)
                            passed, failure = True, None
                        except Exception as exc:
                            passed, failure, schema_valid = False, str(exc), False
                        results.append(
                            {
                                "case_id": case["case_id"],
                                "fixture": fixture,
                                "pass": passed,
                                "failure": failure,
                                "schema_valid": schema_valid,
                                "expected_protocol_error": case[
                                    "expected_behavior"
                                ].get("is_error", False),
                                "latency_ms": elapsed,
                                "startup_ms": startup_ms,
                                "response": response.model_dump(mode="json"),
                            }
                        )
                    if fixture == "synthetic":
                        stats = await client.read_resource("test://request-count")
                        synthetic_requests = int(stats.contents[0].text)
    samples = [x["latency_ms"] for x in results]
    version = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    digest = hashlib.sha256()
    for p in sorted((ROOT / "src/fuelsupply").rglob("*.py")):
        digest.update(p.relative_to(ROOT).as_posix().encode())
        digest.update(p.read_bytes())
    summary = {
        "executed": len(results),
        "passed": sum(x["pass"] for x in results),
        "failed": sum(not x["pass"] for x in results),
        "skipped": 0,
        "schema_valid_responses": sum(x["schema_valid"] for x in results),
        "nonerror_responses": sum(not x["expected_protocol_error"] for x in results),
        "latency_ms": {
            "n": len(samples),
            "min": min(samples),
            "median": statistics.median(samples),
            "p95_nearest_rank": sorted(samples)[math.ceil(0.95 * len(samples)) - 1],
            "max": max(samples),
        },
        "live_checks": "separate_run_see_live_json",
        "agent_evaluation": "not_run_by_this_harness",
        "tool_selection_accuracy": None,
        "real_upstream_requests": 0,
        "synthetic_upstream_requests": synthetic_requests,
        "python": platform.python_version(),
        "dependencies": {
            name: importlib.metadata.version(name)
            for name in ["fastmcp", "mcp", "httpx", "pydantic"]
        },
        "base_revision": version,
        "source_sha256": digest.hexdigest(),
        "registry_version": json.loads(
            (ROOT / "config/series_registry.json").read_text()
        )["version"],
    }
    for fixture in ["production", "synthetic"]:
        for mode in ["live", "cached"]:
            group = [
                x["latency_ms"]
                for x in results
                if x["fixture"] == fixture
                and (x["response"].get("structured_content") or {}).get("mode") == mode
            ]
            summary[f"{fixture}_{mode}_latency_ms"] = {
                "n": len(group),
                "median": statistics.median(group) if group else None,
            }
    (ROOT / "eval/results/protocol.json").write_text(
        json.dumps({"summary": summary, "cases": results}, indent=2)
    )
    print(json.dumps(summary, indent=2))
    return int(summary["failed"] > 0)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
