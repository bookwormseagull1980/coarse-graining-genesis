# -*- coding: utf-8 -*-
"""V5 independence guard: no runtime/verification dependency on the Lean branch."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = (
    "foundations-reference.json",
    "verify_foundations",
    "--foundations",
    "FOUNDATIONS_PROJECT",
)


def test_no_external_lean_foundations_references():
    paths = [ROOT / "README.md", ROOT / "REVIEWER_START_HERE.md",
             ROOT / "pyproject.toml", ROOT / "scripts", ROOT / "tests"]
    offenders = []
    for path in paths:
        files = [path] if path.is_file() else path.rglob("*")
        for item in files:
            if item == Path(__file__).resolve():
                continue
            if not item.is_file() or item.suffix not in {".py", ".md", ".toml"}:
                continue
            text = item.read_text(encoding="utf-8", errors="replace")
            for token in FORBIDDEN:
                if token in text:
                    offenders.append(f"{item.relative_to(ROOT)}: {token}")
    assert not offenders, "\n".join(offenders)
