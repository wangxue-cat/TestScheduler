---
name: verify-log-keywords
description: 日志关键字验证：处理 check.keyword(found)、check.negative_check、check.sub_check、post_check 指令
argument-hint: "<execution_plan_path> [execution_results_path] [env]"
---

# verify-log-keywords

处理执行计划中所有日志相关的校验指令，通过 `testmind:query-log` 确认关键字存在/不存在。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON 文件路径 |
| execution_results_path | string | 否 | 执行结果缓存（含 trace_id、req_no、时间戳） |
| env | string | 否 | 默认取 plan 中的 env 字段 |

## 执行步骤

1. **收集校验指令** — 扫描执行计划中三类指令：check 步骤关键字、post_check、计划级 log_verification
2. **确定查询参数** — 提取标识数据（repay_order_id/repay_tran_no）+ 关键字 + 时间窗口 ±5分钟
3. **执行日志查询** — 通过 `testmind:query-log` 做正向/反向验证
4. **分类结果** — verified_consistent / mismatch / cannot_verify

## 输出

`memory/test_results/verification/` 下的 log_verifications JSON。

## 关键规则

1. 日志查询必须使用 case 的标识数据作为主搜索键
2. negative_check 若主关键字未找到 → 标记 `cannot_verify`
3. 关键字匹配含日志行上下文（前后各1行）

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 输入/输出 Schema → [refs/io.md](refs/io.md)
