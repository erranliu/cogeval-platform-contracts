"""Current self-run package wire contract.

Package contents retain their established v1 schema identifiers; the import
decision is the single v2 result contract. This module is the only active
entry point for Workbench producers and consumers.
"""

from cogeval_platform_contracts.self_run_packages.v1 import (
    EVIDENCE_BUNDLE_SCHEMA,
    SELF_RUN_PACKAGE_MANIFEST_SCHEMA,
    SELF_RUN_RECORD_SCHEMA,
    EvidenceBundle,
    SelfRunPackageManifest,
    SelfRunRecord,
    SelfRunRun,
    Outcome,
    RunOutcome,
    validate_evidence_bundle,
    validate_self_run_package_manifest,
    validate_self_run_record,
)
from cogeval_platform_contracts.self_run_packages.v2 import (
    PACKAGE_IMPORT_RESULT_SCHEMA_V2,
    PackageImportResultV2,
    RecordImportResultV2,
    validate_package_import_result_v2,
)

__all__ = [
    "EVIDENCE_BUNDLE_SCHEMA",
    "SELF_RUN_PACKAGE_MANIFEST_SCHEMA",
    "SELF_RUN_RECORD_SCHEMA",
    "EvidenceBundle",
    "SelfRunPackageManifest",
    "SelfRunRecord",
    "SelfRunRun",
    "Outcome",
    "RunOutcome",
    "validate_evidence_bundle",
    "validate_self_run_package_manifest",
    "validate_self_run_record",
    "PACKAGE_IMPORT_RESULT_SCHEMA_V2",
    "PackageImportResultV2",
    "RecordImportResultV2",
    "validate_package_import_result_v2",
]
