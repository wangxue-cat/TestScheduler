# assemble-params 输入/输出定义

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| execution_plan_path | string | 是 | 执行计划 JSON |
| env | string | 否 | 默认 STG1 |
| user_params | object | 否 | 如 `{"account_id":"xxx"}` |

## 执行步骤展开

### Step 1: 加载执行计划和规则

- 读取 execution_plan.json
- **先**读 `memory/api_channels_rules/common_rules.md`
- **再**读 `memory/api_channels_rules/{channel}.md`
- 字段冲突时渠道规则优先

### Step 2: 按优先级填充参数

见 [refs/rules.md](rules.md) 第2条（四级优先级）。

### Step 3: 组装请求体

每个步骤生成 invokeFacade 请求体：
```json
{
  "env": "STG1",
  "service_name": "com.qihoo.finance.aps.modules.toutiao.facade.TouTiaoOrderFacade",
  "method_name": "orderRequestHandlerMap",
  "content": {
    "method": "checkBefore",
    "appId": "TouTiao360",
    "params": "{\"account_id\":\"111117629707700\"}"
  }
}
```

### Step 4: DB 查询类参数处理

若渠道规则要求从 DB 获取 account_id：
- 通过本地 `sql-execute` skill 查询（禁止直接调 `testmind:sql-execute`）
- 缓存结果供同一 case 内后续步骤使用

## 输出 JSON Schema

```json
{
  "requirement_id": "NREQUEST-48504",
  "env": "STG1",
  "cases": [
    {
      "case_name": "TouTiao信用申请-主流程",
      "steps": [
        {
          "seq": 1,
          "method": "checkBefore",
          "request_body": { "env": "...", "service_name": "...", "method_name": "...", "content": {...} },
          "param_sources": { "account_id": "user_provided" }
        }
      ]
    }
  ],
  "incomplete_params": []
}
```
