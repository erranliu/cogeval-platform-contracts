# Model Capability Catalog v2

Schema: `cogeval.model_capability_catalog.v2`

This contract describes canonical COGEval model identities and model-owned
runtime capabilities. It replaces the v1 global thinking-effort platform
vocabulary with model-owned effort ids and interface-owned vocabulary ids.

## Shape

```text
ModelCapabilityCatalogV2
  interfaces{}
    <interface_id>
      thinking_effort
        surface
        path
        vocabulary[]
          id
          wire_value
          display_name?
  models[]
    model_id
    display_name
    status
    recommended
    capability_tags
    thinking_effort
      values[]
        id
      default?
    interface_capabilities{}
      <interface_id>
        thinking_effort
          mapping{}
            <model_effort_id>: <interface_vocab_id>
          parameter_surface
          adapter_policy
  built_in_account_capabilities[]
    agent_id
    display_name
    model_ids[]
    native_interface?
    provider_interface?
    binding_policy
```

## Boundaries

The Model Capability Catalog owns:

- canonical `model_id`
- user-facing model `display_name`
- model-global capability tags
- model-owned `thinking_effort.values[].id`
- interface-owned thinking-effort vocabulary ids and wire values
- model-to-interface thinking-effort mappings
- built-in agent account model support lists for `codex_cli` and
  `claude_code_cli`
- built-in agent account binding metadata that identifies native execution
  surfaces and the provider interface mapping they reuse

It must not carry `provider_id`, provider API-key details, provider request
model names, base URLs, environment variable names, or Workbench executor
bindings.

Provider-specific model availability and invocation names belong to provider
configuration. Provider interface availability belongs to the Interface
Capability Catalog and provider configuration.

## Thinking Effort

`models[].thinking_effort.values[].id` is the stable model-owned selection and
result key. It is the value that downstream systems should store in
`TestResult.thinking_effort`, distribution candidate configs, and analysis
filters.

`interfaces.<interface_id>.thinking_effort.vocabulary[].id` is the stable
interface-owned vocabulary key. `wire_value` is the actual request payload
value. `wire_value: null` means omitting the interface parameter.

Request payload resolution is:

```text
model_id + model_effort_id -> interface_id + interface_vocab_id -> wire_value
```

There is no v2 `platform_values` field and no v2 `value_mapping` field on the
interface surface. There is no v2 `model_value_labels` field and no model
thinking-effort `display_name`; the model-owned effort `id` is also the
user-facing display name.

## Interface Capabilities

`models[].interface_capabilities` declares whether a model is available through
an interface. If a model does not declare a given `interface_id`, the model is
not available on that interface.

For a declared interface, the `thinking_effort.mapping` object maps model-owned
effort ids to interface-owned vocabulary ids. Missing model effort ids are not
available on that interface.

Rules:

- mapping keys must be declared by `models[].thinking_effort.values[].id`
- mapping targets must be declared by the selected interface vocabulary
- mapping targets must be unique for a model/interface capability
- `parameter_surface` must be `thinking_effort`
- `adapter_policy` is currently `map_values`

## Built-In Accounts

`built_in_account_capabilities` declares which canonical models are available
through a platform-managed agent account. Each row is keyed by `agent_id`.

Current built-in account ids:

- `codex_cli`
- `claude_code_cli`

Every `model_ids[]` value must reference a `models[].model_id` in the same
catalog. Duplicate `agent_id` values are invalid.

Built-in account rows also carry binding metadata:

- `native_interface`: `codex_native`, `claude_code_native`, or `null` for the
  contract default
- `provider_interface`: `openai_responses`,
  `anthropic_compatible_messages`, or `null` for the contract default
- `binding_policy`: `builtin_account_native` or `reuse_provider_interface`;
  defaults to `builtin_account_native`

Defaults and validation:

```text
codex_cli -> native_interface=codex_native, provider_interface=openai_responses
claude_code_cli -> native_interface=claude_code_native, provider_interface=anthropic_compatible_messages
```

`codex_cli` must not declare a provider interface other than
`openai_responses`, and `claude_code_cli` must not declare a provider interface
other than `anthropic_compatible_messages`. `native_interface` must match the
declared `agent_id`.
