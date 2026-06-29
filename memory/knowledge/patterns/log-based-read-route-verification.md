---
name: log-based-read-route-verification
description: 读取路由验证不能仅靠接口返回，必须通过日志确认SQL的FROM表名和读取模式标记
metadata:
  type: project
  tags: [日志验证, 读取路由, 方法论, APS]
  related_requirements: [NREQUEST-49267]
---

# 日志验证读取路由的标准方法

## 核心原则

**读取路由的验证不能仅靠接口返回判断。** 必须通过日志中的 SQL 目标表名和读取模式标记来确认。

## 标准流程（4步法）

### Step 1: 定位请求流水号

用 `repay_order_id` + `method` 在日志中定位请求：

```
查询条件: message_like="pullRepayNotify" + repay_order_id 关键字
→ 得到 req_no（请求流水号）+ trace_id
```

### Step 2: 追踪完整调用链

通过 trace_id 追踪，关注以下关键日志点：

### Step 3: 定位读取模式标记

| 类 | 行号 | 日志内容 | 含义 |
|----|------|---------|------|
| `OrderRepayWithholdServiceImpl` | `:198` | `读取模式:OLD` | readNew=false，查旧表 |
| `OrderRepayWithholdServiceImpl` | `:214` | `读取模式:NEW` | readNew=true，查热表 |

### Step 4: 确认 SQL 目标表名

```
MyBatis: selectByRepayTranNo:139
→ Preparing: SELECT ... FROM order_repay_withhold_hot WHERE repay_tran_no = ?   ← 热表
→ Preparing: SELECT ... FROM order_repay_withhold WHERE repay_tran_no = ?       ← 旧表
→ Preparing: SELECT ... FROM order_repay_withhold_backup WHERE repay_tran_no = ? ← OB穿透
→ Total: N  ← 命中行数
```

### 附加检查

- **热表命中**：`Total: 1`，trace 中无 `_backup` 表查询
- **OB 穿透**：先出现 `_hot` + `Total: 0`，再出现 `_backup` + `Total: 1`

## 日志查询时间约束

触发时间前后 3-5 分钟即可。

## 关联

- [[aps-cold-hot-separation-test-pattern]] — 此方法在APS冷热分离中的实际应用
- [[repay-order-id-field-mapping]] — 查询时需要用对字段名

## 来源

NREQUEST-49267 aps库大表order_repay_withhold冷热分离治理，2026-06-15 STG2 执行验证
