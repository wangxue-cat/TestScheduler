---
name: execute-tool
description: 小工具统一执行入口，根据工具名从 catalog 查找定义，组装参数后通过 Skill(testmind:common-tool-execute) 执行（QOA 追踪）
argument-hint: "<工具名|功能描述> [参数...] [环境]"
---

# execute-tool

小工具统一执行入口。本项目**所有小工具调用必须通过此 skill**。

## 硬性约束

1. **强制统一入口** — TestScheduler 项目所有小工具调用必须通过本 skill
2. **Phase B 必须走 Skill** — 执行阶段必须通过 `Skill(testmind:common-tool-execute)`，确保 QOA 追踪
3. **先查 catalog 再调用** — 不确定工具参数时先查 `innovate_tools_api_catalog.md`

## 执行流程（新架构）

```
用户需求 → Phase A: 本地解析 → Phase B: Skill执行(QOA追踪)
```

### Phase A: 本地解析

1. **读取 Token** — 从 `memory/innovate_tools_api/token.txt`
2. **匹配工具** — 在 catalog 中按名称/描述匹配
3. **组装参数** — 根据 catalog 定义的工具参数 + env

### Phase B: 执行

调用 `Skill(testmind:common-tool-execute, "{工具名} {参数} {env}")`

> 🚫 **禁止**：直接裸 HTTP 请求、直接调 `urllib.request`、绕过 Skill 执行。
> 所有执行必须通过 `Skill(testmind:common-tool-execute)` 以确保 QOA 平台的 `testmind:schedule` 追踪。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 工具名/功能描述 | string | 是 | 工具名称或功能描述 |
| 工具参数 | object | 否 | key=value 或自然语言描述 |
| env | string | 否 | 默认 STG2 |

## 输出

```json
{ "tool": "...", "env": "STG2", "request": {...}, "response": {...}, "status": "success" }
```

## 关键规则

1. Token 从 `d:\TestScheduler\memory\innovate_tools_api\token.txt` 读取
2. 默认环境 STG2，可通过参数覆盖
3. 执行必须走 `Skill(testmind:common-tool-execute)`

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 工具速查表 → [refs/tools.md](refs/tools.md)
