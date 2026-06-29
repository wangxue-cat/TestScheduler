# match-platform-interface 详细规则

## 1. 匹配来源唯一

只从平台接口列表（`testmind:auto-interface-list`）匹配，不凭空编造。

## 2. 禁止本地匹配

禁从本地 `memory/api_channels/` 匹配接口 — 该目录不再维护完整接口定义。所有接口定义唯一真相源是 QOA 自动化平台。

## 3. 无匹配处理

无匹配 → 标记 unmatched + 告知用户，不跳过。用户可选项：
- 手动指定平台接口 ID
- 通过 Platform Manager 录入新接口

## 4. 多候选处理

多个候选时选 confidence 最高的，并记录所有候选供用户参考。

## 5. 输出消费

匹配结果供 generate-execution-plan 使用，必须包含 `platform_id`。

## 6. 三级匹配策略

| 优先级 | 策略 | 示例 |
|--------|------|------|
| 1-精确匹配 | 步骤中文描述命中平台接口 `name` | "还款通知" → "星选还款通知" |
| 2-method匹配 | `interface_params.bodys` 中 method 命中 | "repayNotify" → platform method |
| 3-语义匹配 | 步骤意图与接口功能一致 | "查询还款结果" → "星选还款通知查询" |
