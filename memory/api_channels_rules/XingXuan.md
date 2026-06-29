# 星选渠道规则

> 星选（XingXuan）渠道专用参数取值规则，通用规则见 `common_rules.md`。

## 随机数生成规则

### 基础格式

```
{毫秒级时间戳}{4位随机数字}
```

- 毫秒级时间戳：如 `20260615095814001`（17位）
- 4位随机数字：`0000` ~ `9999`

### 各字段前缀规则

| 字段 | 阶段 | 前缀 | 格式 | 示例 |
|------|------|------|------|------|
| **req_id** | 授信阶段 | `C` | `C{毫秒时间戳}{4位随机}` | `C202606150958140010123` |
| **req_id** | 授信后 | — | 从 DB 取值 | 见下方说明 |
| **account_id** | 授信前 | — | `{年份+1000}{毫秒时间戳后段}{4位随机}` | `302606150958140010123` |
| **account_id** | 授信后 | — | 从 DB 取值 | 见下方说明 |
| **loan_id** | 借款阶段 | `B` | `B{毫秒时间戳}{4位随机}` | `B202606150958140020456` |
| **loan_id** | 借款后 | — | 从 DB 取值 | 见下方说明 |
| **repay_order_id** | 还款阶段 | `R` | `R{毫秒时间戳}{4位随机}` | `R202606150958140030789` |
| **repay_order_id** | 还款后 | — | 从 DB 取值 | 见下方说明 |
| **order_no**（还款通知） | 任意 | — | `{毫秒时间戳}{4位随机}` | `202606150958140040321` |
| **trade_time** | 任意 | — | `当前时间` | `2026-06-12 22:59:36` |

> **account_id 特殊规则**：在 req_id 的年份上加 1000 年以示区分。如 `20260615095814001` + 4位随机 → account_id 用 `30260615095814001` + 4位随机。

---

## 各字段详细说明

### 1. req_id — 授信流水号

授信申请的唯一标识。

| 阶段 | 获取方式 | 说明 |
|------|---------|------|
| **授信阶段** | 随机生成 | `C{毫秒时间戳}{4位随机}` |
| **授信后阶段** | 从 DB 查询 | `aps.order_info` 表的 `order_no_partner` 字段 |

> **查询示例**：`SELECT order_no_partner FROM aps.order_info WHERE partner_code = 'XingXuan' AND appl_state = 'APS' ORDER BY id DESC LIMIT 1`

### 2. account_id — 合作方用户 ID

合作方侧用户唯一标识，**同一用户固定不变**，可多次授信（account_id 不变，流水号变）。

| 阶段 | 获取方式 | 说明 |
|------|---------|------|
| **授信前** | 随机生成 | `{年份+1000}{毫秒时间戳后段}{4位随机}`，如 `302606150958140010123` |
| **授信后** | 从 DB 查询 | `aps.partner_user_order_relation` 表的 `partner_user_no` 字段 |

> **查询示例**：`SELECT partner_user_no FROM partner_user_order_relation WHERE order_no = '{order_no}' LIMIT 1`
>
> **兜底规则**：若 partner_user_order_relation 无记录，则 account_id = `aps.order_info.order_no_partner`。

### 3. loan_id — 借款流水号

借款申请的唯一标识。

| 阶段 | 获取方式 | 说明 |
|------|---------|------|
| **借款阶段** | 随机生成 | `B{毫秒时间戳}{4位随机}` |
| **借款后** | 从 DB 查询 | `aps.order_iou` 表 |

> **查询示例**：`SELECT * FROM order_iou WHERE user_no = '{user_no}' ORDER BY id DESC LIMIT 1`

### 4. repay_order_id — 还款流水号

还款申请的唯一标识。

| 阶段 | 获取方式 | 说明 |
|------|---------|------|
| **还款阶段** | 随机生成 | `R{毫秒时间戳}{4位随机}` |
| **还款后** | 从 DB 查询 | `aps.order_repay_withhold` 表的 `repay_tran_no` 字段 |

> **查询示例**：`SELECT repay_tran_no FROM order_repay_withhold WHERE order_no = '{order_no}' ORDER BY id DESC LIMIT 1`
>
> > ⚠️ **注意**：API 参数名为 `repay_order_id`，落库到 DB 的 `repay_tran_no` 字段，两者值相同（均为 `R` 前缀的还款流水号）。

### 5. order_no（还款通知接口专用）

还款通知接口的 `order_no` 参数，**随机生成即可，无其他用途**。

> ⚠️ **注意区分**：其他地方的 `order_no` 通常指 `aps.order_info` 表的 `order_no` 字段（授信订单号），与还款通知的 `order_no` 不同。

### 6. trade_time — 交易时间

当前时间，格式为 `yyyy-MM-dd HH:mm:ss`。

| 项目 | 说明 |
|------|------|
| **获取方式** | 执行时取系统当前时间 |
| **格式** | `2026-06-12 22:59:36` |
| **适用范围** | 所有需要传入交易时间的接口 |

> **生成示例**：`"2026-06-15 10:15:30"`

---

## 字段来源速查

| 字段 | 首次出现阶段 | 随机生成格式 | 后续来源（表.字段） |
|------|-------------|-------------|-------------------|
| req_id | 授信 | `C{17位毫秒}{4位随机}` | `order_info.order_no_partner` |
| account_id | 授信前 | `{年+1000}{后段毫秒}{4位随机}` | `partner_user_order_relation.partner_user_no` |
| loan_id | 借款 | `B{17位毫秒}{4位随机}` | `order_iou` |
| repay_order_id | 还款 | `R{17位毫秒}{4位随机}` | `order_repay_withhold.repay_tran_no` |
| order_no（还款通知） | 还款通知 | `{17位毫秒}{4位随机}` | 无需查 DB |
| trade_time | 任意 | 当前时间 `yyyy-MM-dd HH:mm:ss` | 无需查 DB |

---

## 其他注意事项

- 同一流程内所有字段值保持不变，不重复随机生成
- 随机数字段值记录到 `d:\TestScheduler\memory\api_channels_rules\XingXuan_flow_log.json`
- 授信后流程获取 account_id 须遵循通用规则的三步查询法
