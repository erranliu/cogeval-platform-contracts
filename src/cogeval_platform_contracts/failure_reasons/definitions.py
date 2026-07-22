from __future__ import annotations

from dataclasses import dataclass

from cogeval_platform_contracts.failure_reasons.v1 import (
    FailureCategory,
    FailureOwner,
    FailureReasonV1,
    RetryPolicy,
)


@dataclass(frozen=True, slots=True)
class FailureDefinition:
    owner: FailureOwner
    code: str
    category: FailureCategory
    retry_policy: RetryPolicy
    message: str

    def __post_init__(self) -> None:
        prefix, separator, _ = self.code.partition(".")
        if not separator or prefix != self.owner:
            raise ValueError("failure definition owner must match code prefix")
        FailureReasonV1(
            code=self.code,
            category=self.category,
            retry_policy=self.retry_policy,
            message=self.message,
        )

    def occur(self) -> FailureReasonV1:
        return FailureReasonV1(
            code=self.code,
            category=self.category,
            retry_policy=self.retry_policy,
            message=self.message,
        )
