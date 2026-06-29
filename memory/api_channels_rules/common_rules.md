# 渠道接口通用规则

> 所有渠道接口调用必须遵守以下通用规则。各渠道专用规则见 `api_channels_rules/{partner_code}.md`。

## 参数填充规则

### 优先级
1. 用户指定了参数 → 使用用户指定的值
2. 用户未指定参数 → 按以下规则随机生成
3. 未提供且无全局常量 → 保持占位符原样

### 同流程参数共享
同一流程内，所有接口使用同一套参数化值，不重复随机生成。
- 参数记录到流程 log 文件：`d:\TestScheduler\memory\api_channels_rules\{partner_code}_flow_log.json`
- 流程开始时生成并写入，后续接口直接读取

### 随机生成规则

| 参数类型 | 生成方式 | 示例 |
|---------|---------|------|
| name / custName / cardHolderName（姓名类） | 随机2-4个中文 | 张三丰 |
| phone / mobileNo / contactMobile / contact_phone（手机号类） | 调用小工具 `operationType=random-mobileNo` | 13812345678 |
| idNo / id_number / identity（身份证号） | 调用小工具 `operationType=random-id` | 460099199601011234 |
| cardNo / bank_account（银行卡号） | 调用 genBankCard 接口，随机选择卡bin生成 | 6232691234567890 |
| requestId | BC + 毫秒时间戳 + 4位随机数字 | BC2026060121270013424 |
| creditApplyNo / credit_trans_no / applyNo / req_id（流水号/申请号类） | 毫秒时间戳 + 4位随机数字 | 202606061901001342 |
| proCreditAcctNo / account_id（合作方侧用户号） | ⚠️ 见下方「渠道侧用户号获取规则」 | — |

### 渠道侧用户号获取规则（account_id / proCreditAcctNo）

> ⚠️ **这是最常见的出错点**：account_id 不能随机生成，必须根据流程阶段区分来源！

| 流程阶段 | 获取方式 | 说明 |
|---------|---------|------|
| **授信流程**（pushCreditInfo / pushOrderInfo 等） | 按渠道规则生成 | 不同渠道生成规则不同：部分渠道用身份证MD5，部分用时间戳+随机数（如头条account_id为纯数字） |
| **授信后流程**（绑卡/试算/借款/还款等） | **必须从数据库查询**，禁止随机生成 | 按下方「授信后流程数据获取规则」三步获取 |

**授信后流程获取 account_id 的步骤**：

1. 从 `aps.order_info` 查 `order_no` + `user_no` + `order_no_partner`（WHERE partner_code = '{渠道}' AND appl_state = 'APS'）
2. 用 `order_no` 去 `partner_user_order_relation` 查 `partner_user_no`
   - **有记录** → `partner_user_no` 就是 account_id
   - **无记录** → account_id 与授信申请单号相同，使用 `aps.order_info` 表的 **`order_no_partner`** 字段值
3. 不同渠道字段名不同：`account_id`（头条/星选等）、`proCreditAcctNo`（平安普惠等）

**❌ 禁止行为**：
- 在授信后流程中自行随机生成account_id → 会查不到对应的授信数据，接口报错
- 在授信后流程中用身份证MD5作为account_id → 只有授信流程部分渠道才用MD5，授信后必须从DB查
- 混淆字段名：`user_id`（不存在）vs `user_no`、`status`（非授信状态）vs `appl_state`、`order_iou.status`（不存在）vs `order_iou.state`

### 全局图片常量（所有渠道通用）

以下三个图片 Base64 常量保存在 `global_constants.json`，**所有渠道共享同一套值**，各渠道仅字段名不同：

| 全局常量名 | 含义 | 值长度 | 各渠道常见字段名 |
|-----------|------|--------|----------------|
| `LIVE_IMG_BASE64` | 人脸照片 Base64 | ✅ 12,785 | live_img, livePic, faceImage |
| `FRONT_IMG_BASE64` | 身份证正面照片 Base64 | ✅ 183,296 | front_img, idcardFrontPic, frontImage |
| `BACK_IMG_BASE64` | 身份证背面照片 Base64 | ✅ 194,020 | back_img, idcardBackPic, backImage |

**使用方式**：渠道 JSON 中对应字段使用 `{LIVE_IMG_BASE64}` / `{FRONT_IMG_BASE64}` / `{BACK_IMG_BASE64}` 占位符，运行时自动从 `global_constants.json` 读取替换。

### 随机生成小工具调用
- **手机号/身份证号**：
  - **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/finance/financeTools/`
  - **Method**: POST
  - **参数**: `{ "operationType": "random-mobileNo" / "random-id" }`
- **银行卡号**：
  - **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/finance/genBankCard`
  - **Method**: POST
  - **参数**: `{ "cardType": "bank", "cardBin": "<随机选一个>", "amount": 1 }`
  - **cardBin 随机池**：`623269`、`621626`、`623058`、`602907`、`622989`、`627069`、`622986`

## 接口调用规则

### 单接口调用
用户明确说"调用xxx接口" → 只调用该接口

### 流程调用
用户未指定单接口 → 读取对应渠道的专用规则，按渠道流程依次调用

### 借款流程：试算与借款参数一致性
在同一借款流程中，如果包含**试算（drawPreCalc / calc / trial）**和**借款（draw / loan / borrow）**两个步骤，则：

> **试算接口的金额、期数 必须与 借款接口的金额、期数 保持一致**

| 约束字段 | 试算接口字段 | 借款接口字段 | 一致性要求 |
|---------|-------------|-------------|-----------|
| 借款金额 | amount / drawAmt / loanAmt | amount / drawAmt / loanAmt | 值必须相同 |
| 借款期数 | term / period / loanTerm | term / period / loanTerm | 值必须相同 |

**执行逻辑**：
1. 先调用试算接口，记录返回的金额和期数
2. 调用借款接口时，**强制复用**试算时使用的金额和期数，不再重新随机生成
3. 如果用户在借款步骤单独指定了不同的金额/期数，需**警告**用户与试算不一致，确认后方可执行

**适用渠道**：所有包含试算+借款流程的渠道（如头条、平安普惠、星选等）

### 借款金额默认值

当用户未指定借款金额时，使用默认值：

| 金额单位 | 默认值 | 说明 |
|---------|--------|------|
| 元 | 1000 | 1000元 |
| 分 | 100000 | 1000元 = 100000分 |

**判断逻辑**：
1. 用户明确指定了借款金额 → 使用用户指定的值
2. 用户未指定 → 使用默认金额1000元（注意金额单位，接口参数通常以分为单位，则填100000）
3. 借款金额不宜过大，避免因超出可用额度或触发风控规则导致接口异常

**⚠️ 金额单位注意**：各渠道接口的金额字段单位不同，需查看渠道JSON中 param_desc 的说明：
- **分为单位**（常见）：amount / loan_amount / bank_amount / drawAmt → 填 100000
- **元为单位**（少见）：需根据渠道具体定义判断

## 授信后流程数据获取规则

授信提交流程之后的接口（如绑卡、借款、还款等），通常需要授信通过的数据才可以正常操作。按以下三个步骤获取所需数据：

### 步骤一：查询授信订单信息

从 **aps.order_info** 表中查询授信订单，获取关键字段：

| 字段 | 含义 | 用途 |
|------|------|------|
| order_no | 授信订单号 | 步骤三的关联键 |
| user_no | 用户号 | 步骤二的查询键 |
| order_no_partner | 渠道侧授信申请单号 | 步骤三的兜底值（partner_user_order_relation 无记录时用作 account_id） |

> **⚠️ 字段名注意**：
> - 用户号字段是 **`user_no`**，不是 `user_id`
> - 授信状态字段是 **`appl_state`**，不是 `status`；授信通过值为 **`APS`**，不是 `CREDIT_PASS`
> - product_code 带前缀，如 **`360JIETIAO`**（不是 `JIETIAO`）、**`360API`**（不是 `API`）

> **查询示例**：`SELECT order_no, user_no, order_no_partner FROM aps.order_info WHERE partner_code = '{渠道}' AND appl_state = 'APS' ORDER BY id DESC LIMIT 1`

### 步骤二：根据用户号获取用户基本信息

根据步骤一获得的 **user_no**，调用**查询用户信息小工具接口**，获取：

| 信息 | 字段名（通用） | 说明 |
|------|---------------|------|
| 姓名 | name / custName | 用户真实姓名 |
| 身份证号 | idNo / identity | 用户身份证号 |
| 银行卡号 | cardNo / bank_account | 用户绑定的银行卡号 |

> **特殊处理**：如果查询结果中**没有银行卡号**，且该渠道有**绑卡接口**，则在提交借款接口前，必须**先调用绑卡接口**完成绑卡，再继续借款流程。

### 步骤三：查询渠道侧用户编号

根据步骤一获得的 **order_no**，去 **partner_user_order_relation** 表中查询渠道侧用户编号：

| 字段 | 含义 | 说明 |
|------|------|------|
| order_no | 授信订单号 | 关联键，来自步骤一 |
| partner_user_no | 渠道侧用户编号 | 该渠道对应用户的唯一标识 |

> **重要**：每个渠道的标识字段名不同，常见的有：
> - `account_id`（如头条、星选等）
> - `proCreditAcctNo`（如平安普惠等）
> - 其他渠道自定义字段名（见各渠道专用规则）
>
> **⚠️ partner_user_order_relation 无记录时的兜底规则**：
> 如果该 order_no 在 partner_user_order_relation 表中查不到记录，则 account_id 使用步骤一中 **`order_no_partner`** 字段的值（即渠道侧授信申请单号）。

### 流程汇总

```
授信通过
  │
  ├─ ① aps.order_info → 获取 order_no + user_no + order_no_partner
  │     ⚠️ 字段: user_no(非user_id), appl_state(非status), product_code带前缀(360JIETIAO非JIETIAO)
  │
  ├─ ② user_no → 查询用户信息小工具 → 获取 姓名/身份证/银行卡号
  │     └─ 若无银行卡号且有绑卡接口 → 先绑卡再借款
  │
  └─ ③ order_no → partner_user_order_relation → 获取 partner_user_no（即 account_id 等）
        └─ 无记录时 → account_id = order_no_partner
```

**适用场景**：所有授信后续流程（绑卡、试算、借款、还款等），在执行前必须先按此三步获取前置数据。
