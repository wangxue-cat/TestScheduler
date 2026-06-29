# curate-entry 详细规则

## 1. create 完整流程

1. **去重检查**: 调用 `testmind:knowledge-retrieve` + 对比本地 `memory/knowledge/` 目录
2. **展示条目预览** → 等待用户确认
3. **写内容文件**: `memory/knowledge/{type}/{name}.md`

   type 取值：`pitfalls` | `references` | `patterns` | `interfaces`

   ```markdown
   ---
   name: {name}
   description: {description}
   metadata:
     type: {type}
   ---
   {content}
   ```

4. **更新 MEMORY.md**: 在 `## Knowledge` > 对应 type 分区下追加
   ```
   - [{Title}](knowledge/{type}/{name}.md) — {description}
   ```
5. **记录 CHANGELOG**: 追加 `- YYYY-MM-DD: 新增条目 {name}`

## 2. update 完整流程

1. 定位 `memory/knowledge/{type}/{name}.md`
2. 合并更新 content
3. 更新 MEMORY.md 中的描述（如变更）
4. 记录 CHANGELOG

## 3. delete 完整流程

1. 定位条目 → Human Confirm
2. 从 MEMORY.md 中移除索引行
3. 删除或归档内容文件
4. 记录 CHANGELOG

## 4. 命名规范

name 使用 kebab-case，全小写英文，如 `ob-async-write-lag`。

## 5. 事务性要求

内容文件 + MEMORY.md + CHANGELOG 三者必须同步更新。任一失败则回滚。

## 6. entry_data 结构

```json
{
  "name": "kebab-case-slug",
  "description": "one-line summary",
  "type": "pitfalls | references | patterns | interfaces",
  "content": "Markdown 正文内容"
}
```
