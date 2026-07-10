from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MODEL_PRICING_CATALOG_SCHEMA = "cogeval.model_pricing_catalog.v1"
RATE_PATTERN = r"^(0|[1-9][0-9]{0,11})(\.[0-9]{1,12})?$"
TIMESTAMP_PATTERN = r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=False)


class PricingRates(StrictContractModel):
    input_uncached: str = Field(pattern=RATE_PATTERN)
    input_cache_read: str = Field(pattern=RATE_PATTERN)
    input_cache_write: str = Field(pattern=RATE_PATTERN)
    output: str = Field(pattern=RATE_PATTERN)
    reasoning_output: str = Field(pattern=RATE_PATTERN)


class ModelPrice(StrictContractModel):
    provider_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    rates: PricingRates

    @field_validator("provider_id", "model_id", mode="before")
    @classmethod
    def reject_blank_ids(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            raise ValueError("provider_id and model_id must not be blank")
        return value


class ModelPricingCatalog(StrictContractModel):
    schema_version: Literal["cogeval.model_pricing_catalog.v1"] = Field(alias="schema")
    updated_at: str
    currency: Literal["USD"]
    unit_tokens: Literal[1_000_000]
    prices: list[ModelPrice]

    @property
    def schema(self) -> str:
        return self.schema_version

    @field_validator("updated_at", mode="before")
    @classmethod
    def validate_updated_at(cls, value: object) -> object:
        if not isinstance(value, str) or re.fullmatch(TIMESTAMP_PATTERN, value) is None:
            raise ValueError("updated_at must be a real UTC timestamp in YYYY-MM-DDTHH:MM:SSZ format")
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as exc:
            raise ValueError(
                "updated_at must be a real UTC timestamp in YYYY-MM-DDTHH:MM:SSZ format"
            ) from exc
        return value

    @model_validator(mode="after")
    def reject_duplicate_prices(self) -> "ModelPricingCatalog":
        pairs = [(price.provider_id, price.model_id) for price in self.prices]
        duplicates = sorted({pair for pair in pairs if pairs.count(pair) > 1})
        if duplicates:
            formatted = ", ".join(f"{provider_id}/{model_id}" for provider_id, model_id in duplicates)
            raise ValueError(f"duplicate provider_id + model_id pair: {formatted}")
        return self


def validate_model_pricing_catalog(payload: object) -> ModelPricingCatalog:
    return ModelPricingCatalog.model_validate(payload)
