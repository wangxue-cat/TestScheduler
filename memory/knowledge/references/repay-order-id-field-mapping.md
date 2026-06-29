---
name: repay-order-id-field-mapping
description: API参数repay_order_id在DB中对应列repay_tran_no，不是repay_detail_id
metadata:
  type: reference
  tags: [字段映射, APS, 还款]
  related_requirements: [NREQUEST-49267]
---

# repay_order_id → repay_tran_no 字段映射

## 映射关系

| 层级 | 字段名 | 说明 |
|------|--------|------|
| API 请求参数 | `repay_order_id` | 还款订单号，格式 `R`+时间戳+序列号 |
| DB 列 | `repay_tran_no` | 还款交易流水号，**同一值** |

## ⚠️ 常见错误

```sql
-- ❌ 错误：用了 repay_detail_id
SELECT * FROM order_repay_withhold WHERE repay_detail_id = 'R202606151439581087586';

-- ✅ 正确：用 repay_tran_no
SELECT * FROM order_repay_withhold WHERE repay_tran_no = 'R202606151439581087586';
```

`repay_detail_id` 是还款明细 ID（格式 `RP` 开头），与 `repay_order_id` 是不同的字段。

## 涉及的表

- `order_repay_withhold`（旧表）
- `order_repay_withhold_hot`（热表）
- `order_repay_withhold_backup`（OB表）

三张表均使用 `repay_tran_no` 作为查询键。

## 来源

NREQUEST-49267 aps库大表order_repay_withhold冷热分离治理，2026-06-15 执行过程中发现此前映射错误并纠正
