# 线程池配置隔离 代码分析报告

> 需求: NREQUEST-49352 (API接口IT巡检202606) -- 条目3: 历史遗留债务，线程池配置隔离
> 分析日期: 2026-06-29
> 分析范围: 25 commits, 核心聚焦 commit 47ccae75 + 7a31ece + 15d6ee60

---

## 一、线程池配置变更总览

### 1.1 核心变更文件

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `spring/threadpool/spring-threadpool.xml` | 修改 | module 从硬编码 `PPS` 改为 `${aps.apollo.config.threadPoolInfoServiceModule:APS}` |
| `sql/thread_pool_aps_module_init.sql` | 新增 | APS module 线程池种子数据 (22个池) |
| `ScheduledTaskExecutorResolver.java` | 新增 | 定时任务线程池解析器 |
| `AbstractCronTaskClientService.java` | 修改 | 支持优化路径: submit-before-lock |
| `AbstractApsExecuteScheduledService.java` | 修改 | 支持优化路径 |
| `AbstractApsExecuteScheduledMultiThreadService.java` | 修改 | 支持优化路径 |
| `TaskParam.java` | 修改 | 新增 `taskPoolName` 字段 |
| `ApsTaskParam.java` | 修改 | 新增 `taskPoolName`, `resolvedTaskPoolName` 等字段 |

### 1.2 新增线程池

| 池名 | coreSize | maxSize | keepAlive | queueSize | policy | 用途 |
|------|----------|---------|-----------|-----------|--------|------|
| **aps_task_execute_pool** | 20 | 100 | 200 | 10000 | CallerRunsPolicy | 定时任务默认执行池 (替代 task_default_pool) |
| **aps_task_long_pool** | 5 | 20 | 200 | 1000 | **AbortPolicy** | 长耗时定时任务专用池 (如文件下载) |

### 1.3 APS Module 种子数据迁移池 (从PPS复制)

共20个池从PPS module迁移至APS module，包括: `task_default_pool`, `loanmarket_pool`, `credit-apply-pool`, `loan-apply-pool`, `push_contract_pool`, `sms_delayed_pool`, `tis_pull_file_pool`, `credit_check_pool`, `msf-default-pool` 等。

### 1.4 线程池参数对比

| 参数 | aps_task_execute_pool (默认池) | aps_task_long_pool (长任务池) | task_default_pool (旧默认池) |
|------|-------------------------------|------------------------------|------------------------------|
| coreSize | 20 | **5** | 20 |
| maxSize | 100 | **20** | 100 |
| keepAlive | 200 | 200 | 200 |
| queueSize | 10000 | **1000** | 10000 |
| policy | CallerRunsPolicy | **AbortPolicy** | CallerRunsPolicy |

---

## 二、线程池选择机制 (ScheduledTaskExecutorResolver)

### 2.1 Apollo 开关

| Apollo Key | 默认值 | 说明 |
|-----------|--------|------|
| `aps.apollo.function.switch.taskScheduleExecuteOptimizeSwitch` | `false` | 总开关，控制是否启用优化路径 |
| `aps.apollo.function.switch.taskScheduleParamPoolSwitch` | `false` | 是否允许 JSS taskParam 指定线程池 |
| `aps.apollo.config.taskScheduleDefaultPoolName` | `aps_task_execute_pool` | 默认定时任务池 |
| `aps.apollo.config.taskSchedulePoolNameMap` | `{}` | taskName → poolName 映射 |
| `aps.apollo.config.taskScheduleAllowedPoolNames` | `["aps_task_execute_pool","aps_task_long_pool"]` | 白名单 |

### 2.2 池选择优先级 (优化路径开启时)

```
1. taskParam.taskPoolName (需 paramPoolSwitch=true) → 白名单校验
2. Apollo taskSchedulePoolNameMap[taskName]        → 白名单校验
3. 内置映射 resolveBuiltInPoolName(taskName)        → 白名单校验  ★ 关键
4. Apollo taskScheduleDefaultPoolName               → 白名单校验
5. 兜底: task_default_pool
```

### 2.3 内置映射 (代码硬编码)

```java
// ScheduledTaskExecutorResolver.java (commit 7a31ece)
private static final String PARTNER_FILE_DOWNLOAD_TASK = "partnerFileDownloadTask";
private static final String TASK_SCHEDULE_LONG_POOL = "aps_task_long_pool";

private String resolveBuiltInPoolName(String taskName) {
    if (PARTNER_FILE_DOWNLOAD_TASK.equals(taskName)) {  // 精确匹配
        return TASK_SCHEDULE_LONG_POOL;
    }
    return null;
}
```

**仅一条内置规则**: 任务名 `"partnerFileDownloadTask"` → `aps_task_long_pool`。

---

## 三、PartnerFileDownloadTask 系列类族谱

### 3.1 继承层次

```
AbstractJssTriggerClient (JSS框架基类)
  └── AbstractCronTaskClientService (定时任务抽象基类, 包含 process/processThread)
        ├── PartnerFileDownloadTask              ★ 基类, bean="partnerFileDownloadTask"
        ├── BoHaiBkPartnerFileDownloadTask       bean="boHaiBkPartnerFileDownloadTask"
        ├── JiangSuBkPartnerFileDownloadTask     bean="jiangSuBkVoucherFileDownloadTask"
        ├── SykcfcPartnerFileDownloadTask        bean="sykcfcPartnerFileDownloadTask"
        ├── NingYinXJPartnerFileDownloadTask     bean="ningYinXJVoucherFileDownloadTask"
        ├── SuShangBKPartnerFileDownloadTask     bean="suShangBKVoucherFileDownloadTask"
        └── BoHaiXiaoWeiPartnerFileDownloadTask  bean="boHaiXiaoWeiPartnerFileDownloadTask"
```

所有7个类均直接继承 `AbstractCronTaskClientService`，无中间抽象层。

### 3.2 执行模型

| 类 | 执行方式 | 说明 |
|----|---------|------|
| **PartnerFileDownloadTask** | 集中分发 | 通过 `PartnerFileDownloadDistributeServiceImpl.distributeDownload()` 按 partnerCode 分发到各渠道处理器 |
| 其他6个子类 | 独立执行 | 各自调用对应渠道的 BizService 方法 (如 `boHaiBkFileDownloadBizService.batchDownloadVoucherFile()`) |

### 3.3 线程池使用情况

**改动前**: 所有 PartnerFileDownloadTask 通过 `AbstractCronTaskClientService.process()` → `ThreadPoolUtil.submit("task_default_pool", ...)` 提交到**共享的** `task_default_pool`。

**改动后 (优化路径关闭时)**: 行为不变，仍使用 `task_default_pool`。

**改动后 (优化路径开启时)**:

| 子类 (Spring Bean名) | JSS taskName (推测) | 解析到的池 | 规则来源 |
|----------------------|---------------------|-----------|---------|
| partnerFileDownloadTask | "partnerFileDownloadTask" | **aps_task_long_pool** | 内置映射 ✓ |
| boHaiBkPartnerFileDownloadTask | "boHaiBkPartnerFileDownloadTask" | aps_task_execute_pool | Apollo默认 |
| jiangSuBkVoucherFileDownloadTask | "jiangSuBkVoucherFileDownloadTask" | aps_task_execute_pool | Apollo默认 |
| sykcfcPartnerFileDownloadTask | "sykcfcPartnerFileDownloadTask" | aps_task_execute_pool | Apollo默认 |
| ningYinXJVoucherFileDownloadTask | "ningYinXJVoucherFileDownloadTask" | aps_task_execute_pool | Apollo默认 |
| suShangBKVoucherFileDownloadTask | "suShangBKVoucherFileDownloadTask" | aps_task_execute_pool | Apollo默认 |
| boHaiXiaoWeiPartnerFileDownloadTask | "boHaiXiaoWeiPartnerFileDownloadTask" | aps_task_execute_pool | Apollo默认 |

### 3.4 @Async 注解情况

**无 @Async 注解**: 所有7个 PartnerFileDownloadTask 类及其父类 `AbstractCronTaskClientService` 均不使用 Spring `@Async`。任务异步执行通过 `ThreadPoolUtil.submit(poolName, target, methodName, args...)` 反射方式提交。

---

## 四、问题清单

### 问题 1: 内置映射覆盖率不足 [风险等级: HIGH]

**描述**: `resolveBuiltInPoolName()` 仅硬编码匹配任务名 `"partnerFileDownloadTask"`，仅覆盖 1/7 (14%) 的 PartnerFileDownloadTask 子类。

**影响**:
- 6 个独立渠道文件下载任务 (渤海银行、江苏银行、苏银凯基、宁银消金、苏商银行、渤海小微) **不被内置映射覆盖**
- 这些任务在优化路径开启后，将使用 Apollo 默认池 `aps_task_execute_pool` (core=20, max=100, CallerRunsPolicy)
- 文件下载是 IO 密集型长耗时操作，如果多个渠道同时执行，可能阻塞 `aps_task_execute_pool` 中的其他定时任务

**根本原因**: 使用精确字符串匹配而非前缀/模式匹配。如果 JSS taskName 不是恰好 `"partnerFileDownloadTask"`，就不会命中。

**涉及文件**:
- `aps-app/src/main/java/com/qihoo/finance/aps/common/task/service/ScheduledTaskExecutorResolver.java`

**触发条件**: `taskScheduleExecuteOptimizeSwitch=true`, 未配置 Apollo `taskSchedulePoolNameMap` 覆盖。

---

### 问题 2: aps_task_long_pool 使用 AbortPolicy 存在任务拒绝风险 [风险等级: MEDIUM]

**描述**: `aps_task_long_pool` 配置为 `AbortPolicy` (拒绝策略)。当池满 (core=5 全忙 + queue=1000 满) 时，新提交的任务会被直接拒绝并抛出 `RejectedExecutionException`。

**影响**:
- 文件下载任务 (PartnerFileDownloadTask) 处理时间不确定，可能长时间占用线程
- 如果 5 个核心线程都被长任务占用，且队列积压超 1000，后续触发将被拒绝
- 被拒绝的任务不会重试，可能导致某次文件下载丢失

**对比**: `aps_task_execute_pool` 和 `task_default_pool` 使用 `CallerRunsPolicy` (调用者运行)，不会丢失任务。

**涉及配置**:
```sql
('aps_task_long_pool', 'APS', 5, 20, 200, 1000, 'AbortPolicy')
```

---

### 问题 3: 内置映射优先级低于 Apollo map 但高于 Apollo default [风险等级: LOW]

**描述**: 代码内置映射 (第3优先级) 可能在 Apollo 配置不当时产生意外的行为组合:
- 如果 Apollo `taskSchedulePoolNameMap` 中配置了 `"partnerFileDownloadTask": "some_other_pool"`，则内置映射被**覆盖** (Apollo map 优先级更高)
- 如果 Apollo `taskScheduleDefaultPoolName` 默认值被修改为非白名单值，内置映射成为最后的有效配置

**当前风险低**，因为这是设计如此 (Apollo 配置优先于内置映射)，但运维人员需要知道这个优先级关系。

---

### 问题 4: coreSize=5 对并发文件下载可能不足 [风险等级: MEDIUM]

**描述**: `aps_task_long_pool` 的核心线程数仅为 5。如果 `PartnerFileDownloadTask` 同时处理多个合作方的文件下载 (通过 distributeDownload 分发)，实际并发度受限于 5。

**影响**:
- `PartnerFileDownloadTask` 的 `selectTasks()` 中按 `taskBatchDateList` 循环调用 `distributeDownload()`，每个合作方都可能涉及多个文件
- 如果 distribute 内部对每个合作方提交异步任务，这些任务共享 5 个核心线程
- 峰值时可能出现任务排队

**建议**: 观察生产环境文件下载任务的实际并发数和平均耗时，评估是否需要调整 coreSize。

---

### 问题 5: 单个 taskParam 新增字段在旧路径下的兼容性 [风险等级: LOW]

**描述**: `TaskParam` 和 `ApsTaskParam` 新增了 `taskPoolName`, `resolvedTaskPoolName`, `taskLockedBeforeHandle`, `taskRunning`, `inlineFirstPartition` 字段。

**影响**:
- 这些字段使用包装类型或默认值，JSON 反序列化时缺失字段不会报错
- `taskLockedBeforeHandle` 默认为 `Boolean.TRUE`，保持旧行为 (`processThread` 假设锁已在提交前获取)
- commit 15d6ee60 额外增加了 `Boolean` 包装类型的重载方法 (`processThread(TaskParam, String, String, Boolean)`) 以兼容 `ThreadPoolUtil` 反射调用

**当前风险低**: 兼容性已通过代码和测试覆盖。

---

## 五、测试建议

### 5.1 Apollo 开关组合测试

| 场景 | taskScheduleExecuteOptimizeSwitch | taskScheduleParamPoolSwitch | 预期行为 |
|------|----------------------------------|-----------------------------|---------|
| S1 | false | false | 旧路径: 先锁后提交到 task_default_pool |
| S2 | true | false | 优化路径: 内置映射生效, partnerFileDownloadTask → aps_task_long_pool |
| S3 | true | true | 优化路径: taskParam 池优先, 校验白名单 |

### 5.2 PartnerFileDownloadTask 线程池验证

| 测试点 | 验证方法 |
|--------|---------|
| partnerFileDownloadTask 使用 aps_task_long_pool | 开启 optimize switch → 日志确认池名 |
| 其他 6 个渠道任务使用 aps_task_execute_pool | 日志确认未命中内置映射, 使用 default |
| Apollo map 覆盖内置映射 | 配置 taskSchedulePoolNameMap 后验证优先级 |
| aps_task_long_pool 拒绝策略行为 | 并发触发超过 maxSize+queueSize 验证 AbortPolicy 日志 |

### 5.3 锁时序验证

| 测试点 | 验证方法 |
|--------|---------|
| 优化路径: 锁在 processThread 内获取 | process 阶段不调 lock, processThread 阶段调 lock |
| 旧路径: 锁在 submit 前获取 | process 阶段调 lock, processThread 阶段不再调 lock |
| 锁异常释放 | submit 失败后验证 unLock 被调用 |

### 5.4 回滚路径验证

| 测试点 | 操作 |
|--------|------|
| 整体回滚 | 设置 taskScheduleExecuteOptimizeSwitch=false |
| 模块回滚 | 设置 aps.apollo.config.threadPoolInfoServiceModule=PPS |
| 池回滚 | 从 taskScheduleAllowedPoolNames 中移除异常池名 |

### 5.5 建议补充的 Apollo 配置

为覆盖问题1中提到的6个未隔离的渠道文件下载任务, 建议在 Apollo `taskSchedulePoolNameMap` 中添加:

```json
{
  "boHaiBkPartnerFileDownloadTask": "aps_task_long_pool",
  "jiangSuBkVoucherFileDownloadTask": "aps_task_long_pool",
  "sykcfcPartnerFileDownloadTask": "aps_task_long_pool",
  "ningYinXJVoucherFileDownloadTask": "aps_task_long_pool",
  "suShangBKVoucherFileDownloadTask": "aps_task_long_pool",
  "boHaiXiaoWeiPartnerFileDownloadTask": "aps_task_long_pool"
}
```

> 注意: 添加前需确认各渠道文件下载任务的实际 JSS taskName (可能与 Spring bean 名一致, 也可能不一致)。

---

## 六、总结

本次"线程池配置隔离"改动整体设计合理, 通过 Apollo 开关实现了渐进式上线和快速回滚能力。核心架构变更包括:

1. **模块独立**: 线程池配置从 PPS module 迁移到 APS module
2. **池隔离**: 新增 `aps_task_execute_pool` (默认) 和 `aps_task_long_pool` (长任务)
3. **锁优化**: 优化路径下锁从 submit 前移到 async 线程内, 避免队列持锁
4. **可观测性**: 白名单校验 + WARN 日志, 方便排查池选择问题

**主要风险**: 内置映射仅覆盖 1/7 的文件下载任务类。建议通过 Apollo `taskSchedulePoolNameMap` 补全其余 6 个渠道任务的池映射, 或考虑将内置匹配改为前缀匹配模式 (如 `endsWith("PartnerFileDownloadTask")`)。

**验证重点**: 关注 `aps_task_long_pool` 的 AbortPolicy 在生产环境是否导致任务拒绝, 以及 coreSize=5 是否满足并发需求。
