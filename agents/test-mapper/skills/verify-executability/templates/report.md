# {req_id} 可执行性检查报告

> 需求: {requirement_id} | 渠道: {channel} | 目标环境: {env} | 检查时间: {checked_at}

---

## 一、检查摘要

| 指标 | 数值 |
|------|------|
| 总检查项 | {total_checks} |
| ✅ 通过 | {pass_count} |
| ⚠️ 警告 | {warn_count} |
| 🚫 阻塞 | {block_count} |
| 是否可继续 | {can_proceed} |

---

## 二、🚫 阻塞项（必须解决）

{blockers_section}

| # | 用例 | 步骤 | 维度 | 问题 | 修复建议 |
|---|------|------|------|------|----------|
{blocker_rows}

> 以上问题不解决将导致对应步骤无法执行。

---

## 三、逐用例检查详情

{case_details}

### Case #{case_index}: {case_name}
优先级: {priority} | 步骤数: {step_count} | 综合: {case_verdict}

| 步骤 | 类型 | 维度 | 结果 | 详情 |
|------|------|------|------|------|
{step_check_rows}

---

## 四、⚠️ 警告项（建议处理）

{warnings_section}

| # | 用例 | 步骤 | 维度 | 问题 | 建议 |
|---|------|------|------|------|------|
{warning_rows}

---

## 五、🔧 自动修复建议

{auto_fix_section}

以下问题可以自动修复，是否需要自动应用？
{auto_fix_list}

---

## 六、下一步

{next_steps}
