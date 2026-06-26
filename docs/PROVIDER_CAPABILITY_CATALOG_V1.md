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
      parameter_surfaces
    models[]
      model_id
      model_name
      capabilities
      interface_capabilities
```

## Thinking Effort

`thinking_effort` is modeled as a capability because support depends on the
provider, interface, and model. Consumers should prefer
`models[].interface_capabilities[interface].thinking_effort` when present;
`models[].capabilities.thinking_effort` is retained for consumers that do not
yet select by interface.

The platform values are:

```text
default | minimal | low | medium | high | xhigh | max
```

`default` means omit the thinking-effort parameter and let the provider,
interface, model, or agent default apply. The platform does not expose disabling
values such as `off` or `none`, and it does not expose `adaptive`.

Example:

```json
{
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

`parameter_surface` references a provider interface entry that says how the
adapter should pass the value, such as `reasoning.effort`,
`generation_config.thinking_level`, or `reasoning_effort`. If a provider's
documentation maps several vocabulary words to the same behavior, the catalog
should expose only the platform values that are meaningful for the model and use
`value_mapping` for the actual provider value.

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
