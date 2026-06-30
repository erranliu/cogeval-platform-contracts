# Workbench Model Capability Catalog v2

Data schema: `cogeval.model_capability_catalog.v2`

Producer: COGEval Website Workbench API

Consumer: COGEval Workbench execution selection catalog

## Purpose

This integration provides canonical model capability facts from the platform to Workbench. Workbench uses it to build execution selections for COG Cases and other local runs, including Codex CLI and Claude Code CLI built-in account model support.

The schema defines valid model capability data. This integration defines how Workbench obtains that data from the platform and which fields must survive the public API boundary.

## Producer API

- Method and path: `GET /api/workbench/v1/model-capabilities`
- Authentication: optional Bearer token. If the platform config requires catalog access, the same token policy as other Workbench catalog APIs applies.
- Response shape: the response body is the `cogeval.model_capability_catalog.v2` catalog itself, not an outer wrapper.
- Required integration fields: `schema`, `updated_at`, `interfaces`, `models`, and `built_in_account_capabilities`.
- `built_in_account_capabilities` must be returned by the public API. It is not enough for this field to exist only in draft storage, active DB rows, admin API payloads, or ops-console state.
- Public `built_in_account_capabilities[]` rows should include `native_interface`, `provider_interface`, and `binding_policy`. Omitted or `null` interface fields are filled by the contract defaults, but producers should emit explicit values at the API boundary.

## Consumer Loader

- Default platform path: `/api/workbench/v1/model-capabilities`
- Config override: Workbench local config may set `platform.model_capability_catalog_path`.
- Base URL: Workbench uses `platform_base_url`, `COG_EVAL_PLATFORM_BASE_URL`, `COGEVAL_PLATFORM_BASE_URL`, or `platform.base_url` from local config.
- Loader implementation: `src/cogeval/api_keys/provider_catalog.py` in the Workbench repository.
- Validation: Workbench validates the payload with `cogeval_platform_contracts.model_capabilities.validate_model_capability_catalog_v2`.
- Bundled payload: if `GET /api/workbench/v1/api-key-providers` returns a `model_capability_catalog` field, Workbench may consume that bundled payload instead of making the separate request.

## Data Flow

```text
Website active model capability catalog
  -> GET /api/workbench/v1/model-capabilities
  -> Workbench api_key_provider_catalog_payload()
  -> provider_catalog_payload["model_capability_catalog"]
  -> COGEvalCatalogProvider.catalog()
  -> built-in account ModelSourceRef rows
  -> GET /api/execution-selection/catalog
  -> COG Cases Agent / Source / Model selectors
```

For Codex CLI built-in account support, Workbench reads the `built_in_account_capabilities` row where `agent_id == "codex_cli"` and creates `builtin:codex_cli_account` only from the listed `model_ids`.

Workbench must use the row binding metadata to distinguish built-in account native execution from API-key provider execution. Current contract defaults are:

```text
codex_cli -> native_interface=codex_native, provider_interface=openai_responses, binding_policy=builtin_account_native
claude_code_cli -> native_interface=claude_code_native, provider_interface=anthropic_compatible_messages, binding_policy=builtin_account_native
```

Workbench must not infer Codex CLI built-in account model support from local CLI model probes or from all `models[]` in the catalog when `built_in_account_capabilities` is absent.

## Failure Behavior

- Platform not configured: Workbench reports provider catalog unconfigured and does not derive platform model capability facts.
- Unauthorized: Workbench records a `model_capability_catalog_unauthorized` error and does not use the model capability catalog.
- Unavailable or timeout: Workbench records a model capability catalog error and does not guess built-in account model support.
- Invalid schema: Workbench records `model_capability_catalog_invalid_payload`; v1 payloads are not accepted for this integration.
- Missing `built_in_account_capabilities`: Workbench treats built-in account model support as undeclared. It may still show local agent login/runtime status, but must not generate Codex built-in account model options from the full model list.

## Required Tests

Producer tests in the Website repository:

- `services/backend/tests/test_workbench_api.py::test_model_capability_catalog_returns_v2_public_contract`
- The test must assert that `GET /api/workbench/v1/model-capabilities` returns `built_in_account_capabilities`.

Consumer tests in the Workbench repository:

- `tests/workbench/test_api_key_provider_catalog.py::test_api_key_provider_catalog_payload_accepts_model_capability_v2`
- `tests/workbench/test_api_key_provider_catalog.py::test_api_key_provider_catalog_payload_fetches_model_capability_catalog_path`
- `tests/workbench/test_execution_selection_api.py::test_execution_selection_catalog_uses_platform_model_capability_v2_for_codex_builtin_account`
- `tests/workbench/test_execution_selection_api.py::test_execution_selection_catalog_requires_builtin_account_assignments_for_codex_models`

## Minimal Payload

```json
{
  "schema": "cogeval.model_capability_catalog.v2",
  "updated_at": "2026-06-29T00:00:00Z",
  "interfaces": {
    "openai_responses": {
      "thinking_effort": {
        "surface": "thinking_effort",
        "path": "reasoning.effort",
        "vocabulary": [
          { "id": "default", "wire_value": null },
          { "id": "high", "wire_value": "high" }
        ]
      }
    }
  },
  "models": [
    {
      "model_id": "gpt-5.5",
      "display_name": "GPT-5.5",
      "thinking_effort": {
        "values": [{ "id": "default" }, { "id": "high" }],
        "default": "default"
      },
      "interface_capabilities": {
        "openai_responses": {
          "thinking_effort": {
            "mapping": {
              "default": "default",
              "high": "high"
            },
            "parameter_surface": "thinking_effort"
          }
        }
      }
    }
  ],
  "built_in_account_capabilities": [
    {
      "agent_id": "codex_cli",
      "display_name": "Codex CLI",
      "model_ids": ["gpt-5.5"],
      "native_interface": "codex_native",
      "provider_interface": "openai_responses",
      "binding_policy": "builtin_account_native"
    },
    {
      "agent_id": "claude_code_cli",
      "display_name": "Claude Code CLI",
      "model_ids": [],
      "native_interface": "claude_code_native",
      "provider_interface": "anthropic_compatible_messages",
      "binding_policy": "builtin_account_native"
    }
  ]
}
```

