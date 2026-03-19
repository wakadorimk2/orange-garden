from __future__ import annotations

import os
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info


class BuildPyWithFrontendCheck(build_py):
    def run(self) -> None:
        sentinel = os.path.join(
            os.path.dirname(__file__),
            "src", "personal_mcp", "web", "app", "index.html",
        )
        if not os.path.isfile(sentinel):
            raise RuntimeError(
                "frontend build missing: run pnpm build in frontend/ first"
            )
        super().run()


class EggInfoWithFrontendCheck(egg_info):
    def run(self) -> None:
        sentinel = os.path.join(
            os.path.dirname(__file__),
            "src", "personal_mcp", "web", "app", "index.html",
        )
        if not os.path.isfile(sentinel):
            raise RuntimeError(
                "frontend build missing: run pnpm build in frontend/ first"
            )
        super().run()


setup(
    cmdclass={
        "build_py": BuildPyWithFrontendCheck,
        "egg_info": EggInfoWithFrontendCheck,
    }
)
