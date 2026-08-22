# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
cg_frg/generation/lz_ladder.py — V4.0: the Landau-Zener generation
hierarchy
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The fermion mass ratios are the LZ ladder of the generation modes:
the extrusion of the modes n = {0, 2, 4} (window_capacity) by the
non-adiabatic squeezing of the scale flow suppresses the masses
exponentially,

    m_i ∝ e^{−α·n_i},   n = {0, 2, 4},

with the sector index α fixed by the internal ladder (sector_alpha):
    α_up = kL − 2τ = 2.453534  (the window width minus the torsion),
    m_t/m_c = e^{2α_up} = 135.2,
    m_c/m_u = e^{2kL_cmb + ln 4} = 571.6  (the CMB-window LZ of the
              first-gen step, times the n = 4 → 2 label factor),
    m_t/m_u = 77304.

The sector ladder (the down and lepton sectors) uses the step
Δ = 6(1−n_s)·kL_CMB = 0.52102 with the 9/8 hypercharge identity
(1/8 of the lepton step carries the down step):

    α_dn = α_up − (18/17)·Δ = 1.901862  (m_b/m_s = e^{2α_dn} = 44.87),
    α_lp = α_up − 2Δ = 1.411486       (m_τ/m_μ = e^{2α_lp} = 16.8).

The indices are the internal ladder (sector_alpha — no observed
calibration).  The absolute masses are anchored internally
(mass_operator_overlap); the first-generation ratios are CLOSED
first-principles: ×4 (up, the n=4→2 label factor ln 2²),
e^{−kL_CMB/3} (down, the so(4) 6-generator dilution), e^{√(2π)}
(lepton, the Euclidean period 2L = √(2π)).

V4 DISCIPLINE
-------------
The sector indices are the internal ladder (sector_alpha — the
window width minus the torsion, the 9/8 hypercharge identity, the
CMB window) — no observed calibration enters the computation.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def compute() -> dict:
    """Publish the LZ ladder ratios from the internal sector indices.

    The indices (alpha_up/alpha_down/alpha_lepton) are consumed
    from the store — written by the authoritative sector_alpha
    ladder.  The ratios are the LZ exponentials of the indices.
    """
    au = float(get("alpha_up"))       # the internal ladder (sector_alpha)
    ad = float(get("alpha_down"))
    al = float(get("alpha_lepton"))
    kL_cmb = float(get("kL_CMB"))     # the CMB-window first-gen step

    mt_mc = math.exp(2.0 * au)
    mb_ms = math.exp(2.0 * ad)
    mtau_mmu = math.exp(2.0 * al)
    mc_mu = math.exp(2.0 * kL_cmb + math.log(4.0))
    mt_mu = mt_mc * mc_mu
    # The down-sector first-generation step:
    # alpha_sd = alpha_dn - kL_CMB/6 (the CMB window over the so(4)
    # isometry's 6 generators — the colour dilution of the first-gen
    # extrusion).  m_s/m_d = e^{2 alpha_sd} = 19.7 vs 19.8 (-0.4%).
    alpha_sd = ad - kL_cmb / 6.0
    ms_md = math.exp(2.0 * alpha_sd)

    pset("m_t_over_m_c", mt_mc, provenance="DERIVED", role="internal",
         note=f"e^(2 alpha_up) = {mt_mc:.1f} (the internal alpha_up from "
              f"sector_alpha)")
    pset("m_b_over_m_s", mb_ms, provenance="DERIVED", role="internal",
         note=f"e^(2 alpha_dn) = {mb_ms:.2f} (the 9/8 ladder alpha_dn)")
    pset("m_t_over_m_u", mt_mu, provenance="DERIVED", role="internal",
         note=f"e^(2 alpha_up) e^(2 kL_CMB + ln4) = {mt_mu:.0f}")
    pset("alpha_sd", alpha_sd, provenance="DERIVED",
         note=f"alpha_sd = alpha_dn - kL_CMB/6 = {alpha_sd:.6f} (the down "
              f"first-gen step: CMB window over the so(4) 6 generators — "
              f"the colour dilution).  SYMMETRY FORM (2026-08-16): "
              f"alpha_sd = Delta_f(1 - s0/N_R) = (3/2)(1 - 2tau/7) = "
              f"{1.5*(1-2*0.02/7):.6f} (the fermion conformal weight "
              f"Delta_f = d/2 = 3/2 times the gravity-higher-order "
              f"correction 1 - s0/N_R; s0/N_R = n_broken/(N_f SigmaY2 N_R) "
              f"= 2/(15*(10/3)*7) = 1/175, HALF the J=2 EC first-order "
              f"torsion shift N_g tau/14 = 8tau/14, factor 2 = (d+1)/2; "
              f"matches the closure to -0.05%)")
    pset("m_s_over_m_d", ms_md, provenance="DERIVED", role="internal",
         note=f"m_s/m_d = e^(2 alpha_sd) = {ms_md:.2f} (the down first-gen "
              f"colour-dilution e^(2 a_dn - kL_CMB/3))")
    # The lepton first-generation:
    # m_mu/m_e = e^(2 alpha_lp + sqrt(2 pi)) — the extra factor
    # e^{sqrt(2 pi)} = the Euclidean period (2L = sqrt(2 pi)).
    mmu_me = math.exp(2.0 * al + math.sqrt(2.0 * math.pi))
    pset("m_mu_over_m_e", mmu_me, provenance="DERIVED", role="internal",
         note=f"m_mu/m_e = e^(2 alpha_lp + sqrt(2pi)) = {mmu_me:.1f} (the "
              f"lepton first-gen Euclidean-period factor e^{{sqrt(2pi)}})")
    return {"alpha_up": au, "alpha_down": ad, "alpha_lepton": al,
            "alpha_sd": alpha_sd,
            "m_t/m_c": mt_mc, "m_b/m_s": mb_ms, "m_t/m_u": mt_mu,
            "m_tau/m_mu": mtau_mmu, "m_c/m_u": mc_mu, "m_s/m_d": ms_md,
            "m_mu/m_e": mmu_me}


if __name__ == "__main__":
    r = compute()
    print(f"alpha_up = {r['alpha_up']:.4f}, alpha_dn = {r['alpha_down']:.4f}, "
          f"alpha_lp = {r['alpha_lepton']:.4f}, alpha_sd = {r['alpha_sd']:.4f}")
    print(f"m_t/m_c = {r['m_t/m_c']:.1f}, m_b/m_s = {r['m_b/m_s']:.1f}, "
          f"m_s/m_d = {r['m_s/m_d']:.1f}, m_mu/m_e = {r['m_mu/m_e']:.1f}")
    print("lz_ladder OK")
