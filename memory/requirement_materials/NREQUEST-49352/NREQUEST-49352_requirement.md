# NREQUEST-49352 需求文档

## 需求基本信息

| 字段 | 值 |
|------|-----|
| 需求编号 | NREQUEST-49352 |
| 需求标题 | API流量IT巡检202606 |
| 迭代版本 | 20260702 |
| 环境 | STG1 |
| 关联Story | JYSG-149999 |

## 需求状态

> 未能通过 testmind:request-manage 获取状态信息（Bash 不可用），需用户手动确认。

## 需求内容

1. aps系统部署耗时过长，减少非必要资源在部署时加载(可以懒加载) @张传球

2. 日常巡视问题优化：
   - 2.1 OCR识别失败，记录具体失败原因，而不是统一的一个大类。对于虚拟号段，半流程拉取协议时直接拒绝，当前会出现NP异常。 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=86533902) V4授信上送过程中，身份证OCR识别错误，但是返回的是身份证过期 @胡志强
   - 2.2 没有代偿凭证、放款凭证，合作方只上传yyyymmdd.ok文件，没有yyyymmdd目录，对业务没有影响，有错误日志 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=89748157) @胡志强
   - 2.3 ERR 微众银行订单状态推送处理 处理前借据状态是终态无需通知 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=91146900) @黄叶鑫
   - 2.4 通知imgp异常，bizNo为空导致通知失败 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779) @黄叶鑫
   - 2.5 快手渠道拉取还款结果时候，order_repay不存在 & order_repay_err_request_log存在 返回BUSINESS_FAIL对方无法处理，初步确认需返回RECORD_NOT_EXISTS [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779) @黄叶鑫
   - 2.6 third_repay_withhold 表存在两条相同数据，业务场景应该只有一条 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779) @黄叶鑫
   - 2.7 头条调额账单记录，会出现同一条流水多笔订单的场景 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634) @张传球
   - 2.8 如果D日无合同文件，只有.ok文件，不会更新当日合同下载状态，会触发告警【【事件处理】【协议文件】【华兴银行】合作方协议文件未成功下载】 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634) @雷跃屏
   - 2.9 半流程拉取协议空指针异常 [Confluence](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634) @胡志强

3. 历史遗留债务，线程池配置隔离 @黄叶鑫

## 关联Confluence文档

| 序号 | 链接 | 负责人 |
|------|------|--------|
| 2.1 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=86533902 | 胡志强 |
| 2.2 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=89748157 | 胡志强 |
| 2.3 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=91146900 | 黄叶鑫 |
| 2.4 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779 | 黄叶鑫 |
| 2.5 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779 | 黄叶鑫 |
| 2.6 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779 | 黄叶鑫 |
| 2.7 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634 | 张传球 |
| 2.8 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634 | 雷跃屏 |
| 2.9 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634 | 胡志强 |

## 涉及人员

| 姓名 | 涉及条目 |
|------|---------|
| 张传球 | 条目1 (APS部署优化)、条目2.7 (头条调额) |
| 胡志强 | 条目2.1 (OCR识别)、条目2.2 (代偿凭证)、条目2.9 (空指针) |
| 黄叶鑫 | 条目2.3 (微众银行)、条目2.4 (imgp通知)、条目2.5 (快手还款)、条目2.6 (third_repay_withhold)、条目3 (线程池) |
| 雷跃屏 | 条目2.8 (合同下载) |

## 涉及系统

- APS系统 (条目1：部署耗时优化)
- API网关/流量系统 (条目2：日常巡视问题)
- 线程池 (条目3：配置隔离)
