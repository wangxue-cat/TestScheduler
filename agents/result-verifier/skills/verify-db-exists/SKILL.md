---
name: verify-db-exists
description: 验证 DB 存在性检查：处理 db_check.expect(exists/not_exists)、capture_fields、wait_seconds 指令
argument-hint: "<execution_plan_path> [execution_results_path] [env]"
---

# verify-db-exists

处理执行计划中所有 `type: "db"` 步骤的 `db_check` 指令，确认数据库记录存在/不存在是否符合预期，并捕获关键字段值供后续比对使用。

## 硬性约束

1. **DB 路由必须经过 `db_info_processed.json`**，不可猜测库名
2. **占位符解析失败必须明确报告**：哪个占位符、为何无法解析

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON |
| execution_results_path | string | 否 | 执行结果缓存，用于解析占位符 |
| env | string | 否 | 默认取 plan 中的 env |

## 执行步骤

1. **解析执行计划** — 提取所有 `type: "db"` 步骤的 db_check 指令
2. **解析占位符** — execution_results → plan param_placeholders → DB 兜底查询
3. **数据库路由** — `subsystem + database` → `db_info_processed.json` → `db_name`
4. **执行存在性查询** — exists/not_exists + capture_fields + wait_seconds 等待
5. **输出结构化结果** — 按 case_name 分组，包含 captured_fields 供 verify-field-compare 使用

## 输出

`memory/test_results/verification/` 下的 db_existence_checks JSON。

## 关键规则

1. OB 异步写入场景：`wait_seconds` 后重试一次，若仍无数据标记 `mismatch`
2. not_exists 检查：至少成功查询一个相关表且无数据 → `verified_consistent`
3. captured_fields 存入全局捕获存储

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 输入/输出 Schema → [refs/io.md](refs/io.md)
