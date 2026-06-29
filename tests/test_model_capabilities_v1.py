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
        "models": [
            {
                "model_id": "gpt-5.5",
                "display_name": "GPT-5.5",
                "thinking_effort": {
                    "values": ["default", "low", "medium", "high"],
                    "default": "default",
                    "model_value_labels": {"high": "High reasoning"},
                },
            }
        ],
    }


def test_validates_provider_free_model_capability_catalog() -> None:
    catalog = validate_model_capability_catalog(_payload())

    assert catalog.schema == MODEL_CAPABILITY_CATALOG_SCHEMA
    assert catalog.models[0].model_id == "gpt-5.5"


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
