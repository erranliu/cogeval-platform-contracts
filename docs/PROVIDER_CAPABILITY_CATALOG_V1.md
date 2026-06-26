# Provider Capability Catalog v1

Schema: `cogeval.provider_capability_catalog.v1`

This contract describes provider, interface, model, and model-level runtime
capabilities. It is intended for platform producers and Workbench consumers.

## Shape

```text
ProviderCapabilityCatalog
  providers[]
    provider_id
    interfaces[]
      interface
    models[]
      model_id
      model_name
      capabilities
      interface_capabilities
```

## Thinking Effort

`thinking_effort` is modeled as a capability because support depends on the
provider, interface, and model. Every model that declares thinking-effort
support must have a model-level declaration at
`models[].capabilities.thinking_effort`. Interface-specific declarations at
`models[].interface_capabilities[interface].thinking_effort` may be used
together with the model-level declaration when a provider interface is selected.

The model-level declaration is model-facing: it declares which platform values
the model supports and gives those values model-facing labels. The interface
declaration is interface-facing: it declares which of the model-supported
platform values are usable through that interface, and how those platform values
map to interface/provider-native parameter values.

Provider Interface Catalog entries must reference the same canonical `model_id`
for official provider models. Provider-specific request names live in the
Provider Interface Catalog `model_name` field and may differ from this canonical
model ID.

Thinking-effort configuration uses three vocabularies:

- Platform values are the canonical values in `Capability.values`. Workbench and
  platform result records use these values for selection, compatibility
  intersection, requests, and result dimensions. Interface capability values
  must be a subset of the model-level capability values.
- Interface values are provider/interface-native parameter values defined by
  the contract's built-in interface registry. They are not catalog
  configuration. Runtime adapters use the same registry when materializing the
  selected platform value onto a provider interface.
- Model value labels are model-facing names declared by the model-level
  `Capability.model_value_labels`. They are descriptive labels for users and
  result grouping; they do not affect runtime materialization. Interface
  capability declarations must not carry `model_value_labels`.

The platform values are:

```text
default | minimal | low | medium | high | xhigh | max
```

`default` means omit the thinking-effort parameter and let the provider,
interface, model, or agent default apply. The platform does not expose disabling
values such as `off` or `none`, and it does not expose `adaptive`.

Built-in interface surfaces for thinking effort:

| Interface | Surface | Parameter path | Interface values |
| --- | --- | --- | --- |
| `openai_responses` | `thinking_effort` | `reasoning.effort` | `minimal`, `low`, `medium`, `high`, `xhigh` |
| `anthropic_messages` | `thinking_effort` | `output_config.effort` | `low`, `medium`, `high`, `xhigh`, `max` |
| `anthropic_compatible_messages` | `thinking_effort` | `output_config.effort` | `low`, `medium`, `high`, `xhigh`, `max` |
| `gemini_interactions` | `thinking_effort` | `generation_config.thinking_level` | `minimal`, `low`, `medium`, `high` |
| `openai_compatible_chat` | `thinking_effort` | `reasoning_effort` | `high`, `max` |

These values are contract code, not catalog data. Changing them requires a
contract change and corresponding Workbench adapter support.

Example:

```json
{
  "capabilities": {
    "thinking_effort": {
      "supported": true,
      "values": ["default", "high", "max"],
      "default": "default",
      "model_value_labels": {
        "default": "Model default",
        "high": "Reasoning high",
        "max": "Reasoning max"
      }
    }
  },
  "interface_capabilities": {
    "openai_compatible_chat": {
      "thinking_effort": {
        "supported": true,
        "values": ["default", "high", "max"],
        "default": "default",
        "parameter_surface": "thinking_effort",
        "adapter_policy": "map_values",
        "value_mapping": {
          "high": "high",
          "max": "max"
        }
      }
    }
  }
}
```

`parameter_surface` references a built-in surface for the selected interface.
For example, the contract registry defines `openai_responses` /
`thinking_effort` as `reasoning.effort`, `gemini_interactions` /
`thinking_effort` as `generation_config.thinking_level`, and
`openai_compatible_chat` / `thinking_effort` as `reasoning_effort`. If a
provider's documentation maps several vocabulary words to the same behavior,
the catalog should expose only the platform values that are meaningful for the
model and use `value_mapping` to select one of the built-in interface values.
The catalog must not define new interface vocabulary values.
Interface `thinking_effort.value_mapping` targets must be strings from that
built-in vocabulary. `default` must not have a mapping because it means omitting
the provider parameter.

`model_value_labels` maps enabled model-level platform values to model-facing
names. These labels are not provider parameters. `default` may have a model
label but should not have a `value_mapping` entry because it means omitting the
provider parameter.

Native model sources that do not use a provider interface use the model-level
declaration directly. In that case, `models[].capabilities.thinking_effort`
still carries the platform values and model labels, and may carry native
`value_mapping` entries when the native model vocabulary differs from platform
values.

Workbench must still intersect provider/model/interface capabilities with its
own agent-adapter capabilities. Provider capability labels and value mappings
come from this catalog; how a selected value is materialized in an agent CLI,
environment variable, config file, or native API is Workbench behavior.

## Adapter Policies

- `pass_through`: send selected values directly.
- `map_values`: translate canonical values before sending.
- `unsupported`: do not expose the control.
- `drop_with_warning`: accept consumer payloads for compatibility, but warn and
  omit the provider parameter.

## Fixtures

Fixtures are contract examples and regression cases:

- `minimal.v1`
- `openai_reasoning.v1`
- `anthropic_effort.v1`
- `gemini_thinking.v1`
- `deepseek_reasoning.v1`
- `unknown_provider.v1`
