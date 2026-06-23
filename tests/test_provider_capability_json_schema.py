from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.provider_capabilities.resources import (
    load_fixture,
    load_schema,
    list_fixtures,
)


def test_provider_capability_json_schema_is_valid() -> None:
    Draft202012Validator.check_schema(load_schema("provider_capability_catalog.v1"))


def test_provider_capability_fixtures_validate_against_json_schema() -> None:
    schema = load_schema("provider_capability_catalog.v1")
    validator = Draft202012Validator(schema)

    for fixture_name in list_fixtures():
        validator.validate(load_fixture(fixture_name))

