from __future__ import annotations

import pytest
from pydantic import ValidationError

from cogeval_platform_contracts.workbench_accounts import (
    WORKBENCH_ACCOUNT_ASSETS_SCHEMA,
    WORKBENCH_AUTH_GITHUB_REQUEST_SCHEMA,
    WORKBENCH_AUTH_GITHUB_RESPONSE_SCHEMA,
    WORKBENCH_COIN_RESERVATION_SCHEMA,
    WorkbenchAuthGithubRequest,
    WorkbenchCoinReservation,
    load_fixture,
    validate_workbench_account_assets,
    validate_workbench_auth_github_request,
    validate_workbench_auth_github_response,
    validate_workbench_coin_reservation,
)


def test_workbench_account_fixtures_are_valid() -> None:
    auth_request = validate_workbench_auth_github_request(load_fixture("auth_github_request.v1"))
    auth_response = validate_workbench_auth_github_response(load_fixture("auth_github_response.v1"))
    assets = validate_workbench_account_assets(load_fixture("account_assets.v1"))
    reservation = validate_workbench_coin_reservation(load_fixture("coin_reservation.v1"))

    assert auth_request.schema == WORKBENCH_AUTH_GITHUB_REQUEST_SCHEMA
    assert auth_response.schema == WORKBENCH_AUTH_GITHUB_RESPONSE_SCHEMA
    assert assets.schema == WORKBENCH_ACCOUNT_ASSETS_SCHEMA
    assert reservation.schema == WORKBENCH_COIN_RESERVATION_SCHEMA


def test_auth_github_request_requires_token() -> None:
    payload = load_fixture("auth_github_request.v1")
    payload["github_access_token"] = ""

    with pytest.raises(ValidationError):
        WorkbenchAuthGithubRequest.model_validate(payload)


def test_coin_reservation_rejects_negative_amount() -> None:
    payload = load_fixture("coin_reservation.v1")
    payload["amount"] = -1

    with pytest.raises(ValidationError):
        WorkbenchCoinReservation.model_validate(payload)
