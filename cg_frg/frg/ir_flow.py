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

"""Endpoint-matched IR trajectory parametrization.

The frozen exponent matches the two declared dimensionless endpoint
lengths. The endpoint entropy span is supplied independently by gamma_M.
The trajectory is specified by its endpoint exponent. An explicitly supplied
gamma(k) is integrated by integrate_supplied_profile. The ir_flow_int_gamma
parameter records the endpoint entropy span.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

def frozen_exponent(kL: float, H0: float, k_GUT: float) -> float:
    """p = ln(kL/√π)/ln(H0/k_GUT) — the frozen-branch exponent that
    matches the endpoint length: L(k) ∝ k^p on the frozen branch
    (γ_M = −1−p gives d ln L/d ln k = p), with L(k_GUT) = √π and
    L(H0) = kL.  p < 0 (k falls, L rises from √π to kL)."""
    return math.log(kL / math.sqrt(math.pi)) / math.log(H0 / k_GUT)


def integrate_supplied_profile(gamma, k_start, k_end, L_start):
    """Integrate an explicitly supplied gamma(k), preserving orientation.

    Returns L_end from d ln L/d ln k=-(1+gamma). This verifies a supplied
    profile and does not select one from endpoint entropy. Quadrature error
    is an estimator, not an interval certificate or a physical uncertainty.
    """
    from scipy.integrate import quad
    if not all(math.isfinite(x) and x > 0 for x in (k_start, k_end, L_start)):
        raise ValueError("positive finite scales and initial length required")
    t0, t1 = math.log(k_start), math.log(k_end)
    integral, error = quad(lambda t: float(gamma(math.exp(t))), t0, t1,
                           epsabs=1e-11, epsrel=1e-11)
    log_length_ratio = -(t1-t0)-integral
    return {"integral_gamma_dlnk": integral, "quadrature_error_estimate": error,
            "log_length_ratio": log_length_ratio,
            "L_end": L_start*math.exp(log_length_ratio),
            "profile_selected_by_endpoint": False}


def compute() -> dict:
    """Publish endpoint matching and the separately prescribed entropy span."""
    kL = get("kL")
    M_G = get("M_G")
    k_GUT = get("k_GUT")
    M_P = get("M_P")
    # gamma_M supplies the endpoint entropy span used in the Hubble readout.
    ent = float(get("entropy_integral"))
    H0 = M_P * math.sqrt(math.pi) * math.exp(-ent)

    p = frozen_exponent(kL, H0, k_GUT)
    g_frozen = -1.0 - p
    int_gamma = ent

    # Publish the frozen-branch exponent and the endpoint entropy separately.
    pset("gamma_M_frozen", g_frozen, provenance="DERIVED",
         note=f"gamma_M frozen branch = -1-p = {g_frozen:.6f} (ir_flow); "
              f"p = ln(kL/sqrt(pi))/ln(H0/k_GUT) = {p:.6f} (the endpoint "
              f"match L(H0)=kL, L(k_GUT)=sqrt(pi))")
    pset("ir_flow_int_gamma", int_gamma, provenance="DERIVED",
         note=f"endpoint entropy S = ln(M_P^2 sqrt(2pi+r23)/sqrt(rho_Lambda)) "
              f"= {int_gamma:.6f} — the two-Gaussian association entropy "
              f"(endpoint prescription; H0 = {H0:.4e} GeV)")
    return {"p": p, "gamma_M_frozen": g_frozen, "int_gamma": int_gamma, "profile_integrated": False,
            "H0": H0, "k_GUT": k_GUT,
            "regimes": {"UV": "gamma_M = 0 (k >= k_GUT, L ~ 1/k)",
                        "transition": "profile supplied to integrate_supplied_profile",
                        "frozen": f"gamma_M ~ {g_frozen:.4f} down to H0"}}

if __name__ == "__main__":
    r = compute()
    print(f"p = {r['p']:.6f}, gamma_M_frozen = {r['gamma_M_frozen']:.6f}")
    print(f"endpoint entropy S = {r['int_gamma']:.6f}")
    print(f"H0 = {r['H0']:.3e} GeV, k_GUT = {r['k_GUT']:.3e} GeV")
    print(f"regimes: {r['regimes']}")
    print("ir_flow OK")
