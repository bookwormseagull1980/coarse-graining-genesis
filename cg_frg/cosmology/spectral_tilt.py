# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
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
cg_frg/cosmology/spectral_tilt.py — V4.0: the spectral tilt closure
1 − n_s = τ·7/4
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The primordial spectral tilt is the exact product of the torsion
modulus and the rational 7/4:

    1 − n_s = τ·(7/4) = 0.02 × 1.75 = 0.035

The 7/4 is exact (the ratio of the scalar/vector mode weights of
the coarse-graining window at the CMB scale — the spectral tilt of
the unbiased Gaussian).

V4 DISCIPLINE
-------------
The closure uses τ (the framework modulus) and the exact 7/4.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def one_minus_ns(tau: float) -> float:
    """1 − n_s = τ·(7/4)."""
    return tau * 7.0 / 4.0


def compute() -> dict:
    """Publish the tilt closure."""
    tau = get("tau")
    val = one_minus_ns(tau)
    pset("ns_tilt", val, provenance="DERIVED", role="internal",
         note="1 - n_s = tau*(7/4) = 0.035 (the torsion modulus times the "
              "exact 7/4 scalar/vector window ratio)")
    return {"one_minus_ns": val, "tau": tau}


if __name__ == "__main__":
    r = compute()
    print(f"1 - n_s = {r['one_minus_ns']}")
    print("spectral_tilt OK")
