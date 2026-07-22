from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

FailureOwner = Literal[
    "case",
    "config",
    "source_execution",
    "host_execution",
    "runner",
    "orchestration",
    "validation",
    "evidence",
    "delivery",
    "workbench",
    "platform",
]
FailureCategory = Literal[
    "invalid_input",
    "not_found",
    "conflict",
    "blocked",
    "unavailable",
    "timeout",
    "execution_failure",
    "contract_violation",
    "invariant_violation",
    "cancelled",
    "internal",
]
RetryPolicy = Literal["never", "same_request", "after_external_recovery", "after_user_action"]

_CODE_RE = re.compile(
    r"^(case|config|source_execution|host_execution|runner|orchestration|validation|evidence|delivery|workbench|platform)\.[a-z][a-z0-9_]*$"
)


class StrictContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
        populate_by_name=True,
    )


class FailureReasonV1(StrictContractModel):
    schema_version: Literal["cogeval.failure-reason.v1"] = "cogeval.failure-reason.v1"
    code: str = Field(min_length=3, max_length=120)
    category: FailureCategory
    retry_policy: RetryPolicy
    message: str = Field(min_length=1, max_length=240)

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if _CODE_RE.fullmatch(value) is None:
            raise ValueError("code must use a known owner and lower_snake_case local code")
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if any(char in value for char in "\r\n"):
            raise ValueError("message must be a single line")
        return value


class FailureEnvelopeV1(StrictContractModel):
    schema_version: Literal["cogeval.failure-envelope.v1"] = "cogeval.failure-envelope.v1"
    reason: FailureReasonV1
    correlation_id: str = Field(min_length=1, max_length=200)
    retry_after_ms: int | None = Field(default=None, ge=0)


def validate_failure_reason(payload: Any) -> FailureReasonV1:
    return FailureReasonV1.model_validate(payload)


def validate_failure_envelope(payload: Any) -> FailureEnvelopeV1:
    return FailureEnvelopeV1.model_validate(payload)
