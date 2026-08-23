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
scripts/audit_observation_leakage.py -- V4.0 observation-isolation audit
========================================================================

The V4 reproducibility claim is only meaningful if observed Standard
Model values cannot silently enter the prediction chain.  This audit
therefore scans the Python source for explicit observation-access APIs:

    sm_value(...)
    get_observed(...)

and allows them only in documented comparison-only contexts:

  * the comparison package itself;
  * scripts/init_v4.py when it builds the SM comparison table;
  * cg_frg/ewsb/ew_precision.py and cg_frg/ewsb/ew_one_loop.py when the
    value is used as a compare_and_set target, a comparison-level table
    column, or in the formula-check/printout block.

Any new use outside these contexts is reported as a violation.  The
script is intentionally conservative: it is not a full taint analyzer,
but it pins the explicit API boundary reviewers care about.
"""

from __future__ import annotations

import ast
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WATCHED = {"sm_value", "get_observed"}
SCAN_DIRS = ("cg_core", "cg_frg", "scripts", "comparison")


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def first_string_arg(node: ast.Call) -> str:
    if node.args and isinstance(node.args[0], ast.Constant) and \
            isinstance(node.args[0].value, str):
        return node.args[0].value
    return "?"


def has_ancestor_call(node: ast.AST, name: str) -> bool:
    parent = getattr(node, "_parent", None)
    while parent is not None:
        if isinstance(parent, ast.Call) and call_name(parent.func) == name:
            return True
        parent = getattr(parent, "_parent", None)
    return False


class ObservationVisitor(ast.NodeVisitor):
    def __init__(self, path: Path):
        self.path = path
        self.rel = rel(path)
        self.functions: list[str] = []
        self.allowed: list[tuple[int, str, str, str]] = []
        self.violations: list[tuple[int, str, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(node.name)
        self.generic_visit(node)
        self.functions.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        if name in WATCHED:
            key = first_string_arg(node)
            reason = self.allowed_reason(node, name, key)
            if reason:
                self.allowed.append((node.lineno, name, key, reason))
            else:
                where = ".".join(self.functions) or "<module>"
                self.violations.append(
                    (node.lineno, name, f"{key} in {where}")
                )
        self.generic_visit(node)

    def allowed_reason(self, node: ast.Call, name: str, key: str) -> str | None:
        if self.rel.startswith("comparison/"):
            return "comparison package"

        if self.rel == "scripts/init_v4.py" and name == "sm_value" and \
                key in {"M_Z", "v_HIGGS"}:
            return "SM comparison-table construction"

        if self.rel in {
            "cg_frg/ewsb/ew_precision.py",
            "cg_frg/ewsb/ew_one_loop.py",
        } and name == "sm_value":
            current = self.functions[-1] if self.functions else ""
            if has_ancestor_call(node, "compare_and_set"):
                return "compare_and_set observed target"
            if self.rel.endswith("ew_one_loop.py") and \
                    has_ancestor_call(node, "level_table"):
                return "one-loop level table comparison column"
            if current in {"formula_check", "main"}:
                return "formula check / printout only"

        return None


def parse_with_parents(path: Path) -> ast.Module:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "_parent", parent)
    return tree


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for dirname in SCAN_DIRS:
        root = ROOT / dirname
        if root.exists():
            files.extend(sorted(root.rglob("*.py")))
    return files


def main() -> int:
    all_allowed: list[tuple[str, int, str, str, str]] = []
    all_violations: list[tuple[str, int, str, str]] = []

    for path in iter_python_files():
        tree = parse_with_parents(path)
        visitor = ObservationVisitor(path)
        visitor.visit(tree)
        all_allowed.extend(
            (visitor.rel, line, name, key, reason)
            for line, name, key, reason in visitor.allowed
        )
        all_violations.extend(
            (visitor.rel, line, name, detail)
            for line, name, detail in visitor.violations
        )

    if all_violations:
        print(f"OBSERVATION-LEAKAGE AUDIT: {len(all_violations)} violation(s)")
        for file, line, name, detail in all_violations:
            print(f"  - {file}:{line}: {name}({detail})")
        print("\nAllowed contexts are documented in this script's module docstring.")
        return 1

    reasons = Counter(reason for *_rest, reason in all_allowed)
    print("OBSERVATION-LEAKAGE AUDIT CLEAN")
    print(f"  explicit observation-access calls: {len(all_allowed)}")
    for reason, count in sorted(reasons.items()):
        print(f"  {count:3d} allowed as {reason}")
    print("  no observed-value access was found in an unapproved prediction context.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
