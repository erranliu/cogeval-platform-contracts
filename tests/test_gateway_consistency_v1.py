from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.gateway_consistency import (
    GATEWAY_CONSISTENCY_BASELINE_SCHEMA,
    GATEWAY_CONSISTENCY_TASK_PACK_SCHEMA,
    GatewayConsistencyBaseline,
    GatewayConsistencyTaskPack,
    load_fixture,
    validate_gateway_consistency_baseline,
    validate_gateway_consistency_task_pack,
)


def test_gateway_consistency_fixtures_are_valid() -> None:
    baseline = validate_gateway_consistency_baseline(load_fixture("baseline_reference.v1"))
    pack = validate_gateway_consistency_task_pack(load_fixture("task_pack.v1"))

    assert baseline.schema == GATEWAY_CONSISTENCY_BASELINE_SCHEMA
    assert pack.schema == GATEWAY_CONSISTENCY_TASK_PACK_SCHEMA


def test_gateway_consistency_task_pack_requires_models_and_cases() -> None:
    payload = load_fixture("task_pack.v1")
    payload["models"] = []

    with pytest.raises(ValidationError, match="task pack must include at least one model"):
        GatewayConsistencyTaskPack.model_validate(payload)


def test_gateway_consistency_task_pack_allows_empty_case_title() -> None:
    payload = load_fixture("task_pack.v1")
    payload["cases"][0]["title"] = ""

    pack = validate_gateway_consistency_task_pack(payload)

    assert pack.cases[0].title == ""


def test_gateway_consistency_baseline_requires_raw_reference_results() -> None:
    payload = load_fixture("baseline_reference.v1")
    payload["raw"] = {}

    with pytest.raises(ValidationError):
        GatewayConsistencyBaseline.model_validate(payload)
