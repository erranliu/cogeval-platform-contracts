from __future__ import annotations

import pytest
from jsonschema import Draft202012Validator, ValidationError as JsonSchemaValidationError

from cogeval_platform_contracts.cog_cases import list_fixtures, load_fixture, load_schema
from cogeval_platform_contracts.cog_cases.current import validate_current_cog_case_group


def test_cog_case_json_schemas_are_valid() -> None:
    for schema_name in ("cog_case.v1", "cog_case.v2", "cog_case.v3", "cog_case_group.v1"):
        Draft202012Validator.check_schema(load_schema(schema_name))


def test_cog_case_fixtures_validate_against_json_schema() -> None:
    mapping = {
        "case_public.v1": "cog_case.v1",
        "case_public.v2": "cog_case.v2",
        "case_public.v3": "cog_case.v3",
        "group_public.v1": "cog_case_group.v1",
    }

    assert set(mapping).issubset(set(list_fixtures()))
    for fixture_name, schema_name in mapping.items():
        Draft202012Validator(load_schema(schema_name)).validate(load_fixture(fixture_name))


def test_current_group_json_schema_and_pydantic_have_the_same_required_shape() -> None:
    payload = load_fixture("group_public.v1")
    Draft202012Validator(load_schema("cog_case_group.v1")).validate(payload)
    group = validate_current_cog_case_group(payload)
    assert group.member_count == len(group.members)

    missing_members = dict(payload)
    missing_members.pop("members")
    with pytest.raises(JsonSchemaValidationError):
        Draft202012Validator(load_schema("cog_case_group.v1")).validate(missing_members)
