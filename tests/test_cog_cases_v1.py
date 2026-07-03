from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.cog_cases import (
    COG_CASE_GROUP_SCHEMA,
    COG_CASE_SCHEMA,
    CogCase,
    CogCaseGroup,
    load_fixture,
    validate_cog_case,
    validate_cog_case_group,
)


def test_cog_case_fixtures_are_valid() -> None:
    case = validate_cog_case(load_fixture("case_public.v1"))
    group = validate_cog_case_group(load_fixture("group_public.v1"))

    assert case.schema == COG_CASE_SCHEMA
    assert group.schema == COG_CASE_GROUP_SCHEMA
    assert group.members[0].test_case_id == case.test_case_id


def test_cog_case_requires_identity_fields() -> None:
    payload = load_fixture("case_public.v1")
    payload.pop("external_id")

    with pytest.raises(ValidationError):
        CogCase.model_validate(payload)


def test_cog_case_group_requires_public_members_to_match_contract() -> None:
    payload = load_fixture("group_public.v1")
    payload["members"][0].pop("source_id")

    with pytest.raises(ValidationError):
        CogCaseGroup.model_validate(payload)


def test_cog_case_group_rejects_time_scope() -> None:
    payload = load_fixture("group_public.v1")
    payload["time_scope"] = {"label": "2026 H1"}

    with pytest.raises(ValidationError):
        CogCaseGroup.model_validate(payload)
