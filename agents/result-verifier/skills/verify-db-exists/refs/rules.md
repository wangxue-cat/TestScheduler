# verify-db-exists 详细规则

## 1. 占位符解析

占位符解析失败必须明确报告：哪个占位符、为何无法解析。

解析优先级：
1. **从 execution_results 解析** — 查找 step 的 `io_bindings_sources`，从执行结果中提取
2. **从执行计划解析** — `param_placeholders` 和 `auto_generated_params`
3. **兜底策略** — 对 repay_tran_no / repay_order_id 等标识字段，结合 account_id 等已知参数，查询 DB 中最近创建记录
4. 若仍无法解析 → `cannot_verify`，reason=`placeholder_unresolvable`

## 2. DB 路由

必须经过 `d:\TestScheduler\memory\db_info_processed.json`，**不可猜测库名**。

常见映射：
- `aps-app` + `aps` → `aps_stg2`
- `apss-ob` → subsystem 直连

若路由缺失 → `cannot_verify`，reason=`db_route_missing`

## 3. captured_fields

`capture_fields` 结果存入全局捕获存储，供 `verify-field-compare` 使用。

## 4. not_exists 判定

若至少成功查询了一个相关表且无数据，即判定 `verified_consistent`。

## 5. OB 异步写入 wait_seconds

指定 `wait_seconds` 时（如 OB 异步写入需等待 3-5 秒），sleep 后再查询。若仍未出现，再等一次后判定：
- 有数据 → `verified_consistent`
- 仍无数据 → `mismatch`

参见 [[ob-async-write-lag]]。

## 6. 执行计划解析

从 `cases[]` 中提取所有 `type == "db"` 步骤的 `db_check` 指令：

- `db_check.subsystem`、`db_check.database`、`db_check.table`
- `db_check.key`（WHERE 条件模板，如 `repay_tran_no = {repay_tran_no}`）
- `db_check.expect`（`exists` / `not_exists`）
- `db_check.capture_fields`（可选）
- `db_check.compare`（可选，跨步骤字段比较指令）
- `db_check.wait_seconds`（可选）
