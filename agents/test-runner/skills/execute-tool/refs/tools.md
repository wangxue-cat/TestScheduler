# execute-tool 工具速查表

公共前缀: `http://stg1-qoatools-app.daikuan.qihoo.net`

## 随机生成类

| 需求 | 工具 | operationType |
|------|------|---------------|
| 随机手机号 | #20 financeTools | `random-mobileNo` |
| 随机身份证号 | #20 financeTools | `random-id` |
| 随机银行卡号 | #20 financeTools | `random-card` |
| 生成指定银行卡 | #21 genBankCard | — |

## 用户查询类

| 需求 | 工具 | 关键参数 |
|------|------|---------|
| 查询用户信息 | #1 getUserInfo | `user` (用户号/手机号/order_no) |
| 获取随机用户 | #2 getRandomUserInfo | — |
| 查询借款信息 | #6 getLoanInfo | `user` |
| 清除用户信息 | #9 deletePpdInfo | `user` |

## 加解密类

| 需求 | 工具 | operationType |
|------|------|---------------|
| crypt解密 | #22 clioTools | `clioDecrypt` |
| crypt加密 | #22 clioTools | `clioEncrypt` |
| md5x加密 | #22 clioTools | `clioMd5` |
| md5加密 | #22 clioTools | `md5` |

## 自动化处理类

| 需求 | 工具 | method |
|------|------|--------|
| 借据变更 | #13 autoProcess | `apsIouChange` |
| 还款选项 | #13 autoProcess | `repayOption` |
| 获取可借款用户 | #13 autoProcess | `getCanLoanUser` |
| 处理还款结果 | #13 autoProcess | `handleRepayResult` |
| APV mock | #4 apvMock | — |

## 完整索引

| # | 工具 | URL |
|---|------|-----|
| 1 | getUserInfo | `/innovateTools/getUserInfo/` |
| 2 | getRandomUserInfo | `/innovateTools/getRandomUserInfo/` |
| 4 | apvMock | `/innovateTools/apvMock/` |
| 5 | creditRetry | `/innovateTools/creditRetry/` |
| 6 | getLoanInfo | `/innovateTools/getLoanInfo/` |
| 7 | updateThirdInfo | `/innovateTools/updateThirdInfo/` |
| 8 | updateFace | `/innovateTools/updateFace/` |
| 9 | deletePpdInfo | `/innovateTools/deletePpdInfo/` |
| 10 | LoanRepaymentPlan | `/innovateTools/LoanRepaymentPlan/` |
| 11 | aiRepayHandle | `/innovateTools/aiRepayHandle/` |
| 12 | ApsRepaymentBatch | `/innovateTools/ApsRepaymentBatchApi/` |
| 13 | autoProcess | `/innovateTools/autoProcess/` |
| 14 | executeTasks | `/innovateTools/executeTasks/` |
| 15 | apsDubboEscape | `/innovateTools/apsDubboEscapeApi/` |
| 16 | ApsOrderQueryDb | `/innovateTools/ApsOrderQueryDbApi/` |
| 17 | APSDBOperations | `/innovateTools/APSDBOperationsApi/` |
| 18 | apsDubboLogParser | `/innovateTools/apsDubboLogParserApi/` |
| 19 | apsLogQueryTool | `/innovateTools/apsLogQueryTool/` |
| 20 | financeTools | `/finance/financeTools/` |
| 21 | genBankCard | `/finance/genBankCard` |
| 22 | clioTools | `/finance/clioTools/` |
