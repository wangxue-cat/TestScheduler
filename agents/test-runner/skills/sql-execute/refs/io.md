# sql-execute 输入/输出定义

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| env | string | 否 | STG1/STG2/STG3，未指定时从当前迭代获取 |
| db_ref | string | 是 | `系统名.表名` 格式，如 `aps.order_info` |
| sql | string | 是 | 完整 SQL 语句 |

## 执行步骤展开

### Step 1: 解析环境

获取当前环境的方式：

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/common_sql_execute/scripts/execute_sql.py" \
  --env STG2 --db-name qoa --page-size 1 \
  --sql "select env from sprint_env_relation where sprint_name='{当前迭代版本}' and is_deleted=0 limit 1;"
```

### Step 2: 解析数据库

**文件路径**：`d:\TestScheduler\memory\db_info_processed.json`

匹配规则：
- 用户使用 `系统名.表名` 格式 → `系统名` 作为 lookup_key，按 `env + system` 匹配 `db_name`
- 用户只说表名 → 需用户补充系统名，或根据上下文推断
- 同一 subsystem 下可能匹配多个库（普通库 + sharding 库）

见 [refs/rules.md](rules.md) 第3条了解完整的 sharding 回退规则。

### Step 3: 组装 SQL

#### 默认追加排序和限制

用户未指定排序和数量时，自动追加 `ORDER BY id DESC LIMIT 1;`

追加条件（**同时满足**）：
1. SQL 中没有 `LIMIT` 子句
2. SQL 中没有 `ORDER BY` 子句
3. 用户没有明确说"查全部"、"查所有"、"查多条"等
4. SQL 是针对整张表的数据查询（无 WHERE 条件过滤）

不追加的情况：
- SQL 中已有 `LIMIT` 或 `ORDER BY`
- 用户明确指定了排序规则或数据条数
- 用户明确要查全量或多条
- SQL 有 WHERE 条件
- SQL 不是数据查询（DESCRIBE、SHOW TABLE STATUS、SHOW COLUMNS 等）
- SQL 是聚合/统计类查询（COUNT、SUM 等）

#### DELETE 和大批量 UPDATE

见 [refs/rules.md](rules.md) 第4条。

### Step 4: 执行

> 🚫 **禁止直接 subprocess 调用 execute_sql.py**。必须通过 `Skill(testmind:sql-execute)` 执行，确保 QOA 平台的 `testmind:schedule` 能追踪到 skill 执行次数。

**Phase B 执行协议**：

1. 从 Phase A (`run.py --resolve-only`) 获取 `skill_args` 字段
2. 调用 `Skill(testmind:sql-execute, "{skill_args}")`
3. Skill 内部会运行 `execute_sql.py` 脚本发起 HTTP 请求
4. 获取返回的 JSON 结果（`flag`、`msg`、`results`）

**Skill 参数格式**：`"<env> <db_name> <sql>"`，如 `"STG1 aps_stg1 SELECT * FROM t WHERE id=1;"`

**注意**：
- Skill 内部自动处理 token 获取和刷新
- 返回格式为 JSON，包含 `flag`、`msg`、`results`

### Step 5: 处理结果

#### 编码修复

服务端返回的中文存在 UTF-8 双重编码（mojibake）：

```python
try:
    fixed_value = original_value.encode('latin1').decode('utf-8')
except:
    fixed_value = original_value
```

#### Sharding 回退

若普通库返回"表不存在"或"数据为空"：
1. 查找同 subsystem 下的 sharding 库
2. 用 sharding 库重新执行同一 SQL
3. 若 sharding 库有数据 → 写入 `sharding_table_cache.json`，告知用户已回退
4. 若 sharding 库也无数据 → 输出原始结果

## 输出

SQL 执行结果（markdown 格式），已修复中文编码。
