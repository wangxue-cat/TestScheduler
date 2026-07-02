# TestScheduler — 测试调度平台

## 项目概述

独立的多Agent测试调度平台，覆盖从需求分析到知识沉淀的完整测试生命周期，基于 testmind 底层技能引擎运行。

## Agent 调度规则

TestScheduler 的操作模式：

### 插件配置

保留启用的插件：
| 插件 | 原因 |
|------|------|
| `testmind@quality-cc-marketplace` | 提供 `Skill(testmind:xxx)` 底层技能引擎 |
| `qoa-mcp@quality-cc-marketplace` | 提供 `Skill(qoa-mcp:qoa)` QOA 平台操作 |
| `superpowers@claude-plugins-official` | 提供 `Skill(superpowers:xxx)` 工作流技能 |
| `skill-creator@claude-plugins-official` | 提供 `Skill(skill-creator:skill-creator)` 技能创建 |

### Agent 注册

TestScheduler 的 9 个本地 Agent 已注册到 `d:\TestScheduler\.claude\agents\`：

| Agent | 注册文件 |
|-------|---------|
| Requirement Collector | `.claude/agents/requirement-collector.md` |
| Test Case Writer | `.claude/agents/testcase-writer.md` |
| Test Mapper | `.claude/agents/test-mapper.md` |
| Test Runner | `.claude/agents/test-runner.md` |
| Result Verifier | `.claude/agents/result-verifier.md` |
| Result Analyst | `.claude/agents/result-analyst.md` |
| Platform Manager | `.claude/agents/platform-manager.md` |
| Knowledge Curator | `.claude/agents/knowledge-curator.md` |
| Code Analyzer | `.claude/agents/code-analyzer.md` |

### 调用规则

1. **用 TestScheduler 本地 Agent**：通过 `Agent({name})` 调度，产出路径为 `d:\TestScheduler\memory\`
2. **testmind Skill 必须走门面**：所有 `Skill(testmind:xxx)` 必须通过 `Skill(testmind-facade)` 门面层
3. **主会话直接执行**：按本文件路由规则逐步调度
4. **testmind:xxx 命名空间 Agent 可用但慎用**：`testmind@quality-cc-marketplace` 插件提供的 Agent（如 `testmind:ai-test-orchestrator`）保留可用，但常规测试流程优先使用 TestScheduler 本地 Agent

## 数据来源

所有数据从以下途径获取，不依赖外部项目：

| 需要的数据 | TestScheduler 获取方式 |
|-----------|----------------------|
| 渠道接口定义 | 从自动化平台查询（`testmind:auto-interface-list`） |
| 渠道规则 MD | 从 `d:\TestScheduler\memory\api_channels_rules\` 读取（参数取值规则，非接口定义） |
| 数据库映射 | 从 `d:\TestScheduler\memory\db_info_processed.json` 读取 |
| 需求/Story/Bug 信息 | 通过 `Skill(testmind:xxx)` 接口实时获取 |
| 接口文档 | 从 `d:\TestScheduler\memory\interface_docs\` 读取 |

### 缺失即建设机会

如果 TestScheduler 本地缺少某个文件导致无法完成任务，直接告知用户文件缺失，这正是项目的建设欠缺所在。

## 多Agent架构

### 9个Agent

| Agent | 入口 | 职责 | 来源 |
|-------|------|------|------|
| **Requirement Collector** | `requirement-collector` | 需求采集：拉取需求详情、收集材料、检查提测 | 新建 |
| **Test Case Writer** | `testcase-writer` | 用例编写：生成Excel→评审→上传QOA | 新建 |
| **Test Mapper** | `test-mapper` | 测试映射：解析用例→匹配平台接口→生成执行计划 | 新建 |
| **Test Runner** | `test-runner` | 测试执行：参数组装→调用testmind执行→收集日志 | 新建 |
| **Result Verifier** | `result-verifier` | 结果复验：DB落库校验→字段比对→日志关键字验证→生成验证报告 | 新建 |
| **Result Analyst** | `result-analyst` | 结果分析：失败诊断→提Bug→出报告→发通知 | 新建 |
| **Platform Manager** | `platform-manager` | 平台维护：接口管理、规则维护、流程编排 | 新建 |
| **Knowledge Curator** | `knowledge-curator` | 知识沉淀：经验提炼、自动发现、条目CRUD | 新建 |
| **Code Analyzer** | `code-analyzer` | 代码分析：仓库准备→拉取diff→静态分析→辅助用例→整理改动→验证修复 | 新建 |

### 调用关系

```
Requirement Collector → Test Case Writer → Test Mapper → Test Runner → Result Verifier → Result Analyst → Knowledge Curator
Platform Manager ⇄ Test Mapper / Test Runner
Result Analyst → Knowledge Curator
Code Analyzer → Test Case Writer / Result Analyst / Knowledge Curator
Requirement Collector / Test Case Writer / Result Analyst → Code Analyzer
```

主会话根据本文件路由规则直接调度各 Agent，无独立调度中间层。

### 一句话指令示例

- "处理需求 NREQUEST-48504" → 全流程（Requirement Collector → Test Case Writer → Test Mapper → Test Runner → Result Verifier → Result Analyst → Knowledge Curator）
- "拉需求 NREQUEST-48504" → 单步（Requirement Collector）
- "写用例 NREQUEST-48504" → 单步（Test Case Writer）
- "映射+执行 NREQUEST-48504" → 从映射开始（Test Mapper → Test Runner → Result Verifier → Result Analyst）
- "只执行+出报告 NREQUEST-48504" → 执行+分析（Test Runner → Result Verifier → Result Analyst）
- "复验 NREQUEST-48504" → 单步（Result Verifier）
- "新增接口 TouTiao" → 平台维护（Platform Manager）
- "沉淀经验 NREQUEST-48504" → 知识沉淀（Knowledge Curator）
- "代码分析 NREQUEST-48777" → 代码分析（Code Analyzer）
- "静态分析 NREQUEST-48777" → 代码分析 → static-code-test（Code Analyzer）
- "辅助写用例 NREQUEST-48777" → 代码分析 → analyze-code-for-testcase（Code Analyzer）
- "整理改动点 NREQUEST-48777" → 代码分析 → organize-changes-by-item（Code Analyzer）
- "验证修复 JYSG-xxxxx" → 代码分析 → verify-bug-fix（Code Analyzer）
- "代码辅助写用例 NREQUEST-48777" → 代码分析 → Test Case Writer（Code Analyzer: setup-repo → analyze-code-for-testcase → Test Case Writer 读取报告编写用例）

---

## 硬性路由规则

### 单步指令

| 用户指令匹配 | 调度目标 |
|-------------|---------|
| "拉需求" / "获取需求" / "需求材料" / "提测了吗" | `Agent(requirement-collector)` |
| "写用例" / "生成用例" / "生成测试用例" | `Agent(testcase-writer)` |
| "映射用例" / "匹配接口" / "生成执行计划" | `Agent(test-mapper)` |
| "执行用例" / "跑用例" / "调接口" / "执行接口" | `Agent(test-runner)` |
| "复验" / "结果复验" / "验证结果" / "核查" / "复验结果" | `Agent(result-verifier)` |
| "分析结果" / "看下执行情况" / "分析失败" | `Agent(result-analyst)` |
| "提Bug" / "报缺陷" / "提交缺陷" | `Agent(result-analyst)` |
| "出报告" / "生成测试报告" / "测试报告" | `Agent(result-analyst)` |
| "新增接口" / "录入接口" / "更新接口" / "接口管理" | `Agent(platform-manager)` |
| "渠道规则" / "编排流程" / "流程编排" | `Agent(platform-manager)` |
| "总结" / "沉淀经验" / "入库" / "知识沉淀" | `Agent(knowledge-curator)` |
| "代码分析" / "分析代码" / "静态扫描" / "代码静态测试" | `Agent(code-analyzer)` |
| "辅助写用例" / "代码辅助" / "代码分析辅助用例" | `Agent(code-analyzer)` → `Agent(testcase-writer)` |
| "整理改动" / "整理改动点" / "按条目整理代码" | `Agent(code-analyzer)` |
| "验证修复" / "验证Bug修复" / "Bug修复验证" | `Agent(code-analyzer)` |
| "拉代码" / "准备仓库" / "setup repo" | `Agent(code-analyzer)` |

### 全流程指令（主会话按序列逐步调度）

| 用户指令 | Agent 执行序列 |
|---------|---------------|
| **"处理需求 {id}"** | Requirement Collector → Test Case Writer → Test Mapper → Test Runner → Result Verifier → Result Analyst → Knowledge Curator |
| **"回归测试 {id}"** | Test Mapper → Test Runner → Result Verifier → Result Analyst |
| **"从映射开始处理 {id}"** | Test Mapper → Test Runner → Result Verifier → Result Analyst → Knowledge Curator |
| **"只执行+出报告 {id}"** | Test Runner → Result Verifier → Result Analyst |
| **"代码分析流程 {id}"** | setup-repo → fetch-code-diff → organize-changes-by-item → static-code-test → analyze-code-for-testcase |
| **"代码辅助写用例 {id}"** | Code Analyzer (setup-repo → analyze-code-for-testcase) → Test Case Writer (读取 testcase_aid_report.md 编写用例) |

**兜底规则**：指令无法匹配到任何 Agent，或纯闲聊/问概念/改配置，则由主会话自由发挥。

### 全流程执行规则

1. **逐步推进**：主会话按序列逐个调度 Agent，每个 Agent 完成后检查产出物，再调度下一个
2. **中断恢复**：任一步骤失败，暂停并告知用户。支持"继续"/"跳过"/"放弃"
3. **状态持久化**：全流程状态写入 `memory/workflow_states/wf-{req_id}.json`
4. **环境传递**：环境信息（STG1/STG2）在每个 Agent 间传递，首次执行时询问用户确认

---

## 全流程编排细节

### "处理需求 {id}" 逐步调度指令

主会话按以下序列执行，**每步完成后检查产出物再调下一步**：

```
Step 1: Agent(requirement-collector)
  提示: "使用 fetch-requirement + collect-materials 拉取需求 {id}"
  产出: memory/requirement_materials/{id}/{id}_requirement.md
  检查: {id}_requirement.md 存在且包含需求内容 → 进入 Step 2
  失败: 暂停，告知用户

Step 2: Agent(testcase-writer)  ← [用户确认 Excel 后继续]
  提示: "使用 api-testcase-writer 为需求 {id} 生成测试用例"
  输入: requirement_materials/{id}/
  产出: memory/testcases/{id}_testcases.xlsx
  检查: Excel 文件存在 → 🔴 Human Confirm → 进入 Step 3
  失败: 暂停，告知用户

Step 3: Agent(test-mapper)
  提示: "使用 parse-case-steps → match-platform-interface → generate-execution-plan 映射需求 {id} 的用例"
  输入: memory/testcases/{id}_testcases.xlsx
  产出: memory/execution_plans/{id}_plan.json
  检查: plan.json 存在且 cases 非空 → 进入 Step 4
  有 unmatched: 🟢 告知用户确认后继续
  失败: 暂停

Step 4: Agent(test-runner)  ← [首次执行需用户确认环境]
  提示: "使用 assemble-params → execute-plan → collect-execution-logs 执行需求 {id}"
  输入: memory/execution_plans/{id}_plan.json + env (默认STG1)
  产出: memory/test_results/cache/{id}_execution_results.json
  检查: results.json 存在 → 进入 Step 5
  失败: 暂停

Step 5: Agent(result-verifier)
  提示: "使用 verify-db-exists → verify-field-compare → verify-log-keywords → generate-verification-report 复验需求 {id}"
  输入: memory/execution_plans/{id}_plan.json + memory/test_results/cache/{id}_execution_results.json
  产出: memory/test_results/verification/{id}_verification_report.json + .md
  检查: verification_report.json 存在 → 进入 Step 6
  有不一致: 🟡 告知用户确认后继续
  失败: 暂停

Step 6: Agent(result-analyst)
  提示: "使用 analyze-failure → generate-report 分析需求 {id} 的执行结果"
  输入: memory/test_results/cache/{id}_execution_results.json + memory/test_results/verification/{id}_verification_report.json
  产出: memory/test_results/reports/{id}_execution_report.md + .html
  有失败: 生成 Bug 草稿 → 🔴 Human Confirm → file-bug
  通知: 🟡 Human Confirm → send-notification
  检查: 报告文件存在 → 进入 Step 7

Step 7: Agent(knowledge-curator)
  提示: "使用 summarize-execution 提炼需求 {id} 的经验"
  输入: 全流程产物
  产出: 知识条目草稿 → 🟡 Human Confirm → curate-entry → MEMORY.md 更新
```

### 中断恢复机制

全流程中任一步骤失败时，执行以下逻辑：

1. **更新工作流状态**: 将当前步骤标记为 `failed`，`state` 设为 `paused`
2. **展示中断信息**:
   ```
   ⚠️ 全流程在 Step {N} ({agent_name}) 中断
   已完成: Step 1 ~ Step {N-1}
   失败步骤: {agent_name} — {error_summary}
   已产出:
     - {已完成步骤的产出物列表}
   选择: [继续重试] [跳过此步骤] [从下一步继续] [放弃]
   ```
3. **用户选择后**:
   - 继续重试: 重新调度失败的 Agent
   - 跳过: 标记步骤为 `skipped`，state 恢复 `running`，继续下一步
   - 放弃: 标记 `state` 为 `abandoned`，结束流程

### 工作流状态管理

每次全流程启动时：
1. 检查 `memory/workflow_states/wf-{req_id}.json` 是否存在
2. 若存在且状态为 `paused`/`running` → 询问用户：继续上次流程 / 重新开始
3. 若不存在 → 创建新状态文件，`state=running`
4. 每步完成/失败时 → 更新状态文件

---

## 核心资产

| 资产 | 路径 | 说明 |
|------|------|------|
| 知识库索引 | `memory/MEMORY.md` | 所有知识条目的入口索引 |
| 变更日志 | `memory/CHANGELOG.md` | 知识库操作变更记录 |
| 需求材料 | `memory/requirement_materials/{req_id}/` | 按需求ID组织的材料目录 |
| 测试用例 | `memory/testcases/` | 测试用例 Excel 存放目录 |
| 测试结果 | `memory/test_results/reports/` | 测试报告（Markdown + HTML） |
| 执行缓存 | `memory/test_results/cache/` | 执行结果缓存 |
| 结果复验 | `memory/test_results/verification/` | 结果复验报告（JSON + Markdown） |
| 执行计划 | `memory/execution_plans/` | 用例→接口映射产物 |
| 渠道规则 | `memory/api_channels_rules/{partner_code}.md` | 渠道参数取值规则 |
| 自动化平台接口 | QOA 自动化平台 | 所有接口定义唯一真相源，通过 `testmind:auto-interface-list` 查询 |
| 接口文档 | `memory/interface_docs/` | 接口文档 MD 缓存（从原始接口文档自动转换） |
| 工作流状态 | `memory/workflow_states/` | 全流程状态持久化 |
| 代码分析报告 | `memory/code_analysis/{req_id}/` | 代码分析产出（辅助用例/静态分析/改动清单/修复验证） |
| 本地代码仓库 | `D:\project\aps`, `D:\project\gws-aps` | APS 和 GWS-APS 代码仓库本地镜像 |

---

## Human-in-the-Loop 确认点

以下操作必须暂停等待用户确认：

| # | 确认点 | 触发时机 | 风险等级 |
|---|--------|---------|---------|
| 1 | 生成用例 Excel | Test Case Writer 产出后 | 🔴 高 |
| 2 | 提 Bug | Result Analyst 提交前 | 🔴 高 |
| 3 | 材料缺失 | 需求文档+测试说明均缺失时 | 🔴 高 |
| 4 | 接口文档缺失 | 渠道接口文档和MD缓存均未找到时 | 🔴 高 |
| 5 | 发送通知 | Teams/邮件发送前 | 🟡 中 |
| 6 | 上传用例到 QOA | Test Case Writer 上传前 | 🟡 中 |
| 7 | 创建知识条目 | Knowledge Curator 入库前 | 🟡 中 |
| 8 | 首次执行 | Test Runner 首次执行前 | 🟡 中 |
| 9 | 接口映射异常 | Test Mapper 匹配失败时 | 🟢 低 |
| 10 | 全流程中断恢复 | 任一步骤失败时 | 🟢 低 |
| 11 | 代码分析发现Blocker | Code Analyzer 静态分析发现线上必现故障时 | 🔴 高 |
| 12 | Bug修复验证高风险 | verify-bug-fix 回归风险评估为High时 | 🟡 中 |

---

## 用例与测试说明同步规则

> 📌 **强制规则：任何对测试用例的修改（Excel/JSON），必须同步更新对应的测试说明文档。**

### 规则

1. **测试说明是唯一真相源**：`memory/requirement_materials/{req_id}/{req_id}_tester_notes.md` 是测试用例的权威说明文档
2. **用例修改必同步**：新增、修改、删除测试用例时，必须同步更新测试说明中的用例清单、配置信息、测试规则
3. **补充信息必记录**：用户对测试用例的任何口头补充说明（渠道选择、接口指定、验证方法、Apollo配置等），都属于测试说明的一部分，必须写入 tester_notes.md
4. **用例可从此重建**：测试说明必须足够完整，即使 Excel 丢失，也能根据测试说明完整重建用例
5. **更新记录**：每次同步在测试说明的「更新记录」表格中追加一行

### 测试说明必须包含的内容

- Apollo 配置清单（配置 Key、类型、默认值、可选值）
- 用例清单（每条用例的核心配置和验证点）
- 测试渠道和接口信息
- 数据库表分布（库名、子系统）
- 日志验证方法（关键字、命令、判断依据）
- 测试规则和注意事项

### 编辑方式

更新 Excel 时**必须直接编辑现有文件**（openpyxl），禁止重新生成覆盖。

---

## SQL 执行强制规则

> 📌 **强制规则：所有 SQL 执行必须通过 TestRunner 的 sql-execute 技能，禁止绕过。**

TestScheduler 有自己独立的 SQL 执行规范文件：[agents/test-runner/skills/sql-execute/SKILL.md](agents/test-runner/skills/sql-execute/SKILL.md)，其中定义了完整的执行流程和安全规则。

### 必须遵守的规则

1. **唯一入口**：所有 SQL 执行必须通过 `agents/test-runner/skills/sql-execute/SKILL.md` 定义的流程，禁止直接调用 `testmind:sql-execute` 或 curl 等方式绕过
2. **环境获取**：用户未指定环境时，必须通过 `testmind:get-current-week-sprint-env` 获取当前迭代默认环境，不可猜测
3. **数据库路由**：必须通过 `d:\TestScheduler\memory\db_info_processed.json` 匹配 db_name，不可猜测库名
4. **SQL 安全组装**：
   - 数据查询无 WHERE/LIMIT/ORDER BY 时自动追加 `ORDER BY id DESC LIMIT 1`
   - 有 WHERE 条件的查询不追加 LIMIT
   - 表结构/统计类查询不追加 LIMIT
5. **安全校验**：DELETE 和大批量 UPDATE（影响 >20 条）必须用户确认
6. **编码修复**：返回结果中的中文必须修复 UTF-8 双重编码
7. **Sharding 回退**：普通库查不到数据时必须尝试同 subsystem 的 sharding 库回退

### 禁止的行为

- ❌ 绕过此 skill 直接调用 `testmind:sql-execute`
- ❌ 使用 curl 直接调用 HTTP API
- ❌ 猜测环境或数据库名
- ❌ 不读 `db_info_processed.json` 就执行 SQL

### 与全局 testmind:sql-execute 的关系

`testmind:sql-execute` 仅作为底层 HTTP 执行通道，TestScheduler 的 sql-execute skill 在其之上封装了环境解析、库路由、SQL 组装、结果处理等逻辑。**主会话执行 SQL 时必须走 TestScheduler 的封装层，不可跳过。**

---

## 执行引擎

### testmind Skill → Agent 映射

| testmind Skill | 归属Agent | 用途 |
|----------------|----------|------|
| `request-manage` | Requirement Collector | 查询需求/提测状态 |
| `story-manage` | Requirement Collector, Test Case Writer | 查询 Story |
| `get-request-content` | Requirement Collector | 获取需求文档正文 |
| `confluence` | Requirement Collector | 读取 Confluence 设计文档 |
| `auto-interface-list` | Test Mapper, Platform Manager | 获取平台接口列表 |
| `auto-testcase-list` | Test Mapper, Platform Manager | 获取平台用例列表 |
| `testcase-manage` | Test Case Writer, Platform Manager | 用例上传/管理 |
| `auto-interface-exec` | Test Runner | 执行单个接口 |
| `auto-testcase-exec` | Test Runner | 执行平台用例 |
| `dubbo-call` | Test Runner | 降级方案（invokeFacade不通时） |
| `query-log` | Test Runner, Result Analyst | 查询应用日志 |
| `sql-execute` | Test Runner | SQL查询（参数准备），走本地 `agents/test-runner/skills/sql-execute/` 封装 |
| `common_tool_execute` | Test Runner | 调用小工具（随机数据生成等） |
| `bug-manage` | Result Analyst | 提交/查询 Bug |
| `test-report` | Result Analyst | 生成测试报告模板 |
| `teams-message` | Result Analyst | Teams 通知 |
| `email-send` | Result Analyst | 邮件通知 |
| `knowledge-retrieve` | Knowledge Curator | 语义检索知识库 |
| `common_http_call_api` | Test Case Writer | Confluence 页面获取 |
| `get-repo-code-diff` | Code Analyzer | 获取关联需求/Story/Bug的代码变更文件和diff |
| `code-info` | Code Analyzer | 查询代码文件结构、方法签名、类层次信息 |
| `analyze-code-change` | Code Analyzer | 分析代码变更范围、依赖影响 |
| `code-check` | Code Analyzer | 代码静态检查（硬编码、空安全、资源管理等） |
| `testcase-code-analyze` | Code Analyzer | 面向测试用例生成的代码分析 |
| `git-manage` | Code Analyzer | Git仓库元数据查询和操作 |
| `branch-manage` | Code Analyzer | Sprint分支管理 |

---

## 本地资源

TestScheduler 独立维护以下本地资源：

- **渠道规则**: `memory/api_channels_rules/{partner_code}.md`（参数取值规则，非接口定义）
- **小工具**: `memory/innovate_tools_api/`
- **数据库映射**: `memory/db_info_processed.json`

> ⚠️ **接口定义不再使用本地 JSON 文件**。所有渠道接口定义统一在 QOA 自动化平台维护，通过 `testmind:auto-interface-list` 查询。

写入操作（新增接口、更新规则）通过 Platform Manager Agent 完成。

---

## 环境信息

- 默认环境：STG1
- 可用环境：STG1 / STG2 / STG3
- 当前迭代版本：跟随 testmind 配置
- 用户角色：测试人员
