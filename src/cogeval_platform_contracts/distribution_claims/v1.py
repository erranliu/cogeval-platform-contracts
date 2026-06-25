from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


DISTRIBUTION_CLAIM_REQUEST_SCHEMA = "cogeval.distribution_claim_request.v1"
DISTRIBUTION_CLAIM_SCHEMA = "cogeval.distribution_claim.v1"


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class DistributionClaimRequest(StrictContractModel):
    schema_: Literal["cogeval.distribution_claim_request.v1"] = Field(alias="schema")
    workbench_id: str | None = None
    agents: list[dict[str, Any]] = Field(default_factory=list)
    supported_sources: list[str] = Field(default_factory=list)
    workspace_readiness: dict[str, Any] = Field(default_factory=dict)
    max_minutes: int | None = Field(default=90, ge=1)

    @property
    def schema(self) -> str:
        return self.schema_


class DistributionClaim(StrictContractModel):
    schema_: Literal["cogeval.distribution_claim.v1"] = Field(alias="schema")
    claim_id: str = Field(min_length=1)
    goal_id: str = Field(min_length=1)
    subtask_id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    workbench_id: str | None = None
    capability_snapshot: dict[str, Any] = Field(default_factory=dict)
    candidate_config: dict[str, Any] = Field(default_factory=dict)
    case_refs: list[dict[str, Any]]
    claimed_at: str = Field(min_length=1)
    occupied_at: str | None = None
    expires_at: str = Field(min_length=1)
    released_at: str | None = None

    @property
    def schema(self) -> str:
        return self.schema_


def validate_distribution_claim_request(payload: Any) -> DistributionClaimRequest:
    return DistributionClaimRequest.model_validate(payload)


def validate_distribution_claim(payload: Any) -> DistributionClaim:
    return DistributionClaim.model_validate(payload)
