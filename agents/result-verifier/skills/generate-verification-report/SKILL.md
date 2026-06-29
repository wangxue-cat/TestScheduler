---
name: generate-verification-report
description: 汇总验证结果生成结构化报告：产出 JSON（供 Result Analyst 消费）+ Markdown（人类可读）
argument-hint: "<db_existence_results> <field_compare_results> <log_keyword_results> <execution_plan_path> <requirement_id>"
---

# generate-verification-report

聚合 verify-db-exists、verify-field-compare、verify-log-keywords 三个 skill 的产出，生成统一的验证报告。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| db_existence_results | object | 是 | verify-db-exists 的产出 |
| field_compare_results | object | 是 | verify-field-compare 的产出 |
| log_keyword_results | object | 是 | verify-log-keywords 的产出 |
| execution_plan_path | string | 是 | 原始执行计划 |
| requirement_id | string | 是 | 需求 ID |

## 执行步骤

1. **合并结果集** — 按 `case_name` 合并三个 skill 产出，从执行计划补充 `priority`、`tags`、`summary`
2. **计算汇总统计** — total_cases / total_checks / by_type / by_status / case_verdicts
3. **生成 JSON 报告** → `memory/test_results/verification/{req_id}_verification_report.json`
4. **生成 Markdown 报告** → `memory/test_results/verification/{req_id}_verification_report.md`

## 输出

- `memory/test_results/verification/{req_id}_verification_report.json` — 机器可读
- `memory/test_results/verification/{req_id}_verification_report.md` — 人类可读

## 关键规则

1. Markdown 报告必须自包含，不依赖外部资源
2. 不一致行用加粗标记突出显示
3. `mismatch_found > 0` 时，报告末尾建议移交 Result Analyst

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 输入/输出 Schema → [refs/io.md](refs/io.md)  
> 📁 Markdown 报告模板 → [templates/report.md](templates/report.md)
