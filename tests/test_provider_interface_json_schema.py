from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.provider_interfaces.resources import (
    list_fixtures,
    load_fixture,
    load_schema,
)


def test_provider_interface_json_schema_is_valid() -> None:
    Draft202012Validator.check_schema(load_schema("provider_interface_catalog.v1"))


def test_provider_interface_json_schema_includes_opencode_native() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    assert "opencode_native" in schema["$defs"]["interface_id"]["enum"]


def test_provider_interface_json_schema_does_not_expose_wire_api() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    assert "wire_api" not in schema["$defs"]["interface"]["properties"]


def test_provider_level_auth_and_routing_fields_are_not_interface_overrides() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    provider_properties = schema["$defs"]["provider"]["properties"]
    interface_properties = schema["$defs"]["interface"]["properties"]
    assert provider_properties["default_env_key"] == {"type": "string", "minLength": 1}
    assert provider_properties["model_provider"] == {"type": ["string", "null"]}
    assert "default_env_key" in schema["$defs"]["provider"]["required"]
    assert "default_env_key" not in interface_properties
    assert "model_provider" not in interface_properties


def test_provider_interface_fixtures_validate_against_json_schema() -> None:
    schema = load_schema("provider_interface_catalog.v1")
    validator = Draft202012Validator(schema)

    for fixture_name in list_fixtures():
        validator.validate(load_fixture(fixture_name))

