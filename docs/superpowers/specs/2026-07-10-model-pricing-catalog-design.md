# Model Pricing Catalog v1 Design

Date: 2026-07-10

## Context

COGEval Workbench is adding canonical token-usage recording for the user-selected primary model. A later Workbench step will convert complete token usage into an estimated monetary cost. The platform must therefore publish provider/model pricing through a versioned cross-project contract before the Website and Workbench implementations are built.

The existing catalogs have different responsibilities:

- `cogeval.interface_capability_catalog.v1` declares API-key providers, their models, and supported interfaces;
- `cogeval.model_capability_catalog.v2` declares model-owned capabilities and built-in account bindings;
- neither contract defines pricing.

Pricing changes independently from provider availability and model capabilities. It therefore needs an independent catalog and public endpoint.

## Goals

- Define a current-only API-key provider/model pricing catalog.
- Publish five rates that correspond to Workbench's canonical token dimensions.
- Use unambiguous decimal and missing-price semantics.
- Give COGEval Website a stable contract for draft/validate/publish configuration.
- Give Workbench a stable public loader contract for future cost estimation.
- Keep pricing failures isolated from execution and token recording.

## Non-Goals

- No historical effective periods or historical price reproduction.
- No built-in account pricing for Codex CLI or Claude Code CLI.
- No tiered pricing, context-length bands, discounts, aliases, regional pricing, or multiple currencies.
- No live price polling.
- No Workbench token implementation or cost-calculation implementation in this contract change.
- No Website implementation in the contract repository.

## Architecture Decision

Add a standalone contract:

```text
cogeval.model_pricing_catalog.v1
```

The public producer API is:

```text
GET /api/workbench/v1/model-pricing
```

The response body is the catalog itself, without an outer envelope. Authentication follows the existing optional Workbench catalog-token policy.

Pricing is not added to the provider interface catalog because that would couple price publication to provider configuration publication. It is not added to the model capability catalog because price is provider-specific rather than a global model capability.

## Contract Shape

```json
{
  "schema": "cogeval.model_pricing_catalog.v1",
  "updated_at": "2026-07-10T00:00:00Z",
  "currency": "USD",
  "unit_tokens": 1000000,
  "prices": [
    {
      "provider_id": "anthropic",
      "model_id": "claude-sonnet-4-6",
      "rates": {
        "input_uncached": "3",
        "input_cache_read": "0.3",
        "input_cache_write": "3.75",
        "output": "15",
        "reasoning_output": "15"
      }
    }
  ]
}
```

### Top-Level Fields

- `schema` is the literal `cogeval.model_pricing_catalog.v1`.
- `updated_at` is a UTC RFC 3339 timestamp in the exact form `YYYY-MM-DDTHH:MM:SSZ`. For an active catalog it identifies publication time. For the no-active empty seed it is a stable producer constant that changes only when the seed definition changes; it must not be generated from request time.
- `currency` is the literal `USD`.
- `unit_tokens` is the integer literal `1000000`.
- `prices` is an array and may be empty.

An empty catalog is valid and means no provider/model price is currently configured.

### Price Identity

Each row is identified by the exact pair:

```text
provider_id + model_id
```

Pairs must be unique. IDs are exact contract identifiers from the active API Key Provider Catalog. There is no fuzzy matching, alias matching, case folding, or built-in account mapping in v1.

The JSON Schema validates each row independently. The Pydantic whole-catalog validator is normative for pair uniqueness and rejects duplicate pairs because standard JSON Schema cannot enforce uniqueness by a two-field projection.

The Website producer performs bidirectional cross-catalog validation:

- pricing publication checks every pricing pair against the committed active API Key Provider Catalog immediately before publishing;
- API Key Provider Catalog publication checks the committed active pricing catalog immediately before publishing and rejects removal of a provider/model pair that is still priced.

Adding a new pair is therefore published provider-first, then pricing. Removing a pair is published pricing-first, then provider. No dual-catalog atomic publication API is required. Each publish operation must perform its counterpart validation inside the publication transaction or equivalent serialization boundary. Workbench still ignores any orphan row defensively if external corruption or a legacy state violates this invariant.

### Rate Dimensions

All five rates are required:

- `input_uncached`
- `input_cache_read`
- `input_cache_write`
- `output`
- `reasoning_output`

They map one-to-one to Workbench's canonical token dimensions:

```text
input_uncached_tokens
input_cache_read_tokens
input_cache_write_tokens
output_tokens
reasoning_output_tokens
```

A provider with no charge for a dimension explicitly publishes `"0"`. Missing a row does not mean free; it means pricing is unavailable.

### Decimal Representation

Rates are JSON strings, not JSON numbers. The exact grammar is:

```regex
^(0|[1-9][0-9]{0,11})(\.[0-9]{1,12})?$
```

This permits up to 12 integer digits and up to 12 fractional digits. Trailing fractional zeros are allowed and preserved as publisher-provided representation. Valid examples are:

```text
0
3
0.3
3.75
```

The contract rejects:

- negative values;
- leading `+` signs;
- scientific notation;
- leading-zero forms such as `00` and `01`;
- incomplete decimal forms such as `.5` and `1.`;
- surrounding or embedded whitespace;
- more than 12 integer or 12 fractional digits;
- `NaN` or infinity;
- JSON integer/float values;
- blank strings.

Consumers use decimal arithmetic. They must not round individual dimensions or intermediate products. Display formatting may round only the final presentation value.

## Cost Formula For Consumers

The later Workbench implementation will calculate:

```text
cost_usd =
  input_uncached_tokens   * input_uncached_rate   / unit_tokens
+ input_cache_read_tokens * input_cache_read_rate / unit_tokens
+ input_cache_write_tokens * input_cache_write_rate / unit_tokens
+ output_tokens            * output_rate            / unit_tokens
+ reasoning_output_tokens  * reasoning_output_rate  / unit_tokens
```

Cost is available only when:

- canonical token usage is complete and attributable;
- the selected model source is an API-key provider source;
- an exact `provider_id + model_id` price row exists;
- the complete pricing catalog passed validation.

Built-in account runs and missing rows return pricing unavailable, never zero cost.

The formula assumes the approved Workbench token contract's ordinary output and reasoning output fields are disjoint. Consumers must not treat `reasoning_output_tokens` as a subset already included in `output_tokens`, and consumer tests must prove reasoning tokens are charged exactly once.

## Producer API And Lifecycle

The Website public endpoint returns the active catalog. If no active pricing catalog has been published, it returns a valid empty seed catalog instead of 404 or 503. The empty seed uses a checked-in or code-level `MODEL_PRICING_CATALOG_SEED_UPDATED_AT` constant in the required UTC format. Repeated reads of an unchanged seed return the same `updated_at` value.

Recommended Website administration lifecycle:

```text
Ops Console structured editor
-> save draft
-> validate contract and provider/model references
-> publish
-> one current active catalog
-> public Workbench endpoint
```

Recommended internal admin endpoints:

- `GET /api/admin/model-pricing/active`
- `GET /api/admin/model-pricing/draft`
- `PUT /api/admin/model-pricing/draft`
- `POST /api/admin/model-pricing/validate`
- `POST /api/admin/model-pricing/publish`
- `POST /api/admin/model-pricing/reset-draft`

These internal admin DTOs remain Website implementation details. The cross-project contract governs the public catalog payload stored inside the version record and returned to Workbench.

The Website may keep internal publication history using its existing catalog-version storage pattern, but the v1 public semantics expose only the current active price and do not support effective-date selection or historical recalculation.

Provider and pricing publication ordering is explicit:

```text
add provider/model: publish Provider Catalog -> publish Pricing Catalog
remove provider/model: publish Pricing Catalog without the row -> publish Provider Catalog
```

If the counterpart active catalog changes before a publish transaction commits, validation must be repeated against the committed counterpart state; a stale pre-validation result is not sufficient.

## Ops Console Design Boundary

The Website handoff should implement a structured table editor rather than a JSON-only editor:

- Provider and Model are selected from the current API Key Provider Catalog.
- Five decimal-string rate inputs are shown per row.
- The unit is fixed and displayed as `USD / 1M tokens`.
- Operators can add and delete rows.
- Existing draft save, validate, publish, and reset patterns are reused.
- Provider/model free text is not accepted.
- Historical pricing, bulk import, tiered prices, and built-in account rows are excluded.

## Consumer Loader

Recommended Workbench behavior for the later consumer task:

- Default path: `/api/workbench/v1/model-pricing`.
- Config override: `platform.model_pricing_catalog_path`.
- Use the same platform base URL and optional catalog authorization as existing provider/model catalogs.
- Validate with `cogeval_platform_contracts.model_pricing.validate_model_pricing_catalog`.
- Load with platform catalog configuration; do not live poll.
- Join only API-key model sources by exact `provider_id + model_id`.
- Ignore orphan pricing rows not present in the accepted provider catalog.

Pricing catalog failures affect only monetary estimates. Token counts, execution selection, and run execution remain available.

## Failure Behavior

- No active Website catalog: public API returns a valid empty catalog.
- Empty catalog: Workbench reports price not configured.
- Missing provider/model row: Workbench reports price not configured.
- Built-in account model source: Workbench reports pricing unavailable.
- Unauthorized, timeout, or unavailable API: Workbench reports pricing unavailable and preserves token usage.
- Invalid schema or rate: Workbench rejects the whole catalog; it does not use valid-looking rows from an invalid payload.
- Duplicate provider/model pair: catalog validation fails.
- Orphan provider/model row: Website blocks pricing publication. Provider Catalog publication also blocks removal of a pair referenced by active pricing. Workbench ignores any orphan row defensively.
- Explicit all-zero row: valid and means the configured model is free for all dimensions.

## Contract Repository Deliverables

Add:

```text
src/cogeval_platform_contracts/model_pricing/
  __init__.py
  v1.py
  resources.py
  schemas/model_pricing_catalog.v1.schema.json
  fixtures/empty.v1.json
  fixtures/provider_models.v1.json
tests/
  test_model_pricing_v1.py
  test_model_pricing_json_schema.py
  test_model_pricing_resources.py
docs/
  MODEL_PRICING_CATALOG_V1.md
  integrations/workbench-model-pricing-v1.md
```

Update:

- `pyproject.toml` package data;
- `docs/契约.md` contract and integration indexes;
- `docs/integrations/README.md`;
- `docs/integrations/workbench-api-key-provider-catalog-v1.md` to document its producer's reverse validation against active pricing before provider/model removal;
- package exports where appropriate.

## Required Contract Tests

Pydantic tests prove:

- an empty catalog is valid;
- realistic provider/model prices are valid;
- all-zero prices are valid;
- all five rates are required;
- JSON numeric rates are rejected;
- negative, scientific-notation, plus-prefixed, blank, and non-finite strings are rejected;
- leading zeros, incomplete decimal forms, whitespace, the 12/12 digit boundaries, and values exceeding either digit limit are tested;
- duplicate `provider_id + model_id` pairs are rejected;
- blank IDs and unknown fields are rejected.

JSON Schema tests prove:

- the schema is valid Draft 2020-12;
- every valid fixture passes;
- representative invalid rates and missing dimensions fail.
- `updated_at` accepts only the exact UTC `YYYY-MM-DDTHH:MM:SSZ` syntax and the empty seed timestamp is stable across reads.

Resource tests prove:

- schema and fixtures are packaged and loadable;
- resources are JSON serializable;
- fixture names are discoverable.

Producer tests required by the integration document:

- Website public endpoint returns the direct v1 contract.
- No active catalog returns a valid empty catalog.
- draft validation uses the shared contract.
- publish rejects missing/unknown provider-model references.
- API Key Provider Catalog publish rejects removal of a pair referenced by active pricing.
- concurrent/stale validation cannot commit mutually inconsistent active catalogs.
- only one active catalog is publicly returned.
- public catalog authentication follows existing catalog policy.

Future Workbench consumer tests required by the integration document:

- accepted catalog is loaded and validated;
- decimal rate strings are preserved;
- exact API-key provider/model matching works;
- missing/built-in/orphan pricing is unavailable;
- invalid catalog disables cost only;
- cache and reasoning dimensions map to the corresponding canonical token fields.
- disjoint ordinary/reasoning output is charged exactly once.

## Compatibility

This is a new v1 contract and does not change existing provider or model capability schemas. V1 is a closed schema: Pydantic uses `extra="forbid"` and JSON Schema uses `additionalProperties: false` at every object level. Adding fields, changing currency or unit semantics, changing identity matching, changing required dimensions, or changing decimal meaning requires a new schema version.
