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
cg_frg/gravity/zk_gravitational_rg.py — V5.0: Z(k) — the
gravitational wavefunction renormalisation and its scale running
=================================================================

PURPOSE
-----------------------------------
This module evaluates a finite-mode kinetic-normalisation prescription.
Z_geo is the
declared geometric background and Z_tot=Z_geo*exp(delta) is its
first-order logarithmic response. The diagnostic coupling convention is

    G_read(k) proportional to 1/Z_tot(k).

THE GEOMETRIC RUNNING (exact on the trajectory)
-----------------------------------------------
On the self-similar trajectory L(k) = L_Gg·M_G/k (kL = const),
the prescribed integrated three-dimensional curvature coefficient
Z_geo*L is held constant, giving

    Z(k) = Z_G·k/M_G,   Z_G = (M_P/M_G)²/(16π) = 0.03947

This relation specifies the geometric trajectory used in the calculation.

THE QUANTUM CORRECTION (one-loop estimate)
------------------------------------------
The matter-counting estimate uses assigned coefficients
+1 scalar / −2 Weyl fermion / +4 vector per degree of freedom,
in units of 1/(384π²), with its threshold average stated below:

    eta_corr = d ln(Z_tot/Z_geo)/d ln k
             = Σ_i c_i*d_i*khat²*f/(384π²*Z_geo*Lhat⁴).
    khat=k/M_G, Lhat=M_G*L, Z_geo=Z_G*khat.

with the EXACT RP³ mode counting (scalar J = 0,2,4… with
J(J+2) ≤ (kL)²; spinor n = 0,2,4… with (n+3/2)² ≤ (kL)²;
vector n = 1,3,5… with (n+1)² ≤ (kL)²), the SM content at M_G
(4 real scalars, 45 Weyl fermions, 24 vector polarisations), and
the threshold factor f evaluated at the average mode x̄ = 1/2
(the documented approximation).

The correction is evaluated on Z_geo, without feeding delta back into
the one-loop estimate. On Lhat=kL/khat it is eta_corr(khat)=eta_corr(1)
*khat^5, so the logarithmic integral has an exact elementary expression.
sqrt(exp(delta))-1 is the normalisation readout. M_P supplies the Planck
anchor. The total logarithmic derivative d ln Z_tot/d ln k is 1+eta_corr
at this order.

MODEL INPUTS
------------
The correction uses the prescribed
384π² normalisation, the threshold average x̄ = 1/2, and the
coefficients as the finite-mode kinetic-response assignment.
Mode counts refer to the explicitly declared scalar, selected spinor
branch and transverse vector catalogue. Spectral positivity and a tensor
pole are evaluated from the corresponding physical source response.
G_N=1/(8π*M_P²) remains the independent dimensional anchor.

PARAMETERS
----------
Reads : M_P, M_G, L_Gg (kL)
Writes: Z_G_dim, Z_quantum_shift, Z_geometric_ratio (DERIVED —
        this module is their writer)

IMPLEMENTATION
-------------
All inputs are internal (M_P, M_G, kL); the SM content (4/45/24)
is the framework's own content (sm_content); no observed value
enters the computation.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def rp3_mode_count(kL: float, spin: float) -> int:
    """Number of RP³ modes with spatial eigenvalue λ ≤ (kL)²/L².

    Exact per-sector counting from the RP³ spectra:
      scalar : J = 0,2,4,…  with J(J+2) ≤ (kL)²,   d_J = (J+1)²
      spinor : n = 0,2,4,…  with (n+3/2)² ≤ (kL)², d_n = (n+1)(n+2)
      vector : n = 1,3,5,…  with (n+1)² ≤ (kL)²,   d_n = 2n(n+2)
    """
    if not math.isfinite(kL) or kL < 0 or spin not in (0, 0.5, 1):
        raise ValueError("nonnegative finite kL and spin 0, 1/2 or 1 required")
    kL2 = kL * kL
    total = 0
    if spin == 0:
        J = 0
        while kL2 >= J * (J + 2):
            total += (J + 1) ** 2
            J += 2
    elif spin == 0.5:
        n = 0
        while (n + 1.5) ** 2 <= kL2:
            total += (n + 1) * (n + 2)
            n += 2
    elif spin == 1:
        n = 1
        while (n + 1.0) ** 2 <= kL2:
            total += 2 * n * (n + 2)
            n += 2
    return total


def z_dim(M_G: float, M_P: float) -> float:
    """Assigned dimensionless reference coefficient (not a pole residue)."""
    if not all(math.isfinite(v) and v > 0 for v in (M_G, M_P)):
        raise ValueError("positive finite M_G and M_P required")
    return (M_P / M_G) ** 2 / (16.0 * math.pi)


def geometric_Z(k_over_MG: float, Z_G: float) -> float:
    """Z(k) = Z_G·k/M_G — the geometric running on the kL-const
    trajectory (Z·L = const)."""
    if not all(math.isfinite(v) and v > 0 for v in (k_over_MG, Z_G)):
        raise ValueError("positive finite k/M_G and Z_G required")
    return Z_G * k_over_MG


def eta_N(k_over_MG: float, L: float, Z_background: float, dof: dict) -> float:
    """Assigned d ln(Z_tot/Z_geo)/d ln k on the supplied background.

        η_N = Σ_i c_i·d_i·(k²/(Z·L⁴))·f / (384π²)

    with c = (+1, −2, +4) per degree of freedom and the threshold
    factor f = (1−x̄)^{3/2}/(1+x̄)² evaluated at x̄ = 1/2.
    L is M_G*L_phys and k_over_MG is k/M_G. Z_background must be
    evaluated at this same k; the convention has the positive logarithmic
    derivative sign, not the often used anomalous-dimension minus sign.
    """
    if not all(math.isfinite(v) and v > 0 for v in (k_over_MG, L, Z_background)):
        raise ValueError("positive finite k, L and background Z required")
    if any(not math.isfinite(dof[name]) or dof[name] < 0
           for name in ("scalar", "fermion", "vector")):
        raise ValueError("finite nonnegative multiplicities required")
    kL = k_over_MG * L
    ns = rp3_mode_count(kL, 0)
    nf = rp3_mode_count(kL, 0.5)
    nv = rp3_mode_count(kL, 1)
    avg_x = 0.5
    f = (1.0 - avg_x) ** 1.5 / (1.0 + avg_x) ** 2
    dim_f = k_over_MG ** 2 / (Z_background * L ** 4)
    denom = 384.0 * math.pi ** 2
    return ((+dof["scalar"] * ns * dim_f * f
             - 2.0 * dof["fermion"] * nf * dim_f * f
             + 4.0 * dof["vector"] * nv * dim_f * f) / denom)


def logarithmic_correction(M_G: float, M_P: float, kL: float, dof: dict) -> float:
    """Exact integral of the assigned first-order eta on Z_geo and fixed kL."""
    if not math.isfinite(kL) or kL <= 0 or M_P < M_G:
        raise ValueError("positive kL and ordered positive mass scales required")
    Z_G = z_dim(M_G, M_P)
    initial = eta_N(1., kL, Z_G, dof)
    return initial * math.expm1(5.*math.log(M_P/M_G))/5.


def compute() -> dict:
    """Publish the Z(k) running and the quantum shift."""
    M_G = float(get("M_G"))
    M_P = float(get("M_P"))
    kL = float(get("kL"))

    Z_G = z_dim(M_G, M_P)
    dof = {"scalar": 4, "fermion": 45, "vector": 24}  # the SM content

    # The geometric ratio across the UV window:
    Z_geo_ratio = geometric_Z(1.0, Z_G) / geometric_Z(M_P / M_G, Z_G)

    dlnZ = logarithmic_correction(M_G, M_P, kL, dof)
    shift = math.expm1(0.5*dlnZ)
    verdict = ("NEGLIGIBLE" if abs(shift) < 0.01
               else "MARGINAL" if abs(shift) < 0.05 else "SIGNIFICANT")

    pset("Z_G_dim", Z_G, provenance="DERIVED", role="internal",
         note=f"Assigned Z_G=(M_P/M_G)^2/(16pi)={Z_G:.6f}; "
              f"reference coefficient of the geometric diagnostic")
    pset("Z_quantum_shift", shift, provenance="DERIVED", role="internal",
         note=f"Prescribed normalisation readout over the M_P-M_G window = "
              f"{shift:+.4%} [{verdict}] (Delta ln Z = {dlnZ:+.6e}; "
              f"the SM content 4 scalar + 45 Weyl + 24 vector, the "
              f"assigned 1/(384pi^2) coefficients; eta=d ln(Z_tot/Z_geo)/d ln k "
              f"evaluated on Z_geo=Z_G*k/M_G. No Planck anchor is changed.)")
    pset("Z_geometric_ratio", Z_geo_ratio, provenance="DERIVED",
         role="internal",
         note=f"Z(M_G)/Z(M_P) = {Z_geo_ratio:.4f} — the geometric "
              f"running Z(k) = Z_G*k/M_G across the UV window (exact "
              f"on the kL-const trajectory)")
    # A separate signed degree-of-freedom catalogue, not the weighted
    # eta coefficient and not a positivity or pole certificate.
    kL2 = kL * kL
    N_s, J = 0, 0
    while J * (J + 2) <= kL2:
        N_s += (J + 1) ** 2; J += 2
    N_f, n = 0, 0
    while (n + 1.5) ** 2 <= kL2:
        N_f += (n + 1) * (n + 2); n += 2
    N_v, m = 0, 1
    while (m + 1.0) ** 2 <= kL2:
        N_v += 2 * m * (m + 2); m += 2
    lay = {"scalar": 4 * N_s, "fermion": 90 * N_f, "gauge": 24 * N_v,
           "ghost": -48 * N_v}
    lay_total = sum(lay.values())
    pset("GN_layers", {**lay, "total": lay_total}, provenance="DERIVED",
         role="internal",
         note=f"Finite signed mode decomposition: scalar {lay['scalar']} + "
              f"fermion {lay['fermion']} + gauge {lay['gauge']} + ghost "
              f"{lay['ghost']} = {lay_total}; the coefficients use the "
              f"stated kinetic-response assignment")

    return {"Z_G": Z_G, "dlnZ": dlnZ, "M_P_shift": shift,
            "verdict": verdict, "Z_geo_ratio": Z_geo_ratio}


if __name__ == "__main__":
    r = compute()
    print(f"Z_G (dim)      = {r['Z_G']:.6f}")
    print(f"Z(M_G)/Z(M_P)  = {r['Z_geo_ratio']:.4f} (geometric)")
    print(f"quantum dlnZ   = {r['dlnZ']:+.6e}")
    print(f"M_P shift      = {r['M_P_shift']:+.4%}  [{r['verdict']}]")
    print("zk_gravitational_rg OK")
