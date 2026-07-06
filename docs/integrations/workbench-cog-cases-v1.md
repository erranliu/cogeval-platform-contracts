# Workbench COG Cases v1/v2

Data schemas: `cogeval.cog_case.v1`, `cogeval.cog_case.v2`, `cogeval.cog_case_group.v1`

Producer: COGEval Website public API

Consumer: COGEval Workbench COG Cases view and workspace preparation flow

## Purpose

This integration provides published COG Cases from the platform to Workbench. Workbench lists these cases, enriches them with local workspace readiness, prepares case workspaces, and creates local test runs using the case identity returned by the platform.

## Producer API

- List cases: `GET /api/public/cog-cases`
- Case detail: `GET /api/public/cog-cases/{test_case_id}`
- List public groups: `GET /api/public/cog-case-groups`
- Group detail: `GET /api/public/cog-case-groups/{slug}`
- Authentication: none for public published COG Case reads.
- List response shape: paged object with `items`, `next_cursor`, and compatible paging fields. Workbench also tolerates legacy list responses.
- Case payloads must validate as `cogeval.cog_case.v1` or `cogeval.cog_case.v2`.
- Group payloads must validate as `cogeval.cog_case_group.v1`.
- Producers must use `cogeval.cog_case.v2` when emitting top-level `environment_requirements`.

## Consumer Loader

- Workbench local API: `GET /api/cog-cases`
- Platform URL: `${platform_base_url}/api/public/cog-cases`
- Loader implementation: `src/cogeval/workbench/cases_api.py` in the Workbench repository.
- Workbench may fetch `/api/public/test-cases/{test_case_id}` as a detail fallback when a COG Case omits fields needed for local workspace matching.
- Workbench validates known COG Case payloads with the matching `cogeval_platform_contracts.cog_cases` validator and preserves forward-compatible fields for local projection.

## Data Flow

```text
Website published COG Cases
  -> GET /api/public/cog-cases
  -> WorkbenchCasesApi.list_platform_cog_cases()
  -> local registry / prepared workspace enrichment
  -> GET /api/cog-cases
  -> COG Cases UI
```

Workbench execution and result submission use `source_id + external_id` as the case identity loop. `cog_case_display_id` is display-only and must not replace the execution identity.

## Case Environment Requirements

COG Case v2 may include `environment_requirements` to declare local resources needed by the case. Current canonical resources are:

- `docker_engine`
- `go_toolchain`

The platform only declares the requirement. Workbench probes local status, exposes the unified Test Environment API, and enriches `/api/cog-cases` with `environment_status` for UI gating. Workbench may still infer requirements for v1 payloads from authorized validation fields or source metadata, but explicit v2 requirements take precedence.

## Case Source and Validation Boundary

Platform COG Case payloads are public projections. They provide case identity, display fields, grouping, and source locator fields that are allowed to be published. They are not the required transport for restricted test content, hidden tests, private fixtures, verifier payloads, or validation data whose upstream license or authorization model forbids redistribution by the platform.

For sources such as DeepSWE, Terminal-Bench/Terminal2, and SWE-bench Pro, Workbench resolves validation by directly accessing the official or otherwise authorized case source using the platform-provided `source_id + external_id` identity and any public locator fields. Missing `validation.command` or setup/build fields in the platform COG Case payload is not a producer failure for these restricted-source cases.

The optional `validation` object remains valid for source kinds where the producer is authorized to publish validation information, such as local, public, or custom cases. When present and authorized, consumers may preserve these fields:

- `validation.backend`
- `validation.command`
- `validation.setup_command`
- `validation.setup_commands`
- `validation.host_command`
- `validation.docker_image`
- `validation.timeout_seconds`
- `validation.backend_config`

Consumers resolve validation configuration in this order:

1. Workbench source hydrator for recognized source families, using `source_id + external_id` and public source locator fields.
2. Cached prepared-case source hydration when the cache revision and source identity still match.
3. Explicit public `validation` fields in the COG Case payload, only for source kinds allowed to publish them.
4. Workbench local validation policy for local/custom cases.
5. Workspace/language fallback for generic local cases.

Language fallback is diagnostic fallback only. It must not hide missing source hydration for supported external case sources that require official or authorized validation material.

## Failure Behavior

- Platform not configured: Workbench returns local smoke/mini case data where available and marks `platform_configured: false`.
- Platform unavailable: Workbench returns a 502-style local API error for the COG Cases request.
- Invalid known-version COG Case payload: Workbench treats the platform response as invalid and fails the local request rather than guessing required identity fields.
- Missing detail fields: Workbench may fetch public test-case detail and merge missing values, but must preserve the original COG Case identity.
- Missing restricted validation fields: not a platform producer error for restricted-source cases; Workbench reports source hydration errors such as source unavailable, unauthorized, or missing validation.

## Required Tests

Producer tests in the Website repository:

- Public COG Case list returns only published COG Cases and validates `cogeval.cog_case.v1` or `cogeval.cog_case.v2`.
- COG Case v2 payloads declare `environment_requirements` only with contract resource ids such as `docker_engine` and `go_toolchain`.
- Public COG Case group list/detail returns only public published groups and validates `cogeval.cog_case_group.v1`.
- Public COG Case payloads do not leak restricted hidden tests, private fixtures, verifier payloads, or validation data from sources whose license or authorization model forbids platform redistribution.
- Published COG Case detail may include `validation` only for source kinds where the producer is authorized to publish those fields.

Consumer tests in the Workbench repository:

- `GET /api/cog-cases` accepts the platform page object shape.
- `GET /api/cog-cases` preserves `source_id + external_id`.
- `GET /api/cog-cases` projects COG Case v2 `environment_requirements` into local `environment_status`.
- Workspace preparation uses platform COG Case identity and local registry matching.
- Workbench source hydration resolves validation directly from supported case sources for DeepSWE, Terminal-Bench/Terminal2, and SWE-bench Pro.
- Workspace preparation persists hydrated validation metadata in the prepared case without requiring restricted validation fields from the platform payload.
- Scheduler-backed run sessions preserve hydrated validation fields in task context and run sidecars.
