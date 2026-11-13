#!/usr/bin/env python3
"""Read-only WorkBuddy environment probe for the office-retro skill.

Purpose: produce verifiable, first-hand evidence (paths, counts, timestamps)
for step 2 of a retro. The script opens configuration files as structured data
and reports key names and counts only; credential values remain in the files.

Usage:
    python3 scripts/workbuddy_env_probe.py
    python3 scripts/workbuddy_env_probe.py --json
    python3 scripts/workbuddy_env_probe.py --workspace /path/to/workspace
    python3 scripts/workbuddy_env_probe.py --home /path/to/.workbuddy --strict
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

OK = "OK"
MISSING = "MISSING"
INFO = "INFO"


def load_json(path: Path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def stamp(path: Path) -> str:
    try:
        return dt.datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return "-"


def files(root: Path, pattern: str):
    if not root.is_dir():
        return []
    return sorted((p for p in root.glob(pattern) if p.is_file()), key=lambda p: p.stat().st_mtime, reverse=True)


def line_count(path: Path) -> int:
    try:
        with path.open(encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def probe(home: Path, workspace: Path):
    rows = []

    def add(item: str, status: str, evidence: str):
        rows.append({"item": item, "status": status, "evidence": evidence})

    add("配置根目录", OK if home.is_dir() else MISSING, str(home))
    if not home.is_dir():
        return rows, []

    # Identity / awareness files (injected into the session by WorkBuddy).
    personal = [p for p in home.glob("user-*-personal") if p.is_dir() and ".bak" not in p.name]
    for p in personal[:1]:
        names = [n for n in ("SOUL.md", "IDENTITY.md", "USER.md", "MEMORY.md") if (p / n).is_file()]
        add("意识文件", OK if names else MISSING,
            "{}: {} ({} bytes / MEMORY.md)".format(
                p.name, ", ".join(names) or "无",
                (p / "MEMORY.md").stat().st_size if (p / "MEMORY.md").is_file() else 0))
    if not personal:
        add("意识文件", MISSING, "user-*-personal 目录")

    user_memory = home / "MEMORY.md"
    add("用户级本地记忆", OK if user_memory.is_file() else MISSING,
        "{} ({} bytes)".format(user_memory, user_memory.stat().st_size) if user_memory.is_file() else str(user_memory))

    ws_memory = workspace / ".workbuddy" / "memory"
    logs = files(ws_memory, "*.md")
    add("工作区记忆", OK if ws_memory.is_dir() else MISSING,
        "{}，日志文件 {} 个".format(ws_memory, len(logs)))

    user_skills = home / "skills"
    project_skills = workspace / ".workbuddy" / "skills"
    add("技能目录（用户级）", OK if user_skills.is_dir() else MISSING,
        "{}，已装技能 {} 个".format(user_skills, len([p for p in user_skills.iterdir() if p.is_dir()]) if user_skills.is_dir() else 0))
    add("技能目录（项目级）", OK if project_skills.is_dir() else INFO,
        "{}".format(project_skills))

    installed = user_skills / "office-retro" / "SKILL.md"
    add("office-retro 安装", OK if installed.is_file() else MISSING, str(installed))

    settings = load_json(home / "settings.json") or {}
    overrides = settings.get("skillOverrides") or {}
    hooks = settings.get("hooks") or {}
    add("技能启用开关", INFO,
        "settings.json skillOverrides 条目 {} 个；office-retro {}".format(
            len(overrides) if isinstance(overrides, dict) else 0,
            "有覆盖记录" if any("office-retro" in str(k) for k in (overrides or {})) else "无覆盖记录"))
    add("UserPromptSubmit 等 hooks", OK if hooks else INFO,
        "hooks 键：{}".format(", ".join(sorted(hooks.keys())) if isinstance(hooks, dict) else "无"))

    mcp = load_json(home / "mcp.json")
    if isinstance(mcp, dict) and "mcpServers" in mcp:
        servers = mcp.get("mcpServers") or {}
        add("MCP 配置结构", OK,
            "顶层键 {}；mcpServers {} 个；disabledMcpServers {} 项（仅计数，值保留在文件内）".format(
                ", ".join(sorted(mcp.keys())), len(servers),
                len(mcp.get("disabledMcpServers") or []) if isinstance(mcp.get("disabledMcpServers"), list) else 0))
    else:
        add("MCP 配置结构", MISSING, "{}，期望双层结构 mcpServers / disabledMcpServers".format(home / "mcp.json"))

    models = load_json(home / "models.json")
    if isinstance(models, (list, dict)):
        total = len(models) if isinstance(models, list) else len(models.get("models") or [])
        add("自定义模型配置", OK, "顶层类型 {}，条目 {} 个（仅计数，凭据字段保留在文件内）".format(type(models).__name__, total))
    else:
        add("自定义模型配置", INFO, "{} 缺失或格式待确认".format(home / "models.json"))

    # First-hand evidence produced by WorkBuddy runs.
    materials = [
        ("会话记录", home / "projects", "*/*.jsonl"),
        ("追踪记录", home / "traces", "*/*.jsonl"),
        ("运行日志", home / "logs", "*/*.log"),
        ("审计日志", home / "audit-log", "*.jsonl"),
        ("任务清单", home / "tasks", "*/*.json"),
        ("会话元数据", home / "sessions", "*.json"),
    ]
    recent = []
    for label, root, pattern in materials:
        found = files(root, pattern)
        add("一手材料 · " + label, OK if found else INFO,
            "{} 下 {} 个文件{}".format(root, len(found),
                                      "，最近 {}".format(stamp(found[0])) if found else ""))
        if label == "会话记录":
            recent = found[:3]

    add("定时任务入口", INFO,
        "左侧导航栏「定时任务」→「定时任务」/「运行记录」；配置含名称、提示词、模型/专家/技能/连接器、工作空间、权限、重复、有效期")
    add("结果区回读", INFO,
        "右侧结果区「产物 / 网页 / 工作空间文件 / 变更」四个视图")
    add("权限与工作模式", INFO,
        "工作模式 Agent / Plan / Ask；权限模式 默认权限 / 完全访问权限；复盘落点建议 Plan + 默认权限")

    evidence = [
        {"path": str(p), "mtime": stamp(p), "lines": line_count(p)} for p in recent
    ]
    return rows, evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only WorkBuddy environment probe for office-retro")
    parser.add_argument("--home", default=os.environ.get("WORKBUDDY_HOME") or str(Path.home() / ".workbuddy"))
    parser.add_argument("--workspace", default=os.environ.get("WORKBUDDY_WORKSPACE") or os.getcwd())
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--strict", action="store_true", help="exit 1 when any MISSING item is found")
    args = parser.parse_args()

    home = Path(args.home).expanduser()
    workspace = Path(args.workspace).expanduser()
    rows, evidence = probe(home, workspace)
    missing = [r["item"] for r in rows if r["status"] == MISSING]

    if args.json:
        print(json.dumps({
            "generatedAt": dt.datetime.now().isoformat(timespec="seconds"),
            "home": str(home),
            "workspace": str(workspace),
            "missing": missing,
            "checks": rows,
            "recentSessions": evidence,
        }, ensure_ascii=False, indent=2))
    else:
        print("# WorkBuddy 环境探测（office-retro）")
        print()
        print("- 生成时间：{}".format(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("- 配置根：`{}`".format(home))
        print("- 工作空间：`{}`".format(workspace))
        print("- 缺失项：{}".format("、".join(missing) if missing else "无"))
        print()
        print("| 检查项 | 状态 | 证据 |")
        print("|---|---|---|")
        for row in rows:
            print("| {} | {} | {} |".format(row["item"], row["status"], row["evidence"].replace("|", "\\|")))
        if evidence:
            print()
            print("## 最近会话记录（复盘步骤 1 的一手材料）")
            for item in evidence:
                print("- `{}` · {} · {} 行".format(item["path"], item["mtime"], item["lines"]))

    if args.strict and missing:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
