# NREQUEST-49352 开发文档

## 概述

本需求为 API 流量 IT 巡检优化，涉及多个系统的日常巡视问题修复和 APS 部署优化。

## 开发负责人

> 未能通过 testmind:request-manage 获取开发负责人信息，需用户确认。

## 涉及系统与模块

### 1. APS 部署优化
- **负责人**: 张传球
- **内容**: aps系统部署耗时过长，减少非必要资源在部署时加载（可以懒加载）

### 2. 日常巡视问题优化

| 编号 | 问题描述 | 负责人 | Confluence |
|------|---------|--------|------------|
| 2.1 | OCR识别失败记录具体原因；虚拟号段半流程拉取协议直接拒绝（NP异常） | 胡志强 | [pageId=86533902](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=86533902) |
| 2.2 | 无代偿凭证/放款凭证，合作方只上传.ok文件，无目录，有错误日志 | 胡志强 | [pageId=89748157](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=89748157) |
| 2.3 | 微众银行订单状态推送处理前借据状态是终态无需通知 | 黄叶鑫 | [pageId=91146900](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=91146900) |
| 2.4 | 通知imgp异常，bizNo为空导致通知失败 | 黄叶鑫 | [pageId=92081779](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779) |
| 2.5 | 快手渠道拉取还款结果，order_repay不存在返回BUSINESS_FAIL，应返回RECORD_NOT_EXISTS | 黄叶鑫 | [pageId=92081779](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779) |
| 2.6 | third_repay_withhold表存在两条相同数据 | 黄叶鑫 | [pageId=92081779](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779) |
| 2.7 | 头条调额账单记录，同一条流水多笔订单 | 张传球 | [pageId=92096634](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634) |
| 2.8 | D日无合同文件只有.ok文件，不更新合同下载状态，触发告警 | 雷跃屏 | [pageId=92096634](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634) |
| 2.9 | 半流程拉取协议空指针异常 | 胡志强 | [pageId=92096634](https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634) |

### 3. 线程池配置隔离
- **负责人**: 黄叶鑫
- **内容**: 历史遗留债务，线程池配置隔离

## 关联 Confluence 文档

| pageId | 链接 |
|--------|------|
| 86533902 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=86533902 |
| 89748157 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=89748157 |
| 91146900 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=91146900 |
| 92081779 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92081779 |
| 92096634 | https://confluence.daikuan.qihoo.net/pages/viewpage.action?pageId=92096634 |

## 提测状态

> 未能通过 testmind:request-manage 获取提测状态（Bash 不可用），需用户确认。
