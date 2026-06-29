---
name: generate-execution-plan
description: 将接口匹配结果组装为完整的可执行计划JSON，含io_bindings依赖链和参数占位符
argument-hint: "<matched_cases_json> <requirement_id>"
---

# generate-execution-plan

将 match-platform-interface 的匹配结果转换为 Test Runner 可直接消费的执行计划 JSON。

## 硬性约束

1. **`platform_id` 必须透传** — 从匹配结果中原样写入每个步骤，供 execute-plan 按 ID 执行

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| matched_cases | object | 是 | match-platform-interface 的输出 |
| requirement_id | string | 是 | 需求编号 |
| channel | string | 是 | 渠道标识 |

## 执行步骤

1. **读取平台接口定义** — platform_id / method / appId / params 模板 / facade 类名
2. **解析 io_bindings 依赖链** — 构建 from_method → field 依赖图，验证依赖完整
3. **提取参数占位符** — 区分 io_bindings 可填充 vs 需外部提供
4. **组装执行计划** → `memory/execution_plans/{req_id}_plan.json`

## 输出

写入 `memory/execution_plans/{requirement_id}_plan.json`

## 关键规则

1. io_bindings 缺失的依赖标记 `pending_data`，不阻塞生成
2. 外部参数在 assemble-params 阶段填充
3. 写入前验证 JSON schema 完整性

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
