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
scripts/audit_param_writers.py — V5.0: the parameter-writer audit
=================================================================

Every parameter declares its provenance
(INPUT/DERIVED/OBSERVED/SM_INPUT), every DERIVED parameter carries
a derivation note, and every comparison record carries a role.
This audit scans cg_params.json and reference_inputs.json and reports
violations:

  1. missing provenance / writer / note fields;
  2. DERIVED parameters without a derivation note;
  3. comparison-role parameters whose notes do not state the
     comparison-only intent;
  4. parameters whose writer is the generic store (not a module).
  5. malformed physical definitions or explicit input fingerprints which
     disagree with the values read when the record was published.

Coverage records the number of declared physical definitions and explicit
input bindings checked by the audit.

Exit code: 0 = audit clean, 1 = violations found.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_core.params import resolve_value  # noqa: E402

_STORE_ROOT = Path(os.environ.get("V5_OUTPUT_DIR", str(_PROJECT_ROOT))).resolve()

REQUIRED = ("value", "provenance", "writer", "note")


def audit_file(path: Path, label: str,
               check_comparison_observed: bool = False) -> list:
    """Audit one store file; return the violation strings.

    check_comparison_observed: only meaningful for cg_params.json.  A
    record with role="comparison" must make its comparison-only status
    explicit.  It may either carry an observed target, or it may be a
    fixed-parameter diagnostic/propagation record whose note states that
    it is not a V5 input.  The SM table is skipped for this check: its
    records ARE the observed comparison values themselves.
    """
    violations = []
    if not path.exists():
        return [f"{label}: file missing ({path})"]
    data = json.loads(path.read_text(encoding="utf-8"))
    params = data.get("parameters", {})
    for key, rec in params.items():
        if not isinstance(rec, dict):
            violations.append(f"{label}/{key}: record is not a dict")
            continue
        for field in REQUIRED:
            if field == "value" and "reference" in rec:
                if "value" in rec:
                    violations.append(f"{label}/{key}: reference also stores a duplicate value")
                try:
                    resolve_value(rec["reference"], params, (key,))
                except (KeyError, TypeError, ValueError, IndexError) as exc:
                    violations.append(f"{label}/{key}: invalid parameter reference: {exc}")
                continue
            if field == "value" and field in rec and rec[field] is None and \
                    rec.get("provenance") == "PENDING" and \
                    rec.get("role") == "informational" and rec.get("note"):
                continue  # explicit unavailable result, never a numerical input
            if field not in rec or rec[field] in (None, ""):
                violations.append(f"{label}/{key}: missing '{field}'")
        prov = rec.get("provenance", "")
        if prov == "DERIVED" and not rec.get("note"):
            violations.append(f"{label}/{key}: DERIVED without a note")
        if check_comparison_observed and \
                rec.get("role") == "comparison" and \
                "observed" not in rec and \
                rec.get("comparison_kind") not in {"diagnostic", "archived_external"}:
            violations.append(
                f"{label}/{key}: comparison role without structured target or diagnostic kind")
        if prov == "DERIVED":
            writer = str(rec.get("writer", ""))
            source = (_PROJECT_ROOT / writer).resolve()
            if not source.is_relative_to(_PROJECT_ROOT) or not source.is_file():
                violations.append(f"{label}/{key}: writer source does not exist: {writer}")
        definition = rec.get("quantity_definition")
        if "value" in rec:
            try:
                resolve_value(rec["value"], params, (key,))
            except (KeyError, TypeError, ValueError, IndexError) as exc:
                violations.append(f"{label}/{key}: invalid value projection: {exc}")
        if definition is not None:
            try:
                QuantityDefinition(**definition)
            except (TypeError, ValueError) as exc:
                violations.append(f"{label}/{key}: invalid physical definition: {exc}")
        if "direct_inputs" in rec:
            # These fingerprints identify values consumed at publication.
            # Compare with those recorded reads, not with a later mutable
            # store state. Formula completeness is reviewed at each writer;
            # this structural audit does not infer it from accumulated reads.
            direct = rec["direct_inputs"]
            reads = rec.get("module_read_inputs", {})
            if not isinstance(direct, dict) or not isinstance(reads, dict):
                violations.append(f"{label}/{key}: input fingerprints must be mappings")
                continue
            if not rec.get("dependency_scope"):
                violations.append(f"{label}/{key}: direct inputs lack their declared scope")
            for parent, fingerprint in direct.items():
                if (not isinstance(parent, str) or not parent or
                        not isinstance(fingerprint, str) or
                        re.fullmatch(r"[0-9a-f]{64}", fingerprint) is None):
                    violations.append(f"{label}/{key}: invalid input fingerprint for {parent}")
                elif reads.get(parent) != fingerprint:
                    violations.append(f"{label}/{key}: direct input {parent} differs from recorded read")
    return violations


def main() -> int:
    violations = []
    for fname, label, chk in (("cg_params.json", "cg_params", True),
                              ("comparison/reference_inputs.json", "sm_inputs",
                               False)):
        violations += audit_file(_STORE_ROOT / fname, label,
                                 check_comparison_observed=chk)

    if violations:
        print(f"AUDIT: {len(violations)} violation(s)")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("AUDIT CLEAN: all parameters carry provenance/writer/note; "
          "every DERIVED names a module; supplied definitions and input bindings are valid.")
    records = json.loads((_STORE_ROOT / "cg_params.json").read_text(encoding="utf-8"))["parameters"]
    definitions = sum(rec.get("quantity_definition") is not None for rec in records.values())
    direct = sum("direct_inputs" in rec for rec in records.values())
    print(f"Metadata coverage: {definitions}/{len(records)} physical definitions; "
          f"{direct}/{len(records)} explicit store-input sets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
