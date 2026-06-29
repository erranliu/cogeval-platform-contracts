# COGEval 集成契约索引

本目录说明平台契约如何通过具体 API 被生产者提供、被消费者读取并投影到产品行为。它补充 schema 文档，不替代 JSON Schema、Pydantic 模型或 fixture。

## 原则

- schema 文档回答 payload 长什么样、字段如何约束。
- 集成契约回答哪个系统通过哪个 API 提供 payload、消费者从哪里读取、失败时如何处理。
- 中台和 Workbench 不应在各自仓库重复定义同一 API path、认证规则或必填字段；应引用本目录文档。
- 每个 Workbench 消费的中台契约都应有对应集成契约文档和生产者/消费者测试清单。

## 集成契约

| 集成契约 | 数据 schema | 数据方向 | 平台 API | Workbench 入口 | 文档 |
|---|---|---|---|---|---|
| Workbench COG Cases v1 | `cogeval.cog_case.v1`, `cogeval.cog_case_group.v1` | 中台 -> Workbench | `GET /api/public/cog-cases` | COG Cases local API | [workbench-cog-cases-v1.md](workbench-cog-cases-v1.md) |
| Workbench API Key Provider Catalog v1 | `cogeval.interface_capability_catalog.v1` | 中台 -> Workbench | `GET /api/workbench/v1/api-key-providers` | provider catalog loader | [workbench-api-key-provider-catalog-v1.md](workbench-api-key-provider-catalog-v1.md) |
| Workbench Provider Capability Catalog v1 | `cogeval.provider_capability_catalog.v1` | 中台 -> Workbench | bundled or configured capability catalog path | provider catalog loader | [workbench-provider-capability-catalog-v1.md](workbench-provider-capability-catalog-v1.md) |
| Workbench Model Capability Catalog v2 | `cogeval.model_capability_catalog.v2` | 中台 -> Workbench | `GET /api/workbench/v1/model-capabilities` | execution selection catalog | [workbench-model-capability-catalog-v2.md](workbench-model-capability-catalog-v2.md) |
| Workbench Gateway Consistency v1 | `cogeval.gateway_consistency.task_pack.v1` | 中台 -> Workbench | `GET /api/workbench/v1/gateway-consistency/task-pack` | Gateway Consistency local API | [workbench-gateway-consistency-v1.md](workbench-gateway-consistency-v1.md) |
| Workbench Accounts v1 | `cogeval.workbench.*.v1` | 双向 | `/api/workbench/v1/auth/github`, `/me`, `/assets`, `/coin-reservations` | platform account client | [workbench-accounts-v1.md](workbench-accounts-v1.md) |
| Workbench Self-run Package Ingest v1 | `cogeval.self_run_*`, `cogeval.evidence_bundle.v1`, `cogeval.package_import_result.v1` | Workbench -> 中台，导入结果返回 Workbench | `POST /api/workbench/v1/ingest/package` | test result submit flow | [workbench-self-run-package-ingest-v1.md](workbench-self-run-package-ingest-v1.md) |
| Workbench Distribution Claims v1 | `cogeval.distribution_claim*.v1` | Workbench 请求，中台返回 claim | `/api/tasks/claim`, `/api/tasks/{claim_id}/start`, `/release` | task claim client | [workbench-distribution-claims-v1.md](workbench-distribution-claims-v1.md) |

## 新增集成契约流程

1. 先确认数据 schema 已在 `docs/契约.md` 和对应 schema 文档中登记。
2. 复制 [TEMPLATE.md](TEMPLATE.md) 创建新的集成契约文档。
3. 写清生产者 API、认证、返回 envelope、消费者 loader、配置覆盖项、失败行为和测试清单。
4. 在本索引登记新文档。
5. 在生产者仓和消费者仓添加测试，证明实际 API 与消费投影符合本集成契约。
