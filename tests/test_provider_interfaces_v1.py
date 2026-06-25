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
    ProviderInterfaceCatalogError,
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


def _canonical_catalog_payload() -> dict[str, object]:
    return {
        "schema": PROVIDER_INTERFACE_CATALOG_SCHEMA,
        "updated_at": "2026-06-24T00:00:00Z",
        "providers": [
            {
                "provider_id": "deepseek",
                "display_name": "DeepSeek",
                "status": "supported",
                "default_base_url": "https://api.deepseek.com",
                "default_env_key": "DEEPSEEK_API_KEY",
                "model_provider": "deepseek",
                "supported_interfaces": [
                    {"interface": "openai_compatible_chat"}
                ],
                "models": [
                    {
                        "model_option_id": "deepseek_chat",
                        "display_name": "DeepSeek Chat",
                        "model_name": "deepseek-chat",
                    }
                ],
            }
        ],
    }


def test_canonical_schema_is_accepted() -> None:
    catalog = validate_provider_interface_catalog(_canonical_catalog_payload())

    provider = catalog.providers[0]
    assert catalog.schema == PROVIDER_INTERFACE_CATALOG_SCHEMA
    assert provider.default_env_key == "DEEPSEEK_API_KEY"
    assert provider.model_provider == "deepseek"
    assert provider.supported_interfaces[0].interface == "openai_compatible_chat"
    assert not hasattr(provider.models[0], "supported_interfaces")


@pytest.mark.parametrize("field_name", ["default_env_key", "model_provider"])
def test_provider_interface_rows_cannot_override_provider_level_fields(field_name: str) -> None:
    payload = _canonical_catalog_payload()
    provider = payload["providers"][0]
    assert isinstance(provider, dict)
    supported_interfaces = provider["supported_interfaces"]
    assert isinstance(supported_interfaces, list)
    interface = supported_interfaces[0]
    assert isinstance(interface, dict)
    interface[field_name] = provider[field_name]

    with pytest.raises(ValidationError) as exc:
        ProviderInterfaceCatalog.model_validate(payload)

    assert ("providers", 0, "supported_interfaces", 0, field_name) in {
        error["loc"] for error in exc.value.errors()
    }


def test_wire_api_is_not_configurable_on_provider_interfaces() -> None:
    payload = _canonical_catalog_payload()
    provider = payload["providers"][0]
    assert isinstance(provider, dict)
    supported_interfaces = provider["supported_interfaces"]
    assert isinstance(supported_interfaces, list)
    interface = supported_interfaces[0]
    assert isinstance(interface, dict)
    interface["wire_api"] = "openai_chat_completions"

    with pytest.raises(ValidationError) as exc:
        ProviderInterfaceCatalog.model_validate(payload)

    assert ("providers", 0, "supported_interfaces", 0, "wire_api") in {
        error["loc"] for error in exc.value.errors()
    }


@pytest.mark.parametrize(
    ("legacy_provider_field", "legacy_interface_field"),
    [
        ("supported_adapters", "interface"),
        ("supported_interfaces", "adapter"),
    ],
)
def test_legacy_field_aliases_are_rejected(
    legacy_provider_field: str,
    legacy_interface_field: str,
) -> None:
    payload = _canonical_catalog_payload()
    provider = payload["providers"][0]
    assert isinstance(provider, dict)
    provider[legacy_provider_field] = provider.pop("supported_interfaces")
    supported_interfaces = provider[legacy_provider_field]
    assert isinstance(supported_interfaces, list)
    interface = supported_interfaces[0]
    assert isinstance(interface, dict)
    interface[legacy_interface_field] = interface.pop("interface")

    with pytest.raises(ValidationError):
        ProviderInterfaceCatalog.model_validate(payload)


@pytest.mark.parametrize(
    "legacy_interface_id",
    [
        "codex_model_provider",
        "anthropic_gateway",
        "qwen_code_api_key",
        "litellm_openai_compatible",
    ],
)
def test_legacy_provider_interface_ids_are_rejected_in_provider_interfaces(legacy_interface_id: str) -> None:
    payload = _canonical_catalog_payload()
    provider = payload["providers"][0]
    assert isinstance(provider, dict)
    supported_interfaces = provider["supported_interfaces"]
    assert isinstance(supported_interfaces, list)
    interface = supported_interfaces[0]
    assert isinstance(interface, dict)
    interface["interface"] = legacy_interface_id

    with pytest.raises(ValidationError, match="unknown provider interface"):
        ProviderInterfaceCatalog.model_validate(payload)


def test_model_supported_interfaces_field_is_rejected() -> None:
    payload = _canonical_catalog_payload()
    provider = payload["providers"][0]
    assert isinstance(provider, dict)
    models = provider["models"]
    assert isinstance(models, list)
    model = models[0]
    assert isinstance(model, dict)
    model["supported_interfaces"] = ["openai_compatible_chat"]

    with pytest.raises(ValidationError):
        ProviderInterfaceCatalog.model_validate(payload)


def test_legacy_field_aliases_are_rejected_by_validate_provider_interface_catalog() -> None:
    payload = _canonical_catalog_payload()
    provider = payload["providers"][0]
    assert isinstance(provider, dict)
    provider["supported_adapters"] = provider.pop("supported_interfaces")

    with pytest.raises(ProviderInterfaceCatalogError) as exc:
        validate_provider_interface_catalog(payload)

    assert exc.value.code == "catalog_invalid_payload"


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


def test_schema_version_field_name_is_rejected_for_canonical_catalog() -> None:
    with pytest.raises(ValidationError) as exc:
        ProviderInterfaceCatalog.model_validate(
            {
                "schema_version": PROVIDER_INTERFACE_CATALOG_SCHEMA,
                "updated_at": "2026-06-24T00:00:00Z",
                "providers": [],
            }
        )

    error_locations = {error["loc"] for error in exc.value.errors()}
    assert ("schema",) in error_locations
    assert ("schema_version",) in error_locations


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


def test_unknown_interface_fails_after_canonicalization() -> None:
    with pytest.raises(ValidationError, match="unknown provider interface"):
        ApiKeyProvider.model_validate(
            {
                "provider_id": "custom",
                "display_name": "Custom",
                "status": "supported",
                "default_base_url": "https://example.invalid",
                "default_env_key": "CUSTOM_API_KEY",
                "supported_interfaces": [
                    {"interface": "not_a_real_interface"}
                ],
                "models": [
                    {
                        "model_option_id": "model",
                        "display_name": "Model",
                        "model_name": "model",
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
                        "default_env_key": "DEEPSEEK_API_KEY",
                        "supported_interfaces": [
                            {"interface": "openai_compatible_chat"}
                        ],
                    },
                    {
                        "provider_id": "deepseek",
                        "display_name": "DeepSeek Copy",
                        "status": "deprecated",
                        "default_base_url": "https://api.deepseek.com",
                        "default_env_key": "DEEPSEEK_API_KEY",
                        "supported_interfaces": [
                            {"interface": "openai_compatible_chat"}
                        ],
                    },
                ],
            }
        )
