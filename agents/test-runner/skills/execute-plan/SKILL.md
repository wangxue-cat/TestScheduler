---
name: execute-plan
description: 按执行计划逐步骤调用testmind执行接口/用例，缓存响应和校验结果
argument-hint: "<assembled_plan_path>"
---

# execute-plan

按组装好参数的执行计划，通过 testmind skill 逐步骤调用平台接口和用例执行。

## 硬性约束

1. **仅使用 `testmind:auto-interface-exec`**（通过 `platform_id` 执行），不尝试其他方式
2. **小工具统一入口**：必须通过本项目 `execute-tool` skill，禁止绕过
3. **Apollo 修改必须查询确认**：修改超时≠失败，但必须调用 Apollo 查询接口确认当前值已变更为目标值后才能继续跑业务

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| assembled_plan_path | string | 是 | assemble-params 产出的执行计划路径 |
| env | string | 否 | 默认 STG1，首次执行必须用户确认 |

## 执行步骤

1. **环境预检查** — 确认环境 + token + 服务可达性
2. **逐步骤执行** — interface(platform_id) / flow(io_bindings自动传递) / tool(execute-tool) / db(sql-execute)
3. **字段校验** — field型(dot-path提取比对) / db型(标记待Result Analyst校验)
4. **记录结果** — status + request + response + validation + duration_ms
5. **写入缓存** → `memory/test_results/cache/{req_id}_execution_results.json`

## 输出

参考 execution_results.json schema（计划文档 Section 8.3）。

## 关键规则

1. 一个步骤失败不终止整个 case（除非是 io_bindings 上游）
2. 超时设置：接口 30s，DB 10s
3. 执行中不分析失败原因（由 Result Analyst 负责）

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
