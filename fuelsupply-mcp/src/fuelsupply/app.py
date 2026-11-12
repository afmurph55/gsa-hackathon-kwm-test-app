import logging
import sys

from fastmcp import FastMCP

from fuelsupply.provenance import LIMITATIONS
from fuelsupply.tools import register_tools

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
    return "\n".join(LIMITATIONS)


@mcp.prompt()
def fuel_briefing(question: str) -> str:
    return (
        f"Prepare an evidence-based fuel briefing: {question}. "
        "Discover coverage, clarify products, retrieve weekly conditions "
        "separately from monthly balances. Cite source bindings, observation "
        "and retrieval times, missing components and limitations. "
        "Never infer purchasable quantities or switching capacity."
    )


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.CRITICAL)
    logging.getLogger("httpcore").setLevel(logging.CRITICAL)
    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
