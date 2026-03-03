import json
from pathlib import Path

from personal_mcp.tools.event import event_add


def test_event_add_creates_jsonl_with_one_line(data_dir: Path) -> None:
    path = data_dir / "events.jsonl"
    event_add(domain="poe2", text="test", data_dir=str(data_dir))

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["domain"] == "poe2"
    assert record["payload"]["text"] == "test"


def test_event_add_appends_without_overwriting(data_dir: Path) -> None:
    path = data_dir / "events.jsonl"
    path.write_text('{"dummy": true}\n', encoding="utf-8")

    event_add(domain="mood", text="second", data_dir=str(data_dir))

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"dummy": True}
    record = json.loads(lines[1])
    assert record["domain"] == "mood"
    assert record["payload"]["text"] == "second"
