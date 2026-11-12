from fuelsupply.models import Query, Result
from fuelsupply.service import service


def register(mcp):
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": True,
        }
    )
    async def assess_fuel_supply_conditions(query: Query) -> Result:
        """Assess market-level production, stocks, implied demand and trade
        using verified EIA series. Weekly monitoring and monthly structure
        remain separate. Cutoff filters observations, not publication
        vintage. Ambiguous products require clarification; missing mappings
        return blocked/unsupported."""
        return await service.run(query, "conditions")
