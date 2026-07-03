from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


COG_CASE_SCHEMA = "cogeval.cog_case.v1"
COG_CASE_GROUP_SCHEMA = "cogeval.cog_case_group.v1"


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CogCase(StrictContractModel):
    schema_: Literal["cogeval.cog_case.v1"] = Field(alias="schema")
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

    @property
    def schema(self) -> str:
        return self.schema_


class CogCaseGroup(StrictContractModel):
    schema_: Literal["cogeval.cog_case_group.v1"] = Field(alias="schema")
    group_id: str = Field(min_length=1)
    slug: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    theme_tags: list[str] = Field(default_factory=list)
    status: Literal["draft", "published", "archived"] = "draft"
    visibility: Literal["internal", "public"] = "internal"
    selection_mode: Literal["manual", "rule_snapshot"] = "manual"
    selection_filters: dict[str, Any] = Field(default_factory=dict)
    member_count: int = Field(default=0, ge=0)
    members: list[CogCase] = Field(default_factory=list)
    created_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)

    @property
    def schema(self) -> str:
        return self.schema_


def validate_cog_case(payload: Any) -> CogCase:
    return CogCase.model_validate(payload)


def validate_cog_case_group(payload: Any) -> CogCaseGroup:
    return CogCaseGroup.model_validate(payload)
