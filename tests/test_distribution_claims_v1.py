from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.distribution_claims import (
    DISTRIBUTION_CLAIM_REQUEST_SCHEMA,
    DISTRIBUTION_CLAIM_SCHEMA,
    DistributionClaim,
    DistributionClaimRequest,
    load_fixture,
    validate_distribution_claim,
    validate_distribution_claim_request,
)


def test_distribution_claim_fixtures_are_valid() -> None:
    request = validate_distribution_claim_request(load_fixture("claim_request.v1"))
    claim = validate_distribution_claim(load_fixture("claim_assigned.v1"))

    assert request.schema == DISTRIBUTION_CLAIM_REQUEST_SCHEMA
    assert claim.schema == DISTRIBUTION_CLAIM_SCHEMA


def test_distribution_claim_request_rejects_negative_max_minutes() -> None:
    payload = load_fixture("claim_request.v1")
    payload["max_minutes"] = -1

    with pytest.raises(ValidationError):
        DistributionClaimRequest.model_validate(payload)


def test_distribution_claim_requires_case_refs() -> None:
    payload = load_fixture("claim_assigned.v1")
    payload.pop("case_refs")

    with pytest.raises(ValidationError):
        DistributionClaim.model_validate(payload)
