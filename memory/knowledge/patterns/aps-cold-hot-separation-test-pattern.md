---
name: aps-cold-hot-separation-test-pattern
description: APS冷热分离治理测试全模式：4种写入模式+2种读路由+OB穿透+监控告警，31字段全量比对
metadata:
  type: project
  tags: [APS, 冷热分离, 测试模式, OceanBase, Apollo]
  related_requirements: [NREQUEST-49267]
---

# APS冷热分离治理测试全模式

## 概述

APS 系统 `order_repay_withhold` 大表治理的完整测试模式，覆盖从写入路由到读取路由、Apollo 动态切换、监控告警的全场景。

## 架构要点

```
渠道接口 (XingXuanOrderFacade)
  → invokeFacade + orderRequestHandlerMap 分发
    ├── repayNotify (写入) → 根据 writeMode 路由到旧表/热表/OB
    └── pullRepayNotify (读取) → 根据 readNew 路由到热表/OB
```

## 涉及的数据库和表

| 数据库 | subsystem | 表 | 角色 |
|--------|-----------|-----|------|
| aps (MySQL) | aps-app | order_repay_withhold | 旧表，原表 |
| aps (MySQL) | aps-app | order_repay_withhold_hot | 热表，按月分区 |
| OB库 | apss-ob | order_repay_withhold_backup | OB冷备，全量 |

## Apollo 配置开关

| 开关 | 类型 | 作用 |
|------|------|------|
| `aps.apollo.config.repayWithholdWriteMode` | String | OLD_ONLY / TRIPLE / DUAL |
| `aps.apollo.function.switch.repayWithholdReadNew` | boolean | false=读旧表 / true=读热表 |
| `aps.apollo.function.switch.repayWithholdObWriteLog` | boolean | OB写入详细日志 |
| `aps.apollo.function.switch.repayWithholdObReadLog` | boolean | OB读取详细日志 |
| `aps.switch.control.monitorEnabled` | boolean | 历史数据监控 |
| `aps.switch.control.monitorDayDiff` | int | 监控天数阈值 |

## 测试用例分类

### 写入路由（4条）

| 用例 | writeMode | 旧表 | 热表 | OB表 |
|------|-----------|:--:|:--:|:--:|
| OLD_ONLY | OLD_ONLY | ✅ | ❌ | ❌ |
| TRIPLE三写 | TRIPLE | ✅ | ✅ | ✅ |
| DUAL双写 | DUAL | ❌ | ✅ | ✅ |
| 紧急回滚 | TRIPLE→OLD_ONLY | ✅ | ❌ | ❌ |

### 读取路由（3条）

| 用例 | readNew | 查表顺序 |
|------|---------|---------|
| 读旧表 | false | order_repay_withhold |
| 读热表 | true | order_repay_withhold_hot (命中) |
| OB穿透 | true | _hot (miss) → _backup (hit) |

### 监控告警（2条）

- monitorEnabled=false：即使超阈值也不告警
- monitorEnabled=true：超 monitorDayDiff 天数触发 ERR 告警 + 监控记录落库

## 落库校验方法

三表 31 字段全量对比：id, order_no, repay_tran_no, partner_code, loan_tran_no, repay_detail_id, user_no, cust_no, pay_type, repay_type, repay_terms, repay_amount, member_request_no, member_request_time, commit_pcs_count, member_no, withhold_state, channel_code, channel_member_no, channel_order_no, channel_label, withhold_amount, repay_time, return_time, result_code, result_msg, ext_info, date_created, created_by, date_updated, updated_by

## 执行注意事项

1. Apollo 修改后等待 2-5 秒 → [[apollo-timeout-but-effective]]
2. OB 异步写入等待 3-5 秒 → [[ob-async-write-lag]]
3. 读取路由必须查日志验证 → [[log-based-read-route-verification]]
4. 字段映射 repay_order_id=repay_tran_no → [[repay-order-id-field-mapping]]
5. 测试完成后恢复 writeMode=OLD_ONLY, readNew=false

## 来源

NREQUEST-49267 aps库大表order_repay_withhold冷热分离治理，2026-06-15 STG2，14条用例3轮执行11条通过
