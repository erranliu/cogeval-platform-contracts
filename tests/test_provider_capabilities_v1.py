from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.provider_capabilities.v1 import (
    SCHEMA_VERSION,
    Capability,
    ProviderCapabilityCatalog,
)


FIXTURE_ROOT = (
    Path(__file__).parents[1]
    / "src"
    / "cogeval_platform_contracts"
    / "provider_capabilities"
    / "fixtures"
)
SCHEMA_PATH = (
    Path(__file__).parents[1]
    / "src"
    / "cogeval_platform_contracts"
    / "provider_capabilities"
    / "schemas"
    / "provider_capability_catalog.v1.schema.json"
)


@pytest.mark.parametrize("path", sorted(FIXTURE_ROOT.glob("*.json")))
def test_provider_capability_fixtures_are_valid(path: Path) -> None:
    catalog = ProviderCapabilityCatalog.model_validate_json(path.read_text(encoding="utf-8"))
    assert catalog.schema == SCHEMA_VERSION


def test_schema_file_matches_contract_version() -> None:
    payload = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert payload["properties"]["schema"]["const"] == SCHEMA_VERSION


def test_supported_capability_requires_values() -> None:
    with pytest.raises(ValidationError):
        Capability(supported=True)


def test_capability_default_must_be_declared_value() -> None:
    with pytest.raises(ValidationError):
        Capability(supported=True, values=["low"], default="high")

