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

## 调用链规则（2026-06-29 强化）

**唯一正确路径**：

```
主会话（编排路由） → Agent（执行） → Skill(testmind-facade) → Skill(testmind:xxx) → Bash
```

- 主会话只做编排：识别用户意图 → 匹配路由规则 → 调度 Agent
- Agent 负责执行：Agent 内部走门面 → skill → Bash
- **主会话禁止直接跑 Bash**，即使 skill 加载到主会话上下文中也不行
- 主会话跑 Bash = 执行者角色错位，架构上主会话是编排者不是执行者

### 禁止行为

- ❌ 直接 Bash 调 `story_manage.py` / `bug_manage.py` / `execute_sql.py` 等
- ❌ 直接 `Skill(testmind:bug-manage)` 跳过门面
- ❌ 在门面加载后，后续操作直接跑 Bash（"反正已经知道路由了"）

## 违规记录

- **2026-06-29 #4**: Skill 加载到主会话后，主会话自己跑了 Bash（bug_manage.py transition）。用户当场指出：主会话是编排者不是执行者，Bash 应该由 Agent 在内部执行，不是主会话直接跑。正确架构：`主会话 → Agent → 门面 → Skill → Bash`，主会话只做路由。

- **2026-06-29 #3**: 整个会话中多次绕过门面直接跑 Bash：SQL 查询（execute_sql.py）、Bug 创建（bug_manage.py create）、Bug 流转（bug_manage.py transition）、接口执行（requests.post）。用户当场纠正：必须严格走 `Skill(testmind-facade)` → `Skill(testmind:xxx)` 路径。

- **2026-06-25 #2**: 查询 bug 走了门面（正确），但后续 5 次状态流转全部绕过门面直接调 Bash。用户当场指出。**教训**：一次会话中完成门面 Phase 1-2 后，不能因为"已经知道路由"就跳过门面直接调 Bash——每次独立的 testmind 操作都需要走完整的 5-Phase 门面协议。

- **2026-06-25 #1**: 批量 bug 状态流转时，直接调用 `Skill(testmind:bug-manage)` 而非 `Skill(testmind-facade)`。
