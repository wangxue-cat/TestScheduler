---
name: file-bug
description: 根据失败分析生成Bug草稿，经用户确认后提交到缺陷系统
argument-hint: "<failure_analysis_path>"
---

# file-bug

将 analyze-failure 产出的 Bug 草稿提交到缺陷系统。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| failure_analysis | object/string | 是 | analyze-failure 的产出 |
| requirement_id | string | 是 | 需求编号 |

## 执行逻辑

### Step 1: 提取待提交 Bug
从 failure_analysis 中筛选 `bugs_to_file > 0` 且有 bug_draft 的失败项。

### Step 2: 展示 Bug 草稿 → Human Confirm
将每个 Bug 草稿格式化展示给用户：
```
═══════════════════════════════════════
  Bug #1: [NREQUEST-48504] confirmDraw接口参数校验失败
═══════════════════════════════════════
  严重程度: 一般
  重现步骤:
    1. 调用 checkBefore 准入
    2. 调用 pushOrderInfo 授信
    3. 调用 confirmDraw 借款
  预期结果: code返回000000
  实际结果: code返回999999，msg=参数校验失败
  关键日志: [ERROR] confirmDraw param validation failed: amount is required
  根因分析: 参数组装时amount字段未正确传递 (置信度: high)
═══════════════════════════════════════
```
询问用户：提交 / 修改后提交 / 跳过

### Step 3: 调用 testmind:bug-manage 提交
用户确认后，调用 `testmind:bug-manage` 提交：
- 标题: `[{需求ID}] {接口名} {失败现象简述}`
- 严重程度: 从 bug_draft.severity 获取
- 重现步骤: 从 bug_draft.reproduce_steps 获取
- 关联需求: requirement_id

### Step 4: 记录提交结果

## 输出

```json
{
  "requirement_id": "NREQUEST-48504",
  "filed_bugs": [
    { "bug_id": "JYSG-xxxxx", "title": "...", "status": "新建" }
  ],
  "skipped_bugs": [],
  "failed_submissions": []
}
```

## 规则

1. 提 Bug 是 🔴 高风险操作，必须 Human Confirm
2. 每次最多提交 5 个 Bug（防止误操作大量提交）
3. 提交失败不重试，返回错误信息给用户
