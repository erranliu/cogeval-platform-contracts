from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MODEL_CAPABILITY_CATALOG_SCHEMA_V2 = "cogeval.model_capability_catalog.v2"
ProviderInterfaceId = Literal[
    "openai_responses",
    "openai_compatible_chat",
    "anthropic_compatible_messages",
]
BuiltInAccountAgentId = Literal["codex_cli", "claude_code_cli"]
BuiltInAccountNativeInterfaceId = Literal["codex_native", "claude_code_native"]
BuiltInAccountBindingPolicy = Literal["builtin_account_native", "reuse_provider_interface"]
ModelInterfaceAdapterPolicy = Literal["map_values"]


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


def _reject_blank_display_name(value: str | None, field_name: str) -> str | None:
    if value is not None and not value.strip():
        raise ValueError(f"{field_name} must not be blank")
    return value


class InterfaceThinkingEffortVocabularyItem(StrictContractModel):
    id: str = Field(min_length=1)
    wire_value: str | None = None
    display_name: str | None = None

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, display_name: str | None) -> str | None:
        return _reject_blank_display_name(display_name, "interface thinking_effort display_name")


class InterfaceThinkingEffortSurface(StrictContractModel):
    surface: Literal["thinking_effort"] = "thinking_effort"
    path: str = Field(min_length=1)
    vocabulary: list[InterfaceThinkingEffortVocabularyItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_shape(self) -> "InterfaceThinkingEffortSurface":
        ids = [item.id for item in self.vocabulary]
        duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        if duplicates:
            raise ValueError("interface thinking_effort vocabulary ids must be unique")
        omit_items = [item.id for item in self.vocabulary if item.wire_value is None]
        if len(omit_items) > 1:
            raise ValueError("interface thinking_effort may declare at most one omitted parameter value")
        return self


class ProviderInterfaceCapabilityContract(StrictContractModel):
    thinking_effort: InterfaceThinkingEffortSurface | None = None


class ModelThinkingEffortValue(StrictContractModel):
    id: str = Field(min_length=1)


class ModelThinkingEffortCapability(StrictContractModel):
    values: list[ModelThinkingEffortValue] = Field(min_length=1)
    default: str | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> "ModelThinkingEffortCapability":
        ids = [value.id for value in self.values]
        duplicates = sorted({value_id for value_id in ids if ids.count(value_id) > 1})
        if duplicates:
            raise ValueError("thinking_effort value ids must be unique")
        if self.default is not None and self.default not in ids:
            raise ValueError("thinking_effort default must be one of values")
        return self


class ModelInterfaceThinkingEffortCapability(StrictContractModel):
    mapping: dict[str, str] = Field(default_factory=dict)
    parameter_surface: Literal["thinking_effort"]
    adapter_policy: ModelInterfaceAdapterPolicy = "map_values"


class ModelInterfaceCapability(StrictContractModel):
    thinking_effort: ModelInterfaceThinkingEffortCapability | None = None


class ModelCapabilityV2(StrictContractModel):
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
    native_interface: BuiltInAccountNativeInterfaceId | None = None
    provider_interface: ProviderInterfaceId | None = None
    binding_policy: BuiltInAccountBindingPolicy = "builtin_account_native"

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

    @model_validator(mode="after")
    def validate_binding_metadata(self) -> "BuiltInAccountCapability":
        expected_native_interface: dict[BuiltInAccountAgentId, BuiltInAccountNativeInterfaceId] = {
            "codex_cli": "codex_native",
            "claude_code_cli": "claude_code_native",
        }
        expected_provider_interface: dict[BuiltInAccountAgentId, ProviderInterfaceId] = {
            "codex_cli": "openai_responses",
            "claude_code_cli": "anthropic_compatible_messages",
        }

        native_interface = self.native_interface or expected_native_interface[self.agent_id]
        provider_interface = self.provider_interface or expected_provider_interface[self.agent_id]
        if native_interface != expected_native_interface[self.agent_id]:
            raise ValueError(
                f"{self.agent_id} native_interface must be {expected_native_interface[self.agent_id]}"
            )
        if provider_interface != expected_provider_interface[self.agent_id]:
            raise ValueError(
                f"{self.agent_id} provider_interface must be {expected_provider_interface[self.agent_id]}"
            )
        self.native_interface = native_interface
        self.provider_interface = provider_interface
        return self


class ModelCapabilityCatalogV2(StrictContractModel):
    schema_version: Literal["cogeval.model_capability_catalog.v2"] = Field(
        default=MODEL_CAPABILITY_CATALOG_SCHEMA_V2,
        alias="schema",
    )
    updated_at: str = Field(min_length=1)
    interfaces: dict[ProviderInterfaceId, ProviderInterfaceCapabilityContract]
    models: list[ModelCapabilityV2] = Field(min_length=1)
    built_in_account_capabilities: list[BuiltInAccountCapability] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    @property
    def schema(self) -> str:
        return self.schema_version

    @model_validator(mode="after")
    def validate_catalog_references(self) -> "ModelCapabilityCatalogV2":
        model_ids = [model.model_id for model in self.models]
        duplicate_model_ids = sorted(
            {model_id for model_id in model_ids if model_ids.count(model_id) > 1}
        )
        if duplicate_model_ids:
            raise ValueError(f"duplicate model_id values: {', '.join(duplicate_model_ids)}")

        for model in self.models:
            model_effort_ids = (
                {item.id for item in model.thinking_effort.values}
                if model.thinking_effort
                else set()
            )
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
                mapping = capability.thinking_effort.mapping
                unsupported_by_model = sorted(set(mapping) - model_effort_ids)
                if unsupported_by_model:
                    raise ValueError(
                        "interface thinking_effort mapping keys must be declared by model: "
                        f"{', '.join(unsupported_by_model)}"
                    )
                vocabulary_ids = {
                    item.id for item in interface_contract.thinking_effort.vocabulary
                }
                unsupported_by_interface = sorted(set(mapping.values()) - vocabulary_ids)
                if unsupported_by_interface:
                    raise ValueError(
                        "interface thinking_effort mapping targets must be declared by interface vocabulary: "
                        f"{', '.join(unsupported_by_interface)}"
                    )
                duplicate_targets = sorted(
                    {target for target in mapping.values() if list(mapping.values()).count(target) > 1}
                )
                if duplicate_targets:
                    raise ValueError(
                        "interface thinking_effort mapping targets must be unique"
                    )

        agent_ids = [account.agent_id for account in self.built_in_account_capabilities]
        duplicate_agent_ids = sorted(
            {agent_id for agent_id in agent_ids if agent_ids.count(agent_id) > 1}
        )
        if duplicate_agent_ids:
            raise ValueError(f"duplicate built-in account agent_id values: {', '.join(duplicate_agent_ids)}")
        known_model_ids = set(model_ids)
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


def validate_model_capability_catalog_v2(payload: object) -> ModelCapabilityCatalogV2:
    return ModelCapabilityCatalogV2.model_validate(payload)
