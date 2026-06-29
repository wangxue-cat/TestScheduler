---
name: summarize-execution
description: 从一次完整的测试执行中提炼可复用知识：新增接口经验、踩坑记录、参数模式、失败模式，并建议 Skill 改进
argument-hint: "<requirement_id>"
---

# summarize-execution

分析一次测试执行的完整产物（需求→用例→执行计划→结果→报告→Bug），提炼可复用知识条目和 Skill 补丁建议。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号 |

## 执行步骤

1. **收集全流程产物** — requirement_materials / testcases / execution_plans / test_results / reports
2. **提取知识维度** — 接口经验 / 踩坑记录 / 参数模式 / 失败模式
3. **去重检查** — `testmind:knowledge-retrieve` + 本地 `memory/knowledge/` 对比
4. **提取 Skill 改进建议** — 对比执行实际 vs Skill 定义，发现遗漏/过时/错误
5. **生成知识条目草稿** — 知识条目 + Skill 补丁

## 输出

```json
{
  "entries": [{ "type": "...", "title": "...", "is_new": true }],
  "skill_patches": [{ "target_skill": "...", "confidence": "high", "suggested_change": "..." }]
}
```

## 关键规则

1. 去重：已有类似条目只标记不重复创建
2. 知识条目需用户确认后入库
3. Skill 补丁为建议性质，需用户单独审批
4. 同 Skill 同类型补丁合并输出

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 输入/输出 Schema → [refs/io.md](refs/io.md)
