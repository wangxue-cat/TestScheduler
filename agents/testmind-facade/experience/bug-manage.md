---
name: bug-manage
description: Bug 提交/查询的经验积累
metadata:
  type: experience
  skill: testmind:bug-manage
  version: 1
  evolution_count: 1
  last_updated: 2026-06-25
  sources: []
---

# bug-manage 经验积累

## 核心原则

{{待积累}}

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| {{待积累}} | | |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->
- **2026-06-25**: 主会话绕过门面直接调 Bash 脚本做 bug 状态流转。正确做法：所有 bug-manage 操作（查询/流转/详情）统一走 `Skill(testmind-facade)`，由门面加载经验后再路由。直接调 Bash = 丢失经验上下文 + 违反隔离规则。
- **2026-06-25**: `update --transition-status` 有 bug 已废弃，不要使用。API 返回 flag=S 但实际状态并未流转。正确做法：走 `Skill(testmind:bug-manage)` 的 `batch-transition` 或 `transition` 命令。

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->
