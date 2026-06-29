---
name: db-info-lookup
description: 数据库查找映射表，根据环境+子系统名查找实际db_name，含sharding合并规则
metadata: 
  type: reference
---

# 数据库查找映射

数据来源：`qoa_test_db.db_info` 表，已处理 sharding 合并规则。

## 查找规则

当用户说"执行 {env} 环境 {subsystem} 库的 SQL"时：
1. 用 `{env}` + `{subsystem}` (不区分大小写) 在 `db_info_processed.json` 中查找 `lookup_key`
2. 取匹配记录的 `db_name` 作为实际数据库名传给 `--db-name` 参数
3. 如果找不到匹配，提示用户确认子系统名

## Sharding 合并规则

- 同一个 subsystem_name 下，如果某个 base_name 同时有普通版和 `-sharding` 版：
  - lookup_key 用去掉 `-sharding` 的 base_name（如 `lcs` 而非 `lcs-sharding`）
  - db_name 取 `-sharding` 版对应的值（如 `lcs_sharding_stg2` 而非 `lcs_stg2`）
  - 普通版记录被丢弃
- 没有 sharding 对应的子系统保持原样

## 示例

| 用户说的子系统 | 环境 | 实际 db_name |
|---|---|---|
| aps | STG2 | aps_stg2 |
| lcs | STG2 | lcs_sharding_stg2 |
| lcs-rp | STG2 | lcs_rp_sharding_stg2 |
| lcs-bill | STG2 | lcs_bill_stg2 |

## 数据文件

完整映射数据：`D:\TestScheduler\memory\db_info_processed.json`

每条记录格式：
```json
{
  "env": "STG2",
  "lookup_key": "aps",
  "system_name": "aps",
  "subsystem_name": "APS",
  "db_name": "aps_stg2"
}
```
