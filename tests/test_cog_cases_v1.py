from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.cog_cases import load_fixture
from cogeval_platform_contracts.cog_cases.v1 import (
    COG_CASE_SCHEMA,
    CogCase,
    validate_cog_case,
)


def test_cog_case_fixtures_are_valid() -> None:
    case = validate_cog_case(load_fixture("case_public.v1"))

    assert case.schema == COG_CASE_SCHEMA


def test_cog_case_requires_identity_fields() -> None:
    payload = load_fixture("case_public.v1")
    payload.pop("external_id")

    with pytest.raises(ValidationError):
        CogCase.model_validate(payload)


def test_workbench_integration_declares_case_no_lookup_contract() -> None:
    root = Path(__file__).resolve().parents[1]
    integration = (root / "docs" / "integrations" / "workbench-cog-cases-v1.md").read_text(encoding="utf-8")
    schema_doc = (root / "docs" / "COG_CASES_V1.md").read_text(encoding="utf-8")

    assert "GET /api/public/cog-cases/lookup" in integration
    assert "cog_case_no" in integration
    assert "cogeval.cog_case.v3" in integration
    assert "404" in integration
    assert "fully hydrated" in integration
    assert "source_id + external_id" in integration
    assert "cog_case_display_id" in schema_doc
    assert "lookup" in schema_doc
    assert "source_id + external_id" in schema_doc
