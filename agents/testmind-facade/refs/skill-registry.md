# Skill Registry — testmind 技能路由表

门面在 Phase 2 (RESOLVE) 阶段查此表确定如何路由每个 testmind 技能调用。

## Delegated（委托本地 wrapper）

以下 testmind 技能已有成熟的本地 wrapper，门面委托给它们执行：

| testmind 技能 | 本地 wrapper | wrapper 逻辑 |
|--------------|-------------|-------------|
| `sql-execute` | `agents/test-runner/skills/sql-execute/` | 环境解析 → 数据库路由 → SQL 安全组装 → execute_sql.py → 编码修复 → sharding 回退 |
| `common-tool-execute` | `agents/test-runner/skills/execute-tool/` | Token 管理 → 目录匹配 → HTTP 参数组装 |

> ⚠️ **委托规则**：这些 wrapper 是唯一合法调用路径，禁止绕过门面直接调 wrapper，也禁止门面绕过 wrapper 直接调 testmind。

## Direct（门面直调 + 经验文件）

以下 testmind 技能无本地 wrapper，门面直接调用 `Skill(testmind:xxx)`，但带着对应经验文件的上下文：

| testmind 技能 | 经验文件 | 主要使用者 |
|--------------|---------|-----------|
| `query-log` | experience/query-log.md | test-runner, result-analyst, result-verifier |
| `bug-manage` | experience/bug-manage.md | result-analyst |
| `teams-message` | experience/teams-message.md | result-analyst |
| `email-send` | experience/email-send.md | result-analyst |
| `test-report` | experience/test-report.md | result-analyst |
| `dubbo-call` | experience/dubbo-call.md | test-runner |
| `auto-interface-exec` | experience/auto-interface-exec.md | test-runner |
| `auto-testcase-exec` | experience/auto-testcase-exec.md | test-runner |
| `knowledge-retrieve` | experience/knowledge-retrieve.md | knowledge-curator, result-verifier |
| `request-manage` | experience/request-manage.md | requirement-collector |
| `story-manage` | experience/story-manage.md | requirement-collector, testcase-writer |
| `get-request-content` | experience/get-request-content.md | requirement-collector |
| `confluence` | experience/confluence.md | requirement-collector |
| `auto-interface-list` | experience/auto-interface-list.md | test-mapper, platform-manager |
| `auto-testcase-list` | experience/auto-testcase-list.md | test-mapper, platform-manager |
| `testcase-manage` | experience/testcase-manage.md | testcase-writer, platform-manager |
| `db-manage` | experience/db-manage.md | result-verifier |
| `get-current-week-sprint-env` | experience/get-current-week-sprint-env.md | test-runner |
| `apollo-config` | experience/apollo-config.md | test-runner |
| `common_http_call_api` | experience/common_http_call_api.md | testcase-writer |
| `get-repo-code-diff` | experience/get-repo-code-diff.md | code-analyzer |
| `code-info` | experience/code-info.md | code-analyzer |
| `analyze-code-change` | experience/analyze-code-change.md | code-analyzer |
| `code-check` | experience/code-check.md | code-analyzer |
| `testcase-code-analyze` | experience/testcase-code-analyze.md | code-analyzer |
| `git-manage` | experience/git-manage.md | code-analyzer |
| `branch-manage` | experience/branch-manage.md | code-analyzer |

> 📌 未列出的 testmind 技能首次调用时自动按模板创建经验 stub。

## 如何新增

### 新增委托类 wrapper

当某个 testmind 技能的本地逻辑足够复杂（环境解析/路由/安全/编码/回退等多种逻辑），可以升级为 Delegated：

1. 创建本地 wrapper skill（参考 `sql-execute` 结构）
2. 在此表将其从 Direct 移到 Delegated
3. 经验文件保留，用于跨 Agent 的高层模式积累

### 新增经验文件

首次调用某个 testmind 技能时：
1. 门面发现 `experience/{name}.md` 不存在
2. 从 `refs/experience-template.md` 复制创建 stub
3. 正常执行
4. 若有发现，写回经验文件
