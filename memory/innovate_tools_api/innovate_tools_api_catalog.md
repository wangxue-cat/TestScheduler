---
name: innovate-tools-api-catalog
description: innovateTools API小工具合集，协助查询/处理API渠道流程（用户/授信/借款/还款等），含参数结构
metadata: 
  node_type: memory
  type: reference
  originSessionId: 4039aa91-1c68-456e-9ce9-fb2f0f490ea2
---

# innovateTools API小工具合集

**定义**: API小工具合集，协助查询、处理API渠道流程，包括查询/处理用户、授信、借款、还款等

**公共前缀**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools`

**共计 21 个接口**

### 请求Headers（所有接口通用）
- **Content-Type**: `application/json`
- **token**: 从 `token.txt` 读取（token会定期变化，更新该文件即可）

> token文件路径: `d:\TestScheduler\memory\innovate_tools_api\token.txt`

### 通用参数（所有接口必填）
- **`env`** (必填) — 环境 (STG1/STG2)，用户未指定时默认 STG2

---

## 用户查询

### 1. 查询用户的三要素、银行卡号、授信评级、额度信息、及管制禁申信息
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/getUserInfo/`
- **Source**: `getUserInfoApi.py`
- **功能**: 根据用户号、客户号、手机号、order_no查询用户信息

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`user`** (必填) — 用户号、客户号、手机号、order_no

### 2. 获取随机用户信息
- **Method**: `GET`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/getRandomUserInfo/`
- **Source**: `getRandomUserInfoApi.py`
- **功能**: 获取随机用户信息（APS开发使用）

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)

---

## 授信处理

### 4. APV借款mock
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/apvMock/`
- **Source**: `apvMockApi.py`
- **功能**: APV审批mock，模拟审批通过/拒绝

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`keyName`** (必填) — mock键名
- **`keyValue`** (必填) — mock键值
- **`mockStatus`** — mock状态 (默认: `APS`)

### 5. 卡授信重试工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/creditRetry/`
- **Source**: `creditRetryApi.py`
- **功能**: 卡授信流程重试

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`order_no`** (必填) — 订单号
- **`output_format`** (必填) — 输出格式：json 或 html
- **`appl_no_apv`** (必填) — APV申请号
- **`result`** (必填) — 当前APV阶段结果

---

## 借款处理

### 6. 获取借款信息by借据
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/getLoanInfo/`
- **Source**: `getLoanInfoApi.py`
- **功能**: 根据用户号查询借据/借款信息

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`user`** (必填) — 用户号

### 7. 解决用户借款无子产品
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/updateThirdInfo/`
- **Source**: `updateThirdInfoApi.py`
- **功能**: 修复用户借款无子产品问题

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`orderNo`** (必填) — 订单号
- **`userLever`** — 用户层级
- **`thirdCode`** — 资方编码

### 8. 更新API流量 授信或借款OCR信息
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/updateFace/`
- **Source**: `updateFaceApi.py`
- **功能**: 更新API渠道授信或借款的OCR信息

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`orderNo`** (必填) — 订单号
- **`address`** — 地址
- **`type`** (必填) — 授信=更新授信人脸OCR，其他值=更新借款人脸OCR
- **`status`** — 状态 (默认: `03`)
- **`isReal`** — 是否真实 (默认: `N`)

### 9. 清除用户信息
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/deletePpdInfo/`
- **Source**: `deletePpdInfoApi.py`
- **功能**: 清除用户相关信息

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`user`** (必填) — 用户号

---

## 还款处理

### 10. APS查询还款计划
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/LoanRepaymentPlan/`
- **Source**: `loanRepaymentPlanApi.py`
- **功能**: 查询APS还款计划详情

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`input_param`** (必填) — 输入参数
- **`output_format`** — 输出格式 (默认: `json`)
- **`ln_loan_fields`** — 借款字段
- **`tr_tran_proc_fields`** — 交易处理字段
- **`ln_plan_fields`** — 还款计划字段

### 11. 处理api还款相关
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/aiRepayHandle/`
- **Source**: `aiRepayHandleApi.py`
- **功能**: 处理API渠道还款相关操作

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`method`** (必填) — 方法分支

### 12. 还款批扣
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/ApsRepaymentBatchApi/`
- **Source**: `ApsRepaymentBatchApi.py`
- **功能**: APS还款批扣处理

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`method`** (必填) — 方法分支

---

## 流程自动化

### 13. 自动化
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/autoProcess/`
- **Source**: `autoProcessApi.py`
- **功能**: 多功能自动化处理，method参数决定具体操作

#### 通用参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`method`** (必填) — 方法分支
- **`orderNo`** (必填) — 订单号
- **`tranNo`** — 交易号
- **`status`** — 状态 (默认: `03`)
- **`term`** — 期数
- **`partnerCode`** — 合作方编码
- **`mockType`** — mock类型 (默认: `apvMock`)
- **`repaymentType`** — 还款方式
- **`custNo`** — 客户号
- **`RTranNo`** — 还款交易号
- **`repayStatus`** — 还款状态 (默认: `success`)
- **`dateSuccess`** — 成功日期
- **`overDueDays`** — 逾期天数 (默认: `5`)

#### method 分支
- `apsIouChange` — APS借据变更
- `repayOption` — 还款选项目
- `getCanLoanUser` — 获取可借款用户
- `handleRepayResult` — 处理还款结果
- `queryApsOrderApplState` — 查询APS订单申请状态

---

## 辅助工具

### 14. 调用定时任务
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/executeTasks/`
- **Source**: `executeTasks.py`
- **功能**: 手动触发定时任务执行

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`taskName`** (必填) — 任务名称
- **`appName`** (必填) — 应用名称

### 15. Dubbo接口转义
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/apsDubboEscapeApi/`
- **Source**: `APSDubboEscapeApi.py`
- **功能**: Dubbo接口参数转义处理

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`input_param`** (必填) — 输入JSON参数

### 16. 查询订单表工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/ApsOrderQueryDbApi/`
- **Source**: `ApsOrderQueryDbApi.py`
- **功能**: 查询订单相关数据库表

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`table_configs`** — 表配置 (默认: `''`)
- **`tables_per_row`** — 每行表数 (默认: `3`)
- **`page_title`** — 页面标题 (默认: `DB-订单查询结果`)
- **`min_length`** — 最小长度 (默认: `8`)

### 17. DB执行工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/APSDBOperationsApi/`
- **Source**: `APSDbOperations.py`
- **功能**: 执行数据库操作

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`input_param`** (必填) — 输入参数

### 18. Dubbo日志转接口工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/apsDubboLogParserApi/`
- **Source**: `APSDubboLogParserApi.py`
- **功能**: 将Dubbo日志解析转换为接口调用

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`log`** (必填) — 日志内容 (key可用 log/content/message/text)

### 19. APS日志查询工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/innovateTools/apsLogQueryTool/`
- **功能**: 查询APS系统日志

#### 参数
- **`env`** (必填) — 环境 (STG1/STG2)
- **`req_no`** (必填) — 请求编号 (与message二选一)
- **`message`** (必填) — 日志消息 (与req_no二选一)

### 22. 加解密小工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/finance/clioTools/`
- **功能**: Clio加解密工具，支持crypt加密/解密、md5x加密、md5加密

#### 参数
- **`operationType`** (必填) — 操作类型
  - 枚举值：
    - `clioDecrypt` — crypt解密
    - `clioEncrypt` — crypt加密
    - `clioMd5` — md5x加密
    - `md5` — md5加密
- **`data`** (必填) — 需要处理的数据

---

## 随机生成信息小工具

### 20. 随机生成信息小工具
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/finance/financeTools/`
- **功能**: 随机生成信息小工具，随机生成手机号、身份证号、银行卡号等

#### 参数
- **`operationType`** (必填) — 生成信息类型
  - 枚举值：
    - `random-mobileNo` — 随机手机号
    - `random-id` — 随机身份证号
    - `random-card` — 随机银行卡号

### 21. 生成指定银行卡信息
- **Method**: `POST`
- **URL**: `http://stg1-qoatools-app.daikuan.qihoo.net/finance/genBankCard`
- **功能**: 生成指定银行卡的银行卡信息，可指定卡bin、卡类型和生成数量

#### 参数
- **`cardType`** (必填) — 卡类型
  - 枚举值：
    - `bank` — 银行卡
    - `credits` — 信用卡
- **`cardBin`** — 银行卡卡bin，指定生成某银行的卡号
- **`amount`** (必填) — 生成数量 (默认: `1`)

---

## 自然语言调用指引

```
根据用户自然语言描述 → 匹配功能分类 → 确定接口 → 提取参数 → 调用接口
```

### 参数提取规则
1. `env` 为所有接口必填参数，用户未指定时默认 STG2
2. `{param}` 标记表示该参数需用户传入具体值
3. 带 `默认` 的参数如用户未提供则使用默认值
4. `method` 参数决定autoProcess进入哪个分支，必须明确指定
