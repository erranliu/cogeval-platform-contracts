# Compatibility Policy

Contracts in this repository are public boundaries between COGEval services.
They are not implementation DTOs.

## Versioning

Every payload includes a `schema` string:

```json
{ "schema": "cogeval.provider_capability_catalog.v1" }
```

The schema string is the runtime version selector. Package versions describe
distribution releases; schema versions describe payload compatibility.

## Compatible Changes

Compatible changes may keep the same schema version:

- Adding a provider, model, or capability.
- Adding optional metadata that consumers may ignore.
- Adding fixtures that document already-supported behavior.
- Relaxing validation without changing existing semantics.

## Breaking Changes

Breaking changes require a new schema version:

- Removing a required field.
- Renaming a field.
- Changing field meaning.
- Removing a provider, model, capability, or supported capability value.
- Tightening validation so previously valid payloads fail.

Enum value additions are reviewed case by case. They are often breaking for
strict consumers even when the field itself is optional.

## CI Expectations

This repository runs contract tests for schema, fixtures, and compatibility
helpers. Producer and consumer repositories should run these same fixtures in
their own CI.

