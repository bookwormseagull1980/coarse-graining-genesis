# -*- coding: utf-8 -*-
# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""
scripts/audit_path_portability.py -- Git portability audit
=========================================================

Reviewer-facing artifacts must not depend on one developer's workstation.
This audit scans source and generated reviewer files for machine-local,
drive-qualified paths, hard-coded user directories, or bundled-runtime
executables leaking into reports/HTML.

Generic commands such as `python scripts/...` or `lean.exe` are allowed.
Concrete local paths should be supplied by the user's environment (`PATH`,
`LEAN_EXE`, or `--lean-exe`) and should not be committed into reviewer
artifacts.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCAN_GLOBS = [
    "README.md",
    "REVIEWER_START_HERE.md",
    "V5_VERIFICATION_REPORT.md",
    "docs/*.html",
    "scripts/*.py",
    "tests/*.py",
]
FORBIDDEN = [
    re.compile(r"(?<![A-Za-z])[A-Za-z]:[\\/](?!/)"),
    re.compile(r"Users\\ROOT"),
    re.compile("lean" + "47"),
    re.compile(r"lean-4\.7\.0-windows"),
    re.compile(r"python\.exe"),
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def scanned_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted({p for p in files if p.is_file()})


def main() -> int:
    violations: list[tuple[str, int, str]] = []
    for path in scanned_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(rx.search(line) for rx in FORBIDDEN):
                violations.append((rel(path), lineno, line.strip()[:180]))

    if violations:
        print("PATH PORTABILITY AUDIT FAILED")
        for file, line, text in violations[:80]:
            print(f"  - {file}:{line}: {text}")
        if len(violations) > 80:
            print(f"  - ... {len(violations) - 80} more")
        return 1

    print("PATH PORTABILITY AUDIT CLEAN")
    print(f"  files scanned: {len(scanned_files())}")
    print("  no machine-local absolute paths in reviewer-facing sources/artifacts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
