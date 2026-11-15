import json
from pathlib import Path

from fuelsupply.config import ROOT
from fuelsupply.models import Binding


def load_registry():
    # Source checkouts use config/; installed wheels carry the same registry
    # under config_data/. Loading validates structure, not new EIA coverage:
    # operators must verify metadata and samples before adding a binding.
    path = ROOT / "config/series_registry.json"
    if not path.exists():
        path = Path(__file__).parent / "config_data/series_registry.json"
    data = json.loads(path.read_text())
    if len(data["series"]) > 512:
        raise ValueError("Registry exceeds bounded coverage size")
    bindings = [Binding.model_validate(x) for x in data["series"]]
    # A metric has one binding per exact product/geography/frequency. Reject
    # duplicates rather than silently selecting a series or double-counting it.
    identities = [
        (x.internal_metric_id, x.fuel_family, x.geography, x.frequency)
        for x in bindings
    ]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate registry bindings")
    return data, bindings
