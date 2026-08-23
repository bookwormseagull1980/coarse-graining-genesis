# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
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

"""Regression tests: the parameter audit script must really check.

(2026-08-21: the comparison-role check was dead code — `if ...: pass`
never flagged anything; fixed.  This test pins the audit behaviour so
it cannot silently regress.)
"""
import subprocess
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _run_audit() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" / "audit_param_writers.py")],
        capture_output=True, text=True)


def test_audit_exits_clean():
    """The audit must pass on the current store (all records complete)."""
    r = _run_audit()
    assert r.returncode == 0, f"audit failed:\n{r.stdout}\n{r.stderr}"
    assert "AUDIT CLEAN" in r.stdout


def test_observation_leakage_audit_exits_clean():
    """Observed-value access must remain quarantined to comparison contexts."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_observation_leakage.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"observation audit failed:\n{r.stdout}\n{r.stderr}"
    assert "OBSERVATION-LEAKAGE AUDIT CLEAN" in r.stdout


def test_lean_source_audit_exits_clean():
    """Lean proof sources must not contain holes or external axioms."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_lean_sources.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"Lean source audit failed:\n{r.stdout}\n{r.stderr}"
    assert "LEAN SOURCE AUDIT CLEAN" in r.stdout
    assert "no interactive output commands" in r.stdout


def test_numeric_precision_audit_exits_clean():
    """Stored numeric values must not be rounded or formatted before writing."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_numeric_precision.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"numeric precision audit failed:\n{r.stdout}\n{r.stderr}"
    assert "NUMERIC PRECISION AUDIT CLEAN" in r.stdout


def test_path_portability_audit_exits_clean():
    """Reviewer-facing files must not leak machine-local absolute paths."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_path_portability.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"path portability audit failed:\n{r.stdout}\n{r.stderr}"
    assert "PATH PORTABILITY AUDIT CLEAN" in r.stdout


def test_audit_detects_missing_observed():
    """The comparison-role check must flag a record without an observed
    target — the 2026-08-21 dead-code regression test.

    We inject a temporary broken record, run the audit, and restore.
    """
    import json
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    saved = data["parameters"].pop("kL", None)
    # Inject a comparison record without an observed target/note.
    data["parameters"]["_audit_test_broken"] = {
        "value": 1.0, "provenance": "DERIVED",
        "role": "comparison", "note": "no observed target here",
        "writer": "tests/test_audit.py",
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True),
                    encoding="utf-8")
    try:
        r = _run_audit()
        assert r.returncode != 0, "audit should flag the broken comparison record"
        assert "_audit_test_broken" in r.stdout
    finally:
        # Restore the original store.
        data = json.loads(path.read_text(encoding="utf-8"))
        data["parameters"].pop("_audit_test_broken", None)
        if saved is not None:
            data["parameters"]["kL"] = saved
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True),
                        encoding="utf-8")
