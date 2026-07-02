# Bug Fix Verification Report: JYSG-151029

## 1. 基本信息

| 项目 | 详情 |
|------|------|
| Bug ID | JYSG-151029 |
| Bug 描述 | 文件下载任务线程池使用错误：6个独立渠道文件下载任务使用 aps_task_execute_pool 而非 aps_task_long_pool |
| 修复 Commit | `f36c6ccc9efff9ca1fc58b35aaa23210a21129c3` |
| 提交者 | huangyexin-jk |
| 提交时间 | 2026-06-29 17:13:07 +0800 |
| 提交信息 | feat(JYSG-151029): 修改长任务线程池加载逻辑 |
| Sprint 分支 | feature/aps1.332.0_20260702 |
| 验证时间 | 2026-06-29 |
| 验证人 | Code Analyzer Agent |

## 2. 变更范围

| 文件 | 路径 | 变更类型 | 行数变更 |
|------|------|---------|---------|
| ScheduledTaskExecutorResolver.java | aps-app/src/main/java/.../common/task/service/ | 核心修复 | +10 / -3 |
| AbstractCronTaskClientService.java | aps-app/src/main/java/.../common/task/service/ | 机制支持 | +12 / -2 |
| ScheduledTaskExecutorResolverTest.java | aps-app/src/test/java/.../common/task/service/ | 测试更新 | +24 / -9 |
| AbstractCronTaskClientServiceTest.java | aps-app/src/test/java/.../common/task/service/ | 测试适配 | +6 / -2 |
| **合计** | 4 文件 | | +38 / -14 |

## 3. 核心修复分析

### 3.1 resolveBuiltInPoolName() 方法变更

**修复前（Buggy）：**
```java
private String resolveBuiltInPoolName(String taskName) {
    if (PARTNER_FILE_DOWNLOAD_TASK.equals(taskName)) {  // 精确匹配 taskName
        return TASK_SCHEDULE_LONG_POOL;
    }
    return null;
}
```

**修复后：**
```java
private String resolveBuiltInPoolName(String taskBeanName) {
    if (PARTNER_FILE_DOWNLOAD_TASK.equalsIgnoreCase(taskBeanName)) {  // 忽略大小写匹配 beanName
        return TASK_SCHEDULE_LONG_POOL;
    }
    return null;
}
```

**变更分析：**
- `equals` -> `equalsIgnoreCase`：增加了大小写容错
- 参数名从 `taskName` 改为 `taskBeanName`：语义上标明这里使用的是 Spring Bean 名称
- `PARTNER_FILE_DOWNLOAD_TASK` 常量值仍为 `"partnerFileDownloadTask"`，仍是精确字符串匹配（非后缀匹配）

### 3.2 resolvePoolName() 新增重载

**新增 3 参数版本：**
```java
public String resolvePoolName(String taskName, String taskBeanName, String taskPoolName) {
    // taskName -> Apollo map 查找（key = taskName）
    // taskBeanName -> Built-in map 查找（key = taskBeanName）
    // taskPoolName -> task param 传参
}
```

**原有 2 参数版本改为委托：**
```java
public String resolvePoolName(String taskName, String taskPoolName) {
    return resolvePoolName(taskName, taskName, taskPoolName);  // backward compat
}
```

**关键设计：** Apollo `taskSchedulePoolNameMap` 以 `taskName` 为 key，built-in map 以 `taskBeanName` 为 key。两者解耦后互不影响。

### 3.3 AbstractCronTaskClientService 变更

- 新增 `implements BeanNameAware`，通过 Spring 容器自动注入 beanName
- 调用 `resolvePoolName(taskParam.getName(), beanName, taskParam.getTaskPoolName())`
- 将 Spring Bean 名称（而非 Lingxi 任务参数中的 name）传入 built-in 匹配逻辑

## 4. 线程池解析优先级（修复后）

`resolvePoolName(taskName, taskBeanName, taskPoolName)` 按以下优先级解析：

| 优先级 | 来源 | Key | 说明 |
|--------|------|-----|------|
| 1 (最高) | Task Param | `taskPoolName` | 当 `taskScheduleParamPoolSwitch=true` 且参数合法时使用 |
| 2 | Apollo Map | `taskName` | `taskSchedulePoolNameMap` 配置，key = taskName |
| 3 | Built-in Map | `taskBeanName` | 硬编码匹配 `"partnerFileDownloadTask"` |
| 4 | Apollo Default | N/A | `taskScheduleDefaultPoolName`（默认 `aps_task_execute_pool`） |
| 5 (最低) | Fallback | N/A | `task_default_pool` |

## 5. 覆盖度分析：所有文件下载任务

### 5.1 受影响的文件下载任务（extends AbstractCronTaskClientService）

| # | @Service Bean Name | 类名 | Bug 提及 | Built-in 匹配 | 状态 |
|---|-------------------|------|---------|-------------|------|
| 1 | `partnerFileDownloadTask` | PartnerFileDownloadTask | 是（集中分发器） | **YES** | 已覆盖 |
| 2 | `sykcfcPartnerFileDownloadTask` | SykcfcPartnerFileDownloadTask | 是（苏银凯基） | **NO** | 需 Apollo |
| 3 | `boHaiBkPartnerFileDownloadTask` | BoHaiBkPartnerFileDownloadTask | 是（渤海银行） | **NO** | 需 Apollo |
| 4 | `jiangSuBkVoucherFileDownloadTask` | JiangSuBkPartnerFileDownloadTask | 是（江苏银行） | **NO** | 需 Apollo |
| 5 | `ningYinXJVoucherFileDownloadTask` | NingYinXJPartnerFileDownloadTask | 是（宁银消金） | **NO** | 需 Apollo |
| 6 | `suShangBKVoucherFileDownloadTask` | SuShangBKPartnerFileDownloadTask | 是（苏商银行） | **NO** | 需 Apollo |
| 7 | `boHaiXiaoWeiPartnerFileDownloadTask` | BoHaiXiaoWeiPartnerFileDownloadTask | 是（渤海小微） | **NO** | 需 Apollo |
| 8 | `ningBoBkVoucherFileDownloadTask` | NingBoBkVoucherFileDownloadTask | **否！遗漏** | **NO** | 需 Apollo |

### 5.2 不受影响的任务

| 类名 | 父类 | 原因 |
|------|------|------|
| JinKeBankContractDownloadTask | AbstractApsExecuteScheduledService | 不同父类，不同线程池解析机制 |

### 5.3 关键发现

**发现 1：Built-in 映射仅覆盖 1/8 个任务。**
修复后的 `resolveBuiltInPoolName()` 仍只精确匹配 `"partnerFileDownloadTask"`（忽略大小写），其他 7 个独立渠道文件下载任务的 bean name 均不匹配。

**发现 2：修复采用 Apollo 配置方案，非后缀匹配方案。**
Bug 报告中建议的方案 A（endsWith 后缀匹配）未被采用。实际修复方案是方案 B：代码层面解耦 taskName 和 taskBeanName，依赖方通过 Apollo `taskSchedulePoolNameMap` 配置将独立渠道任务映射到 `aps_task_long_pool`。

**发现 3：宁波银行凭证文件下载任务（NingBoBkVoucherFileDownloadTask）在 Bug 中遗漏。**
Bug 报告只列出了 7 个任务（1 集中分发器 + 6 独立渠道），但实际存在第 8 个任务 `ningBoBkVoucherFileDownloadTask`（宁波银行凭证文件下载），同样 extends AbstractCronTaskClientService，同样未覆盖。

**发现 4：类名与 Bean 名存在不一致。**
- `JiangSuBkPartnerFileDownloadTask` 类的 @Service 名为 `jiangSuBkVoucherFileDownloadTask`
- `SuShangBKPartnerFileDownloadTask` 类的 @Service 名为 `suShangBKVoucherFileDownloadTask`
- `NingYinXJPartnerFileDownloadTask` 类的 @Service 名为 `ningYinXJVoucherFileDownloadTask`

类名含 "Partner" 但 Bean 名含 "Voucher"，配置 Apollo 时需使用 Bean 名（而非类名），或确认 Lingxi 调度器中的 taskName 是什么。

## 6. 测试覆盖分析

### 6.1 新增/修改的测试用例

| 测试方法 | 类型 | 验证点 |
|---------|------|--------|
| `shouldUseBuiltInLongPoolForPartnerFileDownloadBean` | 新增 | beanName="partnerFileDownloadTask" 时返回 long pool |
| `shouldNotUseBuiltInLongPoolWhenOnlyTaskNameMatches` | 新增 | taskName 匹配但 beanName 不匹配时，不回退到 default pool |
| `shouldUseAllowedParamPoolWhenParamSwitchEnabled` | 修改 | 适配新的 3 参数接口 |
| `shouldIgnoreParamPoolWhenParamSwitchDisabled` | 修改 | 适配新的 3 参数接口 |
| `shouldUseAllowedMapPool` | 修改 | 适配新的 3 参数接口 |
| `shouldFallbackToDefaultWhenMapPoolRejected` | 修改 | 适配新的 3 参数接口 |
| `shouldFallbackToBuiltInDefaultWhenConfiguredDefaultRejected` | 修改 | 适配新的 3 参数接口 |

### 6.2 测试覆盖缺口

| 缺口 | 严重度 | 说明 |
|------|--------|------|
| 无独立渠道任务的集成测试 | 中 | 没有测试验证 `sykcfcPartnerFileDownloadTask`、`boHaiBkPartnerFileDownloadTask` 等通过 Apollo map 正确获取 long pool |
| 无 BeanNameAware 注入验证 | 中 | `AbstractCronTaskClientServiceTest` 中手动 setBeanName，未验证 Spring 容器自动注入 |
| 无 endsWith 后缀匹配的负面测试 | 低 | Bug 报告建议的后缀方案未被采用，但也没有测试证明为何不采用 |

## 7. 验证结论

### 7.1 修复正确性：PARTIAL（部分修复）

| 维度 | 评估 | 说明 |
|------|------|------|
| 代码逻辑 | **正确** | BeanNameAware 机制正确实现，参数解耦合理 |
| 优先级保持 | **正确** | Task Param > Apollo Map > Built-in > Default，未改变 |
| 向后兼容 | **正确** | 2 参数 `resolvePoolName` 保留，委托给 3 参数版本 |
| 测试覆盖 | **基本充分** | 新增 2 个核心测试，修改 5 个已有测试适配新接口 |
| Bug 覆盖 | **不完整** | 6 个独立渠道任务未被 built-in 覆盖，需 Apollo 配置 |
| Bug 遗漏 | **存在** | NingBoBkVoucherFileDownloadTask 未在 Bug 中提及 |

### 7.2 最终判定：CONDITIONAL PASS（有条件通过）

代码修复本身逻辑正确，但存在以下待办事项：

| # | 待办事项 | 优先级 | 负责方 |
|---|---------|--------|--------|
| 1 | 在 Apollo `taskSchedulePoolNameMap` 中为 6 个独立渠道任务添加映射到 `aps_task_long_pool` | **P0 - 阻塞上线** | 开发/运维 |
| 2 | 确认 Lingxi 调度器中各渠道任务的 taskName 值，用于 Apollo map 的 key | **P0 - 阻塞上线** | 开发 |
| 3 | 将 NingBoBkVoucherFileDownloadTask 纳入修复范围 | **P1 - 建议修复** | 开发 |
| 4 | 补充独立渠道任务的集成测试 | P2 - 后续优化 | 测试 |

### 7.3 风险提示

> **高风险：** 如果 Apollo `taskSchedulePoolNameMap` 未配置，这 6 个独立渠道文件下载任务将继续使用 `aps_task_execute_pool`（默认池），文件下载是长耗时操作，可能阻塞同池的其他定时任务，与修复前的问题完全一致。代码修复只是**开启了正确的机制入口**，但实际生效依赖 Apollo 配置。

## 8. 附录：完整任务清单

### 所有 extends AbstractCronTaskClientService 的文件下载相关任务

```
序号 | Spring Bean Name                        | 类名                                   | 渠道
-----|-----------------------------------------|---------------------------------------|---------------
1    | partnerFileDownloadTask                 | PartnerFileDownloadTask               | 集中分发器
2    | sykcfcPartnerFileDownloadTask           | SykcfcPartnerFileDownloadTask         | 苏银凯基
3    | boHaiBkPartnerFileDownloadTask          | BoHaiBkPartnerFileDownloadTask        | 渤海银行
4    | jiangSuBkVoucherFileDownloadTask        | JiangSuBkPartnerFileDownloadTask      | 江苏银行
5    | ningYinXJVoucherFileDownloadTask        | NingYinXJPartnerFileDownloadTask      | 宁银消金
6    | suShangBKVoucherFileDownloadTask        | SuShangBKPartnerFileDownloadTask      | 苏商银行
7    | boHaiXiaoWeiPartnerFileDownloadTask     | BoHaiXiaoWeiPartnerFileDownloadTask   | 渤海小微
8    | ningBoBkVoucherFileDownloadTask         | NingBoBkVoucherFileDownloadTask       | 宁波银行 [Bug遗漏]
```

### 改动文件绝对路径

- `D:\project\aps\aps-app\src\main\java\com\qihoo\finance\aps\common\task\service\ScheduledTaskExecutorResolver.java`
- `D:\project\aps\aps-app\src\main\java\com\qihoo\finance\aps\common\task\service\AbstractCronTaskClientService.java`
- `D:\project\aps\aps-app\src\test\java\com\qihoo\finance\aps\common\task\service\ScheduledTaskExecutorResolverTest.java`
- `D:\project\aps\aps-app\src\test\java\com\qihoo\finance\aps\common\task\service\AbstractCronTaskClientServiceTest.java`
