---
name: db-operation-rules
description: 数据库操作强制规则：SQL执行走sql-execute skill（test-runner agent自有），环境/库名/SQL三参数获取规则
metadata: 
  type: feedback
---

# 数据库操作强制规则

## SQL 执行强制路由

**⚠️ 最高优先级规则：所有 SQL 执行必须通过 Test Runner Agent 的 `sql-execute` skill 执行。**

| 调用场景 | 正确方式 | ❌ 禁止方式 |
|----------|----------|------------|
| 主会话中用户要求查数据 | `Agent(test-runner, "执行SQL: ...")` | 直接调 `testmind:sql-execute` skill |
| 其他 Agent 需要查数据 | 委托 Test Runner Agent 执行 | 自己调 `testmind:sql-execute` |
| 用例执行中需要查数据 | Test Runner 自有的 `sql-execute` skill | innovateTools DB 执行工具 |
| 落库校验 | `db-validation` skill（内部调 sql-execute） | 直接构造 SQL 查询 |

**Why:** 主会话或其他 Agent 直接调 `testmind:sql-execute` 绕过了 Test Runner Agent 的统一入口，导致：① 缺少环境/库路由逻辑 ② 缺少 sharding 回退 ③ 缺少安全校验 ④ 缺少活动日志记录 ⑤ 违反职责边界（SQL 执行是 Test Runner 的专属职责）。

**How to apply:** 任何需要执行 SQL 的场景，先判断当前是否在 Test Runner Agent 内：
- **在 Test Runner 内** → 直接调自有的 `sql-execute` skill
- **不在 Test Runner 内**（主会话/其他 Agent）→ 必须通过 `Agent(test-runner, ...)` 委托执行

## SQL 执行方式

所有数据库操作**必须**通过 `sql-execute` skill（test-runner agent 自有 skill）执行，禁止使用其他方式。

### 推荐执行方式：通过 sql-execute skill

```bash
# AI 调用方式：通过 test-runner agent 的 sql-execute skill
# skill 内部会自动：环境获取 → 数据库路由 → SQL组装 → 安全校验 → 调用testmind:sql-execute → 编码修复 → sharding回退

# CLI 直接调用（调试用）：
python "D:/TestScheduler/agents/test-runner/skills/sql-execute/run.py" \
  --env {环境} \
  --system {系统名} \
  --table {表名} \
  --sql "{SQL语句}" \
  --page-size {条数}
```

### 底层执行（skill 内部调用，用户不可直接使用）

skill 内部通过 `testmind:sql-execute` 的 `execute_sql.py` 脚本执行：

```bash
python "C:/Users/wangxue-jk/.claude/plugins/cache/quality-cc-marketplace/testmind/1.0.34/skills/common_sql_execute/scripts/execute_sql.py" \
  --env {环境} \
  --db-name {数据库名} \
  --sql "{SQL语句}" \
  --format markdown
```

## 三参数获取规则

调用 `sql-execute` skill 需提供 3 个条件：**环境**、**数据库名**、**SQL语句**。

### 1. 环境

| 条件 | 取值 |
|------|------|
| 用户显式给出环境 | 使用用户给出的环境（如 STG1、STG2、STG3） |
| 用户未给出环境 | 调用 `testmind:get-current-week-sprint-env` 获取当前迭代默认环境 |
| testmind 获取失败 | 使用最近一次使用过的环境 |
| 均无历史记录 | 提示用户先初始化环境信息（如运行 `testmind:init` 或手动指定） |

### 2. 数据库名

通过数据库路由规则文件匹配：`D:\TestScheduler\memory\db_info_processed.json`

- 根据**环境 + subsystem_name** 在路由文件中查找，同一 subsystem 下可能匹配多个库（普通库 + sharding 库）
- 用户可通过 **`系统名.表名`** 格式指定，如 `aps.order_info` → 查 system=`aps` → 匹配到 `aps_stg1`
- 若路由规则文件路径变更，此处的匹配路径需同步更新

#### Sharding 库匹配与回退规则

**背景**：部分系统的大表做了分库（如 lcs 的 ln_loan 分为 lcs_sa_0~lcs_sa_7），为方便查询，提供了 sharding 库（如 lcs-sharding）直接查所有分表数据。

**规则**：

1. **用户显式指定 sharding 子系统**：直接查 sharding 库，不查普通库
2. **缓存已标记**：`sharding_table_cache.json` 中已记录该表属于 sharding 库 → 直接查 sharding 库
3. **用户未指定 sharding 且缓存无标记**：优先查**普通库**。如果普通库返回"表不存在"或"数据为空"，自动回退到同 subsystem 下的 **sharding 库**再查一次
4. **Sharding 表标记缓存**：`D:\TestScheduler\memory\sharding_table_cache.json`

**示例**：

| 用户说 | 环境 | 匹配 | 第1次查询 | 结果 | 第2次查询（回退） | 最终 |
|--------|------|------|-----------|------|-------------------|------|
| lcs.ln_loan | STG1 | subsystem=LCS, 优先普通库 | lcs_stg1.ln_loan | 表不存在 | lcs_sharding_stg1.ln_loan | 有数据，标记缓存 |
| lcs.ln_loan（第2次） | STG1 | 缓存命中 | — | — | 直接 lcs_sharding_stg1.ln_loan | 有数据 |
| lcs-sharding.xxx | STG1 | 用户指定 sharding | lcs_sharding_stg1.xxx | — | — | 不回退 |

### 3. SQL 语句

#### SQL 生成限制

**a. 默认追加排序和限制**：用户未指定排序和数量时，自动追加 `ORDER BY id DESC LIMIT 1;`

**b. DELETE 和大批量 UPDATE 需用户确认**

**c. 系统名.表名 格式**：用户使用 `系统名.表名` 格式时自动解析
