# Workbench COG Cases v1

Data schemas: `cogeval.cog_case.v1`, `cogeval.cog_case_group.v1`

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
- Case payloads must validate as `cogeval.cog_case.v1`.
- Group payloads must validate as `cogeval.cog_case_group.v1`.

## Consumer Loader

- Workbench local API: `GET /api/cog-cases`
- Platform URL: `${platform_base_url}/api/public/cog-cases`
- Loader implementation: `src/cogeval/workbench/cases_api.py` in the Workbench repository.
- Workbench may fetch `/api/public/test-cases/{test_case_id}` as a detail fallback when a COG Case omits fields needed for local workspace matching.
- Workbench validates COG Case payloads with `cogeval_platform_contracts.cog_cases.v1.validate_cog_case`.

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

## Failure Behavior

- Platform not configured: Workbench returns local smoke/mini case data where available and marks `platform_configured: false`.
- Platform unavailable: Workbench returns a 502-style local API error for the COG Cases request.
- Invalid COG Case payload: Workbench treats the platform response as invalid and fails the local request rather than guessing required identity fields.
- Missing detail fields: Workbench may fetch public test-case detail and merge missing values, but must preserve the original COG Case identity.

## Required Tests

Producer tests in the Website repository:

- Public COG Case list returns only published COG Cases and validates `cogeval.cog_case.v1`.
- Public COG Case group list/detail returns only public published groups and validates `cogeval.cog_case_group.v1`.

Consumer tests in the Workbench repository:

- `GET /api/cog-cases` accepts the platform page object shape.
- `GET /api/cog-cases` preserves `source_id + external_id`.
- Workspace preparation uses platform COG Case identity and local registry matching.

