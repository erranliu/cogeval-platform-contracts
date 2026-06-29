import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.model_capabilities.v2 import (
    MODEL_CAPABILITY_CATALOG_SCHEMA_V2,
    ModelCapabilityCatalogV2,
    validate_model_capability_catalog_v2,
)


def _payload() -> dict:
    return {
        "schema": MODEL_CAPABILITY_CATALOG_SCHEMA_V2,
        "updated_at": "2026-06-29T00:00:00Z",
        "interfaces": {
            "openai_responses": {
                "thinking_effort": {
                    "surface": "thinking_effort",
                    "path": "reasoning.effort",
                    "vocabulary": [
                        {
                            "id": "default",
                            "wire_value": None,
                            "display_name": "Model default",
                        },
                        {"id": "low", "wire_value": "low"},
                        {"id": "medium", "wire_value": "medium"},
                        {"id": "high", "wire_value": "high"},
                        {"id": "xhigh", "wire_value": "xhigh"},
                    ],
                }
            }
        },
        "models": [
            {
                "model_id": "gpt-5.5",
                "display_name": "GPT-5.5",
                "thinking_effort": {
                    "values": [
                        {"id": "default", "display_name": "Model default"},
                        {"id": "low", "display_name": "Low reasoning"},
                        {"id": "high", "display_name": "High reasoning"},
                        {"id": "max", "display_name": "Max reasoning"},
                    ],
                    "default": "default",
                },
                "interface_capabilities": {
                    "openai_responses": {
                        "thinking_effort": {
                            "parameter_surface": "thinking_effort",
                            "mapping": {
                                "default": "default",
                                "low": "low",
                                "high": "high",
                                "max": "xhigh",
                            },
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


def test_validates_v2_model_capability_catalog() -> None:
    catalog = validate_model_capability_catalog_v2(_payload())

    assert catalog.schema == MODEL_CAPABILITY_CATALOG_SCHEMA_V2
    surface = catalog.interfaces["openai_responses"].thinking_effort
    assert surface is not None
    assert [item.id for item in surface.vocabulary] == [
        "default",
        "low",
        "medium",
        "high",
        "xhigh",
    ]
    assert catalog.models[0].thinking_effort is not None
    assert catalog.models[0].thinking_effort.values[-1].id == "max"


def test_rejects_legacy_platform_values_field() -> None:
    payload = _payload()
    payload["interfaces"]["openai_responses"]["thinking_effort"]["platform_values"] = [
        "default",
        "low",
    ]

    with pytest.raises(ValidationError):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_legacy_value_mapping_field() -> None:
    payload = _payload()
    payload["interfaces"]["openai_responses"]["thinking_effort"]["value_mapping"] = {
        "default": None,
        "low": "low",
    }

    with pytest.raises(ValidationError):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_legacy_model_value_labels_field() -> None:
    payload = _payload()
    payload["models"][0]["thinking_effort"]["model_value_labels"] = {
        "high": "High reasoning",
    }

    with pytest.raises(ValidationError):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_mapping_key_not_declared_by_model() -> None:
    payload = _payload()
    payload["models"][0]["interface_capabilities"]["openai_responses"][
        "thinking_effort"
    ]["mapping"]["minimal"] = "low"

    with pytest.raises(
        ValidationError,
        match="interface thinking_effort mapping keys must be declared by model",
    ):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_mapping_target_not_declared_by_interface() -> None:
    payload = _payload()
    payload["models"][0]["interface_capabilities"]["openai_responses"][
        "thinking_effort"
    ]["mapping"]["max"] = "max"

    with pytest.raises(
        ValidationError,
        match="interface thinking_effort mapping targets must be declared by interface vocabulary",
    ):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_duplicate_interface_vocabulary_id() -> None:
    payload = _payload()
    payload["interfaces"]["openai_responses"]["thinking_effort"][
        "vocabulary"
    ].append({"id": "high", "wire_value": "high"})

    with pytest.raises(
        ValidationError,
        match="interface thinking_effort vocabulary ids must be unique",
    ):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_duplicate_model_effort_id() -> None:
    payload = _payload()
    payload["models"][0]["thinking_effort"]["values"].append(
        {"id": "high", "display_name": "High duplicate"}
    )

    with pytest.raises(
        ValidationError,
        match="thinking_effort value ids must be unique",
    ):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_mapping_collisions() -> None:
    payload = _payload()
    payload["models"][0]["interface_capabilities"]["openai_responses"][
        "thinking_effort"
    ]["mapping"]["max"] = "high"

    with pytest.raises(
        ValidationError,
        match="interface thinking_effort mapping targets must be unique",
    ):
        ModelCapabilityCatalogV2.model_validate(payload)


def test_rejects_builtin_account_unknown_model_id() -> None:
    payload = _payload()
    payload["built_in_account_capabilities"][0]["model_ids"].append("missing-model")

    with pytest.raises(
        ValidationError,
        match="built-in account model_ids must reference declared models",
    ):
        ModelCapabilityCatalogV2.model_validate(payload)
