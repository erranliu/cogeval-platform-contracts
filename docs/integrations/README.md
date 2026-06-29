# COGEval 集成契约索引

本目录说明平台契约如何通过具体 API 被生产者提供、被消费者读取并投影到产品行为。它补充 schema 文档，不替代 JSON Schema、Pydantic 模型或 fixture。

## 原则

- schema 文档回答 payload 长什么样、字段如何约束。
- 集成契约回答哪个系统通过哪个 API 提供 payload、消费者从哪里读取、失败时如何处理。
- 中台和 Workbench 不应在各自仓库重复定义同一 API path、认证规则或必填字段；应引用本目录文档。
- 每个 Workbench 消费的中台契约都应有对应集成契约文档和生产者/消费者测试清单。

## 集成契约

| 集成契约 | 数据 schema | 生产者 API | 消费者入口 | 文档 |
|---|---|---|---|---|
| Workbench Model Capability Catalog v2 | `cogeval.model_capability_catalog.v2` | `GET /api/workbench/v1/model-capabilities` | Workbench execution selection catalog | [workbench-model-capability-catalog-v2.md](workbench-model-capability-catalog-v2.md) |

## 新增集成契约流程

1. 先确认数据 schema 已在 `docs/契约.md` 和对应 schema 文档中登记。
2. 复制 [TEMPLATE.md](TEMPLATE.md) 创建新的集成契约文档。
3. 写清生产者 API、认证、返回 envelope、消费者 loader、配置覆盖项、失败行为和测试清单。
4. 在本索引登记新文档。
5. 在生产者仓和消费者仓添加测试，证明实际 API 与消费投影符合本集成契约。

