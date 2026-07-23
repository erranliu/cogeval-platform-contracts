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

- `cogeval.cog_case.v3` (current published COG Case contract)
- `cogeval.cog_case_group.v1`
- `cogeval.distribution_claim.v1`
- `cogeval.distribution_claim_request.v1`
- `cogeval.evidence_bundle.v1`
- `cogeval.gateway_consistency.baseline.v1`
- `cogeval.gateway_consistency.task_pack.v1`
- `cogeval.package_import_result.v1`
- `cogeval.model_capability_catalog.v1`
- `cogeval.provider_capability_catalog.v1`
- `cogeval.interface_capability_catalog.v1`
- `cogeval.self_run_package_manifest.v1`
- `cogeval.self_run_record.v1`
- `cogeval.workbench.account_assets.v1`
- `cogeval.workbench.auth_github_request.v1`
- `cogeval.workbench.auth_github_response.v1`
- `cogeval.workbench.coin_reservation.v1`

## Repository Layout

```text
src/cogeval_platform_contracts/
  cog_cases/
    schemas/
    fixtures/
  distribution_claims/
    v1.py
    schemas/
    fixtures/
  gateway_consistency/
    v1.py
    schemas/
    fixtures/
  model_capabilities/
    v1.py
    schemas/
    fixtures/
  provider_capabilities/
    v1.py
    schemas/
    fixtures/
  provider_interfaces/
    v1.py
    schemas/
    fixtures/
  self_run_packages/
    v1.py
    schemas/
    fixtures/
  workbench_accounts/
    v1.py
    schemas/
    fixtures/
tests/
docs/
```

Start with [Adding A Contract](docs/ADDING_A_CONTRACT.md) when introducing a
new boundary. See [Compatibility Policy](docs/COMPATIBILITY_POLICY.md) for
versioning rules.

For the Chinese contract index, see [契约.md](docs/契约.md).

## Development

```powershell
python -m pip install -e .[test]
python -m pytest
```
