# NREQUEST-49352 可执行性报告

> 生成时间: 2026-07-02 | 生成者: test-mapper agent | 环境: STG1 | 迭代: 20260702

---

## 1. 执行概要

| 指标 | 数量 | 说明 |
|------|------|------|
| 总用例数 | 37 | 含28条线程池隔离 + 9条IT巡检日常巡视 |
| 可执行用例 | 28 | 线程池配置隔离用例（全维度覆盖） |
| 部分可执行 | 1 | third_repay_withhold去重（仅DB验证部分） |
| 不可执行 | 8 | IT巡检日常巡视用例（缺少平台接口） |
| 匹配的技能 | 5 | apollo-config, lingxi-scheduler, schedule, sql-execute, query-log |

---

## 2. 用例分类

### 2.1 可执行用例（28条）

全部属于"线程池配置隔离"测试维度，映射到testmind基础设施技能：

| 维度 | 用例数 | 主要技能 |
|------|--------|---------|
| 一、优化开关控制 | 2 | apollo-config + lingxi-scheduler + query-log |
| 二、线程池选择四级优先级 | 6 | apollo-config + lingxi-scheduler + query-log |
| 三、JSS参数兼容性 | 3 | lingxi-scheduler + query-log |
| 四、锁行为变更 | 3 | lingxi-scheduler + query-log |
| 五、线程池资源与隔离 | 4 | sql-execute + lingxi-scheduler + query-log |
| 六、异常与兜底 | 3 | lingxi-scheduler + query-log |
| 七、动态配置生效 | 2 | apollo-config + lingxi-scheduler + query-log |
| 八、多线程任务 | 3 | lingxi-scheduler + query-log |
| 九、历史遗留兼容 | 2 | apollo-config + sql-execute + lingxi-scheduler + query-log |

### 2.2 部分可执行用例（1条）

| 用例 | 可执行部分 | 缺失部分 |
|------|-----------|---------|
| third_repay_withhold去重 | DB查询验证重复数据 | 触发业务流程 |

### 2.3 不可执行用例（8条）— BLOCKED

所有IT巡检日常巡视用例因缺少平台接口而标记为 `unmatched`：

| 用例 | 缺失接口 | 建议 |
|------|---------|------|
| OCR识别失败记录具体原因 | OCR识别接口 | Platform Manager 注册 |
| 代偿凭证仅OK文件 | 文件处理接口 | Platform Manager 注册 |
| 微众银行终态不通知 | 订单推送接口 | Platform Manager 注册 |
| imgp通知bizNo为空 | 通知接口 | Platform Manager 注册 |
| 快手还款RECORD_NOT_EXISTS | 还款结果拉取接口 | Platform Manager 注册 |
| 头条调额不多笔订单 | 调额接口 | Platform Manager 注册 |
| 合同下载D日不告警 | 合同下载接口 | Platform Manager 注册 |
| 半流程空指针修复 | 协议拉取接口 | Platform Manager 注册 |

---

## 3. 技能映射

### 3.1 已匹配技能

| 技能 | 调用方式 | 用途 | 参数说明 |
|------|---------|------|---------|
| `testmind:apollo-config` | 通过 testmind-facade 直调 | Apollo配置查询/修改 | key, value, env=STG1 |
| `testmind:lingxi-scheduler` | 通过 testmind-facade 直调 | JSS定时任务触发 | taskName/taskPoolName/shard参数 |
| `testmind:sql-execute` | 通过 testmind-facade → 本地wrapper | 数据库验证 | subsystem=aps-app, database=aps |
| `testmind:query-log` | 通过 testmind-facade 直调 | 日志关键字验证 | app=aps-app, keyword, env=STG1 |
| `testmind:schedule` | 通过 testmind-facade 直调 | 调度管理（备用） | - |

### 3.2 待平台录入的接口

以下对应渠道的API接口需要在自动化平台注册后方可执行IT巡检用例：

- **OCR识别服务**：OCR识别、虚拟号段判断
- **文件处理服务**：代偿凭证/放款凭证文件下载验证
- **微众银行接口**：订单状态推送
- **imgp通知接口**：通知推送（含bizNo字段）
- **快手渠道接口**：还款结果拉取（order_repay查询）
- **头条渠道接口**：调额账单记录
- **华兴银行接口**：合同文件下载
- **半流程协议接口**：协议拉取

---

## 4. Apollo配置清单

执行前需确认以下6个Apollo配置项的当前值：

| 配置Key | 类型 | 建议测试值 | 执行后是否需要恢复 |
|---------|------|-----------|-----------------|
| `aps.apollo.function.switch.taskScheduleExecuteOptimizeSwitch` | boolean | true/false轮换 | 是（默认false） |
| `aps.apollo.function.switch.taskScheduleParamPoolSwitch` | boolean | true/false轮换 | 是（默认false） |
| `aps.apollo.config.taskScheduleAllowedPoolNames` | JSON Array | 按需添加测试池 | 是 |
| `aps.apollo.config.taskSchedulePoolNameMap` | JSON Object | 按需添加映射 | 是 |
| `aps.apollo.config.taskScheduleDefaultPoolName` | string | aps_task_execute_pool | 否（默认值） |
| `aps.apollo.config.threadPoolInfoServiceModule` | string | APS/PPS轮换 | 是（默认APS） |

---

## 5. 数据库依赖

| 库 | 表 | 子系统 | 验证SQL |
|----|-----|--------|---------|
| aps | thread_pool | aps-app | `SELECT poor_code, core_size, max_size, queue_size FROM thread_pool WHERE module = 'APS' ORDER BY poor_code` |

### 预置数据要求

- APS module 下至少21条线程池记录（`thread_pool_aps_module_init.sql` 执行后应存在）
- PPS module 下历史线程池记录（向后兼容测试需要）

---

## 6. 依赖链（io_bindings）

```
配置修改(apollo-config) → 触发任务(lingxi-scheduler) → 日志验证(query-log)
                                                     → DB验证(sql-execute)
```

### pending_data（需外部提供的参数）

| 参数 | 说明 | 获取方式 |
|------|------|---------|
| `task_name` | 测试用JSS任务名 | 从 lingxi-scheduler 获取可用任务列表 |
| `test_pool_name` | 测试用线程池名 | 从 thread_pool 表查询 `module='APS'` |
| `jss_task_params` | JSS任务参数 | 根据实际JSS任务配置组装 |

---

## 7. 日志验证清单

### 7.1 核心关键字

| 场景 | 关键字 | 用途 |
|------|--------|------|
| 池解析 | `ScheduledTaskExecutorResolver.resolvePoolName` | 确认新路径池选择 |
| 白名单拒绝 | `scheduled task pool rejected` / `WARN` | 确认非法池被拒绝 |
| 锁获取 | `task lock acquired` / `getInstanceWithTry` | 确认异步线程内拿锁 |
| 锁失败 | `task lock failed` / `skip` | 确认抢锁失败跳过执行 |
| 最终兜底 | `fallback to task_default_pool` | 确认降级兜底 |
| 模块加载 | `threadPoolInfoServiceModule` / `APS` / `PPS` | 确认模块加载 |
| 旧路径 | `before submit to pool` | 确认旧路径行为 |
| 新路径 | `after submit to pool` | 确认新路径行为 |
| 异常处理 | `handle exception` / `lock released` | 确认异常+锁释放 |

### 7.2 查询参数

- **应用**: aps-app
- **环境**: STG1
- **方式**: 通过 `Skill(testmind-facade)` → `testmind:query-log`

---

## 8. 执行风险

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| Apollo配置修改影响其他测试 | 中 | 执行前后记录并恢复原值 |
| JSS任务触发影响线上数据 | 中 | 使用测试专用任务和参数 |
| 线程池配置错误导致任务阻塞 | 低 | 测试后恢复默认配置 |
| IT巡检用例Block无法执行 | 高 | 需Platform Manager先录入接口 |
| testmind:lingxi-scheduler 参数不明确 | 中 | 首次执行前需确认参数格式 |

---

## 9. 下一步行动

1. **[必需]** 确认 `testmind:lingxi-scheduler` 和 `testmind:schedule` 的具体调用参数
2. **[必需]** 确认测试环境 STG1 的 Apollo 配置当前值
3. **[必需]** 从 `thread_pool` 表获取测试可用线程池名
4. **[建议]** 通过 Platform Manager 注册 IT 巡检用例所需的渠道接口
5. **[建议]** 确认 JSS 任务列表中可用于测试的任务名

---

## 10. 阻塞项

| # | 阻塞项 | 影响范围 | 优先级 |
|---|--------|---------|--------|
| B-1 | IT巡检日常巡视8条用例无平台接口 | 8条用例不可执行 | 高 |
| B-2 | third_repay_withhold 业务流程接口缺失 | 1条用例仅可DB验证 | 中 |
| B-3 | lingxi-scheduler 技能参数需确认 | 所有线程池用例 | 中 |

---

## 更新记录

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-07-02 | 初始生成，37条用例映射，28条可执行，9条blocked | test-mapper agent |
