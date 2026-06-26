from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


SCHEMA_VERSION = "cogeval.provider_capability_catalog.v1"

EffortValue = Literal["default", "minimal", "low", "medium", "high", "xhigh", "max"]
AdapterPolicy = Literal["pass_through", "map_values", "unsupported", "drop_with_warning"]
MappedParameterValue = str | int | float | bool | None
ValueMappingTarget = str | dict[str, MappedParameterValue]
THINKING_EFFORT_VALUES = set(EffortValue.__args__)


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ParameterSurface(StrictContractModel):
    """How a provider interface accepts a capability control."""

    path: str = Field(min_length=1)
    values: list[str] = Field(default_factory=list)
    value_mapping: dict[str, ValueMappingTarget] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Capability(StrictContractModel):
    """A model-level capability exposed to Workbench and execution config."""

    supported: bool
    values: list[str] = Field(default_factory=list)
    default: str | None = None
    parameter_surface: str | None = Field(default=None, min_length=1)
    adapter_policy: AdapterPolicy = "pass_through"
    value_mapping: dict[str, ValueMappingTarget] = Field(default_factory=dict)
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
    interface_capabilities: dict[str, dict[str, Capability]] = Field(default_factory=dict)
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
        interface_surfaces = {
            interface.interface: set(interface.parameter_surfaces)
            for interface in self.interfaces
        }
        for model in self.models:
            for capability_name, capability in model.capabilities.items():
                _validate_platform_capability_values(capability_name, capability, f"model {model.model_id} capability {capability_name}")
                if capability.parameter_surface and capability.parameter_surface not in surfaces:
                    raise ValueError(
                        f"model {model.model_id} capability {capability_name} references unknown parameter surface: "
                        f"{capability.parameter_surface}"
                    )
            for interface_name, capabilities in model.interface_capabilities.items():
                if interface_name not in interface_surfaces:
                    raise ValueError(f"model {model.model_id} references unknown interface: {interface_name}")
                for capability_name, capability in capabilities.items():
                    _validate_platform_capability_values(
                        capability_name,
                        capability,
                        f"model {model.model_id} interface {interface_name} capability {capability_name}",
                    )
                    if capability.parameter_surface and capability.parameter_surface not in interface_surfaces[interface_name]:
                        raise ValueError(
                            f"model {model.model_id} interface {interface_name} capability {capability_name} "
                            f"references unknown parameter surface: {capability.parameter_surface}"
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


def _validate_platform_capability_values(capability_name: str, capability: Capability, location: str) -> None:
    if capability_name != "thinking_effort":
        return
    values = set(capability.values)
    invalid = sorted(values - THINKING_EFFORT_VALUES)
    invalid.extend(sorted(set(capability.value_mapping) - THINKING_EFFORT_VALUES))
    if capability.default is not None and capability.default not in THINKING_EFFORT_VALUES:
        invalid.append(capability.default)
    if invalid:
        raise ValueError(f"{location} contains unsupported thinking effort values: {', '.join(sorted(set(invalid)))}")
