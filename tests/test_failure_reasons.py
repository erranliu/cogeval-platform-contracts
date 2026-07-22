import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.failure_reasons import (
    FailureDefinition,
    FailureEnvelopeV1,
    FailureReasonV1,
    validate_failure_reason,
    load_fixture,
    load_schema,
)


def test_failure_reason_is_self_contained_and_strict() -> None:
    reason = FailureReasonV1(
        code="runner.process_timeout",
        category="timeout",
        retry_policy="same_request",
        message="Runner process timed out.",
    )
    assert reason.model_dump() == {
        "schema_version": "cogeval.failure-reason.v1",
        "code": "runner.process_timeout",
        "category": "timeout",
        "retry_policy": "same_request",
        "message": "Runner process timed out.",
    }
    with pytest.raises(ValidationError):
        validate_failure_reason({**reason.model_dump(), "detail": {}})


def test_definition_requires_owner_prefix() -> None:
    definition = FailureDefinition(
        owner="runner",
        code="runner.process_timeout",
        category="timeout",
        retry_policy="same_request",
        message="Runner process timed out.",
    )
    assert definition.occur().code == "runner.process_timeout"
    with pytest.raises(ValueError):
        FailureDefinition(
            owner="runner",
            code="workbench.process_timeout",
            category="timeout",
            retry_policy="same_request",
            message="Runner process timed out.",
        )


def test_envelope_does_not_duplicate_reason_fields() -> None:
    envelope = FailureEnvelopeV1(
        reason=FailureReasonV1(
            code="workbench.run_group_not_found",
            category="not_found",
            retry_policy="never",
            message="Run group was not found.",
        ),
        correlation_id="corr-1",
    )
    assert envelope.reason.code == "workbench.run_group_not_found"


def test_failure_fixtures_and_schemas_are_packaged() -> None:
    assert load_fixture("runner_process_timeout.v1")["code"] == "runner.process_timeout"
    assert load_schema("failure_reason.v1")["additionalProperties"] is False
    assert load_schema("failure_envelope.v1")["additionalProperties"] is False
