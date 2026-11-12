from fuelsupply.models import Result
from fuelsupply.provenance import DEFINITIONS, LIMITATIONS
from fuelsupply.registry import load_registry


def register(mcp):
    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
        }
    )
    def discover_fuel_coverage() -> Result:
        """Discover verified EIA fuel/metric/geography/frequency combinations
        before analysis. Diesel, gasoline and jet require explicit product
        choice. Empty coverage means live discovery is blocked, not evidence
        that EIA lacks data."""
        registry, bindings = load_registry()
        return Result(
            text="Verified coverage only; no silent substitutions.",
            status="ok" if bindings else "blocked",
            source_bindings=[b.model_dump(mode="json") for b in bindings],
            metrics=[
                {"definitions": DEFINITIONS, "registry_version": registry["version"]}
            ],
            limitations=LIMITATIONS,
            supported_follow_up_actions=[
                "Configure EIA_API_KEY and EIA network access",
                "Verify curated metadata and samples before enabling mappings",
            ],
        )
