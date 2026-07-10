from __future__ import annotations

import json

import cogeval_platform_contracts.model_pricing as model_pricing


def test_model_pricing_exports_resource_helpers() -> None:
    assert callable(model_pricing.load_schema)
    assert callable(model_pricing.list_fixtures)
    assert callable(model_pricing.load_fixture)


def test_list_fixtures_contains_both_v1_fixtures() -> None:
    assert {"empty.v1", "provider_models.v1"} <= set(model_pricing.list_fixtures())


def test_schema_and_fixtures_load_as_json_serializable_dicts() -> None:
    resources = [
        model_pricing.load_schema("model_pricing_catalog.v1"),
        model_pricing.load_fixture("empty.v1"),
        model_pricing.load_fixture("provider_models.v1"),
    ]

    for resource in resources:
        assert isinstance(resource, dict)
        json.dumps(resource)


def test_empty_fixture_has_stable_seed_timestamp_and_no_prices() -> None:
    payload = model_pricing.load_fixture("empty.v1")

    assert payload["updated_at"] == "2026-01-01T00:00:00Z"
    assert payload["prices"] == []


def test_provider_fixture_covers_representative_pricing_shapes() -> None:
    payload = model_pricing.load_fixture("provider_models.v1")
    prices = payload["prices"]

    assert len({price["provider_id"] for price in prices}) >= 2
    assert any(price["rates"]["input_cache_write"] != "0" for price in prices)
    assert any(
        price["rates"]["reasoning_output"] == price["rates"]["output"] != "0"
        for price in prices
    )
    assert any(all(rate == "0" for rate in price["rates"].values()) for price in prices)
