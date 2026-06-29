---
name: fetch-requirement
description: 根据需求ID从Lingxi/QOA拉取需求详情，返回结构化JSON
argument-hint: "<requirement_id>"
---

# fetch-requirement

根据需求 ID（NREQUEST-xxxxx 或 JYSG-xxxxx）从 Lingxi/QOA 系统拉取需求详情。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号，如 NREQUEST-48504 |

## 执行逻辑

### Step 1: 解析需求 ID
- 支持格式：`NREQUEST-xxxxx`、`JYSG-xxxxx`、Lingxi URL（从中提取 ID）
- 若 ID 格式不合法，返回错误提示

### Step 2: 查询需求基本信息
调用 `testmind:request-manage` 查询：
- 需求标题、描述、验收标准
- 当前状态（新建/开发中/已提测/已完成）
- 关联迭代版本
- 开发负责人、测试负责人

### Step 3: 查询关联 Story
调用 `testmind:story-manage query` 查询需求关联的 Story 列表：
- Story ID、标题、状态
- 技术领域、模块

### Step 4: 查询关联 Bug（可选）
若需求已有关联 Bug，一并拉取：
- Bug ID、标题、严重程度、状态

### Step 5: 获取需求文档正文
调用 `testmind:get-request-content` 获取需求描述正文（富文本/Markdown）

## 输出

```json
{
  "requirement_id": "NREQUEST-48504",
  "title": "需求标题",
  "description": "需求描述正文",
  "acceptance_criteria": "验收标准",
  "status": "已提测",
  "iteration": "20260611 迭代版本",
  "developer": "开发者",
  "tester": "测试者",
  "stories": [
    { "story_id": "JYSG-xxxxx", "title": "...", "status": "...", "module": "..." }
  ],
  "bugs": [
    { "bug_id": "JYSG-xxxxx", "title": "...", "severity": "...", "status": "..." }
  ],
  "raw_content": "需求文档原始内容"
}
```

## 规则

1. 需求不存在时直接告知用户，不编造
2. 关联 Story/Bug 为空时返回空数组，不报错
3. 优先使用 `testmind:request-manage`，失败时尝试 WebFetch 访问 Lingxi URL
