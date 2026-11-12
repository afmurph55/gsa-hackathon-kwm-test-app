import json
from pathlib import Path

from fuelsupply.config import ROOT
from fuelsupply.models import Binding


def load_registry():
    path = ROOT / "config/series_registry.json"
    if not path.exists():
        path = Path(__file__).parent / "config_data/series_registry.json"
    data = json.loads(path.read_text())
    if len(data["series"]) > 512:
        raise ValueError("Registry exceeds bounded coverage size")
    bindings = [Binding.model_validate(x) for x in data["series"]]
    identities = [
        (x.internal_metric_id, x.fuel_family, x.geography, x.frequency)
        for x in bindings
    ]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate registry bindings")
    return data, bindings
