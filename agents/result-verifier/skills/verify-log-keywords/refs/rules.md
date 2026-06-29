# verify-log-keywords 详细规则

## 1. 日志查询主搜索键

必须使用 case 的标识数据（repay_order_id / repay_tran_no）作为主搜索键，不能仅用关键字直接搜索（会返回大量无关日志）。

## 2. negative_check 的特殊处理

对于 `negative_check`：若主关键字本身未在日志中找到，标记为 `cannot_verify`。原因：无法在找不到上下文的日志中证明一个否定论断。

## 3. 查询失败处理

若 `testmind:query-log` 对该 case 的所有查询均无结果，该 case 的所有日志校验标记为 `cannot_verify`。

## 4. 日志上下文

关键字匹配应包含日志行上下文（前后各 1 行），用于报告中展示证据。

## 5. 时间窗口

默认取 case 执行时间 ±5 分钟。若从 plan 中无法获取，使用当天的宽时间窗口。

## 6. 应用和日志级别

- app: 从 `log_verification.app` 获取
- 默认查 INFO + ERROR 级别日志
