# src/personal_mcp/tools/poe2_log.py
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from personal_mcp.storage.jsonl import append_jsonl


def _now_iso() -> str:
    # JST運用でもISOはUTCにしておくと後で楽（表示でJSTに変換すればOK）
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Poe2Log:
    ts: str
    kind: str
    text: str
    tags: List[str]
    meta: Dict[str, Any]


def log_add(
    text: str,
    kind: str = "note",
    tags: Optional[List[str]] = None,
    meta: Optional[Dict[str, Any]] = None,
    data_dir: str = "data",
) -> Poe2Log:
    record = Poe2Log(
        ts=_now_iso(),
        kind=kind,
        text=text.strip(),
        tags=tags or [],
        meta=meta or {},
    )

    path = Path(data_dir) / "poe2" / "logs.jsonl"
    append_jsonl(path, asdict(record))
    return record