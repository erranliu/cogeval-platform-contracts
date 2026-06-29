# Workbench Accounts v1

Data schemas: `cogeval.workbench.auth_github_request.v1`, `cogeval.workbench.auth_github_response.v1`, `cogeval.workbench.account_assets.v1`, `cogeval.workbench.coin_reservation.v1`

Producer and consumer: COGEval Workbench and COGEval Website Workbench API

## Purpose

This integration connects a local Workbench installation to a platform account. It covers GitHub login completion, account/session restore, asset reads, logout, and Eval Coins reservations.

## Producer API

Website Workbench API endpoints:

- `GET /api/workbench/v1/client-config`
- `POST /api/workbench/v1/auth/github`
- `GET /api/workbench/v1/me`
- `GET /api/workbench/v1/assets`
- `POST /api/workbench/v1/logout`
- `POST /api/workbench/v1/coin-reservations`
- `POST /api/workbench/v1/coin-reservations/{reservation_id}/commit`
- `POST /api/workbench/v1/coin-reservations/{reservation_id}/cancel`

Authentication:

- `client-config` does not require a Bearer token.
- `auth/github` exchanges a GitHub access token for a Workbench session.
- `me`, `assets`, `logout`, and coin reservation endpoints require the Workbench session Bearer token.
- Mutating endpoints require an `Idempotency-Key` header.

## Consumer Loader

- Workbench platform client implementation: `src/cogeval/workbench/platform_account.py`.
- Local Workbench API routes expose account/session state under `/api/workbench/account/*`.
- Workbench stores the platform session locally and restores it before account-sensitive operations.
- Contract validation uses `cogeval_platform_contracts.workbench_accounts.v1`.

## Data Flow

```text
GitHub Device Flow token
  -> Workbench POST /api/workbench/v1/auth/github
  -> Website validates GitHub identity and returns account/session/assets
  -> Workbench stores session
  -> Workbench uses Bearer token for assets, reservations, and package submission
```

The platform account identity is based on GitHub numeric user id. GitHub login and email are display/search fields, not stable account keys.

## Failure Behavior

- Missing platform base URL: Workbench reports platform not configured and remains local-only.
- Invalid GitHub token: platform returns `INVALID_GITHUB_TOKEN`.
- Missing or expired session: platform returns session errors; Workbench clears or blocks account-sensitive operations.
- Missing idempotency key on mutation: platform rejects the request.
- Insufficient Eval Coins: platform returns an insufficient-balance error and does not mutate assets.

## Required Tests

Producer tests in the Website repository:

- GitHub login creates account/session without persisting the raw GitHub token.
- `me`, `assets`, logout, and coin reservation endpoints enforce session and idempotency rules.

Consumer tests in the Workbench repository:

- Workbench account API restores session and maps platform errors.
- Package submission requires a matching logged-in platform account when platform submission is enabled.

