# Workbench Provider Capability Catalog v1

Data schema: `cogeval.provider_capability_catalog.v1`

Producer: COGEval Website or another platform capability source

Consumer: COGEval Workbench execution selection catalog

## Purpose

This optional integration provides provider/model/interface capability details that are separate from provider interface availability. Workbench uses it to project runtime controls such as thinking effort when a provider interface catalog alone is not enough.

`cogeval.model_capability_catalog.v2` is the preferred source for canonical model-owned capability facts. This v1 provider capability integration remains for provider-specific compatibility and rollout paths.

## Producer API

- Default Website public route: none currently required by this integration.
- Optional platform path: operators may configure a path such as `/api/workbench/v1/provider-capabilities`.
- Bundled response: `GET /api/workbench/v1/api-key-providers` may include a `capability_catalog` field containing `cogeval.provider_capability_catalog.v1`.
- Authentication: if served from a Workbench platform API, use the same optional Bearer token policy as the provider catalog.
- Response shape: either the catalog itself or a wrapper with `catalog`.

## Consumer Loader

- Config override: Workbench local config may set `platform.provider_capability_catalog_path`.
- Loader implementation: `src/cogeval/api_keys/provider_catalog.py` in the Workbench repository.
- Validation: Workbench validates with `cogeval_platform_contracts.provider_capabilities.ProviderCapabilityCatalog`.
- Projection: Workbench merges accepted provider capabilities into the provider catalog used by execution selection.

## Data Flow

```text
Provider capability source
  -> bundled capability_catalog or configured provider_capability_catalog_path
  -> Workbench api_key_provider_catalog_payload()
  -> provider_catalog_for_selection()
  -> execution selection compatibility and row capabilities
```

## Failure Behavior

- Missing path and no bundled payload: Workbench proceeds without provider capability augmentation.
- Unauthorized, unavailable, timeout, or invalid schema: Workbench records `capability_error` and does not use the capability catalog.
- Workbench must not invent provider capability values when this catalog is unavailable.

## Required Tests

Consumer tests in the Workbench repository:

- Bundled `capability_catalog` is validated and projected.
- Invalid provider capability payloads report structured errors.
- Execution selection row capabilities use provider/interface/model capabilities only after validation.

