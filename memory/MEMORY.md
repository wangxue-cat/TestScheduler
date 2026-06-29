# MEMORY

TestScheduler 知识库索引。

## Facts

- [testmind-facade-gateway-enforcement](testmind-facade-gateway-enforcement.md) — 所有 testmind skill 必须通过门面调用，严禁绕过
- [code-fix-boundary](code-fix-boundary.md) — 测试人员角色边界：只验证开发修复，不直接改业务代码

## Agents



- [Requirement Collector](../agents/requirement-collector/AGENT.md) — 需求采集：拉取需求详情、收集材料、检查提测
- [Test Case Writer](../agents/testcase-writer/AGENT.md) — 用例编写：生成Excel→评审→上传QOA（移植自ClaudeMind）
- [Test Mapper](../agents/test-mapper/AGENT.md) — 测试映射：解析用例→匹配平台接口→生成执行计划
- [Test Runner](../agents/test-runner/AGENT.md) — 测试执行：参数组装→调用testmind执行→收集日志
- [Result Analyst](../agents/result-analyst/AGENT.md) — 结果分析：失败诊断→提Bug→出报告→发通知
- [Platform Manager](../agents/platform-manager/AGENT.md) — 平台维护：接口管理、规则维护、流程编排
- [Knowledge Curator](../agents/knowledge-curator/AGENT.md) — 知识沉淀：经验提炼、自动发现、条目CRUD
- [Code Analyzer](../agents/code-analyzer/AGENT.md) — 代码分析：仓库准备→拉取diff→静态分析→辅助用例→整理改动→验证修复

## Facts

- [story-manage 流转必须传 --from-status](story-manage-transition-requires-from-status.md) — transition/batch-transition 不传当前状态会报错，必须 --from-status + --test-type
- [环境解析规则](.env_override.md) — 三级优先级：用户指定 > 本地缓存 > testmind查询；每次切换自动缓存
- [共享资源配置](SHARED_RESOURCES.md) — TestScheduler 与 ClaudeMind 共享渠道JSON、规则、小工具、DB映射，只读访问
- [工作流状态模板](workflow_states/.gitkeep) — 全流程状态持久化模板，6步标准流水线 + context 上下文

## Knowledge

### Pitfalls（踩坑记录）

- [OB异步写入有1秒延迟](knowledge/pitfalls/ob-async-write-lag.md) — OB库写入是afterCommit异步执行，验证前需等待3-5秒
- [Apollo配置超时但已生效](knowledge/pitfalls/apollo-timeout-but-effective.md) — Apollo修改操作返回超时≠失败，需通过业务行为验证

### Patterns（测试模式）

- [日志查询最佳实践](../agents/testmind-facade/experience/query-log.md) — 策略选择矩阵+系统应用映射+踩坑记录，持续进化（已迁移至 testmind-facade）
- [日志验证读取路由方法](knowledge/patterns/log-based-read-route-verification.md) — 4步法：定位req_no→追踪trace_id→确认读取模式→验证SQL目标表
- [APS冷热分离测试全模式](knowledge/patterns/aps-cold-hot-separation-test-pattern.md) — 4种写入+2种读取+OB穿透+监控告警，31字段全量比对

### References（参考）

- [repay_order_id→repay_tran_no字段映射](knowledge/references/repay-order-id-field-mapping.md) — API参数与DB列名的对应关系

## References

- [项目设计文档](file:///C:/Users/wangxue-jk/.claude/plans/agent-witty-bird.md) — 完整的多Agent架构设计和 Skill 全景矩阵
- [ClaudeMind 项目](file:///D:/ClaudeMind/) — 共享 testmind 引擎和渠道接口定义的源项目