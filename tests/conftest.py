"""Shared fixtures for the checks in `scripts/`.

The checks are entry-point scripts rather than an importable package: their names contain
hyphens, and each is meant to be run. So they are loaded by path here, which is what makes
them testable at all — every one of them has a `main()` that *returns* an exit code instead
of calling `sys.exit`, so a test can call it and read the result rather than starting a
process and interpreting a status.

That has a second consequence worth stating, because it shapes what these tests can claim.
An in-process test exercises the check's logic and its reporting, but not the thing that
runs it: `python3 scripts/check-nav.py` is a different act from calling `main()`. The CI job
runs both, so that a check which passes when imported and fails when executed has somewhere
to show up.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


@pytest.fixture(scope="session")
def load_check():
    """Load one of the checks in `scripts/` as a module, by its file name."""

    def _load(stem: str):
        name = stem.replace("-", "_")
        if name in sys.modules:
            return sys.modules[name]
        spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{stem}.py")
        assert spec is not None and spec.loader is not None, stem
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    return _load


@pytest.fixture
def make_tree(tmp_path):
    """Build a throwaway tree of files and return its root."""

    def _make(files: dict[str, str], root: Path | None = None) -> Path:
        where = root or tmp_path
        for name, content in files.items():
            path = where / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return where

    return _make
