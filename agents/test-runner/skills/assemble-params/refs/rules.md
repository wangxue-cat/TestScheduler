# assemble-params 详细规则

## 1. 规则加载优先级

先读 `memory/api_channels_rules/common_rules.md`（通用规则），再读 `memory/api_channels_rules/{channel}.md`（渠道规则）。

⚠️ **字段冲突时以渠道规则为准**：同一参数在通用规则和渠道规则中均有定义时，使用渠道规则中的取值。

## 2. 参数填充四级优先级

### 优先级 1 — 用户显式指定

若 `user_params` 中有对应 key，直接使用。

### 优先级 2 — 渠道规则文档

从 `api_channels_rules/{channel}.md` 中查找参数的默认值、生成规则、数据依赖。

例如：
- `account_id` → "从已放款数据中查 partner_user_no 表"
- `repay_order_id` → "随机生成 RN+日期格式"
- `amount` → "取已放款数据的借款金额"

### 优先级 3 — 随机生成

调用 `testmind:common_tool_execute` 随机生成：
- 身份证号 → genIdCard
- 手机号 → genPhone
- 姓名 → genName
- 银行卡号 → genBankCard
- 订单号 → 时间戳+随机数

### 优先级 4 — 保留占位符

无法填充的保留 `{paramName}` 格式，标记为 incomplete。

## 3. 保留占位符标记

保留占位符的步骤标记为 incomplete，供用户确认。

## 4. 随机数据日志

随机生成的数据在日志中记录，供后续 Bug 分析使用。

## 5. DB 查询参数复用

DB 查询获取的 account_id 在同一 case 内复用，不重复查询。

## 6. 渠道规则文档路径

`memory/api_channels_rules/{channel}.md`，参数获取规则在此维护。

## io_bindings 数据依赖处理

两种方式：
1. **平台拼接用例**：将上下游接口在自动化平台拼接为完整用例，参数依赖由平台处理
2. **渠道规则文档**：在 `api_channels_rules/{channel}.md` 中写明数据获取规则，assemble-params 按规则从 DB 查询填充
