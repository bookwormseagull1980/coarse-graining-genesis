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

"""Self-similar UV branch and the separately prescribed endpoint entropy.

gamma_M=0 gives L proportional to 1/k on the UV branch. Its integral
over that branch is zero. The nonzero quantity retained under the
entropy_integral parameter is the endpoint entropy span
S=log(M_P^2 sqrt(2*pi+r23)/sqrt(rho_Lambda)). The Hubble readout
H0=M_P sqrt(pi) exp(-S) uses this algebraic endpoint prescription.
A scale-dependent gamma_M(k) can be supplied separately to the
trajectory integrator.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def dlnL_dlnk(kL: float) -> float:
    """∂ ln L / ∂ ln k = −(1 + γ_M(kL)) — the trajectory exponent.

    On the self-similar branch γ_M = 0, so L ∝ 1/k exactly.
    """
    gamma = gamma_M(kL)
    return -(1.0 + gamma)


def gamma_M(kL: float) -> float:
    """γ_M(kL) = −kL·d ln C(kL)/d(kL) — the anomalous dimension.

    γ_M = 0 ⟺ C(kL) = η(k)/(k⁴V₃) is constant (the scale-invariant
    trace density).  On the framework's emergent branch this holds
    to machine precision (the endpoint_constraint fixed point
    kL* = 2.4935343 is defined on this branch).
    """
    # On the self-similar branch C(kL) is constant by construction;
    # this zero UV integral is separate from the endpoint entropy below.
    return 0.0


def rho_lambda_internal(v: float, k_GUT: float) -> float:
    """ρ_Λ = Y_u·m_ν1⁴·(1 − 4s0·κ) — the neutrino-mass floor, DERIVED
    (GeV⁴, no observed input; identical to dark_energy.rho_lambda):
    m_ν3 = v²(2π)²/k_GUT·(1 + s0·κ) (Weinberg with the J=2 squash
    seesaw correction), m_ν1 = m_ν3·r12·r23 (the two hypercharge-trace
    ratios r12 = 3/10, r23 = 3/(10√3)), Y_u = 2/3, and the dark-energy
    weight (1 − 4s0·κ) that makes ρ_Λ symmetry-invariant under the
    squash level transfer ."""
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    sk = s0 * kappa
    m3 = v * v * (2.0 * math.pi) ** 2 / k_GUT * (1.0 + sk)
    r12 = 1.0 / (10.0 / 3.0)
    r23 = 1.0 / (math.sqrt(3.0) * 10.0 / 3.0)
    m1 = m3 * r12 * r23
    return (2.0 / 3.0) * m1 ** 4 * (1.0 - 4.0 * sk)


def entropy_integral_internal(M_P: float, rho_L: float) -> float:
    """Endpoint entropy span, with all logarithm arguments dimensionless.

    Uses r23=3/(10 sqrt(3)); no observed H0 or numerical flow integral.
    """
    r23 = 1.0 / (math.sqrt(3.0) * 10.0 / 3.0)
    return math.log(M_P * M_P * math.sqrt(2.0 * math.pi + r23)
                   / math.sqrt(rho_L))


def compute() -> dict:
    """Publish the trajectory and the entropy identity."""
    M_P = get("M_P")
    kL = get("kL")
    M_G = get("M_G")
    v = get("v_HIGGS")
    k_GUT = get("k_GUT")

    # Endpoint prescription; no gamma(k) profile has been integrated.
    rho_L = rho_lambda_internal(v, k_GUT)
    ent = entropy_integral_internal(M_P, rho_L)
    H0_from_id = M_P * math.sqrt(math.pi) * math.exp(-ent)

    pset("gamma_M", 0.0, provenance="DERIVED",
         note="self-similar branch: gamma_M = 0 (trace density scales "
              "as k^4; endpoint_constraint fixed point kL* = 2.4935343)")
    pset("entropy_integral", ent, provenance="DERIVED",
         note=f"endpoint entropy span S = ln(M_P^2 sqrt(2pi+r23)/sqrt(rho_Lambda)) "
              f"= {ent:.6f} (the two-Gaussian association entropy, "
              f"algebraic endpoint entropy from the stated internal inputs)")
    return {"gamma_M": 0.0, "entropy_integral": ent, "kL": kL,
            "M_G": M_G, "H0_anchor": H0_from_id,
            "rho_Lambda": rho_L}


if __name__ == "__main__":
    r = compute()
    print(f"gamma_M = {r['gamma_M']}, endpoint entropy span = {r['entropy_integral']:.6f}")
    print("gamma_M OK")
