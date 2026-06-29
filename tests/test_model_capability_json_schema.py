from jsonschema import Draft202012Validator

from cogeval_platform_contracts.model_capabilities.resources import list_fixtures, load_fixture, load_schema


def test_model_capability_json_schema_is_valid() -> None:
    Draft202012Validator.check_schema(load_schema("model_capability_catalog.v1"))


def test_model_capability_fixtures_validate_against_json_schema() -> None:
    schema = load_schema("model_capability_catalog.v1")
    validator = Draft202012Validator(schema)

    for fixture_name in (name for name in list_fixtures() if name.endswith(".v1")):
        validator.validate(load_fixture(fixture_name))
