---
name: testmind-facade-gateway-enforcement
description: All testmind skill calls MUST go through testmind-facade — not direct Skill() or Bash
metadata:
  type: feedback
  source: user-correction
  last_updated: 2026-06-25
---

# testmind-facade 门面强制规则

## 规则

**所有 `Skill(testmind:xxx)` 调用必须通过 `Skill(testmind-facade)` 门面，严禁绕过。**

### 禁止行为

- ❌ 直接 `Skill(testmind:bug-manage)` → 必须 `Skill(testmind-facade)` 带着 `bug-manage` 参数
- ❌ 直接 Bash 调用 `bug_manage.py` → 必须走门面
- ❌ 直接 `Skill(testmind:query-log)` → 必须走门面
- ❌ 任何跳过门面的 testmind skill 调用

### 正确做法

1. 主会话调用 `Skill(testmind-facade)` 并描述需要调用哪个 testmind skill
2. 门面自动完成：加载经验 → 解析路由 → 执行 → 观察 → 写回
3. 门面按 skill-registry.md 决定是委托本地 wrapper 还是直调 testmind

## Why

用户多次纠正：主会话直接调用 testmind skill 绕过了门面的经验加载/路由解析/观察写回机制。
即使功能上能成功（如 bug-manage 查询和流转），但破坏了架构隔离和经验积累流程。

## How to apply

- 任何需要 testmind skill 时，第一反应是 `Skill(testmind-facade)`，不是 `Skill(testmind:xxx)`
- CLAUDE.md 已将规则从"先读经验文件"升级为"必须通过门面"
- 违反此规则会导致经验无法积累、路由可能错误（如跳过 sql-execute wrapper）

## 违规记录

- **2026-06-25 #2**: 查询 bug 走了门面（正确），但后续 5 次状态流转全部绕过门面直接调 Bash。用户当场指出。**教训**：一次会话中完成门面 Phase 1-2 后，不能因为"已经知道路由"就跳过门面直接调 Bash——每次独立的 testmind 操作都需要走完整的 5-Phase 门面协议。把经验写进 bug-manage.md 更是本末倒置——绕过门面就不会读经验文件。

- **2026-06-25 #1**: 批量 bug 状态流转时，直接调用 `Skill(testmind:bug-manage)` 而非 `Skill(testmind-facade)`。
