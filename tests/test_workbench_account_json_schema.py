from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.workbench_accounts import list_fixtures, load_fixture, load_schema


def test_workbench_account_json_schemas_are_valid() -> None:
    for schema_name in (
        "workbench_auth_github_request.v1",
        "workbench_auth_github_response.v1",
        "workbench_account_assets.v1",
        "workbench_coin_reservation.v1",
    ):
        Draft202012Validator.check_schema(load_schema(schema_name))


def test_workbench_account_fixtures_validate_against_json_schema() -> None:
    mapping = {
        "auth_github_request.v1": "workbench_auth_github_request.v1",
        "auth_github_response.v1": "workbench_auth_github_response.v1",
        "account_assets.v1": "workbench_account_assets.v1",
        "coin_reservation.v1": "workbench_coin_reservation.v1",
    }

    assert set(mapping).issubset(set(list_fixtures()))
    for fixture_name, schema_name in mapping.items():
        Draft202012Validator(load_schema(schema_name)).validate(load_fixture(fixture_name))
