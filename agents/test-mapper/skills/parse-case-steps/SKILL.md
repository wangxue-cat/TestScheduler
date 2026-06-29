---
name: parse-case-steps
description: 解析测试用例 Excel，提取所有 case 和步骤文本，分类为 interface/flow/tool/db/unknown
argument-hint: "<excel_path>"
---

# parse-case-steps

解析测试用例 Excel 文件，提取每个 case 的名称、优先级、前置条件、步骤文本、预期结果，并将步骤按类型分类。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| excel_path | string | 是 | 用例 Excel 文件路径 |
| requirement_id | string | 否 | 需求编号 |

## 执行步骤

1. **读取 Excel** — openpyxl，验证 14 列结构
2. **提取用例列表** — name, priority, precondition, steps, expected
3. **解析步骤分类** — 6 种类型：interface / flow / tool / db / config / unknown
4. **解析预期结果** — field 型 / db 型 / db_update 型

## 步骤分类表

| 类型 | 匹配模式 | 示例 |
|------|---------|------|
| `interface` | "调用XX接口" | "调用 checkBefore 接口" |
| `flow` | "走XX流程" | "走授信全流程" |
| `tool` | "调用小工具XX" | "调用小工具获取用户信息" |
| `db` | "查询数据库XX" | "查询 aps.order_info" |
| `config` | "修改Apollo/配置" | "修改 Apollo 开关" |
| `unknown` | 无法匹配 | 标记待人工确认 |

## 输出

```json
{ "cases": [{ "name": "...", "steps": [{ "seq": 1, "type": "interface", "raw_text": "..." }] }], "unknown_steps": [] }
```

## 关键规则

1. unknown 步骤不阻塞流程，但需标记供用户确认
2. 步骤编号自动提取（1./2./①/②）
3. 预期结果解析失败标记 `type: "unknown"`

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
