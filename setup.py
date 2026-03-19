from __future__ import annotations

from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

FRONTEND_INDEX = (
    Path(__file__).resolve().parent / "src" / "personal_mcp" / "web" / "app" / "index.html"
)
FRONTEND_ASSETS_DIR = FRONTEND_INDEX.parent / "assets"


def ensure_frontend_artifact() -> None:
    if not FRONTEND_INDEX.is_file():
        raise RuntimeError("frontend build missing: run pnpm build in frontend/ first")
    if not FRONTEND_ASSETS_DIR.is_dir() or not any(
        path.is_file() for path in FRONTEND_ASSETS_DIR.rglob("*")
    ):
        raise RuntimeError("frontend build missing: run pnpm build in frontend/ first")


class BuildPyWithFrontendCheck(build_py):
    def run(self) -> None:
        ensure_frontend_artifact()
        super().run()


class SdistWithFrontendCheck(sdist):
    def run(self) -> None:
        ensure_frontend_artifact()
        super().run()


setup(
    cmdclass={
        "build_py": BuildPyWithFrontendCheck,
        "sdist": SdistWithFrontendCheck,
    }
)
