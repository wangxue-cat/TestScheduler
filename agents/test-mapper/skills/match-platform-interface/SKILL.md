---
name: match-platform-interface
description: 通过testmind:auto-interface-list从平台接口列表中匹配每个用例步骤对应的平台接口method
argument-hint: "<case_steps_json> <channel>"
---

# match-platform-interface

将用例步骤文本匹配到自动化平台的具体接口 method。

## 硬性约束

1. **只从平台接口列表匹配**（`testmind:auto-interface-list`），不凭空编造
2. **禁从本地 `memory/api_channels/` 匹配** — 该目录不再维护
3. 无匹配 → 标记 unmatched + 告知用户，不跳过

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| case_steps | object | 是 | parse-case-steps 的输出 |
| channel | string | 是 | 渠道标识 |

## 执行步骤

1. **获取平台接口列表** — `testmind:auto-interface-list` 按渠道搜索
2. **三级匹配** — 精确匹配(name) → method 匹配 → 语义匹配
3. **标记结果** — confidence(high/medium/low) + platform_id + platform_name
4. **查询平台用例** — `testmind:auto-testcase-list` 检查可复用用例

## 输出

```json
{ "matched_cases": [{ "platform_id": 21203, "confidence": "high", ... }], "unmatched_steps": [] }
```

## 关键规则

1. 多个候选时选 confidence 最高的
2. 匹配结果供 generate-execution-plan 使用

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
