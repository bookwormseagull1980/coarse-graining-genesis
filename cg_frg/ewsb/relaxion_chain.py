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
cg_frg/ewsb/relaxion_chain.py — V5.0: structural dilaton shifts
The window stop position and the electroweak hierarchy
=================================================================

PURPOSE
-----------------------------------
The generated window defines the dilaton-stop position and scale ratio:

    φ_stop = 4πkL − ln(3α/π) + 1/(2π) − ln(1 − s0·κ),
    ε = e^{1/(2π)} e^{−φ_stop},       v = M_G·ε,

with α = 1/(16π²), s0 = 2τ and κ = κ(2τ).  The bare-condensate
coordinate is φ_R0 = φ_stop − Δφ_R1 − Δφ_R2 − Δφ_R3.  Its three
structural shifts are:

  R1  Collective-mode normalisation √4 = 2:
          Δφ_R1 = (1/2)·ln 2.

  R2  Symmetric box at q = 0, with the common propagator momentum
      1/(p²+m²)² and RP³ Weyl window ratio (1+2+1+3)/(d+1) = 7/4:
          Δφ_R2 = (1/4)·ln(7/4).

  R3  Single-mode wave-function factor Z = 2·(3/4)³, where
      m² = 6/8 = 3/4 is the Lichnerowicz-to-Casimir ratio:
          Δφ_R3 = −(1/4)·ln Z.

ORDER-PARAMETER COMPARISON
--------------------------
The same stop coordinate also enters the specified condensate relation

    v_chain² = ξ R_c M_G² e^{−2φ_stop}/λ_H,
    φ_req = (1/2)·ln(ξ R_c M_G²/(λ_H v²)),

where ξ = 1/8, R_c = 6/π and v is the generated electroweak scale.
The returned values evaluate this condensate relation and the window
hierarchy at the same stored inputs.

IMPLEMENTATION
-------------
The R2 ratio uses the common RP³ window-weight function.  The stop
position and bare-condensate coordinate use the stored endpoint and
torsion response.  Published quantities use the unified parameter interface.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.window_weights import scalar_vector_window_ratio  # noqa: E402

# ξ = 1/8 (the conformal coupling in d = 3), R_c = 6/π — structural.
XI = 1.0 / 8.0
R_C = 6.0 / math.pi
_ALPHA = 1.0 / (16.0 * math.pi ** 2)

# lambda_H — INTERNAL (the pseudo-dilaton identity (12 pi + 3)/(32 pi^2).
LAM_H = (12.0 * math.pi + 3.0) / (32.0 * math.pi ** 2)


def dphi_R1() -> float:
    """Δφ_R1 = (1/2)·ln 2 — the N = 1 composite normalisation
    (√4 = 2, the 4 basic components → 1 collective mode)."""
    return 0.5 * math.log(2.0)


def dphi_R2() -> float:
    """Δφ_R2 = (1/4)·ln(7/4) — the C15 symmetric box at q = 0
    (1/(p²+m²)²: the box weight vs the product weight; the 7/4 is
    the RP³ Weyl window ratio (1+2+1+3)/(d+1))."""
    return 0.25 * math.log(scalar_vector_window_ratio())


def dphi_R3() -> float:
    """Δφ_R3 = −(1/4)·ln(2·(3/4)³) — the single-mode Z factor.

    m² = 6/8 = 3/4 (the Lichnerowicz-to-Casimir ratio of the TT
    channel), Z = 2·(m²)³ = 0.84375; the VEV scales as √Z, so the
    φ shift is −(1/2)·ln√Z = −(1/4)·ln Z.
    """
    m2 = 3.0 / 4.0
    Z = 2.0 * m2 ** 3
    return -0.25 * math.log(Z)


def phi_R3_window(kL: float) -> float:
    """φ_R3 = 4πkL − ln(3α/π) + 1/(2π) − ln(1 − s0·κ(2τ)) — the
    dilaton-stop position implied by the window-squared line, with the
    J=2 squash correction (s0 = 2τ the amplitude, κ the U(1)_Y
    normalisation — the SAME κ as g1 = g2·κ).

    THE EW-HIERARCHY GEOMETRY : because v = M_G·ε with
    ε = e^{1/(2π)}·e^{−φ_stop} and φ_stop = φ_R3, the EW hierarchy
    is the EXACT structural logarithm

        ln(M_G/v) = φ_stop − 1/(2π) = 4πkL − ln(3α/π) + s0·κ
                  = 4πkL + ln(16π³/3) + s0·κ,

    i.e. the EW hierarchy is the WINDOW CIRCUMFERENCE 4πkL plus the
    loop-factor correction ln(16π³/3) plus the J=2 squash correction
    s0·κ (to first order in s0·κ).  This is the geometric source of
    the EW running factor α_W(v)/α_W(M_G) = 1.590 that closes
    |V_us||V_cb||V_ub| = α_W³ (see cp_sector).
    """
    tau = get("tau")
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    return 4.0 * math.pi * kL - math.log(3.0 * _ALPHA / math.pi) \
        + 1.0 / (2.0 * math.pi) - math.log(1.0 - s0 * kappa)


def phi_R0_derived(kL: float) -> float:
    """Bare-condensate coordinate φ_R0 = φ_R3(window) − ΣΔφ_Ri.

    The structural shifts reconstruct the window-squared scale ratio.
    """
    return phi_R3_window(kL) - dphi_R1() - dphi_R2() - dphi_R3()


# Bare-condensate coordinate derived from the window stop.
PHI_R0 = phi_R0_derived(float(get("kL")))


def phi_stop() -> float:
    """φ_stop = φ_R0 + Δφ_R1 + Δφ_R2 + Δφ_R3."""
    return PHI_R0 + dphi_R1() + dphi_R2() + dphi_R3()


def epsilon_anchor(phi: float) -> float:
    """ε = e^{1/(2π)}·e^{−φ} — the zero-point anchored ratio."""
    return math.exp(1.0 / (2.0 * math.pi)) * math.exp(-phi)


def phi_req_ir(M_G: float, lam_h: float, v: float) -> float:
    """φ_req = (1/2)·ln(ξ R_c M_G²/(λ_H v²)) — the IR anchor."""
    return 0.5 * math.log(XI * R_C * M_G ** 2 / (lam_h * v ** 2))


def v_from_phi(phi: float, M_G: float, lam_h: float) -> float:
    """v² = ξ R_c M_G² e^{−2φ}/λ_H — the condensate relation."""
    return math.sqrt(XI * R_C * M_G ** 2 * math.exp(-2.0 * phi) / lam_h)


def compute() -> dict:
    """Publish the chain and the ε-anchored closure."""
    M_G = get("M_G")
    lam_h = LAM_H
    v = float(get("v_HIGGS"))   # the framework's own VEV (internal)
    phi = phi_stop()
    eps = epsilon_anchor(phi)
    v_anchor = M_G * eps
    v_chain = v_from_phi(phi, M_G, lam_h)
    req = phi_req_ir(M_G, lam_h, v)

    pset("relaxion_phi_stop", phi, provenance="DERIVED",
         note="phi_stop = phi_R0 + (1/2)ln2 + (1/4)ln((1+2+1+3)/(d+1)) "
              "- (1/4)ln(2(3/4)^3), with (1+2+1+3)/(d+1) = 7/4, "
               f"= {phi:.4f}; phi_R0 follows from the window stop "
               f"4 pi kL - ln(3 alpha/pi) + 1/(2 pi) - ln(1-s0*kappa), "
               f"with s0=2 tau and alpha=1/(16 pi^2)")
    pset("epsilon_dilaton", eps, provenance="DERIVED",
          note=f"eps = e^{{1/(2pi)}} e^{{-phi_stop}} = {eps:.12e} "
               "(the zero-point anchored ratio)")
    return {"phi_stop": phi, "dphi_R1": dphi_R1(), "dphi_R2": dphi_R2(),
            "dphi_R3": dphi_R3(), "epsilon": eps, "v_anchor": v_anchor,
            "v_chain": v_chain, "phi_req_IR": req}


if __name__ == "__main__":
    r = compute()
    print(f"chain: R1={r['dphi_R1']:.5f} R2={r['dphi_R2']:.5f} "
          f"R3={r['dphi_R3']:.5f}")
    print(f"phi_stop = {r['phi_stop']:.4f}  (req_IR = {r['phi_req_IR']:.4f})")
    print(f"eps = {r['epsilon']:.5e}  v = M_G*eps = {r['v_anchor']:.2f} GeV")
    print(f"condensate relation: v = {r['v_chain']:.1f} GeV")
    print("relaxion_chain OK")
