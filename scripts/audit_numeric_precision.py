# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
scripts/audit_numeric_precision.py -- precision discipline audit
================================================================

The V4 chain has many exponentially or hierarchically sensitive quantities.
This audit checks the mechanical precision boundary:

  * persisted parameter values must not be rounded or formatted before being
    written by pset()/compare_and_set()/sm_set();
  * non-informational numeric values must be stored as JSON numbers, not as
    formatted numeric strings;
  * high-fanout numeric parameters are reported with their round-trip Python
    representation so reviewers can see that downstream inputs are full float
    values rather than display strings.

The audit does not judge the physics; it verifies that the code path preserves
numeric precision across the generated stores.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = ("cg_core", "cg_frg", "scripts", "comparison")
WRITE_CALLS = {"pset", "set", "record", "compare_and_set", "sm_set"}
PRECISION_LOSS_CALLS = {"round", "format"}
NUMERIC_STRING = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$"
)
INFO_KEY = re.compile(
    r"(status|verdict|spectrum|tower|layers|coeffs|emergence|language|robust)$"
)
SELECTED_KEYS = [
    "kL", "M_G", "k_GUT", "g2_MG", "g1_MG_geo", "g3_MG_geo",
    "alpha_inv_MZ_pred", "alpha_s_MZ_pred", "v_HIGGS", "M_Z_pred",
    "M_W_pred", "M_W_pred_lead1loop", "Gamma_b_pred_1loop",
    "sin2_theta_eff_l_pred", "m_t_pred", "m_b_pred", "m_e_pred",
    "qcd_Lambda_QCD", "rho_Lambda", "H0_GEV", "Omega_Lambda",
    "T_CMB_GeV", "bbn_Neff",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def first_string_arg(node: ast.Call) -> str | None:
    if node.args and isinstance(node.args[0], ast.Constant) and \
            isinstance(node.args[0].value, str):
        return node.args[0].value
    return None


def keyword_string(node: ast.Call, name: str) -> str | None:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant) and \
                isinstance(keyword.value.value, str):
            return keyword.value.value
    return None


def informational_write(node: ast.Call, key: str) -> bool:
    role = keyword_string(node, "role")
    return role == "informational" or bool(INFO_KEY.search(key))


def contains_precision_loss(node: ast.AST, tainted: set[str]) -> bool:
    if isinstance(node, ast.Name):
        return node.id in tainted
    if isinstance(node, ast.JoinedStr):
        return True
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        return True
    if isinstance(node, ast.Call):
        name = call_name(node.func)
        if name in PRECISION_LOSS_CALLS:
            return True
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            return True
        if name in {"float", "int"} and node.args:
            arg = node.args[0]
            if isinstance(arg, (ast.Constant, ast.JoinedStr)) and \
                    not isinstance(getattr(arg, "value", None), (int, float)):
                return True
    return any(contains_precision_loss(child, tainted)
               for child in ast.iter_child_nodes(node))


class PrecisionWriteScan(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.tainted: set[str] = set()
        self.violations: list[tuple[str, int, str]] = []

    def _target_names(self, target: ast.AST) -> list[str]:
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, (ast.Tuple, ast.List)):
            names: list[str] = []
            for elt in target.elts:
                names.extend(self._target_names(elt))
            return names
        return []

    def visit_Assign(self, node: ast.Assign) -> None:
        names = []
        for target in node.targets:
            names.extend(self._target_names(target))
        if contains_precision_loss(node.value, self.tainted):
            self.tainted.update(names)
        else:
            self.tainted.difference_update(names)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        names = self._target_names(node.target)
        if node.value is not None and contains_precision_loss(node.value, self.tainted):
            self.tainted.update(names)
        else:
            self.tainted.difference_update(names)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        if name in WRITE_CALLS and len(node.args) >= 2:
            key = first_string_arg(node) or "<dynamic key>"
            value_arg = node.args[1]
            if not informational_write(node, key) and \
                    contains_precision_loss(value_arg, self.tainted):
                self.violations.append((
                    rel(self.path),
                    node.lineno,
                    f"{name}({key!r}, ...) writes a rounded/formatted value",
                ))
        self.generic_visit(node)


class DependencyScan(ast.NodeVisitor):
    def __init__(self) -> None:
        self.reads: set[str] = set()
        self.writes: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        name = call_name(node.func)
        key = first_string_arg(node)
        if key:
            if name == "get":
                self.reads.add(key)
            elif name in WRITE_CALLS:
                self.writes.add(key)
        self.generic_visit(node)


def python_files() -> list[Path]:
    files: list[Path] = []
    for dirname in SCAN_DIRS:
        base = ROOT / dirname
        if base.exists():
            files.extend(sorted(base.rglob("*.py")))
    return files


def scan_precision_writes() -> list[tuple[str, int, str]]:
    violations: list[tuple[str, int, str]] = []
    for path in python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        visitor = PrecisionWriteScan(path)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    return sorted(violations)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing generated store: {rel(path)}")
    return json.loads(path.read_text(encoding="utf-8"))


def scan_store_numeric_strings(store_path: Path) -> list[str]:
    data = load_json(store_path)
    params = data.get("parameters", {})
    violations: list[str] = []
    for key, rec in sorted(params.items()):
        if not isinstance(rec, dict):
            continue
        value = rec.get("value")
        role = rec.get("role", "")
        if role != "informational" and isinstance(value, str) and \
                NUMERIC_STRING.match(value.strip()):
            violations.append(f"{rel(store_path)}:{key}: numeric value stored as string")
    return violations


def dependency_graph() -> dict[str, set[str]]:
    module_reads: dict[str, set[str]] = {}
    module_writes: dict[str, set[str]] = {}
    for path in python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        scan = DependencyScan()
        scan.visit(tree)
        if scan.reads or scan.writes:
            module = rel(path)
            module_reads[module] = scan.reads
            module_writes[module] = scan.writes

    graph: dict[str, set[str]] = defaultdict(set)
    for module, reads in module_reads.items():
        writes = module_writes.get(module, set())
        for read_key in reads:
            graph[read_key].update(writes)
    return graph


def descendants(graph: dict[str, set[str]], key: str) -> set[str]:
    seen: set[str] = set()
    stack = list(graph.get(key, set()))
    while stack:
        item = stack.pop()
        if item in seen:
            continue
        seen.add(item)
        stack.extend(graph.get(item, set()) - seen)
    return seen


def high_fanout_report() -> list[str]:
    cg = load_json(ROOT / "cg_params.json").get("parameters", {})
    graph = dependency_graph()
    rows: list[tuple[int, str, Any]] = []
    for key, rec in cg.items():
        if not isinstance(rec, dict):
            continue
        value = rec.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        fanout = len(descendants(graph, key))
        if fanout >= 5 or key in SELECTED_KEYS:
            rows.append((fanout, key, value))
    rows.sort(key=lambda row: (-row[0], row[1]))
    lines = []
    for fanout, key, value in rows[:30]:
        lines.append(f"    {key}: {repr(value)}  downstream={fanout}")
    return lines


def main() -> int:
    violations = scan_precision_writes()
    store_violations = []
    store_violations.extend(scan_store_numeric_strings(ROOT / "cg_params.json"))
    store_violations.extend(scan_store_numeric_strings(ROOT / "comparison" / "sm_inputs.json"))

    if violations or store_violations:
        print("NUMERIC PRECISION AUDIT FAILED")
        for file, line, message in violations:
            print(f"  - {file}:{line}: {message}")
        for item in store_violations:
            print(f"  - {item}")
        return 1

    cg = load_json(ROOT / "cg_params.json").get("parameters", {})
    numeric_count = sum(
        1 for rec in cg.values()
        if isinstance(rec, dict) and isinstance(rec.get("value"), (int, float))
        and not isinstance(rec.get("value"), bool)
    )
    print("NUMERIC PRECISION AUDIT CLEAN")
    print(f"  python files scanned: {len(python_files())}")
    print("  no rounded/formatted values are written to parameter stores")
    print("  non-informational numeric records are JSON numbers, not strings")
    print(f"  numeric cg_params records: {numeric_count}")
    print("  high-fanout stored values use round-trip representations:")
    for line in high_fanout_report():
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
