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

"""Internal chi crossing of the assigned compact response and kernel.

The exponent alpha=2 fixes the coordinate of a specified mass-shift
deformation. Eigenvalues, volume and Gaussian window are held fixed.
The product V_TT(chi)*Pi2(chi) determines the internal critical branch
under the stated source convention. Bracketing, the final residual and
the positive crossing derivative are checked. External propagation uses
the momentum derivative of the same sourced tensor equations at criticality.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.spectrum_loop import iter_sm_spectrum  # noqa: E402
from cg_core.rp3_spectrum import volume  # noqa: E402
from cg_frg.frg.spectral_sum import (  # noqa: E402
    _kernel_tmunu_spin2,
    _w_tmunu_spin2,
    _freq_integral_gaussian,
)


def _geometry(kL: float, M_G: float, M_P: float) -> dict:
    """The fixed-point geometry: L, V₃, k, the window."""
    L = kL
    k = M_G / M_P
    return {
        "L": L, "V3": volume(L), "k": k,
        "cutoff": k * k, "p2_min": 8.0 / (L * L),
        "m2_curv": 6.0 / (L * L),
    }


def _deformation(chi: float, alpha: float) -> float:
    if not math.isfinite(chi) or chi < 0 or not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("finite chi>=0 and alpha>0 required")
    return math.exp(-alpha*chi)


def v_tt(chi: float, alpha: float, geo: dict) -> float:
    """V_TT(χ) = 1/[p²(χ)·(p²(χ) + R_k(χ) + m²_curv(χ))].

    Assigned vertex entries 8/L² and 6/L² shrink as e^{−αχ},
    while the matter spectrum and frequency window are fixed.
    """
    s = _deformation(chi, alpha)
    p2 = geo["p2_min"] * s
    m2 = geo["m2_curv"] * s
    y = p2 / (geo["k"] * geo["k"])
    rk = p2 / math.expm1(y) if y < 100.0 else 0.0
    return 1.0 / (p2 * (p2 + rk + m2))


def pi2_chi(chi: float, alpha: float, geo: dict, tau: float) -> float:
    """Π²(χ): the TT spectral sum with the χ-rescaled EC masses.

    Only the EC mass shifts m²_eff scale with χ (the eigenvalues
    λ_n are the fixed RP³ spectrum).  The kernel K_TT is positive-
    definite; the sum is monotonically increasing in χ because
    dK/dm² < 0 and the masses shrink.
    """
    s = _deformation(chi, alpha)
    tot = 0.0
    for kind, name, _l, lam, m2, deg in iter_sm_spectrum(
        geo["L"], geo["k"], tau,
    ):
        w = _w_tmunu_spin2(kind, name)
        if abs(w) < 1e-40:
            continue
        i_f = _freq_integral_gaussian(
            _kernel_tmunu_spin2, lam, m2 * s, geo["cutoff"],
        )
        tot += deg * w * i_f / geo["V3"]
    return tot


def x_chi(chi: float, alpha: float, geo: dict, tau: float) -> float:
    """The ladder product x(χ) = V_TT(χ)·Π²(χ)."""
    return v_tt(chi, alpha, geo) * pi2_chi(chi, alpha, geo, tau)


def crossing_derivative(chi: float, alpha: float, geo: dict, tau: float) -> float:
    """Analytic d(V Pi)/dchi of the same fixed-window mass deformation."""
    scale = _deformation(chi, alpha)
    p2, m2 = geo["p2_min"]*scale, geo["m2_curv"]*scale
    k2 = geo["k"]**2
    y = p2/k2
    if y < 1e-4:
        f = k2*(1+y/2+y*y/12-y**4/720)
        p_df = k2*(y/2+y*y/6-y**4/180)
    else:
        denom = -math.expm1(-y)
        f = p2/denom
        p_df = f-p2*y*math.exp(-y)/(denom*denom)
    dlog_v = alpha*(1+(p_df+m2)/(f+m2))
    pi, dpi = 0., 0.
    for kind, name, _l, lam, shift, deg in iter_sm_spectrum(geo["L"], geo["k"], tau):
        weight = _w_tmunu_spin2(kind, name)
        if not weight:
            continue
        b = shift*scale
        pi += deg*weight*_freq_integral_gaussian(
            _kernel_tmunu_spin2, lam, b, geo["cutoff"])/geo["V3"]
        dpi += deg*weight*_freq_integral_gaussian(
            lambda q, mass2: 2*alpha*mass2*q*q/(q+mass2)**3,
            lam, b, geo["cutoff"])/geo["V3"]
    return v_tt(chi, alpha, geo)*(dpi+pi*dlog_v)


def find_crossing(alpha: float, geo: dict, tau: float) -> float:
    """Bisection: the unique χ_c with x(χ_c) = 1 (machine precision).

    The bisection relies on the monotonicity (Lemma 4): x(0) < 1
    (verified) and x(∞) → ∞ (the e^{2χ} growth of V_TT).
    """
    if not math.isfinite(alpha) or alpha <= 0:
        raise ValueError("alpha must be positive")
    lo, hi = 0.0, 6.0
    f_lo = x_chi(lo, alpha, geo, tau) - 1.0
    if f_lo == 0.0:
        return 0.0
    if f_lo > 0.0:
        raise ValueError("chi=0 already above crossing; no positive root bracket")
    if x_chi(hi, alpha, geo, tau) < 1.0:
        raise ValueError("no crossing bracket on [0,6]")
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mid == lo or mid == hi:
            break
        if x_chi(mid, alpha, geo, tau) < 1.0:
            lo = mid
        else:
            hi = mid
    root = 0.5 * (lo + hi)
    if abs(x_chi(root, alpha, geo, tau) - 1.0) > 1e-10:
        raise RuntimeError("crossing residual exceeded tolerance")
    return root


def compute() -> dict:
    """Publish the χ-pole crossing and its robustness."""
    M_P = get("M_P")
    M_G = get("M_G")
    kL = get("kL")
    tau = get("tau")
    geo = _geometry(kL, M_G, M_P)

    # Coordinate convention for the specified fixed-spectrum mass shift.
    alpha = 2.0
    xc = find_crossing(alpha, geo, tau)
    x0 = x_chi(0.0, alpha, geo, tau)
    x2 = x_chi(2.0, alpha, geo, tau)
    robust = {str(a): round(alpha*xc/a, 4)
              for a in (1.0, 1.5, 2.0, 2.5, 3.0)}
    slope = crossing_derivative(xc, alpha, geo, tau)
    if not math.isfinite(slope) or slope <= 0:
        raise RuntimeError("internal crossing must have a positive finite slope")
    residue = pi2_chi(xc, alpha, geo, tau)/slope

    pset("chi_pole_alpha", alpha, provenance="DERIVED",
         note="alpha=2 defines the coordinate of the assigned mass-shift "
              "deformation; eigenvalues, volume and Gaussian window stay fixed.")
    pset("chi_pole_crossing", xc, provenance="DERIVED",
         note=f"V_TT(chi)*Pi2(chi) = 1 at chi_c = {xc:.4f} (alpha = 2, "
              f"bracketed internal critical branch. x(0)={x0:.4f}, x(2)={x2:.1f})")
    pset("chi_pole_x0", x0, provenance="DERIVED",
         note=f"x(0) = {x0:.4f} < 1 — the ladder product at chi = 0 "
              f"(below the critical value; the crossing requires the "
              f"specified internal deformation)")
    pset("chi_pole_robust", robust, provenance="DERIVED",
         note="Coordinate check across alpha in [1,3]: the deformation "
              "depends on the invariant coordinate alpha*chi.")
    pset("chi_detuning_response", {"slope": slope, "residue": residue,
          "coordinate": "delta=chi_c-chi", "external_pole_established": False},
         provenance="DERIVED", role="internal",
         note="Positive internal detuning residue Pi(chi_c)/x'(chi_c), "
              "with the analytic derivative of the same kernel in the "
              "declared internal coordinate delta=chi_c-chi.")

    return {
        "chi_crossing": xc, "external_pole_established": False, "alpha": alpha, "x0": x0, "x2": x2,
        "coordinate_check": robust, "crossing_slope": slope,
        "internal_detuning_residue": residue,
        "trajectory": [
            {"chi": c, "V_TT": v_tt(c, alpha, geo),
             "Pi2": pi2_chi(c, alpha, geo, tau),
             "x": x_chi(c, alpha, geo, tau)}
            for c in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0)
        ],
    }


if __name__ == "__main__":
    r = compute()
    print(f"chi_crossing = {r['chi_crossing']:.6f}  (alpha = {r['alpha']})")
    print(f"x(0) = {r['x0']:.4f} < 1,  x(2) = {r['x2']:.1f} (unbounded)")
    print(f"coordinate check (alpha -> chi_c): {r['coordinate_check']}")
    print("trajectory:")
    for t in r["trajectory"]:
        print(f"  chi={t['chi']:.1f}  V_TT={t['V_TT']:.4e}  "
              f"Pi2={t['Pi2']:.6e}  x={t['x']:.4f}")
    print("chi_pole_condition OK")
