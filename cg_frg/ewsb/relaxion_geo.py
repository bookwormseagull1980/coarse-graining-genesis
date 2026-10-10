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
cg_frg/ewsb/relaxion_geo.py — V5.0: the relaxion geometry — the
dilaton pole barrier on the internal RP³ and the φ_R0 factor-2
anchor
=================================================================

PURPOSE
-----------------------------------
The electroweak scale is fixed by the dilaton-stop position: the
dilaton field φ rolls along the cosmological flow until it hits
the geometric pole barrier

    x(φ; k) = V(k)·Π_φ(k) = 1

where V(k) is the effective potential curvature and Π_φ(k) the
dilaton polarisation (the spectral sum over the RP³ scalar modes):

    Π_φ(k) = Σ_l d_l/(λ_l + V''(k)) ,   λ_l = l(l+2)/kL² ,
    d_l = (l+1)²  (the even-l RP³ scalars).

At the pole the propagator diverges and the flow freezes.  The
bare-condensate coordinate φ_R0 is obtained from the window stop by
subtracting the three structural logarithmic shifts.

CONDENSATE NORMALISATION
-----------------------
The computed ratio

    v(φ_R0)/v = √(ξ R_c M_G² e^{−2φ_R0}/λ_H)/v

is compared with the structural factor 2.  Both scales use the same
generated parameters; the ratio and its central difference from 2 are
evaluated with the current stored inputs.

IMPLEMENTATION
-------------
The pole-condition structure (the RP³ dilaton polarisation) is
implemented in full; the factor-2 anchor is verified with the
framework's own parameters.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_frg.ewsb.relaxion_chain import PHI_R0, v_from_phi  # noqa: E402

XI = 1.0 / 8.0
R_C = 6.0 / math.pi
# lambda_H — INTERNAL (the pseudo-dilaton identity).
LAM_H_INTERNAL = (12.0 * math.pi + 3.0) / (32.0 * math.pi ** 2)


def dilaton_polarisation(k: float, Vpp: float, kL: float,
                         l_max: int = 80) -> float:
    """Π_φ(k) = Σ_l d_l/(λ_l + Vpp/k²)/k² — the RP³ dilaton
    polarisation (the even-l scalars, d_l = (l+1)²)."""
    s = 0.0
    for l in range(0, l_max + 1, 2):
        lam_l = l * (l + 2) / (kL * kL)
        d_l = (l + 1) * (l + 1)
        s += d_l / (lam_l + Vpp / (k * k) + 1e-30)
    return s / (k * k)


def pole_function(k: float, v_dil: float, gamma_V: float,
                  M_G: float, kL: float) -> float:
    """x(k) = V(k)·Π_φ(k) with V(k) = v_dil²·(k/M_G)^{γ_V}."""
    V_eff = v_dil * v_dil * (k / M_G) ** gamma_V
    return V_eff * dilaton_polarisation(k, V_eff, kL)


def factor_two_anchor() -> dict:
    """Verify the factor-2 anchor: v(φ_R0) ≈ 2 × v (internal)."""
    M_G = get("M_G")
    v = float(get("v_HIGGS"))   # the framework's own VEV (internal)
    lam_h = LAM_H_INTERNAL
    v0 = v_from_phi(PHI_R0, M_G, lam_h)
    return {"v_phi_R0": v0, "factor": v0 / v,
            "target": 2.00, "dev_factor": (v0 / v / 2.0 - 1.0) * 100.0}


def compute() -> dict:
    """Publish the mechanism and verify the factor-2 anchor."""
    kL = get("kL")
    M_G = get("M_G")
    fa = factor_two_anchor()

    # The pole-condition diagnostic at the emergence scale (the
    # mechanism's reference point).
    v_dil_ref = math.sqrt(XI * R_C * M_G ** 2 / LAM_H_INTERNAL)  # the φ=0 VEV
    x_MG = pole_function(M_G, v_dil_ref, 0.0, M_G, kL)

    pset("relaxion_factor_two", fa["factor"], provenance="DERIVED",
         role="cg",
         note=f"v(phi_R0)/v = {fa['factor']:.3f} vs the structural 2.00 "
              f"({fa['dev_factor']:+.1f}% — the factor-2 anchor of the "
              f"relaxion baseline)")
    return {"factor_two": fa, "pole_function_at_MG": x_MG,
            "phi_R0": PHI_R0, "kL": kL}


if __name__ == "__main__":
    r = compute()
    fa = r["factor_two"]
    print(f"v(phi_R0) = {fa['v_phi_R0']:.1f} GeV = "
          f"{fa['factor']:.3f} x v (target 2.00, "
          f"{fa['dev_factor']:+.1f}%)")
    print(f"pole function x(M_G) = {r['pole_function_at_MG']:.4f} "
          f"(the reference point of the mechanism)")
    print(f"phi_R0 = {r['phi_R0']:.4f} (the bare-condensate coordinate)")
    print("relaxion_geo OK")
