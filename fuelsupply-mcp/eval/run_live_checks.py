"""Live validation of curated operator-enabled bindings. Empty registry is a gap."""

import asyncio
import json
import sys

from fuelsupply.config import ROOT, settings
from fuelsupply.models import Query
from fuelsupply.registry import load_registry
from fuelsupply.service import SupplyService


async def main():
    _, bindings = load_registry()
    if not settings.eia_api_key.get_secret_value() or not bindings:
        result = {
            "status": "blocked",
            "executed": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 1,
            "reason": "Missing EIA_API_KEY or verified bindings; no coverage verified.",
        }
    else:
        service = SupplyService(bindings=bindings)
        cases = []
        for fuel, geo, freq in sorted(
            {(b.fuel_family, b.geography, b.frequency) for b in bindings}
        ):
            response = await service.run(
                Query(fuel=fuel, geography=geo, frequency=freq, lookback_periods=3)
            )
            cases.append(
                {
                    "query": {"fuel": fuel, "geography": geo, "frequency": freq},
                    "response": response.model_dump(mode="json"),
                    "pass": response.status in {"ok", "partial"}
                    and bool(response.observation_periods),
                }
            )
        result = {
            "status": "executed",
            "executed": len(cases),
            "passed": sum(x["pass"] for x in cases),
            "failed": sum(not x["pass"] for x in cases),
            "skipped": 0,
            "upstream_requests": service.client.request_count,
            "cases": cases,
        }
    (ROOT / "eval/results/live.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, indent=2))
    return 2 if result["status"] == "blocked" else int(result["failed"] > 0)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
