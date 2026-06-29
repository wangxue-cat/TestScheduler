---
name: testcase-code-analyze
description: 面向测试用例生成的代码分析，识别测试点和覆盖缺口。QOA平台查询为空时自动fallback到本地git diff+源码阅读深度分析。
metadata:
  type: experience
  skill: testmind:testcase-code-analyze
  version: 1
  evolution_count: 1
  last_updated: 2026-06-26
  sources: [NREQUEST-49352]
---

# testcase-code-analyze 经验积累

## 核心原则

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->
- **QOA无报告时的本地深度分析模式** (确认1次): 当QOA平台 testcase-code-analyze 查询返回空(count=0)时，自动fallback到本地分析流程：(1) query stories via story-manage to find associated JYSG-keys, (2) git merge-base → diff --stat 获取变更范围, (3) git diff 各模块关键文件获取详细diff, (4) Read 新增/核心文件源码进行深度阅读, (5) 按模块编译测试点 → Apollo配置 → DB变更 → 专项测试场景 → 风险清单 → 优先级建议的完整报告结构。来源: NREQUEST-49352 / JYSG-149999.

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
