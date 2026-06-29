---
name: fetch-code-diff
description: 根据需求/Bug/Story编号从 testmind 获取关联的代码变更文件列表和 diff 内容
argument-hint: "<id> [type: req|bug|story]"
---

# fetch-code-diff

根据需求/Bug/Story 编号，通过 testmind 查询关联的代码变更信息，返回结构化的变更文件列表和 diff 内容。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 需求/Bug/Story 编号（如 NREQUEST-48777、JYSG-150160） |
| type | string | 否 | 编号类型：`req` / `bug` / `story`，不指定则自动识别 |

## ID 类型自动识别

| 前缀 | 识别为 |
|------|--------|
| `NREQUEST-` | 需求（req） |
| `JYSG-` | Story |
| `API-` | API 任务 |
| `LPS-` | LPS 任务 |

## 执行步骤

### Step 1: 识别 ID 类型

根据前缀自动识别，若无法识别则询问用户。

### Step 2: 通过 testmind-facade 获取变更信息

调用 `Skill(testmind-facade)` → `get-repo-code-diff`，传入 ID 和类型。

期望返回内容：
- 关联的 commit 列表（hash、message、author、date）
- 变更文件列表（文件路径、变更类型：added/modified/deleted）
- 每个文件的 diff 内容（unified diff 格式）
- 所属仓库和分支信息

### Step 3: Fallback 处理

若 `get-repo-code-diff` 返回空或无权限：

1. 调用 `Skill(testmind-facade)` → `code-info` 尝试获取文件级信息
2. 若仍无结果，且本地仓库已通过 `setup-repo` 准备就绪，则用本地 git 查找：

```bash
# 搜索 commit message 中包含 ID 的提交
git log --all --grep="<id>" --oneline -20
# 获取这些 commit 的变更文件
git diff <base_branch>...HEAD --name-only
```

3. 若以上均无结果，明确告知用户"未找到 {id} 关联的代码变更"

### Step 4: 结构化输出

将结果整理为统一的结构化格式。

## 输出

```json
{
  "query": {
    "id": "NREQUEST-48777",
    "type": "req",
    "source": "testmind"
  },
  "repo": "aps",
  "branch": "feature/20260702",
  "commits": [
    {
      "hash": "abc1234",
      "message": "feat: xxx",
      "author": "developer",
      "date": "2026-07-01"
    }
  ],
  "changed_files": [
    {
      "path": "aps-service/src/main/java/com/qihoo/finance/aps/service/PaymentService.java",
      "change_type": "modified",
      "lines_added": 45,
      "lines_deleted": 12
    }
  ],
  "diff_content": "<unified diff 文本>",
  "stats": {
    "files_changed": 5,
    "insertions": 120,
    "deletions": 35
  }
}
```

| 字段 | 说明 |
|------|------|
| query.id | 查询的编号 |
| query.type | 编号类型 |
| query.source | 数据来源：`testmind` 或 `local_git` |
| repo | 所属仓库 |
| branch | 所在分支 |
| commits[] | 关联的 commit 列表 |
| changed_files[] | 变更文件列表（路径、变更类型、行数） |
| diff_content | 完整 unified diff |
| stats | 变更统计 |

## 关键规则

1. **优先 testmind**：先调 testmind 获取 diff，失败时才 fallback 到本地 git
2. **报告来源**：输出中必须标注 `source` 字段，明确数据来自 testmind 还是本地 git
3. **空结果明确告知**：找不到代码变更时不说"可能没有"，而是明确报告"未找到关联变更"并说明尝试了哪些途径
4. **过滤非代码文件**：自动过滤掉非代码变更文件（如 `.gitignore`、`pom.xml` 版本号变更等），但保留配置文件和 SQL 变更
5. **限制 diff 大小**：单个文件 diff 超过 500 行时截断并标注 `[已截断，完整内容过长]`
