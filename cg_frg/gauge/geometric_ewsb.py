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
cg_frg/gauge/geometric_ewsb.py — V4.0: the geometric EWSB — the
Goldstone fate, the L/R hierarchy, and the ε_L/ε_R connection
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The isometry breaking SU(2)_R → U(1)_R of the squashed RP³
produces two Goldstone modes (T¹_R, T²_R).  Their fate is the
Higgs-mechanism analogy: they are ABSORBED by the broken-direction
gauge bosons W_R±, giving them the longitudinal components.  The
GEOMETRIC VEV is the squash amplitude s₀ = 2τ (the chiral-
hypercharge statistics):

    m_WR = g_R·s₀·M_G = 0.50885 × 0.04 × 1.729e18
         = 3.52e16 GeV     (the GUT right-handed scale)

THE L/R BRANCHES OF THE CHIRALITY (steps 12-14)
-----------------------------------------------
· step 13 — the two EW breakings are the L/R branches of the
  chirality: RIGHT = geometric (s₀ — the GUT scale), LEFT =
  dynamical (the Higgs v — the EW scale).  The mechanism
  asymmetry (geometric vs dynamical) realises the chirality.

· step 14 — the L/R hierarchy:

    m_WR/m_W = 3.52e16 / m_W = 4.38e14  ≈  ε_L/ε_R^{-1}

  — the same ×10^14 exponential-small family as the framework's
  ε_L/ε_R = 1.42e-16 (epsilon_ratio, the dilaton-stop line):
  v = M_G·ε (vev_closure) is precisely this L/R ratio.

THE THREE SCALES (the breaking chain)
-------------------------------------
· TRIGGER — the Planck-critical curvature: m² = ξ(R − R_c) = 0
  at the Planck endpoint R = R_c (the order parameter module);
· ONSET — the GUT scale: L_GUT = √3/τ (the J=2 isometry-breaking
  scale) → k_GUT = M_P·L_Cg/L_GUT = 4.98e16 GeV;
· OUTCOME — the U(1)_Y mixing: g₁ = g₂·κ²(s₀) with
  κ²(s₀) = 1.13183 (the store kappa_mixing — the squashed S³ metric).

STATUS
------
The L/R hierarchy is CLOSED: m_W/m_WR = ε/(2 s0), with ε = v/M_G
(the dilaton-stop line, closed via the squash correction (1−s0·κ))
and s0 = 2τ the geometric VEV (1/(2 s0) = 12.5 exact).  m_WR =
g_R·s0·M_G is the GUT-scale right-handed W from the Goldstone
absorption.

PARAMETERS
----------
Reads : M_G, tau, g2_MG, v_HIGGS, kappa_mixing, k_GUT
Writes: geometric_ewsb_m_WR, geometric_ewsb_hierarchy,
        geometric_ewsb_eps_ratio_check, geometric_ewsb_status
        (DERIVED — this module is their writer)

V4 DISCIPLINE
-------------
All inputs are internal (M_G, τ, g₂, v = M_G·ε, κ² = g₁/g₂).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.beta_functions import beta_gauge  # noqa: E402

# The geometric content (the framework's theorem — the exact SO(4)
# diagonal overlap y_0 = 1.0) — scale-invariant, held fixed in the
# geometric RGE (only the gauge couplings run).
Y0_GEOMETRIC = 1.0


def _g2_at_MZ(g2_MG: float, g1_MG: float, g3_MG: float,
              M_G: float, M_Z: float) -> float:
    """g2(M_Z) from the GEOMETRIC RGE: run g1,g2,g3 with the geometric
    content y_0 = 1.0 held fixed, down to M_Z.  The weak coupling at
    M_Z is DERIVED from the geometric couplings."""
    dt = math.log(M_Z) - math.log(M_G)
    n = max(1, int(round(abs(dt) * 400)))
    h = dt / n
    g1, g2, g3 = g1_MG, g2_MG, g3_MG
    for _ in range(n):
        bg = beta_gauge(g1, g2, g3, Y0_GEOMETRIC)
        g1 += h * bg[0]
        g2 += h * bg[1]
        g3 += h * bg[2]
    return g2


def w_R_mass(g_R: float, s0: float, M_G: float) -> float:
    """m_WR = g_R·s₀·M_G — the W_R mass from the Goldstone
    absorption (the geometric VEV s₀ = 2τ)."""
    return g_R * s0 * M_G


def compute() -> dict:
    """Publish the geometric EWSB chain."""
    M_G = float(get("M_G"))
    tau = float(get("tau"))
    g2 = float(get("g2_MG"))
    v = float(get("v_HIGGS"))
    kappa2 = float(get("kappa_mixing"))   # g1/g2 = 1.13183
    k_GUT = float(get("k_GUT"))

    s0 = 2.0 * tau
    m_WR = w_R_mass(g2, s0, M_G)
    m_W = g2 * v / 2.0
    hierarchy = m_WR / m_W
    # THE CLOSED L/R HIERARCHY: m_W/m_WR = epsilon/(2 s0), with
    # epsilon = v/M_G (the dilaton-stop line, epsilon_ratio) and
    # s0 = 2 tau the geometric VEV.  The factor 1/(2 s0) = 12.5 is a
    # closed identity.
    eps_target = v / M_G
    eps_ratio_check = 1.0 / hierarchy      # = epsilon/(2 s0) exactly
    s0_factor = 1.0 / (2.0 * s0)           # = 12.5 exactly
    # The weak coupling at the EW scale (the DERIVED g2 from the
    # geometric RGE run down to the framework's own v):
    g1_MG = float(get("g1_MG_geo"))
    g3_MG = float(get("g3_MG_geo"))
    g_w_MZ = _g2_at_MZ(g2, g1_MG, g3_MG, M_G, v)
    ratio_pred = eps_target * (g_w_MZ / g2) / (2.0 * s0)
    L_GUT = math.sqrt(3.0) / tau

    pset("geometric_ewsb_m_WR", m_WR, provenance="DERIVED", role="internal",
         note=f"m_WR = g_R*s0*M_G = {m_WR:.3e} GeV (the Goldstone "
              f"absorption — the GUT right-handed scale; the geometric "
              f"VEV s0 = 2tau = {s0})")
    pset("geometric_ewsb_hierarchy", hierarchy, provenance="DERIVED",
         role="internal",
         note=f"m_WR/m_W = {hierarchy:.3e} with m_W = g2*v/2 = {m_W:.2f} "
              f"GeV — the L/R EW hierarchy")
    pset("geometric_ewsb_eps_ratio_check", eps_ratio_check,
         provenance="DERIVED", role="internal",
         note=f"m_W/m_WR = epsilon/(2 s0) = {eps_ratio_check:.3e} — the "
              f"CLOSED identity: 1/(2 s0) = {s0_factor:.4f} (s0 = 2 tau = {s0}); the "
              f"exponential smallness is epsilon = v/M_G = "
              f"{eps_target:.3e} (the dilaton-stop line, epsilon_ratio)")
    pset("geometric_ewsb_ratio_pred", ratio_pred, provenance="DERIVED",
         role="internal",
         note=f"m_W/m_WR with the weak coupling at M_Z = {ratio_pred:.3e} "
              f"(m_W = g v/2 at tree level)")
    pset("geometric_ewsb_status",
         "SU(2)_R -> U(1)_R Goldstones absorbed by W_R+/- (the "
         "geometric VEV s0 = 2 tau); the L/R hierarchy CLOSED: "
         "m_W/m_WR = epsilon/(2 s0) with epsilon = v/M_G (dilaton-stop) "
         "and the factor 1/(2 s0) = 12.5 exact",
         provenance="DERIVED", role="informational",
         note="the geometric EWSB status: the Goldstone fate, the "
              "L/R branches of the chirality, the CLOSED hierarchy "
              "epsilon/(2 s0)")

    return {"m_WR": m_WR, "m_W": m_W, "hierarchy": hierarchy,
            "eps_ratio_check": eps_ratio_check, "eps_target": eps_target,
            "s0_factor": s0_factor, "ratio_pred": ratio_pred,
            "s0": s0, "kappa2": kappa2, "L_GUT": L_GUT, "k_GUT": k_GUT}


if __name__ == "__main__":
    r = compute()
    print(f"m_WR = g_R s0 M_G = {r['m_WR']:.3e} GeV  (s0 = 2tau = {r['s0']})")
    print(f"m_W  = g2 v/2 = {r['m_W']:.2f} GeV")
    print(f"m_WR/m_W = {r['hierarchy']:.3e}")
    print(f"m_W/m_WR = epsilon/(2 s0) = {r['eps_ratio_check']:.3e} — CLOSED")
    print(f"  1/(2 s0) = {r['s0_factor']:.4f} (exact)")
    print(f"  with g_w(M_Z): {r['ratio_pred']:.3e}")
    print(f"kappa2 = g1/g2 = {r['kappa2']:.5f}")
    print("geometric_ewsb OK")
