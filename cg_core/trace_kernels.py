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
cg_core/trace_kernels.py — V4.0: the Wetterich trace kernels
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The Wetterich flow of the effective potential is the supertrace of
the regulated propagator:

    ∂_t V_k = (1/V₃) Σ_{modes} d_n · w · C_mode(k, λ_n, m²_eff)

where C_mode is the q₀-integral of the trace kernel and w is the
supertrace weight of the species.  This module provides the kernel:
the exponential-window regulator, its scale derivative, and the
q₀-integrated mode contributions.  The spectrum iterator
(spectrum_loop) supplies the modes; this module supplies the
integration.

THE REGULATOR (the exponential window)
--------------------------------------
R_k(z) = z/(e^{z/k²} − 1)

This is the exponential coarse-graining window: it suppresses the
modes with z ≲ k² (the coarse-graining window) and vanishes for
z ≫ k², with the regulator convention R(0) = k² (finite).  The
scale derivative ∂_t R_k (t = ln k) is computed analytically.
The small-y and large-y branches (y = z/k²) avoid cancellation
errors:
    y → 0 : R_k → k² − z/2,   ∂_t R_k → 2k²(1 − y²/12)
    y ≫ 1 : R_k → 0,          ∂_t R_k → 0
The denominator z + R_k + m² is the full regulated propagator mass.

NOTE (2026-08-21): an earlier version of this docstring (and of
cg_core/frg_regulator) claimed R_k(z) = k²/(e^{z/k²}−1); that form
diverges as k⁴/z at z → 0 and is NOT the implemented window.  The
implemented window is z/(e^{z/k²}−1), identical in both files.

THE KERNEL AND THE WEIGHTS
--------------------------
The q₀-integrand is ∂_t R_k / ((q₀² + λ) + R_k + m²) / (2π).  The
mode contribution for one real bosonic degree of freedom is
+½ ∫ dq₀ (the ½ is the symmetric-integration factor); for one Weyl
fermion it is −1·∫ (the supertrace sign −1 times the two real
components of the Weyl — so a Weyl fermion weighs −2 relative to a
real boson, matching the Str(1) counting of the β-function
coefficient).

V4 DISCIPLINE
-------------
Full precision: math.pi, the q₀-integral with epsabs=1e-14,
epsrel=1e-12 (scipy.integrate.quad).  The Litim sharp-cutoff
regulator (for scheme-independence cross-checks) lives in
cg_core/frg_regulator.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

TWO_PI = 2.0 * math.pi


def _exponential_terms(z: float, k2: float, m2: float) -> tuple[float, float]:
    """(∂_t R_k, z + R_k + m²) for the exponential window.

    The small-y and large-y branches avoid cancellation errors in
    the difference e^y − 1 and in the exponential tail.
    """
    y = z / k2
    if y < 1e-10:
        dR = 2.0 * k2 * (1.0 - y * y / 12.0)
        den = k2 + m2 + z * 0.5
    elif y > 500.0:
        dR = 0.0
        den = z + m2
    else:
        ey = math.exp(y)
        em1 = ey - 1.0
        dR = 2.0 * z * y * ey / (em1 * em1)
        den = z / (1.0 - math.exp(-y)) + m2
    return dR, den


def boson_integrand(q0: float, lam: float, k2: float, m2: float) -> float:
    """∂_t R_k / ((q₀² + λ) + R_k + m²) / (2π) at frequency q₀.

    The overall weight (±½ or −1) is applied by the mode
    contributions, not here.
    """
    z = q0 * q0 + lam
    dR, den = _exponential_terms(z, k2, m2)
    return dR / den / TWO_PI


def fermion_integrand(q0: float, lam: float, k2: float, m2: float) -> float:
    """The fermionic integrand: the same kernel as the boson (the
    spin content enters through the spectrum and the supertrace
    sign only)."""
    return boson_integrand(q0, lam, k2, m2)


def _q0_range(k: float, lam: float) -> float:
    """The integration range: the exponential window suppresses
    q₀² + λ ≳ k², so integrate up to a generous multiple of k (and
    at least up to the scale set by λ when λ is large and positive).
    """
    k2 = k * k
    return max(10.0 * k, math.sqrt(max(0.0, 100.0 * k2 - lam)))


def boson_mode_contribution(k: float, lam: float, m2: float) -> float:
    """C_b = +½ ∫ dq₀/(2π) ∂_t R_k / (q₀²+λ+R_k+m²): the flow of one
    real bosonic mode (supertrace weight +1 per real DOF)."""
    from scipy.integrate import quad

    q_max = _q0_range(k, lam)
    result, _ = quad(
        lambda q0: boson_integrand(q0, lam, k * k, m2),
        -q_max, q_max,
        epsabs=1e-14, epsrel=1e-12, limit=400,
    )
    return 0.5 * result


def fermion_mode_contribution(k: float, lam: float, m2: float) -> float:
    """C_f = −∫ dq₀/(2π) ∂_t R_k / (q₀²+λ+R_k+m²): the flow of one
    Weyl fermion (two real components, supertrace sign −1 → weight
    −2 relative to a real boson)."""
    from scipy.integrate import quad

    q_max = _q0_range(k, lam)
    result, _ = quad(
        lambda q0: fermion_integrand(q0, lam, k * k, m2),
        -q_max, q_max,
        epsabs=1e-14, epsrel=1e-12, limit=400,
    )
    return -result


def _self_test() -> None:
    # The boson contribution at (k=1, λ=0, m²=0.1): the q₀-integral
    # must be positive and finite; the fermion must be −2× the
    # real-boson value at the same (λ, m²) (the two-component
    # weight).
    c_b = boson_mode_contribution(1.0, 0.0, 0.1)
    c_f = fermion_mode_contribution(1.0, 0.0, 0.1)
    assert c_b > 0.0
    assert math.isfinite(c_b)
    assert abs(c_f - (-2.0 * c_b)) < 1e-9
    print(f"trace_kernels self-test OK: C_b = {c_b:.8f}, C_f = {c_f:.8f}")


if __name__ == "__main__":
    _self_test()
