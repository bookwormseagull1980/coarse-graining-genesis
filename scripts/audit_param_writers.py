# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
scripts/audit_param_writers.py — V4.0: the parameter-writer audit
=================================================================

WHY THIS SCRIPT EXISTS (motivation)
-----------------------------------
The V4 discipline requires: every parameter has a provenance
(INPUT/DERIVED/OBSERVED/SM_INPUT), every DERIVED parameter carries
a derivation note, and every comparison record carries a role.
This audit scans cg_params.json and sm_inputs.json and reports
violations:

  1. missing provenance / writer / note fields;
  2. DERIVED parameters without a derivation note;
  3. comparison-role parameters whose notes do not state the
     comparison-only intent;
  4. parameters whose writer is the generic store (not a module).

Exit code: 0 = audit clean, 1 = violations found.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

REQUIRED = ("value", "provenance", "writer", "note")


def audit_file(path: Path, label: str,
               check_comparison_observed: bool = False) -> list:
    """Audit one store file; return the violation strings.

    check_comparison_observed: only meaningful for cg_params.json.  A
    record with role="comparison" must make its comparison-only status
    explicit.  It may either carry an observed target, or it may be a
    fixed-parameter diagnostic/propagation record whose note states that
    it is not a V4 input.  The SM table is skipped for this check: its
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
            if field not in rec or rec[field] in (None, ""):
                violations.append(f"{label}/{key}: missing '{field}'")
        prov = rec.get("provenance", "")
        if prov == "DERIVED" and not rec.get("note"):
            violations.append(f"{label}/{key}: DERIVED without a note")
        note_l = str(rec.get("note", "")).lower()
        comparison_note_ok = (
            "observed" in note_l or
            "comparison" in note_l or
            "not an input" in note_l or
            "supplies no v4 parameter" in note_l or
            "not read by upstream" in note_l
        )
        if check_comparison_observed and \
                rec.get("role") == "comparison" and \
                "observed" not in rec and \
                not comparison_note_ok:
            violations.append(
                f"{label}/{key}: comparison role without an observed "
                f"target or comparison-only note")
    return violations


def main() -> int:
    violations = []
    for fname, label, chk in (("cg_params.json", "cg_params", True),
                              ("comparison/sm_inputs.json", "sm_inputs",
                               False)):
        violations += audit_file(_PROJECT_ROOT / fname, label,
                                 check_comparison_observed=chk)

    # The writer provenance: every DERIVED must name a module.
    if _PROJECT_ROOT.joinpath("cg_params.json").exists():
        data = json.loads(
            _PROJECT_ROOT.joinpath("cg_params.json")
                        .read_text(encoding="utf-8"))
        for key, rec in data.get("parameters", {}).items():
            if rec.get("provenance") == "DERIVED" and \
                    "cg_" not in str(rec.get("writer", "")) and \
                    "init_v4" not in str(rec.get("writer", "")):
                violations.append(f"cg_params/{key}: DERIVED writer is "
                                  f"not a module: {rec.get('writer')}")

    if violations:
        print(f"AUDIT: {len(violations)} violation(s)")
        for v in violations:
            print(f"  - {v}")
        return 1
    print("AUDIT CLEAN: all parameters carry provenance/writer/note; "
          "every DERIVED names a module.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
