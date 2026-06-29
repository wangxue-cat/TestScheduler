---
name: check-handover
description: 检查需求是否已提测（开发→测试交接状态），返回提测状态和阻塞项
argument-hint: "<requirement_id>"
---

# check-handover

检查需求是否已从开发移交到测试阶段。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号 |

## 执行逻辑

### Step 1: 查询提测状态
调用 `testmind:request-manage` 查询需求的提测状态：
- 开发中 → 未提测
- 已提测 → 可开始测试
- 测试中 → 已在测试
- 已完成 → 测试通过

### Step 2: 检查阻塞项
- 关联 Bug 是否有阻塞级别的缺陷
- 部署环境是否就绪
- 依赖接口是否可用

### Step 3: 输出提测报告

## 输出

```json
{
  "requirement_id": "NREQUEST-48504",
  "status": "已提测",
  "can_test": true,
  "blockers": [],
  "handover_time": "2026-06-10T14:00:00",
  "notes": "开发已部署到STG1，可以开始测试"
}
```

## 规则

1. 单纯状态查询，不修改任何数据
2. 状态为"开发中"时，can_test=false，并给出预计提测时间
