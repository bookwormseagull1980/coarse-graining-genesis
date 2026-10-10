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
cg_frg/generation/window_capacity.py — V5.0: the three-generation
spectral-capacity closure
=================================================================

PURPOSE
-----------------------------------
The generation count is the value of the spectral-capacity map on the
Z₂-even RP³ spinor tower.  Its dimensionless Dirac positions are
n+3/2 for n=0,2,4,..., and the closure retains the positions satisfying

    (n + 3/2) < (kL)²

(the capacity criterion at the γ_M=0 fixed point).  With
kL*=2.4935343:

    (kL*)² = 6.2177,
    n = 0 : 1.5  < 6.2177  ✓
    n = 2 : 3.5  < 6.2177  ✓
    n = 4 : 5.5  < 6.2177  ✓
    n = 6 : 7.5  > 6.2177  ✗ (excluded, −20.6% above the edge)

the map returns exactly the three positions n={0,2,4}.  Its capacity
(kL*)²=6.2177 lies 1.04% below the Euclidean-period value 2π.

The mode mass ladder of the generations is m_n ∝ e^{−α·n} with the
extrusion order n = {0, 2, 4} (the LZ non-adiabatic squeezing of
the scale flow — see lz_ladder).

IMPLEMENTATION
-------------
The capacity criterion (n+3/2)<(kL)² is the declared generation
closure, and kL is read from the endpoint fixed point.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.content_response import screening_compatibility


def window_boundary(kL: float) -> float:
    """The window capacity: (kL)²."""
    return kL * kL


def mode_mass_index(n: int) -> float:
    """m_n = (n+3/2)/L — the Z₂-even spinor mode in units of 1/L."""
    return n + 1.5


def count_generations(kL: float) -> tuple[int, list[int], list[float]]:
    """Evaluate the spectral-capacity map (n+3/2)<(kL)².

    Returns (count, [n...], [margin...]) where the margin is the
    fractional distance of the mode from the window edge.
    """
    cap = window_boundary(kL)
    modes, margins = [], []
    n = 0
    while True:
        m = mode_mass_index(n)
        if m >= cap:
            break
        modes.append(n)
        margins.append((cap - m) / cap)
        n += 2
    return len(modes), modes, margins


def compute() -> dict:
    """Verify the endpoint platform of the independently selected copy count."""
    kL = get("kL")
    count, modes, margins = count_generations(kL)
    selected = screening_compatibility()["generations"]
    if count != selected:
        raise ValueError("endpoint platform conflicts with joint screening selection")
    pset("n_generations", count, provenance="DERIVED",
         dependencies=("kL",),
         note="joint extensive-source/colour screening selects g=Nc=3; "
              "the independent endpoint platform retains n={0,2,4}")
    return {"n_generations": count, "modes": modes, "margins": margins,
            "kL": kL, "capacity": window_boundary(kL)}


if __name__ == "__main__":
    r = compute()
    print(f"n_generations = {r['n_generations']} (modes n = {r['modes']}, "
          f"capacity (kL)^2 = {r['capacity']:.4f})")
    print("window_capacity OK")
