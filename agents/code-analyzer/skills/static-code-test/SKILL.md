---
name: static-code-test
description: 结合需求+用例+代码diff 进行静态分析，发现硬编码、空安全、逻辑错误等黑盒测试看不到的问题
argument-hint: "<requirement_id> [code_diff_json] [testcase_path]"
---

# static-code-test

从黑盒测试的盲区角度审查代码变更：结合需求文档和已有测试用例，检测黑盒测试无法发现的内部逻辑缺陷、不可达代码、资源泄漏等问题。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | string | 是 | 需求编号 |
| code_diff_json | object | 否 | 已获取的 code diff |
| testcase_path | string | 否 | 测试用例 Excel 路径（默认 `memory/testcases/{req_id}_testcases.xlsx`） |
| requirement_materials_path | string | 否 | 需求材料目录路径 |

## 执行步骤

### Step 1: 确保输入就绪

1. 若未提供 `code_diff_json`，调用 `fetch-code-diff`
2. 尝试加载已有测试用例（从 `testcase_path` 或默认路径）
3. 加载需求材料（requirement.md + tester_notes.md）
4. **测试用例缺失时**：标注为"无测试用例基线，跳过覆盖对比"，继续执行代码模式扫描

### Step 2: 自动化静态检查

对每个变更文件，调用 `Skill(testmind-facade)` → `code-check` 进行自动化扫描：

- 硬编码值检测
- 空指针风险
- 资源未关闭
- 异常被吞没
- 线程安全隐患

### Step 3: 变更影响分析

调用 `Skill(testmind-facade)` → `analyze-code-change`，获取：
- 变更范围（方法级）
- 被调用方分析（哪些其他代码调用了变更方法）
- 依赖变更影响

### Step 4: 测试覆盖对比

将代码变更与已有测试用例进行覆盖对比：

1. 解析测试用例 Excel，提取测试步骤中涉及的接口/方法/场景
2. 对比变更方法/类：
   - **变更方法有覆盖用例** → 检查用例是否覆盖了新增的分支/条件
   - **变更方法无覆盖用例** → 「覆盖缺口」，标注严重度
   - **代码删除导致用例步骤过时** → 「用例过时」，建议清理
3. 新增的分支/条件判断 → 检查是否有测试用例覆盖两侧（true/false 都测到）

### Step 5: 规则驱动的模式扫描

按 [refs/rules.md](refs/rules.md) 中的规则逐项扫描：

1. **硬编码值检测** — 应配置化的常量
2. **空安全规则** — null 解引用风险
3. **边界条件规则** — 数值/集合/字符串边界
4. **逻辑错误模式** — 条件反转、死代码、switch fall-through
5. **资源管理规则** — 连接/流未关闭
6. **事务边界规则** — 事务范围、回滚完整性
7. **线程安全规则** — 共享可变状态
8. **覆盖缺口分析** — 用例覆盖不足

### Step 6: 生成报告

## 输出

输出文件：`memory/code_analysis/{req_id}/static_analysis_report.md`

```
# {req_id} 静态代码分析报告

> 需求: {title} | 分析时间: {date} | 仓库: {repo} | 测试用例: {path}

## 执行摘要

| 指标 | 数值 |
|------|------|
| 分析文件数 | N |
| 发现问题总数 | N |
| Blocker | N |
| Critical | N |
| Major | N |
| Minor | N |
| Suggestion | N |
| 覆盖缺口 | N |
| 过时用例 | N |

## Blocker — 必须修复

### B-001: {标题}

- **代码位置**: {file}:{line}
- **问题描述**: ...
- **为什么黑盒测试发现不了**: ...
- **建议修复**: ...
- **相关代码**:
  ```java
  // 问题代码片段
  ```

## Critical / Major / Minor（同上结构）

## 测试覆盖缺口

| 变更方法/类 | 覆盖用例 | 缺口描述 | 严重度 |
|------------|---------|---------|--------|
| Service.method() | 无 | 核心支付逻辑变更无用例覆盖 | Critical |
| Util.format() | TC-003 | 新增的 null 分支未覆盖 | Major |

## 过时用例

| 用例编号 | 步骤 | 过时原因 | 建议操作 |
|---------|------|---------|---------|
| TC-007 | Step 3 | 调用的 validateOld() 已被删除 | 删除此步骤或替换 |

## 按文件汇总

| 文件 | Blocker | Critical | Major | Minor | Suggestion |
|------|---------|----------|-------|-------|------------|
```

## 关键规则

1. **必须结合测试用例对比**：不能孤立分析代码，要有覆盖度视角
2. **解释黑盒盲区**：每个发现必须解释"为什么黑盒测试发现不了"
3. **严重度实事求是**：不为了显得有价值而夸大问题等级
4. **有代码位置引用**：每个发现必须有 `文件:方法:行号`
5. **建议修复可操作**：不只说"有问题"，还要说"怎么改"
6. **覆盖缺口 ≠ Bug**：缺口是风险提示，不是代码缺陷

## 辅助文件

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
