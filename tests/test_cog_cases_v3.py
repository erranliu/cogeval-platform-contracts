from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.cog_cases import (
    COG_CASE_V3_SCHEMA,
    CogCaseV3,
    load_fixture,
    validate_cog_case_v3,
)


def test_cog_case_v3_fixture_requires_product_identity() -> None:
    case = validate_cog_case_v3(load_fixture("case_public.v3"))

    assert case.schema == COG_CASE_V3_SCHEMA
    assert case.cog_case_display_id == "SWEPro#1"


def test_cog_case_v3_rejects_missing_display_id() -> None:
    payload = load_fixture("case_public.v3")
    payload.pop("cog_case_display_id")

    with pytest.raises(ValidationError):
        CogCaseV3.model_validate(payload)
