# CHANGELOG

TestScheduler 知识库变更日志。

## 2026-06-26

### 新增：Code Analyzer Agent

- 创建第 9 个 Agent：`agents/code-analyzer/`，负责代码分析全流程
- 6 个自有 Skill：
  - `setup-repo` — 拉取 APS/GWS-APS 仓库，自动检测迭代版本并切换分支
  - `fetch-code-diff` — 根据需求/Bug/Story编号从 testmind 获取代码变更
  - `analyze-code-for-testcase` — 分析代码改动 → 测试点/边界/数据流，辅助 testcase-writer
  - `static-code-test` — 静态分析：硬编码、空安全、逻辑错误等黑盒盲区问题
  - `organize-changes-by-item` — 按需求条目整理代码改动清单
  - `verify-bug-fix` — Bug修复验证：根因分析、副作用检测、回归风险
- 集成 7 个 testmind 代码分析 skill：get-repo-code-diff, code-info, analyze-code-change, code-check, testcase-code-analyze, git-manage, branch-manage
- 创建 7 个 experience stub 文件
- 更新 CLAUDE.md / AGENTS.md：Agent 表（8→9）、路由规则、Skill 映射、核心资产、HITL 确认点
- 更新 MEMORY.md 索引

## 2026-06-24

### 新增：testmind-facade 统一门面层
- 创建 `agents/testmind-facade/` 门面层，所有 `Skill(testmind:xxx)` 调用的统一入口
- 5 阶段执行协议：LOAD → RESOLVE → EXECUTE → OBSERVE → WRITE-BACK
- 经验文件 1:1 映射 testmind 技能，含 EVOLUTION_MARKER 自动进化机制
- 现有 sql-execute / common-tool-execute wrapper 保持独立，门面委托
- 迁移 `log-query-best-practices.md` → `experience/query-log.md`
- 8 个 AGENT.md 的「复用 testmind Skill」表替换为 facade 引用
- CLAUDE.md 新增门面层强制规则
- 修正 result-verifier/AGENT.md + assemble-params/refs/io.md 中 testmind:sql-execute 歧义措辞

### 新增：日志查询最佳实践（已迁移至 facade）
- 创建 `log-query-best-practices.md`（后迁移至 `agents/testmind-facade/experience/query-log.md`）

### 新增：testcase-execute 经验（facade）
- 创建 `agents/testmind-facade/experience/testcase-execute.md`
- 5 个踩坑 + 1 个验证模式：start→end→execute 流程、start_time/end_time 顶层传参、命令行超长规避
- 修正上次误写入 `memory/knowledge/patterns/` 的冗余

## 2026-06-11

### Phase 1: 项目骨架
- 项目初始化：创建 TestScheduler 测试调度平台
- 新建 7 Agent 体系：Requirement Collector, Test Case Writer, Test Mapper, Test Runner, Result Analyst, Platform Manager, Knowledge Curator
- 建立 22 Skill 技能树（3移植 + 19新建），每个含完整的输入/输出/执行逻辑/规则
- 创建 CLAUDE.md 主调度路由规则（10条单步 + 4条全流程 + 中断恢复）

### Phase 2: Test Case Writer 移植
- 创建 `run.py`（8个action，完整适配 TestScheduler）
- 创建 `testcase_writing_rules.md`（3条强制规则 + 4条分类规则）
- 创建 `interface_doc_cache/`（PingAnPh 接口文档缓存 + 索引）
- 创建 14列用例模板 `template.xlsx`

## 2026-06-24

### Knowledge Curator 首次运行 — NREQUEST-49267 知识沉淀
- 从 NREQUEST-49267 (APS冷热分离治理) 全流程产物中提取 5 条知识
- 建立 `memory/knowledge/` 分类目录结构：pitfalls / patterns / references / interfaces
- 新增 5 条知识条目：
  - `ob-async-write-lag` — OB库异步写入延迟踩坑
  - `apollo-timeout-but-effective` — Apollo配置超时但已生效踩坑
  - `log-based-read-route-verification` — 日志验证读取路由标准方法
  - `repay-order-id-field-mapping` — repay_order_id→repay_tran_no 字段映射参考
  - `aps-cold-hot-separation-test-pattern` — APS冷热分离测试全模式
- 更新 `curate-entry` Skill 输出路径为 `memory/knowledge/{type}/{name}.md`
- MEMORY.md 新增 `## Knowledge` 索引分区

### Phase 5: 集成与运维
- 新增全流程编排细节（6步逐步调度指令 + 每步输入/产出/检查）
- 新增中断恢复机制（继续重试/跳过/放弃 三级选择）
- 新增工作流状态管理（创建/恢复/更新 wf-*.json）
- 新增本地资源配置索引
- 新增 `.gitignore` 配置
- 定义 4 个核心数据 JSON Schema：执行计划、执行结果、Bug草稿、工作流状态
