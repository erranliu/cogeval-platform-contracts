# COGEval Platform Contracts

Shared, versioned contracts between the COGEval platform and Workbench.

This repository is the canonical source for cross-project payload schemas. Producer
services validate payloads before publishing them. Consumer services validate
payloads before relying on them.

## Contract Rules

- Schemas are the contract truth. Documentation explains the schema but does not
  replace it.
- Payloads must include a `schema` field.
- Additive fields are compatible only when consumers are required to ignore
  unknown future fields. Otherwise, create a new schema version.
- Enum changes require explicit compatibility review.
- Fixtures are part of the contract. Producer and consumer CI should both run
  them.

## Current Contracts

- `cogeval.provider_capability_catalog.v1`

## Repository Layout

```text
src/cogeval_platform_contracts/
  provider_capabilities/
    v1.py
    schemas/
    fixtures/
tests/
docs/
```

Start with [Adding A Contract](docs/ADDING_A_CONTRACT.md) when introducing a
new boundary. See [Compatibility Policy](docs/COMPATIBILITY_POLICY.md) for
versioning rules.

## Development

```powershell
python -m pip install -e .[test]
python -m pytest
```
