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
```

## Thinking Effort

`thinking_effort` is modeled as a capability because support depends on the
provider, interface, and model.

Example:

```json
{
  "capabilities": {
    "thinking_effort": {
      "supported": true,
      "values": ["minimal", "low", "medium", "high"],
      "default": "medium",
      "parameter_surface": "thinking_effort",
      "adapter_policy": "pass_through"
    }
  }
}
```

`parameter_surface` references a provider interface entry that says how the
adapter should pass the value, such as `reasoning.effort`,
`generation_config.thinking_level`, or `reasoning_effort`.

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

