# summarize-execution 输入/输出定义

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号 |

## 执行步骤展开

### Step 1: 收集全流程产物

- 需求材料: `memory/requirement_materials/{req_id}/`
- 测试用例: `memory/testcases/{req_id}_testcases.xlsx`
- 执行计划: `memory/execution_plans/{req_id}_plan.json`
- 执行结果: `memory/test_results/cache/{req_id}_execution_results.json`
- 测试报告: `memory/test_results/reports/{req_id}_execution_report.md`

### Step 2: 提取知识维度

见 [refs/rules.md](rules.md) 维度表。

### Step 3: 去重检查

`testmind:knowledge-retrieve` + 本地 `memory/knowledge/` 对比。

### Step 4: 提取 Skill 改进建议

对比实际执行过程与相关 Skill 的定义，发现遗漏/过时/错误。

补丁格式：
```json
{
  "target_skill": "agents/test-runner/skills/execute-plan/SKILL.md",
  "confidence": "high",
  "title": "OB表验证前增加等待步骤",
  "problem": "OB写入为afterCommit异步，当前Skill未定义等待",
  "suggested_change": "在OB表落库校验步骤前追加：wait_seconds: 5",
  "related_entry": "ob-async-write-lag"
}
```

### Step 5: 生成知识条目草稿

知识条目按 `memory/knowledge/{type}/{name}.md` 路径生成，type 取值：pitfalls / references / patterns / interfaces。

## 输出 JSON Schema

```json
{
  "requirement_id": "NREQUEST-49267",
  "entries": [
    { "type": "踩坑记录", "title": "OB异步写入1秒延迟", "content": "...", "is_new": true }
  ],
  "total_entries": 5,
  "new_entries": 5,
  "existing_entries": 0,
  "skill_patches": [
    {
      "target_skill": "agents/test-runner/skills/execute-plan/SKILL.md",
      "confidence": "high",
      "title": "...",
      "problem": "...",
      "suggested_change": "...",
      "related_entry": "ob-async-write-lag"
    }
  ]
}
```
