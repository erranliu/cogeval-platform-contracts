# Provider Interface Catalog v1

`cogeval.provider_interface_catalog.v1` is the provider-facing contract for API
key provider catalogs shared by the COGEval platform and Workbench.

The platform owns provider facts:

- provider identity, display text, status, and documentation URLs
- provider models, canonical model IDs, and provider invocation model names
- supported interface IDs such as `openai_compatible_chat`
- default base URLs and model prefixes
- interface alias canonicalization and schema compatibility

Workbench owns runtime binding:

- which local executor can consume an interface
- environment variable injection
- preflight and live probe execution
- legacy execution profile metadata

## Schema Compatibility

The only accepted schema for this contract is
`cogeval.provider_interface_catalog.v1`. Catalog payloads using the legacy
`cogeval.api_key_provider_catalog.v1` schema are not valid provider interface
catalogs.

Legacy interface IDs may remain as alias helpers for canonical interface IDs,
but the legacy catalog schema is not accepted.

The SDK projection used by execution-config remains
`cogeval.execution_config.provider_catalog.v1` and keeps `supported_adapters`
vocabulary for its public API.

## Producer Guidance

Platform producers should publish provider, model, and interface facts only.
They must not publish Workbench executor IDs, local CLI/native binding behavior,
or `_native` interface IDs.

Provider model entries use two model identifiers:

- `model_id` is the canonical COGEval model identifier. Official provider
  entries must use a `model_id` selected from the Provider Capability Catalog so
  the same model has the same identity across providers.
- `model_name` is the provider-specific invocation name sent to the provider
  API. It may differ from `model_id` when a provider aliases, routes, or versions
  a canonical model under a different request name.

For example, an official provider may expose canonical `model_id`
`deepseek-v4-flash` while requiring `model_name` `deepseek-chat` in the provider
request payload.

Before publishing, validate payloads with:

```python
from cogeval_platform_contracts.provider_interfaces import validate_provider_interface_catalog

validate_provider_interface_catalog(payload)
```

