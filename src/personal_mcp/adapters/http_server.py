from __future__ import annotations

import json
import mimetypes
import os.path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse
from importlib.resources import files

from personal_mcp.tools.candidates import FIXED_CANDIDATES, list_candidates
from personal_mcp.tools.daily_summary import (
    count_events_by_date,
    count_events_by_date_debug,
    get_latest_summary,
    list_summaries,
)
from personal_mcp.tools.log_form import (
    event_add_sqlite,
    ui_event_add_sqlite,
)


def load_dashboard_html() -> str:
    return (
        files("personal_mcp.web.templates").joinpath("dashboard.html").read_text(encoding="utf-8")
    )


_DASHBOARD_HTML = load_dashboard_html().replace(
    "DASHBOARD_FALLBACK_CANDIDATES_JSON",
    json.dumps(list(FIXED_CANDIDATES), ensure_ascii=False),
)


_APP_ROOT = files("personal_mcp.web").joinpath("app")


def _sanitize_subpath(raw: str) -> str:
    """Return a safe relative path within app root, stripping traversal attempts."""
    parts: list[str] = []
    for part in raw.lstrip("/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
        else:
            parts.append(part)
    return "/".join(parts)


def _make_handler(data_dir: str):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            pass

        def _write_response(
            self, status: int, content_type: str, payload: bytes, *, charset: str | None = None
        ) -> None:
            try:
                self.send_response(status)
                header_value = content_type
                if charset:
                    header_value = f"{content_type}; charset={charset}"
                self.send_header("Content-Type", header_value)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                return

        def _serve_app(self, subpath: str) -> None:
            index = _APP_ROOT.joinpath("index.html")
            if not index.is_file():
                self._json(
                    503,
                    {"error": "frontend not built", "hint": "run pnpm build in frontend/ first"},
                )
                return
            target = _APP_ROOT
            for part in subpath.split("/"):
                if part:
                    target = target.joinpath(part)
            if target.is_file():
                fname = subpath.split("/")[-1] if subpath else "index.html"
            else:
                # Distinguish SPA routes (no ext / .html) from missing assets
                leaf = subpath.split("/")[-1] if subpath else ""
                _, ext = os.path.splitext(leaf)
                if ext and ext.lower() not in (".html", ".htm"):
                    # e.g. /app/assets/missing.js → 404, not SPA fallback
                    self._json(404, {"error": "not found"})
                    return
                # SPA fallback: extension-less or .html path → serve index.html
                target = index
                fname = "index.html"
            data = target.read_bytes()
            ct, _ = mimetypes.guess_type(fname)
            charset = "utf-8" if ct == "text/html" else None
            self._write_response(200, ct or "application/octet-stream", data, charset=charset)

        def _json(self, status: int, body: Any) -> None:
            payload = json.dumps(body, ensure_ascii=False).encode()
            self._write_response(status, "application/json", payload)

        def _read_json_body(self) -> Any:
            try:
                length = int(self.headers.get("Content-Length", 0))
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            try:
                return json.loads(self.rfile.read(length))
            except Exception as exc:
                raise ValueError("invalid JSON") from exc

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html", "/dashboard"):
                html = _DASHBOARD_HTML.encode("utf-8")
                self._write_response(200, "text/html", html, charset="utf-8")
            elif parsed.path == "/health":
                self._json(200, {"status": "ok"})
            elif parsed.path == "/summaries":
                params = parse_qs(parsed.query)
                date_vals = params.get("date", [])
                if not date_vals:
                    self._json(400, {"error": "date query param required"})
                    return
                rec = get_latest_summary(date_vals[0], data_dir or None)
                if rec is None:
                    self._json(404, {"error": "no summary for date"})
                else:
                    self._json(200, rec)
            elif parsed.path == "/api/heatmap":
                self._json(200, count_events_by_date(42, data_dir or None))
            elif parsed.path == "/api/heatmap/debug":
                self._json(200, count_events_by_date_debug(42, data_dir or None))
            elif parsed.path == "/api/candidates":
                self._json(200, list_candidates(data_dir or None))
            elif parsed.path == "/api/summaries/list":
                self._json(200, list_summaries(28, data_dir or None))
            elif parsed.path == "/app" or parsed.path.startswith("/app/"):
                subpath = _sanitize_subpath(parsed.path[len("/app") :])
                self._serve_app(subpath)
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self) -> None:
            if self.path not in ("/events", "/events/ui"):
                self._json(404, {"error": "not found"})
                return
            try:
                body = self._read_json_body()
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
                return
            if not isinstance(body, dict):
                self._json(400, {"error": "invalid JSON"})
                return

            if self.path == "/events/ui":
                event_name = (body.get("event_name") or "").strip()
                ui_mode = (body.get("ui_mode") or "").strip()
                extra_data = body.get("extra_data")
                if extra_data is not None and not isinstance(extra_data, dict):
                    self._json(400, {"error": "extra_data must be an object"})
                    return
                try:
                    record = ui_event_add_sqlite(
                        event_name=event_name,
                        ui_mode=ui_mode,
                        data_dir=data_dir or None,
                        extra_data=extra_data,
                    )
                except ValueError as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(201, record)
                return

            domain = (body.get("domain") or "").strip()
            kind = (body.get("kind") or "").strip()
            text = (body.get("text") or "").strip()
            annotation = (body.get("annotation") or "").strip() or None

            try:
                record = event_add_sqlite(
                    domain=domain or None,
                    kind=kind or None,
                    text=text,
                    annotation=annotation,
                    data_dir=data_dir or None,
                )
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
                return
            self._json(201, record)

    return _Handler


def serve(host: str = "0.0.0.0", port: int = 8080, data_dir: str = "") -> None:
    handler_cls = _make_handler(data_dir)
    server = ThreadingHTTPServer((host, port), handler_cls)
    print(f"serving on http://{host}:{port}  data_dir={data_dir or '(default)'}", flush=True)
    server.serve_forever()
