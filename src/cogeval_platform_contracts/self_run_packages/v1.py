from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


SELF_RUN_PACKAGE_MANIFEST_SCHEMA = "cogeval.self_run_package_manifest.v1"
SELF_RUN_RECORD_SCHEMA = "cogeval.self_run_record.v1"
EVIDENCE_BUNDLE_SCHEMA = "cogeval.evidence_bundle.v1"
PACKAGE_IMPORT_RESULT_SCHEMA = "cogeval.package_import_result.v1"

Outcome = Literal["resolved", "unresolved", "error", "mixed"]
RunOutcome = Literal["resolved", "unresolved", "error"]


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SelfRunPackageManifest(StrictContractModel):
    schema_: Literal["cogeval.self_run_package_manifest.v1"] = Field(alias="schema")
    schema_version: str = Field(min_length=1)
    submitter: str | None = None
    package_id: str = Field(min_length=1)
    created_at: str = Field(min_length=1)
    target_source_id: str = Field(min_length=1)
    submitted_by_account_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def schema(self) -> str:
        return self.schema_


class SelfRunRun(StrictContractModel):
    run_index: int = Field(ge=0)
    outcome: RunOutcome
    metrics: dict[str, Any] = Field(default_factory=dict)
    evidence_ref: str | None = None


class SelfRunRecord(StrictContractModel):
    schema_: Literal["cogeval.self_run_record.v1"] = Field(alias="schema")
    external_case_ref: str = Field(min_length=1)
    agent: str = Field(min_length=1)
    agent_version: str | None = None
    model: str = Field(min_length=1)
    model_version: str | None = None
    thinking_effort: str | None = None
    control_vars: dict[str, Any] = Field(default_factory=dict)
    outcome: Outcome
    pass_rate: float = Field(ge=0, le=1)
    repeat_count: int = Field(ge=0)
    result_summary: dict[str, Any] = Field(default_factory=dict)
    runs: list[SelfRunRun] = Field(default_factory=list)

    @property
    def schema(self) -> str:
        return self.schema_

    @model_validator(mode="after")
    def validate_aggregate(self) -> "SelfRunRecord":
        if self.repeat_count != len(self.runs):
            raise ValueError("repeat_count must match runs length")
        if self.runs:
            expected = list(range(len(self.runs)))
            actual = [run.run_index for run in self.runs]
            if actual != expected:
                raise ValueError("run_index values must be contiguous from 0")
        return self


class EvidenceBundle(StrictContractModel):
    schema_: Literal["cogeval.evidence_bundle.v1"] = Field(alias="schema")
    trajectory: str | None = None
    final_diff: str | None = None
    test_execution_result: dict[str, Any] | None = None

    @property
    def schema(self) -> str:
        return self.schema_

    @model_validator(mode="after")
    def validate_verifiable(self) -> "EvidenceBundle":
        if self.test_execution_result is None:
            raise ValueError("test_execution_result is required")
        return self


class RecordImportResult(StrictContractModel):
    external_case_ref: str = Field(min_length=1)
    accepted: bool
    test_result_id: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    queued_for_review: bool = False
    review_item_id: str | None = None


class PackageImportResult(StrictContractModel):
    schema_: Literal["cogeval.package_import_result.v1"] = Field(alias="schema")
    package_id: str | None = None
    snapshot_id: str = Field(min_length=1)
    n_accepted: int = Field(ge=0)
    n_rejected: int = Field(ge=0)
    results: list[RecordImportResult] = Field(default_factory=list)

    @property
    def schema(self) -> str:
        return self.schema_

    @model_validator(mode="after")
    def validate_counts(self) -> "PackageImportResult":
        accepted = sum(1 for item in self.results if item.accepted)
        rejected = len(self.results) - accepted
        if accepted != self.n_accepted or rejected != self.n_rejected:
            raise ValueError("n_accepted and n_rejected must match results")
        return self


def validate_self_run_package_manifest(payload: Any) -> SelfRunPackageManifest:
    return SelfRunPackageManifest.model_validate(payload)


def validate_self_run_record(payload: Any) -> SelfRunRecord:
    return SelfRunRecord.model_validate(payload)


def validate_evidence_bundle(payload: Any) -> EvidenceBundle:
    return EvidenceBundle.model_validate(payload)


def validate_package_import_result(payload: Any) -> PackageImportResult:
    return PackageImportResult.model_validate(payload)
