---
name: apollo-timeout-but-effective
description: Apollo配置修改操作返回超时不等同于失败，但必须调用查询接口确认修改成功后才能跑业务，不可仅凭返回值判断
metadata:
  type: project
  tags: [Apollo, 配置, 超时, 踩坑]
  related_requirements: [NREQUEST-49267]
---

# Apollo配置修改超时但实际已生效

## 现象

通过 Apollo 修改配置时，操作经常返回"超时"错误，给人一种操作失败的假象。但实际上配置已经推送并生效。

## 验证方法

❌ **错误做法**：看操作返回值，超时就认为失败，反复重试  
❌ **错误做法**：不看返回值，直接跑业务验证（如果配置实际未生效，业务验证结果不可信）  
✅ **正确做法**：

1. 修改配置后**等待 2-5 秒**
2. **调用 Apollo 查询接口**确认当前值是否为修改后的目标值
3. **确认修改成功后再跑业务**，不可在未确认的情况下直接进入业务验证
4. 若查询结果显示未修改成功 → 重试修改 → 再次查询确认

## 实际案例

NREQUEST-49267 测试中，以下 Apollo 操作均返回超时但实际已生效：
- `monitorEnabled`: true → false（超时但生效）
- `monitorEnabled`: false → true（超时但生效）
- `readNew`: true → false（超时但生效）

## 关联

- [[ob-async-write-lag]] — 另一个容易误判的场景

## 来源

NREQUEST-49267 aps库大表order_repay_withhold冷热分离治理，2026-06-15 STG2 执行验证
