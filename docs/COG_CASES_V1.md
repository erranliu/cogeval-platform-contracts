# COG Cases v1

COG Case 是中台向 Workbench、公开网站和分析台暴露的题目消费契约。它把上游原始 Test Case 加工成 COG 系统可选择、可解释、可引用的发布层。

## 范围

本契约定义：

- 单个已发布 COG Case 的跨项目 payload。
- COG Case Group 的跨项目 payload。
- 分组成员与 COG Case 的关系。

本契约不定义：

- 中台内部 Test Case 抓取落地表。
- ops-console 的编辑 DTO。
- LLM 标签生成流程。

## Schemas

| schema | 说明 | 模型 |
|---|---|---|
| `cogeval.cog_case.v1` | 单个 COG Case | `CogCase` |
| `cogeval.cog_case_group.v1` | COG Case 分组 | `CogCaseGroup` |

对应机器文件位于：

- `src/cogeval_platform_contracts/cog_cases/v1.py`
- `src/cogeval_platform_contracts/cog_cases/schemas/`
- `src/cogeval_platform_contracts/cog_cases/fixtures/`

## 生产者与消费者

中台 public/workbench API 是生产者。Workbench、公开网站和分析台是消费者。

消费者只能依赖本契约字段，不应依赖中台内部 ORM、ops-console DTO 或抓取层字段。

## COG Case 字段

`CogCase` 必须携带：

- `schema`: 固定为 `cogeval.cog_case.v1`。
- `test_case_id`: 中台内部题目关联标识。
- `source_id`: 来源标识。
- `external_id`: 来源内题目标识。
- `title`: 展示标题。
- `promoted_at`: 晋升为 COG Case 的时间。

重要可选字段：

- `cog_case_display_id`: v1 中的可选历史字段。当前发布和执行应使用 [COG_CASES_V3.md](COG_CASES_V3.md)，其中该字段是必填的产品身份。
- `original_url`: 原始题目 URL。
- `labels`: COG Case 级标签。
- `semantic_profile`: COG Case 语义加工结果。
- `semantic_version`: 语义加工版本。
- `interpretation`: 面向用户的题目解释。
- `online_at`: 上线时间。

## 身份键

历史 v1 payload 的执行兼容仍以 `source_id + external_id` 定位；当前 Workbench 执行必须使用 v3，并以 `cog_case_display_id` 作为产品身份，source pair 仅作为内部技术坐标。

平台可以提供按 COG Case No. 查询单题的 API，例如 `GET /api/public/cog-cases/lookup?cog_case_no=...`。该 lookup 的输入是人类可读的 `cog_case_display_id`，返回 payload 仍携带 `source_id + external_id` 供历史 v1 消费者使用；当前 v3 消费者以 Display ID 作为产品身份，source pair 仅用于内部执行和结果路由。

## 标签与语义加工

`labels` 和 `semantic_profile` 属于 COG Case 发布层，不代表上游原始事实。消费者必须按前向兼容方式读取：

- 允许新增标签键。
- 未识别标签必须忽略。
- 不应把空缺标签解释为否定事实。
- 需要强依赖的标签应由具体产品流程另行约束。

## COG Case Group

`CogCaseGroup` 是面向主题、评测周期或运营目标的 COG Case 分组。

必须携带：

- `schema`: 固定为 `cogeval.cog_case_group.v1`。
- `group_id`: 稳定不透明 ID。
- `slug`: URL 安全的稳定标识。
- `name`: 展示名称。
- `status`: `draft`、`published` 或 `archived`。
- `visibility`: `internal` 或 `public`。
- `selection_mode`: `manual` 或 `rule_snapshot`。
- `member_count`: 成员数量。
- `members`: 详情读取时的成员列表。
- `created_at`、`updated_at`: 时间戳。

可选字段包括 `description`、`theme_tags` 和 `selection_filters`。

## 分组约束

- 公开 API 只应暴露 `status = published` 且 `visibility = public` 的分组。
- 成员必须引用已有 COG Case。
- 重复添加同一成员应幂等。
- 成员顺序由中台保持稳定。
- `rule_snapshot` 记录生成成员快照时使用的筛选条件，但成员列表不会因规则变化自动更新。
- COG Case 下线或撤回不应自动删除分组成员；公开详情返回时只返回当前仍可公开展示的成员。

## 兼容策略

- 新增字段需确认消费者忽略未知字段；当前模型 `extra = forbid`，跨仓新增字段通常应走新 schema 版本。
- `status`、`visibility`、`selection_mode` 枚举变更必须走兼容性评审。
- `labels` 和 `semantic_profile` 是可扩展对象，新增内部键不构成 schema 字段变更，但仍需保持消费者可忽略。
