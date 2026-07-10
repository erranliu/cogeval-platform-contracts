from __future__ import annotations

from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

import cogeval_platform_contracts.model_pricing as model_pricing


RATE_FIELDS = (
    "input_uncached",
    "input_cache_read",
    "input_cache_write",
    "output",
    "reasoning_output",
)


def _validator() -> Draft202012Validator:
    return Draft202012Validator(
        model_pricing.load_schema("model_pricing_catalog.v1"),
        format_checker=FormatChecker(),
    )


def _valid_payload() -> dict[str, object]:
    return {
        "schema": model_pricing.MODEL_PRICING_CATALOG_SCHEMA,
        "updated_at": "2026-07-10T13:14:15Z",
        "currency": "USD",
        "unit_tokens": 1_000_000,
        "prices": [
            {
                "provider_id": "openai",
                "model_id": "gpt-5.4",
                "rates": {field: "0" for field in RATE_FIELDS},
            }
        ],
    }


def test_model_pricing_json_schema_is_valid_draft_2020_12() -> None:
    schema = model_pricing.load_schema("model_pricing_catalog.v1")

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)


def test_model_pricing_json_schema_uses_repository_identifier_convention() -> None:
    schema = model_pricing.load_schema("model_pricing_catalog.v1")

    assert (
        schema["$id"]
        == "https://contracts.cogeval.dev/model_pricing_catalog.v1.schema.json"
    )


def test_both_fixtures_validate_with_json_schema_and_pydantic() -> None:
    validator = _validator()

    for fixture_name in ("empty.v1", "provider_models.v1"):
        payload = model_pricing.load_fixture(fixture_name)
        validator.validate(payload)
        assert model_pricing.validate_model_pricing_catalog(payload).model_dump(
            by_alias=True
        ) == payload


@pytest.mark.parametrize(
    "field",
    ["schema", "updated_at", "currency", "unit_tokens", "prices"],
)
def test_json_schema_requires_every_top_level_field(field: str) -> None:
    payload = _valid_payload()
    del payload[field]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize("field", ["provider_id", "model_id", "rates"])
def test_json_schema_requires_every_price_field(field: str) -> None:
    payload = _valid_payload()
    del payload["prices"][0][field]  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize("field", RATE_FIELDS)
def test_json_schema_requires_all_five_rate_fields(field: str) -> None:
    payload = _valid_payload()
    del payload["prices"][0]["rates"][field]  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


def test_json_schema_requires_rates_object() -> None:
    payload = _valid_payload()
    payload["prices"][0]["rates"] = None  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize("field", ["provider_id", "model_id"])
@pytest.mark.parametrize("value", [" ", "\t", "\n"])
def test_json_schema_rejects_whitespace_only_price_identifiers(
    field: str,
    value: str,
) -> None:
    payload = _valid_payload()
    payload["prices"][0][field] = value  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize("rate", [1, 0.5, True, False])
def test_json_schema_rejects_json_numeric_and_boolean_rates(rate: object) -> None:
    payload = _valid_payload()
    payload["prices"][0]["rates"]["input_uncached"] = rate  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize(
    "rate",
    [
        "123456789012",
        "0.123456789012",
        "123456789012.123456789012",
    ],
)
def test_json_schema_accepts_twelve_digit_decimal_boundaries(rate: str) -> None:
    payload = _valid_payload()
    payload["prices"][0]["rates"]["input_uncached"] = rate  # type: ignore[index]

    _validator().validate(payload)


@pytest.mark.parametrize(
    "rate",
    [
        "00",
        "01",
        ".5",
        "1.",
        "1234567890123",
        "0.1234567890123",
        "1e3",
        "+1",
        "-1",
        "",
    ],
)
def test_json_schema_rejects_invalid_decimal_boundaries(rate: str) -> None:
    payload = _valid_payload()
    payload["prices"][0]["rates"]["input_uncached"] = rate  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize("rate", ["1\n", " 1", "1 ", "\t1", "1\r\n"])
def test_json_schema_rejects_rates_containing_whitespace(rate: str) -> None:
    payload = _valid_payload()
    payload["prices"][0]["rates"]["input_uncached"] = rate  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize("level", ["catalog", "price", "rates"])
def test_json_schema_rejects_unknown_fields_at_every_level(level: str) -> None:
    payload = _valid_payload()
    targets = {
        "catalog": payload,
        "price": payload["prices"][0],  # type: ignore[index]
        "rates": payload["prices"][0]["rates"],  # type: ignore[index]
    }
    targets[level]["unknown"] = "forbidden"  # type: ignore[index]

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-7-10T13:14:15Z",
        "2026-07-10 13:14:15Z",
        "2026-07-10T13:14:15+00:00",
        "2026-07-10T13:14:15.000Z",
    ],
)
def test_json_schema_rejects_malformed_timestamp_syntax(timestamp: str) -> None:
    payload = _valid_payload()
    payload["updated_at"] = timestamp

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-02-30T13:14:15Z",
        "2025-02-29T13:14:15Z",
        "2026-13-10T13:14:15Z",
        "2026-07-10T24:14:15Z",
    ],
)
def test_json_schema_format_checker_rejects_impossible_calendar_timestamps(
    timestamp: str,
) -> None:
    payload = _valid_payload()
    payload["updated_at"] = timestamp

    with pytest.raises(ValidationError):
        _validator().validate(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", "cogeval.model_pricing_catalog.v2"),
        ("currency", "EUR"),
        ("unit_tokens", 1_000),
    ],
)
def test_json_schema_enforces_catalog_constants(field: str, value: object) -> None:
    payload = _valid_payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        _validator().validate(payload)


def test_json_schema_allows_empty_prices() -> None:
    payload = deepcopy(_valid_payload())
    payload["prices"] = []

    _validator().validate(payload)


def test_json_schema_allows_duplicate_pairs_because_pydantic_is_normative() -> None:
    payload = _valid_payload()
    payload["prices"].append(deepcopy(payload["prices"][0]))  # type: ignore[union-attr]

    _validator().validate(payload)
