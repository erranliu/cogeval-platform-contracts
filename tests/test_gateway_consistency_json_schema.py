from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.gateway_consistency import list_fixtures, load_fixture, load_schema


def test_gateway_consistency_json_schemas_are_valid() -> None:
    for schema_name in ("gateway_consistency_baseline.v1", "gateway_consistency_task_pack.v1"):
        Draft202012Validator.check_schema(load_schema(schema_name))


def test_gateway_consistency_fixtures_validate_against_json_schema() -> None:
    mapping = {
        "baseline_reference.v1": "gateway_consistency_baseline.v1",
        "task_pack.v1": "gateway_consistency_task_pack.v1",
    }

    assert set(mapping).issubset(set(list_fixtures()))
    for fixture_name, schema_name in mapping.items():
        Draft202012Validator(load_schema(schema_name)).validate(load_fixture(fixture_name))
