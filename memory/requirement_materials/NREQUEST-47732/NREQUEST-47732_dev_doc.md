# 开发文档 - NREQUEST-47732

## Confluence 设计文档

**状态：待补充**

Story JYSG-148218 在 QOA 中 `has_confluence` 为 `false`，未关联 Confluence 设计文档。

## 关键设计信息（来自需求分析）

| 字段 | 值 |
|------|-----|
| 涉及应用 | aps-app |
| 涉及环节 | 动支前查询、动支试算、动支申请等所有借款环节 |
| 处理逻辑 | 对静默 360API 失败的 JIEITAO 用户，APS 做交易拒绝 |
| 拒绝原因 | "用户状态异常，静默 360API 失败" |
| 开发人员 | huzhiqiang-jk |
| 实现方式 | codeAndConfig（来自关联 API-10377） |

## 待补充项

- [ ] Confluence 设计文档链接
- [ ] 具体接口列表及改动点
- [ ] 数据库表变更（如有）
- [ ] 配置项变更（如有）
