# Producer And Consumer CI

This package should be used by both sides of a cross-project contract.

## Producer CI

Platform producer CI should:

1. Install this package at the agreed version.
2. Generate or load representative payloads.
3. Validate payloads with the Pydantic model.
4. Validate payloads against the JSON Schema.
5. Run compatibility checks against the latest published fixture set.

## Consumer CI

Workbench consumer CI should:

1. Install this package at the agreed version.
2. Validate all bundled fixtures.
3. Parse fixtures into internal models.
4. Assert consumer-facing behavior for each fixture.
5. Add a fixture or compatibility test before requesting producer changes.

## Release Gate

A contract change is ready to publish only when:

- The schema version is correct for the compatibility impact.
- Fixtures cover new behavior.
- Compatibility tests explain breaking or additive changes.
- Producer and consumer owners have reviewed the fixture impact.

