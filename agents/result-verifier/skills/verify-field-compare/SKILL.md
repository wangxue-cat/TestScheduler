---
name: verify-field-compare
description: 跨表字段比对：处理 db_check.compare、check.compare_fields(all_equal)、compare_api_response_with_db 指令
argument-hint: "<execution_plan_path> <captured_data> [execution_results_path] [env]"
---

# verify-field-compare

处理执行计划中三类字段比对指令，逐字段验证数据一致性。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON 文件路径 |
| captured_data | object | 是 | verify-db-exists 产出的 captured_fields 数据 |
| execution_results_path | string | 否 | 执行结果缓存 |
| env | string | 否 | 默认取 plan 中的 env 字段 |

## 执行阶段

- **Phase A**: 跨步骤单字段比对 (db_check.compare)
- **Phase B**: 多表多字段全量比对 (check.compare_fields + all_equal)
- **Phase C**: API 响应 vs DB 一致性 (compare_api_response_with_db)

## 输出

`memory/test_results/verification/` 下的 field_comparisons JSON。

## 关键规则

1. compare_fields 少于实际字段时，查询全部列做完整比对
2. NULL 与空字符串视为等价
3. date_updated 类时间戳允许 ±2 秒偏差
4. 严重等级：critical(id不一致) > major(业务字段) > minor(时间戳偏差)

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 输入/输出 Schema → [refs/io.md](refs/io.md)
