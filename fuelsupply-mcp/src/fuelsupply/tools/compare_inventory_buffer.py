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
    async def compare_inventory_buffer(query: Query) -> Result:
        """Compare stocks and custom inventory coverage only for matching
        products, geography, periods and units. The calculated ratio is not
        official EIA days of supply or a countdown. Seasonal baseline uses
        prior five years, minimum three matching years; discloses missing
        years and week 53."""
        # The service checks alignment before the ratio and evaluates seasonal
        # history separately, so a valid ratio can still lack a baseline.
        return await service.run(query, "inventory")
