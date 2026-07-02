---
name: bug-manage
description: Bug 提交/查询的经验积累
metadata:
  type: experience
  skill: testmind:bug-manage
  version: 1
  evolution_count: 2
  last_updated: 2026-06-29
  sources: []
---

# bug-manage 经验积累

## 核心原则

1. **Bug 创建必须两步前置查询**：`jira-issues --keyword <故事key>` 获取 sprint-id → `test-group-list` 获取 group-nos → 再 execute `create`
2. **Agent 上下文无 Bash 权限**：result-analyst Agent 无法直接执行 python 脚本，需由主会话执行; Agent 负责分析+组装命令，主会话负责执行
3. **描述可含复现步骤+日志+修复建议**：`--description` 支持多段落长文本，可以包含复现步骤、日志证据、根因分析、修复建议

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| Agent 内提 Bug | Agent 组装完整命令 → 主会话 Bash 执行 | Agent 上下文 Bash 不可用 |
| 缺少 sprint-id | `jira-issues --keyword <StoryKey>` | 必须从 Story 获取数字迭代 ID |
| 缺少 group-nos | `test-group-list` 查用户所属组 ID | create 接口必填 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->
- **2026-06-29**: Agent 上下文中 Skill(testmind:bug-manage) 仅加载文档不执行脚本，Bash 工具不可用。正确做法：Agent 负责组装完整 create 命令，由主会话（有 Bash）执行 python 脚本。
- **2026-06-25**: 主会话绕过门面直接调 Bash 脚本做 bug 状态流转。正确做法：所有 bug-manage 操作（查询/流转/详情）统一走 `Skill(testmind-facade)`，由门面加载经验后再路由。直接调 Bash = 丢失经验上下文 + 违反隔离规则。
- **2026-06-25**: `update --transition-status` 有 bug 已废弃，不要使用。API 返回 flag=S 但实际状态并未流转。正确做法：走 `Skill(testmind:bug-manage)` 的 `batch-transition` 或 `transition` 命令。

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->
- **2026-06-29**: sprint-id 2510 = JYSG 项目 20260702 迭代版本（来自 JYSG-149999 Story）；group-nos 5 = 产品创新组（wangxue-jk/王雪所属）
- **2026-06-29**: 系统测试阶段程序缺陷模板：project-key=JYSG, severity=一般, bug-new-type=程序缺陷, bug-stage=系统测试, packages=aps-app, duedate=today+4d
