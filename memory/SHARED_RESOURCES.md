# 共享资源配置

TestScheduler 与 ClaudeMind 共享以下资源。本文件记录共享路径和同步规则。

## 共享资源清单

| 资源 | ClaudeMind 路径 | 用途 | 访问模式 |
|------|----------------|------|---------|
| 渠道接口定义 | `D:/ClaudeMind/memory/api_channels/*.json` | 接口 method、params、io_bindings、response_schema | 只读 |
| 全局常量 | `D:/ClaudeMind/memory/api_channels/global_constants.json` | LIVE_IMG_BASE64 等全局常量 | 只读 |
| 渠道规则 | `D:/ClaudeMind/memory/api_channels_rules/*.md` | 参数生成规则、流程定义、特殊逻辑 | 只读 |
| 小工具 API | `D:/ClaudeMind/memory/innovate_tools_api/` | 20 个辅助小工具（随机数据生成、加解密等） | 只读 |
| 数据库映射 | `D:/TestScheduler/memory/db_info_processed.json` | 环境+子系统→db_name 映射（本地副本，由 ClaudeMind 同步） | 只读 |
| Sharding 缓存 | `D:/TestScheduler/memory/sharding_table_cache.json` | sharding 表标记缓存 | 读写 |
| 接口文档合集 | `D:/接口文档合集/` | 原始接口文档（xlsx/docx/pdf） | 只读 |

## TestScheduler 私有资源

| 资源 | TestScheduler 路径 | 用途 |
|------|-------------------|------|
| 需求材料 | `D:/TestScheduler/memory/requirement_materials/` | 按需求 ID 组织的材料目录 |
| 测试用例 | `D:/TestScheduler/memory/testcases/` | 生成的测试用例 Excel |
| 执行计划 | `D:/TestScheduler/memory/execution_plans/` | 用例→接口映射产物 |
| 执行结果 | `D:/TestScheduler/memory/test_results/cache/` | 执行结果缓存 |
| 测试报告 | `D:/TestScheduler/memory/test_results/reports/` | Markdown + HTML 报告 |
| 工作流状态 | `D:/TestScheduler/memory/workflow_states/` | 全流程状态持久化 |

## 写入规则

- TestScheduler **只读**共享资源，不修改
- 如需新增渠道接口/规则 → 通过 **Platform Manager Agent** 操作，写入 ClaudeMind 共享路径
- TestScheduler 写入 ClaudeMind 共享路径时，需记录变更原因
