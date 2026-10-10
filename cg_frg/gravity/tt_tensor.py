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
cg_frg/gravity/tt_tensor.py — V5.0: an internal-mode trajectory
diagnostic with G_TT ∝ k^{-2}
=================================================================

PURPOSE
-----------------------------------
This module evaluates a regulated internal-mode denominator along
the framework's self-similar trajectory L(k) = kL/k (γ_M = 0).
For the J = 2 mode, the implemented quantities are

    p²  = J(J+2)/L² = 8·k²/kL²   (the spatial eigenvalue)
    m²  = 6/L² = 6·k²/kL²        (the implemented curvature term)
    R_k = p²/(e^{p²/k²}−1)       (the exponential window)
    G_TT = 1/(p² + R_k + m²)

The tracker evaluates G_TT and the dimensionless product Z = p²·G_TT
over a finite range of RG scales k. The delta_forming flag checks
the following trajectory slopes:

    slope_G = d ln G_TT / d ln k < −1.5
    |slope_Z| < 0.5

Here p², m² and R_k all scale as k², so G_TT ∝ k^{-2} and constant
Z follow from the specified trajectory. The response variable here is the
RG scale k; an external spectral calculation uses Q² on a fixed background.

n_grav = 0 records the absence of an internal zero mode in this
implemented denominator: its lowest unregulated value is 14/L² > 0.
The external tensor channel uses its sourced propagation operator.

IMPLEMENTATION
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
    """G_TT and the product Z = p²·G_TT for one mode (J ≥ 2) at scale k.

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

    Returns G_TT and Z per k and their trajectory power laws.
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
    """Trajectory criterion: slope_G < −1.5, |slope_Z| < 0.5.

    The slopes are the log-log power laws of G_TT and Z across the
    sampled range (numpy polyfit, full precision). The retained key
    delta_forming records satisfaction of these two scale conditions.
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
    """Publish the fixed-trajectory scale diagnostics."""
    kL = get("kL")
    # Sample the trajectory with k in [M_G/30,M_G] and L=kL/k.
    M_G = get("M_G")
    k_vals = np.geomspace(M_G / 30.0, M_G, 60)
    tracker = tt_tracker(k_vals, kL)
    crit = analyze_delta(tracker)
    pset("TT_slope_G", crit["slope_G"], provenance="DERIVED",
         note="d ln G_TT / d ln k over the fixed trajectory L=kL/k")
    pset("TT_delta_forming", crit["delta_forming"], provenance="DERIVED",
         note="Trajectory scaling criterion: slope_G < -1.5 and |slope_Z| < 0.5")
    return {"criterion": crit, "n_grav": 0, "slope_G": crit["slope_G"],
            "slope_Z": crit["slope_Z"], "delta_forming": crit["delta_forming"]}


if __name__ == "__main__":
    r = compute()
    c = r["criterion"]
    print(f"slope_G = {c['slope_G']:.3f}, slope_Z = {c['slope_Z']:.4f}, "
          f"trajectory scaling criterion: {c['delta_forming']}")
    print(f"n_grav = {r['n_grav']} (no internal zero mode in this denominator)")
    print("tt_tensor OK")
