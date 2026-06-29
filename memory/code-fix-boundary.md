---
name: code-fix-boundary
description: 测试人员角色边界：不直接修改业务代码，只验证开发修复
metadata:
  type: feedback
  sources: [[verify-bug-fix]]
---

# 测试人员代码修改边界

## 核心原则

**测试人员只验证开发的修复是否合理，不直接修改业务代码。**

## Why

用户（王雪）的角色是测试人员，职责是验证而非实施修复。当发现 Bug 时：
- ✅ 分析根因、指出代码问题位置
- ✅ 提 Bug 给开发
- ✅ 开发修复后验证修复是否合理
- ❌ 直接编辑业务代码仓库（D:\project\aps、D:\project\gws-aps 等）

## How to apply

1. 代码分析定位到 Bug 根因后 → 提 Bug，在描述中写清楚根因和建议修复方向
2. 开发提交修复后 → 拉取远程代码，分析 diff，评估修复合理性
3. 不要直接在业务代码仓库做修改提交
4. TestScheduler 自身的配置/工具代码可以修改（如 CLAUDE.md、skill、memory）

## 例外

- TestScheduler 项目自身的代码（d:\TestScheduler\）不受此限制
- 测试脚本、工具脚本等非业务代码可以修改
