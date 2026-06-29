---
name: sql-execute
description: SQL 执行的高层模式积累（跨 Agent 的 SQL 使用经验，不替代 sql-execute wrapper 的底层规则）
metadata:
  type: experience
  skill: testmind:sql-execute
  version: 1
  evolution_count: 0
  last_updated: 2026-06-24
  sources: []
---

# sql-execute 经验积累

> **路由方式**: 委托给 `agents/test-runner/skills/sql-execute/`
> **本文件作用**: 积累跨 Agent 的 SQL 使用模式和踩坑经验（高层），底层规则（环境路由/SQL安全/编码修复/sharding回退）由 wrapper 自己管理。

## 核心原则

{{待积累}}

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| APS 冷热分离验证 | 查完热表后等待 3-5 秒再查 OB 表 | OB 库写入是 afterCommit 异步执行 |
| 带加密字段的查询 | 注意加密字段（_encryptx, _md5x）需解密后才能比对 | 存储的是密文 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

## 关联

- 底层规则: `agents/test-runner/skills/sql-execute/refs/rules.md`
- 冷热分离: [[aps-cold-hot-separation-test-pattern]]
- OB 异步延迟: [[ob-async-write-lag]]
