# Workbench Accounts v1

Workbench Accounts 契约定义 Workbench 与中台之间的 GitHub 登录初始化、账号资产读取和 Eval Coins 预留 payload。

## 范围

本契约定义：

- Workbench 向中台提交 GitHub access token 的请求形状。
- 中台返回账号、GitHub 身份、资产和 session 的响应形状。
- Workbench 拉取资产状态的响应形状。
- Workbench 创建或跟踪 Eval Coins 预留的响应形状。

本契约不定义：

- GitHub Device Flow 本身。
- 中台 session token 的签名算法。
- 资产账本内部表结构。
- 支付购买 Eval Coins 的流程。

## Schemas

| schema | 说明 | 模型 |
|---|---|---|
| `cogeval.workbench.auth_github_request.v1` | GitHub 登录请求 | `WorkbenchAuthGithubRequest` |
| `cogeval.workbench.auth_github_response.v1` | GitHub 登录响应 | `WorkbenchAuthGithubResponse` |
| `cogeval.workbench.account_assets.v1` | 资产状态 | `WorkbenchAccountAssets` |
| `cogeval.workbench.coin_reservation.v1` | Eval Coins 预留 | `WorkbenchCoinReservation` |

对应机器文件位于：

- `src/cogeval_platform_contracts/workbench_accounts/v1.py`
- `src/cogeval_platform_contracts/workbench_accounts/schemas/`
- `src/cogeval_platform_contracts/workbench_accounts/fixtures/`

## 生产者与消费者

Workbench 是 `auth_github_request` 的生产者，中台 Workbench API 是消费者。

中台 Workbench API 是 `auth_github_response`、`account_assets` 和 `coin_reservation` 的生产者，Workbench 是消费者。

## GitHub 登录请求

`WorkbenchAuthGithubRequest` 必须携带：

- `schema`: 固定为 `cogeval.workbench.auth_github_request.v1`。
- `github_access_token`: Workbench 通过 GitHub Device Flow 获得的 token。

可选字段：

- `workbench_device_id`: Workbench 本地设备或安装标识。
- `workbench_version`: Workbench 版本。
- `client_time`: 客户端时间。

## GitHub 登录响应

`WorkbenchAuthGithubResponse` 必须携带：

- `schema`: 固定为 `cogeval.workbench.auth_github_response.v1`。
- `account`: 中台账号。
- `github_identity`: 中台校验后的 GitHub 身份。
- `assets`: 账号资产。
- `session`: Workbench 后续访问中台 API 的 session。

账号身份原则：

- 中台账号外部身份键使用 GitHub `id`，不是 `login` 或 email。
- `github_login` 只用于展示和搜索辅助。
- email 可以为空，不作为唯一身份键。

## 资产状态

`WorkbenchAssets` 包含：

- `eval_score`: 累计贡献积分，只能由中台认可后增加。
- `eval_coins`: 可消耗虚拟币余额。
- `ledger_version`: 账本版本。
- `updated_at`: 资产更新时间。

`WorkbenchAccountAssets` 包含：

- `schema`: 固定为 `cogeval.workbench.account_assets.v1`。
- `assets`: 当前资产状态。
- `ledger_entries`: 可选账本变更明细。

Workbench 可以缓存资产用于展示，但需要权威判断时必须以中台返回值为准。

## Eval Coins 预留

`WorkbenchCoinReservation` 用于创建、确认、取消或展示虚拟币预留状态。字段包括：

- `schema`: 固定为 `cogeval.workbench.coin_reservation.v1`。
- `reservation_id`: 预留标识。
- `status`: 预留状态。
- `amount`: 金额，必须大于等于 `0`。
- `action`: 业务动作。
- `subject`: 业务对象。
- `client_context`: 客户端上下文。
- `expires_at`: 过期时间。
- `assets`: 预留后的资产快照。
- `ledger_entry`: 对应账本记录。

Workbench 不应直接提交“把余额改成 X”的请求，只能提交可审计业务事件或预留请求。

## 与 self-run package 的关系

登录后的普通 Workbench 用户提交 self-run package 时，应使用当前 session 绑定账号。package 结构仍由 [SELF_RUN_PACKAGES_V1.md](SELF_RUN_PACKAGES_V1.md) 定义。

## 兼容策略

- `account.status`、`coin_reservation.status` 当前是字符串，业务状态集合由中台流程约束；如需跨仓强枚举，应发布新版本或补充兼容策略。
- `ledger_entries`、`subject`、`client_context`、`ledger_entry` 是扩展面，消费者必须忽略未知键。
- 顶层新增字段需确认消费者处理策略；当前模型 `extra = forbid`，跨仓新增字段通常应走新 schema 版本。
