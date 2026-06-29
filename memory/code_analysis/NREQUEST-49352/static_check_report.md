# 代码静态检查报告

> 需求编号: NREQUEST-49352
> 关联 Story: JYSG-149999 (API流量IT巡检202606)
> 迭代版本: 20260702
> 仓库: 360jr-mkt/aps
> 分支: feature/aps1.332.0_20260702
> 检查日期: 2026-06-26
> 检查方法: testmind:code-check (QOA平台) + 直接源码静态分析
> 源码路径: D:\project\aps

---

## 检查摘要

| 检查维度 | 问题数 | 严重(High) | 中等(Medium) | 轻微(Low) |
|---------|--------|-----------|-------------|----------|
| 硬编码 | 3 | 0 | 3 | 0 |
| 空安全 | 3 | 0 | 1 | 2 |
| 资源管理 | 1 | 0 | 0 | 1 |
| 异常处理 | 2 | 0 | 1 | 1 |
| 事务边界 | 0 | 0 | 0 | 0 |
| 并发安全 | 1 | 1 | 0 | 0 |
| **合计** | **10** | **1** | **5** | **4** |

---

## 一、Prometheus度量监控 (API-10531)

### 涉及文件
- `MeasureUtil.java` (新增)
- `MetricsHolder.java` (修改)
- `MeasureKeyEnum.java` (新增)
- `MeasureResultEnum.java` (新增)

---

### ISSUE #1 [HIGH] [并发安全] MetricsHolder.getOrAddMeasureCounter 存在竞态条件

**文件**: `aps-app/src/main/java/com/qihoo/finance/aps/common/prometheus/MetricsHolder.java`
**位置**: 第 94-111 行

**问题描述**:
`getOrAddMeasureCounter` 方法使用典型的 double-check 模式，但 `Counter.builder().register()` 在 `putIfAbsent` 之前执行：

```java
// Line 100-110
if (MEASURE_COUNTER_MAP.containsKey(counterKey)) {
    return MEASURE_COUNTER_MAP.get(counterKey);
}
Counter counter = Counter.builder(MEASURE_COUNTER_NAME)
    .description(MEASURE_COUNTER_DESCRIPTION)
    .tag(MEASURE_KEY, measureKey.getKey())
    .tag(RESULT, result.getResult())
    .register(MetricsHolder.getRegistry());  // <-- 竞态窗口
Counter preCounter = MEASURE_COUNTER_MAP.putIfAbsent(counterKey, counter);
return preCounter != null ? preCounter : counter;
```

**竞态场景**:
1. 线程A: `containsKey` 返回 false
2. 线程B: `containsKey` 返回 false
3. 线程A: `Counter.builder().register()` 注册成功
4. 线程B: `Counter.builder().register()` 尝试注册同名 Counter -> Micrometer 抛出 `IllegalArgumentException`

**影响**:
- 并发场景下可能抛出运行时异常，导致度量记录失败
- 受影响的方法调用链: `MeasureUtil.record()` -> `MetricsHolder.getOrAddMeasureCounter()`
- 虽然 `MeasureUtil.record()` 有外层 catch Exception，但异常被吞掉不会传播

**建议修复**:
```java
// 方案1: 使用 computeIfAbsent (线程安全)
return MEASURE_COUNTER_MAP.computeIfAbsent(counterKey, k -> {
    return Counter.builder(MEASURE_COUNTER_NAME)
        .description(MEASURE_COUNTER_DESCRIPTION)
        .tag(MEASURE_KEY, measureKey.getKey())
        .tag(RESULT, result.getResult())
        .register(MetricsHolder.getRegistry());
});

// 方案2: 在 putIfAbsent 之后再 register (仅当自己是赢家时注册)
Counter preCounter = MEASURE_COUNTER_MAP.putIfAbsent(counterKey, counter);
if (preCounter != null) {
    return preCounter;
}
// 只有插入成功才注册
counter = Counter.builder(MEASURE_COUNTER_NAME)...register(registry);
```

**同样问题存在于**:
- `getOrAddErrCounter()` (第 65-76 行)
- `getOrAddInfoCounter()` (第 80-92 行)

---

### ISSUE #2 [MEDIUM] [异常处理] MeasureUtil.record 吞异常范围过宽

**文件**: `aps-app/src/main/java/com/qihoo/finance/aps/common/prometheus/measure/MeasureUtil.java`
**位置**: 第 28-31 行

**问题描述**:
`catch (Exception e)` 捕获所有异常，包括不应被吞掉的严重错误:

```java
try {
    Counter counter = MetricsHolder.getOrAddMeasureCounter(measureKey, result);
    if (counter != null) {
        counter.increment();
    }
} catch (Exception e) {
    log.error("ERR [Measure] record measure failed, ...", e);
}
```

**问题**: `Exception` 包含 `NullPointerException`、`IllegalStateException` 等，应有区分：
- 度量相关的异常（如 Counter 注册冲突）: 可吞掉，因为度量不应影响业务
- 非预期的严重异常: 应传播或至少记录更明确的错误级别

**建议**:
将 catch 范围缩小为 `RuntimeException` 或针对 Micrometer 异常类型进行捕获，严重错误使用 `ERROR` 级别日志并考虑上报告警。

---

### ISSUE #3 [LOW] [异常处理] MeasureUtil 中 counter.increment() 抛出异常无单独处理

**文件**: 同上，第 26 行

`counter.increment()` 本身也可能抛出异常（如 Counter 已被移除），但在 catch 块中未区分是 `getOrAddMeasureCounter` 还是 `increment` 失败。

**影响**: 难以定位问题根因。

---

## 二、定时任务线程池隔离 (API-10523)

### 涉及文件
- `ScheduledTaskExecutorResolver.java` (新增)
- `AbstractApsExecuteScheduledMultiThreadService.java` (修改)
- `AbstractCronTaskClientService.java` (修改)

---

### ISSUE #4 [LOW] [空安全] @ApolloJsonValue 注入失败时 poolNameMap 可能为 null

**文件**: `aps-app/src/main/java/com/qihoo/finance/aps/common/task/service/ScheduledTaskExecutorResolver.java`
**位置**: 第 33-37 行

```java
@ApolloJsonValue("${aps.apollo.config.taskSchedulePoolNameMap:{}}")
private Map<String, String> taskSchedulePoolNameMap = Collections.emptyMap();

@ApolloJsonValue("${aps.apollo.config.taskScheduleAllowedPoolNames:[\"aps_task_execute_pool\",\"aps_task_long_pool\"]}")
private List<String> taskScheduleAllowedPoolNames = Arrays.asList("aps_task_execute_pool", "aps_task_long_pool");
```

**分析**: 
- `@ApolloJsonValue` 在 Apollo 不可用时不会注入，字段保持为 `null`（覆盖默认值）
- Line 51: `MapUtils.isEmpty(taskSchedulePoolNameMap)` 确实能处理 null -> OK
- Line 95: `CollectionUtils.isEmpty(taskScheduleAllowedPoolNames)` 确实能处理 null -> OK

**结论**: 安全风险已被正确防御，标记为 LOW 仅因防御措施依赖于 MapUtils/CollectionUtils 的工具方法行为而非显式 null 检查。

---

### 总体评价

`ScheduledTaskExecutorResolver` 整体代码质量良好：
- 四级池名解析逻辑清晰，每级都有白名单校验
- 配置缺失时正确 fallback 到 default -> 兜底池
- 所有路径都有 WARN 日志记录便于排查
- 线程安全：无共享可变状态

---

## 三、平安普惠还款幂等控制 (API-10523) --- Redis锁

### 涉及文件
- `PingAnPhDebtQueryFacadeAdapter.java` (修改)
- `PingAnPhBizService.java` (修改)
- `PingAnPhOrderServiceProactivePay.java` (修改)
- `LockKeyGenerator.java` (修改)
- `RedisLockUtil.java` (工具类)

---

### ISSUE #5 [MEDIUM] [硬编码] Redis锁超时参数硬编码

**涉及文件** (3处重复):
- `PingAnPhDebtQueryFacadeAdapter.java` 第 59-60 行
- `PingAnPhBizService.java` 第 90-91 行
- `PingAnPhOrderServiceProactivePay.java` 第 56-57 行

```java
private static final long PINGANPH_THIRD_REPAY_WITHHOLD_LOCK_MILLIS = 20000L;  // 20秒
private static final long PINGANPH_THIRD_REPAY_WITHHOLD_TRY_MILLIS = 1500L;    // 1.5秒
```

**问题**:
1. 同一常量在 3 个文件中重复定义，违反 DRY 原则
2. 锁超时和等待时间写死，无法按环境/场景动态调整
3. 如果业务执行时间超过 20 秒（如远程调用慢），锁会过期导致另一个请求获取到锁

**建议**:
```java
// 统一定义在配置类或 Apollo 配置中
@Value("${aps.apollo.config.pingAnPh.repayIdempotentLockMillis:20000}")
private long idempotentLockMillis;
@Value("${aps.apollo.config.pingAnPh.repayIdempotentTryMillis:1500}")
private long idempotentTryMillis;
```

---

### ISSUE #6 [LOW] [资源管理] RedisLockUtil.close() 重复调用安全性

**文件**: `aps-app/src/main/java/com/qihoo/finance/aps/v4/util/RedisLockUtil.java`
**位置**: 第 45-48 行

```java
@Override
public void close() {
    if (locked) {
        SpringContextHolder.getBean(RedisLockService.class).unLock(lockKey);
    }
}
```

**问题**:
- `close()` 可能被 try-with-resources 多次调用（虽然规范上只调用一次）
- 如果 unLock 失败（如 Redis 连接断开），locked 字段不重置，后续 close 仍尝试解锁

**影响**: 极低，RedisLockService.unLock 应为幂等操作。

---

### ISSUE #7 [LOW] [资源管理] syncRepayResult 和 repayConfirm 使用不同的锁模式

**文件**: `PingAnPhBizService.java`

两种锁使用模式共存:
| 方法 | 模式 | 位置 |
|------|------|------|
| `repayConfirm` | try-with-resources (AutoCloseable) | 第 819-833 行 |
| `repayConfirm4RongDan` | try-with-resources (AutoCloseable) | 第 936-954 行 |
| `syncRepayResult` | 手动 lock/finally unlock | 第 555-615 行 |
| `repayCancel` | 手动 lock/finally unlock | 第 1017-1058 行 |

**分析**:
- 两种模式功能上都是正确的（finally 块保证解锁）
- 但模式不一致增加了维护成本和出错风险

**建议**: 统一使用 try-with-resources 模式，减少手动 finally 代码。

---

### Double-Check Locking 正确性验证

所有三个幂等控制点的 double-check locking 模式均正确实现:

```
// 正确模式 (以 PingAnPhDebtQueryFacadeAdapter.collectOverdueRepay 为例)
1. 无锁查询 DB (第 201 行)
   ThirdRepayWithhold thirdRepayWithhold = thirdRepayWithholdService.queryBy...(...);
   if (thirdRepayWithhold != null) { return ...; }  // 幂等返回

2. 获取 Redis 锁, try-with-resources (第 210-211 行)
   try (RedisLockUtil lock = RedisLockUtil.getInstanceWithTry(lockKey, ...)) {

3. 锁获取失败 -> 抛异常 (第 212-216 行)
   if (!lock.holdLock()) { throw ApsBusinessException.bizErr("获取幂等锁失败"); }

4. 锁内 double-check DB (第 217-224 行)
   thirdRepayWithhold = thirdRepayWithholdService.queryBy...(...);
   if (thirdRepayWithhold != null) { return ...; }  // 幂等返回

5. 执行业务 (第 225 行)
   thirdRepayWithhold = executeCollectOverdueRepay(...);

6. 自动释放锁 (try-with-resources close())
```

**结论**: 分布式锁实现正确。

---

## 四、微信半流程拉合同 (API-10524)

### 涉及文件
- `PullContractWeChatService.java`
- `MobileUtil.java`

---

### ISSUE #8 [MEDIUM] [空安全] pullCreditContractList 返回 null 而非错误响应

**文件**: `PullContractWeChatService.java`
**位置**: 第 152-154 行

```java
Response<String> userNoResponse = userService.getUserNo(...);
if (userNoResponse.checkIfFail() || Objects.isNull(userNoResponse.getData())) {
    log.warn("WARN 半流程拉取合同失败,获取用户号失败,...");
    return null;  // <-- 返回 null
}
```

**问题**:
- 方法签名是 `V4OrderResponse<List<WeChatPullContractResp>>`，返回 null 违反约定
- 上层调用者 `bizHandle(WeChatPullContractReq request)` 第 96-106 行不对 null 做检查，直接返回给更上层
- 上层可能对 null 返回值做 `response.checkIfFail()` 调用，导致 NPE

**建议**: 返回 `V4OrderResponses.fail(...)` 而不是 null。

---

### ISSUE #9 [MEDIUM] [硬编码] MobileUtil 手机号段正则硬编码

**文件**: `aps-app/src/main/java/com/qihoo/finance/aps/v4/util/MobileUtil.java`
**位置**: 第 23-65 行 (REGEX_MOBILE) 和 第 68-73 行 (REGEX_MOBILE_BY5G)

**问题**:
- 手机号段前缀在代码中硬编码，5G 号段 (172/193/196/197) 需代码变更才能扩展
- 号段由工信部分配，属于频繁变更的外部数据，硬编码会导致维护困难

**建议**: 将号段配置移至 Apollo 配置或数据库，支持动态更新。

---

### ISSUE #10 [LOW] [硬编码] MobileUtil 导入了 sun 内部 API (不可用)

**文件**: 同上，第 6 行

```java
import com.sun.org.apache.regexp.internal.RE;
```

**问题**:
- `com.sun.org.apache.regexp.internal.RE` 是 JDK 内部 API，不应被应用代码直接引用
- 不同 JDK 版本中可能不可用或被移除

**建议**: 此行似乎未被使用（方法中都用了 `String.matches()`），应删除此 import。

---

## 五、事务边界检查

### 检查范围
在已审查的代码中，未发现显式的 `@Transactional` 注解使用。Redis 分布式锁用于幂等控制而非事务保护，实现正确。

`PingAnPhDebtQueryFacadeAdapter.executeCollectOverdueRepay()` (第 243-285 行):
- 先调用远程服务 `repayRequestByXj/repayRequestByRongDan`
- 再保存本地记录 `thirdRepayWithholdService.saveRecord()`
- **潜在问题**: 远程调用成功后本地保存失败，会导致远程已执行但本地无记录的不一致
- 当前采用了先落库提交记录(`SUBMIT_SUC`)再异步同步结果的模式，通过 `syncRepayResult` 补偿，可接受

---

## 六、QOA平台 code-check 查询结果

通过 `testmind:code-check` 查询平台已有的检查任务:
- **方法变更检查 (method-change-query)**: 当前迭代 20260702 下无记录（尚未有预校验任务生成）
- **删除/注释检查 (delete-query)**: 当前迭代 20260702 下无记录

> 说明: QOA 平台的 code-check 任务由定时任务或手动触发创建，当前迭代可能尚未生成对应检查任务。

---

## 七、风险汇总

| # | 风险等级 | 类别 | 描述 | 影响模块 | 建议处理 |
|---|---------|------|------|---------|---------|
| R1 | HIGH | 并发安全 | MetricsHolder Counter 注册竞态条件 | Prometheus度量 | 使用 computeIfAbsent 修复，P0 |
| R2 | MEDIUM | 异常处理 | MeasureUtil 吞异常过宽 | Prometheus度量 | 缩小 catch 范围，P1 |
| R3 | MEDIUM | 硬编码 | 锁超时参数3处重复+不可动态调整 | PingAnPh幂等 | 提取为 Apollo 配置，P1 |
| R4 | MEDIUM | 空安全 | pullCreditContractList 返回 null | 半流程拉合同 | 改为返回错误响应对象，P1 |
| R5 | MEDIUM | 硬编码 | 手机号段正则硬编码 | MobileUtil | 迁移到 Apollo 配置，P2 |
| R6 | LOW | 资源管理 | RedisLockUtil.close() 无异常保护 | PingAnPh幂等 | 添加 try-catch 包裹 unLock，P2 |
| R7 | LOW | 资源管理 | 两种锁释放模式不一致 | PingAnPhBizService | 统一为 try-with-resources，P2 |
| R8 | LOW | 硬编码 | sun 内部 API import | MobileUtil | 删除未使用的 import，P2 |
| R9 | LOW | 空安全 | @ApolloJsonValue null fallback | ScheduledTaskExecutor | 已有防御，观察即可 |
| R10 | LOW | 异常处理 | MeasureUtil increment 无单独 catch | Prometheus度量 | P3，低优先级 |

---

## 八、正面发现 (代码优点)

1. **Double-Check Locking 模式实现正确**: 三个幂等控制点 (PingAnPhDebtQueryFacadeAdapter, PingAnPhBizService.repayConfirm, PingAnPhBizService.repayConfirm4RongDan, PingAnPhOrderServiceProactivePay) 的分布式锁使用 double-check 模式，逻辑严谨。

2. **ScheduledTaskExecutorResolver 设计良好**: 四级 fallback + 白名单校验，各级有日志，线程安全。

3. **try-with-resources 模式应用于新增代码**: `RedisLockUtil` 实现 `Closeable`，配合 try-with-resources 自动释放锁，避免了手动的 finally 解锁错误。

4. **空安全防御充分**: 大多数方法的参数校验和外调返回值 null 检查到位。

5. **MeasureUtil 防御式设计**: 度量记录失败不影响业务主流程，null 参数有明确日志记录。

6. **Apollo 开关设计**: 幂等开关和线程池优化开关均可动态切换，支持灰度发布和紧急回滚。

---

*报告生成时间: 2026-06-26 | 检查工具: Code Analyzer Agent + testmind:code-check + 直接源码分析*
