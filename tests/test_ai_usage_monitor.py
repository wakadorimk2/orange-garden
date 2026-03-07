"""Tests for scripts/ai_usage_monitor.py -- Issue #132"""

import json
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import ai_usage_monitor as mon


# --- _fmt_claude -------------------------------------------------------------


def test_fmt_claude_none():
    assert mon._fmt_claude(None) == "N/A"


def test_fmt_claude_zero_tokens():
    usage = {"total_tokens": 0, "input_tokens": 0, "output_tokens": 0, "source": "local"}
    assert "0 tokens" in mon._fmt_claude(usage)


def test_fmt_claude_with_values():
    usage = {
        "total_tokens": 5000,
        "input_tokens": 3000,
        "output_tokens": 2000,
        "source": "ccusage",
    }
    result = mon._fmt_claude(usage)
    assert "5,000 tokens" in result
    assert "ccusage" in result


# --- _fmt_codex --------------------------------------------------------------


def test_fmt_codex_none():
    assert mon._fmt_codex(None) == "N/A"


def test_fmt_codex_zero():
    # 0 と N/A を区別: ファイルは存在するが当日セッションなし
    assert "0 session" in mon._fmt_codex(0)


def test_fmt_codex_positive():
    assert "7 session" in mon._fmt_codex(7)


# --- get_claude_usage --------------------------------------------------------


def test_claude_via_local_read_error_returns_none(tmp_path):
    """ローカル JSONL が読めない場合は取得不能扱い (None)。"""
    projects_dir = tmp_path / ".claude" / "projects" / "p1"
    projects_dir.mkdir(parents=True)
    (projects_dir / "s1.jsonl").write_text("{}\n", encoding="utf-8")

    with (
        patch.object(Path, "home", return_value=tmp_path),
        patch.object(Path, "open", side_effect=OSError("permission denied")),
    ):
        assert mon._claude_via_local() is None


# --- get_codex_sessions ------------------------------------------------------


def test_get_codex_sessions_missing_dir(tmp_path):
    """~/.codex/history.jsonl が存在しない -> None"""
    with patch.object(Path, "home", return_value=tmp_path):
        assert mon.get_codex_sessions() is None


def test_get_codex_sessions_no_today(tmp_path):
    """ファイルは存在するが当日レコードなし -> 0"""
    codex_dir = tmp_path / ".codex"
    codex_dir.mkdir()
    hist = codex_dir / "history.jsonl"
    old_ts = 946684800  # 2000-01-01 00:00:00 UTC
    hist.write_text(
        json.dumps({"session_id": "s1", "ts": old_ts, "text": "x"}) + "\n",
        encoding="utf-8",
    )
    with patch.object(Path, "home", return_value=tmp_path):
        assert mon.get_codex_sessions() == 0


def test_get_codex_sessions_today(tmp_path):
    """当日に 2 つの session_id（1 つは重複）-> 2"""
    codex_dir = tmp_path / ".codex"
    codex_dir.mkdir()
    hist = codex_dir / "history.jsonl"
    now_ts = datetime.now().timestamp()
    records = [
        {"session_id": "sess-1", "ts": now_ts, "text": "a"},
        {"session_id": "sess-1", "ts": now_ts, "text": "b"},
        {"session_id": "sess-2", "ts": now_ts, "text": "c"},
    ]
    hist.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n",
        encoding="utf-8",
    )
    with patch.object(Path, "home", return_value=tmp_path):
        assert mon.get_codex_sessions() == 2


def test_get_codex_sessions_malformed_lines(tmp_path):
    """不正 JSON 行はスキップされ、正常行のみ集計される"""
    codex_dir = tmp_path / ".codex"
    codex_dir.mkdir()
    hist = codex_dir / "history.jsonl"
    now_ts = datetime.now().timestamp()
    hist.write_text(
        "not-json\n" + json.dumps({"session_id": "s1", "ts": now_ts, "text": "ok"}) + "\n",
        encoding="utf-8",
    )
    with patch.object(Path, "home", return_value=tmp_path):
        assert mon.get_codex_sessions() == 1
