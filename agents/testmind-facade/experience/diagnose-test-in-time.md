---
name: diagnose-test-in-time
description: testmind:diagnose-test-in-time 技能经验积累 — 测试流程及时性诊断
metadata:
  type: experience
  skill: testmind:diagnose-test-in-time
  version: 1
  evolution_count: 0
  last_updated: 2026-06-30
  sources: []
---

# diagnose-test-in-time 经验积累

## 核心原则

{{principles discovered through repeated use — 升级到此处需 ≥3 次确认}}

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| {{scenario}} | {{approach}} | {{rationale}} |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

- **[2026-06-30]** 脚本直接输出到 Bash stdout 遇到 GBK 编码错误（含特殊 Unicode 空格 ` `），必须设置 `PYTHONUTF8=1` + 重定向到临时文件再读取，否则会 UnicodeEncodeError 退出。
- **[2026-06-30]** sprint_name 使用最新迭代（"20260702 灰度版本"）时可能返回"数据获取为空"（迭代尚未开始），应回退到"20260611 迭代版本"等已结束迭代。

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

- **[2026-06-30]** 正确执行步骤：`subprocess.run(..., stdout=f, env={PYTHONUTF8:1})` 输出到临时 JSON 文件，再 `json.load(f, encoding='utf-8')` 解析。（确认次数: 1）

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
