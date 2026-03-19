# tests/test_packaging_smoke.py
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def _copy_repo(tmp_path: Path) -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    repo_copy = tmp_path / "repo"
    shutil.copytree(repo_root, repo_copy)
    return repo_copy


def _write_frontend_index(
    repo_root: Path,
    html: str = "<!DOCTYPE html><html><body>app</body></html>",
) -> None:
    app_dir = repo_root / "src" / "personal_mcp" / "web" / "app"
    app_dir.mkdir(parents=True, exist_ok=True)
    (app_dir / "index.html").write_text(html, encoding="utf-8")


def _build_wheel(
    repo_root: Path, dist_dir: Path, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
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
        capture_output=True,
        text=True,
        check=check,
    )


def test_wheel_contains_dashboard_template_and_can_load_it(tmp_path: Path) -> None:
    repo_root = _copy_repo(tmp_path)
    dist_dir = tmp_path / "dist"
    _write_frontend_index(repo_root)

    result = _build_wheel(repo_root, dist_dir)

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
    repo_copy = _copy_repo(tmp_path)
    dist_dir = tmp_path / "dist"

    expected_html = "<!DOCTYPE html><html><body>packaged app</body></html>"
    _write_frontend_index(repo_copy, expected_html)

    _build_wheel(repo_copy, dist_dir)

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


def test_build_fails_with_hint_when_frontend_artifact_is_missing(tmp_path: Path) -> None:
    repo_copy = _copy_repo(tmp_path)
    dist_dir = tmp_path / "dist"

    shutil.rmtree(repo_copy / "src" / "personal_mcp" / "web" / "app", ignore_errors=True)
    shutil.rmtree(repo_copy / "build", ignore_errors=True)

    result = _build_wheel(repo_copy, dist_dir, check=False)

    assert result.returncode != 0
    assert "run pnpm build in frontend/ first" in (result.stderr + result.stdout)
