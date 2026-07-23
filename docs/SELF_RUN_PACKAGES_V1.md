# Self-run Packages v1

Self-run package 是 Workbench 向中台提交真实跑测结果的跨项目契约。它覆盖包清单、单条结果记录、证据包，以及中台导入后的逐条处理结果。

## 范围

本契约定义：

- Workbench 生成的包级清单。
- Workbench 生成的每条 self-run 结果记录。
- 每条结果可引用的证据包最小形状。
- 中台 ingest 后返回的导入摘要。

本契约不定义：

- 证据文件的对象存储位置。
- 中台对外鉴权策略。
- 运营复核队列的内部表结构。

## Schemas

| schema | 说明 | 模型 |
|---|---|---|
| `cogeval.self_run_package_manifest.v1` | 包级元信息 | `SelfRunPackageManifest` |
| `cogeval.self_run_record.v1` | 单条结果记录 | `SelfRunRecord` |
| `cogeval.evidence_bundle.v1` | 证据包 | `EvidenceBundle` |
| `cogeval.package_import_result.v2` | 导入响应 | `PackageImportResultV2` |

对应机器文件位于：

- `src/cogeval_platform_contracts/self_run_packages/v1.py`
- `src/cogeval_platform_contracts/self_run_packages/schemas/`
- `src/cogeval_platform_contracts/self_run_packages/fixtures/`

## 生产者与消费者

Workbench 是 `self_run_package_manifest`、`self_run_record` 和 `evidence_bundle` 的生产者。中台 ingest 是消费者。

中台 ingest 是 `package_import_result` 的生产者。Workbench、运营工具或联调脚本是消费者。

## 包清单

`SelfRunPackageManifest` 必须携带：

- `schema`: 固定为 `cogeval.self_run_package_manifest.v1`。
- `schema_version`: 兼容旧导出流程的版本字段，不替代 `schema`。
- `package_id`: 包唯一标识。
- `created_at`: 包生成时间。
- `target_source_id`: 结果目标来源。

可选字段：

- `submitter`: 旧提交者标识。
- `submitted_by_account_id`: 登录 Workbench 用户账号。
- `metadata`: 扩展元数据。

## 结果记录

`SelfRunRecord` 必须携带：

- `schema`: 固定为 `cogeval.self_run_record.v1`。
- `external_case_ref`: 中台下发的 case 外部标识原样回填。
- `agent`、`model`: 运行主体和模型。
- `outcome`: `resolved`、`unresolved`、`error` 或 `mixed`。
- `pass_rate`: `0..1`。
- `repeat_count`: 重复次数。
- `runs`: 单次运行明细。

约束：

- `repeat_count` 必须等于 `runs.length`。
- `runs[].run_index` 必须从 `0` 开始连续递增。
- `runs[].outcome` 只能是 `resolved`、`unresolved` 或 `error`。

## 证据包

`EvidenceBundle` 必须携带：

- `schema`: 固定为 `cogeval.evidence_bundle.v1`。
- `test_execution_result`: 测试执行结果。当前验证要求该字段存在。

可选字段：

- `trajectory`: 运行轨迹或日志引用。
- `final_diff`: 最终代码差异或补丁引用。

证据包用于中台验证和人工复核。它不要求把大体积日志直接塞入 payload，可以放引用，但引用必须让复核流程可达。

## 导入结果

`PackageImportResult` 必须携带：

- `schema`: 固定为 `cogeval.package_import_result.v2`。
- `snapshot_id`: 导入时生成或使用的中台快照标识。
- `n_accepted`: 接受数量。
- `n_rejected`: 拒绝数量。
- `results`: 每条记录的处理结果。

约束：

- `n_accepted` 必须等于 `results` 中 `accepted = true` 的数量。
- `n_rejected` 必须等于 `results` 中 `accepted = false` 的数量。

每条 `RecordImportResult` 包含 `external_case_ref`、`accepted`、可选 `test_result_id`、`reason_codes`、`queued_for_review` 和 `review_item_id`。

## 身份闭环

Workbench 消费中台下发 case 时，应保存 `(source_id, external_id)`。提交结果时：

- `manifest.target_source_id` 对应中台下发的 `source_id`。
- `record.external_case_ref` 对应中台下发的 `external_id`。

中台据此把结果挂回正确的 COG Case 和 Test Result 记录。

## 兼容策略

- 新字段只能在消费者明确忽略未知字段的前提下添加；当前模型 `extra = forbid`，因此新增字段通常需要新版本。
- `outcome`、`runs[].outcome` 等枚举变更必须走兼容性评审。
- `schema_version` 是旧包结构兼容字段；跨仓契约判断以 `schema` 为准。
