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
cg_frg/ewsb/vev_closure.py — V5.0: the electroweak VEV closure
=================================================================

PURPOSE
-----------------------------------
The electroweak vacuum expectation value is the product of the
emergence scale and the left-right ratio:

    v = M_G · ε

with M_G = 1.7310765e18 GeV (endpoint_constraint) and ε = 1.42218e-16
(epsilon_ratio, the window-squared line with the squash correction):

    v = 1.7310765e18 × 1.42218e-16 = 246.19 GeV

The cross-check chain (the alternative route through the Higgs
quartic) v = M_G·A·e^{−φ}·e^{−1/(2π)} with A = √(ξR_c/λ_H) gives
243.2 GeV (0.988×, less precise — the λ_H ambiguity); it is a
cross-check only, not the closure.

IMPLEMENTATION
-------------
The closure v = M_G·ε uses only internal quantities (M_G from the
endpoint chain, ε from the framework's two lines).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_frg.ewsb.epsilon_ratio import epsilon_window  # noqa: E402


def vev(M_G: float, epsilon: float) -> float:
    """v = M_G·ε — the EW VEV from the emergence scale and the
    left-right ratio."""
    return M_G * epsilon


def cross_check_vev(M_G: float, phi_R3: float) -> float:
    """v = M_G·√(ξR_c/λ_H)·e^{−φ_R3}·e^{−1/(2π)} — the alternative
    route through the Higgs quartic (a cross-check, not the
    closure; the λ_H ambiguity limits its precision)."""
    xi_rc = (1.0 / 8.0) * (6.0 / math.pi)  # ξ = 1/8, R_c = 6/π
    # lambda_H — INTERNAL (the pseudo-dilaton identity).
    lam_h = (12.0 * math.pi + 3.0) / (32.0 * math.pi ** 2)
    A = math.sqrt(xi_rc / lam_h)
    return M_G * A * math.exp(-phi_R3) * math.exp(-1.0 / (2.0 * math.pi))


def compute() -> dict:
    """Publish the VEV closure (ε already carries the J=2 squash
    correction)."""
    M_G = get("M_G")
    kL = get("kL")
    eps = epsilon_window(kL)  # the window-squared line (includes the
                              # (1 - s0*kappa) squash correction)
    v = vev(M_G, eps)         # = M_G·ε (fully internal, corrected)

    # v's (1−s0·κ) base factor is the
    # geometric charge c=−1 (the traceless shear) of squash_level_transfer.
    # See epsilon_ratio SOURCE OF THE CORRECTION FACTORS.
    pset("v_HIGGS", v, provenance="DERIVED", role="internal",
         dependencies=("M_G", "kL", "tau"),
         definition=QuantityDefinition(
             object="electroweak hierarchy VEV", unit="GeV",
             carrier="retained projected compact-space matter content",
             operator="window-squared hierarchy readout",
             source="emergence scale and the torsion-dependent squash response",
             projection="inherited fixed matter projection and response domain",
             normalization="v=M_G[3/(16*pi^3)]exp(-4*pi*kL)(1-2*tau*kappa)",
             scheme="declared electroweak hierarchy closure",
             order="specified multiplicative squash correction",
             assumptions=("M_G and kL belong to the same endpoint branch",
                          "positive squash-corrected hierarchy branch")),
         note=f"v = M_G*epsilon_window = {v:.2f} GeV (the window-squared "
              f"line eps=(3alpha/pi)e^(-4pi kL)(1 - s0*kappa(2tau)) — "
              f"the J=2 squash correction s0=2tau, kappa=U(1)_Y norm)")
    return {"v": v, "M_G": M_G, "epsilon": eps}


if __name__ == "__main__":
    r = compute()
    print(f"v = {r['v']:.2f} GeV")
    print("vev_closure OK")
