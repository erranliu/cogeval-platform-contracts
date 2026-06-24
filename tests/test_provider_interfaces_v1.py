from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.provider_interfaces.v1 import (
    PROVIDER_INTERFACE_CATALOG_SCHEMA,
    WORKBENCH_PROVIDER_CATALOG_SCHEMA,
    ApiKeyProvider,
    ProviderInterfaceCatalog,
    canonical_provider_interface_id,
    is_valid_provider_interface,
    provider_interface_ids_equal,
    validate_provider_interface_catalog,
)


FIXTURE_ROOT = (
    Path(__file__).parents[1]
    / "src"
    / "cogeval_platform_contracts"
    / "provider_interfaces"
    / "fixtures"
)
SCHEMA_PATH = (
    Path(__file__).parents[1]
    / "src"
    / "cogeval_platform_contracts"
    / "provider_interfaces"
    / "schemas"
    / "provider_interface_catalog.v1.schema.json"
)


@pytest.mark.parametrize("path", sorted(FIXTURE_ROOT.glob("*.json")))
def test_provider_interface_fixtures_are_valid(path: Path) -> None:
    catalog = ProviderInterfaceCatalog.model_validate_json(path.read_text(encoding="utf-8"))
    assert catalog.schema == PROVIDER_INTERFACE_CATALOG_SCHEMA


def test_schema_file_matches_contract_version() -> None:
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert payload["properties"]["schema"]["const"] == PROVIDER_INTERFACE_CATALOG_SCHEMA


def test_canonical_schema_is_accepted_and_field_aliases_are_normalized() -> None:
    catalog = validate_provider_interface_catalog(
        {
            "schema": PROVIDER_INTERFACE_CATALOG_SCHEMA,
            "updated_at": "2026-06-24T00:00:00Z",
            "providers": [
                {
                    "provider_id": "deepseek",
                    "display_name": "DeepSeek",
                    "status": "supported",
                    "default_base_url": "https://api.deepseek.com",
                    "supported_adapters": [
                        {"adapter": "openai_compatible_chat", "default_env_key": "DEEPSEEK_API_KEY"}
                    ],
                    "models": [
                        {
                            "model_option_id": "deepseek_chat",
                            "display_name": "DeepSeek Chat",
                            "model_name": "deepseek-chat",
                            "supported_adapters": ["openai_compatible_chat"],
                        }
                    ],
                }
            ],
        }
    )

    provider = catalog.providers[0]
    assert catalog.schema == PROVIDER_INTERFACE_CATALOG_SCHEMA
    assert provider.supported_interfaces[0].interface == "openai_compatible_chat"
    assert provider.models[0].supported_interfaces == ["openai_compatible_chat"]


def test_legacy_workbench_schema_is_rejected_for_canonical_catalog() -> None:
    with pytest.raises(ValidationError) as exc:
        ProviderInterfaceCatalog.model_validate(
            {
                "schema": WORKBENCH_PROVIDER_CATALOG_SCHEMA,
                "updated_at": "2026-06-24T00:00:00Z",
                "providers": [],
            }
        )

    schema_errors = [error for error in exc.value.errors() if error["loc"] == ("schema",)]
    assert schema_errors
    assert schema_errors[0]["type"] == "literal_error"


def test_missing_schema_is_rejected_for_canonical_catalog() -> None:
    with pytest.raises(ValidationError) as exc:
        ProviderInterfaceCatalog.model_validate(
            {
                "updated_at": "2026-06-24T00:00:00Z",
                "providers": [],
            }
        )

    schema_errors = [error for error in exc.value.errors() if error["loc"] == ("schema",)]
    assert schema_errors


def test_alias_helpers_canonicalize_legacy_interface_ids() -> None:
    assert canonical_provider_interface_id("codex_model_provider") == "openai_responses"
    assert canonical_provider_interface_id("anthropic_gateway") == "anthropic_compatible_messages"
    assert provider_interface_ids_equal("anthropic_gateway", "anthropic_compatible_messages")


def test_litellm_openai_compatible_is_not_an_openai_chat_alias() -> None:
    assert canonical_provider_interface_id("litellm_openai_compatible") == "litellm_openai_compatible"
    assert not provider_interface_ids_equal("litellm_openai_compatible", "openai_compatible_chat")
    assert is_valid_provider_interface("litellm_openai_compatible") is False


def test_opencode_native_is_a_valid_provider_interface() -> None:
    assert canonical_provider_interface_id("opencode_native") == "opencode_native"
    assert is_valid_provider_interface("opencode_native") is True


def test_model_referencing_undeclared_interface_fails() -> None:
    with pytest.raises(ValidationError, match="undeclared provider interfaces"):
        ApiKeyProvider.model_validate(
            {
                "provider_id": "deepseek",
                "display_name": "DeepSeek",
                "status": "supported",
                "default_base_url": "https://api.deepseek.com",
                "supported_interfaces": [
                    {"interface": "openai_compatible_chat", "default_env_key": "DEEPSEEK_API_KEY"}
                ],
                "models": [
                    {
                        "model_option_id": "claude",
                        "display_name": "Claude",
                        "model_name": "claude",
                        "supported_interfaces": ["anthropic_compatible_messages"],
                    }
                ],
            }
        )


def test_unknown_interface_fails_after_canonicalization() -> None:
    with pytest.raises(ValidationError, match="unknown provider interface"):
        ApiKeyProvider.model_validate(
            {
                "provider_id": "custom",
                "display_name": "Custom",
                "status": "supported",
                "default_base_url": "https://example.invalid",
                "supported_interfaces": [
                    {"interface": "not_a_real_interface", "default_env_key": "CUSTOM_API_KEY"}
                ],
                "models": [
                    {
                        "model_option_id": "model",
                        "display_name": "Model",
                        "model_name": "model",
                        "supported_interfaces": ["not_a_real_interface"],
                    }
                ],
            }
        )


def test_duplicate_providers_fail() -> None:
    with pytest.raises(ValidationError, match="duplicate provider_id"):
        ProviderInterfaceCatalog.model_validate(
            {
                "schema": PROVIDER_INTERFACE_CATALOG_SCHEMA,
                "updated_at": "2026-06-24T00:00:00Z",
                "providers": [
                    {
                        "provider_id": "deepseek",
                        "display_name": "DeepSeek",
                        "status": "deprecated",
                        "default_base_url": "https://api.deepseek.com",
                        "supported_interfaces": [
                            {"interface": "openai_compatible_chat", "default_env_key": "DEEPSEEK_API_KEY"}
                        ],
                    },
                    {
                        "provider_id": "deepseek",
                        "display_name": "DeepSeek Copy",
                        "status": "deprecated",
                        "default_base_url": "https://api.deepseek.com",
                        "supported_interfaces": [
                            {"interface": "openai_compatible_chat", "default_env_key": "DEEPSEEK_API_KEY"}
                        ],
                    },
                ],
            }
        )
