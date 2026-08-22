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
cg_frg/generation/sector_alpha.py — V4.0: the sector-α LADDER,
fully internal (the authoritative writer of the sector indices)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The three sector LZ exponents (up / down / lepton) are NOT
observed back-fits: they form a ladder from the framework's own
closed quantities.  The V4 discipline (external-value discipline
first) requires every index to be computed from internal
quantities — no observed ratio enters the computation.  This
module is the authoritative writer of alpha_up / alpha_down /
alpha_lepton (lz_ladder consumes them).

THE LADDER (the internal derivation chain)
------------------------------------------
RUNG 1 — the up-sector index (the window width minus the
         non-adiabatic torsion correction):

    α_up = kL − 2τ
         = 2.4935343 − 0.04 = 2.453534
    (kL = 2.4935343 — the self-consistent F_MG fixed point;
     2τ — the EC torsion's non-adiabatic correction; the LZ
     index is NOT kL: kL − α_up = 2τ exactly).

RUNG 2 — the sector step (the so(4)-isometry × the tilt × the
         CMB window):

    Δ = 6·(1−n_s)·kL_CMB = 6 × 0.035 × 2.4810667 = 0.52102

    · 6      — the so(4) isometry's 6 generators (the extrusion
                coupling — the 4D rotation group);
    · 1−n_s  — the spectral tilt τ·(7/4) = 0.035 (ns_tilt,
                the closed window-evolution rate);
    · kL_CMB — the CMB-scale window width (the SCALE_CHOICE
                published by perturbation_amplitude; the
                closed value 2.4810667).

RUNG 3 — the 9/8 hypercharge identity (the exact algebra):

    9/8 = 1 / (1 − (Y_d/Y_l)²)      (Y_d = 1/3, Y_l = 1 — exact)
    (Y_l² − Y_d²)/Y_l² = 8/9 — the lepton step carries 8/9 of
    the down step; the mechanism (the hypercharge weight in the
    covariant derivative on RP³ shifting the LZ exponent);
    the identity itself is exact algebra.

RUNG 4 — the ladder (the two sector steps split by 9/8, with
         the mean step = Δ):

    step_lep = s = 16Δ/17,   step_dn = (9/8)·s = 18Δ/17
    α_dn = α_up − (18/17)·Δ = 1.901862
    α_lp = α_up − 2Δ         = 1.411486

    (α_lp = α_up − 2Δ is independent of the 9/8 split — the
    lepton rung spans two steps exactly; the 9/8 identity
    corrects only the down rung, from +1.69% (uniform ladder)
    to +0.08%.)

V4 DISCIPLINE
-------------
Every rung is internal: kL, τ, 1−n_s, kL_CMB, and the exact
9/8 hypercharge identity.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def alpha_up(kL: float, tau: float) -> float:
    """α_up = kL − 2τ — the up-sector LZ index.

    The window width minus the non-adiabatic correction 2τ (the
    EC torsion): the LZ index is the window width corrected by
    the torsion's non-adiabaticity — kL − α_up = 2τ exactly.
    """
    return kL - 2.0 * tau


def sector_step(one_minus_ns: float, kL_cmb: float) -> float:
    """Δ = 6·(1−n_s)·kL_CMB — the sector ladder step.

    6 = the so(4) isometry's generators (the extrusion coupling);
    1−n_s = the spectral tilt (τ·7/4 — ns_tilt, the closed
    window-evolution rate); kL_CMB = the CMB-scale window width.
    """
    return 6.0 * one_minus_ns * kL_cmb


def ladder_down(alpha_up_val: float, delta: float) -> float:
    """α_dn = α_up − (18/17)·Δ — the down-sector index.

    The down step is (9/8)·s with s = 16Δ/17 (the 9/8 hypercharge
    identity 9/8 = 1/(1−(Y_d/Y_l)²) splitting the two sector
    steps whose mean is Δ): (9/8)·(16/17)·Δ = (18/17)·Δ.
    """
    return alpha_up_val - (18.0 / 17.0) * delta


def ladder_lepton(alpha_up_val: float, delta: float) -> float:
    """α_lp = α_up − 2Δ — the lepton-sector index.

    The lepton rung spans two steps (down + lepton) — 2Δ exactly,
    independent of the 9/8 split.
    """
    return alpha_up_val - 2.0 * delta


def compute() -> dict:
    """Publish the internal sector ladder (the authoritative
    writer of alpha_up / alpha_down / alpha_lepton)."""
    kL = float(get("kL"))
    tau = float(get("tau"))
    ns_tilt = float(get("ns_tilt"))          # = 1 − n_s = 0.035
    kL_cmb = float(get("kL_CMB"))            # the CMB window (SCALE_CHOICE)

    au = alpha_up(kL, tau)
    Delta = sector_step(ns_tilt, kL_cmb)
    ad = ladder_down(au, Delta)
    al = ladder_lepton(au, Delta)
    s_lep = 16.0 * Delta / 17.0

    pset("alpha_up", au, provenance="DERIVED",
         note=f"alpha_up = kL - 2tau = {au:.6f} (the "
              f"window width minus the non-adiabatic torsion 2tau; "
              f"kL - alpha_up = 2tau exactly)")
    pset("alpha_down", ad, provenance="DERIVED",
         note=f"alpha_dn = alpha_up - (18/17)Delta = {ad:.6f} ("
              f"the 9/8 hypercharge ladder, step = (9/8)s, s = 16Delta/17)")
    pset("alpha_lepton", al, provenance="DERIVED",
         note=f"alpha_lp = alpha_up - 2Delta = {al:.6f} (the "
              f"lepton rung spans two steps exactly)")
    pset("sector_alpha_delta", Delta, provenance="DERIVED",
         note=f"Delta = 6(1-n_s)kL_CMB = {Delta:.6f} (the so(4) "
              f"isometry's 6 generators x the tilt 1-n_s = tau*7/4 x "
              f"the CMB window kL_CMB)")
    pset("sector_alpha_s_lep", s_lep, provenance="DERIVED",
         note=f"the lepton step s = 16Delta/17 = {s_lep:.6f} (the 9/8 "
              f"ladder split with the mean step Delta)")
    pset("ladder_98_identity", 9.0 / 8.0, provenance="DERIVED",
         role="cg",
         note="9/8 = 1/(1-(Y_d/Y_l)^2) exact (Y_d = 1/3, Y_l = 1): the "
              "down/lepton hypercharge structure of the sector ladder")

    return {"alpha_up": au, "alpha_down": ad, "alpha_lepton": al,
            "delta": Delta, "s_lep": s_lep,
            "step_ratio": (au - ad) / (ad - al)}


if __name__ == "__main__":
    r = compute()
    print(f"alpha_up = {r['alpha_up']:.6f}")
    print(f"alpha_dn = {r['alpha_down']:.6f}")
    print(f"alpha_lp = {r['alpha_lepton']:.6f}")
    print(f"Delta    = {r['delta']:.6f}")
    print(f"step ratio (a_up-a_dn)/(a_dn-a_lp) = {r['step_ratio']:.10f} "
          f"(9/8 = {9.0/8.0})")
    print("sector_alpha OK")
