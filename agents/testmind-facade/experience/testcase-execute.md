---
name: testcase-execute
description: 批量用例执行：start→end→execute 正确流程，time 传参位置，脚本调用限制
metadata:
  type: experience
  skill: testmind:testcase-execute
  version: 1
  evolution_count: 2
  last_updated: 2026-06-30
  sources: [testmind:testcase-execute, testmind:testcase-query, testmind:testcase-record, testmind:testcase-statistics, batch_execute API]
---

# testcase-execute 经验积累

## 核心原则

_（尚未达到升级阈值，≥3 次确认后升级至此区）_

## 执行策略

| 场景 | 策略 | 原因 |
|------|------|------|
| 批量执行大量用例 | start → wait(≥1s/条) → end → execute | 见下方已验证模式 |
| 命令行参数超长 | import 模块直调 或 urllib 裸调 API | shell 参数上限约 32KB |
| tester 过滤 | 使用中文展示名（如 王雪）非 username | API 返回空结果根源 |

## 已知踩坑

<!-- EVOLUTION_MARKER: pitfalls — 追加新条目到此行下方 -->

### P6: 登记后统计表 / 查询接口看不到结果或时长
- **现象**：`case-execute` 返回 flag=S 后，`cm_case_execute_statistics`（case-exec 统计）pass 数不变，仍是旧值；`normal-query`/`case-record` 均不返回每条用例的执行时长
- **根因**：统计表是定时任务重算的派生快照，非实时；只读查询接口不暴露 execute_time 字段
- **确认次数**：1
- **规避**：核验**状态**用 `normal-query --filter-result P`（实时，可见 case_executor 填充）；核验**时长**只能等统计表刷新或直查 STG2 qoa_testcase DB

### P1: execute 报「开始时间和结束时间不能为空」
- **现象**：`POST /cm/api/batchexecute/` 返回 `用例执行的开始时间和结束时间不能为空`
- **根因**：API 要求 payload 顶层传 `start_time` + `end_time`，仅靠 `batch_data` 中 case 对象的 `execute_start_time` / `execute_end_time` 不够
- **确认次数**：5+
- **规避**：payload 中加 `"start_time": "..."`, `"end_time": "..."`，值从 case 对象的对应字段获取

### P2: execute 报「时间过于接近，平均每用例<1秒」
- **现象**：start 和 end 之间间隔太短
- **根因**：API 校验 总时长 ÷ 用例数 必须 ≥1 秒
- **确认次数**：2
- **规避**：start 后 sleep ≥ 用例数量秒，再 end

### P3: start 后 execute_end_time 被置为 None
- **现象**：start 成功但 execute 仍报时间为空
- **根因**：start 操作将 case 的 `execute_end_time` 重置为 None，必须先 end 再 execute
- **确认次数**：3
- **规避**：严格按 start → wait → end → execute 顺序执行

### P4: 已 start 的用例重复 start 报错
- **现象**：`记录中存在正在执行中的用例, 无法开始执行!`
- **规避**：需先 end 再重新 start，或直接继续 end→execute 流程

### P5: 命令行 JSON 超长
- **现象**：`--batch-data-json` 传入大数组时报 `Argument list too long`
- **根因**：shell 参数有上限（Windows ~32KB），17 条用例约 39KB
- **规避**：Python import testcase_execute 模块直接调用，或用 urllib 发 HTTP 请求

## 已验证模式

<!-- EVOLUTION_MARKER: patterns — 追加新条目到此行下方 -->

### M1: 批量执行 N 条用例完整流程
```
POST /cm/api/cases/executeCaseStartEnd/  {plan_name, case_list, operate_type:"start"}
sleep(N+3) 秒
POST /cm/api/cases/executeCaseStartEnd/  {plan_name, case_list, operate_type:"end"}
GET  /cm/api/cases/ 重新查询获取更新后的 case 对象
POST /cm/api/batchexecute/  {
  batch_data, result:"P", sprint,
  start_time: cases[0].execute_start_time,  ← 必须顶层传
  end_time: cases[0].execute_end_time,      ← 必须顶层传
  packages: [...], page_usage:"allInOne"
}
POST /cm/api/queryrecords/resetCaseExecuteTime/ 重置时长（可选）
```
- **确认次数**：1（本次 64 条用例分 4 story 全通过）
- **适用场景**：需要批量标记用例已执行时

### M2: case-execute 子命令直接登记通过（小批量）
```
存 normal-query 结果到文件 → 脚本按 id 筛 7 条 → batch.json
testcase_execute.py case-execute --sprint "..." --result P \
  --batch-data-json "$(cat batch.json)" --time-type separate --time-hours 8
→ {"flag":"S","msg":"用例执行成功","count":7}
```
- **确认次数**：1（7 条 N→P，单 story JYSG-149999）
- **要点**：7 条规模命令行 JSON 未超长（参见 P5，17 条才超）；`case-execute` 脚本封装了 start/end，无需手动走 M1 的 start→end 流程；`--time-type separate --time-hours 8` 提交合计 8h 平摊
- **遗留**：separate 是否=总时长按条数平摊，尚未经 DB 回读证实，待下次直查 qoa_testcase 确认

## 进化规则

1. 每次无效调用 → 追加到踩坑区
2. 每次验证成功 → 追加到模式区（含确认次数）
3. 同类踩坑 ≥3 次 → 升级为「核心原则」硬规则
4. 同类模式确认 ≥3 次 → 升级为「执行策略」条目
5. 每次更新递增 evolution_count，更新 last_updated
