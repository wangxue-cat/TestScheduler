# apollo-config 经验积累

---
name: apollo-config
description: Apollo配置查询和修改的经验积累
metadata:
  type: experience
  skill: testmind:apollo-config
  version: 1
  evolution_count: 0
  last_updated: 2026-07-01
  sources: []
---

# apollo-config 经验积累

## 核心原则

（暂无，待积累）

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| 查询配置 | 直接调用 testmind:apollo-config | 无复杂逻辑 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
