---
name: auto-discover
description: 扫描最近的执行日志和报告，自动发现值得沉淀的知识条目
---

# auto-discover

主动扫描 memory/ 目录下的执行报告和日志，自动识别值得沉淀的知识。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| days | number | 否 | 扫描最近 N 天，默认 7 |
| auto_confirm | boolean | 否 | 是否自动确认，默认 false |

## 执行逻辑

### Step 1: 扫描执行报告
- 遍历 `memory/test_results/reports/` 下最近 N 天的报告
- 提取失败模式（相同接口/相同错误码/相同根因）
- 统计高频失败（出现 ≥2 次的标记为 pattern）

### Step 2: 扫描执行计划
- 遍历 `memory/execution_plans/` 下的计划
- 发现新接口的使用模式

### Step 3: 扫描渠道变更
- 检查 `memory/api_channels/` 的修改时间
- 有新接口但无对应知识的标记

### Step 4: 生成建议清单
- 按优先级排序：高频失败 > 新接口 > 新规则 > 其他

## 输出

```json
{
  "scanned_at": "2026-06-11T19:00:00",
  "scan_range": "最近7天",
  "suggestions": [
    {
      "priority": "high",
      "type": "失败模式",
      "title": "TouTiao confirmDraw频繁失败：amount缺失",
      "evidence": "最近5次执行中3次失败，根因均为参数组装问题",
      "suggested_action": "沉淀为踩坑记录，更新渠道规则增加amount默认值"
    }
  ]
}
```

## 规则

1. 只建议，不自动入库（需用户确认）
2. 高频 = ≥2 次相同模式
3. 建议清单最多 10 条，超出按优先级截断
