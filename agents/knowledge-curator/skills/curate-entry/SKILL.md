---
name: curate-entry
description: CRUD 知识条目：创建/更新/删除 MEMORY.md 索引 + 内容文件 + CHANGELOG 记录
argument-hint: "<entry_data> <operation>"
---

# curate-entry

知识条目的标准入库操作：创建 → 写内容文件 → 更新 MEMORY.md 索引 → 记录 CHANGELOG。

## 硬性约束

1. 🟡 create/delete 必须 Human Confirm
2. **事务性**：内容文件 + MEMORY.md + CHANGELOG 三者同步

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| entry_data | object | 是 | `{ name, description, type, content }` |
| operation | string | 是 | create / update / delete |

## 执行操作

- **create** — 去重 → 写 `memory/knowledge/{type}/{name}.md` → 更新 MEMORY.md Knowledge 分区 → 记录 CHANGELOG
- **update** — 定位文件 → 合并 content → 更新 MEMORY.md → 记录 CHANGELOG
- **delete** — Human Confirm → 移除索引 → 删除/归档文件 → 记录 CHANGELOG

## 输出

```json
{ "operation": "create", "name": "...", "status": "success", "files_updated": ["..."] }
```

## 关键规则

1. name 使用 kebab-case，全小写英文
2. 创建前必须检索去重（`testmind:knowledge-retrieve` + 本地 `memory/knowledge/`）

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
