#!/usr/bin/env python3
"""
AI Usage Monitor -- Issue #132
Displays Claude/Codex daily usage every 5 minutes.
No required external dependencies (ccusage is optional).
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

INTERVAL = 300  # seconds (5 minutes)


def _today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def _today_date():
    return datetime.now().date()


# --- Claude -------------------------------------------------------------------


def _claude_via_ccusage():
    """Run ccusage daily --json for today. Returns parsed dict or None."""
    today = _today_str()
    try:
        result = subprocess.run(
            ["ccusage", "daily", "--since", today, "--until", today, "--json", "--offline"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        if isinstance(data, list):
            row = data[0] if data else {}
        elif isinstance(data, dict):
            rows = data.get("daily", [])
            row = rows[0] if rows else data
        else:
            return None
        return {
            "input_tokens": int(row.get("inputTokens", 0) or 0),
            "output_tokens": int(row.get("outputTokens", 0) or 0),
            "cache_creation_tokens": int(row.get("cacheCreationTokens", 0) or 0),
            "cache_read_tokens": int(row.get("cacheReadTokens", 0) or 0),
            "total_tokens": int(row.get("totalTokens", 0) or 0),
            "source": "ccusage",
        }
    except FileNotFoundError:
        return None  # ccusage not installed
    except Exception:
        return None


def _accumulate_jsonl(path: Path, today, totals: dict) -> bool:
    """Parse one JSONL file, adding today's assistant token counts into totals.
    Returns False if the file cannot be read."""
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("type") != "assistant":
                    continue
                ts_raw = record.get("timestamp", "")
                if not ts_raw:
                    continue
                try:
                    ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                    ts_local = ts.astimezone().date()
                except (ValueError, TypeError):
                    continue
                if ts_local != today:
                    continue
                usage = record.get("message", {}).get("usage", {})
                try:
                    totals["input"] += int(usage.get("input_tokens") or 0)
                    totals["output"] += int(usage.get("output_tokens") or 0)
                    totals["cache_creation"] += int(usage.get("cache_creation_input_tokens") or 0)
                    totals["cache_read"] += int(usage.get("cache_read_input_tokens") or 0)
                except (TypeError, ValueError):
                    pass
    except OSError:
        return False
    return True


def _claude_via_local():
    """Read ~/.claude/projects/**/*.jsonl and sum today's tokens.
    Returns None if the projects directory does not exist or cannot be fully read."""
    projects_dir = Path.home() / ".claude" / "projects"
    if not projects_dir.exists():
        return None
    today = _today_date()
    totals = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0}
    try:
        for jsonl in projects_dir.glob("*/*.jsonl"):
            if not _accumulate_jsonl(jsonl, today, totals):
                return None
        for jsonl in projects_dir.glob("*/*/subagents/*.jsonl"):
            if not _accumulate_jsonl(jsonl, today, totals):
                return None
    except Exception:
        return None
    return {
        "input_tokens": totals["input"],
        "output_tokens": totals["output"],
        "total_tokens": sum(totals.values()),
        "source": "local",
    }


def get_claude_usage():
    """Try ccusage first; fall back to local JSONL read."""
    result = _claude_via_ccusage()
    if result is not None:
        return result
    return _claude_via_local()


# --- Codex -------------------------------------------------------------------


def get_codex_sessions():
    """Count unique Codex sessions today from ~/.codex/history.jsonl.
    Returns None if the file is missing or unreadable.
    Returns 0 if readable but no sessions found today."""
    history_path = Path.home() / ".codex" / "history.jsonl"
    if not history_path.exists():
        return None
    today = _today_date()
    session_ids: set = set()
    try:
        with history_path.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts_raw = record.get("ts")
                if ts_raw is None:
                    continue
                try:
                    ts_local = datetime.fromtimestamp(float(ts_raw)).date()
                except (ValueError, OSError, OverflowError):
                    continue
                if ts_local != today:
                    continue
                sid = record.get("session_id")
                if sid:
                    session_ids.add(sid)
    except OSError:
        return None
    return len(session_ids)


# --- Rendering ----------------------------------------------------------------


def _fmt_claude(usage) -> str:
    if usage is None:
        return "N/A"
    total = usage.get("total_tokens", 0)
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    source = usage.get("source", "?")
    return f"{total:,} tokens  (in={inp:,}  out={out:,})  [via {source}]"


def _fmt_codex(sessions) -> str:
    if sessions is None:
        return "N/A"
    return f"{sessions} session(s) today"


def render(claude_usage, codex_sessions) -> None:
    now = datetime.now().strftime("%H:%M")
    os.system("clear")
    print(f"AI Usage Monitor  (updated: {now})")
    print()
    print("Claude usage (today)")
    print(f"  tokens  : {_fmt_claude(claude_usage)}")
    print()
    print("Codex usage (today)")
    print(f"  sessions: {_fmt_codex(codex_sessions)}")
    print()
    print(f"Next update in {INTERVAL // 60} min  |  Ctrl-C to quit")


# --- Entry point --------------------------------------------------------------


def main() -> None:
    try:
        while True:
            claude = get_claude_usage()
            codex = get_codex_sessions()
            render(claude, codex)
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()
