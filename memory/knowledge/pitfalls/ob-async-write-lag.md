---
name: ob-async-write-lag
description: OB库(apss-ob)写入是afterCommit异步执行，有约1秒延迟，验证前需等待3-5秒，date_updated差1秒属正常
metadata:
  type: project
  tags: [OB, 异步写入, 落库验证, APS]
  related_requirements: [NREQUEST-49267]
---

# OB库异步写入有1秒延迟

## 现象

OB表（`apss-ob.order_repay_withhold_backup`）的写入是事务提交后异步执行（`afterCommit`），存在约1秒的写入延迟。

DUAL 模式下，热表与 OB 表的 `date_updated` 字段可能差 1 秒，这是异步写入的正常时间差，**不是 Bug**。

## 影响

如果在接口调用后立即查询 OB 表，可能因数据尚未写入而误判为"OB未落库"。

## 正确做法

1. **调用写入接口后等待 3-5 秒**再查询 OB 表
2. `date_updated` 差 1-2 秒属于正常现象，不作为不一致判定依据
3. 其他 30 个字段应完全一致

## 关联

- [[aps-cold-hot-separation-test-pattern]] — APS冷热分离测试全模式
- [[apollo-timeout-but-effective]] — 另一个容易误判的场景

## 来源

NREQUEST-49267 aps库大表order_repay_withhold冷热分离治理，2026-06-15 STG2 执行验证
