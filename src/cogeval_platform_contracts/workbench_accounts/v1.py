from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


WORKBENCH_AUTH_GITHUB_REQUEST_SCHEMA = "cogeval.workbench.auth_github_request.v1"
WORKBENCH_AUTH_GITHUB_RESPONSE_SCHEMA = "cogeval.workbench.auth_github_response.v1"
WORKBENCH_ACCOUNT_ASSETS_SCHEMA = "cogeval.workbench.account_assets.v1"
WORKBENCH_COIN_RESERVATION_SCHEMA = "cogeval.workbench.coin_reservation.v1"


class StrictContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class WorkbenchAuthGithubRequest(StrictContractModel):
    schema_: Literal["cogeval.workbench.auth_github_request.v1"] = Field(alias="schema")
    github_access_token: str = Field(min_length=1)
    workbench_device_id: str | None = None
    workbench_version: str | None = None
    client_time: str | None = None

    @property
    def schema(self) -> str:
        return self.schema_


class WorkbenchAccount(StrictContractModel):
    account_id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    display_name: str | None = None
    avatar_url: str | None = None
    primary_email: str | None = None
    created_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)
    last_login_at: str | None = None


class WorkbenchGithubIdentity(StrictContractModel):
    provider: Literal["github"] = "github"
    github_user_id: str = Field(min_length=1)
    github_login: str | None = None
    profile_url: str | None = None
    avatar_url: str | None = None
    email: str | None = None
    verified_email: bool = False
    linked_at: str = Field(min_length=1)
    last_verified_at: str = Field(min_length=1)


class WorkbenchAssets(StrictContractModel):
    eval_score: int = Field(ge=0)
    eval_coins: int = Field(ge=0)
    ledger_version: int = Field(ge=0)
    updated_at: str = Field(min_length=1)


class WorkbenchSession(StrictContractModel):
    access_token: str = Field(min_length=1)
    token_type: Literal["bearer"] = "bearer"
    expires_at: str = Field(min_length=1)


class WorkbenchAuthGithubResponse(StrictContractModel):
    schema_: Literal["cogeval.workbench.auth_github_response.v1"] = Field(alias="schema")
    account: WorkbenchAccount
    github_identity: WorkbenchGithubIdentity
    assets: WorkbenchAssets
    session: WorkbenchSession

    @property
    def schema(self) -> str:
        return self.schema_


class WorkbenchAccountAssets(StrictContractModel):
    schema_: Literal["cogeval.workbench.account_assets.v1"] = Field(alias="schema")
    assets: WorkbenchAssets
    ledger_entries: list[dict[str, Any]] = Field(default_factory=list)

    @property
    def schema(self) -> str:
        return self.schema_


class WorkbenchCoinReservation(StrictContractModel):
    schema_: Literal["cogeval.workbench.coin_reservation.v1"] = Field(alias="schema")
    reservation_id: str | None = None
    status: str | None = None
    amount: int = Field(ge=0)
    action: str | None = None
    subject: dict[str, Any] = Field(default_factory=dict)
    client_context: dict[str, Any] = Field(default_factory=dict)
    expires_at: str | None = None
    assets: WorkbenchAssets | None = None
    ledger_entry: dict[str, Any] | None = None

    @property
    def schema(self) -> str:
        return self.schema_


def validate_workbench_auth_github_request(payload: Any) -> WorkbenchAuthGithubRequest:
    return WorkbenchAuthGithubRequest.model_validate(payload)


def validate_workbench_auth_github_response(payload: Any) -> WorkbenchAuthGithubResponse:
    return WorkbenchAuthGithubResponse.model_validate(payload)


def validate_workbench_account_assets(payload: Any) -> WorkbenchAccountAssets:
    return WorkbenchAccountAssets.model_validate(payload)


def validate_workbench_coin_reservation(payload: Any) -> WorkbenchCoinReservation:
    return WorkbenchCoinReservation.model_validate(payload)
