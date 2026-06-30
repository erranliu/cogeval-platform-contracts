from jsonschema import Draft202012Validator

from cogeval_platform_contracts.model_capabilities.resources import (
    load_fixture,
    load_schema,
)


def test_model_capability_v2_json_schema_is_valid() -> None:
    Draft202012Validator.check_schema(load_schema("model_capability_catalog.v2"))


def test_model_capability_v2_fixture_validates_against_json_schema() -> None:
    schema = load_schema("model_capability_catalog.v2")
    validator = Draft202012Validator(schema)

    validator.validate(load_fixture("minimal.v2"))


def test_model_capability_v2_json_schema_rejects_builtin_binding_mismatch() -> None:
    schema = load_schema("model_capability_catalog.v2")
    validator = Draft202012Validator(schema)
    payload = load_fixture("minimal.v2")
    payload["built_in_account_capabilities"][0]["provider_interface"] = "openai_compatible_chat"

    errors = list(validator.iter_errors(payload))

    assert errors
