# 用例代码分析报告

> 需求编号: NREQUEST-49352
> 关联 Story: JYSG-149999 (API流量IT巡检202606)
> 迭代版本: 20260702
> 仓库: 360jr-mkt/aps
> 分支: feature/aps1.332.0_20260702
> 分析日期: 2026-06-26
> 变更规模: 85个文件, +7123/-175行 (核心Java/XML/SQL: 41文件, +2414/-135行)

---

## 一、变更模块总览

| # | 模块 | API编号 | 核心变更 | 风险等级 |
|---|------|---------|---------|---------|
| 1 | 定时任务线程池隔离 | API-10523 | 线程池从PPS迁移到APS，池隔离与解析 | 🔴 高 |
| 2 | 平安普惠第三方还款幂等控制 | API-10523 | Redis分布式锁实现幂等防护 | 🔴 高 |
| 3 | 合作方协议框架 | API-10416/10417/10477/10478 | 协议版本快照、SFTP下载、模式查询 | 🟡 中 |
| 4 | Prometheus度量监控 | API-10531 | 通用度量工具（MeasureUtil）与Counter | 🟢 低 |
| 5 | 半流程合同手机号段校验 | API-10524 | 5G号段限制拉取合同 | 🟡 中 |
| 6 | 宁银拒量融单OK文件优化 | API-10524 | 日期文件处理逻辑调整 | 🟡 中 |
| 7 | 身份证OCR识别错误调整 | API-10524 | OCR识别错误返回码修正 | 🟡 中 |
| 8 | 头条调额账单多订单场景 | API-10525 | 同一流水号多笔订单处理 | 🟡 中 |
| 9 | IT巡检华兴协议优化 | API-10526 | 空批次自动置成功 | 🟢 低 |
| 10 | Apollo配置变更 | - | 新增开关/配置项 | 🟡 中 |

---

## 二、模块详细分析与测试点

### 2.1 定时任务线程池隔离 (API-10523) 🔴 高

#### 变更文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `ScheduledTaskExecutorResolver.java` | **新增** | 核心解析器：三级池名解析 + 白名单校验 |
| `AbstractApsExecuteScheduledMultiThreadService.java` | 修改 | 优化调度执行：池解析 → 锁分离 → 内联首分片 |
| `AbstractCronTaskClientService.java` | 修改 | Cron任务接入池解析 |
| `AbstractApsExecuteScheduledService.java` | 修改 | 单线程调度服务适配 |
| `AbstractApsLoopQueryExecuteService.java` | 修改 | 循环查询服务适配 |
| `ApsTaskParam.java` | 修改 | 新增6个字段（taskPoolName, resolvedTaskPoolName, taskLockedBeforeHandle, taskRunning, inlineFirstPartition等） |
| `ApsMultiTaskParam.java` | 修改 | 新增分片控制字段 |
| `TaskParam.java` | 修改 | 新增taskPoolName字段 |
| `spring-threadpool.xml` | 修改 | module从硬编码"PPS"改为Apollo配置 |
| `thread_pool_aps_module_init.sql` | **新增** | 21个线程池种子数据 |

#### 调度任务线程池解析逻辑 (ScheduledTaskExecutorResolver)

```
resolvePoolName(taskName, taskPoolName):
  1. taskScheduleParamPoolSwitch=true AND task参数有指定池
     → 白名单校验 → 通过则使用
  2. Apollo配置 taskSchedulePoolNameMap 有该taskName映射
     → 白名单校验 → 通过则使用
  3. 内置规则：partnerFileDownloadTask → aps_task_long_pool
     → 白名单校验 → 通过则使用
  4. Apollo配置 taskScheduleDefaultPoolName (默认: aps_task_execute_pool)
     → 白名单校验 → 通过则使用
  5. 最终兜底 → task_default_pool (警告日志)
```

#### 池隔离开关 (Apollo)
| 配置Key | 类型 | 默认值 | 说明 |
|---------|------|--------|------|
| `aps.apollo.function.switch.taskScheduleExecuteOptimizeSwitch` | boolean | false | 总开关，控制是否启用优化路径 |
| `aps.apollo.function.switch.taskScheduleParamPoolSwitch` | boolean | false | 是否允许任务参数指定线程池 |
| `aps.apollo.config.taskScheduleDefaultPoolName` | String | aps_task_execute_pool | 默认线程池名称 |
| `aps.apollo.config.taskSchedulePoolNameMap` | JSON Map | {} | 按任务名映射线程池 |
| `aps.apollo.config.taskScheduleAllowedPoolNames` | JSON List | ["aps_task_execute_pool","aps_task_long_pool"] | 允许的线程池白名单 |
| `aps.apollo.config.threadPoolInfoServiceModule` | String | APS | 线程池信息模块名 |

#### 线程池种子数据 (新增21个池)

| 线程池 poor_code | core/max | queue | policy | 用途 |
|-------------------|----------|-------|--------|------|
| aps_task_execute_pool | 20/100 | 10000 | CallerRunsPolicy | **默认调度执行池** |
| aps_task_long_pool | 5/20 | 1000 | AbortPolicy | **长任务专用池** (partnerFileDownloadTask) |
| task_default_pool | 20/100 | 10000 | CallerRunsPolicy | 兜底默认池 |
| pps-notice-pool | 10/100 | 10000 | CallerRunsPolicy | 通知 |
| loanmarket_pool | 16/64 | 1000 | AbortPolicy | 贷款市场 |
| credit-apply-pool | 10/100 | 10000 | CallerRunsPolicy | 授信申请 |
| loan-apply-pool | 10/100 | 10000 | CallerRunsPolicy | 放款申请 |
| push_contract_pool | 4/8 | 200 | AbortPolicy | 推送合同 |
| sms_delayed_pool | 1/2 | 200 | AbortPolicy | 延迟短信 |
| credit_check_pool | 10/100 | 1000 | CallerRunsPolicy | 授信检查 |
| ... (其余11个) | | | | 从PPS迁移 |

#### 新旧路径对比

| 维度 | 旧路径 (optimizeSwitch=false) | 新路径 (optimizeSwitch=true) |
|------|------------------------------|------------------------------|
| 池选择 | 固定 task_default_pool | 四级解析 → 按任务分配池 |
| 锁获取 | task提交前获取锁 | handle内获取锁（可与池提交解耦） |
| 首分片 | 所有分片提交到线程池 | 首分片在当前线程内联执行 |
| 锁过期 | 固定超时 | 定时续期（每分钟续期） |
| 分片取消 | 不支持 | 支持分片级取消 + 未提交分片跳过 |
| 异常恢复 | 无 | 提交失败时取消未启动分片 + countDown补齐 |

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T1 | optimizeSwitch=false 走旧路径 | 开关关闭 | 走旧路径: task提交前加锁 → task_default_pool执行 | P0 |
| T2 | optimizeSwitch=true 走新路径 | 开关开启 | 走新路径: 池解析 → 提交到指定池 → handle内加锁 | P0 |
| T3 | task名称匹配Apollo Map | 配置映射: partnerFileDownloadTask→aps_task_long_pool | 任务在aps_task_long_pool执行 | P0 |
| T4 | task参数指定池名(白名单内) | paramPoolSwitch=true, task指定aps_task_execute_pool | 使用task参数指定的池 | P1 |
| T5 | task参数指定池名(白名单外) | paramPoolSwitch=true, task指定非法池名 | 拒绝，fallback到下一级 | P1 |
| T6 | 所有级别都不匹配 → 兜底 | 无配置、无映射 | 最终使用task_default_pool + 输出WARN日志 | P1 |
| T7 | 多个调度任务并发执行 | 同时触发10个不同taskName | 各任务在正确池中执行，不互相阻塞 | P0 |
| T8 | 长任务不阻塞短任务 | partnerFileDownloadTask与普通task并发 | 长任务在aps_task_long_pool，不占用默认池 | P0 |
| T9 | 分片提交异常 → 优雅降级 | 线程池满导致提交失败 | 取消未启动分片+countDown补齐+等待已启动分片结束 | P1 |
| T10 | handle内获取锁失败 | 同任务已被另一个节点执行 | 跳过执行，输出WARN日志 | P1 |
| T11 | 锁续期机制 | 任务执行超过锁过期时间 | 每分钟自动续期，锁不过期 | P1 |
| T12 | 首分片内联执行 | inlineFirstPartition=true | 首分片在当前线程执行，其余提交到池 | P2 |
| T13 | 分片取消检测 | 执行中取消标志置位 | 分片内部检测取消 → 停止处理子任务 | P2 |
| T14 | 旧路径提交失败 → 解锁 | 池提交异常 | finally块正确解锁 | P1 |
| T15 | 新路径handle异常 → 解锁 | handle执行抛异常 | finally块：判断taskLocked → 正确解锁 | P1 |
| T16 | Cron任务走新路径 | optimizeSwitch=true | AbstractCronTaskClientService走池解析+processThread新签名 | P1 |
| T17 | DB thread_pool表数据完整性 | SQL执行后 | 21条记录全部正确写入，module='APS' | P0 |
| T18 | spring-threadpool.xml module可配置 | Apollo配置module=APS | ThreadPoolInfoService读取APS的线程池配置 | P1 |

---

### 2.2 平安普惠第三方还款幂等控制 (API-10523) 🔴 高

#### 变更文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `PingAnPhDebtQueryFacadeAdapter.java` | 修改 | collectOverdueRepay: Redis锁 + DB double-check |
| `PingAnPhBizService.java` | 修改 | repayConfirm + repayConfirm4RongDan: Redis锁幂等 |
| `PingAnPhOrderServiceProactivePay.java` | 修改 | 主动还款: Redis锁幂等 |
| `LockKeyGenerator.java` | 修改 | 新增 generatePingAnPhThirdRepayWithholdIdempotentLockKey() |
| `CreditSubmitServiceImpl.java` | 修改 | 授信提交适配 |
| `ApsApolloFunctionSwitch.java` | 修改 | 新增 isPingAnPhThirdRepayWithholdIdempotentSwitch() |

#### 幂等机制设计

```
锁Key格式: aps_pinganph_third_repay_withhold_idempotent_lock_{partnerCode}_{repayTranNo}
锁持有时间: 20000ms (20秒)
尝试获取等待: 1500ms (1.5秒)
```

**核心模式 (Double-Check Locking)**:
```
1. 无锁查询: 查DB是否已有记录 → 有则直接返回
2. 开关判断: isPingAnPhThirdRepayWithholdIdempotentSwitch()
3. 获取Redis锁 (try-with-resources, 20s lease, 1.5s try-wait)
4. 锁内再次查询: 查DB双重确认 → 有则返回
5. 执行业务操作 → 写DB
6. 自动释放锁
```

#### 涉及的四个接口场景

| 接口 | 方法 | 幂等控制点 | 说明 |
|------|------|-----------|------|
| 逾期代扣申请 | `collectOverdueRepay` | PingAnPhDebtQueryFacadeAdapter | 先查thirdRepayWithhold是否存在，不存在则加锁执行 |
| 批扣确认(消金) | `repayConfirm` | PingAnPhBizService | 锁内查询thirdRepayWithhold → 存在则跳过 |
| 批扣确认(融担-代偿后) | `repayConfirm4RongDan` | PingAnPhBizService | 先无锁查询 → 再加锁 double check |
| 主动还款 | `proactivePay` | PingAnPhOrderServiceProactivePay | 同上double-check模式 |

#### Apollo开关

| 配置Key | 默认值 | 说明 |
|---------|--------|------|
| `aps.apollo.function.switch.pingAnPhThirdRepayWithholdIdempotentSwitch` | false | 平安普惠第三方还款幂等总开关 |

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T19 | 幂等开关关闭 → 走旧路径 | switch=false | 不获取Redis锁，直接执行业务逻辑 | P0 |
| T20 | 幂等开关开启 → 走新路径 | switch=true | 获取Redis锁 → double-check → 执行业务 | P0 |
| T21 | 逾期代扣：首次请求正常执行 | switch=true, DB无记录 | 获取锁 → 执行业务 → 落库 → 释放锁 | P0 |
| T22 | 逾期代扣：重复请求幂等拦截（锁外查到） | switch=true, DB已有记录 | 无锁查询命中 → 直接返回已有结果 | P0 |
| T23 | 逾期代扣：重复请求幂等拦截（锁内查到） | switch=true, 并发两个相同请求 | 第一个加锁执行，第二个锁外未查到 → 获取锁 → 锁内查到 → 返回 | P0 |
| T24 | 逾期代扣：获取锁失败 | switch=true, Redis锁被占用且超时 | 抛出ApsBusinessException "获取幂等锁失败" | P1 |
| T25 | 批扣确认(消金)：重复请求幂等 | switch=true, repayTranNo相同 | 锁内查到已有记录 → 直接return不重复处理 | P1 |
| T26 | 批扣确认(融担代偿)：重复请求幂等 | switch=true, repayTranNo相同 | 先无锁查到已有记录 → 直接return | P1 |
| T27 | 批扣确认(融担代偿)：并发请求幂等 | switch=true, 并发两个相同请求 | 第一个加锁执行，第二个锁内查到 → return | P1 |
| T28 | 主动还款：并发请求幂等 | switch=true | 锁内double-check → 只执行一次 | P1 |
| T29 | Redis不可用 | switch=true, Redis连接失败 | 获取锁失败 → 抛出业务异常 | P1 |
| T30 | 锁自动过期 | 业务执行超20s未释放 | 锁自动过期 → 第二个请求可以获取锁 | P2 |
| T31 | LockKey格式正确性 | partnerCode=TEST, repayTranNo=123 | lockKey = aps_pinganph_third_repay_withhold_idempotent_lock_TEST_123 | P1 |

---

### 2.3 Prometheus度量监控 (API-10531) 🟢 低

#### 变更文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `MeasureUtil.java` | **新增** | 工具类: record/success/bizError/sysError/timeout/unknownError |
| `MeasureKeyEnum.java` | **新增** | 度量Key枚举（当前仅 self_test） |
| `MeasureResultEnum.java` | **新增** | 5种标准结果: success/biz_error/sys_error/timeout/unknown_error |
| `MetricsHolder.java` | 修改 | 新增 getOrAddMeasureCounter() + MEASURE_COUNTER_MAP |

#### 设计要点

- Counter命名: `aps_measure_calls_total`
- Tag维度: `measure_key` + `result`
- 低基数保证: MeasureKeyEnum必须是预定义枚举，禁止动态值
- 告警PromQL: 基于 ratio = biz_error / (success + biz_error) 配置比例告警

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T32 | self_test场景记录success | 调用MeasureUtil.success(SELF_TEST) | Counter increment, tag: result=success | P1 |
| T33 | self_test场景记录bizError | 调用MeasureUtil.bizError(SELF_TEST) | Counter increment, tag: result=biz_error | P1 |
| T34 | 传null key → 不记录 | measureKey=null | 输出WARN日志，不抛异常 | P2 |
| T35 | 传null result → 不记录 | result=null | 输出WARN日志，不抛异常 | P2 |
| T36 | Counter注册幂等 | 同一key+result调用两次 | 第二次复用已有Counter，不重复注册 | P2 |
| T37 | Prometheus endpoint可访问 | 应用启动后 | /actuator/prometheus 返回 aps_measure_calls_total | P1 |

---

### 2.4 Apollo配置变更汇总 🟡 中

#### 新增配置项完整清单

| # | 配置Key | 类型 | 默认值 | 所属模块 | 说明 |
|---|---------|------|--------|---------|------|
| 1 | `aps.apollo.function.switch.taskScheduleExecuteOptimizeSwitch` | boolean | false | 线程池隔离 | 调度任务优化总开关 |
| 2 | `aps.apollo.function.switch.taskScheduleParamPoolSwitch` | boolean | false | 线程池隔离 | 允许任务参数指定池 |
| 3 | `aps.apollo.config.taskScheduleDefaultPoolName` | String | aps_task_execute_pool | 线程池隔离 | 默认线程池名 |
| 4 | `aps.apollo.config.taskSchedulePoolNameMap` | JSON Map | {} | 线程池隔离 | 任务→池名映射 |
| 5 | `aps.apollo.config.taskScheduleAllowedPoolNames` | JSON List | ["aps_task_execute_pool","aps_task_long_pool"] | 线程池隔离 | 合法池名白名单 |
| 6 | `aps.apollo.config.threadPoolInfoServiceModule` | String | APS | 线程池隔离 | 线程池信息模块名 |
| 7 | `aps.apollo.function.switch.pingAnPhThirdRepayWithholdIdempotentSwitch` | boolean | false | 幂等控制 | 平安普惠还款幂等开关 |
| 8 | `aps.apollo.config.jinke.bankContract.emptyBatchSuccessPartnerCodeList` | JSON List | ["HuaXing"] | 华兴协议 | 空批次自动置成功渠道 |
| 9 | `aps.config.value.orderInfoReasonDescMaxLength` | int | 50 | 订单信息 | 原因描述最大长度 |

#### Apollo配置测试点

| # | 测试场景 | 配置项 | 测试操作 | 预期结果 | 优先级 |
|---|---------|--------|---------|---------|--------|
| T38 | 线程池隔离总开关开启/关闭 | optimizeSwitch | 动态切换true/false | 不需要重启，实时生效 | P0 |
| T39 | 任务池映射动态变更 | poolNameMap | 实时新增/修改映射 | 下次任务触发使用新映射 | P1 |
| T40 | 白名单动态调整 | allowedPoolNames | 新增/移除池名 | 不在白名单的池被拒绝 | P1 |
| T41 | 幂等开关动态开启/关闭 | idempotentSwitch | 动态切换 | 实时生效，不丢请求 | P0 |
| T42 | threadPoolInfoServiceModule | module名 | 配置为APS vs PPS | DB查询thread_pool表时使用正确module过滤 | P1 |
| T43 | 默认值回退 | 多个配置 | 设置非法值/空值 | 回退到代码中@Value指定的默认值 | P2 |

---

### 2.5 合作方协议框架 (API-10416/10417/10477/10478) 🟡 中

#### 变更要点

| 子模块 | 说明 | 涉及文件 |
|--------|------|---------|
| 协议版本快照 | 订单级指定协议版本，携程借款PLCCDS过渡 | PartnerAgreementService, PartnerAgreementInstanceExtMapper |
| VIPs SFTP合同下载 | 信用申请+放款确认时构建协议实例 | VipsOrderServicePushOrderInfo, PartnerAgreementService |
| 协议模式查询 | Dubbo Facade: AgreementModeQueryFacade | 新增Dubbo服务 |
| 合同编号保存 | 保存合同编号到协议实例 | PartnerAgreementService |
| 华兴空批次优化 | 协议下载ready后空批次自动置成功 | AbstractJinKeBankContractDownloadBizService |

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T44 | 协议版本快照：指定版本下单 | 订单指定协议版本 | 使用快照版本生成协议 | P1 |
| T45 | 协议版本快照：未指定版本 | 订单不指定协议版本 | 使用当前最新版本 | P1 |
| T46 | VIPs信用申请 SFTP下载协议 | Vips渠道信用申请 | 通过SFTP获取合同文件，构建协议实例 | P1 |
| T47 | VIPs放款确认 SFTP下载协议 | Vips渠道放款确认 | 通过SFTP获取合同文件，构建协议实例 | P1 |
| T48 | AgreementModeQueryFacade Dubbo查询 | 下游系统调用 | 返回协议模式及就绪状态 | P1 |
| T49 | 华兴空批次自动成功 | HuaXing渠道, 协议下载ready, batch为空 | 自动将批次状态置为成功 | P1 |
| T50 | 华兴空批次非HuaXing渠道 | 非HuaXing渠道, 空批次 | 不自动置成功，保持原逻辑 | P2 |
| T51 | 合同编号保存 | 协议下载完成 | contractNo正确保存到协议实例 | P2 |

---

### 2.6 半流程合同手机号段校验 (API-10524) 🟡 中

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T52 | 5G号段拉取合同 | 手机号为5G号段 | 允许拉取，正常返回合同 | P1 |
| T53 | 非5G号段拉取合同 | 手机号非5G号段 | 拒绝拉取，返回错误码 + 记录日志 | P1 |
| T54 | 手机号为空/异常 | 手机号null/空串 | 空指针防护，不抛异常 | P2 |

---

### 2.7 宁银拒量融单OK文件优化 (API-10524) 🟡 中

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T55 | 宁银拒量融单: 有OK文件+日期文件 | 正常场景 | 正常处理 | P1 |
| T56 | 宁银拒量融单: 只有OK文件无日期文件 | 异常场景(优化前失败) | 优化后正常处理，不依赖日期文件 | P1 |

---

### 2.8 身份证OCR识别错误调整 (API-10524) 🟡 中

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T57 | OCR识别错误 → 返回身份证过期 | OCR返回身份证OCR识别错误 | 不再错误返回身份证过期，返回正确错误码 | P1 |
| T58 | OCR正常识别 | 正常OCR结果 | 流程正常，无影响 | P1 |

---

### 2.9 头条调额账单多订单场景 (API-10525) 🟡 中

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T59 | 同一流水号对应多笔订单 | flowNo相同, 多笔订单 | 每笔订单都能正确处理，不丢失、不重复 | P1 |
| T60 | 同一流水号对应单笔订单 | flowNo唯一 | 正常处理（回归验证） | P1 |

---

### 2.10 IT巡检华兴协议优化 (API-10526) 🟢 低

#### 测试点

| # | 测试场景 | 前置条件 | 预期结果 | 优先级 |
|---|---------|---------|---------|--------|
| T61 | HuaXing空批次自动成功 | HuaXing渠道, batch为空 | 自动置成功，不阻塞后续流程 | P2 |

---

## 三、数据库变更影响分析

### 3.1 新增SQL初始化脚本

**文件**: `aps-app/src/main/resources/sql/thread_pool_aps_module_init.sql`

**影响**: 需要在APS的数据库中执行此SQL，写入21条thread_pool记录（module='APS'）。

**表**: `thread_pool`

**关键字段**:
| 字段 | 说明 |
|------|------|
| poor_code | 线程池标识 (如 aps_task_execute_pool) |
| module | 模块名 (APS) |
| core_size | 核心线程数 |
| max_size | 最大线程数 |
| keep_alive | 线程存活时间(秒) |
| queue_size | 队列大小 |
| policy | 拒绝策略 (CallerRunsPolicy/AbortPolicy) |

⚠️ **注意**: SQL使用INSERT VALUES，未使用INSERT IGNORE或ON DUPLICATE KEY UPDATE。重复执行会报主键冲突。需确认目标环境是否已有这些记录。

### 3.2 MyBatis Mapper变更

**文件**: `PartnerAgreementInstanceExtMapper.xml`

**影响**: 协议实例扩展字段变更，涉及表结构的扩展。需确认DDL已在目标环境执行。

### 3.3 ThirdRepayWithhold表

幂等控制依赖 `third_repay_withhold` 表作为幂等记录存储。需确认:
- 表在目标环境存在且可写入
- `repay_tran_no` + `partner_code` 有唯一索引/联合约束

---

## 四、Apollo配置变更测试要点

### 4.1 配置环境对照矩阵

| 配置Key | STG1 | STG2 | 生产 | 影响范围 |
|---------|------|------|------|---------|
| taskScheduleExecuteOptimizeSwitch | false(默认) | 待确认 | false | 全部调度任务 |
| pingAnPhThirdRepayWithholdIdempotentSwitch | false(默认) | 待确认 | false | 平安普惠还款 |
| threadPoolInfoServiceModule | APS(默认) | 待确认 | APS | 线程池DB配置加载 |

### 4.2 开关组合测试矩阵

| optimizeSwitch | paramPoolSwitch | 预期行为 |
|----------------|-----------------|---------|
| false | 任意 | 走旧路径: 固定task_default_pool, 提交前加锁 |
| true | false | 走新路径: Apollo Map / 内置规则 / 默认值 → 池解析 |
| true | true | 走新路径: 优先使用task参数池 → 其次Apollo Map → ... |

| idempotentSwitch | 预期行为 |
|-----------------|---------|
| false | 不获取Redis锁，直接执行业务 |
| true | 获取Redis锁，double-check模式 |

---

## 五、关键功能专项测试场景

### 5.1 幂等性专项

| # | 测试场景 | 测试方法 | 预期 | 优先级 |
|---|---------|---------|------|--------|
| I1 | 单节点重复请求 | 同一repayTranNo连续发两次 | 第二次幂等返回，不重复执行 | P0 |
| I2 | 双节点并发请求 | 两个节点同时发相同repayTranNo | 只有一个执行成功，另一个幂等返回 | P0 |
| I3 | 锁超时后的幂等 | 第一个请求锁超时(模拟20s+处理) | 第二个请求获取锁后，double-check查DB → 幂等 | P1 |
| I4 | DB记录已存在但状态为失败 | thirdRepayWithhold状态=FAIL | 根据状态正确返回(不重复执行) | P1 |
| I5 | DB记录已存在但状态为成功 | thirdRepayWithhold状态=SUCCESS | 直接返回成功 | P1 |

### 5.2 线程池隔离专项

| # | 测试场景 | 测试方法 | 预期 | 优先级 |
|---|---------|---------|------|--------|
| P1 | 池隔离有效性 | 长任务+短任务同时大量触发 | 长任务在aps_task_long_pool，不占用默认池 | P0 |
| P2 | 池满载处理 | aps_task_long_pool打满 | AbortPolicy → 新任务被拒绝，但不影响默认池 | P1 |
| P3 | 池配置错误恢复 | 配置不存在/已删除的池名 | 白名单拒绝 → fallback到默认池 → WARN日志 | P1 |
| P4 | switch频繁切换 | optimizeSwitch在任务执行中切换 | 当前任务按原路径完成，新任务用新路径 | P2 |

---

## 六、风险清单

| # | 风险 | 等级 | 说明 | 建议 |
|---|------|------|------|------|
| R1 | 线程池DB seed数据重复执行 | 🔴 中 | SQL为INSERT VALUES，重复执行报错 | 确认目标环境thread_pool记录状态，如已存在需用INSERT IGNORE |
| R2 | 旧路径与新路径并发 | 🔴 高 | switch动态切换时，新旧任务可能同时存在 | 灰度切换，确认旧任务全部完成后再开启 |
| R3 | Redis锁依赖 | 🟡 中 | 幂等控制强依赖Redis可用性 | 确认Redis高可用，锁获取失败有明确业务异常 |
| R4 | 线程池module从PPS改为APS | 🔴 高 | spring-threadpool.xml module变更影响thread_pool表查询 | 确认APS的thread_pool表数据完整 |
| R5 | 旧路径锁+提交原子性 | 🟡 中 | 旧路径提交失败时解锁是新逻辑 | 回归验证旧路径的解锁正确性 |
| R6 | inline首分片阻塞 | 🟡 中 | 首分片在当前线程执行，可能阻塞后续分片提交 | 监控inline分片耗时不超时 |

---

## 七、测试优先级与覆盖建议

### P0 (必须测试 - 6项)
1. 线程池隔离: optimizeSwitch=true场景 (T2)
2. 线程池隔离: optimizeSwitch=false回归 (T1) 
3. 线程池隔离: Apollo Map映射 (T3)
4. DB seed数据完整性 (T17)
5. 幂等控制: switch开启场景 (T20)
6. 幂等控制: switch关闭回归 (T19)

### P1 (重点测试 - 约25项)
- 线程池隔离: 多任务并发、白名单校验、兜底fallback、异常恢复、锁续期
- 幂等控制: 四个接口的并发幂等、获取锁失败、DB记录状态判断
- Apollo配置: 开关动态切换、白名单调整
- 协议框架: 版本快照、SFTP下载、Dubbo Facade
- 宁银/OCR/半流程/头条: 各场景验证

### P2 (补充测试 - 约8项)
- Prometheus: 端点可访问、Counter注册
- 边界场景: 锁自动过期、Default值回退

---

## 八、测试数据准备建议

### 线程池测试数据
```sql
-- 检查APS module的线程池数据
SELECT * FROM thread_pool WHERE module = 'APS';
-- 预期: 21条记录
```

### 幂等测试数据
```
渠道: PingAnPh (平安普惠)
partnerCode: 使用现有测试渠道
repayTranNo: 测试用交易流水号（注意唯一性）
Redis Key: aps_pinganph_third_repay_withhold_idempotent_lock_{partnerCode}_{repayTranNo}
```

### Apollo配置准备
```
# 按测试环境(STG1/STG2)分别配置:
aps.apollo.function.switch.taskScheduleExecuteOptimizeSwitch = true/false
aps.apollo.function.switch.pingAnPhThirdRepayWithholdIdempotentSwitch = true/false
aps.apollo.config.threadPoolInfoServiceModule = APS
```

---

*报告生成时间: 2026-06-26 | 分析工具: Code Analyzer Agent + testcase-code-analyze + Git diff*
