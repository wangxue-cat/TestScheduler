# sql-execute 详细规则

## 1. 唯一入口

所有 SQL 执行必须通过此 skill，**禁止以下行为**：

- ❌ 直接 subprocess 调用 `execute_sql.py`（绕过 QOA 追踪）
- ❌ 使用 curl 直接调用 HTTP API
- ❌ 使用 innovateTools DB 执行工具
- ❌ 直接 SQL 连接

**正确方式**：
1. Phase A: wrapper 解析参数（`run.py --resolve-only`）
2. Phase B: `Skill(testmind:sql-execute, args)` 执行（QOA 追踪）
3. Phase C: 编码修复 + sharding 回退

## 2. 环境获取

| 条件 | 取值 |
|------|------|
| 用户显式给出环境 | 使用用户给出的环境 |
| 用户未给出环境 | 调用 `testmind:get-current-week-sprint-env` 获取当前迭代默认环境 |

**不可猜测环境**。

## 3. 数据库路由

通过 `d:\TestScheduler\memory\db_info_processed.json` 匹配：

- `系统名.表名` → `系统名` 作为 lookup_key，按 `env + system` 匹配 `db_name`
- 只说表名 → 需用户补充系统名
- 同一 subsystem 可能匹配多个库（普通库 + sharding 库）

### Sharding 库匹配与回退规则

1. **用户显式指定 sharding**（如 `lcs-sharding.xxx`）→ 直接查 sharding 库
2. **缓存已标记**（`sharding_table_cache.json`）→ 直接查 sharding 库
3. **未指定且缓存无标记** → 优先查普通库
   - 普通库返回"表不存在"或"数据为空" → 自动回退同 subsystem 的 sharding 库
   - 回退查到数据 → 写入 `sharding_table_cache.json` 标记
4. 缓存文件：`d:\TestScheduler\memory\sharding_table_cache.json`

示例：

| 用户说 | 环境 | db_name | 回退 |
|--------|------|---------|------|
| aps.order_info | STG2 | aps_stg2 | 无需 |
| lcs.ln_loan | STG2 | lcs_stg2 → 表不存在 → lcs_sharding_stg2 | 回退并标记缓存 |
| lcs-sharding.xxx | STG2 | lcs_sharding_stg2 | 不回退 |

## 4. SQL 安全组装

### 自动追加 LIMIT

同时满足以下**全部条件**才追加 `ORDER BY id DESC LIMIT 1`：

1. SQL 中没有 `LIMIT` 子句
2. SQL 中没有 `ORDER BY` 子句
3. 用户没有明确说"查全部"、"查所有"、"查多条"
4. SQL 是针对整张表的数据查询（无 WHERE 条件过滤）

不追加的情况：

| SQL | 是否追加 | 原因 |
|-----|---------|------|
| `SELECT * FROM order_info` | ✅ 追加 | 无WHERE，针对全表数据 |
| `SELECT * FROM order_info WHERE user_id = 'xxx'` | ❌ 不追加 | 有WHERE条件 |
| `DESCRIBE order_info` | ❌ 不追加 | 查表结构 |
| `SHOW TABLE STATUS LIKE 'order_info'` | ❌ 不追加 | 查表信息 |
| `SELECT COUNT(*) FROM order_info` | ❌ 不追加 | 统计查询 |
| `SELECT id, name FROM order_info LIMIT 10` | ❌ 不追加 | 已有LIMIT |

### DELETE 和大批量 UPDATE

**必须暂停执行，用户确认**：

- 任何 DELETE 语句
- UPDATE 影响超过 20 条

确认展示格式：
```
⚠️ 危险操作确认
- 操作类型：DELETE / UPDATE
- SQL：{完整SQL}
- 预估影响行数：{N} 条
- 是否继续执行？
```

### 系统名.表名 格式解析

```
aps.order_info → env=STG2, db_name=aps_stg2, SQL=SELECT * FROM order_info ...
```

## 5. 编码修复

返回结果中的中文存在 UTF-8 双重编码（mojibake），修复方式：

```python
try:
    fixed_value = original_value.encode('latin1').decode('utf-8')
except:
    fixed_value = original_value  # ASCII 字段无需修复
```

## 6. 执行方式

**新架构（QOA 追踪）**：

```
# Phase A: 本地解析
python run.py --resolve-only --env STG1 --system aps --table order_info --sql "SELECT ..."

# Phase B: Skill 执行（QOA 追踪）
Skill(testmind:sql-execute, "{skill_args}")

# Phase C: 后处理
编码修复 + sharding 回退
```

> 🚫 **禁止**直接 subprocess 调用 execute_sql.py。执行必须通过 `Skill(testmind:sql-execute)` 确保 QOA 追踪。
