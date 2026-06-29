# Model Capability Catalog v1

Schema: `cogeval.model_capability_catalog.v1`

This contract describes canonical COGEval model identities and model-global
runtime capabilities. It is provider-free: provider availability is derived
from API Key Provider Catalog rows that reference the same `model_id`.

## Shape

```text
ModelCapabilityCatalog
  models[]
    model_id
    display_name
    status
    recommended
    capability_tags
    thinking_effort
```

## Boundaries

The Model Capability Catalog owns:

- canonical `model_id`
- user-facing model `display_name`
- model-global capability tags
- model-global `thinking_effort` platform values, default, and labels

It must not carry `provider_id`, provider API-key details, provider request
model names, base URLs, environment variable names, or Workbench executor
bindings.

Provider-specific model availability and invocation names belong to provider
configuration. Interface parameter paths and vocabularies belong to the
Interface Capability Catalog and Workbench adapter contract.
