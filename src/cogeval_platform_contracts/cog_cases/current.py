"""Current-only public COG Case contracts consumed by Workbench.

The current cut is deliberately strict: producers publish a fully hydrated
v3 case and a v1 group envelope. Historical case validators are not part of
the active Workbench boundary.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


COG_CASE_SCHEMA = "cogeval.cog_case.v3"
COG_CASE_GROUP_SCHEMA = "cogeval.cog_case_group.v1"


class StrictCurrentContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CaseEnvironmentRequirement(StrictCurrentContractModel):
    id: Literal["docker_engine", "go_toolchain"]
    kind: Literal["container_engine", "host_toolchain"]
    display_name: str = Field(min_length=1)
    required: bool = True
    version_constraint: str | None = None
    applies_to: list[Literal["workspace_prepare", "candidate_execution", "official_validation"]] = Field(default_factory=list)
    reason: str | None = None


class CurrentCogCase(StrictCurrentContractModel):
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
    # Source-specific public projections may omit these fields. When present,
    # they are validated as part of the single current snapshot rather than
    # being merged from a legacy detail endpoint.
    summary: str | None = None
    source_text: str | None = None
    task_type: str | None = None
    tags: list[Any] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    source: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    source_locator: dict[str, Any] = Field(default_factory=dict)
    validation: dict[str, Any] | None = None
    workspace: dict[str, Any] | None = None

    @property
    def schema(self) -> str:
        return self.schema_


class CurrentCogCaseGroup(StrictCurrentContractModel):
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
    members: list[CurrentCogCase] = Field(default_factory=list)
    created_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_member_count(self) -> "CurrentCogCaseGroup":
        if self.member_count != len(self.members):
            raise ValueError("member_count must match members length")
        return self

    @property
    def schema(self) -> str:
        return self.schema_


def validate_current_cog_case(payload: Any) -> CurrentCogCase:
    return CurrentCogCase.model_validate(payload)


def validate_current_cog_case_group(payload: Any) -> CurrentCogCaseGroup:
    return CurrentCogCaseGroup.model_validate(payload)
