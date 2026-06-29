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
        display_name?
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
interface surface. There is no v2 `model_value_labels` field; model display
text lives on each `values[]` item as `display_name`.

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

Built-in accounts may reuse existing interface mappings operationally:

```text
codex_cli -> openai_responses
claude_code_cli -> anthropic_compatible_messages
```

Future contracts may add first-class built-in interface ids if native execution
surfaces diverge from those mappings.
