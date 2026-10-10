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
cg_frg/gravity/pole_analysis.py — internal-mode and density comparisons
=================================================================

PURPOSE
-----------------------------------
The result reports three algebraic checks:

    spectral_positive : p²_min = 8/L² > 0 (positive internal-mode label)
    pole_stable       : Σ(M_G) < m²_bare (density readout below
                        the implemented denominator scale 14/L²)
    matter_is_small   : Σ(M_G)/p²_min < 0.1 (signed ratio below 0.1)

These quantities describe the specified internal denominator. A tensor
spectral calculation evaluates the connected source correlator, its
physical critical space, momentum slope and source overlaps.

THE SCALES (RP³ at the trajectory)
----------------------------------
    p²_min  = 8/L²   (the J = 2 Casimir momentum)
    m²_bare = 14/L²  (p²_min + the implemented curvature term 6/L²)
    Σ(M_G)  = ρ_MG/(16π²·M_P²)  (the prescribed density readout)

IMPLEMENTATION
-------------
compute() evaluates the zero-density branch ρ_MG = 0. A supplied
density enters through self_energy_MG and the same internal denominator.
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
    """Σ(M_G) = ρ_MG/(16π²·M_P²), a prescribed mass² estimate.

    rho_MG is the supplied density (units GeV⁴); division by
    16π²·M_P² gives mass² units. rho_MG is an explicit input to this
    density-normalisation prescription.
    """
    return rho_MG / (16.0 * math.pi ** 2 * M_P * M_P)


def stability(sigma_MG: float, L: float) -> dict:
    """Evaluate the three internal-mode comparisons at L."""
    if not math.isfinite(L) or L <= 0 or not math.isfinite(sigma_MG):
        raise ValueError("finite sigma and positive finite L required")
    pmin = 8.0 / (L * L)
    m2b = pmin + 6.0 / (L * L)
    domain = sigma_MG >= 0.0
    return {
        "spectral_positive": pmin > 0.0,
        "nonnegative_prescribed_sigma": domain,
        "pole_stable": domain and sigma_MG < m2b,
        "matter_is_small": abs(sigma_MG) / pmin < 0.1,
        "p2_min": pmin, "m2_bare": m2b, "sigma_MG": sigma_MG,
        "stable": domain and sigma_MG < m2b and abs(sigma_MG) / pmin < 0.1,
        "external_pole_established": False,
    }


def compute() -> dict:
    """Publish the zero-density internal-mode diagnostic."""
    kL = get("kL")
    M_P = get("M_P")
    M_G = get("M_G")
    L = kL / M_G  # reciprocal GeV, matching sigma's mass-squared units

    # The declared branch has rho_MG=0.
    rho_MG = 0.0
    sigma = self_energy_MG(rho_MG, M_P)
    s = stability(sigma, L)
    pset("TT_internal_mode_checks_passed", s["stable"], provenance="DERIVED",
         note="Internal-mode comparisons at the declared zero-density "
              "branch rho_MG=0: positive label, positive denominator "
              "and density ratio below the stated threshold.")
    pset("TT_pole_verified", False, provenance="DERIVED", role="informational",
         note="External spectral certification evaluates the physical tensor "
              "kernel, positive momentum slope and nonzero source overlap.")
    return s


if __name__ == "__main__":
    r = compute()
    print(f"internal-mode comparisons: spectral_positive={r['spectral_positive']}, "
          f"pole_stable={r['pole_stable']}, matter_is_small={r['matter_is_small']}, "
          f"stable={r['stable']}")
    print("pole_analysis OK")
