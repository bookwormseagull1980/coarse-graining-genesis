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
cg_frg/framework/cp_sector.py — V5.0: the CP sector — the 8/7
left-right content ratio, the CKM/PMNS CP phases, the Jarlskog
invariant and the baryon asymmetry
=================================================================

PURPOSE
-----------------------------------
The CP sector records the framework's content-ratio classification
of the CP phases and the Jarlskog/baryon-asymmetry closure:

  THE 8/7 CONTENT RATIO (exact)
  -----------------------------
  The SM left/right Weyl-component ratio — 8 left-handed components
  in four weak doublets and 7 right-handed singlets per generation:
  Q_L(2×3), L_L(2), u_R(3), d_R(3), e_R(1)):

      n_L/n_R = 8/7 = 1.142857  (exact content classification)

  The PMNS CP phase (the lepton sector):
      δ_PMNS = (8/7)π.

  The CKM CP phase (the quark sector):
      δ_CKM = (8/7)π/N_c = 8π/21 ≈ 68.57°  (the colour-number
      dilution: the lepton-sector phase divided by N_c = 3)

  STATUS
  ------
  · the ratio 8/7 is exact (content classification); δ_CKM =
    8π/21 is DERIVED (the colour-number dilution δ_CKM =
    δ_PMNS/N_c = δ_PMNS/d, the internal-space dimension d = N_c = 3
    diluting the quark mixing phase, the lepton sector undiluted);
  · the baryon-asymmetry readout η_B = J·α_W²/56 combines the CP
    invariant, an assigned weak weight and the Weyl-content count.
    A dynamical interpretation specifies a baryon-number violating
    rate and the nonequilibrium evolution through symmetry breaking.

IMPLEMENTATION
-------------
No external value enters the computation: the 8/7 is the exact
content ratio, δ_CKM = 8π/21 and J are derived, η_B = J·α_W²/56
is the Sakharov content closure.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.gauge_running import run_geometric  # noqa: E402


def left_right_ratio() -> float:
    """n_L/n_R = 8/7 — the SM left/right Weyl-component ratio.

    8 left-handed components in four doublets: Q_L (2×3) + L_L (2) = 8;
    7 right-handed singlets: u_R (3) + d_R (3) + e_R (1) = 7.
    """
    return 8.0 / 7.0


def alpha_W_EW() -> float:
    """α_W(v) = g2(v)²/(4π) — the weak coupling at the EW scale, from
    the GEOMETRIC RGE (g1,g2,g3 run down from M_G with the geometric
    content y_0 = 1.0 held fixed; only the gauge couplings run)."""
    M_G = float(get("M_G"))
    v = float(get("v_HIGGS"))
    g1 = float(get("g1_MG_geo"))
    g2 = float(get("g2_MG"))
    g3 = float(get("g3_MG_geo"))
    g1, g2, g3 = run_geometric((g1, g2, g3), M_G, v)
    return g2 * g2 / (4.0 * math.pi)


def baryon_asymmetry(J: float, alpha_W: float) -> float:
    """η_B = J·α_W²/(n_L·n_R) = J·α_W²/56, the assigned effective readout.

    The effective readout combines the CP invariant, the assigned weak
    weight alpha_W^2 and the Weyl-content normalization 1/56. Its
    dynamical realization requires the baryon-number violating rate and
    a specified nonequilibrium history."""
    return J * alpha_W * alpha_W / 56.0


def compute() -> dict:
    """Publish the CP-sector pattern, the Jarlskog magnitude closure
    and the CKM/PMNS phases."""
    ratio = left_right_ratio()
    delta_over_pi = ratio                       # (8/7) = 1.142857

    # The Jarlskog MAGNITUDE closure: J = |V_us||V_cb||V_ub|*c12*c23*sin(delta).  The
    # framework's assigned CKM elements: |V_us| = sqrt(r_G)
    # (the Gatto dominant term), |V_ub| = sqrt(m_u/m_t) (the LZ
    # ladder); |V_cb| = sqrt(m_u/m_c) (the Gatto geometric element),
    # and sin(delta) from the DERIVED delta_CKM = (8/7) pi / 3 =
    # 8 pi / 21 (the left-right pattern per generation).
    V_us = math.sqrt(float(get("md_over_ms_geo")))   # Cabibbo source input r_G
    # |V_cb| = sqrt(m_u/m_c) — the Gatto-type geometric element:
    # m_u/m_c = e^{-2 alpha_up}/4 -> sqrt = e^{-alpha_up}/2.
    # ---- squash symmetry corrections  ----
    # V_cb (the 2-3 adjacent-generation mixing) carries −s0·κ (the
    # squash amplitude — the J=2 isometry breaking acting on the
    # adjacent generation); V_ub (the 1-3 cross-generation mixing,
    # charged) carries +τ·κ (the charged-quotient response, acting on the
    # cross-generation).  The adjacent-vs-cross generation distinction
    # selects the squash (s0 = 2τ) vs chiral (τ) content.
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    V_cb = math.exp(-float(get("alpha_up"))) / 2.0 * (1.0 - s0 * kappa)
    # sqrt(m_u/m_t): m_u/m_c = e^{-2 alpha_up}/4, m_c/m_t = e^{-2 alpha_up}
    # -> m_u/m_t = e^{-4 alpha_up}/4 -> sqrt = e^{-2 alpha_up}/2
    V_ub = math.exp(-2.0 * float(get("alpha_up"))) / 2.0 * (1.0 + tau * kappa)
    c12 = math.sqrt(1.0 - V_us ** 2)
    c23 = math.sqrt(1.0 - V_cb ** 2)
    # The CKM phase DIRECTION is DERIVED: delta_CKM = (8/7) pi / 3 =
    # 8 pi / 21 = 68.57 deg (the left-right pattern (8/7) pi per
    # generation — the PMNS pattern divided by the three generations,
    # rotating the direction from the third to the first quadrant).
    # sin(delta) follows directly — no Wolfenstein eta/rho_bar input.
    delta_ckm = ratio * math.pi / 3.0          # 8 pi / 21 = 68.57 deg
    sin_d = math.sin(delta_ckm)                # = 0.9306
    J = V_us * V_cb * V_ub * c12 * c23 * sin_d

    pset("cp_87_ratio", ratio, provenance="DERIVED", role="cg",
         note=f"n_L/n_R = 8/7 = {ratio:.6f} — the SM left/right content "
              f"ratio (8 left components in four doublets, 7 right singlets)")
    # The CKM phase DIRECTION (the left-right pattern per generation):
    # delta_CKM = (8/7) pi / 3 = 8 pi / 21 — the PMNS pattern (8/7)pi
    # divided by the three generations.  The quadrant differs from the
    # PMNS: the CKM sits in the first quadrant (68.6 deg, cos > 0)
    # while the PMNS sits in the third (205.7 deg, cos < 0) — the
    # per-generation division rotates the direction.
    d_ckm = ratio * math.pi / 3.0
    pset("ckm_delta_direction", d_ckm, provenance="DERIVED",
         role="cg",
         note=f"delta_CKM = (8/7) pi / N_c = 8 pi / 21 = "
              f"{math.degrees(d_ckm):.2f} deg — the COLOUR-"
              f"NUMBER dilution: delta_CKM = delta_PMNS/N_c, where "
              f"delta_PMNS = (n_L/n_R) pi = (8/7) pi (the lepton sector, "
              f"colourless) and N_c = 3 (the quarks carry 3 colours, so "
              f"their mixing phase is diluted by the colour number); "
              f"the quadrant differs from the PMNS (first vs third — the "
              f"1/N_c dilution rotates the direction); the 1/N_c dilution "
              f"= the internal-space-dimension dilution: the quark mixing "
              f"phase is diluted by d = 3 = N_c (the RP³ dimension = the "
              f"colour rank, the N_g·ξ = 1 unique solution), while the "
              f"lepton mixing (colourless, no colour dimension) is "
              f"undiluted)")
    pset("cp_pmns_87_pattern", delta_over_pi, provenance="DERIVED",
         role="cg",
         note=f"delta_PMNS/pi ~ (8/7) = {delta_over_pi:.6f} (the 8/7 content "
              f"ratio n_L/n_R: 8 left Weyl components vs 7 right singlets per "
              f"generation; the phase = (content ratio) × pi, the pi "
              f"being the complex-plane half-turn of maximal CP)")
    pset("cp_jarlskog_magnitude", J, provenance="DERIVED",
         role="cg",
         note=f"J = |V_us||V_cb||V_ub| c12 c23 sin(delta) = {J:.4e} (the "
              f"retained leading-angle Jarlskog readout with the framework's closed "
              f"|V_us|, |V_cb|, |V_ub| (Gatto geometric elements) and the "
              f"content phase delta_CKM = 8 pi / 21; c12 and c23 are "
              f"the positive cosines associated with the generated mixing "
              f"angles. The same mixing elements and phase enter the baryon "
              f"asymmetry readout.)")
    pset("cp_sector_status",
         "the 8/7 left-right content ratio (delta_PMNS ~ 1.14 pi); "
         "the CKM delta DERIVED (8 pi / 21 = 68.57 deg, the colour-number "
         "dilution); the Jarlskog magnitude closed at retained leading-angle order; "
         "the baryogenesis eta_B = J alpha_W^2/56 (Sakharov content)",
         provenance="DERIVED", role="informational",
         note="the CP sector status: the 8/7 content ratio exact, the "
              "CKM delta derived (8 pi / 21), the Jarlskog magnitude "
              "closed, the baryogenesis = J alpha_W^2/56")

    # The baryon asymmetry η_B = J·α_W²/56 — the Sakharov content.
    aW = alpha_W_EW()
    # NOTE : eta_B needs NO separate chiral-squash factor —
    # the V_cb (1−s0·κ) and V_ub (1+τ·κ) corrections above already carry
    # the squash content into J, and eta_B = J·α_W²/56 inherits it.
    # A separate (1−τ·κ) would double-count (J already −2.35% →
    # eta_B −0.15%).
    eta_B = baryon_asymmetry(J, aW)
    pset("eta_b", eta_B, provenance="DERIVED", role="cg",
         note=f"eta_B = J alpha_W^2/56 = {eta_B:.3e}: effective baryon-asymmetry "
              f"readout with CP invariant J, alpha_W(v) = {aW:.5f}, "
              f"assigned weak weight alpha_W^2 and Weyl-content factor "
              f"1/(n_L*n_R) = 1/56. Dynamical matching specifies the "
              f"baryon-number violating rate and nonequilibrium history.")

    return {"ratio": ratio, "delta_over_pi": delta_over_pi,
            "eta_b": eta_B}


if __name__ == "__main__":
    r = compute()
    print(f"n_L/n_R = 8/7 = {r['ratio']:.6f}")
    print(f"delta_PMNS/pi ~ (8/7) = {r['delta_over_pi']:.6f}")
    print(f"eta_B = J alpha_W^2/56 = {r['eta_b']:.3e} (Sakharov content)")
    print("cp_sector OK")
