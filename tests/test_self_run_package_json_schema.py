from __future__ import annotations

from jsonschema import Draft202012Validator

from cogeval_platform_contracts.self_run_packages import list_fixtures, load_fixture, load_schema


def test_self_run_package_json_schemas_are_valid() -> None:
    for schema_name in (
        "self_run_package_manifest.v1",
        "self_run_record.v1",
        "evidence_bundle.v1",
        "package_import_result.v1",
    ):
        Draft202012Validator.check_schema(load_schema(schema_name))


def test_self_run_package_fixtures_validate_against_json_schema() -> None:
    mapping = {
        "manifest_minimal.v1": "self_run_package_manifest.v1",
        "record_resolved.v1": "self_run_record.v1",
        "evidence_minimal.v1": "evidence_bundle.v1",
        "import_result_mixed.v1": "package_import_result.v1",
    }

    fixture_names = set(list_fixtures())
    for fixture_name, schema_name in mapping.items():
        assert fixture_name in fixture_names
        Draft202012Validator(load_schema(schema_name)).validate(load_fixture(fixture_name))
