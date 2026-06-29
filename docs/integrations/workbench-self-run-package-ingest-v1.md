# Workbench Self-run Package Ingest v1

Data schemas: `cogeval.self_run_package_manifest.v1`, `cogeval.self_run_record.v1`, `cogeval.evidence_bundle.v1`, `cogeval.package_import_result.v1`

Request payload producer: COGEval Workbench

Receiver and response producer: COGEval Website Workbench API

## Purpose

This integration submits locally generated Workbench run results to the platform. Workbench exports a self-run package and posts it to Website ingest. Website validates the package, imports accepted results, and returns a package import result.

## Platform Receive API

Website receives Workbench-submitted packages through:

- User submission: `POST /api/workbench/v1/ingest/package`
- Admin submission: `POST /api/admin/ingest/package`

Authentication:

- Workbench user submission requires a Workbench session Bearer token.
- User submission requires an `Idempotency-Key` header.
- Admin submission follows admin API authentication policy and is not the default Workbench path.

Request shape:

- Either `package_dir` pointing to a package directory visible to the server, or inline `manifest`, `results`, and `evidence`.
- `manifest` must validate as `cogeval.self_run_package_manifest.v1`.
- Result records must validate as `cogeval.self_run_record.v1`.
- Evidence entries must validate as `cogeval.evidence_bundle.v1` when dereferenced.

Response payload:

- Successful response validates as `cogeval.package_import_result.v1` plus platform asset award fields when returned by the Workbench user API.

## Workbench Submitter

- Workbench local submit API: `POST /api/test-results/submit-package`
- Platform submit URL: `${platform_base_url}/api/workbench/v1/ingest/package`
- Workbench implementation: `src/cogeval/workbench/test_results_api.py` and `src/cogeval/workbench/platform_account.py`.
- Workbench validates the platform import result with `cogeval_platform_contracts.self_run_packages.v1.validate_package_import_result`.

## Data Flow

```text
Workbench completed local runs
  -> export self-run package
  -> POST /api/workbench/v1/ingest/package
  -> Website validates/imports package
  -> package import result and optional asset award
  -> Workbench local submission record
```

Case identity must close the loop from COG Case read to result submission:

- `manifest.target_source_id` is the platform `source_id`.
- `record.external_case_ref` is the platform `external_id`.

## Failure Behavior

- Platform not configured: Workbench exports locally and marks the package as not submitted.
- Session missing: Workbench blocks remote submission.
- Account mismatch: platform rejects packages whose `submitted_by_account_id` does not match the session account.
- Unknown source or case identity: platform rejects or queues the record according to ingest policy.
- Invalid package: platform returns a structured invalid request/import result.

## Required Tests

Producer tests in the Workbench repository:

- Exported package manifest, records, and evidence validate against contract fixtures.
- Platform submission posts to `/api/workbench/v1/ingest/package`.

Consumer tests in the Website repository:

- Workbench ingest rejects account mismatch.
- Inline and package-dir submissions validate package contents.
- Import result counts match accepted/rejected records.
