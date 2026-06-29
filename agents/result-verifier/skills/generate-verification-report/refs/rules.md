# generate-verification-report 详细规则

## 1. Markdown 报告自包含

Markdown 报告必须自包含，不依赖外部资源。所有表格、数据、结论均在报告内展示，无需跳转外部链接。

## 2. 不一致标记

不一致行用加粗 + 标记突出显示：
```markdown
| id | 旧表=202 | 热表=203 | ❌ **不一致** |
```

## 3. JSON Schema 稳定性

JSON 报告供 Result Analyst 程序化消费，已有 schema 结构需保持稳定：
- `summary` 统计维度不变
- `cases[]` 数组元素结构不变
- `mismatch_details[]` 和 `unverifiable_details[]` 字段名不变

## 4. 产出目录

两类文件均写入 `memory/test_results/verification/` 目录。若目录不存在则创建。

## 5. 移交建议

若汇总统计中 `mismatch_found > 0`，报告末尾列出建议：移交 Result Analyst 进行根因分析。

## 6. 统计维度定义

| 统计维度 | 说明 |
|---------|------|
| `total_cases` | 涉及校验的 case 总数 |
| `total_checks` | 全部校验项数（db_existence + field_compare + log_keyword） |
| `by_type` | 按 db_existence / field_compare / log_keyword 分类计数 |
| `by_status` | 按 verified_consistent / mismatch_found / cannot_verify 分类计数 |
| `case_verdicts` | 按 case 级别汇总：all_verified / mismatch_found / partially_verified / fully_unverifiable |
