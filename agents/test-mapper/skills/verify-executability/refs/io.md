# verify-executability — 输入输出规范

## 输入

```json
{
  "parsed_cases": {
    "cases": [
      {
        "name": "用例名称",
        "priority": "高",
        "precondition": ["前置条件文本行1", "前置条件文本行2"],
        "steps": [
          {
            "seq": 1,
            "type": "interface|db|check|tool|config|unknown",
            "raw_text": "步骤原始文本",
            "expected": {
              "type": "field|db|db_update|log|mq|unknown",
              "raw_text": "预期结果原始文本"
            }
          }
        ]
      }
    ],
    "unknown_steps": []
  },
  "requirement_id": "NREQUEST-48847",
  "excel_path": "d:/TestScheduler/memory/testcases/NREQUEST-48847_testcases.xlsx",
  "channel": "头条智选",
  "env": "STG1"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `parsed_cases` | object | 是 | parse-case-steps 的输出 |
| `requirement_id` | string | 是 | 需求编号 |
| `excel_path` | string | 否 | Excel 路径，用于降级读取原始内容 |
| `channel` | string | 是 | 用户指定的渠道中文名 |
| `env` | string | 否 | 目标环境，默认 STG1 |

## 输出

### JSON（程序消费）

文件路径：`memory/execution_plans/{requirement_id}_executability_check.json`

```json
{
  "requirement_id": "NREQUEST-48847",
  "checked_at": "2026-07-01T16:00:00",
  "channel": "TouTiao",
  "channel_resolved": true,
  "env": "STG1",
  "summary": {
    "total_checks": 32,
    "pass": 25,
    "warn": 5,
    "block": 2
  },
  "can_proceed": false,
  "cases": [
    {
      "case_name": "头条智选促动支配置缺失不触发",
      "priority": "高",
      "verdict": "block",
      "steps": [{
        "seq": 1,
        "type": "interface",
        "raw_text": "...",
        "checks": [{
          "dimension": "channel_mapping",
          "result": "pass|warn|block",
          "detail": "...",
          "auto_fix": null
        }]
      }]
    }
  ],
  "blockers": [{
    "case_name": "...",
    "step_seq": 3,
    "dimension": "db_landing",
    "detail": "DB步骤未指定库名和表名",
    "suggestion": "请补充库名和表名，如'查询aps.aps_credit_pass_promotion_task'"
  }],
  "warnings": [],
  "auto_fixes": [{
    "case_name": "...",
    "step_seq": 1,
    "dimension": "channel_mapping",
    "fix": "渠道'头条智选'→ partner_code='TouTiao'"
  }]
}
```

### Markdown（供人阅读）

文件路径：`memory/execution_plans/{requirement_id}_executability_report.md`

使用 `templates/report.md` 模板渲染。
