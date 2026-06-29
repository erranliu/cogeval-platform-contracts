"""Canonical model capability catalog contracts."""

from cogeval_platform_contracts.model_capabilities.resources import list_fixtures, load_fixture, load_schema
from cogeval_platform_contracts.model_capabilities.v1 import (
    BuiltInAccountCapability,
    BuiltInAccountAgentId,
    InterfaceThinkingEffortSurface,
    MODEL_CAPABILITY_CATALOG_SCHEMA,
    ModelCapability,
    ModelCapabilityCatalog,
    ModelInterfaceAdapterPolicy,
    ModelInterfaceCapability,
    ModelInterfaceThinkingEffortCapability,
    ModelThinkingEffortCapability,
    ProviderInterfaceCapabilityContract,
    ProviderInterfaceId,
    ThinkingEffortPlatformValue,
    validate_model_capability_catalog,
)
from cogeval_platform_contracts.model_capabilities.v2 import (
    MODEL_CAPABILITY_CATALOG_SCHEMA_V2,
    InterfaceThinkingEffortVocabularyItem,
    ModelCapabilityCatalogV2,
    ModelCapabilityV2,
    ModelThinkingEffortValue,
    validate_model_capability_catalog_v2,
)

__all__ = [
    "BuiltInAccountCapability",
    "BuiltInAccountAgentId",
    "InterfaceThinkingEffortSurface",
    "MODEL_CAPABILITY_CATALOG_SCHEMA",
    "MODEL_CAPABILITY_CATALOG_SCHEMA_V2",
    "InterfaceThinkingEffortVocabularyItem",
    "ModelCapability",
    "ModelCapabilityCatalogV2",
    "ModelCapabilityV2",
    "ModelCapabilityCatalog",
    "ModelInterfaceAdapterPolicy",
    "ModelInterfaceCapability",
    "ModelInterfaceThinkingEffortCapability",
    "ModelThinkingEffortCapability",
    "ModelThinkingEffortValue",
    "ProviderInterfaceCapabilityContract",
    "ProviderInterfaceId",
    "ThinkingEffortPlatformValue",
    "list_fixtures",
    "load_fixture",
    "load_schema",
    "validate_model_capability_catalog",
    "validate_model_capability_catalog_v2",
]
