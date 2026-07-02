# verify-executability — 10 维度检查规则

## 概述

本文件定义了 `verify-executability` skill 的 10 个检查维度，每个维度说明触发条件、检查逻辑、检查依据和判定标准。

## 判定标准

| 结果 | 含义 | 行为 |
|------|------|------|
| `pass` | 步骤可执行，必要条件齐全 | 无操作 |
| `warn` | 可执行但模糊或有风险 | 提醒用户，不阻塞流程 |
| `block` | 步骤字面无法执行 | 暂停流程，用户必须解决 |

---

## 维度 1：定时任务检查 (scheduled_task)

### 触发条件
步骤 `raw_text` 匹配以下任意模式：
- 包含 `定时任务` / `调度` / `扫描` / `Task` / `lingxi`
- `step.type == "tool"` 且描述涉及任务触发
- 步骤中提到 `CreditPassPromotion` 等任务类名

### 检查逻辑
1. 从步骤文本中提取定时任务名称（如 `CreditPassPromotionTaskSendTask`、`CreditPassPromotionCompensationTask`）
2. 检查名称是否明确：
   - 只提到"触发定时任务"而未指定名称 → **warn**："定时任务名称不明确，请补充具体任务类名"
   - 名称明确（如含完整类名）→ 继续步骤 3
3. **实检（必须）**：通过 Skill 调用灵犀调度 API 查询该任务在目标环境是否存在：
   ```
   Skill(testmind:lingxi-scheduler, "get {env} {task_name}")
   ```
   - `result[]` 非空 → **pass**："任务 {task_name} 在 {env} 环境已配置"
   - `result[]` 为空 → **block**："任务 {task_name} 在 {env} 环境未配置，需先在灵犀调度平台创建"
4. **注意**：任务不存在不代表用例错误（可能是新功能尚未部署），block 级别的含义是"当前环境不具备执行条件"

### 检查依据
- 灵犀调度 API：通过 `Skill(testmind:lingxi-scheduler)` 查询
- Apollo 任务开关配置
- 开发文档中的定时任务章节

### 示例
| 查询结果 | 判定 | 说明 |
|---------|------|------|
| result 含任务配置 | pass | 任务已配置，可执行 |
| result 为空 | block | 任务未配置，需先创建 |

### 任务名提取规则
- 从步骤文本中匹配 `[A-Z][a-zA-Z]*Task` 模式
- 常见 Java 类名：`CreditPassPromotionTaskSendTask`、`CreditPassPromotionCompensationTask`
- **注意**：灵犀调度平台中任务名可能带前缀，如 Java 类 `CreditPassPromotionTaskSendTask` → 灵犀任务名 `APS_creditPassPromotionTaskSendTask`
- 查询时优先用 Java 类名搜索，若无结果再尝试添加 `APS_` 前缀

---

## 维度 2：DB 落库检查 (db_landing)

### 触发条件
- `step.type == "db"`
- 步骤/预期结果文本匹配 `查.*库|查.*表|落库|写入|SELECT|INSERT|UPDATE|DB`
- expected 类型为 `db` 或 `db_update`

### 检查逻辑
1. **库名检查**：从步骤文本中提取库名（如 `aps`、`aps_stg1`）
   - 无库名 → **block**："DB 步骤未指定库名，请补充如'查询 aps.aps_credit_pass_promotion_task'"
   - 有库名 → 查 `db_info_processed.json` 校验该库在目标 env 中是否存在
     - 存在 → 继续步骤 2
     - 不存在 → **block**："库 {db_name} 在 {env} 环境中不存在"
2. **表名检查**：从步骤文本中提取表名
   - 无表名 → **block**："DB 步骤未指定表名"
   - 有表名 → 继续步骤 3
3. **实检（必须）**：查询 `information_schema.TABLES` 确认表在目标库中存在：
   ```sql
   SELECT TABLE_NAME FROM information_schema.TABLES
   WHERE TABLE_SCHEMA='{db_name}' AND TABLE_NAME='{table_name}'
   ```
   - 表存在 → **pass**："表 {db_name}.{table_name} 在 {env} 环境存在"
   - 表不存在 → **block**："表 {db_name}.{table_name} 在 {env} 环境不存在，DDL 可能尚未部署"
4. **字段检查**：从预期结果中提取需比对的字段名
   - 无字段名 → **warn**："预期结果未指定需校验的字段，建议补充具体字段和期望值"
   - 有字段名 → pass
5. **期望值检查**：预期结果是否有明确的期望状态/值
   - 仅有"有数据"/"写入成功"等笼统描述 → **warn**："建议补充具体期望字段值，如'status=INIT'"
   - 有具体值 → pass

### 检查依据
- `d:\TestScheduler\memory\db_info_processed.json` 数据库路由表
- `information_schema.TABLES` 实时查询

### 示例
| 步骤文本 | 实检结果 | 判定 | 说明 |
|---------|---------|------|------|
| "查aps_credit_pass_promotion_task" | 表存在 | pass | 库名/表名明确且存在 |
| "查aps_credit_pass_promotion_task" | 表不存在 | block | 表未部署，无法执行 |
| "查数据库" | — | block | 缺少库名和表名 |
| "查aps.order_info" | 表存在 | warn | 有库和表但期望值笼统 |

### 表名提取规则
- 从步骤文本中匹配 `[a-z_]+` 模式（小写字母+下划线）
- 结合上下文（`FROM`/`WHERE`/`INSERT INTO`/`UPDATE`）定位表名
- 常见表名前缀：`aps_credit_pass_promotion_`、`order_iou`、`aps_`

---

## 维度 3：接口/流程匹配预检 (interface_precheck)

### 触发条件
- `step.type == "interface"` 或 `step.type == "flow"`
- 步骤文本匹配 `调用.*接口|发起.*申请|执行.*流程`

### 检查逻辑
1. **渠道预查**：调用 `testmind:auto-interface-list` 按 channel 搜索
   - 该渠道有已注册接口 → pass
   - 该渠道无任何接口 → **warn**："渠道 {channel} 在自动化平台无注册接口，match-platform-interface 阶段将无法匹配"
2. **步骤描述具体性**：
   - 步骤仅写"调用接口"未说明是什么接口 → **warn**："步骤描述过于笼统，建议补充接口用途（如授信/借款/还款）"
   - 步骤含接口用途关键词 → pass
3. **注意**：此维度永远不 block，正式接口匹配是 `match-platform-interface` 的职责

### 检查依据
- `testmind:auto-interface-list` 查询结果

### 示例
| 步骤文本 | 结果 | 说明 |
|---------|------|------|
| "通过头条智选授信接口发起授信申请" | pass | 渠道+接口用途明确 |
| "调用接口" | warn | 过于笼统 |

---

## 维度 4：渠道映射检查 (channel_mapping)

### 触发条件
步骤或前置条件文本中包含中文渠道名（如"头条智选"/"星选"/"携程"等）

### 检查逻辑
1. 从文本中提取中文渠道名
2. 查 `memory/api_channels_rules/partner_code_mapping.json` 进行模糊匹配
3. 匹配结果：
   - 精确匹配到 1 条 → pass，自动记录 `partner_code`
   - 模糊匹配到多条 → **warn**，列出候选让用户选择
   - 无匹配 → **block**："渠道'{channel_name}'在 partner_code_mapping 中未找到，请确认渠道名称或更新映射表"
4. **禁止猜测 partner_code**：不得自行编造编码

### 检查依据
- `memory/api_channels_rules/partner_code_mapping.json`

### 示例
| 文本 | 结果 | 说明 |
|------|------|------|
| "头条智选" | pass → TouTiao | 精确匹配 |
| "头条" | warn → TouTiao/XingXuan 候选 | 模糊匹配多条 |
| "某未知渠道" | block | 无匹配 |

---

## 维度 5：Apollo 配置检查 (apollo_config)

### 触发条件
- `step.type == "config"`
- 步骤/前置文本匹配 `Apollo|配置开关|修改配置|修改.*开关|forceStop|promotion_switch`

### 检查逻辑
1. 从文本中提取 Apollo 配置 key（格式 `namespace.key`）
   - 无法提取 → **block**："Apollo 配置步骤未指定配置 key，请补充如'aps.task.creditPassPromotionTaskSendTask.forceStop'"
   - 提取成功 → 记录
2. 检查是否指定了目标值
   - 无目标值 → **warn**："未指定配置目标值，请补充期望修改为的值"
   - 有目标值 → pass
3. 可选：调用 `testmind:apollo-config` 查询该 key 在目标环境的当前值
   - 键不存在 → **warn**："配置 key {key} 在 {env} 环境未找到，请确认 key 名称是否正确"

### 检查依据
- 开发文档中的 Apollo 配置章节
- `testmind:apollo-config` 查询结果

### 示例
| 文本 | 结果 | 说明 |
|------|------|------|
| "Apollo: aps.task.creditPassPromotionTaskSendTask.forceStop=false" | pass | key + 目标值明确 |
| "修改 Apollo 开关" | block | 无具体 key |
| "确认 Apollo aps.task.xxx.forceStop=false" | pass | key + 值明确 |

---

## 维度 6：日志验证检查 (log_verification)

### 触发条件
预期结果文本匹配 `日志|log|关键字|OUTREQ|OUTRESP|ERR|WARN`

### 检查逻辑
1. **关键字检查**：从预期中提取日志搜索关键字
   - 有关键字（如 `queryTagInUserChannelType`、`cas_all_event_topic`）→ pass
   - 无关键字 → **warn**："预期结果提到查日志但未指定搜索关键字，补充后执行时可精确定位"
2. **应用名检查**：从步骤/前置中提取应用名（如 `aps-app`、`gws-aps-web`）
   - 有应用名 → pass
   - 无应用名 → **warn**："未指定查哪个应用的日志，请补充应用名"
3. **日志类型**：区分实时日志 vs 定时日志
   - 如果涉及流水号查询，提示优先使用定时日志

### 示例
| 文本 | 结果 | 说明 |
|------|------|------|
| "查APS日志: OUTREQ cas_all_event_topic" | pass | 应用+关键字明确 |
| "查日志" | warn | 缺少关键字和应用名 |
| "日志确认发送成功" | warn | 无具体关键字 |

---

## 维度 7：参数完整性检查 (param_completeness)

### 触发条件
- 步骤文本包含 `${param}` 占位符
- 步骤引用了外部数据（如"使用上一步返回的 order_no"）
- 步骤需要输入参数但未说明来源

### 检查逻辑
对每个参数判断来源：
1. **用户提供** → pass
2. **渠道规则覆盖**（查 `api_channels_rules/{partner_code}.md`）→ pass
3. **随机生成**（查 `common_rules.md` 随机生成规则表）→ pass
4. **DB 查询获取**（从 io_bindings 上游步骤获取）→ pass
5. **无任何来源** → **block**："参数 {param} 来源不明，请指定参数值或数据来源"

### 检查依据
- `memory/api_channels_rules/common_rules.md`
- `memory/api_channels_rules/{partner_code}.md`

### 示例
| 参数 | 场景 | 结果 | 说明 |
|------|------|------|------|
| order_no | 用户已提供 | pass | 有明确来源 |
| account_id | 渠道规则: 授信后从DB三步查询 | pass | 来源明确 |
| 未知参数 | 无任何规则覆盖 | block | 来源不明 |

---

## 维度 8：前置条件可满足性 (precondition_satisfiability)

### 触发条件
case 的 `precondition[]` 非空

### 检查逻辑
1. **Apollo 前置**：包含配置 key → 走维度 5 检查
2. **数据前置**：如"需要已授信订单"、"需要订单号 XXX"
   - 数据来源明确（用户提供/前置步骤产出）→ pass
   - 数据来源不明确 → **warn**："前置条件'{desc}'的数据来源不明确，执行时可能无法准备"
3. **环境前置**：如"需要 STG1 环境"、"MQ 服务正常"
   - 环境可确认 → pass
   - 无法确认 → **warn**："无法确认'{desc}'在 {env} 环境是否满足"
4. **配置前置**：如"TouTiao 配置 promotion_switch=Y"
   - 该配置在当前用例中可设置（有对应的 config 步骤）→ pass
   - 该配置需手动提前设置 → **warn**："配置'{key}={value}'需在执行前手动设置"

### 示例
| 前置条件 | 结果 | 说明 |
|---------|------|------|
| "aps_credit_pass_promotion_config: partner_code=TouTiao, promotion_switch=Y" | pass | 步骤中可 INSERT 设置 |
| "需要 UTAS 标签 mock 数据" | warn | 需提前准备 mock |
| "需要一个可授信通过的订单" | pass | 可通过现有接口创建 |

---

## 维度 9：MQ 验证检查 (mq_verification)

### 触发条件
预期结果文本匹配 `MQ|message|topic|eventTag|EventBus|发送消息|cas_all_event`

### 检查逻辑
1. **topic 检查**：从预期中提取 MQ topic 名
   - 无 topic → **block**："MQ 验证未指定 topic，请补充如'topic=cas_all_event_topic'"
   - 有 topic → pass
2. **eventTag 检查**：从预期中提取 eventTag
   - 无 eventTag → **warn**："建议补充 eventTag 以精确定位 MQ 消息（如 eventTag=cas-app_adjust_apply）"
3. **payload 字段检查**：是否指定了需要验证的 payload 字段
   - 无具体字段 → **warn**："建议补充需验证的 payload 字段（如 activeCode=drawActivate）"
   - 有具体字段 → pass
4. **日志验证**：是否提到了通过日志验证 MQ 发送
   - 提到了 `OUTREQ/OUTRESP` → pass
   - 未提到 → **warn**："建议补充日志验证方式：查 OUTREQ/OUTRESP {topic}"

### 示例
| 文本 | 结果 | 说明 |
|------|------|------|
| "日志OUTREQ cas_all_event_topic, eventTag=cas-app_adjust_apply, activeCode=drawActivate" | pass | topic/tag/payload 齐全 |
| "MQ 消息发送成功" | block | 缺少 topic |
| "cas_all_event_topic 发送 drawActivate" | warn | 有 topic 和 activeCode，缺 eventTag |

---

## 维度 10：环境一致性检查 (env_consistency)

### 触发条件
步骤中引用了数据库名、表名或 Apollo 配置 key

### 检查逻辑
1. **环境自动获取**：如果用户未指定 `env`，通过 `testmind:get-current-week-sprint-env` 获取需求所属版本的默认环境
   - 当前周版本默认 STG1，下周版本默认 STG2
   - 获取成功 → 使用该环境继续检查
   - 获取失败 → **warn**："无法获取当前迭代默认环境，请手动指定"
2. **DB 环境检查**：查 `db_info_processed.json`，按 `{env}` 过滤
   - 引用的 subsystem/db_name 在目标环境存在 → pass
   - 不存在 → **block**："库 {db_name} 在 {env} 环境中不存在，请确认环境或库名"
3. **表环境检查**：对每张引用的表，在目标环境的数据库中做实检（见维度 2 步骤 3）
4. **Apollo 环境检查**：同一配置 key 在不同环境可能有不同值
   - 检查配置 key 是否带环境前缀 → pass
   - 不带 → **warn**："Apollo key '{key}' 未指定环境，确认是否需要在 {env} 环境单独配置"

### 检查依据
- `d:\TestScheduler\memory\db_info_processed.json`
- `testmind:get-current-week-sprint-env` 当前迭代环境

### 环境确定优先级
1. 用户显式指定 `--env STG2`
2. 通过 `get-current-week-sprint-env` 获取需求所属迭代的默认环境
3. 默认回落 STG1

---

## 跨维度规则

1. **维度激活**：不是所有维度对每个步骤都激活，仅当触发条件匹配时才进行检查
2. **累加判定**：一个步骤可能触发多个维度，每个维度的判定独立
3. **步骤级汇总**：步骤中任一维度 block → 该步骤 verdict = block；无 block 但有 warn → verdict = warn；全 pass → verdict = pass
4. **用例级汇总**：任一步骤 block → 该用例 verdict = block
5. **全局判定**：任一用例 block → `can_proceed = false`
6. **自动修复**：维度 4（渠道映射）的精确匹配结果自动记录为 auto_fix
