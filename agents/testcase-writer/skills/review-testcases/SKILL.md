---
name: review-testcases
description: 评审测试用例覆盖度、重复检测、遗漏场景识别
argument-hint: "<excel_path> <requirement_id>"
---

# review-testcases

对生成的测试用例 Excel 进行评审：覆盖度检查、重复检测、遗漏场景识别。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| excel_path | string | 是 | 用例 Excel 路径 |
| requirement_id | string | 是 | 需求编号 |

## 输出

```json
{
  "coverage": { "covered": [...], "uncovered": [...] },
  "duplicates": [...],
  "missing_scenarios": [...],
  "suggestions": [...]
}
```
