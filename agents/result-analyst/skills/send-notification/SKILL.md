---
name: send-notification
description: 发送Teams/邮件通知测试结果摘要
argument-hint: "<report_summary> [recipients]"
---

# send-notification

测试完成后发送 Teams 消息和/或邮件通知相关人员。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_summary | object | 是 | generate-report 的摘要输出 |
| recipients | string | 否 | 收件人（默认从需求信息中获取开发和测试负责人） |
| channels | string[] | 否 | 通知渠道，默认 ["teams"]，可选 ["teams", "email"] |

## 执行逻辑

### Step 1: 构建消息内容
```
📊 测试报告 — {requirement_id} {需求标题}
━━━━━━━━━━━━━━━━━━━━━━━━
环境: STG1
总数: {total} | 通过: {passed} ✅ | 失败: {failed} ❌ | 通过率: {pass_rate}
失败用例: {failed_case_names}
报告链接: {report_path}
━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 2: Human Confirm
展示消息预览，询问用户确认发送。

### Step 3: 发送通知
- Teams: 调用 `testmind:teams-message`
- 邮件: 调用 `testmind:email-send`

## 输出

```json
{
  "teams": { "status": "sent", "channel": "测试通知群" },
  "email": { "status": "skipped" }
}
```

## 规则

1. 🟡 中风险操作，必须 Human Confirm
2. 失败时告知用户，不支持自动重试
3. 默认只发 Teams，邮件按需
