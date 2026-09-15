from collections.abc import Callable
from pathlib import Path
from textwrap import dedent

import pytest

from gym_tracker.analysis import SCHEMAS

WriteLog = Callable[..., Path]


@pytest.fixture
def write_log(tmp_path: Path) -> WriteLog:
    """Write a training log to a temp dir; pass CSV rows (without header) per table."""

    def _write(**tables: str) -> Path:
        unknown = set(tables) - set(SCHEMAS)
        if unknown:
            raise KeyError(f"Unknown tables: {sorted(unknown)}")
        for name, schema in SCHEMAS.items():
            rows = dedent(tables.get(name, "")).strip()
            content = ",".join(schema) + "\n" + (rows + "\n" if rows else "")
            (tmp_path / f"{name}.csv").write_text(content, encoding="utf-8")
        return tmp_path

    return _write
