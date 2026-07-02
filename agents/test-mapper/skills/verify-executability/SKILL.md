---
name: verify-executability
description: "可执行性检查：用例生成后在接口匹配前，逐条检查每个步骤和验证点是否可执行，产出 pass/warn/block 检查报告"
argument-hint: "[需求编号] [渠道] [环境]"
---

# verify-executability — 可执行性检查

在测试用例生成后、接口匹配前，逐条检查每个用例的每个步骤和验证点是否可执行。产出 pass/warn/block 报告。

## 硬性约束

1. **渠道映射禁止猜测**：必须从 `memory/api_channels_rules/partner_code_mapping.json` 查找，不可自行编造 partner_code
2. **DB 库名禁止猜测**：必须从 `memory/db_info_processed.json` 校验库名在目标环境是否存在
3. **block 必须暂停**：有 block 项时 `can_proceed=false`，必须用户确认后才能进入 match-platform-interface
4. **不修改输入**：只产出检查报告，不修改用例 Excel 或 parsed_cases

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `parsed_cases` | object | 是 | `parse-case-steps` 的输出 |
| `excel_path` | string | 是 | 用例 Excel 路径，降级读取原始内容 |
| `requirement_id` | string | 是 | 需求编号 |
| `channel` | string | 是 | 用户指定的渠道中文名（如"头条智选"） |
| `env` | string | 否 | 目标环境 STG1/STG2/STG3，默认 STG1 |

## 执行流程

```
输入 → Step1 加载资源 → Step2 逐用例检查 → Step3 汇总判定 → Step4 生成报告
```

### Step 1：加载检查资源

1. 读 `memory/api_channels_rules/partner_code_mapping.json` → 渠道映射表
2. 读 `memory/db_info_processed.json` → 数据库路由表
3. 读 `memory/api_channels_rules/common_rules.md` → 通用规则
4. 读渠道专用规则（如果存在）：`memory/api_channels_rules/{partner_code}.md`
5. 可选：调用 `testmind:auto-interface-list` 按 channel 搜索接口列表

### Step 2：逐用例逐步骤检查

对 `parsed_cases.cases[]` 中每个 case 的每个 step，运行 10 维度检查器：

| # | 维度 | 触发条件 | 依据 |
|---|------|---------|------|
| 1 | 定时任务 | 步骤提到定时任务/调度/扫描 | testmind:lingxi-scheduler |
| 2 | DB 落库 | step.type=="db" 或预期含 DB 操作 | db_info_processed.json |
| 3 | 接口预检 | step.type=="interface"/"flow" | auto-interface-list |
| 4 | 渠道映射 | 含中文渠道名 | partner_code_mapping.json |
| 5 | Apollo 配置 | step.type=="config" 或含 Apollo 操作 | testmind:apollo-config |
| 6 | 日志验证 | 预期含日志/关键字 | 步骤文本解析 |
| 7 | 参数完整性 | 有外部参数占位符 | common_rules.md + 渠道规则 |
| 8 | 前置可满足性 | precondition[] 非空 | 步骤文本解析 |
| 9 | MQ 验证 | 预期含 MQ/topic/eventTag | 步骤文本解析 |
| 10 | 环境一致性 | 引用库/表/配置 | db_info_processed.json |

每个维度的详细规则见 `refs/rules.md`。

### Step 3：汇总判定

```
步骤级：任一维度 block → step verdict = block
用例级：任一步骤 block → case verdict = block
全局级：任一用例 block → can_proceed = false
```

### Step 4：生成报告

1. 生成 JSON：`memory/execution_plans/{requirement_id}_executability_check.json`
2. 渲染 Markdown：使用 `templates/report.md` 模板 → `memory/execution_plans/{requirement_id}_executability_report.md`
3. 返回 `can_proceed` + `blockers` 列表

## 输出

参见 `refs/io.md` 的完整 schema。

- `memory/execution_plans/{req_id}_executability_check.json`
- `memory/execution_plans/{req_id}_executability_report.md`

## 关键规则

1. **Block 必须解决**：block 项有修复建议，用户解决后重新运行此 skill
2. **Warn 不阻塞**：warn 仅提醒，不阻止进入 match-platform-interface
3. **Auto-fix**：渠道映射精确匹配结果自动记录，提示用户可自动应用
4. **环境感知**：DB 存在性检查按目标 env 过滤 `db_info_processed.json`
5. **接口预检非最终**：维度 3 仅是预检，正式匹配是 match-platform-interface 的职责，因此永不 block

> 📁 详细规则 → [refs/rules.md](refs/rules.md)
> 📁 输入输出 schema → [refs/io.md](refs/io.md)
> 📁 报告模板 → [templates/report.md](templates/report.md)
