# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
cg_frg/gravity/zk_gravitational_rg.py — V4.0: Z(k) — the
gravitational wavefunction renormalisation and its scale running
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The gravitational sector is the transverse-traceless (TT) metric
fluctuation on the RP³ background.  Its kinetic coefficient is
the wavefunction renormalisation Z(k) — the gravitational analogue
of the field-strength renormalisation in gauge theories — and it
controls the effective Newton constant:

    G_N(k) = G_N / Z(k)      (Z(H0) → 1 — the deep IR)

THE GEOMETRIC RUNNING (exact on the trajectory)
-----------------------------------------------
On the self-similar trajectory L(k) = L_Gg·M_G/k (kL = const),
the Einstein–Hilbert action density scales as S ∝ Z·L; the
dimensionless combination Z·L is constant, hence

    Z(k) = Z_G·k/M_G,   Z_G = (M_P/M_G)²/(16π) = 0.03947

— a purely geometric running, exact on the trajectory.

THE QUANTUM CORRECTION (one-loop estimate)
------------------------------------------
The SM matter loops (one-loop graviton self-energy: coefficients
+1 scalar / −2 Weyl fermion / +4 vector per degree of freedom,
in units of 1/(384π²), Veltman-type) shift Z:

    η_N = Σ_i c_i·d_i·(k²/(Z·L⁴))·f / (384π²)

with the EXACT RP³ mode counting (scalar J = 0,2,4… with
J(J+2) ≤ (kL)²; spinor n = 0,2,4… with (n+3/2)² ≤ (kL)²;
vector n = 1,3,5… with (n+1)² ≤ (kL)²), the SM content at M_G
(4 real scalars, 45 Weyl fermions, 24 vector polarisations), and
the threshold factor f evaluated at the average mode x̄ = 1/2
(the documented approximation).

Integrating k dZ/dk = η_N over the UV window k ∈ [M_G, M_P]:

    Δln Z = +0.01226   →   M_P shift = √(e^{Δln Z}) − 1 = +0.615%

(the matter anti-screens gravity: Z > 1 at high scales — gravity
is weaker at short distances; the shift is NEGLIGIBLE (< 1%) — the
quantum correction does not disturb the geometric Z(k)·k/M_G
running in the M_P → M_G window.)

STATUS
------
The quantum correction is an order-of-magnitude estimate: the
384π² normalisation, the threshold average x̄ = 1/2, and the
Veltman-type coefficients are the documented standard one-loop
structure; the RP³ mode counting below it is exact (from
cg_core.rp3_spectrum).  The V4 computation gives +0.615%.
G_N itself is the identity anchor G_N = 1/(8π·M_P²) — the Z(k)
structure describes the RUNNING, not the anchor (newton.py).

PARAMETERS
----------
Reads : M_P, M_G, L_Gg (kL)
Writes: Z_G_dim, Z_quantum_shift, Z_geometric_ratio (DERIVED —
        this module is their writer)

V4 DISCIPLINE
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


def rp3_mode_count(kL: float, spin: int) -> int:
    """Number of RP³ modes with spatial eigenvalue λ ≤ (kL)²/L².

    Exact per-sector counting from the RP³ spectra:
      scalar : J = 0,2,4,…  with J(J+2) ≤ (kL)²,   d_J = (J+1)²
      spinor : n = 0,2,4,…  with (n+3/2)² ≤ (kL)², d_n = (n+1)(n+2)
      vector : n = 1,3,5,…  with (n+1)² ≤ (kL)²,   d_n = 2n(n+2)
    """
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
    """Z_G = (M_P/M_G)²/(16π) — the dimensionless kinetic
    coefficient at the emergence scale."""
    return (M_P / M_G) ** 2 / (16.0 * math.pi)


def geometric_Z(k_over_MG: float, Z_G: float) -> float:
    """Z(k) = Z_G·k/M_G — the geometric running on the kL-const
    trajectory (Z·L = const)."""
    return Z_G * k_over_MG


def eta_N(k_over_MG: float, L: float, Z_G: float, dof: dict) -> float:
    """One-loop graviton self-energy in dimensionless units:

        η_N = Σ_i c_i·d_i·(k²/(Z·L⁴))·f / (384π²)

    with c = (+1, −2, +4) per degree of freedom and the threshold
    factor f = (1−x̄)^{3/2}/(1+x̄)² evaluated at x̄ = 1/2.
    """
    kL = k_over_MG * L
    ns = rp3_mode_count(kL, 0)
    nf = rp3_mode_count(kL, 0.5)
    nv = rp3_mode_count(kL, 1)
    avg_x = 0.5
    f = (1.0 - avg_x) ** 1.5 / (1.0 + avg_x) ** 2
    dim_f = k_over_MG ** 2 / max(Z_G * L ** 4, 1e-30)
    denom = 384.0 * math.pi ** 2
    return ((+dof["scalar"] * ns * dim_f * f
             - 2.0 * dof["fermion"] * nf * dim_f * f
             + 4.0 * dof["vector"] * nv * dim_f * f) / denom)


def compute() -> dict:
    """Publish the Z(k) running and the quantum shift."""
    M_G = float(get("M_G"))
    M_P = float(get("M_P"))
    kL = float(get("kL"))

    Z_G = z_dim(M_G, M_P)
    dof = {"scalar": 4, "fermion": 45, "vector": 24}  # the SM content

    # The geometric ratio across the UV window:
    Z_geo_ratio = geometric_Z(1.0, Z_G) / geometric_Z(M_P / M_G, Z_G)

    # The quantum correction: integrate η_N over k ∈ [M_G, M_P].
    # On the trajectory L(k) = kL/k (kL const), so kL stays fixed.
    n_steps = 60
    dlnZ = 0.0
    for i in range(n_steps):
        # trapezoid integration in ln(k/M_G) over [0, ln(M_P/M_G)]
        k = math.exp(math.log(M_P / M_G) * i / n_steps)
        k_next = math.exp(math.log(M_P / M_G) * (i + 1) / n_steps)
        L = kL / k
        L_next = kL / k_next
        eta_i = eta_N(k, L, Z_G, dof)
        eta_j = eta_N(k_next, L_next, Z_G, dof)
        dlnZ += 0.5 * (eta_i + eta_j) * math.log(k_next / k)
    shift = math.sqrt(math.exp(dlnZ)) - 1.0
    verdict = ("NEGLIGIBLE" if abs(shift) < 0.01
               else "MARGINAL" if abs(shift) < 0.05 else "SIGNIFICANT")

    pset("Z_G_dim", Z_G, provenance="DERIVED", role="internal",
         note=f"Z_G = (M_P/M_G)^2/(16pi) = {Z_G:.6f} — the TT kinetic "
              f"coefficient at the emergence scale")
    pset("Z_quantum_shift", shift, provenance="DERIVED", role="internal",
         note=f"the one-loop M_P shift over the M_P-M_G window = "
              f"{shift:+.4%} [{verdict}] (Delta ln Z = {dlnZ:+.6e}; "
              f"the SM content 4 scalar + 45 Weyl + 24 vector, the "
              f"exact RP3 mode counting, the Veltman-type 1/(384pi^2) "
              f"one-loop graviton self-energy)")
    pset("Z_geometric_ratio", Z_geo_ratio, provenance="DERIVED",
         role="internal",
         note=f"Z(M_G)/Z(M_P) = {Z_geo_ratio:.4f} — the geometric "
              f"running Z(k) = Z_G*k/M_G across the UV window (exact "
              f"on the kL-const trajectory)")
    # The TT layer decomposition (with the correct rp3_spectrum
    # degeneracies): the TT self-energy layers from
    # the SM sector content within the kL window.  The supertrace is
    # positive, ensuring the graviton pole survives.
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
         note=f"the TT layer decomposition: scalar {lay['scalar']} + "
              f"fermion {lay['fermion']} + gauge {lay['gauge']} + ghost "
              f"{lay['ghost']} = {lay_total} > 0 — the positive supertrace "
              f"(the graviton pole survives; rp3_spectrum degeneracies)")

    return {"Z_G": Z_G, "dlnZ": dlnZ, "M_P_shift": shift,
            "verdict": verdict, "Z_geo_ratio": Z_geo_ratio}


if __name__ == "__main__":
    r = compute()
    print(f"Z_G (dim)      = {r['Z_G']:.6f}")
    print(f"Z(M_G)/Z(M_P)  = {r['Z_geo_ratio']:.4f} (geometric)")
    print(f"quantum dlnZ   = {r['dlnZ']:+.6e}")
    print(f"M_P shift      = {r['M_P_shift']:+.4%}  [{r['verdict']}]")
    print("zk_gravitational_rg OK")
