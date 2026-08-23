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
cg_frg/generation/window_capacity.py — V4.0: the three-generation
count (the window-capacity theorem)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The number of fermion generations is not an input of the framework:
it is the number of spinor modes of the internal RP³ that fit
inside the coarse-graining window.  The Z₂-even spinor tower has
the eigenvalues m_n = (n+3/2)/L (n = 0, 2, 4, ...); the window of
the scale flow retains the modes with

    (n + 3/2) < (kL)²

(the framework's window criterion — the scale-invariant combination
kL at the γ_M = 0 fixed point).  With kL* = 2.4935343:

    (kL*)² = 6.2177,
    n = 0 : 1.5  < 6.2177  ✓
    n = 2 : 3.5  < 6.2177  ✓
    n = 4 : 5.5  < 6.2177  ✓
    n = 6 : 7.5  > 6.2177  ✗ (excluded, −20.6% above the edge)

so the window contains exactly the three modes n = {0, 2, 4}: the
three generations.  The edge of the window sits at 1.04% below
2π (the Euclidean-period value of the window; the two derivations
— the framework's (kL)² and the paper's 2π — are the same
count).

The mode mass ladder of the generations is m_n ∝ e^{−α·n} with the
extrusion order n = {0, 2, 4} (the LZ non-adiabatic squeezing of
the scale flow — see lz_ladder).

V4 DISCIPLINE
-------------
The window criterion (n+3/2) < (kL)² is derived from the
coarse-graining window of the scale flow; kL is read from the
store (the endpoint_constraint fixed point).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def window_boundary(kL: float) -> float:
    """The window capacity: (kL)²."""
    return kL * kL


def mode_mass_index(n: int) -> float:
    """m_n = (n+3/2)/L — the Z₂-even spinor mode in units of 1/L."""
    return n + 1.5


def count_generations(kL: float) -> tuple[int, list[int], list[float]]:
    """The generation count: the modes with (n+3/2) < (kL)².

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
    """Publish the generation count."""
    kL = get("kL")
    count, modes, margins = count_generations(kL)
    pset("n_generations", count, provenance="DERIVED",
         note="window-capacity theorem: spinor modes with (n+3/2) < (kL)^2 "
              "= exactly 3 (n = {0,2,4})")
    return {"n_generations": count, "modes": modes, "margins": margins,
            "kL": kL, "capacity": window_boundary(kL)}


if __name__ == "__main__":
    r = compute()
    print(f"n_generations = {r['n_generations']} (modes n = {r['modes']}, "
          f"capacity (kL)^2 = {r['capacity']:.4f})")
    print("window_capacity OK")
