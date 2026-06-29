---
name: collect-materials
description: 收集需求相关的全部材料（需求文档+开发文档+测试说明+代码仓库），统一存入结构化目录
argument-hint: "<requirement_id>"
---

# collect-materials

收集需求文档、开发文档、测试说明、代码仓库等全部材料，统一存入 `memory/requirement_materials/{req_id}/` 目录。

## 硬性约束

1. **需求文档 + 测试说明两者均缺失时，必须暂停提示用户确认**，不可静默跳过

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号 |
| requirement_json | object | 否 | fetch-requirement 的产出，未提供则自动调用 |

## 执行步骤

1. **确保需求 JSON** — 未传入则调用 fetch-requirement
2. **创建目录** → `memory/requirement_materials/{req_id}/`
3. **保存需求文档** → `{req_id}_requirement.md`
4. **获取开发文档** → confluence + story-manage
5. **获取测试说明** → `{req_id}_tester_notes.md`
6. **获取代码仓库** → `{req_id}_code_repo.md`
7. **完整性校验** — 关键材料缺失时暂停确认

## 输出

```
memory/requirement_materials/{req_id}/
  ├── {req_id}_requirement.md
  ├── {req_id}_dev_doc.md
  ├── {req_id}_tester_notes.md
  └── {req_id}_code_repo.md
```

## 关键规则

1. 开发文档、代码仓库缺失不阻塞流程
2. 已有材料目录时询问是否覆盖
3. 所有文件 UTF-8 编码

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
