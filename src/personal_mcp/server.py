# src/personal_mcp/server.py
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List, Optional

from personal_mcp.adapters.mcp_server import get_system_context
from personal_mcp.tools.poe2_log import log_add


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="personal-mcp")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info", help="print loaded context length")

    p_log = sub.add_parser("poe2-log-add", help="append a poe2 log entry")
    p_log.add_argument("text", help="log text")
    p_log.add_argument("--kind", default="note")
    p_log.add_argument("--tags", default="")
    p_log.add_argument("--meta-json", default="{}")
    p_log.add_argument("--data-dir", default="data")

    args = parser.parse_args(argv)

    if args.cmd == "info":
        text = get_system_context()
        print(f"loaded system context: {len(text)} chars")
        return 0

    if args.cmd == "poe2-log-add":
        tags = [t for t in args.tags.split(",") if t]
        meta: Dict[str, Any] = json.loads(args.meta_json)
        rec = log_add(
            text=args.text,
            kind=args.kind,
            tags=tags,
            meta=meta,
            data_dir=args.data_dir,
        )
        print(json.dumps(rec.__dict__, ensure_ascii=False, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())