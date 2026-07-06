# COG Cases v2

COG Case v2 extends `cogeval.cog_case.v1` with explicit case environment requirements. It is the platform-to-Workbench contract for cases that need host or container tools before candidate execution or official validation can run.

## Schemas

| schema | Description | Model |
|---|---|---|
| `cogeval.cog_case.v2` | Single COG Case with environment requirements | `CogCaseV2` |

Machine-readable files:

- `src/cogeval_platform_contracts/cog_cases/v2.py`
- `src/cogeval_platform_contracts/cog_cases/schemas/cog_case.v2.schema.json`
- `src/cogeval_platform_contracts/cog_cases/fixtures/case_public.v2.json`

## Environment Requirements

`environment_requirements` is optional and defaults to an empty list. Each item declares a local resource that Workbench must check before run creation or preflight.

Allowed `id` values:

- `docker_engine`: Docker Engine / Docker Desktop.
- `go_toolchain`: Go CLI/toolchain.

Allowed `applies_to` values:

- `workspace_prepare`
- `candidate_execution`
- `official_validation`

Workbench owns local status probing, install actions, and UI projection. The platform only declares that the case needs a resource.

## Compatibility

This is a new schema because v1 rejects unknown top-level fields. Producers must emit `schema = "cogeval.cog_case.v2"` when sending `environment_requirements`. Consumers that only support v1 must reject or ignore v2 according to their integration policy, not reinterpret v2 as v1.
