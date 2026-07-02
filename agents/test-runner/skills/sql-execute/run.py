# -*- coding: utf-8 -*-
"""
Script skill: sql-execute (TestScheduler)

统一SQL执行入口：环境获取 + 数据库路由 + SQL组装 + 安全校验 + 执行 + 编码修复 + sharding回退

## 新架构（推荐，QOA 追踪）

  # Phase A: 本地解析（纯本地，无网络调用）
  python run.py --resolve-only --env STG1 --system aps --table t --sql "SELECT ..."
  → 输出 JSON {env, db_name, sql, skill_args, ...}

  # Phase B: 执行（通过 Skill，QOA 追踪）
  Skill(testmind:sql-execute, "{skill_args}")

  # Phase C: 后处理
  编码修复 + sharding 回退

  **环境获取**: 若用户未指定环境，主会话先调用 Skill(testmind:get-current-week-sprint-env)

## 旧模式（已废弃，仅向后兼容）

  python run.py --sql "..." --system aps --sprint-name "..."
  → 完整执行流程（含 subprocess），不走 Skill 追踪
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── 路径配置 ──────────────────────────────────────────────
def _find_latest_plugin_root() -> Path:
    """自动发现 testmind 插件最新版本目录"""
    base = Path("c:/Users/wangxue-jk/.claude/plugins/cache/quality-cc-marketplace/testmind")
    if not base.exists():
        raise FileNotFoundError(f"testmind 插件目录不存在: {base}")
    versions = sorted(
        (d for d in base.iterdir() if d.is_dir()),
        key=lambda p: tuple(int(x) for x in p.name.split(".")),
        reverse=True,
    )
    if not versions:
        raise FileNotFoundError(f"testmind 插件目录下未找到版本子目录: {base}")
    return versions[0]


PLUGIN_ROOT = _find_latest_plugin_root()
EXECUTE_SQL_SCRIPT = PLUGIN_ROOT / "skills" / "sql-execute" / "scripts" / "execute_sql.py"

# TestScheduler 本地路径
DB_INFO_PATH = Path("D:/TestScheduler/memory/db_info_processed.json")
SHARDING_CACHE_PATH = Path("D:/TestScheduler/memory/sharding_table_cache.json")


# ── Step 1: 环境获取 ─────────────────────────────────────
def resolve_env(env: str = "") -> str:
    """
    解析环境（新架构）：仅做规范化，不发起任何网络/subprocess 调用。

    主会话责任：若 env 为空，主会话必须先调用 Skill(testmind:get-current-week-sprint-env)
    获取当前迭代默认环境后再传入。若仍为空，返回空字符串。
    """
    return (env or "").strip().upper()


def _resolve_env_legacy(env: str = "", sprint_name: str = "") -> str:
    """
    [已废弃] 旧架构的环境解析（含 subprocess 调 execute_sql.py 查 sprint 环境）。
    仅用于旧 run() 路径的向后兼容，新架构禁止使用。
    """
    env = (env or "").strip().upper()
    if env:
        return env

    if not sprint_name:
        sprint_name = os.environ.get("CURRENT_SPRINT_NAME", "")

    if sprint_name:
        import subprocess
        try:
            cmd = [
                sys.executable, str(EXECUTE_SQL_SCRIPT),
                "--env", "STG2", "--db-name", "qoa", "--page-size", "1",
                "--sql", f"select env from sprint_env_relation where sprint_name='{sprint_name}'"
                        f" and is_deleted=0 limit 1;"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(result.stdout)
            if data.get("results"):
                resolved_env = data["results"][0].get("env", "")
                if resolved_env:
                    return resolved_env.upper()
        except Exception:
            pass

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

    is_sharding_requested = "-sharding" in system_lower
    lookup_system = system_lower.replace("-sharding", "")

    matches = [
        r for r in db_info
        if r.get("env", "").upper() == env.upper()
        and r.get("system", "").lower() == lookup_system
    ]

    if not matches:
        matches = [
            r for r in db_info
            if r.get("env", "").upper() == env.upper()
            and r.get("subsystem_name", "").lower() == lookup_system
        ]

    if not matches:
        return ("", False)

    normal = [r for r in matches if "-sharding" not in r.get("system", "")]
    sharding = [r for r in matches if "-sharding" in r.get("system", "")]

    cache_key = f"{system}.{table}" if table else ""
    sharding_cache = _load_sharding_cache()
    if cache_key and cache_key in sharding_cache:
        if sharding:
            return (sharding[0]["db_name"], True)

    if is_sharding_requested:
        if sharding:
            return (sharding[0]["db_name"], True)

    if normal:
        return (normal[0]["db_name"], False)
    if sharding:
        return (sharding[0]["db_name"], True)

    return ("", False)


def try_sharding_fallback(env: str, system: str, table: str, db_name_used: str) -> Optional[str]:
    """普通库查不到时，回退到 sharding 库"""
    db_info = _load_db_info()
    current = next((r for r in db_info if r.get("db_name") == db_name_used), None)
    if not current:
        return None

    subsystem = current.get("subsystem_name", "")
    sharding = next(
        (r for r in db_info
         if r.get("env", "").upper() == env.upper()
         and r.get("subsystem_name") == subsystem
         and "-sharding" in r.get("system", "")),
        None
    )
    if sharding:
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

    if sql_upper.startswith("DELETE"):
        needs_confirm = True

    if sql_upper.startswith("UPDATE"):
        limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if not limit_match or int(limit_match.group(1)) > 20:
            needs_confirm = True

    if not user_wants_all:
        has_limit = "LIMIT" in sql_upper
        has_order = "ORDER BY" in sql_upper
        if not has_limit and not has_order:
            sql = sql.rstrip(";") + " ORDER BY id DESC LIMIT 1;"

    return (sql, needs_confirm)


# ── 解析器（新架构核心）──────────────────────────────────
def resolve(params: dict) -> dict:
    """
    仅解析，不执行。返回结构化解析结果，供主会话传给 Skill(testmind:sql-execute)。

    参数：
      - env: 环境（必填，主会话应已通过 Skill(testmind:get-current-week-sprint-env) 解析）
      - system: 系统名（如 aps、lcs）
      - table: 表名（可选）
      - sql: SQL 语句
      - page_size: 返回条数（默认10）
      - user_wants_all: 是否查全量（默认False）
      - confirm_dangerous: 是否已确认危险操作（默认False）

    返回 dict:
      - ok: bool
      - env: 解析后的环境
      - db_name: 解析后的数据库名
      - system: 系统名
      - table: 表名
      - sql: 组装后的 SQL
      - page_size: int
      - is_sharding: bool
      - needs_confirm: bool
      - error: str（仅 ok=False 时）
      - skill_args: str（可直接传给 Skill(testmind:sql-execute) 的参数字符串）
    """
    env = params.get("env", "")
    system = params.get("system", "")
    table = params.get("table", "")
    sql = params.get("sql", "")
    page_size = int(params.get("page_size", 10))
    user_wants_all = params.get("user_wants_all", False)
    confirm_dangerous = params.get("confirm_dangerous", False)

    if not sql:
        return {"ok": False, "error": "缺少 SQL 语句"}

    # Step 1: 解析环境（仅规范化，不发起网络调用）
    resolved_env = resolve_env(env)
    if not resolved_env:
        return {
            "ok": False,
            "error": "未指定环境",
            "hint": "请先调用 Skill(testmind:get-current-week-sprint-env) 获取当前迭代默认环境，"
                    "或手动指定 --env STG1/STG2/STG3"
        }

    # Step 2: 解析数据库
    db_name = ""
    is_sharding = False
    if system:
        db_name, is_sharding = resolve_db_name(resolved_env, system, table)
        if not db_name:
            return {
                "ok": False,
                "error": f"未找到系统 '{system}' 在环境 '{resolved_env}' 下的数据库映射",
                "hint": "请检查系统名是否正确，或查看 db_info_processed.json"
            }

    # Step 3: 组装 SQL
    final_sql, needs_confirm = assemble_sql(sql, user_wants_all)
    if needs_confirm and not confirm_dangerous:
        return {
            "ok": False,
            "error": "危险操作需要用户确认",
            "needs_confirm": True,
            "sql": final_sql,
            "hint": "请在主会话中确认后重试"
        }

    if not db_name:
        return {
            "ok": False,
            "error": "缺少系统名，无法路由到数据库",
            "hint": "请提供 system 参数（如 aps、lcs）或使用 '系统名.表名' 格式"
        }

    # 构建可直接传给 Skill(testmind:sql-execute) 的参数
    skill_args = f"{resolved_env} {db_name} {final_sql}"

    return {
        "ok": True,
        "env": resolved_env,
        "db_name": db_name,
        "system": system,
        "table": table,
        "sql": final_sql,
        "page_size": page_size,
        "is_sharding": is_sharding,
        "needs_confirm": False,
        "skill_args": skill_args
    }


# ── Step 4: 执行 SQL（仅旧模式使用）──────────────────────
def execute_sql(env: str, db_name: str, sql: str, page_size: int = 10, fmt: str = "json") -> Dict[str, Any]:
    """
    [已废弃] 直接 subprocess 调用 execute_sql.py，绕过 QOA 追踪。
    新架构请用：resolve() → Skill(testmind:sql-execute)
    """
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
        if any('一' <= c <= '鿿' for c in fixed):
            return fixed
    except Exception:
        pass
    return value


def fix_result_encoding(data: Any) -> Any:
    """递归修复结果中的 mojibake"""
    if isinstance(data, dict):
        return {k: fix_result_encoding(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [fix_result_encoding(item) for item in data]
    elif isinstance(data, str):
        return fix_mojibake(data)
    return data


# ── 旧模式主入口（向后兼容，已废弃）──────────────────────
def run(params: dict) -> str:
    """
    [已废弃] 完整执行流程（含 subprocess 调用），不走 QOA 追踪。
    请使用新架构：
      1. python run.py --resolve-only --env STG1 ...  → 解析参数
      2. Skill(testmind:sql-execute, args)             → 执行（QOA 追踪）
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

    # 旧架构：用 legacy 环境解析（含 subprocess 查 sprint 环境）
    resolved_env = _resolve_env_legacy(env, sprint_name)

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

    # Step 4: 执行 SQL（subprocess — 已废弃，不走 QOA 追踪）
    result = execute_sql(resolved_env, db_name, final_sql, page_size)

    # Step 5: 编码修复
    result = fix_result_encoding(result)

    # sharding 回退
    results = result.get("results", [])
    is_empty = not results
    is_table_not_exist = "不存在" in result.get("msg", "") or "doesn't exist" in result.get("msg", "").lower()

    if (is_empty or is_table_not_exist) and not is_sharding and system and table:
        sharding_db = try_sharding_fallback(resolved_env, system, table, db_name)
        if sharding_db:
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

    flag = result.get("flag", "")
    return json.dumps({
        "ok": flag in ("S", "T", True),
        "env": resolved_env,
        "db_name": db_name,
        "sql": final_sql,
        "is_sharding": is_sharding,
        "data": result
    }, ensure_ascii=False)


# ── CLI ──────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="统一SQL执行入口 (TestScheduler)")
    parser.add_argument("--env", default="", help="环境（STG1/STG2/STG3）")
    parser.add_argument("--system", default="", help="系统名（aps/lcs/lcs-sharding）")
    parser.add_argument("--table", default="", help="表名")
    parser.add_argument("--sql", required=True, help="SQL语句")
    parser.add_argument("--page-size", type=int, default=10, help="返回条数")
    parser.add_argument("--sprint-name", default="", help="[已废弃] 当前迭代版本名，仅旧模式使用")
    parser.add_argument("--all", dest="user_wants_all", action="store_true", help="查全量（不追加LIMIT）")
    parser.add_argument("--confirm-dangerous", action="store_true", help="确认执行危险操作")
    parser.add_argument("--resolve-only", action="store_true",
                        help="仅解析参数不执行。输出 JSON 供主会话传给 Skill(testmind:sql-execute)")
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

    if args.resolve_only:
        # 新架构：仅解析，主会话拿到结果后调用 Skill(testmind:sql-execute)
        result = resolve(params)
        print(json.dumps(result, ensure_ascii=False))
    else:
        # 旧模式（已废弃，向后兼容）
        print(run(params))
