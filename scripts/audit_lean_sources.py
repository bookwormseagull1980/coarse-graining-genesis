# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#
#  DOI records:
#    [Software] 10.5281/zenodo.22067006
#    [Paper I]  10.5281/zenodo.22067118
#    [Paper II] 10.5281/zenodo.22067469
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#         DOI: 10.5281/zenodo.22067118
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
#         DOI: 10.5281/zenodo.22067469
# =============================================================================

"""
scripts/audit_lean_sources.py -- Lean proof-source hygiene audit
================================================================

This is a lightweight reviewer check for the Lean archive.  It does not
replace compiling the proofs with Lean 4 (`verify_v4.py --lean`), but it
does make the most important proof-hygiene boundary mechanical:

  * no `sorry`;
  * no `admit`;
  * no explicit `axiom`;
  * no `unsafe`;
  * no `opaque`;
  * no interactive output commands (`#eval`, `#reduce`, `#print`, `#check`);
  * no Mathlib import.

The scanner strips Lean line comments and nested block comments before
matching tokens, so explanatory prose may still mention axioms.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LEAN_ROOT = ROOT / "lean_proofs"
FORBIDDEN_TOKEN = re.compile(r"\b(sorry|admit|axiom|unsafe|opaque)\b")
OUTPUT_COMMAND = re.compile(r"^\s*#(eval|reduce|print|check)\b", re.MULTILINE)
MATHLIB_IMPORT = re.compile(r"^\s*import\s+Mathlib\b", re.MULTILINE)


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def strip_comments_preserve_lines(text: str) -> tuple[str, int]:
    """Remove Lean comments while preserving line numbers.

    Lean block comments can be nested.  Replacing comment bodies by their
    newlines keeps violation line numbers useful without parsing Lean.
    """
    out: list[str] = []
    i = 0
    depth = 0
    n = len(text)
    while i < n:
        two = text[i:i + 2]
        if depth == 0 and two == "--":
            while i < n and text[i] != "\n":
                i += 1
            if i < n:
                out.append("\n")
                i += 1
            continue
        if depth == 0 and two == "/-":
            depth = 1
            i += 2
            continue
        if depth > 0:
            if two == "/-":
                depth += 1
                i += 2
                continue
            if two == "-/":
                depth -= 1
                i += 2
                continue
            if text[i] == "\n":
                out.append("\n")
            i += 1
            continue
        out.append(text[i])
        i += 1
    return "".join(out), depth


def strip_strings_preserve_lines(text: str) -> str:
    out: list[str] = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if not in_string:
            if ch == '"':
                in_string = True
                out.append('"')
            else:
                out.append(ch)
            i += 1
            continue
        if ch == "\\":
            i += 2
            continue
        if ch == '"':
            in_string = False
            out.append('"')
        elif ch == "\n":
            out.append("\n")
        i += 1
    return "".join(out)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def audit_file(path: Path) -> list[tuple[str, int, str]]:
    text = path.read_text(encoding="utf-8")
    stripped, open_depth = strip_comments_preserve_lines(text)
    code = strip_strings_preserve_lines(stripped)
    violations: list[tuple[str, int, str]] = []

    if open_depth:
        violations.append((rel(path), code.count("\n") + 1, "unclosed block comment"))

    for match in FORBIDDEN_TOKEN.finditer(code):
        violations.append((rel(path), line_number(code, match.start()), match.group(1)))

    for match in OUTPUT_COMMAND.finditer(code):
        violations.append((rel(path), line_number(code, match.start()), match.group(0).strip()))

    for match in MATHLIB_IMPORT.finditer(code):
        violations.append((rel(path), line_number(code, match.start()), "Mathlib import"))

    return violations


def main() -> int:
    files = sorted(LEAN_ROOT.glob("*.lean"))
    if not files:
        print("LEAN SOURCE AUDIT: no lean_proofs/*.lean files found")
        return 1

    violations: list[tuple[str, int, str]] = []
    for path in files:
        violations.extend(audit_file(path))

    if violations:
        print(f"LEAN SOURCE AUDIT: {len(violations)} violation(s)")
        for file, line, token in violations:
            print(f"  - {file}:{line}: {token}")
        return 1

    print("LEAN SOURCE AUDIT CLEAN")
    print(f"  files scanned: {len(files)}")
    print("  no sorry/admit/axiom/unsafe/opaque tokens in executable Lean code")
    print("  no interactive output commands")
    print("  no Mathlib imports")
    return 0


if __name__ == "__main__":
    sys.exit(main())
