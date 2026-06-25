from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.provider_interfaces.resources import (
    list_fixtures,
    load_fixture,
    load_schema,
)


def test_provider_interface_json_schema_is_valid() -> None:
    Draft202012Validator.check_schema(load_schema("provider_interface_catalog.v1"))


def test_provider_interface_json_schema_excludes_native_interfaces() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    assert not {
        "qwen_code_native",
        "kimi_code_native",
        "gemini_cli_native",
        "trae_agent_native",
        "opencode_native",
    } & set(schema["$defs"]["interface_id"]["enum"])


def test_provider_interface_json_schema_does_not_expose_wire_api() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    assert "wire_api" not in schema["$defs"]["interface"]["properties"]


def test_provider_catalog_schema_omits_auth_routing_and_model_option_fields() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    provider_properties = schema["$defs"]["provider"]["properties"]
    interface_properties = schema["$defs"]["interface"]["properties"]
    model_properties = schema["$defs"]["model"]["properties"]
    assert "default_env_key" not in provider_properties
    assert "model_provider" not in provider_properties
    assert "default_env_key" not in schema["$defs"]["provider"]["required"]
    assert "default_env_key" not in interface_properties
    assert "model_provider" not in interface_properties
    assert "model_option_id" not in model_properties
    assert "model_option_id" not in schema["$defs"]["model"]["required"]


def test_provider_interface_fixtures_validate_against_json_schema() -> None:
    schema = load_schema("provider_interface_catalog.v1")
    validator = Draft202012Validator(schema)

    for fixture_name in list_fixtures():
        validator.validate(load_fixture(fixture_name))

