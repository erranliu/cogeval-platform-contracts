from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.self_run_packages import load_fixture
from cogeval_platform_contracts.self_run_packages.v1 import (
    EVIDENCE_BUNDLE_SCHEMA,
    PACKAGE_IMPORT_RESULT_SCHEMA,
    SELF_RUN_PACKAGE_MANIFEST_SCHEMA,
    SELF_RUN_RECORD_SCHEMA,
    EvidenceBundle,
    PackageImportResult,
    SelfRunPackageManifest,
    SelfRunRecord,
    validate_evidence_bundle,
    validate_package_import_result,
    validate_self_run_package_manifest,
    validate_self_run_record,
)


def test_self_run_package_fixtures_are_valid() -> None:
    manifest = validate_self_run_package_manifest(load_fixture("manifest_minimal.v1"))
    record = validate_self_run_record(load_fixture("record_resolved.v1"))
    evidence = validate_evidence_bundle(load_fixture("evidence_minimal.v1"))
    result = validate_package_import_result(load_fixture("import_result_mixed.v1"))

    assert manifest.schema == SELF_RUN_PACKAGE_MANIFEST_SCHEMA
    assert record.schema == SELF_RUN_RECORD_SCHEMA
    assert evidence.schema == EVIDENCE_BUNDLE_SCHEMA
    assert result.schema == PACKAGE_IMPORT_RESULT_SCHEMA


def test_self_run_manifest_requires_target_source_id() -> None:
    payload = load_fixture("manifest_minimal.v1")
    payload.pop("target_source_id")

    with pytest.raises(ValidationError):
        SelfRunPackageManifest.model_validate(payload)


def test_self_run_record_requires_repeat_count_to_match_runs() -> None:
    payload = load_fixture("record_resolved.v1")
    payload["repeat_count"] = 2

    with pytest.raises(ValidationError, match="repeat_count must match runs length"):
        SelfRunRecord.model_validate(payload)


def test_self_run_record_rejects_invalid_pass_rate() -> None:
    payload = load_fixture("record_resolved.v1")
    payload["pass_rate"] = 1.5

    with pytest.raises(ValidationError):
        SelfRunRecord.model_validate(payload)


def test_evidence_bundle_requires_machine_verifiable_content() -> None:
    with pytest.raises(ValidationError, match="test_execution_result is required"):
        EvidenceBundle.model_validate({"schema": EVIDENCE_BUNDLE_SCHEMA})


def test_import_result_counts_must_match_rows() -> None:
    payload = load_fixture("import_result_mixed.v1")
    payload["n_accepted"] = 99

    with pytest.raises(ValidationError, match="n_accepted and n_rejected must match results"):
        PackageImportResult.model_validate(payload)
