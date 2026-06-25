from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.distribution_claims import list_fixtures, load_fixture, load_schema


def test_distribution_claim_json_schemas_are_valid() -> None:
    for schema_name in ("distribution_claim_request.v1", "distribution_claim.v1"):
        Draft202012Validator.check_schema(load_schema(schema_name))


def test_distribution_claim_fixtures_validate_against_json_schema() -> None:
    mapping = {
        "claim_request.v1": "distribution_claim_request.v1",
        "claim_assigned.v1": "distribution_claim.v1",
    }

    assert set(mapping).issubset(set(list_fixtures()))
    for fixture_name, schema_name in mapping.items():
        Draft202012Validator(load_schema(schema_name)).validate(load_fixture(fixture_name))
