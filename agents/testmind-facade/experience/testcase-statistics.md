---
name: testcase-statistics
description: 用例执行统计查询经验积累
metadata:
  type: experience
  skill: testmind:testcase-statistics
  version: 1
  evolution_count: 0
  last_updated: 2026-06-30
  sources: []
---

# testcase-statistics 经验积累

## 核心原则

按当前迭代版本 + 用户/测试组维度查询用例执行进度，区分总数/已执行/通过/失败/阻塞。

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| 查个人本周执行情况 | 传当前迭代版本 + 当前用户 | 聚焦个人进度 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->
- [2026-06-30] 查个人执行情况用 `case-exec --plan-name "<迭代版本>" --user "<中文名>"`，user 参数传中文名（如"王雪"）有效，非工号。返回含 `_execute_rate`/`_pass_rate`/`_executed_amount`/`_remaining_amount` 便捷字段。（确认 1 次）

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
