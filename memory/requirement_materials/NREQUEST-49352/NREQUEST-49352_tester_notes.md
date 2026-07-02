# NREQUEST-49352 测试说明

## 状态

> 未找到该需求的测试说明文档。需联系测试负责人确认测试策略。

## 测试负责人

> 未能通过 testmind:request-manage 获取测试负责人信息，需用户确认。

## 关键测试点（从需求内容提取）

### 1. APS 部署优化测试
- 验证 APS 系统部署耗时是否有改善
- 验证懒加载后功能是否正常
- 验证非必要资源是否正确延迟加载

### 2. 日常巡视问题验证

#### 2.1 OCR 识别优化
- 验证 OCR 识别失败时记录的具体失败原因
- 验证虚拟号段半流程拉取协议时是否正确拒绝（不再出现 NP 异常）
- 验证 V4 授信上送过程中身份证 OCR 识别过期返回

#### 2.2 代偿/放款凭证
- 验证合作方只上传 yyyymmdd.ok 文件时的错误日志
- 确认对业务无影响

#### 2.3 微众银行订单推送
- 验证借据状态为终态时是否不再通知

#### 2.4 imgp 通知
- 验证 bizNo 为空时通知不失败

#### 2.5 快手还款结果
- 验证 order_repay 不存在时返回 RECORD_NOT_EXISTS（而非 BUSINESS_FAIL）

#### 2.6 third_repay_withhold 去重
- 验证表中无重复数据

#### 2.7 头条调额
- 验证同一条流水不会出现多笔订单

#### 2.8 合同下载告警
- 验证 D 日无合同文件时不再触发告警

#### 2.9 空指针异常
- 验证半流程拉取协议不再出现空指针异常

### 3. 线程池配置隔离（历史遗留债务）

> 负责人：黄叶鑫 | 代码仓库：aps-app | 用例数量：28条
>
> 参考文档：
> - IT巡检用例 (it巡检.xlsx)
> - [APS 定时任务隔离 & 平安普惠代扣幂等评审材料](aps-scheduled-task-and-pinganph-idempotent-review.html)

#### 3.1 需求背景

**历史遗留问题**：
1. 线程池配置模块硬编码为 PPS，无法按业务隔离
2. 所有定时任务共用 `task_default_pool`，长任务（如文件下载）会阻塞短任务
3. 触发线程在提交线程池**前**获取分布式锁，排队期间也持锁，放大了锁的影响范围

**修改方案**：
1. 新增 `ScheduledTaskExecutorResolver`，按四级优先级选择执行线程池
2. 优化路径：先投递线程池 → 异步线程内再抢锁（锁只保护执行窗口）
3. 线程池配置模块从硬编码 PPS 改为 Apollo 可配（`threadPoolInfoServiceModule`，默认 APS）
4. 新增 APS 模块 21 个线程池 seed SQL（`thread_pool_aps_module_init.sql`）

#### 3.2 Apollo 配置清单

| 配置 Key | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `aps.apollo.function.switch.taskScheduleExecuteOptimizeSwitch` | boolean | `false` | 优化路径总开关，控制是否启用"先投递、异步内抢锁" |
| `aps.apollo.function.switch.taskScheduleParamPoolSwitch` | boolean | `false` | 参数池开关，控制 JSS 参数 `taskPoolName` 是否允许覆盖执行池 |
| `aps.apollo.config.taskScheduleAllowedPoolNames` | JSON Array | `["aps_task_execute_pool","aps_task_long_pool"]` | 白名单，限制参数和映射不能把任务导入非预期业务池 |
| `aps.apollo.config.taskSchedulePoolNameMap` | JSON Object | `{}` | 按任务名→池名的兜底映射（优先级2） |
| `aps.apollo.config.taskScheduleDefaultPoolName` | string | `aps_task_execute_pool` | 默认调度任务池（优先级4） |
| `aps.apollo.config.threadPoolInfoServiceModule` | string | `APS` | MSF 线程池配置读取 module，必要时可临时回 PPS |

#### 3.3 线程池选择四级优先级

```
优先级1: 任务参数 taskPoolName（需 paramPoolSwitch=true + 白名单校验）
    ↓ 未命中
优先级2: Apollo PoolNameMap 按 taskName 映射（需白名单校验）
    ↓ 未命中
优先级3: 内置映射（partnerFileDownloadTask → aps_task_long_pool）
    ↓ 未命中
优先级4: Apollo taskScheduleDefaultPoolName 默认池
    ↓ 未命中/非法
最终兜底: task_default_pool
```

#### 3.4 测试维度与用例分布

| 维度 | 用例数 | 覆盖点 |
|------|--------|--------|
| 一、优化开关控制 | 2 | 开关关闭走旧路径、开关开启走新路径 |
| 二、线程池选择四级优先级 | 6 | 参数池指定、白名单拒绝、PoolNameMap、内置映射、默认池、最终兜底 |
| 三、JSS参数兼容性 | 3 | Legacy Cron(name字段)、APS Execute(taskName字段)、paramPoolSwitch开关 |
| 四、锁行为变更 | 3 | 旧路径先锁后提交、新路径异步内抢锁失败跳过、任务锁自动续期 |
| 五、线程池资源与隔离 | 4 | 不同任务池隔离、长任务不阻塞短任务、21个池seed数据校验、module加载 |
| 六、异常与兜底 | 3 | 新路径handle异常锁释放、旧路径提交失败锁释放、池不存在时报错 |
| 七、动态配置生效 | 2 | 开关false→true实时生效、PoolNameMap动态修改生效 |
| 八、多线程任务 | 3 | 外层+分片统一池、首分片内联执行、分片取消机制 |
| 九、历史遗留兼容 | 2 | PPS模块回退兼容、旧task_default_pool向后兼容 |

#### 3.5 关键测试场景

**必须验证的核心场景**：
1. ✅ 开关关闭 → 旧路径：提交前拿锁，提交到 task_default_pool
2. ✅ 开关开启 → 新路径：Resolver 选池 → 提交 → 异步线程内拿锁
3. ✅ 文件下载任务（partnerFileDownloadTask）→ 内置映射到 aps_task_long_pool
4. ✅ 白名单拒绝 → WARN 日志 + 继续降级
5. ✅ 四级全未命中 → 最终兜底 task_default_pool
6. ✅ 新路径抢锁失败 → 不执行 selectTasks/execute
7. ✅ handle 异常 → finally 正确释放锁
8. ✅ APS 模块 21 个池 seed 数据完整性
9. ✅ module 回退 PPS → 仍可正常工作
10. ✅ 开关动态切换 → 无需重启实时生效

**JSS 参数易错点**：
- Legacy Cron 任务 → 用 `"name"` 字段（非 `"taskName"`）
- APS Execute 任务 → 用 `"taskName"` 字段（非 `"name"`）
- 线程池字段统一 → `"taskPoolName"`

**不生效排查顺序**（参考评审文档）：
1. `taskScheduleExecuteOptimizeSwitch` 是否为 true？
2. `taskScheduleParamPoolSwitch` 是否为 true（如依赖参数指定）？
3. 目标池是否在 `taskScheduleAllowedPoolNames` 白名单中？
4. 目标池是否在 `thread_pool` 表 APS module 下真实存在？
5. JSS 参数字段名是否正确（name vs taskName）？

#### 3.6 数据库表分布

| 库 | 表 | 用途 |
|----|-----|------|
| aps | thread_pool | 线程池配置表，按 module 区分 APS/PPS |

验证 SQL：
```sql
-- 检查 APS 模块 21 个线程池
SELECT poor_code, core_size, max_size, queue_size 
FROM thread_pool WHERE module = 'APS' ORDER BY poor_code;

-- 检查 PPS 模块历史池（向后兼容）
SELECT poor_code, core_size, max_size, queue_size 
FROM thread_pool WHERE module = 'PPS' ORDER BY poor_code;
```

#### 3.7 日志关键字

| 场景 | 关键字 | 用途 |
|------|--------|------|
| 池解析 | `ScheduledTaskExecutorResolver.resolvePoolName` | 确认走了新路径的池选择逻辑 |
| 白名单拒绝 | `scheduled task pool rejected` / WARN | 确认非法池被正确拒绝 |
| 任务锁获取 | `task lock acquired` / `getInstanceWithTry` | 确认锁在异步线程内获取 |
| 锁获取失败 | `task lock failed` / `skip` | 确认抢锁失败跳过业务执行 |
| 最终兜底 | `fallback to task_default_pool` | 确认降级到最终兜底池 |
| 模块加载 | `threadPoolInfoServiceModule` / `APS` | 确认加载了正确的模块池 |

## 更新记录

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-06-26 | 初始创建，从需求内容提取关键测试点 | wangxue-jk |
| 2026-06-29 | 重写条目3：线程池配置隔离，参考IT巡检用例+APS评审文档，生成28条用例覆盖9个测试维度 | wangxue-jk |
