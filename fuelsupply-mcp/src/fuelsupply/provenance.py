LIMITATIONS = [
    "Product supplied is implied demand, not direct customer sales.",
    (
        "EIA market data cannot establish uncommitted purchasable "
        "fuel, quotes, guaranteed delivery, airport availability, "
        "spare pipeline capacity, or a guaranteed shortage or price "
        "forecast."
    ),
    (
        "Refinery utilization is context, not usable spare product "
        "capacity. Historical yields do not establish feasible or "
        "immediately switchable production."
    ),
    (
        "Historical flows are not confirmed replacement supply; net "
        "receipts alone do not establish source diversification."
    ),
    (
        "Observation cutoffs filter periods, not historical "
        "publication knowledge. Vintage data are unavailable."
    ),
    (
        "Weekly monitoring and monthly structural analysis are "
        "separate; co-occurrence does not establish causation."
    ),
]
DEFINITIONS = {
    "distillate": "Distillate fuel oil (broad product family; not ULSD)",
    ("ulsd"): (
        "Ultra-low sulfur diesel (specific sulfur definition requires"
        " verified metadata)"
    ),
    "finished_gasoline": "Finished motor gasoline (excludes blending components)",
    ("gasoline_blending_components"): (
        "Motor gasoline blending components (not finished motor gasoline)"
    ),
    "kerosene_jet": "Kerosene-type jet fuel (not aviation gasoline)",
    "avgas": "Aviation gasoline (not kerosene-type jet fuel)",
}
