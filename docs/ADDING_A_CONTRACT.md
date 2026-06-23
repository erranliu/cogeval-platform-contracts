# Adding A Contract

Use this checklist for every new cross-project contract. The goal is to make
each contract independently understandable, testable, and versioned.

## Required Files

For a contract named `example_contract.v1`, add:

```text
src/cogeval_platform_contracts/<domain>/
  __init__.py
  v1.py
  schemas/example_contract.v1.schema.json
  fixtures/minimal.v1.json
  fixtures/<realistic-case>.v1.json
tests/
  test_<domain>_v1.py
  test_<domain>_json_schema.py
docs/
  <DOMAIN>_V1.md
```

## Required Tests

- Pydantic model accepts every valid fixture.
- JSON Schema validates itself.
- JSON Schema validates every valid fixture.
- Invalid shapes fail for the intended reason.
- Compatibility helper flags known breaking changes when the contract is
  intended to evolve in place.

## Compatibility Rules

- Keep the same `schema` value only for compatible changes.
- Create a new version for breaking changes.
- New optional fields are compatible only when consumers must ignore unknown
  fields.
- Enum value additions require explicit review because old consumers may reject
  unknown values.
- Removing providers, models, capabilities, or supported values is breaking for
  capability catalogs.

## Producer And Consumer Duties

Producers:

- Depend on this package.
- Validate payloads before publishing.
- Add or update fixtures for changed behavior.

Consumers:

- Depend on this package.
- Validate payloads before relying on them.
- Add consumer-driven fixtures or compatibility tests before asking producers to
  change payloads.

