# Workbench COG Cases — current contract

The active Workbench contract is `cogeval.cog_case.v3` for cases and
`cogeval.cog_case_group.v1` for groups. Payloads from case v1/v2 are retired;
consumers must reject them instead of scanning or normalizing them.

## Producer API

- `GET /api/public/cog-cases` returns one page envelope: `{items, next_cursor, total}`.
- `GET /api/public/cog-cases/lookup?cog_case_no=...` returns one fully hydrated
  immutable `cogeval.cog_case.v3` snapshot or `404`.
- `GET /api/public/cog-case-groups` returns one page envelope whose items are
  fully hydrated `cogeval.cog_case_group.v1` values.
- `GET /api/public/cog-case-groups/{slug}` is not used by Workbench and may be
  retired by the producer.
- Authentication is not required for these published reads.

The v3 case includes the identity (`cog_case_display_id`, `source_id`,
`external_id`) and any public source/workspace/validation fields needed for
local preparation. Workbench must not issue a second public test-case detail
request or merge data from another endpoint.
The `source_id + external_id` pair remains the internal materialization
coordinate; `cog_case_display_id` is the product identity.

## Consumer behavior

Workbench validates the exact current schemas, preserves the source identity,
and adds only local workspace/environment projections. A missing platform,
network error, malformed JSON, wrong envelope, unknown schema, or incomplete
required case is an error; no empty cache entry or legacy list scan is used.

The local `/api/cog-cases` projection may still expose the Workbench mini case
when the platform is not configured. That is an explicit product-local case,
not a platform fallback.

## Required producer checks

- list and lookup return only published active cases;
- lookup matches `cog_case_display_id` exactly and returns a complete v3 payload;
- group list items are complete group payloads with members when advertised;
- restricted source data is not leaked into the public projection.
