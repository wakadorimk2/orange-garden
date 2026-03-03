# src/personal_mcp/tools/event.py
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from personal_mcp.core.event import Event
from personal_mcp.storage.jsonl import append_jsonl


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def event_add(
    domain: str,
    text: str,
    tags: Optional[List[str]] = None,
    meta: Optional[Dict[str, Any]] = None,
    data_dir: str = "data",
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"text": text}
    if meta:
        payload["meta"] = meta

    event = Event(
        ts=_now_iso(),
        domain=domain,
        payload=payload,
        tags=tags or [],
    )

    path = Path(data_dir) / "events.jsonl"
    record = asdict(event)
    append_jsonl(path, record)
    return record
