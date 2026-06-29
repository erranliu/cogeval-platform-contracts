import json

from cogeval_platform_contracts.model_capabilities.resources import load_fixture, load_schema, list_fixtures
from cogeval_platform_contracts.model_capabilities.v1 import MODEL_CAPABILITY_CATALOG_SCHEMA, ModelCapabilityCatalog


def test_load_schema_returns_model_capability_schema() -> None:
    schema = load_schema("model_capability_catalog.v1")

    assert schema["properties"]["schema"]["const"] == MODEL_CAPABILITY_CATALOG_SCHEMA


def test_load_fixture_returns_valid_model_capability_catalog() -> None:
    payload = load_fixture("minimal.v1")

    catalog = ModelCapabilityCatalog.model_validate(payload)

    assert catalog.schema == MODEL_CAPABILITY_CATALOG_SCHEMA
    assert catalog.models[0].model_id == "gpt-5.5"


def test_list_fixtures_includes_minimal_fixture() -> None:
    assert "minimal.v1" in list_fixtures()


def test_model_capability_resources_are_json_serializable() -> None:
    json.dumps(load_schema("model_capability_catalog.v1"))
    json.dumps(load_fixture("minimal.v1"))
