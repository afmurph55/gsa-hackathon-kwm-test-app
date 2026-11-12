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
    async def explain_regional_supply_balance(query: Query) -> Result:
        """Explain monthly regional supply/disposition with explicit residual
        or insufficient_components; never force reconciliation. Net receipts
        cannot reveal gross source diversification. Weekly input is
        unsupported."""
        return await service.run(query, "balance")
