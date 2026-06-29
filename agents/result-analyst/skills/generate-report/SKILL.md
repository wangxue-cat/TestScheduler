---
name: generate-report
description: 生成测试报告（Markdown详细报告 + HTML可视化报告）
argument-hint: "<execution_results_path> [failure_analysis_path]"
---

# generate-report

根据执行结果和失败分析，生成 Markdown 和 HTML 两种格式的测试报告。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_results | object/string | 是 | 执行结果 JSON |
| failure_analysis | object/string | 否 | 失败分析 |
| requirement_id | string | 是 | 需求编号 |

## 执行步骤

1. **统计汇总** — 总数/通过/失败/通过率，按优先级和接口维度统计
2. **生成 Markdown 报告** → `memory/test_results/reports/{req_id}_execution_report.md`
3. **生成 HTML 报告** — 调用 `testmind:test-report` → `memory/test_results/reports/{req_id}_execution_report.html`

## 输出

```json
{ "report_paths": { "markdown": "...", "html": "..." }, "summary": { "total": 5, "passed": 4, "pass_rate": "80%" } }
```

## 关键规则

1. 报告必须生成到 `memory/test_results/reports/`
2. 失败用例必须展示完整请求体和响应体
3. HTML 报告必须自包含（无外部依赖）

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
