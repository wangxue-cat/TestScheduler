---
name: query-log
description: 日志查询策略选择与踩坑经验积累 — 每次查询后观察并写回新模式
metadata:
  type: experience
  skill: testmind:query-log
  version: 1
  evolution_count: 7
  last_updated: 2026-06-24
  sources: [main-session, STG3, APS]
---

# query-log 经验积累

## 核心原则

**不是所有查询都适合实时日志。根据查询目标选择正确策略，避免无效试错。**

> ⚠️ 以下为 ≥3 次确认升级的硬规则

- **流水号/traceId 查询直接用定时日志** — 实时日志路径常常无效，且流水号跨应用
- **定时日志是流水号查询的首选，不是备选** — `--req-nos` / `--trace-ids` 自动搜索所有相关应用

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| 流水号 (req_no) | **定时日志** `--req-nos` | 流水号跨应用，定时日志自动搜索所有相关应用 |
| traceId | **定时日志** `--trace-ids` | 同上，traceId 跨应用链路追踪 |
| 关键字/错误日志 | **实时日志** `--pattern` | 已知应用+日志路径，实时无延迟 |
| 最新业务日志 | **实时日志** `--mode tail` | 看最新 N 行，快速 |
| 时间范围排查 | **定时日志** `--log-start-time/--log-end-time` | 按时间段检索 |
| 实时日志报 `invalid logfile path` | **立即降级定时日志** | 不反复尝试不同路径 |

## 系统→应用映射

> 🔄 每次发现新的系统-应用对应关系追加到此

| 用户说的系统 | 实际 package_name | 角色 |
|-------------|------------------|------|
| APS | `gws-aps-web` | 网关层（请求入口+响应出口） |
| APS | `aps-app` | 核心业务层（Dubbo 服务+DB操作） |
| APS | `aps-app-rd` | 数据报表 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

### 坑1: STG3 aps-app 实时日志路径无效
- **日期**: 2026-06-24
- **现象**: `/home/q/aps/aps-app/logs/aps-app_biz.log` 和 `/home/q/aps/logs/aps-app_biz.log` 均报 `invalid logfile path`
- **原因**: STG3 APS 的日志目录结构与标准公式不一致
- **解决**: 使用定时日志 `--req-nos` 成功，自动发现相关应用为 `gws-aps-web` + `aps-app`
- **教训**: STG3 APS 的实时日志路径不可用，流水号查询直接用定时日志
- **来源**: main-session, 2026-06-24

### 坑2: 流水号查询会跨应用
- **日期**: 2026-06-24
- **现象**: 用户说"APS系统"，实际日志分布在 `gws-aps-web` 和 `aps-app` 两个应用
- **原因**: 系统≠单个应用，一个请求经过网关层→业务层两个应用
- **解决**: 定时日志自动发现关联应用，比手动指定更可靠
- **教训**: 不要假设系统只对应一个 package_name
- **来源**: main-session, 2026-06-24

### 坑3: service-query 的 log_path 不可直接使用
- **日期**: 2026-06-24
- **现象**: service-query 返回 `log_path: /home/q/aps//logs`，与标准路径公式 `/home/q/aps/aps-app/logs/` 不一致
- **原因**: log_path 字段是服务注册时的元数据，可能存在格式问题（双斜杠、缺少应用名目录）
- **解决**: 不依赖此字段构造实时日志路径
- **教训**: service-query 的 log_path 仅供参考，不用于直接拼路径
- **来源**: main-session, 2026-06-24

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

### 模式1: 定时日志查流水号
- **日期**: 2026-06-24
- **发现**: 用 `--req-nos` 查流水号 `597c370610e3488f83e83f98fb22fe54`，定时日志瞬间返回完整请求链路（gws-aps-web → aps-app）
- **确认次数**: 1
- **来源**: main-session, STG3

### 模式2: 实时日志→定时日志降级
- **日期**: 2026-06-24
- **发现**: 实时日志连续 2 次 `invalid logfile path` 后切换到定时日志成功
- **确认次数**: 1
- **来源**: main-session, STG3

## 决策树

```
用户请求查日志
  ├─ 目标是流水号/traceId？
  │   └─ 是 → 直接用定时日志（--req-nos / --trace-ids）
  ├─ 明确知道应用+日志路径？
  │   ├─ 是 → 实时日志，1次尝试
  │   │   └─ invalid logfile path → 降级定时日志
  │   └─ 否 → 直接用定时日志
  └─ 实时日志无结果 → 告知用户，切换定时日志兜底
```

## 进化规则

1. 每次无效的实时日志调用 → 追加踩坑
2. 每次验证成功的路径/策略 → 追加模式（含确认次数）
3. 每次发现新的系统-应用映射 → 追加到映射表
4. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
5. 同类模式确认 ≥3 次 → 升级为「执行策略」条目

## 关联

- [[log-based-read-route-verification]] — 日志验证读取路由的标准方法
- [[aps-cold-hot-separation-test-pattern]] — APS 冷热分离测试中大量使用日志验证
