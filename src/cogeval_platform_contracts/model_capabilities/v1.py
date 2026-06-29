from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MODEL_CAPABILITY_CATALOG_SCHEMA = "cogeval.model_capability_catalog.v1"
ThinkingEffortPlatformValue = Literal["default", "minimal", "low", "medium", "high", "xhigh", "max"]
ProviderInterfaceId = Literal["openai_responses", "openai_compatible_chat", "anthropic_compatible_messages"]
BuiltInAccountAgentId = Literal["codex_cli", "claude_code_cli"]
ModelInterfaceAdapterPolicy = Literal["omit_default", "map_values"]
THINKING_EFFORT_VALUES = set(ThinkingEffortPlatformValue.__args__)


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class InterfaceThinkingEffortSurface(StrictContractModel):
    surface: Literal["thinking_effort"] = "thinking_effort"
    path: str = Field(min_length=1)
    platform_values: list[ThinkingEffortPlatformValue] = Field(min_length=1)
    value_mapping: dict[ThinkingEffortPlatformValue, str | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_shape(self) -> "InterfaceThinkingEffortSurface":
        if len(set(self.platform_values)) != len(self.platform_values):
            raise ValueError("interface thinking_effort platform_values must be unique")
        unknown_mapping_values = sorted(set(self.value_mapping) - set(self.platform_values))
        if unknown_mapping_values:
            raise ValueError(
                "interface thinking_effort value_mapping keys must be declared platform_values: "
                f"{', '.join(unknown_mapping_values)}"
            )
        missing_mapping_values = sorted(set(self.platform_values) - set(self.value_mapping))
        if missing_mapping_values:
            raise ValueError(
                "interface thinking_effort value_mapping must cover platform_values: "
                f"{', '.join(missing_mapping_values)}"
            )
        if self.value_mapping.get("default") is not None:
            raise ValueError("interface thinking_effort default must map to null")
        return self


class ProviderInterfaceCapabilityContract(StrictContractModel):
    thinking_effort: InterfaceThinkingEffortSurface | None = None


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


class ModelInterfaceThinkingEffortCapability(StrictContractModel):
    values: list[ThinkingEffortPlatformValue] = Field(default_factory=list)
    parameter_surface: Literal["thinking_effort"]
    adapter_policy: ModelInterfaceAdapterPolicy = "map_values"

    @model_validator(mode="after")
    def validate_shape(self) -> "ModelInterfaceThinkingEffortCapability":
        if len(set(self.values)) != len(self.values):
            raise ValueError("interface thinking_effort values must be unique")
        return self


class ModelInterfaceCapability(StrictContractModel):
    thinking_effort: ModelInterfaceThinkingEffortCapability | None = None


class ModelCapability(StrictContractModel):
    model_id: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    status: Literal["supported", "preview", "deprecated"] = "supported"
    recommended: bool = False
    capability_tags: list[str] = Field(default_factory=list)
    thinking_effort: ModelThinkingEffortCapability | None = None
    interface_capabilities: dict[ProviderInterfaceId, ModelInterfaceCapability] = Field(
        default_factory=dict
    )
    metadata: dict[str, object] = Field(default_factory=dict)


class BuiltInAccountCapability(StrictContractModel):
    agent_id: BuiltInAccountAgentId
    display_name: str = Field(min_length=1)
    model_ids: list[str] = Field(default_factory=list)

    @field_validator("model_ids")
    @classmethod
    def validate_model_ids(cls, model_ids: list[str]) -> list[str]:
        blank_ids = [model_id for model_id in model_ids if not model_id.strip()]
        if blank_ids:
            raise ValueError("built-in account model_ids must not contain blank values")
        duplicates = sorted({model_id for model_id in model_ids if model_ids.count(model_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate built-in account model_ids: {', '.join(duplicates)}")
        return model_ids


class ModelCapabilityCatalog(StrictContractModel):
    schema_version: Literal["cogeval.model_capability_catalog.v1"] = Field(
        default=MODEL_CAPABILITY_CATALOG_SCHEMA,
        alias="schema",
    )
    updated_at: str = Field(min_length=1)
    interfaces: dict[ProviderInterfaceId, ProviderInterfaceCapabilityContract]
    models: list[ModelCapability] = Field(min_length=1)
    built_in_account_capabilities: list[BuiltInAccountCapability] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    @property
    def schema(self) -> str:
        return self.schema_version

    @model_validator(mode="after")
    def validate_catalog_references(self) -> "ModelCapabilityCatalog":
        ids = [model.model_id for model in self.models]
        duplicates = sorted({model_id for model_id in ids if ids.count(model_id) > 1})
        if duplicates:
            raise ValueError(f"duplicate model_id values: {', '.join(duplicates)}")
        for model in self.models:
            model_values = set(model.thinking_effort.values) if model.thinking_effort else set()
            for interface_id, capability in model.interface_capabilities.items():
                interface_contract = self.interfaces.get(interface_id)
                if interface_contract is None:
                    raise ValueError(f"model {model.model_id} references unknown interface: {interface_id}")
                if capability.thinking_effort is None:
                    continue
                if interface_contract.thinking_effort is None:
                    raise ValueError(
                        f"model {model.model_id} interface {interface_id} references missing thinking_effort contract"
                    )
                unsupported_by_model = sorted(set(capability.thinking_effort.values) - model_values)
                if unsupported_by_model:
                    raise ValueError(
                        "interface thinking_effort values must be declared by model: "
                        f"{', '.join(unsupported_by_model)}"
                    )
                interface_values = set(interface_contract.thinking_effort.platform_values)
                unsupported_by_interface = sorted(set(capability.thinking_effort.values) - interface_values)
                if unsupported_by_interface:
                    raise ValueError(
                        "interface thinking_effort values must be supported by interface contract: "
                        f"{', '.join(unsupported_by_interface)}"
                    )
                interface_value_mapping = interface_contract.thinking_effort.value_mapping
                mapped_values = [
                    interface_value_mapping[value]
                    for value in capability.thinking_effort.values
                ]
                duplicate_mapped_values = {
                    value for value in mapped_values if mapped_values.count(value) > 1
                }
                if duplicate_mapped_values:
                    raise ValueError(
                        "interface thinking_effort values must map to distinct interface values"
                    )
        agent_ids = [account.agent_id for account in self.built_in_account_capabilities]
        duplicate_agent_ids = sorted(
            {agent_id for agent_id in agent_ids if agent_ids.count(agent_id) > 1}
        )
        if duplicate_agent_ids:
            raise ValueError(f"duplicate built-in account agent_id values: {', '.join(duplicate_agent_ids)}")
        known_model_ids = set(ids)
        unknown_model_ids = sorted(
            {
                model_id
                for account in self.built_in_account_capabilities
                for model_id in account.model_ids
                if model_id not in known_model_ids
            }
        )
        if unknown_model_ids:
            raise ValueError(
                "built-in account model_ids must reference declared models: "
                f"{', '.join(unknown_model_ids)}"
            )
        return self


def validate_model_capability_catalog(payload: object) -> ModelCapabilityCatalog:
    return ModelCapabilityCatalog.model_validate(payload)
