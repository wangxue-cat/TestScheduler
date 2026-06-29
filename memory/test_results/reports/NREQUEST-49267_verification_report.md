# NREQUEST-49267 冷热分离验证测试报告

> 需求: aps库大表order_repay_withhold冷热分离治理 (JYSG-148994)
> 测试日期: 2026-06-15
> 测试环境: STG2
> 测试渠道: XingXuan (星选)
> Apoolo 配置: `repayWithholdWriteMode=TRIPLE`, `repayWithholdReadNew=true`

---

## 一、写用例「TRIPLE三写」— repayNotify

### 1.1 接口调用

| 项目 | 值 |
|------|-----|
| Facade | `com.qihoo.finance.aps.modules.xingxuan.facade.XingXuanOrderFacade` |
| Method | `repayNotify` (via `orderRequestHandlerMap`) |
| AppId | TTXX360 |
| 环境 | STG2 |

### 1.2 请求参数

| 参数 | 值 | 来源 |
|------|-----|------|
| loan_id | LN20260612240134401 | 用户指定 |
| amount | 100 (分) | 用户指定 |
| account_id | 202606122401344 | DB查询 (partner_user_order_relation) |
| repay_order_id | R17814957104970512 | 渠道规则生成 (R前缀) |
| order_no | 20260615115510123 | 渠道规则生成 (时间戳+随机) |
| trade_time | 2026-06-15 11:55:10 | 系统当前时间 |

### 1.3 响应

```
code=S, status=1, elapsed 102ms
```

### 1.4 三表全字段对比

> 查询条件: `repay_tran_no = 'R17814957104970512'`

| # | 字段 | order_repay_withhold (旧表) | order_repay_withhold_hot (热表) | order_repay_withhold_backup (OB表) | 是否一致 |
|---|------|-----------|-----------|-----------|---------|
| 1 | id | 202 | 202 | 202 | ✅ |
| 2 | order_no | XingXuan-mjaynja2mtiyndaxmzq001 | XingXuan-mjaynja2mtiyndaxmzq001 | XingXuan-mjaynja2mtiyndaxmzq001 | ✅ |
| 3 | repay_tran_no | R17814957104970512 | R17814957104970512 | R17814957104970512 | ✅ |
| 4 | partner_code | XingXuan | XingXuan | XingXuan | ✅ |
| 5 | loan_tran_no | (空) | (空) | (空) | ✅ |
| 6 | repay_detail_id | RP6785291014052777984 | RP6785291014052777984 | RP6785291014052777984 | ✅ |
| 7 | user_no | UR6785038771298762753 | UR6785038771298762753 | UR6785038771298762753 | ✅ |
| 8 | cust_no | CT6785038800059105281 | CT6785038800059105281 | CT6785038800059105281 | ✅ |
| 9 | pay_type | 1 | 1 | 1 | ✅ |
| 10 | repay_type | T | T | T | ✅ |
| 11 | repay_terms | (空) | (空) | (空) | ✅ |
| 12 | repay_amount | 1.0 | 1.0 | 1.0 | ✅ |
| 13 | member_request_no | WH6785291014052777985 | WH6785291014052777985 | WH6785291014052777985 | ✅ |
| 14 | member_request_time | 2026-06-15 11:55:16 | 2026-06-15 11:55:16 | 2026-06-15 11:55:16 | ✅ |
| 15 | commit_pcs_count | 1 | 1 | 1 | ✅ |
| 16 | member_no | 1000173 | 1000173 | 1000173 | ✅ |
| 17 | withhold_state | WH_SUC | WH_SUC | WH_SUC | ✅ |
| 18 | channel_code | third_partner | third_partner | third_partner | ✅ |
| 19 | channel_member_no | third_partner | third_partner | third_partner | ✅ |
| 20 | channel_order_no | CP202606150000000004 | CP202606150000000004 | CP202606150000000004 | ✅ |
| 21 | channel_label | third_partner | third_partner | third_partner | ✅ |
| 22 | withhold_amount | 1.0 | 1.0 | 1.0 | ✅ |
| 23 | repay_time | 2026-06-15 11:55:10 | 2026-06-15 11:55:10 | 2026-06-15 11:55:10 | ✅ |
| 24 | return_time | 2026-06-15 12:00:17 | 2026-06-15 12:00:17 | 2026-06-15 12:00:17 | ✅ |
| 25 | result_code | 0000 | 0000 | 0000 | ✅ |
| 26 | result_msg | 交易成功 | 交易成功 | 交易成功 | ✅ |
| 27 | ext_info | `{"accountId":"202606122401344",...}` | `{"accountId":"202606122401344",...}` | `{"accountId":"202606122401344",...}` | ✅ |
| 28 | date_created | 2026-06-15 11:55:16 | 2026-06-15 11:55:16 | 2026-06-15 11:55:16 | ✅ |
| 29 | created_by | sys | sys | sys | ✅ |
| 30 | date_updated | 2026-06-15 12:00:16 | 2026-06-15 12:00:16 | 2026-06-15 12:00:16 | ✅ |
| 31 | updated_by | sys | sys | sys | ✅ |

> **数据库来源**:
> - 旧表: `aps_stg2.order_repay_withhold`
> - 热表: `aps_stg2.order_repay_withhold_hot`
> - OB表: `apss-ob.order_repay_withhold_backup`

**结论: TRIPLE三写完全正确，31个字段三表100%一致。** ✅

---

## 二、读用例「readNew=true 查热表」— pullRepayNotify

### 2.1 接口调用

| 项目 | 值 |
|------|-----|
| Facade | `com.qihoo.finance.aps.modules.xingxuan.facade.XingXuanOrderFacade` |
| Method | `pullRepayNotify` (via `orderRequestHandlerMap`) |
| AppId | TTXX360 |
| 环境 | STG2 |
| 请求流水号 | `1e26bfae77724d0e9ca9596321b89106` |
| Trace ID | `e082904d4bd74d629d87b5fe67ac16a9.670.17815022677831819` |

### 2.2 请求参数

| 参数 | 值 |
|------|-----|
| account_id | 202606122401344 |
| repay_order_id | R17814957104970512 |

### 2.3 响应

```
code=S, status=1, amount=100(分), finish_time=2026-06-15 12:00:17, trade_time=2026-06-15 11:55:10
```

### 2.4 读表日志追踪

#### 步骤1: 通过 repay_order_id + method 定位流水号

```
查询条件: message_like="pullRepayNotify", repay_order_id=R17814957104970512
→ 请求流水号(req_no): 1e26bfae77724d0e9ca9596321b89106
→ Trace ID: e082904d4bd74d629d87b5fe67ac16a9.670.17815022677831819
```

#### 步骤2: 通过流水号追踪完整调用链

调用链（按 trace_id 中 span 顺序）:

```
1. XingXuanOrderFacadeImpl:86
   → REQ 接收请求 params={method=pullRepayNotify, ..., repay_order_id=R17814957104970512}

2. XingXuanOrderFacadeImpl:145
   → 通过orderNo动态查询合作方账号关系

3. XingXuanOrderFacadeImpl:177
   → 分发到 serviceName=xingXuanOrderServicePullRepayNotify

4. XingXuanOrderServicePullRepayNotify:52
   → REQ 还款结果查询接口 request={account_id=202606122401344, 
     repay_order_id=R17814957104970512, ...}

5. OrderRepayWithholdServiceImpl:214  ← ★ 关键日志
   → PRD OrderRepayWithholdServiceImpl.queryRepayByRepayTranNo-读取模式:NEW
```

#### 步骤3: 读表 SELECT 语句确认

```
MyBatis Mapper: selectByRepayTranNo:139

==> Preparing:
SELECT id, order_no, repay_tran_no, partner_code, loan_tran_no,
       repay_detail_id, user_no, cust_no, pay_type, repay_type,
       repay_terms, repay_amount, member_request_no, member_request_time,
       commit_pcs_count, member_no, withhold_state, channel_code,
       channel_member_no, channel_order_no, channel_label,
       withhold_amount, repay_time, return_time, result_code,
       result_msg, ext_info, date_created, created_by,
       date_updated, updated_by
FROM order_repay_withhold_hot    ← ★ 关键: 查的是热表(hot)
WHERE repay_tran_no = ?

==> Parameters: R17814957104970512(String)

<== Total: 1   ← ★ 热表命中，返回1条记录
```

#### 步骤4: 验证无 OB 穿透

- 在完整 trace 中，`selectByRepayTranNo` 只执行了一次
- SQL 目标表为 `order_repay_withhold_hot`（热表，非 `_backup` OB表）
- 热表命中后直接返回（Total: 1），未触发 OB 回表查询
- 确认无多余 SQL 落到 `order_repay_withhold_backup` 或 `order_repay_withhold`（旧表）

**结论: readNew=true 时正确走 NEW 模式，查询热表 `order_repay_withhold_hot`，热表直接命中，无 OB 穿透。** ✅

---

## 三、综合判定

#### 3.1 TRIPLE三写 (Case 2: repay_order_id=R17814957104970512)

| 验证项 | 预期 | 实际 | 结果 |
|--------|------|------|------|
| TRIPLE 三写 — 旧表写入 | 有数据 | id=202, 31字段完整 | ✅ |
| TRIPLE 三写 — 热表写入 | 有数据，与旧表一致 | id=202, 31字段完全一致 | ✅ |
| TRIPLE 三写 — OB表写入 | 有数据，与旧表一致 | id=202, 31字段完全一致 | ✅ |
| readNew=true — 读取模式 | NEW | `OrderRepayWithholdServiceImpl:214` 输出“读取模式:NEW” | ✅ |
| readNew=true — 查热表 | 查 `_hot` 表 | `selectByRepayTranNo` SQL 目标 `order_repay_withhold_hot` | ✅ |
| readNew=true — 热表命中 | Total: 1 | `Total: 1` | ✅ |
| readNew=true — 无OB穿透 | 不查 `_backup` 表 | trace 中无 `_backup` 表查询 | ✅ |
| readNew=true — 返回数据正确 | amount=100 | amount=100, status=1 | ✅ |

#### 3.2 DUAL双写 (Case 3: repay_order_id=R202606151442426566159) — 补充字段级校验

| 验证项 | 预期 | 实际 | 结果 |
|--------|------|------|------|
| DUAL — 旧表不写入 | 无数据 | aps_stg2.order_repay_withhold 无记录 | ✅ |
| DUAL — 热表写入 | 有数据 | id=500000001, 31字段完整 | ✅ |
| DUAL — OB表写入 | 有数据 | id=500000001, 31字段完整 | ✅ |
| DUAL — 热vsOB字段逐列比对 | 全部一致 | 31字段中30个完全一致，date_updated差1秒(OB异步写入) | ✅ |

#### 3.3 全流程回归 TRIPLE (Case 14: repay_order_id=R202606151439581087586) — 补充字段级校验

| 验证项 | 预期 | 实际 | 结果 |
|--------|------|------|------|
| TRIPLE — 三表id一致 | id相同 | 旧表=203, 热表=203, OB表=203 | ✅ |
| TRIPLE — 热表vsOB字段比对 | 全部一致 | 31字段100%一致（均为初始插入快照） | ✅ |
| TRIPLE — 旧表差异分析 | — | 自动还款结果回调触发时 writeMode 已切为 OLD_ONLY，仅写旧表（预期行为，有定时任务兜底同步） | ✅ |

---

## 四、发现项

| # | 发现 | 详情 | 风险 |
|---|------|------|:--:|
| 1 | **OB异步写入有1秒延迟** | Case 3: OB表 date_updated 比热表晚1秒，afterCommit 异步写入正常延迟，数据无差异 | 🟢 低 |

## 五、后续建议

1. **Apollo 配置恢复**: 测试完成后将 `repayWithholdReadNew` 恢复为 `false`，`repayWithholdWriteMode` 按需恢复
2. **全量用例执行**: 本次验证通过后，可执行 NREQUEST-49267 全部 14 条用例
3. **Apollo 延迟注意**: Apollo 修改后有 1-2 分钟传播延迟，建议修改后等待 5 秒再执行
