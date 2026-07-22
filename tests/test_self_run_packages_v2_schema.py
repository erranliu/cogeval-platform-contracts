from jsonschema import Draft202012Validator

from cogeval_platform_contracts.self_run_packages import load_fixture, load_schema


def test_v2_fixture_validates_against_schema() -> None:
    schema = load_schema("package_import_result.v2")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(load_fixture("import_result_mixed.v2"))
