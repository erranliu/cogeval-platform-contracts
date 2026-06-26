from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.provider_capabilities.v1 import (
    SCHEMA_VERSION,
    Capability,
    EffortValue,
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


def test_thinking_effort_platform_values_exclude_disable_controls() -> None:
    assert set(EffortValue.__args__) == {
        "default",
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
        "max",
    }
    assert "off" not in EffortValue.__args__
    assert "adaptive" not in EffortValue.__args__
    assert "none" not in EffortValue.__args__


def test_thinking_effort_rejects_non_platform_values() -> None:
    payload = {
        "schema": SCHEMA_VERSION,
        "updated_at": "2026-06-25T00:00:00Z",
        "providers": [
            {
                "provider_id": "invalid",
                "display_name": "Invalid",
                "interfaces": [
                    {
                        "interface": "openai_responses",
                        "parameter_surfaces": {
                            "thinking_effort": {
                                "path": "reasoning.effort",
                                "values": ["none", "high"],
                            }
                        },
                    }
                ],
                "models": [
                    {
                        "model_id": "invalid-model",
                        "display_name": "Invalid Model",
                        "model_name": "invalid-model",
                        "interface_capabilities": {
                            "openai_responses": {
                                "thinking_effort": {
                                    "supported": True,
                                    "values": ["default", "none", "high"],
                                    "default": "default",
                                    "parameter_surface": "thinking_effort",
                                }
                            }
                        },
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError):
        ProviderCapabilityCatalog.model_validate(payload)


def test_deepseek_thinking_effort_is_declared_per_interface() -> None:
    catalog = ProviderCapabilityCatalog.model_validate_json(
        (FIXTURE_ROOT / "deepseek_reasoning.v1.json").read_text(encoding="utf-8")
    )
    model = catalog.providers[0].models[0]

    capability = model.interface_capabilities["openai_compatible_chat"]["thinking_effort"]

    assert capability.values == ["default", "high", "max"]
    assert capability.default == "default"
