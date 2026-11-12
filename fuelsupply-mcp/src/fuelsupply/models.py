from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

Fuel = Literal[
    "diesel",
    "distillate",
    "ulsd",
    "gasoline",
    "finished_gasoline",
    "gasoline_blending_components",
    "jet",
    "kerosene_jet",
    "avgas",
]
Geography = Literal["US", "PADD1", "PADD2", "PADD3", "PADD4", "PADD5"]
Frequency = Literal["weekly", "monthly"]


class Query(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(default="", max_length=2000)
    fuel: Fuel
    geography: Geography = "US"
    frequency: Frequency = "weekly"
    observation_cutoff: date | None = None
    lookback_periods: int = Field(default=12, ge=1, le=260)


class Binding(BaseModel):
    model_config = ConfigDict(extra="forbid")
    internal_metric_id: str
    fuel_family: Fuel
    product_definition: str
    geography: Geography
    frequency: Frequency
    route: str = Field(max_length=512)
    facets: dict[str, list[str]] = Field(max_length=10)
    value_column: Literal["value"] = "value"
    units: str
    classification: Literal["stock", "flow", "context"]
    period_convention: str
    observed_coverage: tuple[str, str]
    verified_at: datetime
    source_url: HttpUrl
    methodology_notes: str
    verification_status: Literal["verified"]

    @field_validator("route")
    @classmethod
    def safe_route(cls, v):
        import re

        if not re.fullmatch(r"petroleum/(?:[a-z0-9-]+/)+data/", v):
            raise ValueError("Expected a verified relative petroleum data route")
        return v


class Result(BaseModel):
    text: str
    status: Literal[
        "ok",
        "partial",
        "unsupported",
        "blocked",
        "needs_clarification",
        "out_of_scope",
        "error",
    ]
    mode: Literal["live", "cached", "replay"] = "live"
    resolved_product_definition: str | None = None
    geography: str | None = None
    observation_periods: list[str] = Field(default_factory=list)
    retrieval_timestamp: str | None = None
    metrics: list[dict] = Field(default_factory=list)
    calculations: list[dict] = Field(default_factory=list)
    data_quality_diagnostics: list[str] = Field(default_factory=list)
    source_bindings: list[dict] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    supported_follow_up_actions: list[str] = Field(default_factory=list)
