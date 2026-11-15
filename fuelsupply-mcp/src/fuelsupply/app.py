# MCP composition root: assemble public tools, methodology and prompt, then
# start the stdio transport when main() is invoked by a launcher or CLI.
import logging
import sys

from fastmcp import FastMCP

from fuelsupply.provenance import LIMITATIONS
from fuelsupply.tools import register_tools

# Review path: register_tools -> tools/<name>.py -> SupplyService.run -> EIAClient.
# FastMCP derives the tool schemas from the Query/Result Pydantic annotations.
mcp = FastMCP(
    "FuelSupply MCP",
    instructions=(
        "Public EIA market analysis prototype. Discover coverage "
        "first; clarify products; never infer purchasable fuel, spare"
        " capacity or forecasts."
    ),
)
register_tools(mcp)


@mcp.resource("fuelsupply://methodology")
def methodology() -> str:
    # Expose the same interpretation limits carried in each analytical result.
    return "\n".join(LIMITATIONS)


@mcp.prompt()
def fuel_briefing(question: str) -> str:
    # This is client guidance, not an LLM call or an executed analysis workflow.
    return (
        f"Prepare an evidence-based fuel briefing: {question}. "
        "Discover coverage, clarify products, retrieve weekly conditions "
        "separately from monthly balances. Cite source bindings, observation "
        "and retrieval times, missing components and limitations. "
        "Never infer purchasable quantities or switching capacity."
    )


def main():
    # stdout belongs to MCP JSON-RPC. Keep diagnostics on stderr and suppress
    # HTTP library logs because EIA request URLs contain the server-side API key.
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    logging.getLogger("httpcore").setLevel(logging.CRITICAL)
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
