# generate-verification-report 输入/输出定义

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| db_existence_results | object | 是 | verify-db-exists 的产出 |
| field_compare_results | object | 是 | verify-field-compare 的产出 |
| log_keyword_results | object | 是 | verify-log-keywords 的产出 |
| execution_plan_path | string | 是 | 原始执行计划（用于获取 case_name、priority、tags 等上下文） |
| requirement_id | string | 是 | 需求 ID |

## 执行步骤展开

### Step 1: 合并结果集

将三个 skill 的产出按 `case_name` 合并为统一的 case 视图。

从执行计划中补充每个 case 的元信息：
- `priority`、`tags`、`summary`
- `precondition`（用于报告中展示预期状态）

### Step 2: 计算汇总统计

按 case 粒度统计，维度见 [refs/rules.md](rules.md) 第6条。

### Step 3: 生成 JSON 报告

写入 `memory/test_results/verification/{req_id}_verification_report.json`。

JSON 结构包含：
- 元信息（requirement_id, title, channel, env, verified_at）
- 汇总统计
- 逐 case 的详细校验结果
- mismatch 明细（expected vs actual + evidence + severity）
- cannot_verify 明细（reason + suggestion）

### Step 4: 生成 Markdown 报告

写入 `memory/test_results/verification/{req_id}_verification_report.md`。

Markdown 结构见 [templates/report.md](../templates/report.md)。

### Step 5: 确保产出目录

若 `memory/test_results/verification/` 目录不存在则创建。

## 输出 JSON Schema

```json
{
  "requirement_id": "NREQUEST-49267",
  "requirement_title": "aps库大表order_repay_withhold冷热分离治理",
  "channel": "XingXuan",
  "env": "STG2",
  "verified_at": "2026-06-15T16:00:00",
  "source_plan": "memory/execution_plans/NREQUEST-49267_plan.json",
  "summary": {
    "total_cases": 14,
    "total_checks": 87,
    "by_type": { "db_existence": 42, "field_compare": 28, "log_keyword": 17 },
    "by_status": { "verified_consistent": 82, "mismatch_found": 2, "cannot_verify": 3 },
    "case_verdicts": { "all_verified": 10, "mismatch_found": 1, "partially_verified": 2, "fully_unverifiable": 1 }
  },
  "cases": [
    {
      "case_name": "aps冷热分离-写入-TRIPLE三写",
      "priority": "P0",
      "verdict": "all_verified",
      "db_existence_checks": [],
      "field_comparisons": [],
      "log_verifications": []
    }
  ],
  "mismatch_details": [],
  "unverifiable_details": []
}
```
