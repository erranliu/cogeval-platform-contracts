# Workbench Gateway Consistency v1

Data schemas: `cogeval.gateway_consistency.task_pack.v1`, `cogeval.gateway_consistency.baseline.v1`

Producer: COGEval Website Workbench API

Consumer: COGEval Workbench Gateway Consistency view and batch runner

## Purpose

This integration provides a platform-curated gateway consistency task pack to Workbench. Workbench uses the task pack to prepare cases, select models, create local gateway consistency batches, and compare local runs against the platform baseline references.

## Producer API

- Method and path: `GET /api/workbench/v1/gateway-consistency/task-pack`
- Authentication: Workbench account Bearer token is required.
- Response shape: the response body is `cogeval.gateway_consistency.task_pack.v1`.
- The task pack embeds `cogeval.gateway_consistency.baseline.v1` payloads in `cases[].baseline`.
- The platform may return 404 when no active task pack is configured.

## Consumer Loader

- Workbench platform client path: `/api/workbench/v1/gateway-consistency/task-pack`
- Local Workbench API proxy: `GET /api/gateway-consistency/task-pack`
- Loader implementation: `src/cogeval/workbench/platform_account.py` and `src/cogeval/workbench/gateway_consistency_api.py`.
- Validation: Workbench validates with its gateway consistency contract models before creating batches.

## Data Flow

```text
Website gateway consistency task pack
  -> GET /api/workbench/v1/gateway-consistency/task-pack
  -> WorkbenchPlatformClient.fetch_gateway_consistency_task_pack()
  -> WorkbenchGatewayConsistencyApi.gateway_consistency_task_pack()
  -> GET /api/gateway-consistency/task-pack
  -> Gateway Consistency UI and batch creation
```

Workbench batch creation is local. Platform task pack data is the source for allowed models, cases, defaults, and baseline references.

## Failure Behavior

- Platform not configured: local API returns `platform_configured: false`.
- Session missing or expired: Workbench returns an account/session error and does not expose the task pack as runnable.
- Task pack unavailable: Workbench surfaces the platform error.
- Invalid task pack schema: Workbench reports `gateway_consistency_task_pack_invalid_payload`.
- Case workspace not ready: Workbench may list the case but blocks batch creation until workspace readiness is satisfied.

## Required Tests

Producer tests in the Website repository:

- `GET /api/workbench/v1/gateway-consistency/task-pack` validates the task pack and embedded baselines.

Consumer tests in the Workbench repository:

- `GET /api/gateway-consistency/task-pack` handles platform-not-configured and valid platform payloads.
- Batch creation rejects task packs with unsupported executor/model/case readiness.

