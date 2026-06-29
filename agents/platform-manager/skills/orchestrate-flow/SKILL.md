---
name: orchestrate-flow
description: 编排测试流程（定义接口调用顺序、步骤依赖、数据流转）
argument-hint: "<channel> <flow_name> [steps]"
---

# orchestrate-flow

编排渠道的测试流程：定义接口调用顺序、步骤依赖关系和数据流转规则。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| channel | string | 是 | 渠道标识 |
| flow_name | string | 是 | 流程名称，如 "授信全流程"、"借款流程" |
| steps | array | 否 | 步骤定义（新建/更新时必填） |
| operation | string | 是 | query / create / update / delete |

## 执行逻辑

### query — 查询已有流程
1. 读取渠道 JSON 中的 flows 字段（如存在）
2. 调用 `testmind:auto-testcase-list` 获取平台上已有的流程用例
3. 返回本地 + 平台双视图

### create — 创建新流程
1. 验证每个 step 的 method 在渠道 JSON 中已定义
2. 定义 io_bindings（步骤间数据依赖）
3. 定义 flow 级别的参数（全局 account_id 等）
4. 写入渠道 JSON 的 flows 字段

### update — 更新流程
1. 定位 flow_name
2. 合并更新 steps
3. 重新验证 io_bindings 完整性

## 输出

```json
{
  "channel": "TouTiao",
  "flow_name": "授信全流程",
  "steps": [
    { "seq": 1, "method": "checkBefore", "description": "准入检查" },
    { "seq": 2, "method": "pushOrderInfo", "description": "提交授信申请", "io_bindings": {} },
    { "seq": 3, "method": "pullApplResult", "description": "查询授信结果", "io_bindings": { "uniqueNo": { "from_method": "pushOrderInfo", "from_field": "data.uniqueNo" } } }
  ]
}
```

## 规则

1. 流程中的每个 method 必须在渠道 JSON 的 interfaces 中已定义
2. io_bindings 的 from_method 必须是流程中的前序步骤
3. 流程定义写入渠道 JSON 的 `flows` 字段
