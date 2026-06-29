# verify-db-exists 输入/输出定义

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON |
| execution_results_path | string | 否 | 执行结果缓存，用于解析占位符 |
| env | string | 否 | 默认取 plan 中的 env 字段或 STG2 |

## 执行步骤展开

### Step 1: 解析执行计划

从 `cases[]` 中提取所有 `steps[]` 中 `type == "db"` 的步骤，收集：
- case_name、step_seq、description
- subsystem、database、table
- key（WHERE 条件模板）
- expect（exists / not_exists）
- capture_fields、compare、wait_seconds

### Step 2: 解析参数占位符

见 [refs/rules.md](rules.md) 第1条。

### Step 3: 数据库路由

`subsystem + database` → `db_info_processed.json` → `db_name`

见 [refs/rules.md](rules.md) 第2条。

### Step 4: 执行存在性查询

通过 `testmind:sql-execute` 执行：

**expect = "exists"**
```sql
SELECT {capture_fields 或 *} FROM {table} WHERE {key} LIMIT 1
```
验证返回行数 > 0。若 `capture_fields` 非空，记录捕获值。

**expect = "not_exists"**
```sql
SELECT 1 FROM {table} WHERE {key} LIMIT 1
```
验证返回行数 == 0。

**wait_seconds 处理**
见 [refs/rules.md](rules.md) 第5条。

### Step 5: 输出结构化结果

按 case_name 分组输出。

## 输出 JSON Schema

```json
{
  "requirement_id": "NREQUEST-49267",
  "verified_at": "2026-06-15T14:00:00",
  "db_existence_checks": [
    {
      "case_name": "aps冷热分离-写入-OLD_ONLY仅写旧表",
      "step_seq": 2,
      "directive": {
        "table": "order_repay_withhold",
        "database": "aps",
        "subsystem": "aps-app",
        "key": "repay_tran_no = 'R17814957104970512'",
        "expect": "exists"
      },
      "verification": {
        "status": "verified_consistent",
        "sql_executed": "SELECT * FROM order_repay_withhold WHERE repay_tran_no = '...' LIMIT 1",
        "db_name": "aps_stg2",
        "found": true,
        "row_count": 1,
        "captured_fields": { "id": "202", "repay_tran_no": "..." },
        "evidence": "Record id=202 in aps_stg2.order_repay_withhold"
      }
    }
  ],
  "placeholder_issues": [],
  "cannot_verify": []
}
```
