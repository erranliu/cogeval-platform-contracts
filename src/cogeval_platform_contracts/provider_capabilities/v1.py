from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SCHEMA_VERSION = "cogeval.provider_capability_catalog.v1"

EffortValue = Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]
AdapterPolicy = Literal["pass_through", "map_values", "unsupported", "drop_with_warning"]


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ParameterSurface(StrictContractModel):
    """How a provider interface accepts a capability control."""

    path: str = Field(min_length=1)
    values: list[str] = Field(default_factory=list)
    value_mapping: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Capability(StrictContractModel):
    """A model-level capability exposed to Workbench and execution config."""

    supported: bool
    values: list[str] = Field(default_factory=list)
    default: str | None = None
    parameter_surface: str | None = Field(default=None, min_length=1)
    adapter_policy: AdapterPolicy = "pass_through"
    value_mapping: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("values")
    @classmethod
    def require_non_empty_values(cls, values: list[str]) -> list[str]:
        for value in values:
            if not value.strip():
                raise ValueError("capability values must not be blank")
        return values

    @model_validator(mode="after")
    def validate_supported_shape(self) -> "Capability":
        if self.supported and not self.values:
            raise ValueError("supported capabilities must declare values")
        if self.default is not None and self.default not in self.values:
            raise ValueError("capability default must be one of values")
        if not self.supported and self.default is not None:
            raise ValueError("unsupported capabilities must not declare default")
        return self


class ProviderInterface(StrictContractModel):
    interface: str = Field(min_length=1)
    display_name: str | None = None
    parameter_surfaces: dict[str, ParameterSurface] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProviderModel(StrictContractModel):
    model_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    model_name: str = Field(min_length=1)
    capabilities: dict[str, Capability] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Provider(StrictContractModel):
    provider_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    status: Literal["supported", "preview", "deprecated"] = "supported"
    interfaces: list[ProviderInterface] = Field(default_factory=list)
    models: list[ProviderModel] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_unique_children(self) -> "Provider":
        _require_unique([item.interface for item in self.interfaces], "interface")
        _require_unique([item.model_id for item in self.models], "model_id")
        surfaces = {
            surface_name
            for interface in self.interfaces
            for surface_name in interface.parameter_surfaces
        }
        for model in self.models:
            for capability_name, capability in model.capabilities.items():
                if capability.parameter_surface and capability.parameter_surface not in surfaces:
                    raise ValueError(
                        f"model {model.model_id} capability {capability_name} references unknown parameter surface: "
                        f"{capability.parameter_surface}"
                    )
        return self


class ProviderCapabilityCatalog(StrictContractModel):
    schema_version: Literal["cogeval.provider_capability_catalog.v1"] = Field(
        default=SCHEMA_VERSION,
        alias="schema",
    )
    updated_at: str = Field(min_length=1)
    providers: list[Provider] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def schema(self) -> str:
        return self.schema_version

    @model_validator(mode="after")
    def validate_unique_providers(self) -> "ProviderCapabilityCatalog":
        _require_unique([item.provider_id for item in self.providers], "provider_id")
        return self


def _require_unique(values: list[str], field_name: str) -> None:
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise ValueError(f"duplicate {field_name} values: {', '.join(duplicates)}")

