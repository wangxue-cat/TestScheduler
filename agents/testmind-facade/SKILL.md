---
name: testmind-facade
description: "TestScheduler统一testmind技能调度门面。所有 Skill(testmind:xxx) 调用必须通过此入口：自动加载 per-skill 经验文件 → 解析路由（委托本地 wrapper 或直调）→ 执行 → 观察新模式 → 写回经验。"
argument-hint: "<testmind-skill-name> [调用参数描述...]"
---

# testmind-facade — TestMind 统一门面

## 硬性约束

1. **唯一入口**：所有 `Skill(testmind:xxx)` 调用必须通过此门面，禁止在各 Agent 中直接调用
2. **经验优先**：每次调用前加载 `experience/{skill-name}.md`，带着经验执行
3. **执行后观察**：每次调用后检查是否有新发现，有则写回
4. **委托优先**：已有本地 wrapper 的 testmind 技能（sql-execute、common-tool-execute），门面委托给 wrapper

## 执行协议

```
Phase 1: LOAD    → 读取 experience/{skill-name}.md，不存在则从模板创建 stub
Phase 2: RESOLVE → 查 refs/skill-registry.md 确定路由方式
Phase 3: EXECUTE → 带着经验上下文执行（委托 wrapper 或直调 testmind）
Phase 4: OBSERVE → 发现新模式/踩坑/映射？
Phase 5: WRITE-BACK → 追加到对应经验文件的 EVOLUTION_MARKER 位置
```

> 📁 协议详解 → [refs/execution-protocol.md](refs/execution-protocol.md)
> 📁 路由表 → [refs/skill-registry.md](refs/skill-registry.md)
> 📁 经验模板 → [refs/experience-template.md](refs/experience-template.md)

## Skill Registry 速查

| testmind 技能 | 路由方式 | 说明 |
|--------------|---------|------|
| `sql-execute` | **委托** `agents/test-runner/skills/sql-execute/` | 环境解析+库路由+SQL安全+编码修复 |
| `common-tool-execute` | **委托** `agents/test-runner/skills/execute-tool/` | Token管理+目录匹配+HTTP组装 |
| `query-log` | 直调 + [experience/query-log.md](experience/query-log.md) | 日志查询策略选择 |
| 其余所有 | 直调 + experience/{name}.md | 按需加载对应经验文件 |

## 使用示例

### 示例 1：查询日志（直调类）

```
用户: "查 APS 流水号 597c3706... 的日志"

门面执行:
  Phase 1 LOAD → 读 experience/query-log.md
    → 学到: 流水号用定时日志，APS = gws-aps-web + aps-app，STG3 实时日志路径无效
  Phase 2 RESOLVE → query-log 无本地 wrapper，直调
  Phase 3 EXECUTE → 直接用定时日志 --req-nos 查（跳过了实时日志试错！）
  Phase 4 OBSERVE → 无新发现，跳过写回
```

### 示例 2：执行 SQL（委托类）

```
用户: "查 aps.order_info 表"

门面执行:
  Phase 1 LOAD → 读 experience/sql-execute.md
  Phase 2 RESOLVE → sql-execute 有本地 wrapper，委托给 agents/test-runner/skills/sql-execute/
  Phase 3 EXECUTE → sql-execute wrapper 处理: 环境→库路由→SQL组装→执行→编码修复
  Phase 4 OBSERVE → 无新发现
```

### 示例 3：Bug 提交（首次，经验为空）

```
用户: "提 Bug"

门面执行:
  Phase 1 LOAD → experience/bug-manage.md 不存在 → 从模板创建 stub
  Phase 2 RESOLVE → bug-manage 无本地 wrapper，直调 testmind:bug-manage
  Phase 3 EXECUTE → 标准调用
  Phase 4 OBSERVE → 发现: 提 Bug 必须先用 story-manage 查 Story ID
  Phase 5 WRITE-BACK → 追加到 experience/bug-manage.md 的 EVOLUTION_MARKER
```

## 经验文件位置

所有经验文件在 `experience/` 目录下，与 testmind 技能名 1:1 对应：

| 经验文件 | 所属 testmind 技能 | 状态 |
|---------|-------------------|------|
| [experience/query-log.md](experience/query-log.md) | `testmind:query-log` | ✅ 已迁移 |
| [experience/sql-execute.md](experience/sql-execute.md) | `testmind:sql-execute` | ✅ 已创建 |
| [experience/bug-manage.md](experience/bug-manage.md) | `testmind:bug-manage` | ✅ 种子 |
| [experience/teams-message.md](experience/teams-message.md) | `testmind:teams-message` | ✅ 种子 |
| 其余 | 对应 testmind 技能 | ⏳ 首次调用时自动创建 |
