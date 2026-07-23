# COGEval integration contracts

This index records the platform contracts used by Workbench. JSON Schema and
Pydantic definitions remain the authoritative payload definitions; these docs
describe the API producer, consumer, and failure boundary.

## Principles

- Every Workbench integration has one current contract entry and one owner.
- API paths, authentication, envelopes, and required fields are documented in
  the contract repository, not redefined in the Workbench repository.
- Historical payloads are not discovered, migrated, or silently normalized.

## Integrations

| Integration | Schema | Direction | Platform API | Workbench entrypoint | Contract |
|---|---|---|---|---|---|
| Workbench COG Cases current | `cogeval.cog_case.v3`, `cogeval.cog_case_group.v1` | Platform -> Workbench | `GET /api/public/cog-cases`, `/lookup`, `/api/public/cog-case-groups` | COG Cases local API | [workbench-cog-cases-current.md](workbench-cog-cases-current.md) |
| Workbench API Key Provider Catalog v1 | `cogeval.interface_capability_catalog.v1` | Platform -> Workbench | `GET /api/workbench/v1/api-key-providers` | provider catalog loader | [workbench-api-key-provider-catalog-v1.md](workbench-api-key-provider-catalog-v1.md) |
| Workbench Model Pricing Catalog v1 | `cogeval.model_pricing_catalog.v1` | Platform -> Workbench | `GET /api/workbench/v1/model-pricing` | model pricing catalog loader | [workbench-model-pricing-v1.md](workbench-model-pricing-v1.md) |
| Workbench Provider Capability Catalog v1 | `cogeval.provider_capability_catalog.v1` | Platform -> Workbench | bundled or configured capability catalog path | provider catalog loader | [workbench-provider-capability-catalog-v1.md](workbench-provider-capability-catalog-v1.md) |
| Workbench Model Capability Catalog v2 | `cogeval.model_capability_catalog.v2` | Platform -> Workbench | `GET /api/workbench/v1/model-capabilities` | execution selection catalog | [workbench-model-capability-catalog-v2.md](workbench-model-capability-catalog-v2.md) |
| Workbench Gateway Consistency v1 | `cogeval.gateway_consistency.task_pack.v1` | Platform -> Workbench | `GET /api/workbench/v1/gateway-consistency/task-pack` | Gateway Consistency local API | [workbench-gateway-consistency-v1.md](workbench-gateway-consistency-v1.md) |
| Workbench Accounts v1 | `cogeval.workbench.*.v1` | Bidirectional | `/api/workbench/v1/auth/github`, `/me`, `/assets`, `/coin-reservations` | platform account client | [workbench-accounts-v1.md](workbench-accounts-v1.md) |
| Workbench Self-run Package Ingest v2 | `cogeval.package_import_result.v2`, `cogeval.failure-reason.v1` | Workbench -> Platform | `POST /api/workbench/v1/ingest/package` | current self-run submit flow | [workbench-self-run-package-ingest-v2.md](workbench-self-run-package-ingest-v2.md) |
| Workbench Distribution Claims v1 | `cogeval.distribution_claim*.v1` | Workbench -> Platform | `/api/tasks/claim`, `/api/tasks/{claim_id}/start`, `/release` | task claim client | [workbench-distribution-claims-v1.md](workbench-distribution-claims-v1.md) |

## Adding an integration

1. Register the schemas in the contract and integration documents.
2. Define the producer API, authentication, envelope, consumer entrypoint,
   configuration overrides, failure behavior, and test checklist.
3. Add producer and consumer contract tests before changing either repository.
