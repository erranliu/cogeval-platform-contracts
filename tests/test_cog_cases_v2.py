from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.cog_cases import load_fixture
from cogeval_platform_contracts.cog_cases.v1 import COG_CASE_SCHEMA, CogCase
from cogeval_platform_contracts.cog_cases.v2 import (
    COG_CASE_V2_SCHEMA,
    validate_cog_case_v2,
)


def test_cog_case_v2_fixture_declares_environment_requirements() -> None:
    case = validate_cog_case_v2(load_fixture("case_public.v2"))

    assert case.schema == COG_CASE_V2_SCHEMA
    assert case.environment_requirements[0].id == "go_toolchain"
    assert case.environment_requirements[0].required is True
    assert "candidate_execution" in case.environment_requirements[0].applies_to


def test_cog_case_v2_rejects_unknown_environment_resource() -> None:
    payload = load_fixture("case_public.v2")
    payload["environment_requirements"][0]["id"] = "unknown_toolchain"

    with pytest.raises(ValidationError):
        validate_cog_case_v2(payload)


def test_cog_case_v1_still_rejects_top_level_environment_requirements() -> None:
    payload = load_fixture("case_public.v1")
    payload["environment_requirements"] = []

    assert payload["schema"] == COG_CASE_SCHEMA
    with pytest.raises(ValidationError):
        CogCase.model_validate(payload)
