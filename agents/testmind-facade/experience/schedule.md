# schedule 经验积累

---
name: schedule
description: testmind:schedule 技能经验积累 — 调度/定时任务相关
metadata:
  type: experience
  skill: testmind:schedule
  version: 1
  evolution_count: 3
  last_updated: 2026-07-01
  sources: []
---

# schedule 经验积累

## 核心原则

{{principles discovered through repeated use — 升级到此处需 ≥3 次确认}}

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| 手动调用 schedule | 按 诊断→rollup→Teams日报→插件日报→回填 顺序执行，Teams失败不阻塞后续，CDP不可用时自动跳过 | 3次手动执行验证：诊断可发现迭代及时性问题；Teams常因CDP未开需要跳过；回填幂等安全 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

- **[2026-06-29]** 360Teams CDP导出失败：客户端停留在 `/#/user/login` 更新页面，无法进入主聊天页。需手动退出后以调试模式冷启动。status=requires_manual_quit，下次周期可重试。
- **[2026-06-29]** diagnose-test-in-time 脚本输出为 GBK 编码，直接用 Bash 工具捕获会乱码。需用 `subprocess.run(capture_output=True)` + `.stdout.decode('gbk')` 处理。

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

- **[2026-06-29]** 手动调用 schedule 执行5任务顺序：诊断→rollup→Teams日报→插件日报→回填。Teams失败不阻塞后续。（确认次数: 1）
- **[2026-06-30]** 手动调用 schedule 完整执行：诊断（20260611迭代）→rollup（2026-06-29）→Teams跳过（CDP未开）→日报上报15条→回填30天成功。（确认次数: 2）
- **[2026-07-01]** 手动调用 schedule 完整执行：诊断（20260702迭代，发现用例执行及时率71.61%+测试处理及时率85.71%双异常）→rollup（2026-06-30，9条entries）→Teams跳过（CDP未开，360Teams已在运行）→日报上报8条→回填31天全部成功。（确认次数: 3）

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
