from __future__ import annotations

from copy import deepcopy

from cogeval_platform_contracts.provider_capabilities.compatibility import compare_catalogs
from cogeval_platform_contracts.provider_capabilities.resources import load_fixture
from cogeval_platform_contracts.provider_capabilities.v1 import ProviderCapabilityCatalog


def test_compare_catalogs_allows_additive_provider() -> None:
    old = ProviderCapabilityCatalog.model_validate(load_fixture("minimal.v1"))
    new_payload = load_fixture("openai_reasoning.v1")
    new = ProviderCapabilityCatalog.model_validate(new_payload)

    report = compare_catalogs(old, new)

    assert report.compatible is True
    assert report.breaking_changes == []
    assert any(change.code == "provider_added" for change in report.additive_changes)


def test_compare_catalogs_flags_removed_capability_value() -> None:
    old_payload = load_fixture("openai_reasoning.v1")
    new_payload = deepcopy(old_payload)
    capability = new_payload["providers"][0]["models"][0]["capabilities"]["thinking_effort"]
    capability["values"].remove("high")
    if capability["default"] == "high":
        capability["default"] = "medium"
    old = ProviderCapabilityCatalog.model_validate(old_payload)
    new = ProviderCapabilityCatalog.model_validate(new_payload)

    report = compare_catalogs(old, new)

    assert report.compatible is False
    assert any(change.code == "capability_value_removed" for change in report.breaking_changes)


def test_compare_catalogs_flags_removed_interface_capability_value() -> None:
    old_payload = load_fixture("deepseek_reasoning.v1")
    new_payload = deepcopy(old_payload)
    capability = new_payload["providers"][0]["models"][0]["interface_capabilities"]["openai_compatible_chat"][
        "thinking_effort"
    ]
    capability["values"].remove("max")
    old = ProviderCapabilityCatalog.model_validate(old_payload)
    new = ProviderCapabilityCatalog.model_validate(new_payload)

    report = compare_catalogs(old, new)

    assert report.compatible is False
    assert any(change.code == "interface_capability_value_removed" for change in report.breaking_changes)


def test_compare_catalogs_flags_removed_provider() -> None:
    old = ProviderCapabilityCatalog.model_validate(load_fixture("openai_reasoning.v1"))
    new = ProviderCapabilityCatalog.model_validate(load_fixture("minimal.v1"))

    report = compare_catalogs(old, new)

    assert report.compatible is False
    assert any(change.code == "provider_removed" for change in report.breaking_changes)
