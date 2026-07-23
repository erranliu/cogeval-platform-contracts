from __future__ import annotations

from typing import Any

from cogeval_platform_contracts.cog_cases.current import CurrentCogCase


COG_CASE_V3_SCHEMA = "cogeval.cog_case.v3"
CogCaseV3 = CurrentCogCase


def validate_cog_case_v3(payload: Any) -> CurrentCogCase:
    """Historical import path pointing at the single current v3 owner."""
    return CurrentCogCase.model_validate(payload)
