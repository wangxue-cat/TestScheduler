---
name: code-check
description: 代码静态检查：硬编码、空安全、资源管理、线程安全等常见问题
metadata:
  type: experience
  skill: testmind:code-check
  version: 1
  evolution_count: 1
  last_updated: 2026-06-26
  sources: []
---

# code-check 经验积累

## 核心原则

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

- [2026-06-26] QOA平台 code-check 的 method-change-query/delete-query 依赖平台预校验任务，当前迭代可能无数据返回。静态分析必须配合直接源码阅读才能完成深度检查。
- [2026-06-26] code-check 是代码归并/删除/方法变更检查工具，不是传统静态分析(SpotBugs/SonarQube)，无法直接检测硬编码、空安全、资源管理等问题。需自行阅读源码补充。
- [2026-06-26] 检查分布式锁正确性时需关注：锁超时参数是否可配置、try-with-resources 是否正确释放、double-check locking 第三步锁内查询是否正确执行、锁模式是否一致。

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

- [2026-06-26][1] 代码静态检查的标准流程：code-check 查询平台任务 + 直接源码阅读补充。平台任务覆盖方法变更/删除注释检查，源码阅读覆盖硬编码/空安全/资源管理/异常处理/事务边界/并发安全 6 维度。产出 Markdown 报告含 ISSUE 编号+文件+行号+修复建议。

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
