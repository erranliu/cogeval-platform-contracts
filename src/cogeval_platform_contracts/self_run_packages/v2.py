from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator

from cogeval_platform_contracts.failure_reasons import FailureReasonV1
from cogeval_platform_contracts.self_run_packages.v1 import StrictContractModel

PACKAGE_IMPORT_RESULT_SCHEMA_V2 = "cogeval.package_import_result.v2"


class RecordImportResultV2(StrictContractModel):
    external_case_ref: str = Field(min_length=1)
    accepted: bool
    test_result_id: str | None = None
    failure_reason: FailureReasonV1 | None = None
    decision_codes: list[str] = Field(default_factory=list)
    queued_for_review: bool = False
    review_item_id: str | None = None

    @model_validator(mode="after")
    def validate_reason_boundary(self) -> "RecordImportResultV2":
        if self.accepted and self.failure_reason is not None:
            raise ValueError("accepted result cannot contain failure_reason")
        if self.failure_reason is not None and self.decision_codes:
            raise ValueError("failure result cannot contain decision_codes")
        if self.queued_for_review and self.failure_reason is not None:
            raise ValueError("review decision cannot contain failure_reason")
        if self.queued_for_review and not self.decision_codes:
            raise ValueError("queued review result requires decision_codes")
        if not self.accepted and not self.queued_for_review and self.failure_reason is None:
            raise ValueError("rejected result requires failure_reason")
        return self


class PackageImportResultV2(StrictContractModel):
    schema_: Literal["cogeval.package_import_result.v2"] = Field(alias="schema")
    package_id: str | None = None
    snapshot_id: str = Field(min_length=1)
    n_accepted: int = Field(ge=0)
    n_rejected: int = Field(ge=0)
    results: list[RecordImportResultV2] = Field(default_factory=list)

    @property
    def schema(self) -> str:
        return self.schema_

    @model_validator(mode="after")
    def validate_counts(self) -> "PackageImportResultV2":
        accepted = sum(1 for item in self.results if item.accepted)
        rejected = len(self.results) - accepted
        if accepted != self.n_accepted or rejected != self.n_rejected:
            raise ValueError("n_accepted and n_rejected must match results")
        return self


def validate_package_import_result_v2(payload: Any) -> PackageImportResultV2:
    return PackageImportResultV2.model_validate(payload)
