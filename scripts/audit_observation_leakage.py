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
scripts/audit_observation_leakage.py -- V5.0 observation-isolation audit
========================================================================

The V5 reproducibility claim is only meaningful if observed Standard
Model values cannot silently enter the prediction chain.  This audit
therefore scans the Python source for explicit observation-access APIs:

    sm_value(...)
    get_observed(...)
    published_sm_value(...)
    published_record(...)
    read_store_document(store="references")

and allows them only in documented comparison-only contexts:

  * the comparison package itself;
  * scripts/init_v5.py when it builds the SM comparison table;
  * cg_frg/ewsb/ew_precision.py and cg_frg/ewsb/ew_one_loop.py when the
    value is used as a compare_and_set target, a comparison-level table
    column, or in the formula-check/printout block.
  * the named cosmological comparison readers and comparison commands,
    for the registered CAMB, DESI and SPARC records.
  * reference-document reads in the named verification, reproduction
    fingerprint and presentation functions.

Comparison data may be written to the separate reference store or to an explicit
role="comparison" record. The analysis propagates comparison sources
through assignments, supported container mutations, and return summaries
of the scanned Python modules. Reads of known comparison diagnostics are
checked separately from computed values accompanied by observed targets.

This is a finite source analysis of the registered API boundary. Dynamic
imports, reflection, arbitrary file readers and general Python control-flow
dependence are outside its supported language. Runtime input guards and
the stated production negative controls supply complementary checks.
"""

from __future__ import annotations

import ast
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
WATCHED = {"sm_value", "get_observed", "published_sm_value", "published_record"}
SCAN_DIRS = ("cg_core", "cg_frg", "scripts", "comparison")

# These identify the read operation and its function, rather than exempting
# a whole module containing both production and comparison calculations.
COMPARISON_READS = {
    ("scripts/init_v5.py", "init", "published_sm_value"):
        {"key"},
    ("scripts/reproduce_v5.py", "summary", "sm_value"):
        {"reference_key"},
    ("cg_frg/cosmology/camb_interface.py", "current_camb_record", "published_record"):
        {"CAMB_RECORD_KEY", "endpoint_camb_record"},
    ("cg_frg/cosmology/camb_interface.py", "current_bao_record", "published_sm_value"):
        {"BAO_DATA_KEY", "DESI_DR2_BAO"},
    ("cg_frg/cosmology/endpoint_residual.py", "current_sparc_record", "published_sm_value"):
        {"SPARC_DATA_KEY", "SPARC_MASS_MODELS"},
    ("cg_frg/cosmology/endpoint_residual.py", "compute", "published_sm_value"):
        {"BAO_DATA_KEY", "SPARC_DATA_KEY", "DESI_DR2_BAO", "SPARC_MASS_MODELS"},
    ("scripts/run_bao_comparison.py", "main", "sm_value"):
        {"BAO_DATA_KEY", "DESI_DR2_BAO"},
    ("scripts/run_explicit_camb.py", "main", "sm_value"):
        {"CAMB_PROPAGATION_SETTINGS"},
    ("scripts/validate_endpoint_cosmology.py", "run_bao", "sm_value"):
        {"BAO_DATA_KEY", "DESI_DR2_BAO"},
    ("scripts/validate_endpoint_cosmology.py", "registered_scale_diagnostic", "sm_value"):
        {"BAO_DATA_KEY", "DESI_DR2_BAO", "CMB_MONOPOLE"},
    ("scripts/validate_endpoint_cosmology.py", "run_sparc", "sm_value"):
        {"SPARC_DATA_KEY", "SPARC_MASS_MODELS"},
}
COMPARISON_READERS = {"current_camb_record", "current_bao_record", "current_sparc_record"}
REFERENCE_DOCUMENT_READERS = {
    ("scripts/reproduce_v5.py", "external_input_fingerprints"),
    ("scripts/verify_v5.py", "store_summary"),
    ("scripts/audit_numeric_stability.py", "load_records"),
    ("scripts/make_reviewer_dashboard.py", "load_json"),
}
CONTAINER_MUTATIONS = {"append", "extend", "insert", "update", "setdefault", "__setitem__"}


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
    def __init__(self, path: Path, *, return_summaries=(), comparison_records=()):
        self.path = path
        self.rel = rel(path)
        self.functions: list[str] = []
        self.allowed: list[tuple[int, str, str, str]] = []
        self.violations: list[tuple[int, str, str]] = []
        self.aliases = {name: name for name in WATCHED}
        self.aliases.update({"pset": "set", "compare_and_set": "compare_and_set"})
        self.tainted_returns = {"formula_check", *COMPARISON_READERS}
        self.return_summaries = set(return_summaries)
        self.comparison_records = set(comparison_records)
        self.module = self.rel.removesuffix(".py").replace("/", ".")
        self.constants = {}

    def resolved(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Attribute):
            base = self.resolved(node.value)
            if base and (base in SCAN_DIRS or base.startswith(
                    ("comparison.", "cg_core.", "cg_frg.", "scripts."))):
                qualified = base+"."+node.attr
                return node.attr if base == "cg_core.params" else qualified
        name = call_name(node)
        return self.aliases.get(name, name)

    def prepare_module(self, node: ast.Module) -> None:
        for part in ast.walk(node):
            if isinstance(part, ast.ImportFrom):
                self.visit_ImportFrom(part)
            elif isinstance(part, ast.Import):
                self.visit_Import(part)
            elif (isinstance(part, ast.Assign) and isinstance(part.value, ast.Constant)
                  and isinstance(part.value.value, str)):
                for target in part.targets:
                    if isinstance(target, ast.Name):
                        self.constants[target.id] = part.value.value

    def infer_returns(self, node: ast.Module) -> None:
        functions = [part for part in ast.walk(node)
                     if isinstance(part, (ast.FunctionDef, ast.AsyncFunctionDef))]
        changed = True
        while changed:
            changed = False
            for function in functions:
                if function.name in self.tainted_returns:
                    continue
                names = self.tainted_names(function)
                if any(isinstance(part, ast.Return) and part.value is not None
                       and self.tainted(part.value, names) for part in ast.walk(function)):
                    self.tainted_returns.add(function.name)
                    changed = True

    def visit_Module(self, node: ast.Module) -> None:
        self.prepare_module(node)
        self.infer_returns(node)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if node.level:
            module = ".".join(self.module.split(".")[:-node.level]+([module] if module else []))
        for alias in node.names:
            qualified = module+"."+alias.name
            self.aliases[alias.asname or alias.name] = (
                alias.name if module == "cg_core.params" or alias.name in WATCHED
                or (module in {"cg_frg.cosmology.camb_interface", "cg_frg.cosmology.endpoint_residual"}
                    and alias.name in COMPARISON_READERS)
                else qualified)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.aliases[alias.asname or alias.name.split(".")[0]] = (
                alias.name if alias.asname else alias.name.split(".")[0])

    def comparison_source(self, node: ast.Call) -> bool:
        name = self.resolved(node.func)
        if (name in WATCHED or name in self.tainted_returns
                or name in self.return_summaries
                or self.module+"."+str(name) in self.return_summaries
                or self.reference_document_read(node)):
            return True
        if name == "get":
            argument = node.args[0] if node.args else next(
                (kw.value for kw in node.keywords if kw.arg == "key"), None)
            key = (argument.value if isinstance(argument, ast.Constant)
                   else self.constants.get(argument.id) if isinstance(argument, ast.Name) else None)
            return key in self.comparison_records
        return False

    def reference_document_read(self, node: ast.Call) -> bool:
        if self.resolved(node.func) != "read_store_document":
            return False
        argument = node.args[0] if node.args else next(
            (kw.value for kw in node.keywords if kw.arg == "store"), None)
        identity = (argument.value if isinstance(argument, ast.Constant)
                    else self.constants.get(argument.id) if isinstance(argument, ast.Name) else None)
        return identity == "references"

    def tainted(self, node: ast.AST, names: set[str]) -> bool:
        return any(
            isinstance(part, ast.Name) and part.id in names or
            isinstance(part, ast.Call) and self.comparison_source(part)
            for part in ast.walk(node)
        )

    def tainted_names(self, node: ast.AST) -> set[str]:
        """Monotone propagation through assignment and container mutation."""
        names: set[str] = set()
        assignments = [part for part in ast.walk(node)
                       if isinstance(part, (ast.Assign, ast.AnnAssign, ast.AugAssign))]
        mutations = [part for part in ast.walk(node) if isinstance(part, ast.Call)
                     and isinstance(part.func, ast.Attribute)
                     and part.func.attr in CONTAINER_MUTATIONS]
        changed = True
        while changed:
            changed = False
            for part in assignments:
                if part.value is not None and self.tainted(part.value, names):
                    targets = part.targets if isinstance(part, ast.Assign) else [part.target]
                    discovered = {item.id for target in targets for item in ast.walk(target)
                                  if isinstance(item, ast.Name)}
                    if not discovered <= names:
                        names.update(discovered)
                        changed = True
                # Mutable aliases remain linked when mutation taints either name.
                if isinstance(part, ast.Assign) and isinstance(part.value, ast.Name):
                    linked = {part.value.id, *(target.id for target in part.targets
                                              if isinstance(target, ast.Name))}
                    if names & linked and not linked <= names:
                        names.update(linked)
                        changed = True
            for part in mutations:
                arguments = [*part.args, *(kw.value for kw in part.keywords)]
                if any(self.tainted(argument, names) for argument in arguments):
                    targets = {item.id for item in ast.walk(part.func.value)
                               if isinstance(item, ast.Name)}
                    if not targets <= names:
                        names.update(targets)
                        changed = True
        return names

    def check_prediction_sinks(self, node: ast.FunctionDef) -> None:
        """Conservative local propagation through assignments and writer values."""
        names = self.tainted_names(node)
        for part in ast.walk(node):
            if not isinstance(part, ast.Call):
                continue
            name = self.resolved(part.func)
            if name not in {"set", "record", "compare_and_set"}:
                continue
            value = part.args[1] if len(part.args) > 1 else next(
                (kw.value for kw in part.keywords if kw.arg == "value"), None)
            if value is not None and self.tainted(value, names):
                if name in {"set", "record"} and any(
                        kw.arg == "role" and isinstance(kw.value, ast.Constant)
                        and kw.value.value == "comparison" for kw in part.keywords):
                    continue
                self.violations.append((part.lineno, str(name),
                                        "observation reaches prediction value"))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.check_prediction_sinks(node)
        self.functions.append(node.name)
        self.generic_visit(node)
        self.functions.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)  # type: ignore[arg-type]

    def visit_Call(self, node: ast.Call) -> None:
        name = self.resolved(node.func)
        if name in WATCHED or self.reference_document_read(node):
            key = "references" if self.reference_document_read(node) else first_string_arg(node)
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

        if self.rel == "scripts/init_v5.py" and name == "sm_value" and \
                key in {"M_Z", "v_HIGGS"}:
            return "SM comparison-table construction"

        current = self.functions[-1] if self.functions else ""
        if (self.reference_document_read(node)
                and (self.rel, current) in REFERENCE_DOCUMENT_READERS):
            return "reference verification or reporting (prediction sinks checked)"
        keys = COMPARISON_READS.get((self.rel, current, name), set())
        argument = node.args[0] if node.args else next(
            (kw.value for kw in node.keywords if kw.arg == "key"), None)
        argument_key = argument.value if isinstance(argument, ast.Constant) else None
        if ((isinstance(argument, ast.Name) and argument.id in keys)
                or isinstance(argument_key, str) and argument_key in keys):
            return "registered comparison (prediction sinks checked)"
        if (keys and isinstance(argument, ast.Name) and argument.id == "dataset_key"):
            parent = getattr(node, "_parent", None)
            while parent is not None and not isinstance(parent, ast.FunctionDef):
                if (isinstance(parent, ast.For) and isinstance(parent.target, ast.Name)
                        and parent.target.id == argument.id
                        and isinstance(parent.iter, (ast.Tuple, ast.List))
                        and all(isinstance(item, ast.Name) and item.id in keys
                                for item in parent.iter.elts)):
                    return "registered observation-store transfer (prediction sinks checked)"
                parent = getattr(parent, "_parent", None)

        if self.rel in {
            "cg_frg/ewsb/ew_precision.py",
            "cg_frg/ewsb/ew_one_loop.py",
        } and name == "sm_value":
            current = self.functions[-1] if self.functions else ""
            child = node
            parent = getattr(child, "_parent", None)
            while parent is not None:
                if isinstance(parent, ast.Call) and self.resolved(parent.func) == "compare_and_set":
                    permitted = list(parent.args[2:3]) + [
                        kw.value for kw in parent.keywords if kw.arg in {"observed", "note"}]
                    if any(node is item for branch in permitted for item in ast.walk(branch)):
                        return "compare_and_set target or comparison note"
                    return None
                parent = getattr(parent, "_parent", None)
            if self.rel.endswith("ew_one_loop.py") and \
                    has_ancestor_call(node, "level_table"):
                return "one-loop level table comparison column"
            if current in {"formula_check", "main"}:
                return "diagnostic routine (prediction sinks checked)"

        return None


def parse_with_parents(path: Path) -> ast.Module:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
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


def comparison_record_names(trees, records=None) -> set[str]:
    """Known diagnostic keys, from published roles and explicit source writers.

    An observed_target record's value is the computed value, so that role
    does not taint get(key). The adjacent observed metadata is a different
    field. This pass reads classifications only, never observational values.
    """
    if records is None:
        from cg_core.params import read_store_document
        path = ROOT / "cg_params.json"
        records = read_store_document(source_root=ROOT)["parameters"] if path.exists() else {}
    names = {key for key, rec in records.items() if rec.get("role") == "comparison"
             and rec.get("comparison_kind") != "observed_target"}
    for tree in trees.values():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or call_name(node.func) not in {"set", "pset", "record", "record_alias"}:
                continue
            role = next((kw.value for kw in node.keywords if kw.arg == "role"), None)
            if isinstance(role, ast.Constant) and role.value == "comparison":
                key = first_string_arg(node)
                if key != "?":
                    names.add(key)
    return names


def project_return_summaries(trees, comparison_records=()) -> set[str]:
    """Infer comparison-bearing return values across explicit module imports.

    Parsing occurs once. The finite set of function summaries grows until
    no module acquires a new summary; no scientific calculation is run.
    """
    visitors = {}
    for path, tree in trees.items():
        visitor = ObservationVisitor(path, comparison_records=comparison_records)
        visitor.prepare_module(tree)
        visitors[path] = visitor
    summaries: set[str] = set()
    changed = True
    while changed:
        changed = False
        for path, tree in trees.items():
            visitor = visitors[path]
            visitor.return_summaries = summaries
            visitor.infer_returns(tree)
            declared = {part.name for part in ast.walk(tree)
                        if isinstance(part, (ast.FunctionDef, ast.AsyncFunctionDef))}
            additions = {visitor.module+"."+name for name in declared & visitor.tainted_returns}
            if not additions <= summaries:
                summaries.update(additions)
                changed = True
    return summaries


def main() -> int:
    all_allowed: list[tuple[str, int, str, str, str]] = []
    all_violations: list[tuple[str, int, str, str]] = []

    trees = {path: parse_with_parents(path) for path in iter_python_files()}
    diagnostic_keys = comparison_record_names(trees)
    summaries = project_return_summaries(trees, diagnostic_keys)
    for path, tree in trees.items():
        visitor = ObservationVisitor(path, return_summaries=summaries,
                                     comparison_records=diagnostic_keys)
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
    print(f"  cross-module comparison return summaries: {len(summaries)}")
    print(f"  known comparison diagnostic keys: {len(diagnostic_keys)}")
    for reason, count in sorted(reasons.items()):
        print(f"  {count:3d} allowed as {reason}")
    print("  no observed-value access was found in an unapproved prediction context.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
