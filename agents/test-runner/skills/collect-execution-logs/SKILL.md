---
name: collect-execution-logs
description: 收集执行日志，特别是失败步骤的详细日志和错误堆栈
argument-hint: "<execution_results_path>"
---

# collect-execution-logs

根据执行结果，对失败和异常的步骤收集应用日志。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_results_path | string | 是 | 执行结果 JSON 文件路径 |
| requirement_id | string | 是 | 需求编号 |

## 执行逻辑

### Step 1: 识别需要查日志的步骤
- 所有 status=failed 的步骤
- 所有 status=incomplete 的步骤（超时/网络错误）
- 所有返回异常但 validation 未覆盖的步骤

### Step 2: 查询应用日志
对每个需要查日志的步骤，调用 `testmind:query-log`：
- 按时间范围（步骤执行前后 1 分钟）
- 按关键字（method 名称、appId、错误码）
- 获取 ERROR/WARN 级别日志

### Step 3: 提取关键信息
- 错误堆栈
- 异常信息
- 参数校验失败详情
- 下游服务调用异常

### Step 4: 生成日志摘要
按 step 组织，输出结构化日志摘要。

## 输出

```json
{
  "requirement_id": "NREQUEST-48504",
  "collected_at": "2026-06-11T11:05:00",
  "logs": [
    {
      "case_name": "TouTiao借款-异常参数",
      "step_seq": 1,
      "method": "confirmDraw",
      "log_entries": [
        {
          "timestamp": "2026-06-11 11:00:01",
          "level": "ERROR",
          "message": "confirmDraw param validation failed: amount is required",
          "stack_trace": "..."
        }
      ]
    }
  ]
}
```

## 规则

1. 只收集失败/异常步骤的日志，成功的跳过
2. 日志查询时间窗口默认 ±1 分钟
3. 若查不到日志，标记为 `no_logs_found` 而非报错
