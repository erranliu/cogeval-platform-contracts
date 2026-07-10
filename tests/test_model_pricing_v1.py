from copy import deepcopy

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.model_pricing import (
    MODEL_PRICING_CATALOG_SCHEMA,
    ModelPrice,
    ModelPricingCatalog,
    PricingRates,
    validate_model_pricing_catalog,
)


RATE_FIELDS = (
    "input_uncached",
    "input_cache_read",
    "input_cache_write",
    "output",
    "reasoning_output",
)


def _rates(value: object = "0") -> dict[str, object]:
    return {field: value for field in RATE_FIELDS}


def _price(
    *,
    provider_id: str = "openai",
    model_id: str = "gpt-5.4",
    rates: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "provider_id": provider_id,
        "model_id": model_id,
        "rates": _rates() if rates is None else rates,
    }


def _payload(*, prices: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "schema": MODEL_PRICING_CATALOG_SCHEMA,
        "updated_at": "2026-07-10T13:14:15Z",
        "currency": "USD",
        "unit_tokens": 1_000_000,
        "prices": [] if prices is None else prices,
    }


def test_validates_exact_empty_current_catalog() -> None:
    payload = _payload()

    catalog = validate_model_pricing_catalog(payload)

    assert catalog.schema == "cogeval.model_pricing_catalog.v1"
    assert catalog.schema_version == MODEL_PRICING_CATALOG_SCHEMA
    assert catalog.updated_at == "2026-07-10T13:14:15Z"
    assert catalog.currency == "USD"
    assert catalog.unit_tokens == 1_000_000
    assert catalog.prices == []
    assert catalog.model_dump(by_alias=True) == payload


def test_validates_realistic_price_rows_and_all_zero_rates() -> None:
    payload = _payload(
        prices=[
            _price(
                rates={
                    "input_uncached": "1.25",
                    "input_cache_read": "0.125",
                    "input_cache_write": "1.5",
                    "output": "10",
                    "reasoning_output": "10.75",
                }
            ),
            _price(provider_id="anthropic", model_id="claude-sonnet-4", rates=_rates("0")),
        ]
    )

    catalog = ModelPricingCatalog.model_validate(payload)

    assert catalog.prices[0] == ModelPrice(
        provider_id="openai",
        model_id="gpt-5.4",
        rates=PricingRates(
            input_uncached="1.25",
            input_cache_read="0.125",
            input_cache_write="1.5",
            output="10",
            reasoning_output="10.75",
        ),
    )
    assert catalog.prices[1].rates.reasoning_output == "0"


@pytest.mark.parametrize(
    "rate",
    ["0", "3", "0.3", "3.75", "123456789012", "0.123456789012"],
)
def test_accepts_canonical_decimal_rate_strings(rate: str) -> None:
    catalog = validate_model_pricing_catalog(_payload(prices=[_price(rates=_rates(rate))]))

    assert catalog.prices[0].rates.input_uncached == rate


@pytest.mark.parametrize(
    "rate",
    [
        "00",
        "01",
        ".5",
        "1.",
        " 1",
        "1 ",
        "\t1",
        "1\n",
        "1e3",
        "1E+3",
        "-1",
        "1234567890123",
        "0.1234567890123",
        1,
        0.5,
        True,
        False,
        "",
    ],
)
def test_rejects_noncanonical_or_nonstring_rates(rate: object) -> None:
    with pytest.raises(ValidationError):
        validate_model_pricing_catalog(_payload(prices=[_price(rates=_rates(rate))]))


@pytest.mark.parametrize("missing_field", RATE_FIELDS)
def test_requires_all_five_rates(missing_field: str) -> None:
    rates = _rates()
    del rates[missing_field]

    with pytest.raises(ValidationError):
        validate_model_pricing_catalog(_payload(prices=[_price(rates=rates)]))


@pytest.mark.parametrize("field", ["provider_id", "model_id"])
@pytest.mark.parametrize("value", ["", " ", "\t", "\n", " \t\n"])
def test_rejects_blank_or_whitespace_only_ids(field: str, value: str) -> None:
    price = _price()
    price[field] = value

    with pytest.raises(ValidationError, match="must not be blank"):
        validate_model_pricing_catalog(_payload(prices=[price]))


@pytest.mark.parametrize("level", ["catalog", "price", "rates"])
def test_rejects_unknown_fields_at_every_model_level(level: str) -> None:
    payload = _payload(prices=[_price()])
    target = {
        "catalog": payload,
        "price": payload["prices"][0],
        "rates": payload["prices"][0]["rates"],
    }[level]
    target["unknown"] = "forbidden"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        validate_model_pricing_catalog(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", "cogeval.model_pricing_catalog.v2"),
        ("currency", "EUR"),
        ("unit_tokens", 1_000),
    ],
)
def test_enforces_schema_currency_and_unit_literals(field: str, value: object) -> None:
    payload = _payload()
    payload[field] = value

    with pytest.raises(ValidationError):
        validate_model_pricing_catalog(payload)


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-7-10T13:14:15Z",
        "2026-07-1T13:14:15Z",
        "2026-07-10T3:14:15Z",
        "2026-07-10T13:4:15Z",
        "2026-07-10T13:14:5Z",
        "2026-07-10 13:14:15Z",
        "2026-07-10T13:14:15+00:00",
        "2026-02-30T13:14:15Z",
        "2025-02-29T13:14:15Z",
        "2026-13-10T13:14:15Z",
        "2026-07-10T24:14:15Z",
    ],
)
def test_rejects_nonexact_or_impossible_utc_timestamps(timestamp: str) -> None:
    payload = _payload()
    payload["updated_at"] = timestamp

    with pytest.raises(ValidationError, match="updated_at must be a real UTC timestamp"):
        validate_model_pricing_catalog(payload)


@pytest.mark.parametrize(
    "field",
    ["schema", "updated_at", "currency", "unit_tokens", "prices"],
)
def test_requires_every_top_level_field(field: str) -> None:
    payload = _payload()
    del payload[field]

    with pytest.raises(ValidationError):
        validate_model_pricing_catalog(payload)


def test_rejects_internal_schema_version_wire_key() -> None:
    payload = _payload()
    payload["schema_version"] = payload.pop("schema")

    with pytest.raises(ValidationError):
        validate_model_pricing_catalog(payload)


def test_rejects_duplicate_provider_and_model_pair_with_clear_message() -> None:
    payload = _payload(prices=[_price(), deepcopy(_price())])

    with pytest.raises(
        ValidationError,
        match=r"duplicate provider_id \+ model_id pair: openai/gpt-5\.4",
    ):
        validate_model_pricing_catalog(payload)
