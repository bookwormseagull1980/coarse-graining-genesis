# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#
#  DOI records:
#    [Software] 10.5281/zenodo.22067006
#    [Paper I]  10.5281/zenodo.22067118
#    [Paper II] 10.5281/zenodo.22067469
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#         DOI: 10.5281/zenodo.22067118
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
#         DOI: 10.5281/zenodo.22067469
# =============================================================================

"""
cg_frg/gravity/tt_tensor.py — V4.0: the TT propagator and the
spectral-pole identity G_TT ∝ k^{-2}
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The emergent graviton is the spectral pole of the transverse-
traceless (TT) propagator of the improved energy-momentum tensor.
On the framework's self-similar trajectory L(k) = kL/k (γ_M = 0),
the J = 2 TT mode has

    p²  = J(J+2)/L² = 8·k²/kL²   (the spatial eigenvalue)
    m²  = 6/L² = 6·k²/kL²        (the Lichnerovich shift)
    R_k = p²/(e^{p²/k²}−1)       (the exponential window)
    G_TT = 1/(p² + R_k + m²)

The tracker evaluates G_TT and the residue Z = p²·G_TT across an
IR range of k; the delta criterion decides whether the pole
survives:

    slope_G = d ln G_TT / d ln k  < −1.5   (G_TT grows as k^α with
                                           α < −1.5 — the k^{-2}-type
                                           pole approaching a delta)
    |slope_Z| < 0.5                        (the residue Z = p²·G_TT is
                                           k-independent — the
                                           massless-pole structure)

n_grav = 0: the lowest TT eigenvalue on RP³ is 14/L² > 0 (no TT
zero mode); the graviton is the spectral pole, not a zero mode.

V4 DISCIPLINE
-------------
The module is a pure engine: the input is the trajectory
(kL, the k range); no physics value is hard-coded.  numpy is used
for the polyfit slopes (full precision).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def tt_mode_propagator(k: float, J: int, L: float) -> dict:
    """G_TT and the residue Z for one TT mode (J ≥ 2) at scale k.

    p² = J(J+2)/L², m² = 6/L², R_k = p²/(e^{p²/k²}−1), G_TT =
    1/(p²+R_k+m²), Z = p²·G_TT.  For p²/k² ≳ 100 the regulator is
    exponentially suppressed and the mode enters the pure
    propagator regime.
    """
    k2 = k * k
    lam = float(J * (J + 2)) / (L * L)
    m2 = 6.0 / (L * L)
    y = lam / k2
    rk = lam / (math.exp(y) - 1.0) if y < 100.0 else 0.0
    den = lam + rk + m2
    g = 1.0 / den if den > 1e-300 else 1e300
    deg = (J + 1) * (J + 1)  # the scalar degeneracy on RP³
    return {
        "J": J, "p2": lam, "m2_curv": m2, "R_k": rk,
        "G_TT": g, "Z": lam * g if lam > 1e-300 else 0.0, "deg": deg,
    }


def tt_tracker(k_vals, kL_const: float) -> dict:
    """Track the lowest TT mode (J = 2) along L(k) = kL_const/k.

    Returns G_TT and Z per k — the power laws decide whether a
    delta-function pole develops at p² = 0 as k → 0.
    """
    kv = np.asarray(k_vals, dtype=np.float64)
    n = len(kv)
    out = {"k_vals": kv, "G_TT": np.zeros(n), "Z": np.zeros(n)}
    for i in range(n):
        k = kv[i]
        L = kL_const / k
        m = tt_mode_propagator(k, 2, L)
        out["G_TT"][i] = m["G_TT"]
        out["Z"][i] = m["Z"]
    return out


def analyze_delta(tracker: dict) -> dict:
    """The delta-function criterion: slope_G < −1.5, |slope_Z| < 0.5.

    The slopes are the log-log power laws of G_TT and Z across the
    IR range (numpy polyfit, full precision).
    """
    k = tracker["k_vals"]
    G = tracker["G_TT"]
    Z = tracker["Z"]
    ok = (k > 0) & (G > 0)
    if ok.sum() > 5:
        slope_G = float(np.polyfit(np.log(k[ok]), np.log(G[ok]), 1)[0])
    else:
        slope_G = float("nan")
    okz = (k > 0) & (Z > 1e-300)
    if okz.sum() > 5:
        slope_Z = float(np.polyfit(np.log(k[okz]), np.log(Z[okz]), 1)[0])
    else:
        slope_Z = float("nan")
    delta_forming = (
        not math.isnan(slope_G) and slope_G < -1.5
        and not math.isnan(slope_Z) and abs(slope_Z) < 0.5
    )
    return {"slope_G": slope_G, "slope_Z": slope_Z, "delta_forming": delta_forming}


def compute() -> dict:
    """Publish the pole identity at the fixed point."""
    kL = get("kL")
    # The IR range: from M_G down to M_G/30 (the pole develops as
    # k → 0 on the trajectory).
    M_G = get("M_G")
    k_vals = np.geomspace(M_G / 30.0, M_G, 60)
    tracker = tt_tracker(k_vals, kL)
    crit = analyze_delta(tracker)
    pset("TT_slope_G", crit["slope_G"], provenance="DERIVED",
         note="d ln G_TT / d ln k over the IR trajectory (the k^{-2}-type "
              "pole criterion)")
    pset("TT_delta_forming", crit["delta_forming"], provenance="DERIVED",
         note="the delta-function pole criterion (slope_G < -1.5, "
              "|slope_Z| < 0.5)")
    return {"criterion": crit, "n_grav": 0, "slope_G": crit["slope_G"],
            "slope_Z": crit["slope_Z"], "delta_forming": crit["delta_forming"]}


if __name__ == "__main__":
    r = compute()
    c = r["criterion"]
    print(f"slope_G = {c['slope_G']:.3f}, slope_Z = {c['slope_Z']:.4f}, "
          f"delta pole: {c['delta_forming']}")
    print(f"n_grav = {r['n_grav']} (no TT zero mode; the pole is spectral)")
    print("tt_tensor OK")
