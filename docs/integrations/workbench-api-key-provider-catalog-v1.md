# Workbench API Key Provider Catalog v1

Data schema: `cogeval.interface_capability_catalog.v1`

Producer: COGEval Website Workbench API

Consumer: COGEval Workbench API key config and execution selection catalog

## Purpose

This integration provides platform-owned provider, model, and interface facts to Workbench. Workbench uses the catalog to create platform-backed API key configs and to build execution selections for API-key model sources.

The platform response uses the interface capability catalog schema. Workbench projects it into its internal API-key provider catalog facade for existing UI and execution-config code.

## Producer API

- Method and path: `GET /api/workbench/v1/api-key-providers`
- Authentication: optional Bearer token controlled by platform catalog access settings.
- Response shape: the response body is `cogeval.interface_capability_catalog.v1`.
- Required fields: `schema`, `updated_at`, `providers[]`, `providers[].supported_interfaces[]`, and `providers[].models[]`.
- Provider entries must not publish Workbench executor IDs or local CLI binding behavior.
- Built-in account native execution bindings do not belong in this provider API-key catalog. They are declared by `cogeval.model_capability_catalog.v2` `built_in_account_capabilities[]` rows with `native_interface`, `provider_interface`, and `binding_policy`.

## Consumer Loader

- Default platform path: `/api/workbench/v1/api-key-providers`
- Config override: Workbench local config may set `platform.api_key_provider_catalog_path`.
- Loader implementation: `src/cogeval/api_keys/provider_catalog.py` in the Workbench repository.
- Validation: Workbench validates with `cogeval_platform_contracts.provider_interfaces.validate_provider_interface_catalog`.
- Projection: Workbench rewrites the accepted payload to the local `cogeval.api_key_provider_catalog.v1` facade for API key config UI and execution selection.

## Data Flow

```text
Website provider interface catalog
  -> GET /api/workbench/v1/api-key-providers
  -> Workbench api_key_provider_catalog_payload()
  -> API key config expansion / execution selection catalog
  -> COG Cases and Executors model-source selectors
```

The same platform response may bundle `capability_catalog` and `model_capability_catalog`. If bundled, Workbench validates and consumes those sub-payloads according to their integration contracts. Bundled model capability catalogs remain the source of truth for built-in account binding metadata; API-key provider rows must not duplicate or override it.

## Failure Behavior

- Platform not configured: Workbench reports `platform_not_configured` and does not create platform provider sources.
- Unauthorized: Workbench reports `catalog_unauthorized`.
- Unavailable or timeout: Workbench reports `catalog_unavailable` or `catalog_timeout`.
- Invalid schema: Workbench reports `catalog_invalid_payload`.
- Unknown provider interface IDs are invalid.

## Required Tests

Producer tests in the Website repository:

- `GET /api/workbench/v1/api-key-providers` returns `cogeval.interface_capability_catalog.v1`.
- Public provider payloads do not expose secrets, env var values, or Workbench executor IDs.

Consumer tests in the Workbench repository:

- `tests/workbench/test_api_key_provider_catalog.py` validates accepted platform payloads.
- Execution selection tests cover platform provider API key configs and compatible rows.

