from __future__ import annotations

import json

from cogeval_platform_contracts.provider_capabilities.resources import (
    load_fixture,
    load_schema,
    list_fixtures,
)
from cogeval_platform_contracts.provider_capabilities.v1 import SCHEMA_VERSION, ProviderCapabilityCatalog


def test_load_schema_returns_provider_capability_schema() -> None:
    schema = load_schema("provider_capability_catalog.v1")

    assert schema["properties"]["schema"]["const"] == SCHEMA_VERSION


def test_list_fixtures_returns_packaged_fixture_names() -> None:
    fixtures = list_fixtures()

    assert "openai_reasoning.v1" in fixtures
    assert "minimal.v1" in fixtures


def test_load_fixture_returns_valid_catalog_payload() -> None:
    payload = load_fixture("openai_reasoning.v1")

    catalog = ProviderCapabilityCatalog.model_validate(payload)
    assert catalog.providers[0].provider_id == "openai"


def test_loaded_schema_and_fixture_are_json_serializable() -> None:
    json.dumps(load_schema("provider_capability_catalog.v1"))
    json.dumps(load_fixture("minimal.v1"))

