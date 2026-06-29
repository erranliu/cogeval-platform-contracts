# Workbench Distribution Claims v1

Data schemas: `cogeval.distribution_claim_request.v1`, `cogeval.distribution_claim.v1`

Request producer: COGEval Workbench

Claim producer: COGEval Website Tasks API

## Purpose

This integration lets Workbench claim official platform-distributed run tasks. The platform selects an eligible subtask and returns a claim. Workbench starts or releases the claim and later submits results through the self-run package ingest integration.

## Platform Task API

Website Tasks API endpoints:

- Claim next task: `POST /api/tasks/claim`
- Start a claim: `POST /api/tasks/{claim_id}/start`
- Release a claim: `POST /api/tasks/{claim_id}/release`

Authentication: platform deployment policy. The contract requires the payload shape but does not define deployment-specific auth.

Request and response payloads:

- `POST /api/tasks/claim` consumes `cogeval.distribution_claim_request.v1`.
- All three endpoints return `cogeval.distribution_claim.v1`.

## Workbench Claim Client

- Workbench task-claim client is expected to call the `/api/tasks/*` endpoints against `platform_base_url`.
- Workbench should validate claim responses before treating a claim as runnable.
- Result submission still uses `POST /api/workbench/v1/ingest/package`; `claim_id` is task context, not the case identity.

## Data Flow

```text
Workbench capabilities and constraints
  -> POST /api/tasks/claim
  -> Website DistributionClaim
  -> POST /api/tasks/{claim_id}/start
  -> Workbench runs assigned cases
  -> POST /api/workbench/v1/ingest/package
  -> optional release on failure or user cancellation
```

## Failure Behavior

- No task available: platform may return 404.
- Invalid claim request: platform returns 400.
- Start or release state conflict: platform returns 409.
- Expired claim: platform may reject start/release or expire it through admin maintenance.
- Workbench must not submit results without preserving the `source_id + external_id` case identity from the claim case refs.

## Required Tests

Producer tests in the Website repository:

- Claim, start, release endpoints return valid `cogeval.distribution_claim.v1`.
- Claim request validation rejects invalid capability payloads.

Consumer tests in Workbench or task client repository:

- Claim responses are validated before run scheduling.
- Self-run package submission preserves claim context separately from case identity.
