---
name: upload-testcases
description: 上传用例Excel到QOA平台并关联Story
argument-hint: "<excel_path> <requirement_id>"
---

# upload-testcases ★ 移植自 ClaudeMind

> **来源**: `D:\ClaudeMind\.claude\agents\testcase-writer\skills\upload-testcases\SKILL.md`
> 
> 本文件为移植占位。将测试用例 Excel 上传到 QOA 平台并关联对应 Story。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| excel_path | string | 是 | 用例 Excel 路径 |
| requirement_id | string | 是 | 需求编号 |

## 输出

```json
{
  "status": "success",
  "uploaded_cases": 5,
  "linked_stories": ["JYSG-xxxxx"]
}
```

## 规则

- 🔴 高风险操作，必须 Human Confirm
