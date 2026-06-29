---
name: setup-repo
description: 根据需求/Bug/Story编号找到对应迭代分支，拉取APS/GWS-APS仓库最新代码到本地
argument-hint: "<id> [repo: aps|gws-aps|all]"
---

# setup-repo

根据需求/Bug/Story 编号查询所属迭代，确定正确的分支名（`feature/{版本}` 或 `release/{版本}`），
然后拉取最新代码。每次执行都会 `git fetch + pull`，确保代码是最新的。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 需求/Bug/Story 编号（如 NREQUEST-48777、JYSG-150160） |
| repo | string | 否 | 目标仓库：`aps` / `gws-aps` / `all`（默认 `all`） |

## 仓库信息

| 仓库 | GitLab 地址 | 本地路径 |
|------|------------|---------|
| APS | `https://gitlab.daikuan.qihoo.net/360jr-mkt/aps.git` | `D:\project\aps` |
| GWS-APS | `https://gitlab.daikuan.qihoo.net/360jr-mkt/gws-aps.git` | `D:\project\gws-aps` |

## 执行步骤

### Step 1: 查询 ID 所属迭代

根据 ID 类型查询所属迭代版本：

| ID 前缀 | 查询方式 | 获取字段 |
|---------|---------|---------|
| `NREQUEST-` | `Skill(testmind-facade)` → `request-manage` 查询需求详情 | 迭代版本号（如 `20260702`） |
| `JYSG-`（Story） | `Skill(testmind-facade)` → `story-manage` 查询 Story 详情 | 迭代版本号 |
| `JYSG-`（Bug） | `Skill(testmind-facade)` → `bug-manage` 查询 Bug 详情，再关联 Story | 迭代版本号 |

若查询不到迭代信息，fallback 到 `get-current-week-sprint-env` 获取当前迭代版本。

解析版本号格式：`20260702 迭代版本` → `20260702`。

### Step 2: 确定目标分支

按优先级尝试：
1. `feature/{版本号}` — 开发分支（优先）
2. `release/{版本号}` — 发布分支

### Step 3: 确保仓库存在

对每个目标仓库：
- **本地路径不存在** → `git clone <url> <local_path>`
- **已存在** → `git fetch --all --prune`

认证：依赖 Windows 凭据管理器。

### Step 4: 切换到目标分支并拉取最新

```bash
# 若当前分支不是目标分支，先 checkout
git checkout <target_branch>

# 拉取最新代码（每次都拉）
git pull origin <target_branch>
```

若目标分支在 remote 中不存在：
- 列出 `feature/*` 和 `release/*` 中与版本号最接近的分支
- 告知用户选择，暂停等待确认

### Step 5: 确认状态

```json
{
  "query": {
    "id": "NREQUEST-48777",
    "iteration": "20260702",
    "target_branch": "feature/20260702"
  },
  "repos": [
    {
      "name": "aps",
      "local_path": "D:\\project\\aps",
      "branch": "feature/20260702",
      "head_commit": "abc1234",
      "head_message": "feat: xxx",
      "action": "switched_and_pulled"
    }
  ]
}
```

## 输出

| 字段 | 说明 |
|------|------|
| query.id | 查询的编号 |
| query.iteration | 所属迭代版本号 |
| query.target_branch | 目标分支名 |
| repos[].name | 仓库名 |
| repos[].local_path | 本地路径 |
| repos[].branch | 当前所在分支 |
| repos[].head_commit | HEAD commit hash |
| repos[].action | 执行的动作：`cloned` / `switched_and_pulled` / `fast_forwarded` |

## 关键规则

1. **每次都拉**：不管当前分支是否已正确，都执行 `git pull` 确保代码最新
2. **迭代来源优先**：以 ID 所属迭代为准，不是当前迭代；查不到才 fallback
3. **不删除已有仓库**：已存在只做 fetch + checkout + pull，不重新 clone
4. **未提交修改处理**：若有本地修改，执行 `git stash` 暂存
5. **分支不存在时**：列出最近 feature/release 分支，让用户选择
6. **网络异常时**：提示检查 VPN 和 GitLab 凭证
