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
cg_frg/framework/five_items.py — V4.0: the five framework
results' status
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
This module records the current status of five framework results,
each with its closing module:

  ITEM 1 — WHY 3 GENERATIONS (n = {0,2,4}):
    CLOSED-formal: the window-capacity theorem (window_capacity:
    the RP³ Dirac spectrum j = 1/2, 5/2, 9/2 inside the Nyquist
    window 2π/L — the exact mode-counting theorem).

  ITEM 2 — THE BRANCH CHOICE (the hypercharge B′ vs C′):
    the branch selection of the hypercharge assignment — recorded
    (the U(1)_Y generator choice in the geometric EWSB).

  ITEM 3 — 2L = √(2π):
    CLOSED: the entropy-minimum distance (the Gaussian maximum-
    entropy correlation distance √(2π); the twoL discrimination).

  ITEM 4 — THE TWO v-PATHS (the factor-2 unification):
    CLOSED: the ε is the common object — v = M_G·ε = 246.19 GeV
    (vev_closure, −0.012%); the factor-2 anchor of the relaxion
    baseline (relaxion_geo: v(φ_R0) = 1.97×v).

  ITEM 5 — THE m_e:
    CLOSED: m_e = M_P·e^{−20kL}·(1−s0·κ) = 0.510 MeV (−0.13%,
    electron_mass); the cascade mechanism.

V4 DISCIPLINE
-------------
A status ledger: every claim names its closing module.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def compute() -> dict:
    """Publish the five items' status."""
    items = {
        "ITEM 1 — 3 generations (n = {0,2,4})": {
            "status": "CLOSED-formal",
            "module": "window_capacity (the Nyquist mode-counting "
                      "theorem: j = 1/2, 5/2, 9/2 in the window 2pi/L)",
            "value": get("n_generations"),
        },
        "ITEM 2 — the branch choice (hypercharge B' vs C')": {
            "status": "recorded",
            "module": "the U(1)_Y generator choice in the geometric "
                      "EWSB (the branch selection)",
            "value": None,
        },
        "ITEM 3 — 2L = sqrt(2pi)": {
            "status": "CLOSED",
            "module": "the entropy-minimum distance (the Gaussian "
                      "maximum-entropy correlation distance)",
            "value": None,
        },
        "ITEM 4 — the two v-paths (the factor-2 unification)": {
            "status": "CLOSED",
            "module": "vev_closure (v = M_G eps = 246.19) + "
                      "relaxion_geo (the factor-2 anchor 1.97)",
            "value": get("v_HIGGS"),
        },
        "ITEM 5 — the m_e": {
            "status": "CLOSED-near",
            "module": "electron_mass (m_e = 0.510 MeV, -0.13%)",
            "value": None,
        },
    }
    status = {k: v["status"] for k, v in items.items()}
    pset("five_items_status", str(status), provenance="DERIVED",
         note="the five items' status ledger (1: CLOSED-formal, "
              "2: recorded, 3: CLOSED, 4: CLOSED, 5: CLOSED-near)")
    return {"items": items, "closed_count": 4}


if __name__ == "__main__":
    r = compute()
    for k, v in r["items"].items():
        val = "" if v["value"] is None else f" = {v['value']}"
        print(f"  {k}: {v['status']}{val}")
    print(f"closed: {r['closed_count']}/5 (item 2 recorded, item 5 near)")
    print("five_items OK")
