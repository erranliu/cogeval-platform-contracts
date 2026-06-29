import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.model_capabilities.v1 import (
    MODEL_CAPABILITY_CATALOG_SCHEMA,
    ModelCapabilityCatalog,
    validate_model_capability_catalog,
)


def _payload() -> dict:
    return {
        "schema": MODEL_CAPABILITY_CATALOG_SCHEMA,
        "updated_at": "2026-06-27T00:00:00Z",
        "interfaces": {
            "openai_responses": {
                "thinking_effort": {
                    "surface": "thinking_effort",
                    "path": "reasoning.effort",
                    "platform_values": ["default", "minimal", "low", "medium", "high"],
                    "value_mapping": {
                        "default": None,
                        "minimal": "minimal",
                        "low": "low",
                        "medium": "medium",
                        "high": "high",
                    },
                }
            }
        },
        "models": [
            {
                "model_id": "gpt-5.5",
                "display_name": "GPT-5.5",
                "thinking_effort": {
                    "values": ["default", "low", "medium", "high"],
                    "default": "default",
                    "model_value_labels": {"high": "High reasoning"},
                },
                "interface_capabilities": {
                    "openai_responses": {
                        "thinking_effort": {
                            "values": ["default", "low", "medium", "high"],
                            "parameter_surface": "thinking_effort",
                            "adapter_policy": "map_values",
                        }
                    }
                },
            }
        ],
        "built_in_account_capabilities": [
            {
                "agent_id": "codex_cli",
                "display_name": "Codex CLI",
                "model_ids": ["gpt-5.5"],
            },
            {
                "agent_id": "claude_code_cli",
                "display_name": "Claude Code CLI",
                "model_ids": [],
            },
        ],
    }


def test_validates_provider_free_model_capability_catalog() -> None:
    catalog = validate_model_capability_catalog(_payload())

    assert catalog.schema == MODEL_CAPABILITY_CATALOG_SCHEMA
    assert catalog.interfaces["openai_responses"].thinking_effort is not None
    assert catalog.models[0].model_id == "gpt-5.5"
    assert catalog.built_in_account_capabilities[0].agent_id == "codex_cli"


def test_rejects_provider_id_on_model_capability() -> None:
    payload = _payload()
    payload["models"][0]["provider_id"] = "openai"

    with pytest.raises(ValidationError):
        ModelCapabilityCatalog.model_validate(payload)


def test_rejects_unknown_thinking_effort_value() -> None:
    payload = _payload()
    payload["models"][0]["thinking_effort"]["values"].append("adaptive")

    with pytest.raises(ValidationError):
        ModelCapabilityCatalog.model_validate(payload)


def test_rejects_duplicate_model_id() -> None:
    payload = _payload()
    payload["models"].append(dict(payload["models"][0]))

    with pytest.raises(ValidationError):
        ModelCapabilityCatalog.model_validate(payload)


def test_rejects_interface_capability_value_not_declared_by_model() -> None:
    payload = _payload()
    payload["models"][0]["interface_capabilities"]["openai_responses"]["thinking_effort"][
        "values"
    ].append("minimal")

    with pytest.raises(ValidationError, match="interface thinking_effort values must be declared by model"):
        ModelCapabilityCatalog.model_validate(payload)


def test_rejects_builtin_account_unknown_model_id() -> None:
    payload = _payload()
    payload["built_in_account_capabilities"][0]["model_ids"].append("missing-model")

    with pytest.raises(ValidationError, match="built-in account model_ids must reference declared models"):
        ModelCapabilityCatalog.model_validate(payload)


def test_rejects_duplicate_builtin_account_agent_id() -> None:
    payload = _payload()
    payload["built_in_account_capabilities"][1]["agent_id"] = "codex_cli"

    with pytest.raises(ValidationError, match="duplicate built-in account agent_id values"):
        ModelCapabilityCatalog.model_validate(payload)
