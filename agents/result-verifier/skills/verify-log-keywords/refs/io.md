# verify-log-keywords 输入/输出定义

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON 文件路径 |
| execution_results_path | string | 否 | 执行结果缓存（含 trace_id、req_no、时间戳） |
| env | string | 否 | 执行环境，默认取 plan 中的 env 字段 |

## 执行步骤展开

### Step 1: 收集日志校验指令

扫描执行计划中所有步骤，收集三类日志校验指令：

**a) check 步骤的关键字验证**
- `check.keyword` + `check.expect: "found"` → 关键字必须出现
- `check.negative_check` → 关键字必须不出现
- `check.sub_check` → 在主关键字命中的上下文中验证子条件
- `check.source` → 引用哪个步骤的日志（如 "step2日志"）

**b) post_check 指令**
- `expect: "positive_keyword found"` → 关键字必须出现
- `expect: "negative_keyword NOT found"` → 关键字必须不出现

**c) 计划级 log_verification 配置**
- `log_verification.app` → 日志所属应用
- `log_verification.keywords` → 关键字速查表
- `log_verification.log_classes` → 关键类的日志行号映射

### Step 2: 确定日志查询参数

对每个校验指令：

**a) 查询标识**
- `repay_order_id` / `repay_tran_no` → 主要搜索键
- `trace_id` / `req_no` → 精确追踪（若 execution_results 中有）
- 时间窗口 → 接口调用时间前后 3-5 分钟

**b) 查询关键字**
- 主关键字：`check.keyword` 或 `post_check` 中的 positive_keyword
- 反关键字：`check.negative_check` 或 negative_keyword

### Step 3: 执行日志查询

通过 `testmind:query-log` 执行：

**a) 正向验证 (expect: found)**
```
query-log: app={app}, keyword="{identifying_data} {check.keyword}", env={env}
```

**b) 反向验证 (negative_check / NOT found)**
```
query-log: app={app}, keyword="{identifying_data} {negative_keyword}", env={env}
```

### Step 4: 分类结果

- `verified_consistent`：日志状态与预期一致
- `mismatch`：日志状态与预期相反
- `cannot_verify`：日志不可用、查询失败、或关键标识数据缺失

## 输出 JSON 结构

```json
{
  "requirement_id": "NREQUEST-49267",
  "log_verifications": [
    {
      "case_name": "...",
      "step_seq": 3,
      "type": "keyword_found",
      "directive": { "keyword": "读取模式:OLD", "expect": "found", "source": "step2日志" },
      "verification": {
        "status": "verified_consistent",
        "found": true,
        "match_count": 1,
        "log_snippet": "OrderRepayWithholdServiceImpl:198 → PRD 读取模式:OLD",
        "query_params": { "app": "aps-app", "keyword": "...", "env": "STG2" }
      }
    }
  ]
}
```

三种 type 示例：
- `keyword_found` — 单关键字正向验证
- `keyword_found_with_negative` — 正向+反向组合
- `post_check_positive` — post_check 正向验证
