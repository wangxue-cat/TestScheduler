# NREQUEST-47459 测试说明

更新时间: 2026-06-16 16:48:20

## 补充说明

- 渠道: 蚂蚁贷超
- 需求: 贷中清退，由风险发起用户清退通知 APS，APS 通过蚂蚁授信信息变更申请通知蚂蚁，蚂蚁再通过授信信息变更结果通知回传最终结果。
- 清退类型: 风险清退，接口文档枚举为 `RISK_CLEAR`。
- 清退前置限制: 蚂蚁侧反馈无额外前置限制；月限量约 2000，超限需线下评估并由蚂蚁打开限量后再走线上清退。
- 对账文件口径: 清退用户 `acct_status=正常`，`credit_status=失效`，授信额度不变。
- 贷中拦截口径: 清退成功后，蚂蚁侧确保不再将该用户发起奇富借款；授信拒绝 180 天后重新分发场景需单独评估。

## 接口信息

| 场景 | 接口章节 | 接口名称 | 方向 | 关键字段/口径 |
|---|---|---|---|---|
| 清退申请 | 5.1.4 | `ant.loanmarket.credit.loan.institution.info.change.apply` | 机构 -> 平台 | `changeReqNo`、`creditProdCode`、清退类型 `RISK_CLEAR`，授信状态正常 -> 失效，额度不变 |
| 清退结果通知 | 5.1.5 | `ant.loanmarket.credit.loan.institution.info.change.result` | 平台 -> 机构 | `applyNo`、`changeReqNo`、`changeResult=Y/N`、`changeResultReasonCode`、`changeResultReasonMsg` |

## 用例清单

| 序号 | 用例名称 | 优先级 | 回归 | 核心验证点 |
|---|---|---|---|---|
| 1 | 蚂蚁贷超风险清退用户发起授信信息变更申请成功 | 高 | 是 | 5.1.4 返回 `resultInfo.resultCode=0000`，生成可关联的 `applyNo/changeReqNo` |
| 2 | 蚂蚁贷超清退结果通知成功后回传风险成功 | 高 | 是 | 5.1.5 `changeResult=Y` 后 APS 回传风险成功 |
| 3 | 蚂蚁贷超清退结果通知拒绝后回传风险失败原因 | 中 | 否 | 5.1.5 `changeResult=N` 时保存并回传拒绝原因 |
| 4 | 蚂蚁贷超重复清退结果通知保持幂等 | 中 | 否 | 相同 `applyNo/changeReqNo` 重复通知不产生冲突状态 |
| 5 | 蚂蚁贷超授信信息变更申请必填参数缺失返回参数错误 | 中 | 否 | 5.1.4 必填字段缺失返回 `resultInfo.resultCode=0011` |
| 6 | 蚂蚁贷超清退月限量超2000走线下评估后再清退 | 中 | 否 | 超限不直接线上清退，打开限量后再走 5.1.4 |
| 7 | 蚂蚁贷超清退用户日终授信对账文件字段正确 | 高 | 是 | 对账文件中 `acct_status=正常`、`credit_status=失效`、额度不变 |
| 8 | 蚂蚁贷超清退成功用户不再发起奇富借款 | 高 | 是 | 清退成功用户无新的奇富借款请求进入我方 |
| 9 | 蚂蚁贷超动用前查询清退用户额度状态为失效 | 中 | 否 | 动用前查询额度状态与对账文件 `credit_status=失效` 保持一致 |

## 产物

- Excel: `memory/testcases/NREQUEST-47459_testcases.xlsx`
- JSON: `memory/testcases/NREQUEST-47459_testcases.json`

## 更新记录

| 时间 | 更新人 | 内容 |
|---|---|---|
| 2026-06-16 16:48:20 | Codex | 创建测试说明模板，待根据生成用例同步补充 |
| 2026-06-16 16:55:32 | Codex | 基于需求材料和蚂蚁贷超接口文档生成 9 条测试用例，并同步渠道、接口、验证口径 |
