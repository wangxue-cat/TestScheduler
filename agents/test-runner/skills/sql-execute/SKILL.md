---
name: sql-execute
description: "SQL执行skill：统一入口，环境获取+数据库路由+SQL组装+安全校验+执行，所有SQL执行必须通过此skill"
argument-hint: "[环境] [系统名.表名] [SQL]"
---

# sql-execute

所有 SQL 执行的**唯一入口**。任何涉及 SQL 执行的操作都必须通过此 skill，禁止绕过。

## 硬性约束

1. **唯一入口** — 禁止绕过此 skill 直接调 `testmind:sql-execute` 或 curl
2. **不可猜测** — 环境通过 `testmind:get-current-week-sprint-env` 获取，库名通过 `db_info_processed.json` 匹配
3. **危险操作确认** — DELETE 和 >20 条影响的 UPDATE 必须用户确认

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| env | string | 否 | STG1/STG2/STG3，未指定时自动获取 |
| db_ref | string | 是 | `系统名.表名` 格式，如 `aps.order_info` |
| sql | string | 是 | SQL 语句 |

## 执行流程

```
用户需求 → Step1解析环境 → Step2解析数据库 → Step3组装SQL → Step4执行 → Step5处理结果
```

1. **解析环境** — 用户指定优先，否则查当前迭代默认环境
2. **解析数据库** — `系统名.表名` → `db_info_processed.json` 匹配 `db_name`，支持 sharding 回退
3. **组装 SQL** — 无 WHERE/LIMIT/ORDER BY 的数据查询自动追加 `ORDER BY id DESC LIMIT 1`
4. **执行** — 通过 `execute_sql.py` 脚本调用 `testmind:sql-execute`
5. **处理结果** — 编码修复（mojibake）+ sharding 回退

## 输出

SQL 执行结果（markdown 格式），自动修复中文编码。

## 关键规则

1. DELETE/大批量UPDATE 必须暂停确认
2. 查不到数据时自动回退同 subsystem 的 sharding 库
3. 中文结果修复 UTF-8 双重编码

> 📁 详细规则 → [refs/rules.md](refs/rules.md)  
> 📁 执行步骤展开 → [refs/io.md](refs/io.md)  
> 📁 执行脚本 → [run.py](run.py)
