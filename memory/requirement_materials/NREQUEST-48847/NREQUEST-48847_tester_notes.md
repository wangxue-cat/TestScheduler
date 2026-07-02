# NREQUEST-48847 测试说明

## 基本信息

| 项目 | 内容 |
|------|------|
| 需求编号 | NREQUEST-48847 |
| 需求标题 | 202605 新携程API渠道新增促动调额调价 |
| 版本 | 20260709 迭代版本 |
| 状态 | 40开发中 |
| 测试负责人 | shenwenjie-jk |
| APS测试人员 | wangxue-jk |

## Story 分工

| Story | 标题 | 模块 | 测试人员 | 开发人员 |
|-------|------|------|---------|---------|
| JYSG-150408 | 流量运营 | aps-app | shenwenjie-jk | huangyexin-jk |
| JYSG-150409 | 风控 | cas-app/cas-batch-app/apv-app/eep-app/fep-online-app | lilili-jk | dengbin-jk |
| JYSG-150410 | 标签 | utas-sink-app | liyangyang2-jk | zhangzongyao-jk |

## 测试分工说明

1. **APS 模块（本用例聚焦）**：授信通过后促动支触发流程，包括配置开关检查、UTAS 标签查询、任务/补偿落库、定时扫描、借款痕迹拦截、MQ 发送
2. **调额动作成功/失败**：由 CAS/风控模块测试人员确认
3. **优惠券成功/失败**：由其他模块测试人员确认
4. **UTAS 标签数据准确性**：由标签模块测试人员确认

## 测试渠道

- **测试渠道**：头条智选（TouTiaoZhiXuan），非头条星选
- **接口变更**：本需求无接口层面改动，无需匹配接口文档，用例聚焦业务流程即可

## APS 测试关注点

1. 授信通过后是否正确触发促动支入口
2. 配置开关（aps_credit_pass_promotion_config）是否生效
3. UTAS 标签查询请求参数是否正确
4. 任务表（aps_credit_pass_promotion_task）落库验证
5. 补偿表（aps_credit_pass_promotion_compensation）落库验证
6. 定时任务 CreditPassPromotionTaskSendTask 扫描和 MQ 发送
7. 定时任务 CreditPassPromotionCompensationTask 补偿重试
8. MQ 消息格式验证

## 数据库表

| 表名 | 用途 |
|------|------|
| aps_credit_pass_promotion_config | 促动支渠道配置 |
| aps_credit_pass_promotion_task | 促动支任务表 |
| aps_credit_pass_promotion_compensation | 促动支补偿表 |
| order_iou | 借款痕迹表 |
| order_iou_err_request_log | 借款错误请求日志表 |

## 开发文档

- 文件：credit-pass-promotion-trigger-test-guide.html（授信通过后促动支触发测试说明）
- 位置：C:\Users\wangxue-jk\AppData\Roaming\360Teams\downloadFiles\

---

## 更新记录

| 日期 | 更新内容 | 更新人 |
|------|---------|--------|
| 2026-07-01 | 初始创建测试说明 | wangxue-jk |
| 2026-07-01 | 修正渠道为头条智选；明确无接口改动、无需匹配接口文档 | wangxue-jk |
