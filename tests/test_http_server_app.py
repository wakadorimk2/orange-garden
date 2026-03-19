# tests/test_http_server_app.py
#
# /app/ static serving と SPA fallback の unit / integration テスト (#445)
# build artifact は fake_app_root fixture で hermetic に生成し、
# CI の pnpm build や git 管理外 artifact に依存しない。
from __future__ import annotations

import http.client
import json
import threading
from unittest.mock import patch

import pytest
from http.server import HTTPServer

from personal_mcp.adapters import http_server
from personal_mcp.adapters.http_server import _make_handler, _sanitize_subpath


# ─── _sanitize_subpath ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("", ""),
        ("/", ""),
        ("/index.html", "index.html"),
        ("assets/foo.js", "assets/foo.js"),
        ("/assets/foo.js", "assets/foo.js"),
        ("../etc/passwd", "etc/passwd"),
        ("/../etc/passwd", "etc/passwd"),
        ("a/../../b", "b"),
        ("a/../b", "b"),
        ("a/./b", "a/b"),
    ],
)
def test_sanitize_subpath(raw: str, expected: str) -> None:
    assert _sanitize_subpath(raw) == expected


# ─── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def fake_app_root(tmp_path_factory):
    """Minimal Vite build artifact tree for hermetic testing (pnpm build 不要)."""
    app_dir = tmp_path_factory.mktemp("app")
    (app_dir / "index.html").write_bytes(b"<!DOCTYPE html><html><body>app</body></html>")
    (app_dir / "assets").mkdir()
    (app_dir / "assets" / "main.js").write_bytes(b"console.log('main')")
    (app_dir / "assets" / "style.css").write_bytes(b"body { margin: 0; }")
    return app_dir


@pytest.fixture(scope="module", autouse=True)
def patch_app_root(fake_app_root):
    """_APP_ROOT をモジュール全体で fake_app_root に向ける。"""
    with patch.object(http_server, "_APP_ROOT", fake_app_root):
        yield fake_app_root


@pytest.fixture(scope="module")
def server_port(tmp_path_factory, patch_app_root):
    data_dir = str(tmp_path_factory.mktemp("data"))
    handler = _make_handler(data_dir)
    server = HTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    yield port
    server.shutdown()


def _get(port: int, path: str) -> http.client.HTTPResponse:
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.request("GET", path)
    return conn.getresponse()


# ─── /app/ serving (build exists) ─────────────────────────────────────────────


def test_app_root_serves_index_html(server_port: int) -> None:
    resp = _get(server_port, "/app/")
    assert resp.status == 200
    ct = resp.getheader("Content-Type", "")
    assert "text/html" in ct
    assert b"<!DOCTYPE html>" in resp.read()


def test_app_index_html_explicit(server_port: int) -> None:
    resp = _get(server_port, "/app/index.html")
    assert resp.status == 200
    assert b"<!DOCTYPE html>" in resp.read()


def test_app_no_trailing_slash(server_port: int) -> None:
    resp = _get(server_port, "/app")
    assert resp.status == 200
    assert b"<!DOCTYPE html>" in resp.read()


def test_app_assets_js(server_port: int) -> None:
    resp = _get(server_port, "/app/assets/main.js")
    assert resp.status == 200
    assert "javascript" in resp.getheader("Content-Type", "")


def test_app_assets_css(server_port: int) -> None:
    resp = _get(server_port, "/app/assets/style.css")
    assert resp.status == 200
    assert "css" in resp.getheader("Content-Type", "")


# ─── SPA fallback ─────────────────────────────────────────────────────────────


def test_app_spa_fallback_for_unknown_route(server_port: int) -> None:
    """拡張子なし未知パス → SPA fallback (200 index.html)。"""
    resp = _get(server_port, "/app/some-unknown-react-route")
    assert resp.status == 200
    assert "text/html" in resp.getheader("Content-Type", "")


def test_app_spa_fallback_for_html_extension(server_port: int) -> None:
    """.html 拡張子で存在しないパス → SPA fallback。"""
    resp = _get(server_port, "/app/nonexistent-page.html")
    assert resp.status == 200
    assert b"<!DOCTYPE html>" in resp.read()


def test_app_missing_asset_returns_404(server_port: int) -> None:
    """.js / .css などの asset パスが存在しない → 404 (SPA fallback しない)。"""
    for path in ("/app/assets/nonexistent.js", "/app/assets/nonexistent.css"):
        resp = _get(server_port, path)
        resp.read()  # drain
        assert resp.status == 404, f"expected 404 for {path}"


# ─── 503 when build missing ───────────────────────────────────────────────────


def test_app_503_when_no_build(tmp_path) -> None:
    handler = _make_handler(str(tmp_path))
    server = HTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever)
    t.daemon = True
    t.start()
    try:
        # 空ディレクトリを指すことで index.html が存在しない状態を再現
        with patch.object(http_server, "_APP_ROOT", tmp_path):
            resp = _get(port, "/app/")
            assert resp.status == 503
            body = json.loads(resp.read())
            assert "hint" in body
            assert "pnpm build" in body["hint"]
    finally:
        server.shutdown()


# ─── 既存ルートの非回帰 ───────────────────────────────────────────────────────


def test_health_route_unchanged(server_port: int) -> None:
    resp = _get(server_port, "/health")
    assert resp.status == 200


def test_unknown_route_still_404(server_port: int) -> None:
    resp = _get(server_port, "/not-a-real-path-xyz")
    assert resp.status == 404
