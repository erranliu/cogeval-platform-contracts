# Distribution Claims v1

Distribution Claim 是中台向 Workbench 分发官方测试任务的跨项目契约。它覆盖 Workbench 能力上报、任务领取、占用、释放，以及提交结果时与任务上下文的关联。

## 范围

本契约定义：

- Workbench 领取任务时提交的能力与约束。
- 中台分配给 Workbench 的 claim payload。
- claim 与 self-run package 结算之间的关联字段。

本契约不定义：

- ops-console 中 distribution goal 的完整编辑结构。
- 中台内部 subtask 拆分算法。
- 奖励策略和账本内部表结构。

## Schemas

| schema | 说明 | 模型 |
|---|---|---|
| `cogeval.distribution_claim_request.v1` | 领取请求 | `DistributionClaimRequest` |
| `cogeval.distribution_claim.v1` | 领取结果 | `DistributionClaim` |

对应机器文件位于：

- `src/cogeval_platform_contracts/distribution_claims/v1.py`
- `src/cogeval_platform_contracts/distribution_claims/schemas/`
- `src/cogeval_platform_contracts/distribution_claims/fixtures/`

## 生产者与消费者

Workbench 是 `distribution_claim_request` 的生产者，中台任务分发 API 是消费者。

中台任务分发 API 是 `distribution_claim` 的生产者，Workbench 是消费者。

## 领取请求

`DistributionClaimRequest` 必须携带：

- `schema`: 固定为 `cogeval.distribution_claim_request.v1`。

可选字段：

- `workbench_id`: Workbench 实例标识。
- `agents`: Workbench 支持的 agent 能力列表。
- `supported_sources`: Workbench 可运行的来源列表。
- `workspace_readiness`: 本地工作区准备情况。
- `max_minutes`: 期望占用时长，默认 `90`，最小为 `1`。

中台可以根据 agent 能力、source 支持、workspace readiness 和目标优先级决定是否分配任务。

## 领取结果

`DistributionClaim` 必须携带：

- `schema`: 固定为 `cogeval.distribution_claim.v1`。
- `claim_id`: 领取记录标识。
- `goal_id`: 任务目标标识。
- `subtask_id`: 子任务标识。
- `status`: claim 当前状态。
- `case_refs`: 分配的 case 引用列表。
- `claimed_at`: 领取时间。
- `expires_at`: 过期时间。

可选字段：

- `workbench_id`: 领取方实例标识。
- `capability_snapshot`: 中台记录的领取时能力快照。
- `candidate_config`: 候选 agent/model 配置。
- `occupied_at`: start 后的正式占用时间。
- `released_at`: release 后的释放时间。

## 典型流程

1. Workbench 调用任务 claim 接口，提交 `DistributionClaimRequest`。
2. 中台返回 `DistributionClaim`，状态表示已分配但未必已正式占用。
3. Workbench 调用 start 接口后，中台记录 `occupied_at`。
4. Workbench 完成跑测后提交 self-run package，并携带 `claim_id`。
5. 中台验证 package，按 claim 上下文结算 score 或记录复核。
6. Workbench 无法完成时调用 release，中台记录 `released_at` 并释放容量。

## 与 self-run package 的关系

任务结果仍走 [SELF_RUN_PACKAGES_V1.md](SELF_RUN_PACKAGES_V1.md) 定义的包和结果记录。`claim_id` 是任务分发上下文，不替代 `source_id + external_id` 的题目身份闭环。

## 兼容策略

- `status` 当前为字符串，具体状态集合由中台流程约束；如需跨仓强枚举，应发布新版本或补充兼容策略。
- `agents`、`workspace_readiness`、`candidate_config`、`case_refs` 内部对象是扩展面，消费者必须忽略未知键。
- 新增顶层字段需确认消费者处理策略；当前模型 `extra = forbid`，跨仓新增字段通常应走新 schema 版本。
