---
name: assemble-params
description: 根据执行计划的参数占位符，按优先级组装实际请求参数（随机数据/DB查询/常量替换/rules匹配）
argument-hint: "<execution_plan_path> [env]"
---

# assemble-params

将执行计划中的参数占位符替换为实际值，产出可直接发送的请求体。

## 硬性约束

1. **规则优先级**：渠道规则 > 通用规则（字段冲突时渠道规则优先）
2. **保留占位符标记 incomplete**，供用户确认

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON |
| env | string | 否 | 默认 STG1 |
| user_params | object | 否 | 用户显式指定的参数值 |

## 执行步骤

1. **加载规则** — 先 `common_rules.md`，再 `{channel}.md`，字段冲突渠道优先
2. **按优先级填充** — 用户指定 → 渠道规则 → 随机生成 → 保留占位符
3. **组装请求体** — invokeFacade 格式：`{ env, service_name, method_name, content: {...} }`
4. **DB 查询参数** — 按渠道规则从 DB 获取 account_id，同 case 内复用

## 输出

```json
{ "cases": [{ "case_name": "...", "steps": [{ "request_body": {...}, "param_sources": {...} }] }], "incomplete_params": [] }
```

## 关键规则

1. 随机生成的数据在日志中记录
2. DB 获取的 account_id 在同一 case 内复用
3. 渠道规则路径：`memory/api_channels_rules/{channel}.md`

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 输入/输出 Schema → [refs/io.md](refs/io.md)
