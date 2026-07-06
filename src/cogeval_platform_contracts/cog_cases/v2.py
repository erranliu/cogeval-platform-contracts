from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from cogeval_platform_contracts.cog_cases.v1 import StrictContractModel


COG_CASE_V2_SCHEMA = "cogeval.cog_case.v2"


class CaseEnvironmentRequirement(StrictContractModel):
    id: Literal["docker_engine", "go_toolchain"]
    kind: Literal["container_engine", "host_toolchain"]
    display_name: str = Field(min_length=1)
    required: bool = True
    version_constraint: str | None = None
    applies_to: list[Literal["workspace_prepare", "candidate_execution", "official_validation"]] = Field(default_factory=list)
    reason: str | None = None


class CogCaseV2(StrictContractModel):
    schema_: Literal["cogeval.cog_case.v2"] = Field(alias="schema")
    test_case_id: str = Field(min_length=1)
    cog_case_display_id: str | None = None
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


def validate_cog_case_v2(payload: Any) -> CogCaseV2:
    return CogCaseV2.model_validate(payload)
