from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from cogeval_platform_contracts.cog_cases.v1 import StrictContractModel
from cogeval_platform_contracts.cog_cases.v2 import CaseEnvironmentRequirement


COG_CASE_V3_SCHEMA = "cogeval.cog_case.v3"


class CogCaseV3(StrictContractModel):
    """Current published COG Case contract with a required product identity."""

    schema_: Literal["cogeval.cog_case.v3"] = Field(alias="schema")
    test_case_id: str = Field(min_length=1)
    cog_case_display_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    external_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    original_url: str | None = None
    labels: dict[str, Any] = Field(default_factory=dict)
    semantic_profile: dict[str, Any] = Field(default_factory=dict)
    semantic_version: str | None = None
    interpretation: str | None = None
    online_at: str | None = None
    promoted_at: str = Field(min_length=1)
    environment_requirements: list[CaseEnvironmentRequirement] = Field(default_factory=list)

    @property
    def schema(self) -> str:
        return self.schema_


def validate_cog_case_v3(payload: Any) -> CogCaseV3:
    return CogCaseV3.model_validate(payload)
