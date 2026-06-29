---
name: analyze-failure
description: 分析执行失败用例，结合日志+响应+预期值定位根因，输出置信度评分
argument-hint: "<execution_results_path> <logs_path>"
---

# analyze-failure

对失败的测试用例进行根因分析，输出结构化的失败分析报告，为提 Bug 和出报告提供依据。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_results | object/string | 是 | 执行结果 JSON 或文件路径 |
| logs | object/string | 是 | collect-execution-logs 的产出 |
| requirement_json | object | 否 | 需求详情 |

## 执行步骤

1. **筛选失败用例** — 提取 status=failed 的 case 和 step
2. **逐步骤分析** — 响应码分析 + 字段值比对 + 日志关联 + io_bindings 链路追踪
3. **根因分类** — test_data / param_assembly / api_logic / env_issue / downstream / unknown
4. **生成 Bug 草稿** — api_logic 和 param_assembly 类别生成 Bug 草稿

## 输出

```json
{ "failures": [{ "root_cause": "...", "category": "api_logic", "confidence": "high", "bug_draft": {...} }], "summary": {...} }
```

## 关键规则

1. 根因分析必须有证据支撑
2. test_data 和 env_issue 类别不提 Bug
3. 每个失败最多一个 Bug 草稿

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
