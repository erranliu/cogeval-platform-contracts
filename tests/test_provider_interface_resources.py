from __future__ import annotations

import json

from cogeval_platform_contracts.provider_interfaces.resources import (
    list_fixtures,
    load_fixture,
    load_schema,
)
from cogeval_platform_contracts.provider_interfaces.v1 import (
    PROVIDER_INTERFACE_CATALOG_SCHEMA,
    ProviderInterfaceCatalog,
)


def test_load_schema_returns_provider_interface_schema() -> None:
    schema = load_schema("provider_interface_catalog.v1")

    assert schema["properties"]["schema"]["const"] == PROVIDER_INTERFACE_CATALOG_SCHEMA


def test_list_fixtures_returns_packaged_fixture_names() -> None:
    fixtures = list_fixtures()

    assert "minimal.v1" in fixtures
    assert "deepseek_openai_compatible.v1" in fixtures


def test_load_fixture_returns_valid_catalog_payload() -> None:
    payload = load_fixture("deepseek_openai_compatible.v1")

    catalog = ProviderInterfaceCatalog.model_validate(payload)
    assert catalog.providers[0].provider_id == "deepseek"


def test_loaded_schema_and_fixture_are_json_serializable() -> None:
    json.dumps(load_schema("provider_interface_catalog.v1"))
    json.dumps(load_fixture("minimal.v1"))

