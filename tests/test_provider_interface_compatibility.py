from __future__ import annotations

from copy import deepcopy

from cogeval_platform_contracts.provider_interfaces.compatibility import compare_catalogs
from cogeval_platform_contracts.provider_interfaces.resources import load_fixture
from cogeval_platform_contracts.provider_interfaces.v1 import ProviderInterfaceCatalog


def test_compare_catalogs_allows_additive_provider() -> None:
    old = ProviderInterfaceCatalog.model_validate(load_fixture("minimal.v1"))
    new = ProviderInterfaceCatalog.model_validate(load_fixture("deepseek_openai_compatible.v1"))

    report = compare_catalogs(old, new)

    assert report.compatible is True
    assert report.breaking_changes == []
    assert any(change.code == "provider_added" for change in report.additive_changes)


def test_compare_catalogs_flags_removed_interface() -> None:
    old_payload = load_fixture("deepseek_openai_compatible.v1")
    new_payload = deepcopy(old_payload)
    new_payload["providers"][0]["supported_interfaces"] = [
        {"interface": "anthropic_compatible_messages"}
    ]
    old = ProviderInterfaceCatalog.model_validate(old_payload)
    new = ProviderInterfaceCatalog.model_validate(new_payload)

    report = compare_catalogs(old, new)

    assert report.compatible is False
    assert any(change.code == "interface_removed" for change in report.breaking_changes)
    assert any(change.code == "interface_added" for change in report.additive_changes)


def test_compare_catalogs_flags_removed_model() -> None:
    old_payload = load_fixture("deepseek_openai_compatible.v1")
    new_payload = deepcopy(old_payload)
    new_payload["providers"][0]["models"] = []
    new_payload["providers"][0]["status"] = "deprecated"
    old = ProviderInterfaceCatalog.model_validate(old_payload)
    new = ProviderInterfaceCatalog.model_validate(new_payload)

    report = compare_catalogs(old, new)

    assert report.compatible is False
    assert any(change.code == "model_removed" for change in report.breaking_changes)


def test_compare_catalogs_reports_provider_model_name_changes_as_informational() -> None:
    old_payload = load_fixture("deepseek_openai_compatible.v1")
    new_payload = deepcopy(old_payload)
    new_payload["providers"][0]["models"][0]["model_name"] = "deepseek-v4-flash"
    old = ProviderInterfaceCatalog.model_validate(old_payload)
    new = ProviderInterfaceCatalog.model_validate(new_payload)

    report = compare_catalogs(old, new)

    assert report.compatible is True
    assert any(change.code == "model_model_name_changed" for change in report.informational_changes)

