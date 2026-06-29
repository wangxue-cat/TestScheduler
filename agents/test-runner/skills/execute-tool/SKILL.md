---
name: execute-tool
description: 小工具统一执行入口，根据工具名从 catalog 查找定义，读取 token 后执行 HTTP 调用
argument-hint: "<工具名|功能描述> [参数...] [环境]"
---

# execute-tool

小工具统一执行入口。本项目**所有小工具调用必须通过此 skill**，不直接使用 `testmind:common_tool_execute` 或裸 HTTP 请求。

## 硬性约束

1. **强制统一入口** — TestScheduler 项目所有小工具调用必须通过本 skill，禁止绕过
2. **先查 catalog 再调用** — 不确定工具参数时先查 `innovate_tools_api_catalog.md`

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 工具名/功能描述 | string | 是 | 工具名称或功能描述 |
| 工具参数 | object | 否 | key=value 或自然语言描述 |
| env | string | 否 | 默认 STG2 |

## 执行步骤

1. **读取 Token** — 从 `memory/innovate_tools_api/token.txt`
2. **匹配工具** — 在 catalog 中按名称/描述匹配
3. **组装请求** — URL + headers(token) + body(参数+env)
4. **执行调用** — Python HTTP 请求，超时 30s
5. **返回结果** — 解析响应并返回

## 输出

```json
{ "tool": "...", "env": "STG2", "request": {...}, "response": {...}, "status": "success" }
```

## 关键规则

1. Token 从 `d:\TestScheduler\memory\innovate_tools_api\token.txt` 读取
2. 默认环境 STG2，可通过参数覆盖
3. 请求超时 30s

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 工具速查表 → [refs/tools.md](refs/tools.md)
