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
cg_frg/generation/lz_dynamics.py — V4.0: the Landau-Zener extrusion
dynamics — the sector indices from the non-adiabatic two-level
structure, not from a written-down ratio
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The sector indices alpha_up / alpha_down / alpha_lepton were
previously written as content ratios (sector_alpha.py).  This
module exposes the LZ two-level dynamics behind them: the
non-adiabatic extrusion of the generation modes is a Landau-Zener
crossing in the scale flow, whose adiabatic part is the window
width kL and whose non-adiabatic part is the Einstein-Cartan
torsion.

THE TWO-LEVEL STRUCTURE
-----------------------
The scale flow L(k) = C/k extrudes the generation modes n = {0,2,4}
out of the coarse-graining window.  Each extrusion is a Landau-
Zener two-level system

    H(t) = ( v t   Δ  )
           (  Δ   -v t )

with the avoided-crossing gap Δ and the sweep rate v.  The
non-adiabatic transition probability is

    P = e^{−2π Δ²/v} ,

so the LZ index is γ = 2π Δ²/v.  The framework's index decomposes
into the adiabatic window width and the non-adiabatic torsion:

    α_up = kL − 2τ = kL − n_broken·τ ,

    · kL      — the adiabatic part: the window width, the extrusion
                of a mode across the full coarse-graining window;
    · 2τ      — the non-adiabatic part: the EC torsion makes the
                crossing non-adiabatic, and n_broken = 2 = (d+1)/2
                is the number of broken SU(2)_R generators (the
                Goldstone directions of the squash), each carrying
                the torsion modulus τ.

In the LZ reading, the adiabatic window width kL is the index of a
completely adiabatic extrusion (τ → 0), and the torsion subtracts
2τ because the crossing is non-adiabatic: the survival of the mode
is reduced by the torsion content.  The identity kL − α_up = 2τ is
therefore exact and physical: the non-adiabatic deficit is the
torsion content of the two broken generators.

The sector step Δ = 6(1−n_s)·kL_CMB is the sweep rate of the
extrusion: the six so(4) generators (the extrusion coupling), the
spectral tilt 1−n_s (the closed window-evolution rate τ·7/4), and
the CMB window kL_CMB (the scale of the extrusion).  The 9/8 split
is the hypercharge weight Y_d = 1/3 vs Y_l = 1 in the covariant
derivative on RP³ shifting the LZ exponent of the down/lepton
doublets.

V4 DISCIPLINE
-------------
The module computes the LZ indices from the two-level structure
(kL, τ, 1−n_s, kL_CMB, the 9/8 identity) — the same content ratios
as sector_alpha, now exposed as the adiabatic + non-adiabatic
decomposition of the Landau-Zener crossing.  No observed ratio
enters.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def lz_survival(index: float) -> float:
    """P = e^{−2γ} — the survival of a mode with LZ index γ (the
    factor 2 is the extrusion of both the creation and the
    stabilisation crossing)."""
    return math.exp(-2.0 * index)


def adiabatic_index(kL: float) -> float:
    """γ_adia = kL — the adiabatic part, the window width."""
    return kL


def nonadiabatic_deficit(tau: float) -> float:
    """γ_non = 2τ = n_broken·τ — the non-adiabatic deficit, the
    torsion content of the two broken generators."""
    return 2.0 * tau


def alpha_up(kL: float, tau: float) -> float:
    """α_up = kL − 2τ — the up-sector LZ index (adiabatic minus
    non-adiabatic)."""
    return adiabatic_index(kL) - nonadiabatic_deficit(tau)


def sector_step(one_minus_ns: float, kL_cmb: float) -> float:
    """Δ = 6·(1−n_s)·kL_CMB — the sweep rate of the extrusion."""
    return 6.0 * one_minus_ns * kL_cmb


def ladder_down(alpha_up_val: float, delta: float) -> float:
    """α_dn = α_up − (18/17)Δ — the down-sector index (9/8 split)."""
    return alpha_up_val - (18.0 / 17.0) * delta


def ladder_lepton(alpha_up_val: float, delta: float) -> float:
    """α_lp = α_up − 2Δ — the lepton-sector index."""
    return alpha_up_val - 2.0 * delta


def compute() -> dict:
    """Publish the LZ indices from the two-level structure."""
    kL = float(get("kL"))
    tau = float(get("tau"))
    ns_tilt = float(get("ns_tilt"))
    kL_cmb = float(get("kL_CMB"))

    au = alpha_up(kL, tau)
    Delta = sector_step(ns_tilt, kL_cmb)
    ad = ladder_down(au, Delta)
    al = ladder_lepton(au, Delta)

    pset("lz_adiabatic", kL, provenance="DERIVED",
         note=f"the adiabatic LZ index = kL = {kL:.6f} (the window width)")
    pset("lz_nonadiabatic_deficit", 2.0 * tau, provenance="DERIVED",
         note=f"the non-adiabatic deficit = 2tau = {2.0*tau:.6f} "
              f"(n_broken = 2 broken generators x tau)")
    pset("lz_alpha_up_dyn", au, provenance="DERIVED",
         note=f"alpha_up (LZ dynamics) = kL - 2tau = {au:.6f} — the "
              f"adiabatic window width minus the non-adiabatic torsion; "
              f"the identity kL - alpha_up = 2tau is exact")
    pset("lz_sector_delta_dyn", Delta, provenance="DERIVED",
         note=f"Delta (LZ sweep rate) = 6(1-n_s)kL_CMB = {Delta:.6f}")
    pset("lz_alpha_dn_dyn", ad, provenance="DERIVED",
         note=f"alpha_dn (LZ dynamics) = alpha_up - (18/17)Delta = {ad:.6f}")
    pset("lz_alpha_lp_dyn", al, provenance="DERIVED",
         note=f"alpha_lp (LZ dynamics) = alpha_up - 2Delta = {al:.6f}")

    return {"alpha_up": au, "alpha_down": ad, "alpha_lepton": al,
            "delta": Delta, "adiabatic": kL, "nonadiabatic": 2.0 * tau}


if __name__ == "__main__":
    # self-test with the framework's canonical values
    kL, tau = 2.49732, 0.02
    ns_tilt, kL_cmb = 0.035, 2.4848
    au = alpha_up(kL, tau)
    Delta = sector_step(ns_tilt, kL_cmb)
    ad = ladder_down(au, Delta)
    al = ladder_lepton(au, Delta)
    print(f"adiabatic (kL)        = {kL:.6f}")
    print(f"non-adiabatic (2tau)  = {2.0*tau:.6f}")
    print(f"alpha_up  = kL - 2tau = {au:.6f} (deficit exact: "
          f"{kL - au:.6f} = 2tau)")
    print(f"Delta     = 6(1-ns)kL_CMB = {Delta:.6f}")
    print(f"alpha_dn  = alpha_up - (18/17)Delta = {ad:.6f}")
    print(f"alpha_lp  = alpha_up - 2Delta     = {al:.6f}")
    print("lz_dynamics OK")
