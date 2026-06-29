# -*- coding: utf-8 -*-
"""
Script skill: sql-execute (TestScheduler)

统一SQL执行入口：环境获取 + 数据库路由 + SQL组装 + 安全校验 + 执行 + 编码修复 + sharding回退
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── 路径配置 ──────────────────────────────────────────────
PLUGIN_ROOT = Path("c:/Users/wangxue-jk/.claude/plugins/cache/quality-cc-marketplace/testmind/1.0.34")
EXECUTE_SQL_SCRIPT = PLUGIN_ROOT / "skills" / "common_sql_execute" / "scripts" / "execute_sql.py"

# TestScheduler 本地路径
DB_INFO_PATH = Path("D:/TestScheduler/memory/db_info_processed.json")
SHARDING_CACHE_PATH = Path("D:/TestScheduler/memory/sharding_table_cache.json")


# ── Step 1: 环境获取 ─────────────────────────────────────
def resolve_env(env: str = "", sprint_name: str = "") -> str:
    """解析环境：用户指定 > 调用testmind获取当前迭代默认环境"""
    env = (env or "").strip().upper()
    if env:
        return env

    # 调用 testmind:get-current-week-sprint-env 获取默认环境
    # 需要当前迭代版本名
    if not sprint_name:
        # 尝试从环境变量或默认获取
        sprint_name = os.environ.get("CURRENT_SPRINT_NAME", "")

    if sprint_name:
        import subprocess
        try:
            cmd = [
                sys.executable, str(EXECUTE_SQL_SCRIPT),
                "--env", "STG2", "--db-name", "qoa", "--page-size", "1",
                "--sql", f"select env from sprint_env_relation where sprint_name='{sprint_name}' and is_deleted=0 limit 1;"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            if data.get("results"):
                resolved_env = data["results"][0].get("env", "")
                if resolved_env:
                    return resolved_env.upper()
        except Exception:
            pass

    # 最终兜底
    return "STG2"


# ── Step 2: 数据库路由 ───────────────────────────────────
def _load_db_info() -> List[Dict]:
    if not DB_INFO_PATH.exists():
        return []
    with open(DB_INFO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_sharding_cache() -> Dict[str, str]:
    if not SHARDING_CACHE_PATH.exists():
        return {}
    with open(SHARDING_CACHE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_sharding_cache(cache: Dict[str, str]) -> None:
    SHARDING_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SHARDING_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def resolve_db_name(env: str, system: str, table: str = "") -> Tuple[str, bool]:
    """
    解析数据库名：通过 db_info_processed.json 路由匹配
    返回 (db_name, is_sharding)
    """
    db_info = _load_db_info()
    system_lower = system.lower().strip()

    # 检查用户是否显式指定 sharding
    is_sharding_requested = "-sharding" in system_lower
    lookup_system = system_lower.replace("-sharding", "")

    # 匹配同 env + system 的所有库
    matches = [
        r for r in db_info
        if r.get("env", "").upper() == env.upper()
        and r.get("system", "").lower() == lookup_system
    ]

    if not matches:
        # 尝试 subsystem_name 匹配
        matches = [
            r for r in db_info
            if r.get("env", "").upper() == env.upper()
            and r.get("subsystem_name", "").lower() == lookup_system
        ]

    if not matches:
        return ("", False)

    # 分离普通库和 sharding 库
    normal = [r for r in matches if "-sharding" not in r.get("system", "")]
    sharding = [r for r in matches if "-sharding" in r.get("system", "")]

    # 检查 sharding 缓存
    cache_key = f"{system}.{table}" if table else ""
    sharding_cache = _load_sharding_cache()
    if cache_key and cache_key in sharding_cache:
        if sharding:
            return (sharding[0]["db_name"], True)

    # 用户显式指定 sharding
    if is_sharding_requested:
        if sharding:
            return (sharding[0]["db_name"], True)

    # 优先普通库
    if normal:
        return (normal[0]["db_name"], False)
    if sharding:
        return (sharding[0]["db_name"], True)

    return ("", False)


def try_sharding_fallback(env: str, system: str, table: str, db_name_used: str) -> Optional[str]:
    """普通库查不到时，回退到 sharding 库"""
    db_info = _load_db_info()
    # 找到当前库的 subsystem
    current = next((r for r in db_info if r.get("db_name") == db_name_used), None)
    if not current:
        return None

    subsystem = current.get("subsystem_name", "")
    # 找同 subsystem 的 sharding 库
    sharding = next(
        (r for r in db_info
         if r.get("env", "").upper() == env.upper()
         and r.get("subsystem_name") == subsystem
         and "-sharding" in r.get("system", "")),
        None
    )
    if sharding:
        # 写入缓存
        cache = _load_sharding_cache()
        cache_key = f"{system}.{table}" if table else ""
        if cache_key:
            cache[cache_key] = "sharding"
            _save_sharding_cache(cache)
        return sharding["db_name"]
    return None


# ── Step 3: SQL 组装 ─────────────────────────────────────
def assemble_sql(sql: str, user_wants_all: bool = False) -> Tuple[str, bool]:
    """
    组装 SQL：追加排序限制 + 检测危险操作
    返回 (final_sql, needs_confirm)
    """
    sql = sql.strip()
    if not sql.endswith(";"):
        sql += ";"

    needs_confirm = False
    sql_upper = sql.upper().strip()

    # 检测 DELETE
    if sql_upper.startswith("DELETE"):
        needs_confirm = True

    # 检测大批量 UPDATE（无 LIMIT 或 LIMIT > 20）
    if sql_upper.startswith("UPDATE"):
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if not limit_match or int(limit_match.group(1)) > 20:
            needs_confirm = True

    # 追加 ORDER BY id DESC LIMIT 1（条件同时满足）
    if not user_wants_all:
        has_limit = "LIMIT" in sql_upper
        has_order = "ORDER BY" in sql_upper
        if not has_limit and not has_order:
            # 去掉末尾分号追加
            sql = sql.rstrip(";") + " ORDER BY id DESC LIMIT 1;"

    return (sql, needs_confirm)


# ── Step 4: 执行 SQL ─────────────────────────────────────
def execute_sql(env: str, db_name: str, sql: str, page_size: int = 10, fmt: str = "json") -> Dict[str, Any]:
    """调用 testmind:sql-execute 的 execute_sql.py 脚本执行"""
    import subprocess
    cmd = [
        sys.executable, str(EXECUTE_SQL_SCRIPT),
        "--env", env,
        "--db-name", db_name,
        "--sql", sql,
        "--page-size", str(page_size),
        "--format", fmt
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        return {"flag": "F", "msg": f"执行失败: {result.stderr[:500]}", "results": []}

    try:
        data = json.loads(result.stdout)
    except Exception as e:
        return {"flag": "F", "msg": f"解析返回失败: {e}", "results": []}

    return data


# ── Step 5: 编码修复 ─────────────────────────────────────
def fix_mojibake(value: str) -> str:
    """修复 UTF-8 双重编码导致的 mojibake"""
    if not value or not any(ord(c) > 127 for c in value):
        return value
    try:
        fixed = value.encode('latin1').decode('utf-8')
        # 验证修复后是否包含中文字符
        if any('一' <= c <= '鿿' for c in fixed):
            return fixed
    except Exception:
        pass
    return value


def fix_result_encoding(data: Dict[str, Any]) -> Dict[str, Any]:
    """递归修复结果中的 mojibake"""
    if isinstance(data, dict):
        return {k: fix_result_encoding(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [fix_result_encoding(item) for item in data]
    elif isinstance(data, str):
        return fix_mojibake(data)
    return data


# ── 主入口 ───────────────────────────────────────────────
def run(params: dict) -> str:
    """
    统一SQL执行入口

    参数：
      - env: 环境（可选，不传则自动获取）
      - system: 系统名（如 aps、lcs、lcs-sharding）
      - table: 表名（可选）
      - sql: SQL语句
      - page_size: 返回条数（默认10）
      - sprint_name: 当前迭代版本名（可选，用于获取默认环境）
      - user_wants_all: 用户是否要查全量（默认False）
      - confirm_dangerous: 用户是否已确认危险操作（默认False）
    """
    env = params.get("env", "")
    system = params.get("system", "")
    table = params.get("table", "")
    sql = params.get("sql", "")
    page_size = int(params.get("page_size", 10))
    sprint_name = params.get("sprint_name", "")
    user_wants_all = params.get("user_wants_all", False)
    confirm_dangerous = params.get("confirm_dangerous", False)

    if not sql:
        return json.dumps({"ok": False, "error": "缺少 SQL 语句"}, ensure_ascii=False)

    # Step 1: 解析环境
    resolved_env = resolve_env(env, sprint_name)

    # Step 2: 解析数据库
    db_name = ""
    is_sharding = False
    if system:
        db_name, is_sharding = resolve_db_name(resolved_env, system, table)
        if not db_name:
            return json.dumps({
                "ok": False,
                "error": f"未找到系统 '{system}' 在环境 '{resolved_env}' 下的数据库映射",
                "hint": "请检查系统名是否正确，或查看 db_info_processed.json"
            }, ensure_ascii=False)

    # Step 3: 组装 SQL
    final_sql, needs_confirm = assemble_sql(sql, user_wants_all)
    if needs_confirm and not confirm_dangerous:
        return json.dumps({
            "ok": False,
            "error": "危险操作需要用户确认",
            "needs_confirm": True,
            "sql": final_sql,
            "hint": "请设置 confirm_dangerous=true 确认执行"
        }, ensure_ascii=False)

    if not db_name:
        return json.dumps({
            "ok": False,
            "error": "缺少系统名，无法路由到数据库",
            "hint": "请提供 system 参数（如 aps、lcs）或使用 '系统名.表名' 格式"
        }, ensure_ascii=False)

    # Step 4: 执行 SQL
    result = execute_sql(resolved_env, db_name, final_sql, page_size)

    # Step 5: 编码修复
    result = fix_result_encoding(result)

    # 检查是否需要 sharding 回退
    results = result.get("results", [])
    is_empty = not results
    is_table_not_exist = "不存在" in result.get("msg", "") or "doesn't exist" in result.get("msg", "").lower()

    if (is_empty or is_table_not_exist) and not is_sharding and system and table:
        sharding_db = try_sharding_fallback(resolved_env, system, table, db_name)
        if sharding_db:
            # 回退到 sharding 库重查
            sharding_result = execute_sql(resolved_env, sharding_db, final_sql, page_size)
            sharding_result = fix_result_encoding(sharding_result)
            sharding_results = sharding_result.get("results", [])
            if sharding_results:
                sharding_result["sharding_fallback"] = {
                    "original_db": db_name,
                    "fallback_db": sharding_db,
                    "reason": "普通库无数据/表不存在，已自动回退到 sharding 库"
                }
                return json.dumps({
                    "ok": True,
                    "env": resolved_env,
                    "db_name": sharding_db,
                    "sql": final_sql,
                    "is_sharding": True,
                    "data": sharding_result
                }, ensure_ascii=False)

    # 返回结果
    flag = result.get("flag", "")
    return json.dumps({
        "ok": flag in ("S", "T", True),
        "env": resolved_env,
        "db_name": db_name,
        "sql": final_sql,
        "is_sharding": is_sharding,
        "data": result
    }, ensure_ascii=False)


if __name__ == "__main__":
    # CLI 模式：从命令行参数执行
    import argparse
    parser = argparse.ArgumentParser(description="统一SQL执行入口 (TestScheduler)")
    parser.add_argument("--env", default="", help="环境（STG1/STG2/STG3）")
    parser.add_argument("--system", default="", help="系统名（aps/lcs/lcs-sharding）")
    parser.add_argument("--table", default="", help="表名")
    parser.add_argument("--sql", required=True, help="SQL语句")
    parser.add_argument("--page-size", type=int, default=10, help="返回条数")
    parser.add_argument("--sprint-name", default="", help="当前迭代版本名")
    parser.add_argument("--all", dest="user_wants_all", action="store_true", help="查全量（不追加LIMIT）")
    parser.add_argument("--confirm-dangerous", action="store_true", help="确认执行危险操作")
    args = parser.parse_args()

    params = {
        "env": args.env,
        "system": args.system,
        "table": args.table,
        "sql": args.sql,
        "page_size": args.page_size,
        "sprint_name": args.sprint_name,
        "user_wants_all": args.user_wants_all,
        "confirm_dangerous": args.confirm_dangerous,
    }
    print(run(params))
