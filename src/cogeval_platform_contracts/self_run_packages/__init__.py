"""Self-run package contracts."""

from cogeval_platform_contracts.self_run_packages.resources import list_fixtures, load_fixture, load_schema
from cogeval_platform_contracts.self_run_packages.v1 import (
    EVIDENCE_BUNDLE_SCHEMA,
    PACKAGE_IMPORT_RESULT_SCHEMA,
    SELF_RUN_PACKAGE_MANIFEST_SCHEMA,
    SELF_RUN_RECORD_SCHEMA,
    EvidenceBundle,
    PackageImportResult,
    RecordImportResult,
    SelfRunPackageManifest,
    SelfRunRecord,
    SelfRunRun,
    validate_evidence_bundle,
    validate_package_import_result,
    validate_self_run_package_manifest,
    validate_self_run_record,
)

__all__ = [
    "EVIDENCE_BUNDLE_SCHEMA",
    "PACKAGE_IMPORT_RESULT_SCHEMA",
    "SELF_RUN_PACKAGE_MANIFEST_SCHEMA",
    "SELF_RUN_RECORD_SCHEMA",
    "EvidenceBundle",
    "PackageImportResult",
    "RecordImportResult",
    "SelfRunPackageManifest",
    "SelfRunRecord",
    "SelfRunRun",
    "list_fixtures",
    "load_fixture",
    "load_schema",
    "validate_evidence_bundle",
    "validate_package_import_result",
    "validate_self_run_package_manifest",
    "validate_self_run_record",
]
