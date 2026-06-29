# NREQUEST-49267 测试说明

## Apollo 配置清单

> 执行时根据前置条件中的配置名和值，自动读取/修改 Apollo 配置。

| # | 配置 Key | 类型 | 默认值 | 可选值 | 说明 |
|---|---------|------|--------|--------|------|
| 1 | `aps.apollo.config.repayWithholdWriteMode` | String | OLD_ONLY | OLD_ONLY / TRIPLE / DUAL | 写入模式路由 |
| 2 | `aps.apollo.function.switch.repayWithholdReadNew` | boolean | false | true / false | 读取路由开关 |
| 3 | `aps.apollo.function.switch.repayWithholdObWriteLog` | boolean | false | true / false | OB写入日志开关 |
| 4 | `aps.apollo.function.switch.repayWithholdObReadLog` | boolean | false | true / false | OB读取日志开关 |
| 5 | `aps.switch.control.monitorEnabled` | boolean | false | true / false | 历史数据监控开关 |
| 6 | `aps.switch.control.monitorDayDiff` | int | 1 | 正整数 | 监控差值天数阈值 |

## 测试渠道

使用 **星选（XingXuan）** 渠道进行冷热分离读写验证。

| 项目 | 内容 |
|------|------|
| 渠道代码 | XingXuan |
| 渠道AppId | TTXX360 |
| Facade | `XingXuanOrderFacade#orderRequestHandlerMap` |

## 涉及接口

### 写入接口：还款通知接口

触发 order_repay_withhold 表的写入操作。写入目标表由 Apollo 开关 `repayWithholdWriteMode` 决定。

### 读取接口：还款结果查询接口

触发 order_repay_withhold 表的读取操作。读取目标表由 Apollo 开关 `repayWithholdReadNew` 决定。日志中关键标记：`读取模式:NEW`（热表）或 `读取模式:OLD`（旧表）。

> 注：具体的接口 method、入参匹配和参数组装由 test-mapper Agent 负责，用例和测试说明只需中文描述接口意图即可。

## 数据库表分布

| 表名 | 所在库 | 所属子系统 | 说明 |
|------|--------|-----------|------|
| `order_repay_withhold` | aps 库 | aps-app | 旧MySQL表，改造前主表 |
| `order_repay_withhold_hot` | aps 库（同库同实例） | aps-app | 新MySQL热表，按月分区，保留近2个月数据 |
| `order_repay_withhold_backup` | OB 库 | apss-ob 子系统 | OceanBase 备份表，全量冷数据 |
| `order_repay_withhold_detail` | aps 库（主库**仅**） | aps-app | 还款代扣明细表，**仅存在于主库** |
| `order_repay_withhold_bill` | aps 库（主库**仅**） | aps-app | 还款代扣账单表，**仅存在于主库** |

> ⚠️ **主库独有表**：`order_repay_withhold_detail` 和 `order_repay_withhold_bill` 仅存在于主库，从库无此表。
> 
> ⚠️ **强制落库规则**：无论 `repayWithholdWriteMode` 配置为 OLD_ONLY / TRIPLE / DUAL，`saveRepayInfo` 方法**同时写 withhold 表 + detail 表 + bill 表**，这两个表的数据必定落库到主库，不受读写路由开关影响。校验时需直连主库查询。

## 读取路由验证方法（日志判断）

### 核心方法

调用查询接口后，通过查询应用日志判断**实际读取的是哪张表**：

1. **日志关键字**：使用还款订单号（`repay_order_id`，如 `RN20260612240134403`）作为关键字
2. **查询命令**：
   ```bash
   python qoa_api.py log --env STG2 \
     --package-names '["aps-app"]' \
     --message-like "RN20260612240134403" \
     --log-start-time "时间" --log-end-time "时间"
   ```
3. **判断依据**：
   - 搜索 SQL 日志中的 `Preparing:` 行，查看 `FROM` 子句的表名
   - 搜索 `读取模式:` 日志（`OrderRepayWithholdServiceImpl` 输出），确认是 `NEW`（热表）还是 `OLD`（旧表）
   - 若读到热表：SQL 为 `FROM order_repay_withhold_hot`
   - 若读到旧表：SQL 为 `FROM order_repay_withhold`
   - 若穿透读 OB：SQL 为 `FROM order_repay_withhold_backup`

### 日志关键定位点

| 日志类 | 关键内容 | 说明 |
|--------|---------|------|
| `XingXuanOrderFacadeImpl:86` | `REQ 头条星选订单请求处理 params={method=pullRepayNotify...}` | 请求入口 |
| `XingXuanOrderServicePullRepayNotify:52` | `REQ 还款结果查询接口 请求入参` | 查询接口入参 |
| `OrderRepayWithholdServiceImpl:214` | `PRD ... 读取模式:NEW` 或 `读取模式:OLD` | 读取路由判断 |
| `O.selectByRepayTranNo:139` | `Preparing: SELECT ... FROM order_repay_withhold_hot WHERE repay_tran_no = ?` | 实际执行的SQL |

## 测试流程

### 星选渠道冷热分离验证流程

```
Step 1: 调用星选还款通知接口（pullRepayNotify），触发写入
  → 入参: account_id + repay_order_id (如 RN20260612240134403)
  
Step 2: 查询旧MySQL表 order_repay_withhold，确认数据写入情况
  → 根据 writeMode 判断是否应写入旧表
  
Step 3: 查询新MySQL热表 order_repay_withhold_hot，确认数据写入情况
  → 根据 writeMode 判断是否应写入热表
  
Step 4: 查询OB表 order_repay_withhold_backup，确认数据写入情况
  → 根据 writeMode 判断是否应写入OB（异步，稍等后查询）
  
Step 5: 查询 order_repay_withhold_detail，确认数据写入情况
  → ⚠️ 仅存在于主库，无论 writeMode 如何，必定落库
  
Step 6: 查询 order_repay_withhold_bill，确认数据写入情况
  → ⚠️ 仅存在于主库，无论 writeMode 如何，必定落库
  
Step 7: 调用查询接口，用 repay_order_id 查日志确认读取路由
  → 使用 --message-like 搜索 repay_order_id
  → 确认 SQL 中 FROM 的表名
  → 确认读取模式日志
```

---

## 用例清单

> 共 14 条用例，分 6 类。每条用例前置条件中包含完整 Apollo 配置名和值。

### 写入路由（5条）

| # | 用例 | 核心配置 | 验证点 |
|---|------|---------|--------|
| 1 | OLD_ONLY仅写旧表 | writeMode=OLD_ONLY, readNew=false | 仅aps库旧表有数据 |
| 2 | TRIPLE三写 | writeMode=TRIPLE, readNew=false | aps旧表+热表+apss-ob OB表均有数据，id一致 |
| 3 | DUAL双写不写旧表 | writeMode=DUAL, readNew=true | aps旧表无数据，热表+OB有数据 |
| 4 | TRIPLE→OLD_ONLY紧急回滚 | writeMode: TRIPLE→OLD_ONLY | 切换后仅写旧表 |
| 5 | DUAL→OLD_ONLY紧急回滚 | writeMode: DUAL→OLD_ONLY, readNew: true→false | 切换后仅写旧表 |

### 读取路由（3条）

| # | 用例 | 核心配置 | 验证点 |
|---|------|---------|--------|
| 6 | readNew=false查旧表 | readNew=false | 日志：读取模式=OLD，SQL查order_repay_withhold |
| 7 | readNew=true查热表 | readNew=true | 日志：读取模式=NEW，SQL查order_repay_withhold_hot |
| 8 | 热表miss穿透OB | readNew=true | 日志：热表Total=0→OB Total=1 |

### Apollo动态切换（1条）

| # | 用例 | 核心配置 | 验证点 |
|---|------|---------|--------|
| 9 | OLD_ONLY⇄TRIPLE互切 | writeMode动态修改 | 多次切换后路由正确，无状态残留 |

### 日志开关（2条）

| # | 用例 | 核心配置 | 验证点 |
|---|------|---------|--------|
| 10 | OB写入日志 | repayWithholdObWriteLog=false→true | 开关控制OB写入详细日志 |
| 11 | OB读取日志 | repayWithholdObReadLog=false→true | 开关控制OB OUTREQ/OUTRESP日志 |

### 监控配置（2条）

| # | 用例 | 核心配置 | 验证点 |
|---|------|---------|--------|
| 12 | 监控默认关闭不告警 | monitorEnabled=false, monitorDayDiff=1 | 查询历史数据无ERR日志 |
| 13 | 监控开启触发告警 | monitorEnabled=true, monitorDayDiff=1 | 查询超过1天数据打印 ERR 监控order_repay_withhold表历史数据 |

### 业务回归（1条）

| # | 用例 | 核心配置 | 验证点 |
|---|------|---------|--------|
| 14 | 星选TRIPLE端到端 | writeMode=TRIPLE, readNew=true | 写入→三表验证→查询→日志确认→数据比对 |

---

## 监控配置说明

### 配置项

| 配置 Key | 默认值 | 说明 |
|---------|--------|------|
| `aps.switch.control.monitorEnabled` | false | true=打开监控，检查order_repay_withhold表历史数据访问 |
| `aps.switch.control.monitorDayDiff` | 1 | 监控差值天数阈值，date_created超过此天数的数据被访问时触发告警 |

### 告警日志格式

当 monitorEnabled=true 且查询/更新的数据 date_created 超过 monitorDayDiff 天时：

```
ERR 监控order_repay_withhold表历史数据 ...
```

---

## 测试规则

> 📌 **重要规则：任何对测试用例的额外补充、修改说明、测试技巧、注意事项，都必须同步更新到本测试说明文档中。** 确保测试说明始终是最新、最完整的测试指导文档。

### 规则明细

1. **测试渠道固定**：本需求的冷热分离验证统一使用星选（XingXuan）渠道，避免多渠道混用导致排查困难
2. **日志验证必查**：读取路由的验证**必须通过日志确认**实际 SQL 访问的表名，不能仅凭接口返回结果判断
3. **还款订单号即日志关键字**：每次测试的 `repay_order_id`（格式 RN+日期+序列号）即日志搜索关键字，测试时记录下来方便回溯
4. **OB写入异步等待**：OB 表写入为事务提交后异步执行，验证 OB 数据时需等待 3-5 秒再查询
5. **Apollo 开关变更后等待生效**：修改 Apollo 配置后等待 1-2 秒确保配置刷新
6. **detail/bill 表必落主库**：`order_repay_withhold_detail` 和 `order_repay_withhold_bill` 仅存在于主库，不受 Apollo 读写路由开关控制，所有写入模式（OLD_ONLY/TRIPLE/DUAL）下均需落库到主库

---

## 更新记录

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-06-14 | 初始版本：星选渠道测试说明、日志验证方法、测试规则 | wangxue-jk |
| 2026-06-14 | v2：新增Apollo配置清单（6个配置）、新增监控配置用例（monitorEnabled/monitorDayDiff）、用例简化至14条 | wangxue-jk |
| 2026-06-15 | v3：新增 order_repay_withhold_detail 和 order_repay_withhold_bill 落库规则（仅主库、必落），更新 DB 分布表、测试流程 Step 5/6、规则 #6，7 条写入相关用例预期结果同步更新 | wangxue-jk |
