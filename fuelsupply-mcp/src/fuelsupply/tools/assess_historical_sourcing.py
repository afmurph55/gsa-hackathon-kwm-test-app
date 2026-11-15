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
    async def assess_historical_sourcing(query: Query) -> Result:
        """Describe historical production, imports, exports and interregional
        net receipts where verified. Historical flows cannot confirm
        replacement supply, purchasing availability, refinery switching or
        spare pipeline capacity."""
        # This purpose also requires net receipts for completeness. It reports
        # historical evidence without selecting suppliers or inferring capacity.
        return await service.run(query, "sourcing")
