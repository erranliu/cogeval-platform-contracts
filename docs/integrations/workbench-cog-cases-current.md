# Workbench COG Cases — current contract

The active Workbench contract is `cogeval.cog_case.v3` for cases and
`cogeval.cog_case_group.v1` for groups. Retired case payloads are rejected;
consumers do not scan, normalize, or merge historical versions.

## Producer API

- `GET /api/public/cog-cases` returns one page envelope:
  `{items, next_cursor, total}`, where `total` is a non-negative integer when
  the producer computes it and otherwise `null`.
  Workbench may pass `source_id` to narrow the current published catalog. The
  endpoint remains paginated; consumers must follow `next_cursor` and match
  `external_id` locally when resolving the `(source_id, external_id)` identity.
- `GET /api/public/cog-cases/lookup?cog_case_no=...` returns one immutable
  `cogeval.cog_case.v3` snapshot containing the complete identity and any
  source-specific public projection fields available to Workbench, or `404`.
- `GET /api/public/cog-case-groups` returns a page of fully hydrated
  `cogeval.cog_case_group.v1` values.
- Authentication is not required for these published reads.

The v3 case includes `cog_case_display_id`, `source_id`, and `external_id` in
the same snapshot. Workbench must not issue a second detail request or merge
data from another endpoint.

## Consumer behavior

Workbench validates the exact current schemas and adds only local
workspace/environment projections. A missing platform, network error,
malformed JSON, wrong envelope, unknown schema, or incomplete required case is
an error. The local `/api/cog-cases` projection may still expose the
Workbench mini case when the platform is not configured; that is an explicit
product-local case.

## Required producer checks

- list and lookup return only published active cases;
- lookup matches `cog_case_display_id` exactly and returns a complete v3 payload;
- group list items are complete group payloads with members;
- restricted source data is not leaked into the public projection.
