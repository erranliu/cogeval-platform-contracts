from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


MODEL_CAPABILITY_CATALOG_SCHEMA = "cogeval.model_capability_catalog.v1"
ThinkingEffortPlatformValue = Literal["default", "minimal", "low", "medium", "high", "xhigh", "max"]
THINKING_EFFORT_VALUES = set(ThinkingEffortPlatformValue.__args__)


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ModelThinkingEffortCapability(StrictContractModel):
    values: list[ThinkingEffortPlatformValue] = Field(default_factory=list)
    default: ThinkingEffortPlatformValue | None = None
    model_value_labels: dict[ThinkingEffortPlatformValue, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_shape(self) -> "ModelThinkingEffortCapability":
        if not self.values:
            raise ValueError("thinking_effort values must not be empty")
        if len(set(self.values)) != len(self.values):
            raise ValueError("thinking_effort values must be unique")
        if self.default is not None and self.default not in self.values:
            raise ValueError("thinking_effort default must be one of values")
        unknown_labels = sorted(set(self.model_value_labels) - set(self.values))
        if unknown_labels:
            raise ValueError(
                "model_value_labels keys must be declared thinking_effort values: "
                f"{', '.join(unknown_labels)}"
            )
        blank_labels = sorted(key for key, label in self.model_value_labels.items() if not label.strip())
        if blank_labels:
            raise ValueError(
                "model_value_labels values must not be blank: "
                f"{', '.join(blank_labels)}"
            )
        return self


class ModelCapability(StrictContractModel):
    model_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    status: Literal["supported", "preview", "deprecated"] = "supported"
    recommended: bool = False
    capability_tags: list[str] = Field(default_factory=list)
    thinking_effort: ModelThinkingEffortCapability | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class ModelCapabilityCatalog(StrictContractModel):
    schema_version: Literal["cogeval.model_capability_catalog.v1"] = Field(
        default=MODEL_CAPABILITY_CATALOG_SCHEMA,
        alias="schema",
    )
    updated_at: str = Field(min_length=1)
    models: list[ModelCapability] = Field(min_length=1)
    metadata: dict[str, object] = Field(default_factory=dict)

    @property
    def schema(self) -> str:
        return self.schema_version

    @model_validator(mode="after")
    def validate_unique_models(self) -> "ModelCapabilityCatalog":
        ids = [model.model_id for model in self.models]
        duplicates = sorted({model_id for model_id in ids if ids.count(model_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate model_id values: {', '.join(duplicates)}")
        return self


def validate_model_capability_catalog(payload: object) -> ModelCapabilityCatalog:
    return ModelCapabilityCatalog.model_validate(payload)
