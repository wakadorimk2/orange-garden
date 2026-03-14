# tests/test_packaging_smoke.py
from __future__ import annotations

import os
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
