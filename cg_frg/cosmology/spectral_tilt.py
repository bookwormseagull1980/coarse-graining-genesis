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
cg_frg/cosmology/spectral_tilt.py — V4.0: the spectral tilt closure
1 − n_s = τ·[(1+2+1+3)/(d+1)] = τ·7/4
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The primordial spectral tilt is the exact product of the torsion
modulus and the RP³ Weyl window ratio:

    1 − n_s = τ·(7/4) = 0.02 × 1.75 = 0.035

The ratio is computed from the RP³ Weyl-law degree-of-freedom count
divided by the four-level window/cascade normalisation:

    (scalar + vector + spinor + TT)/(d+1)
      = (1 + 2 + 1 + 3)/4 = 7/4.

The conformal-curvature identity 1 + ξR_LC L² = 1 + (1/8)·6 gives
the same rational value and is kept as a cross-check.

V4 DISCIPLINE
-------------
The closure uses τ (the framework modulus) and the exact window
ratio computed in cg_core.window_weights.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.window_weights import scalar_vector_window_ratio  # noqa: E402


def one_minus_ns(tau: float) -> float:
    """1 − n_s = τ·[(1+2+1+3)/(d+1)] = τ·(7/4)."""
    return tau * scalar_vector_window_ratio()


def compute() -> dict:
    """Publish the tilt closure."""
    tau = get("tau")
    val = one_minus_ns(tau)
    pset("ns_tilt", val, provenance="DERIVED", role="internal",
         note="1 - n_s = tau*((1+2+1+3)/(d+1)) = tau*(7/4) = 0.035 "
              "(the torsion modulus times the RP3 Weyl window ratio; "
              "1+2+1+3 from scalar/vector/spinor/TT d.o.f., d+1=4; "
              "cross-check: 1+xi R_LC L^2=7/4)")
    return {"one_minus_ns": val, "tau": tau}


if __name__ == "__main__":
    r = compute()
    print(f"1 - n_s = {r['one_minus_ns']}")
    print("spectral_tilt OK")
