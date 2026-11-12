from fuelsupply.tools import (
    assess_fuel_supply_conditions,
    assess_historical_sourcing,
    compare_inventory_buffer,
    discover_fuel_coverage,
    explain_regional_supply_balance,
)


def register_tools(mcp):
    for module in (
        discover_fuel_coverage,
        assess_fuel_supply_conditions,
        compare_inventory_buffer,
        explain_regional_supply_balance,
        assess_historical_sourcing,
    ):
        module.register(mcp)
