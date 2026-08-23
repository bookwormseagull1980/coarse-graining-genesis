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

"""Regression test for the reviewer HTML dashboard generator."""

import subprocess
import sys
from pathlib import Path


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_reviewer_dashboard_generates():
    out = _PROJECT_ROOT / "docs" / "_test_reviewer_dashboard.html"
    try:
        r = subprocess.run(
            [sys.executable, str(_PROJECT_ROOT / "scripts" /
                                "make_reviewer_dashboard.py"),
             "--output", str(out)],
            cwd=str(_PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"dashboard generation failed:\n{r.stdout}\n{r.stderr}"
        text = out.read_text(encoding="utf-8")
        assert "V4 Reviewer Dashboard" in text
        assert "Anchor-to-results tree" in text
        assert "treeSector" in text
        assert "anchor_tree" in text
        assert "numeric precision" in text
        assert "path portability" in text
        assert "G_N_PDG" in text
        assert "OBSERVATION-LEAKAGE AUDIT CLEAN" in text
    finally:
        if out.exists():
            out.unlink()
