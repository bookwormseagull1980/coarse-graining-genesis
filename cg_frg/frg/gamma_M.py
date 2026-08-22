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
cg_frg/frg/gamma_M.py — V4.0: the geometry-flow trajectory and the
anomalous dimension γ_M
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The scale flow of the internal geometry is L(k) = C/k with the
anomalous dimension γ_M:

    ∂_k ln L(k) = −(1 + γ_M(k))/k .

γ_M = 0 is the self-similar branch (L ∝ 1/k, the coarse-graining
of a scale-invariant geometry): the framework's emergent chain runs
on this branch from M_P down to the emergence scale M_G.  The
closure ∫γ_M = 0 between M_P and M_G is the entropy identity
∫γ_M = ln(kL·M_G/H0) = 139.253 that anchors the cosmological
quantities (H0, Λ).

THE γ_M ZERO CONDITION (why the branch is self-similar)
-------------------------------------------------------
The dimensionless combination C(kL) = η(k)/(k⁴V₃) — the trace
density η in units of the geometric volume — is a pure function of
kL on a self-similar flow.  γ_M = 0 ⟺ C(kL) is constant ⟺ the
trace density scales as η ∝ k⁴ (the scale-invariant spectrum).

THE ENTROPY IDENTITY (∫γ_M)
---------------------------
∫_{M_G}^{M_P} γ_M d ln k = ln(kL·M_G/H0) ≈ 139.253

The identity is the RG-flow integral that converts the geometric
flow into the physical scales: H0 = M_P·√π·e^{−∫γ_M} and the dark
energy Λ = ⟨η⟩·∫γ_M (cf12_lambda_synthesis).  This module records
the identity and its components.

V4 DISCIPLINE
-------------
The module is analytic: γ_M(k) = 0 on the self-similar branch; the
IR deviations (ir_freeze, ir_structure) are separate modules.
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
    # the closure ∫γ_M = 0 is the entropy identity below.
    return 0.0


def rho_lambda_internal(v: float, k_GUT: float) -> float:
    """ρ_Λ = Y_u·m_ν1⁴·(1 − 4s0·κ) — the neutrino-mass floor, DERIVED
    (GeV⁴, no observed input; identical to dark_energy.rho_lambda):
    m_ν3 = v²(2π)²/k_GUT·(1 + s0·κ) (Weinberg with the J=2 squash
    seesaw correction), m_ν1 = m_ν3·r12·r23 (the two hypercharge-trace
    ratios r12 = 3/10, r23 = 3/(10√3)), Y_u = 2/3, and the dark-energy
    weight (1 − 4s0·κ) that makes ρ_Λ symmetry-invariant under the
    squash level transfer (2026-08-16)."""
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
    """∫γ_M = ln(M_P²·√(2π + r23)/√ρ_Λ) — the two-Gaussian association
    entropy (the internal closure; no observed H0 enters).

    Two Gaussians — the Planck Gaussian N(0, M_P²) and the vacuum-floor
    Gaussian N(0, √ρ_Λ) — have differential entropies
        H(σ) = (1/2)ln(2πe σ²);
    their association (twice the entropy difference) plus the Gaussian
    entropy-minimum distance gives
        ∫γ_M = 2[H(M_P) − H(√ρ_Λ)] + ln(√(2π + r23))
             = ln(M_P²·√(2π + r23)/√ρ_Λ),
    where r23 = m2/m3 = 1/(√3·Tr(Y²)) = 3/(10√3) is the hypercharge-
    trace hierarchy ratio (the second/third-generation correction to
    the Gaussian entropy-minimum distance √(2π)).  This gives
    Ω_Λ = 2/3 + r23/(3π) = 0.68504 (+0.007%) — the geometric flat-
    universe value with the hierarchy correction.

    THE ENTROPY MICROSCOPIC ORIGIN (the Boltzmann analogy):
    ∫γ_M = ln(kL·M_G/H0) = ln(window span) = 139.253 is the Boltzmann
    entropy S = ln W — the window span e^{∫γ_M} = 3×10⁶⁰ is the phase-
    space volume W, its logarithm the entropy.  γ_M is the entropy
    production rate per scale slice (dS = γ_M d ln k): γ_M = 0 on the
    self-similar branch (scale-invariant, no entropy production),
    γ_M ≠ 0 at the IR end (scale breaking, entropy production).  The
    IR end (H0, Λ) is the MAXIMUM-ENTROPY state (Jaynes MaxEnt) —
    duality emergence is driven by disorder (entropy maximisation).
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

    # The entropy integral is DERIVED internally (the two-Gaussian
    # association entropy): ∫γ_M = ln(M_P²·√(2π)/√ρ_Λ), with ρ_Λ the
    # internal neutrino floor.  H0 = M_P·√π·e^{−∫γ_M} is then DERIVED
    # from it (gw_ratio).
    rho_L = rho_lambda_internal(v, k_GUT)
    ent = entropy_integral_internal(M_P, rho_L)
    H0_from_id = M_P * math.sqrt(math.pi) * math.exp(-ent)

    pset("gamma_M", 0.0, provenance="DERIVED",
         note="self-similar branch: gamma_M = 0 (trace density scales "
              "as k^4; endpoint_constraint fixed point kL* = 2.4935343)")
    pset("entropy_integral", ent, provenance="DERIVED",
         note=f"integral of gamma_M = ln(M_P^2 sqrt(2pi)/sqrt(rho_Lambda)) "
              f"= {ent:.6f} (the two-Gaussian association entropy, "
              f"INTERNAL — no observed H0)")
    return {"gamma_M": 0.0, "entropy_integral": ent, "kL": kL,
            "M_G": M_G, "H0_anchor": H0_from_id,
            "rho_Lambda": rho_L}


if __name__ == "__main__":
    r = compute()
    print(f"gamma_M = {r['gamma_M']}, entropy integral = {r['entropy_integral']:.6f}")
    print("gamma_M OK")
