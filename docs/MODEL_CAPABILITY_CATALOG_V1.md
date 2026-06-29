# Model Capability Catalog v1

Schema: `cogeval.model_capability_catalog.v1`

This contract describes canonical COGEval model identities and model-global
runtime capabilities. It is provider-free: provider availability is derived
from API Key Provider Catalog rows that reference the same `model_id`.

## Shape

```text
ModelCapabilityCatalog
  interfaces{}
    <interface_id>
      thinking_effort
        surface
        path
        platform_values[]
        value_mapping{}
  models[]
    model_id
    display_name
    status
    recommended
    capability_tags
    thinking_effort
    interface_capabilities{}
      <interface_id>
        thinking_effort
          values[]
          parameter_surface
          adapter_policy
  built_in_account_capabilities[]
    agent_id
    display_name
    model_ids[]
```

## Boundaries

The Model Capability Catalog owns:

- canonical `model_id`
- user-facing model `display_name`
- model-global capability tags
- model-global `thinking_effort` platform values, default, and labels
- model-to-interface capability projections for built-in interface ids
- built-in interface parameter paths and value mappings for model-global
  capabilities
- built-in agent account model support lists for `codex_cli` and
  `claude_code_cli`

It must not carry `provider_id`, provider API-key details, provider request
model names, base URLs, environment variable names, or Workbench executor
bindings.

Provider-specific model availability and invocation names belong to provider
configuration. Interface availability by provider belongs to the Interface
Capability Catalog and provider configuration.

## Built-In Accounts

`built_in_account_capabilities` declares which canonical models are available
through a platform-managed agent account. Each row is keyed by `agent_id`.

Current built-in account ids:

- `codex_cli`
- `claude_code_cli`

Every `model_ids[]` value must reference a `models[].model_id` in the same
catalog. Duplicate `agent_id` values are invalid.

## Interface Capabilities

`models[].interface_capabilities` projects a model-global capability onto a
built-in provider interface. Interface capability values must be declared by
the model-level `thinking_effort.values` and supported by the target
`interfaces.<interface_id>.thinking_effort.platform_values`.
