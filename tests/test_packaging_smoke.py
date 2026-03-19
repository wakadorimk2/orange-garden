# tests/test_packaging_smoke.py
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def test_wheel_contains_dashboard_template_and_can_load_it(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = tmp_path / "dist"

    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(dist_dir),
        ],
        cwd=repo_root,
        check=True,
    )

    wheel_path = next(dist_dir.glob("*.whl"))
    with zipfile.ZipFile(wheel_path) as zf:
        names = set(zf.namelist())
        assert "personal_mcp/web/templates/dashboard.html" in names
        zf.extractall(tmp_path / "site")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path / "site")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from personal_mcp.adapters.http_server import load_dashboard_html; "
                "html = load_dashboard_html(); "
                "assert 'id=\"heatmap\"' in html; "
                "assert 'DASHBOARD_FALLBACK_CANDIDATES_JSON' in html"
            ),
        ],
        cwd=tmp_path,
        env=env,
        check=True,
    )

    assert result.returncode == 0


def test_app_root_traversable_resolves_from_installed_package(tmp_path: Path) -> None:
    """Documented web/app resource contract remains readable after wheel install."""
    repo_root = Path(__file__).resolve().parent.parent
    repo_copy = tmp_path / "repo"
    dist_dir = tmp_path / "dist"

    shutil.copytree(repo_root, repo_copy)

    app_dir = repo_copy / "src" / "personal_mcp" / "web" / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    expected_html = "<!DOCTYPE html><html><body>packaged app</body></html>"
    (app_dir / "index.html").write_text(expected_html, encoding="utf-8")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(dist_dir),
        ],
        cwd=repo_copy,
        check=True,
    )

    wheel_path = next(dist_dir.glob("*.whl"))
    with zipfile.ZipFile(wheel_path) as zf:
        zf.extractall(tmp_path / "site")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(tmp_path / "site")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from importlib.resources import files; "
                "index = files('personal_mcp').joinpath('web/app/index.html'); "
                "assert index.is_file(); "
                "text = index.read_text(encoding='utf-8'); "
                "assert 'packaged app' in text; "
                "print('ok')"
            ),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "ok" in result.stdout
