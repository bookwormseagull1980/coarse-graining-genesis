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
cg_core/cluster_decay.py — V4.0: clustering verification of the
spectral-sum two-point function
====================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
Paper 4 (sec. 8, after Theorem [nomassless]) records that the
positive scalar mass m_δ > 0 implies exponential clustering of the
colour-singlet Schwinger functions — the spectral-sum-definition
analogue of the OS4 clustering axiom.  This module upgrades that
prose statement into a verified lemma by evaluating the reconstructed
two-point function numerically:

    S₂(d) = Σ_{l even} d_l · Δ_{M_l}(d),

    M_l = (λ_l + m_δ²)^{1/2},   λ_l = l(l+2)/L²,   d_l = (l+1)²
    (the RP³ Z₂-even scalar spectrum),

    Δ_M(d) = M K₁(M d)/(4 π² d)    (the massive four-dimensional
                                    Euclidean propagator at separation d > 0),

and checks the three statements of the lemma:

  (i)   Exponential rate (temporal).  C(τ) = Σ_l d_l e^{−M_l τ}/(2 M_l),
        the p = 0 projection, carries no power prefactor, so its
        log-slope equals −m_δ to machine precision.  Its τ → 0
        divergence is the contact singularity — this is why the
        clustering statement is made for separated points, as in OS4.
  (ii)  Zero-mode dominance (spatial).  S₂(d)/Δ_{m_δ}(d) → 1 as
        d → ∞: the l ≥ 2 tower decays with the larger rate
        M₂ − m_δ = (m_δ² + 8/L²)^{1/2} − m_δ > 0.  The spatial
        log-slope of S₂ carries the power prefactor of Δ_{m_δ},
        d/dd log S₂(d) = −m_δ − 3/(2d) + O(d⁻²) — verified
        against the finite-difference slope.
  (iii) Uniform bound.  S₂(d) ≤ C(d₀) e^{−m_δ d} for d ≥ d₀ with
        C(d₀) = e^{m_δ d₀} S₂(d₀), finite for every d₀ > 0; the
        scan shows the envelope S₂(d) e^{m_δ d} attains its maximum
        at d = d₀ (residual ≤ 1).

Units: dimensionless (L = 1, m_δ = 1 by default).  The statements are
scale-free: λ_l ≥ 0 for every l, hence M_l ≥ m_δ, and the zero mode
saturates the bound.  The physical-scale application is a rescaling:
with the framework's colour-singlet gap m_δ,phys and internal radius L,
every distance scales as d → d/(m_δ,phys L).

Writes (DERIVED, internal verification, no external input):
  cluster_temporal_slope     d/dτ log C(τ) at large τ (≈ −m_δ)
  cluster_zero_mode_ratio    S₂(d)/Δ_{m_δ}(d) at the largest d of the
                             scan (→ 1 from above)
  cluster_bound_constant     C(d₀) = e^{m_δ d₀} S₂(d₀)
  cluster_bound_residual     max_d S₂(d) e^{m_δ d}/C(d₀) over d ≥ d₀
                             (≤ 1, attained at d = d₀)
  cluster_rate_slope         finite-difference slope of log S₂ over
                             the fit window (matches −m_δ − 3/(2d̄))
"""

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scipy.special import k1  # noqa: E402

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.rp3_spectrum import scalar_modes  # noqa: E402


def propagator_4d(M: float, d: float) -> float:
    """Δ_M(d) = M K₁(M d)/(4 π² d) — the massive 4D Euclidean propagator."""
    if d <= 0.0:
        raise ValueError("separation d must be positive")
    return M * k1(M * d) / (4.0 * math.pi * math.pi * d)


def two_point(d: float, L: float = 1.0, m_delta: float = 1.0,
              l_max: int = 200) -> float:
    """S₂(d) = Σ_{l even} d_l Δ_{M_l}(d), M_l² = λ_l + m_δ².

    The reconstructed two-point function of the colour-singlet scalar
    on R⁴ × RP³ at equal internal point and Euclidean separation d
    in the R⁴ factor.
    """
    total = 0.0
    for l, lam, mult in scalar_modes(L, l_max):
        M = math.sqrt(lam + m_delta * m_delta)
        total += mult * propagator_4d(M, d)
    return total


def temporal_correlator(tau: float, L: float = 1.0, m_delta: float = 1.0,
                        l_max: int = 200) -> float:
    """C(τ) = Σ_{l even} d_l e^{−M_l τ}/(2 M_l) — the p = 0 temporal
    correlator (each internal mode contributes its massive propagator
    projected onto zero spatial momentum)."""
    total = 0.0
    for l, lam, mult in scalar_modes(L, l_max):
        M = math.sqrt(lam + m_delta * m_delta)
        total += mult * math.exp(-M * tau) / (2.0 * M)
    return total


def uniform_bound(d0: float, L: float = 1.0, m_delta: float = 1.0,
                  l_max: int = 200) -> float:
    """C(d₀) = e^{m_δ d₀} S₂(d₀) — the constant of the uniform bound
    S₂(d) ≤ C(d₀) e^{−m_δ d} for d ≥ d₀.  Finite for every d₀ > 0."""
    return math.exp(m_delta * d0) * two_point(d0, L, m_delta, l_max)


def log_slope(fn, d1: float, d2: float) -> float:
    """Finite-difference slope of log f over [d1, d2]."""
    return (math.log(fn(d2)) - math.log(fn(d1))) / (d2 - d1)


def compute(L: float = 1.0, m_delta: float = 1.0, l_max: int = 200,
            d0: float = 1.0, d_ratio: tuple = (10.0, 14.0, 18.0),
            d_fit: tuple = (10.0, 18.0),
            tau_fit: tuple = (10.0, 18.0),
            publish: bool = True) -> dict:
    """Run the three clustering checks and publish the results."""
    S = lambda d: two_point(d, L, m_delta, l_max)          # noqa: E731
    C = lambda t: temporal_correlator(t, L, m_delta, l_max)  # noqa: E731

    # (i) temporal rate — prefactor-free
    tslope = log_slope(C, *tau_fit)
    tdev = (tslope + m_delta) / m_delta

    # (ii) zero-mode dominance — the spatial exponential rate is m_δ
    ratios = [S(d) / propagator_4d(m_delta, d) for d in d_ratio]
    ratio_last = ratios[-1]
    # spatial finite-difference slope vs the power-prefactor prediction
    slope = log_slope(S, *d_fit)
    d_mid = 0.5 * (d_fit[0] + d_fit[1])
    expected = -m_delta - 3.0 / (2.0 * d_mid)
    prefactor_dev = abs(slope - expected)

    # (iii) uniform bound
    Cbound = uniform_bound(d0, L, m_delta, l_max)
    residual = 1.0
    for k in range(0, 40):
        d = d0 + 0.5 * k
        r = S(d) * math.exp(m_delta * d) / Cbound
        residual = max(residual, r)

    if publish:
        pset("cluster_temporal_slope", tslope, provenance="DERIVED",
         role="internal",
         note=f"d/dtau log C(tau) = {tslope:.9f} (fit over tau in "
              f"{tau_fit}, expect -m_delta = {-m_delta:.6f}; deviation "
              f"{tdev:.2e}; the p=0 correlator carries no power prefactor "
              f"so the rate is exact)")
        pset("cluster_zero_mode_ratio", ratio_last, provenance="DERIVED",
             role="internal",
             note=f"S2(d)/Delta_m(d) at d = {d_ratio}: {ratios} (-> 1 from "
                  f"above; the l>=2 tower decays with the larger rate "
                  f"M2 - m_delta > 0, so the spatial exponential rate is "
                  f"exactly m_delta)")
        pset("cluster_rate_slope", slope, provenance="DERIVED",
             role="internal",
             note=f"d/dd log S2 = {slope:.6f} (finite difference over "
                  f"{d_fit}) vs -m_delta - 3/(2 d_mid) = {expected:.6f} "
                  f"(K1 power prefactor d^(-3/2); |dev| = {prefactor_dev:.2e})")
        pset("cluster_bound_constant", Cbound, provenance="DERIVED",
             role="internal",
             note=f"C(d0={d0}) = e^(m_delta d0) S2(d0) = {Cbound:.6e} "
                  f"(the uniform bound S2(d) <= C(d0) e^(-m_delta d) "
                  f"for d >= d0, finite for every d0 > 0)")
        pset("cluster_bound_residual", residual, provenance="DERIVED",
             role="internal",
             note=f"max_d S2(d) e^(m_delta d)/C(d0) = {residual:.6e} over "
                  f"d >= d0 (expect <= 1, attained at d = d0; the bound "
                  f"is saturated by the zero mode)")

    return {"temporal_slope": tslope, "temporal_deviation": tdev,
            "zero_mode_ratio": ratio_last, "zero_mode_ratios": ratios,
            "rate_slope": slope, "prefactor_deviation": prefactor_dev,
            "bound_constant": Cbound, "bound_residual": residual}


def _self_test() -> None:
    r = compute()
    assert abs(r["temporal_deviation"]) < 1e-6, r
    assert abs(r["zero_mode_ratio"] - 1.0) < 1e-3, r
    assert r["bound_residual"] <= 1.0 + 1e-12, r
    assert r["prefactor_deviation"] < 1e-2, r
    # a second mass value: the statements are scale-free (no store writes)
    r2 = compute(L=1.0, m_delta=0.5, publish=False)
    assert abs((r2["temporal_slope"] + 0.5) / 0.5) < 1e-6, r2
    print(f"temporal slope    = {r['temporal_slope']:.9f} "
          f"(dev {r['temporal_deviation']:.2e})")
    print(f"zero-mode ratio   = {r['zero_mode_ratios']}  (-> 1)")
    print(f"spatial FD slope  = {r['rate_slope']:.6f} "
          f"(prefactor dev {r['prefactor_deviation']:.2e})")
    print(f"bound constant    = {r['bound_constant']:.6e}")
    print(f"bound residual    = {r['bound_residual']:.6e}  (<= 1)")
    print("cluster_decay OK (m_delta > 0 => exponential clustering)")


if __name__ == "__main__":
    _self_test()
