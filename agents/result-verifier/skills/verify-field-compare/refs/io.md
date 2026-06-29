# verify-field-compare 输入/输出定义

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON |
| captured_data | object | 是 | verify-db-exists 产出的 captured_fields |
| execution_results_path | string | 否 | 执行结果缓存 |
| env | string | 否 | 默认取 plan 中的 env |

## 执行阶段展开

### Phase A: 跨步骤单字段比对 (db_check.compare)

处理 `db_check.compare: { field, with_step, expect }` 指令：

1. 从本步骤的 captured_fields 获取 `field` 的值
2. 从 `with_step` 步骤的 captured_fields 获取同名字段的值
3. 比对：按 `expect` 判断（默认 `equal`）
4. 记录结果：`verified_consistent` 或 `mismatch`

### Phase B: 多表多字段全量比对 (check.compare_fields + all_equal)

处理 `check.compare_fields[]` + `check.expect: "all_equal"` + `check.tables[]` 指令：

1. **确定查询键**：从 db_existence 步骤中获取 shared key
2. **逐表查询**：对每个表用 shared key 查询全部字段
3. **构建比对矩阵**：行=字段，列=表名
4. **逐字段判定**：all_equal 或 mismatch
5. **扩展策略**：查询**全部字段**，compare_fields 是最小集合
6. **verify_each_round**：若为 true，对每轮重复比对

### Phase C: API 响应 vs DB 一致性 (compare_api_response_with_db)

1. 解析 `step{N}_response`（API 响应方法）和 `step{N}_db`（DB 表名）
2. 从 execution_results 提取 API 响应字段
3. 从 captured_data 提取 DB 字段
4. 按同名字段逐一比对
5. 若 execution_results 缺失 → `cannot_verify`

## 输出 JSON Schema

```json
{
  "requirement_id": "NREQUEST-49267",
  "field_comparisons": [
    {
      "type": "cross_step_compare",
      "case_name": "...",
      "verification": {
        "status": "verified_consistent",
        "current_value": "202",
        "with_step_value": "202",
        "match": true
      }
    },
    {
      "type": "multi_table_all_equal",
      "case_name": "...",
      "verification": {
        "status": "verified_consistent",
        "total_fields_compared": 31,
        "matched_fields": 31,
        "field_matrix": [{ "field": "id", "table_a": "202", "table_b": "202", "all_equal": true }]
      }
    },
    {
      "type": "api_vs_db_compare",
      "case_name": "...",
      "verification": {
        "status": "verified_consistent",
        "api_source": "pullRepayNotify response",
        "db_sources": ["order_repay_withhold", "order_repay_withhold_hot"],
        "all_matched": true
      }
    }
  ]
}
```
