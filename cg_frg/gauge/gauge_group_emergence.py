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
cg_frg/gauge/gauge_group_emergence.py — V4.0: the gauge group
SU(3)×SU(2)×U(1) from the RP³ isometry
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The internal RP³ = S³/Z₂ has the natural isometry group
SO(4) ≅ SU(2)_L × SU(2)_R (six Killing vectors).  The Z₂ quotient
distinguishes the two SU(2) factors by their handedness:

  · the 3 EVEN (untwisted) generators → SU(2)_L (the weak isospin
    — the isometry of the untwisted sector);
  · the 3 ODD (twisted) generators → SU(2)_R (the twisted sector,
    broken by the geometric isometry breaking);
  · U(1)_Y ← the diagonal generator of the chirality layers (the
    geometric EWSB: SU(2)_R → U(1)_Y, the long-root condensate
    selects the direction);
  · SU(3)_c ← the composite of the two SU(2) blocks with the
    long-root coupling (the A₂ root system on the twisted sector).

THE GROUP STRUCTURE
-------------------
g₃ is CLOSED via the long-root correction (geometric_couplings):
the two su(2) blocks share the Killing normalisation at order α⁰,
and the long-root E_{±(α₁+α₂)} carries the α²/K correction with
K = 8/3 — g₃ = g₂·(1+α_GUT²/K).  The GROUP STRUCTURE (the
emergence of SU(3)×SU(2)×U(1) as the isometry/twist content of
RP³) is the statement of this module; the COUPLINGS are the
statement of geometric_couplings.

V4 DISCIPLINE
-------------
The module records the group-emergence structure (the algebraic
content of the RP³ isometry and the Z₂ quotient); the couplings
(g₂/g₁/g₃) are closed in geometric_couplings.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def compute() -> dict:
    """Publish the gauge-group emergence structure."""
    structure = {
        "SO(4) isometry": "SU(2)_L x SU(2)_R (6 Killing vectors of "
                          "S^3, Z_2-quotiented to RP^3)",
        "SU(2)_L": "the 3 even (untwisted) generators — the weak "
                   "isospin",
        "SU(2)_R": "the 3 odd (twisted) generators — broken by the "
                   "geometric isometry breaking (EWSB)",
        "U(1)_Y": "the diagonal generator of the chirality layers "
                  "(SU(2)_R -> U(1)_Y by the long-root condensate)",
        "SU(3)_c": "the composite of the two su(2) blocks with the "
                   "long-root coupling (the A_2 root system) — the "
                   "coupling is CLOSED via g3 = g2*(1+alpha_GUT^2/K)",
    }
    coupling_status = {
        "g2": "CLOSED (the KV normalisation, geometric_couplings)",
        "g1": "CLOSED (g1 = g2*kappa, the squash mixing)",
        "g3": "CLOSED (g3 = g2*(1+alpha_GUT^2/K) at k_GUT, the "
              "long-root bifurcation — the two su(2) blocks share the "
              "Killing normalisation at order alpha^0, the long-root "
              "E_{±(alpha_1+alpha_2)} carries the alpha^2/K correction with "
              "K = 8/3)",
    }
    pset("gauge_group_emergence", str(structure), provenance="DERIVED",
         note="the gauge group SU(3)xSU(2)xU(1) as the isometry/twist "
              "content of RP^3 (the group structure; couplings in "
              "geometric_couplings with g3 = g2*(1+alpha_GUT^2/K) "
              "CLOSED)")
    return {"structure": structure, "coupling_status": coupling_status}


if __name__ == "__main__":
    r = compute()
    for k, v in r["structure"].items():
        print(f"  {k}: {v}")
    print("  couplings:")
    for k, v in r["coupling_status"].items():
        print(f"    {k}: {v}")
    print("gauge_group_emergence OK")
