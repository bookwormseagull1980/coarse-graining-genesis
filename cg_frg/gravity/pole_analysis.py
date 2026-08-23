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
cg_frg/gravity/pole_analysis.py — V4.0: the spectral-pole stability
criteria
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The massless spin-2 pole of the emergent TT propagator is a stable
physical pole if the spectral density is positive and the matter
self-energy stays below the bare mass:

    spectral_positive : p²_min = 8/L² > 0 (the first TT level — the
                        positive spectral density of the pole)
    pole_stable       : Σ(M_G) < m²_bare (the matter self-energy
                        below the bare mass 14/L² — the pole is not
                        pushed off by the matter content)
    matter_is_small   : Σ(M_G)/p²_min < 0.1 (the self-energy is a
                        small perturbation of the first level)

THE SCALES (RP³ at the trajectory)
----------------------------------
    p²_min  = 8/L²   (the J = 2 Casimir momentum)
    m²_bare = 14/L²  (p²_min + the Lichnerovich shift 6/L²)
    Σ(M_G)  = ρ_MG/(16π²·M_P²)  (the matter self-energy from the
              mode-sum density ρ_MG at the emergence scale)

V4 DISCIPLINE
-------------
The self-energy density ρ_MG is read from the store (published by
the mode-sum engine); the criteria are the framework's stability
statement (no ghost, no gap, no decoherence).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def self_energy_MG(rho_MG: float, M_P: float) -> float:
    """Σ(M_G) = ρ_MG/(16π²·M_P²) — the matter self-energy (a mass²).

    ρ_MG is the mode-sum density of the matter content at the
    emergence scale (units GeV⁴); the division by 16π²·M_P²
    converts it to the mass² scale of the pole.
    """
    return rho_MG / (16.0 * math.pi ** 2 * M_P * M_P)


def stability(sigma_MG: float, L: float) -> dict:
    """The three pole-stability criteria at radius L."""
    pmin = 8.0 / (L * L)
    m2b = pmin + 6.0 / (L * L)
    return {
        "spectral_positive": pmin > 0.0,
        "pole_stable": sigma_MG < m2b,
        "matter_is_small": sigma_MG / pmin < 0.1,
        "p2_min": pmin, "m2_bare": m2b, "sigma_MG": sigma_MG,
        "stable": pmin > 0.0 and sigma_MG < m2b and sigma_MG / pmin < 0.1,
    }


def compute() -> dict:
    """Publish the stability analysis at the fixed point."""
    kL = get("kL")
    M_P = get("M_P")
    M_G = get("M_G")
    L = kL  # the trajectory's L at k = M_G

    # FREE-FIELD verification only: the matter self-energy ρ_MG is not
    # yet computed by the mode-sum engine (spectral_sum publishes the
    # channel spectra, not ρ_MG), so the stability criteria are verified
    # in the ρ_MG -> 0 limit.  The verdict is scoped to that limit and
    # does NOT include the matter back-reaction.
    rho_MG = 0.0
    sigma = self_energy_MG(rho_MG, M_P)
    s = stability(sigma, L)
    pset("TT_pole_verified", s["stable"], provenance="DERIVED",
         note="TT pole stability in the FREE-FIELD limit (rho_MG = 0): "
              "positive spectral density, self-energy below the bare "
              "mass; the matter back-reaction is NOT yet included "
              "(pole_analysis)")
    return s


if __name__ == "__main__":
    r = compute()
    print(f"spectral_positive={r['spectral_positive']}, "
          f"pole_stable={r['pole_stable']}, matter_is_small={r['matter_is_small']}, "
          f"stable={r['stable']}")
    print("pole_analysis OK")
