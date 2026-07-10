# Workbench Model Pricing Catalog v1

Data schema: `cogeval.model_pricing_catalog.v1`

Producer: COGEval Website Workbench API

Consumer: COGEval Workbench cost estimation for API-key model sources

## Purpose

This integration delivers the current API-key provider/model token prices to
Workbench. The shared schema defines payload validity; this document defines
the public route, loader behavior, cross-catalog publication invariant, and
failure isolation.

## Producer API

- Method and path: `GET /api/workbench/v1/model-pricing`.
- Response shape: the response body is the
  `cogeval.model_pricing_catalog.v1` catalog itself, without an outer envelope.
- Authentication: use the existing optional Workbench catalog Bearer-token policy.
  A deployment that protects the other Workbench catalog endpoints
  protects this endpoint with the same configured token.
- Scope: rows cover API-key provider sources only. Built-in account sources are excluded.
- No active version: return the stable valid empty seed, not `404`, `503`, an
  envelope, or a request-time timestamp. The seed has `prices: []` and a stable
  checked-in or code-level `updated_at` constant.

The producer validates the public response with the shared contract. Internal
draft/version storage and admin DTOs are Website implementation details, not
cross-project contracts. A structured draft, validate, and publish lifecycle is
recommended, with a single current active catalog exposed publicly.

## Consumer Loader

- Default path: `/api/workbench/v1/model-pricing`.
- Config override: `platform.model_pricing_catalog_path`.
- Base URL: use the same configured platform base URL resolution as the other
  Workbench catalogs (`platform_base_url`, `COG_EVAL_PLATFORM_BASE_URL`,
  `COGEVAL_PLATFORM_BASE_URL`, or `platform.base_url`).
- Authentication: send the same optional catalog authorization used by existing
  Workbench catalog loaders.
- Validation: validate the complete response using
  `cogeval_platform_contracts.model_pricing.validate_model_pricing_catalog`.
- Matching: join API-key provider sources only by exact
  `provider_id + model_id`; do not case-fold or use aliases.
- Caching: load through platform catalog configuration and retain the validated
  catalog for that configuration/run lifecycle. Do not live poll prices.

The Workbench consumer is intentionally future work. This integration reserves
the loader behavior and failure contract without defining Workbench internal
storage or UI DTOs.

## Data Flow

```text
Website committed active pricing catalog (or stable empty seed)
  -> GET /api/workbench/v1/model-pricing
  -> Workbench configured catalog loader
  -> shared whole-catalog validation
  -> exact API-key provider_id + model_id join
  -> five canonical token dimensions
  -> Decimal cost estimate
```

Workbench may additionally check accepted pricing pairs against its accepted
API Key Provider Catalog and ignore an orphan row defensively. This does not
relax the producer publication invariant.

## Publication Ordering and Concurrency

Before commit, pricing publication validates every row against the active API Key Provider Catalog.
Conversely, API Key Provider Catalog publication validates against the
active Model Pricing Catalog and cannot remove a pair that remains priced.

The required operator ordering is:

- Add a pair: provider-first, then pricing.
- Remove a pair: pricing-first, then provider.

No dual-catalog atomic publish endpoint is required. However, counterpart validation must be repeated inside the publish transaction or equivalent
serialization boundary against the committed active counterpart. A successful
draft validation against stale state is insufficient. If the counterpart
changes concurrently, publication must revalidate the committed active
counterpart and reject a result that would make the two active catalogs
inconsistent.

## Failure Behavior

- No active Website version returns the stable valid empty seed; Workbench
  reports price not configured.
- An empty catalog or missing exact row means price not configured, never zero.
- An explicit zero rate is valid and means the corresponding dimension is free.
- Built-in account, missing, and orphan rows have pricing unavailable.
- Unauthorized, timeout, unavailable, invalid JSON, or invalid catalog disables cost estimation only; token recording and execution remain available.
- The consumer rejects an invalid catalog as a whole. It does not recover
  valid-looking rows from an invalid payload.
- Duplicate exact pairs fail shared Pydantic validation.
- Cache read/write and uncached input map only to their matching canonical token
  fields; reasoning and ordinary output are disjoint and each is charged exactly once.

## Required Tests

### Producer tests

The Website repository must prove:

- public endpoint returns the direct v1 catalog;
- no active catalog returns the stable valid empty seed;
- draft validation uses the shared contract;
- publish rejects unknown provider/model references;
- provider catalog publish blocks referenced removal;
- stale validation cannot commit inconsistent active catalogs;
- only one current active catalog is returned;
- endpoint authentication follows the existing catalog policy.

### Future Workbench consumer tests

The Workbench repository must prove:

- accepted payloads are loaded and validated;
- decimal strings are preserved;
- exact API-key `provider_id + model_id` matching works;
- missing, built-in, and orphan pricing are unavailable;
- invalid catalog disables cost only while tokens and execution remain usable;
- cache and reasoning dimensions map to canonical token fields;
- reasoning output is charged exactly once and ordinary output is not double
  counted.

## Minimal Payload

```json
{
  "schema": "cogeval.model_pricing_catalog.v1",
  "updated_at": "2026-01-01T00:00:00Z",
  "currency": "USD",
  "unit_tokens": 1000000,
  "prices": []
}
```
