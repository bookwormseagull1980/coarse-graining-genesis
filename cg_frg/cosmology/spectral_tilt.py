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
cg_frg/cosmology/spectral_tilt.py — V5.0: the spectral tilt closure
1 − n_s = τ·[(1+2+1+3)/(d+1)] = τ·7/4
=================================================================

PURPOSE
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

IMPLEMENTATION
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
         dependencies=("tau",),
         note="1 - n_s = tau*((1+2+1+3)/(d+1)) = tau*(7/4) = 0.035 "
              "(the torsion modulus times the RP3 Weyl window ratio; "
              "1+2+1+3 from scalar/vector/spinor/TT d.o.f., d+1=4; "
              "cross-check: 1+xi R_LC L^2=7/4)")
    return {"one_minus_ns": val, "tau": tau}


if __name__ == "__main__":
    r = compute()
    print(f"1 - n_s = {r['one_minus_ns']}")
    print("spectral_tilt OK")
