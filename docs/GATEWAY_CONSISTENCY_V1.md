# Gateway Consistency v1

Gateway Consistency 契约定义中台向 Workbench 下发的网关一致性任务包。中台选择已有结果作为基线矩阵，Workbench 选择模型并按任务包运行。

## 范围

本契约定义：

- 单个 case 的基线原始数据容器。
- Workbench 可消费的任务包快照。
- 任务包内模型、case、执行默认值和基线引用的最小结构。

本契约不定义：

- ops-console 选择 TestResult 的页面 DTO。
- 中台构建矩阵的内部校验错误响应。
- Workbench 的网关 API key 处理。
- 一致性评分或可靠性结论。

## Schemas

| schema | 说明 | 模型 |
|---|---|---|
| `cogeval.gateway_consistency.baseline.v1` | 单个 case 的基线容器 | `GatewayConsistencyBaseline` |
| `cogeval.gateway_consistency.task_pack.v1` | Workbench 任务包 | `GatewayConsistencyTaskPack` |

对应机器文件位于：

- `src/cogeval_platform_contracts/gateway_consistency/v1.py`
- `src/cogeval_platform_contracts/gateway_consistency/schemas/`
- `src/cogeval_platform_contracts/gateway_consistency/fixtures/`

## 生产者与消费者

中台是 `gateway_consistency.task_pack` 和 `gateway_consistency.baseline` 的生产者。Workbench 是消费者。

中台应在保存和返回任务包前校验 payload。Workbench 应在执行前校验收到的任务包。

## 基线

`GatewayConsistencyBaseline` 必须携带：

- `schema`: 固定为 `cogeval.gateway_consistency.baseline.v1`。
- `source`: 基线来源描述。
- `raw`: 原始基线数据。

约束：

- `raw.reference_results_by_model` 必须存在。

`raw` 是保留原始平台参考结果的容器。Workbench 可以读取所选模型对应的参考结果，但不应假设 `raw` 中所有键都稳定为执行输入。

## 任务包

`GatewayConsistencyTaskPack` 必须携带：

- `schema`: 固定为 `cogeval.gateway_consistency.task_pack.v1`。
- `task_pack_id`: 外部任务包标识。
- `display_name`: 展示名称。
- `updated_at`: 快照更新时间。
- `executor`: 执行器要求。
- `defaults`: 默认运行参数。
- `models`: Workbench 可选模型。
- `cases`: 要运行的 case 列表。

约束：

- `models` 至少包含一项。
- `cases` 至少包含一项。
- `defaults.repeat_count`、`defaults.timeout_seconds` 必须大于等于 `1`。
- `defaults.cost_limit` 必须大于等于 `0`。

## 模型与 case

每个模型项包含：

- `model_option_id`: 任务包内稳定选项 ID。
- `display_name`: 展示名称。
- `model_name`: Workbench 实际执行时使用的模型名。

每个 case 项包含：

- `task_case_id`: 任务包内 case ID。
- `source_id`: 中台来源 ID。
- `external_id`: 来源内题目标识。
- `title`: 展示标题。
- `baseline`: 该 case 的基线容器。
- `metadata`: 扩展元数据。

Workbench 选择一个 `model_option_id` 后，对任务包内所有 `cases` 执行。对应基线一般从 `case.baseline.raw.reference_results_by_model[model_option_id]` 读取。

## 兼容策略

- `raw` 和 `metadata` 是扩展面，消费者必须忽略未知键。
- 顶层结构、`models`、`cases`、`defaults` 的字段变更需要 schema 版本管理。
- `executor.required` 的语义变更会影响 Workbench 调度，应走兼容性评审。
