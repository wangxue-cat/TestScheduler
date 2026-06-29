# get-current-week-sprint-env 经验积累

---
name: get-current-week-sprint-env
description: 获取当前迭代版本+环境+用户信息
metadata:
  type: experience
  skill: testmind:get-current-week-sprint-env
  version: 1
  evolution_count: 1
  last_updated: 2026-06-25
  sources: []
---

# get-current-week-sprint-env 经验积累

## 核心原则

{{principles discovered through repeated use}}

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| 获取当前迭代环境 | 直接调用，无参数 | 接口自动返回当前用户所属迭代信息 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

- [1] **sprint_name 格式**: `YYYYMMDD 迭代版本`（如 `20260625 迭代版本`），非"常规版本"等其他变体。查询 SQL: `select env from sprint_env_relation where sprint_name='{date} 迭代版本' and is_deleted=0 limit 1`，qoa 库固定查 STG2。确认于 2026-06-25。

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
