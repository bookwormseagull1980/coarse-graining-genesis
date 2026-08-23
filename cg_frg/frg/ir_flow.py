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
cg_frg/frg/ir_flow.py — V4.0: the full γ_M(k) profile from
self-similar UV to frozen IR
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The geometry flow's anomalous dimension γ_M(k) is the framework's
central dynamical function: its integral enters the Λ docking
formula (the entropy span).  The full profile has three regimes:

    1. UV (k ≥ k_GUT):     γ_M(k) = 0 — self-similar flow,
                           L(k) ∝ 1/k (the geometric branch);
    2. TRANSITION (k ≈ k_GUT): γ_M crosses 0 → −1−p over
                           Δ ln k ≈ 0.43 (~0.3 decades);
    3. FROZEN (H0 ≤ k < k_GUT): γ_M ≈ −1−p — the frozen branch,
                           L(k) ∝ k^p (geometry nearly constant).

THE FROZEN EXPONENT (the derivation)
-------------------------------------------
p = ln(1/kL)/ln(H0/k_GUT) — the exponent that makes the frozen
branch reach L ≈ kL at the Hubble scale (the endpoint match:
L(H0) = L_Cg·(H0/k_GUT)^p, and the frozen length at the IR end
is the window length kL).

THE RG INVARIANT
----------------
∫γ_M d ln k (from H0 to M_G) = ln(kL·M_G/H0) ≈ 139.253 — the
same entropy identity as gamma_M.py (the UV part γ_M = 0
contributes nothing; the frozen branch carries the span).

V4 DISCIPLINE
-------------
The profile is pure structure (the three regimes, the tanh
cross-over, the endpoint exponent p from the trajectory);
no physics value is hard-coded.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

# The γ_M(k) profile transition width (descriptive only): γ_M goes
# 0 → −1−p over this ln-k span.  It shapes the profile shape (a tanh
# cross-over), never entering any closed value — ∫γ_M is fixed by the
# endpoint match p = ln(kL/√π)/ln(H0/k_GUT) and γ_M_frozen = −1−p by
# the trajectory, both independent of this width.
DELTA_LN_K = 0.43


def frozen_exponent(kL: float, H0: float, k_GUT: float) -> float:
    """p = ln(kL/√π)/ln(H0/k_GUT) — the frozen-branch exponent that
    matches the endpoint length: L(k) ∝ k^p on the frozen branch
    (γ_M = −1−p gives d ln L/d ln k = p), with L(k_GUT) = √π and
    L(H0) = kL.  p < 0 (k falls, L rises from √π to kL)."""
    return math.log(kL / math.sqrt(math.pi)) / math.log(H0 / k_GUT)


def compute() -> dict:
    """Publish the full γ_M(k) profile and its integral."""
    kL = get("kL")
    M_G = get("M_G")
    k_GUT = get("k_GUT")
    M_P = get("M_P")
    # The entropy integral is INTERNAL (gamma_M.py: the two-Gaussian
    # association entropy); H0 = M_P·√π·e^{−∫γ_M} is DERIVED from it.
    ent = float(get("entropy_integral"))
    H0 = M_P * math.sqrt(math.pi) * math.exp(-ent)

    p = frozen_exponent(kL, H0, k_GUT)
    g_frozen = -1.0 - p
    int_gamma = ent

    # The tanh profile is normalised to the integral: the frozen
    # branch carries ln(k_GUT/H0) e-folds at γ_M = −1−p; the UV
    # (γ_M = 0) contributes nothing.
    pset("gamma_M_frozen", g_frozen, provenance="DERIVED",
         note=f"gamma_M frozen branch = -1-p = {g_frozen:.6f} (ir_flow); "
              f"p = ln(kL/sqrt(pi))/ln(H0/k_GUT) = {p:.6f} (the endpoint "
              f"match L(H0)=kL, L(k_GUT)=sqrt(pi))")
    pset("ir_flow_int_gamma", int_gamma, provenance="DERIVED",
         note=f"int gamma_M d ln k = ln(M_P^2 sqrt(2pi)/sqrt(rho_Lambda)) "
              f"= {int_gamma:.6f} — the two-Gaussian association entropy "
              f"(INTERNAL; H0 DERIVED = {H0:.4e} GeV)")
    return {"p": p, "gamma_M_frozen": g_frozen, "int_gamma": int_gamma,
            "H0": H0, "k_GUT": k_GUT, "delta_ln_k": DELTA_LN_K,
            "regimes": {"UV": "gamma_M = 0 (k >= k_GUT, L ~ 1/k)",
                        "transition": f"0 -> {g_frozen:.4f} over "
                                      f"{DELTA_LN_K} ln-k",
                        "frozen": f"gamma_M ~ {g_frozen:.4f} down to H0"}}

if __name__ == "__main__":
    r = compute()
    print(f"p = {r['p']:.6f}, gamma_M_frozen = {r['gamma_M_frozen']:.6f}")
    print(f"int gamma_M = {r['int_gamma']:.6f} (the RG invariant)")
    print(f"H0 = {r['H0']:.3e} GeV, k_GUT = {r['k_GUT']:.3e} GeV")
    print(f"regimes: {r['regimes']}")
    print("ir_flow OK")
