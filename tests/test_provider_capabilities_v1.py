from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.provider_capabilities.v1 import (
    INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES,
    SCHEMA_VERSION,
    Capability,
    EffortValue,
    ProviderCapabilityCatalog,
)


FIXTURE_ROOT = (
    Path(__file__).parents[1]
    / "src"
    / "cogeval_platform_contracts"
    / "provider_capabilities"
    / "fixtures"
)
SCHEMA_PATH = (
    Path(__file__).parents[1]
    / "src"
    / "cogeval_platform_contracts"
    / "provider_capabilities"
    / "schemas"
    / "provider_capability_catalog.v1.schema.json"
)


@pytest.mark.parametrize("path", sorted(FIXTURE_ROOT.glob("*.json")))
def test_provider_capability_fixtures_are_valid(path: Path) -> None:
    catalog = ProviderCapabilityCatalog.model_validate_json(path.read_text(encoding="utf-8"))
    assert catalog.schema == SCHEMA_VERSION


def test_schema_file_matches_contract_version() -> None:
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert payload["properties"]["schema"]["const"] == SCHEMA_VERSION


def test_supported_capability_requires_values() -> None:
    with pytest.raises(ValidationError):
        Capability(supported=True)


def test_capability_default_must_be_declared_value() -> None:
    with pytest.raises(ValidationError):
        Capability(supported=True, values=["low"], default="high")


def test_value_mapping_must_reference_declared_values() -> None:
    with pytest.raises(ValidationError):
        Capability(
            supported=True,
            values=["low"],
            value_mapping={"high": "provider-high"},
        )


def test_model_value_labels_must_reference_declared_values() -> None:
    with pytest.raises(ValidationError):
        Capability(
            supported=True,
            values=["low"],
            model_value_labels={"high": "High reasoning"},
        )


def test_model_value_labels_must_not_be_blank() -> None:
    with pytest.raises(ValidationError):
        Capability(
            supported=True,
            values=["low"],
            model_value_labels={"low": "  "},
        )


def test_thinking_effort_platform_values_exclude_disable_controls() -> None:
    assert set(EffortValue.__args__) == {
        "default",
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
        "max",
    }
    assert "off" not in EffortValue.__args__
    assert "adaptive" not in EffortValue.__args__
    assert "none" not in EffortValue.__args__


def test_thinking_effort_rejects_non_platform_values() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_responses"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "none", "high"],
                                "default": "default",
                            }
                        },
                        "interface_capabilities": {
                            "openai_responses": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "none", "high"],
                                    "default": "default",
                                    "parameter_surface": "thinking_effort",
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_thinking_effort_rejects_non_platform_model_value_label_keys() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_responses"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "high", "turbo"],
                                "default": "default",
                                "model_value_labels": {
                                    "default": "Model default",
                                    "high": "High reasoning",
                                    "turbo": "Turbo reasoning",
                                },
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_capability_requires_model_level_capability() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_responses"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "interface_capabilities": {
                            "openai_responses": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "high"],
                                    "default": "default",
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_capability_values_must_be_model_level_values() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_responses"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "low"],
                                "default": "default",
                            }
                        },
                        "interface_capabilities": {
                            "openai_responses": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "high"],
                                    "default": "default",
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_capability_must_not_declare_model_value_labels() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_responses"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "high"],
                                "default": "default",
                                "model_value_labels": {"default": "Default", "high": "High reasoning"},
                            }
                        },
                        "interface_capabilities": {
                            "openai_responses": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "high"],
                                    "default": "default",
                                    "model_value_labels": {"high": "High reasoning"},
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_parameter_surfaces_are_builtin_contract_values() -> None:
    assert INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES["openai_responses"]["thinking_effort"].path == "reasoning.effort"
    assert INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES["openai_responses"]["thinking_effort"].values == (
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
    )
    assert INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES["openai_compatible_chat"]["thinking_effort"].path == "reasoning_effort"
    assert INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES["openai_compatible_chat"]["thinking_effort"].values == (
        "high",
        "max",
    )
    assert INTERFACE_THINKING_EFFORT_PARAMETER_SURFACES["anthropic_compatible_messages"]["thinking_effort"].values == (
        "low",
        "medium",
        "high",
        "xhigh",
        "max",
    )


def test_provider_interface_must_not_configure_parameter_surfaces() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [
                    {
                        "interface": "openai_responses",
                        "parameter_surfaces": {
                            "thinking_effort": {
                                "path": "reasoning.effort",
                                "values": ["high"],
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_capability_requires_builtin_parameter_surface() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_responses"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "high"],
                                "default": "default",
                            }
                        },
                        "interface_capabilities": {
                            "openai_responses": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "high"],
                                    "default": "default",
                                    "parameter_surface": "unknown_surface",
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_capability_value_mapping_targets_builtin_interface_vocabulary() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_compatible_chat"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "high"],
                                "default": "default",
                            }
                        },
                        "interface_capabilities": {
                            "openai_compatible_chat": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "high"],
                                    "default": "default",
                                    "parameter_surface": "thinking_effort",
                                    "adapter_policy": "map_values",
                                    "value_mapping": {"high": "extreme"},
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_pass_through_interface_values_must_exist_in_builtin_interface_vocabulary() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_compatible_chat"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "low"],
                                "default": "default",
                            }
                        },
                        "interface_capabilities": {
                            "openai_compatible_chat": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "low"],
                                    "default": "default",
                                    "parameter_surface": "thinking_effort",
                                    "adapter_policy": "pass_through",
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_interface_capability_must_not_map_default_value() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [{"interface": "openai_compatible_chat"}],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "capabilities": {
                            "thinking_effort": {
                                "supported": True,
                                "values": ["default", "high"],
                                "default": "default",
                            }
                        },
                        "interface_capabilities": {
                            "openai_compatible_chat": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "high"],
                                    "default": "default",
                                    "parameter_surface": "thinking_effort",
                                    "adapter_policy": "map_values",
                                    "value_mapping": {"default": "high", "high": "high"},
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_deepseek_thinking_effort_is_declared_per_interface() -> None:
    catalog = ProviderCapabilityCatalog.model_validate_json(
        (FIXTURE_ROOT / "deepseek_reasoning.v1.json").read_text(encoding="utf-8")
    )
    model = catalog.providers[0].models[0]

    model_capability = model.capabilities["thinking_effort"]
    capability = model.interface_capabilities["openai_compatible_chat"]["thinking_effort"]

    assert model_capability.values == ["default", "high", "max"]
    assert model_capability.model_value_labels == {
        "default": "Model default",
        "high": "Reasoning high",
        "max": "Reasoning max",
    }
    assert capability.values == ["default", "high", "max"]
    assert capability.default == "default"
    assert capability.value_mapping == {"high": "high", "max": "max"}
    assert capability.model_value_labels == {}
