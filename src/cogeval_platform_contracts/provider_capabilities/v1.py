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


class InterfaceParameterSurface(StrictContractModel):
    """Built-in parameter surface owned by the interface contract."""

    path: str = Field(min_length=1)
    values: tuple[str, ...]


INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES: dict[str, dict[str, InterfaceParameterSurface]] = {
    "openai_responses": {
        "thinking_effort": InterfaceParameterSurface(
            path="reasoning.effort",
            values=("minimal", "low", "medium", "high", "xhigh"),
        )
    },
    "anthropic_messages": {
        "thinking_effort": InterfaceParameterSurface(
            path="output_config.effort",
            values=("low", "medium", "high", "xhigh", "max"),
        )
    },
    "anthropic_compatible_messages": {
        "thinking_effort": InterfaceParameterSurface(
            path="output_config.effort",
            values=("low", "medium", "high", "xhigh", "max"),
        )
    },
    "gemini_interactions": {
        "thinking_effort": InterfaceParameterSurface(
            path="generation_config.thinking_level",
            values=("minimal", "low", "medium", "high"),
        )
    },
    "openai_compatible_chat": {
        "thinking_effort": InterfaceParameterSurface(
            path="reasoning_effort",
            values=("high", "max"),
        )
    },
}


class Capability(StrictContractModel):
    """A model-level capability exposed to Workbench and execution config."""

    supported: bool
    values: list[str] = Field(default_factory=list)
    default: str | None = None
    parameter_surface: str | None = Field(default=None, min_length=1)
    adapter_policy: AdapterPolicy = "pass_through"
    value_mapping: dict[str, ValueMappingTarget] = Field(default_factory=dict)
    model_value_labels: dict[str, str] = Field(default_factory=dict)
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
        unknown_mapped_values = sorted(set(self.value_mapping) - set(self.values))
        if unknown_mapped_values:
            raise ValueError(
                "value_mapping keys must be declared capability values: "
                f"{', '.join(unknown_mapped_values)}"
            )
        unknown_label_values = sorted(set(self.model_value_labels) - set(self.values))
        if unknown_label_values:
            raise ValueError(
                "model_value_labels keys must be declared capability values: "
                f"{', '.join(unknown_label_values)}"
            )
        blank_labels = sorted(key for key, label in self.model_value_labels.items() if not label.strip())
        if blank_labels:
            raise ValueError(
                "model_value_labels values must not be blank: "
                f"{', '.join(blank_labels)}"
            )
        return self


class ProviderInterface(StrictContractModel):
    interface: str = Field(min_length=1)
    display_name: str | None = None
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
        interface_surfaces = {
            interface.interface: set(
                INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES.get(interface.interface, {})
            )
            for interface in self.interfaces
        }
        for model in self.models:
            for capability_name, capability in model.capabilities.items():
                _validate_platform_capability_values(capability_name, capability, f"model {model.model_id} capability {capability_name}")
            for interface_name, capabilities in model.interface_capabilities.items():
                if interface_name not in interface_surfaces:
                    raise ValueError(f"model {model.model_id} references unknown interface: {interface_name}")
                for capability_name, capability in capabilities.items():
                    model_capability = model.capabilities.get(capability_name)
                    if model_capability is None:
                        raise ValueError(
                            f"model {model.model_id} interface {interface_name} capability {capability_name} "
                            "requires a model-level capability declaration"
                        )
                    unsupported_interface_values = sorted(set(capability.values) - set(model_capability.values))
                    if unsupported_interface_values:
                        raise ValueError(
                            f"model {model.model_id} interface {interface_name} capability {capability_name} "
                            "contains values not declared by the model-level capability: "
                            f"{', '.join(unsupported_interface_values)}"
                        )
                    if capability.model_value_labels:
                        raise ValueError(
                            f"model {model.model_id} interface {interface_name} capability {capability_name} "
                            "must not declare model_value_labels; use the model-level capability"
                        )
                    _validate_platform_capability_values(
                        capability_name,
                        capability,
                        f"model {model.model_id} interface {interface_name} capability {capability_name}",
                    )
                    _validate_interface_capability_surface(
                        interface_name=interface_name,
                        capability_name=capability_name,
                        capability=capability,
                        location=f"model {model.model_id} interface {interface_name} capability {capability_name}",
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
    invalid.extend(sorted(set(capability.model_value_labels) - THINKING_EFFORT_VALUES))
    if capability.default is not None and capability.default not in THINKING_EFFORT_VALUES:
        invalid.append(capability.default)
    if invalid:
        raise ValueError(f"{location} contains unsupported thinking effort values: {', '.join(sorted(set(invalid)))}")


def _validate_interface_capability_surface(
    *,
    interface_name: str,
    capability_name: str,
    capability: Capability,
    location: str,
) -> None:
    if capability_name != "thinking_effort":
        return
    if not capability.supported:
        return
    if capability.parameter_surface is None:
        raise ValueError(f"{location} must declare parameter_surface")
    interface_surfaces = INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES.get(interface_name)
    if not interface_surfaces:
        raise ValueError(f"{location} references interface without built-in thinking effort surfaces: {interface_name}")
    surface = interface_surfaces.get(capability.parameter_surface)
    if surface is None:
        raise ValueError(f"{location} references unknown parameter surface: {capability.parameter_surface}")

    surface_values = set(surface.values)
    for platform_value, target in capability.value_mapping.items():
        if platform_value == "default":
            raise ValueError(f"{location} must not map default; omit the interface parameter instead")
        _validate_interface_thinking_effort_target(
            location=location,
            platform_value=platform_value,
            target=target,
            surface_values=surface_values,
        )
    for platform_value in capability.values:
        if platform_value == "default":
            continue
        if platform_value in capability.value_mapping:
            continue
        _validate_interface_thinking_effort_target(
            location=location,
            platform_value=platform_value,
            target=platform_value,
            surface_values=surface_values,
        )


def _validate_interface_thinking_effort_target(
    *,
    location: str,
    platform_value: str,
    target: ValueMappingTarget,
    surface_values: set[str],
) -> None:
    if not isinstance(target, str):
        raise ValueError(
            f"{location} maps {platform_value} to a non-string interface thinking effort value"
        )
    if target not in surface_values:
        raise ValueError(
            f"{location} maps {platform_value} to unsupported interface thinking effort value: {target}"
        )
