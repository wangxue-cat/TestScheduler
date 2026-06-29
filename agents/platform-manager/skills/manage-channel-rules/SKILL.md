---
name: manage-channel-rules
description: 维护渠道调用规则（默认参数、生成规则、特殊逻辑、参数约束）
argument-hint: "<channel> [rule_content]"
---

# manage-channel-rules

维护渠道的调用规则文档。规则决定参数组装时的默认值、生成策略和特殊逻辑。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| channel | string | 是 | 渠道标识 |
| operation | string | 是 | query / update / append |
| rule_section | string | 否 | 规则章节名，如 "account_id获取规则" |
| rule_content | string | 否 | 规则内容 |

## 执行逻辑

### query — 查询规则
读取 `memory/api_channels_rules/{channel}.md`，返回当前规则内容。

### update — 更新规则章节
1. 定位 `rule_section` 对应的章节
2. 替换章节内容
3. 在文件顶部注释记录变更时间和原因

### append — 追加规则
1. 在规则文件末尾追加新章节
2. 记录变更日志

## 输出

```json
{
  "channel": "TouTiao",
  "operation": "update",
  "section": "account_id获取规则",
  "file_updated": "memory/api_channels_rules/TouTiao.md"
}
```

## 规则

1. 每次变更必须在文件顶部注释记录：`<!-- 2026-06-11 wangxue-jk: 更新xxx规则，原因：... -->`
2. 规则文件为 Markdown 格式，用 ## 标题分隔章节
3. 涉及 SQL 查询的规则，写清楚表名和查询条件
