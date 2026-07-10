# Model Pricing Catalog v1

Schema: `cogeval.model_pricing_catalog.v1`

This contract publishes the current token prices for models reached through
platform API-key providers. It is independent of provider availability and
model capability catalogs because a price can change without either capability
contract changing.

## Scope and Compatibility

V1 is a current-only catalog. It exposes one current price per exact provider
and model pair; it does not reproduce historical prices or select a price by an
effective date.

This is a closed v1 schema. Pydantic rejects extra fields, and JSON Schema sets
`additionalProperties: false` at every object level. Adding a field, changing
the identity rule, currency, token unit, decimal meaning, or required rate
dimensions is incompatible and requires a new schema version.

V1 does not define built-in account pricing, tiers, context-window bands,
discounts, aliases, regions, multiple currencies, live polling, or historical
cost recalculation.

## Catalog Shape

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

Top-level fields are all required:

| Field | Contract meaning |
|---|---|
| `schema` | Literal `cogeval.model_pricing_catalog.v1`. |
| `updated_at` | Publication time, using the exact UTC grammar `YYYY-MM-DDTHH:MM:SSZ`. |
| `currency` | Literal `USD`. |
| `unit_tokens` | Integer literal `1000000`. Rates are USD per exactly 1,000,000 tokens. |
| `prices` | Current price rows; the array may be empty. |

`updated_at` has no fractional seconds or numeric offset. Its calendar and time
must also be real, so invalid dates such as `2026-02-30T00:00:00Z` and hour 24
are rejected.

For an active catalog, `updated_at` is its publication time. For the no-active empty seed, `updated_at` is a stable seed-definition constant and is never generated from request time. The seed value changes only when the seed definition changes.

## Identity and Uniqueness

The row identity is the exact `provider_id + model_id` pair. Both identifiers
come from the active API Key Provider Catalog and are matched byte-for-byte.
There is no alias expansion, fuzzy match, case folding, or built-in account
mapping.

Each pair occurs at most once. JSON Schema can validate each row but cannot
enforce uniqueness of a two-field projection. Pydantic whole-catalog validation is normative for pair uniqueness.
Producers and consumers must therefore run the shared Pydantic validator in
addition to any boundary JSON Schema checks.

## Rate Dimensions and Token Mapping

Every row requires all five decimal-string rates:

| Pricing rate | Canonical Workbench token field |
|---|---|
| `input_uncached` | `input_uncached_tokens` |
| `input_cache_read` | `input_cache_read_tokens` |
| `input_cache_write` | `input_cache_write_tokens` |
| `output` | `output_tokens` |
| `reasoning_output` | `reasoning_output_tokens` |

The five dimensions are independent. In particular, ordinary output and reasoning output are disjoint token counts; each dimension is charged exactly once.

## Decimal Strings

Rates are JSON strings, never JSON numbers. Their exact grammar and bounds are:

```regex
^(0|[1-9][0-9]{0,11})(\.[0-9]{1,12})?$
```

The integer part has at most 12 digits, the optional fractional part has from
1 through 12 digits, and trailing fractional zeros are preserved. Consumers
must use decimal arithmetic and must not round an individual dimension or an
intermediate product.

Valid values include `"0"`, `"3"`, `"0.3"`, `"3.75"`,
`"123456789012"`, and `"0.123456789012"`.

Invalid values include JSON numbers, negative or plus-prefixed values,
scientific notation, `NaN`, infinity, blank or whitespace-bearing strings,
leading-zero forms such as `"00"` and `"01"`, incomplete decimals such as
`".5"` and `"1."`, and values exceeding either 12-digit bound.

## Empty, Missing, and Zero Semantics

An empty `prices` array is a valid catalog and means no model prices are
currently configured. A missing row means pricing is unavailable; it never means free.
Within an existing row, an explicit rate of `"0"` means that dimension is free.
An explicit row with all five rates set to `"0"` therefore means that model is
configured as entirely free.

Only API-key provider model sources can join to this contract. Built-in account
sources such as Codex CLI and Claude Code CLI are outside v1 and have pricing
unavailable.

## Cost Semantics

For complete canonical token usage and an exact matching row, consumers compute:

```text
cost_usd =
  input_uncached_tokens    * input_uncached_rate    / unit_tokens
+ input_cache_read_tokens  * input_cache_read_rate  / unit_tokens
+ input_cache_write_tokens * input_cache_write_rate / unit_tokens
+ output_tokens            * output_rate            / unit_tokens
+ reasoning_output_tokens  * reasoning_output_rate  / unit_tokens
```

The formula uses the five disjoint canonical dimensions. In particular,
reasoning tokens are not a subset to subtract from ordinary output and are not
included twice. Display formatting may round only the final presentation value.

Cost is unavailable unless canonical token usage is complete, the source is an
API-key provider source, the exact pair exists, and the entire catalog passes
validation.

## Normative Resources

- Pydantic model and validator: `cogeval_platform_contracts.model_pricing`
- JSON Schema: `model_pricing_catalog.v1.schema.json`
- Stable empty example: `empty.v1.json`
- Representative provider examples: `provider_models.v1.json`
