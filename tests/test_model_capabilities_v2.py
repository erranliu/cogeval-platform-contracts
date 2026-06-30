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
                        {"id": "default"},
                        {"id": "low"},
                        {"id": "high"},
                        {"id": "max"},
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


def test_defaults_builtin_account_binding_metadata() -> None:
    catalog = validate_model_capability_catalog_v2(_payload())

    codex_account = catalog.built_in_account_capabilities[0]
    claude_account = catalog.built_in_account_capabilities[1]
    assert codex_account.native_interface == "codex_native"
    assert codex_account.provider_interface == "openai_responses"
    assert codex_account.binding_policy == "builtin_account_native"
    assert claude_account.native_interface == "claude_code_native"
    assert claude_account.provider_interface == "anthropic_compatible_messages"
    assert claude_account.binding_policy == "builtin_account_native"


@pytest.mark.parametrize(
    ("agent_index", "field_name", "invalid_value", "expected_message"),
    [
        (
            0,
            "provider_interface",
            "openai_compatible_chat",
            "codex_cli provider_interface must be openai_responses",
        ),
        (
            1,
            "provider_interface",
            "openai_responses",
            "claude_code_cli provider_interface must be anthropic_compatible_messages",
        ),
        (
            0,
            "native_interface",
            "claude_code_native",
            "codex_cli native_interface must be codex_native",
        ),
        (
            1,
            "native_interface",
            "codex_native",
            "claude_code_cli native_interface must be claude_code_native",
        ),
    ],
)
def test_rejects_builtin_account_binding_mismatches(
    agent_index: int,
    field_name: str,
    invalid_value: str,
    expected_message: str,
) -> None:
    payload = _payload()
    payload["built_in_account_capabilities"][agent_index][field_name] = invalid_value

    with pytest.raises(ValidationError, match=expected_message):
        ModelCapabilityCatalogV2.model_validate(payload)


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


def test_rejects_model_thinking_effort_display_name_field() -> None:
    payload = _payload()
    payload["models"][0]["thinking_effort"]["values"][1]["display_name"] = "Low reasoning"

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
        {"id": "high"}
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
