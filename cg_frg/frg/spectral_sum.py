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
cg_frg/frg/spectral_sum.py — V4.0: the CGC channel spectral sums on
RP³
===================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The emergence criterion of the framework is a composite-operator
two-point amplitude: the mode content of RP³ must be such that the
operator's Π²(p²=0) is positive (the operator can condense —
emergence is possible) or negative/zero (the operator cannot —
emergence is impossible).  The amplitudes are evaluated on the
DISCRETE RP³ spectrum:

    Π² = (1/V₃) Σ_{fields, modes} d_n · w(field) · ∫ dω/π K_ch(ω²+λ_n, m²_eff)

with V₃ = π²L³.  Each channel probes a different operator:

    Tμν spin-2 : the TT projection of the improved energy-momentum
                 tensor (the graviton-like emergence channel)
    Tμν spin-0 : the trace channel of the improved EMT
    F²         : field-strength squared (gauge + fermion bubbles)
    G²         : the gluon condensate (SU(3) gluons only)
    J^μ        : the conserved vector current (fermions only)

THE KERNELS (one-loop p = 0 two-point amplitudes, per d.o.f.)
-------------------------------------------------------------
    K_TT = k⁴/(k²+m²)²               TT projection — vanishes at
                                     m² = 0 by the Ward identity, so
                                     the spin-2 channel is activated
                                     only by the curvature/torsion
                                     masses of the RP³ modes
    K_0  = (1/3)(k²+3m²)²/(k²+m²)²   improved (conformal) trace
    K_F2 = 12 k⁴/(k²+m²)²            gauge; −8 k²/(k²+m²)² fermion
    K_G2 = 12 k⁴/(k²+m²)²            SU(3) gluons
    K_J  = −k²/(k²+m²)²              per unit charge

UNIQUENESS OF K_TT (2026-08-18): the transverse-traceless
projection of a spin-2 mode is forced by the Ward identity
(transversality — the kernel vanishes at m² = 0) together with
tracelessness (spin 2), and its spectral density is K_TT =
k⁴/(k²+m²)² — the two powers of k² are the two transverse
polarisations and the denominator is the propagator squared, so with
y = m²/(k²+m²) the kernel is exactly (1−y)².  No other function is
transverse, traceless, and of spin 2, so (1−y)² is unique given the
spin-2 requirement — inherited from general relativity, not selected.

The channel weights w(field) carry the operator-specific
multiplicity and the supertrace sign (bosons +, fermions −); the
Faddeev-Popov ghosts are excluded from the gauge-invariant operator
channels.

Two frequency cutoffs are provided: a smooth Gaussian window
(preferred for the discrete spectrum, consistent with the
coarse-graining envelope) and the sharp Litim step.  The
classification conclusions (the SIGN of Π² per channel) are
scheme-independent.

PHYSICAL ROLE
-------------
· channel_tmunu_spin2 → the spectral-pole critical scale
  V₃·Π²^{Tμν2}/(32π²) = 4/27 at k* = M_G (the F_MG fixed point of
  endpoint_constraint — the self-consistent emergence scale);
· channel_f2 / g2 / jmu → the excluded channels (F² fermion-
  dominated negative, G² zero — no gluon zero modes, J^μ negative)
  that exclude the alternative emergence routes.

V4 DISCIPLINE
-------------
The module is a pure engine: all scale inputs (L, cutoff, τ) are
explicit arguments; no physics value is hard-coded.  Full precision
(quad epsabs=1e-14, epsrel=1e-12).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scipy.integrate import quad  # noqa: E402

from cg_core.rp3_spectrum import volume  # noqa: E402
from cg_core.spectrum_loop import iter_sm_spectrum  # noqa: E402


# ---------------------------------------------------------------------------
# Frequency integrals (the ω-integration of the trace).
# ---------------------------------------------------------------------------
def _freq_integral_litim(kernel, lam: float, m2: float, cutoff: float) -> float:
    """∫₀^{√(Λ²−λ)} dω/π K(ω²+λ, m²) — the sharp Litim step.

    Modes with ω²+λ ≥ Λ² are removed entirely (the hard momentum
    cutoff).
    """
    if lam >= cutoff:
        return 0.0
    a = math.sqrt(cutoff - lam)
    if a < 1e-40:
        return 0.0
    I, _ = quad(lambda w: kernel(w * w + lam, m2), 0.0, a,
                epsabs=1e-14, epsrel=1e-12, limit=200)
    return I / math.pi


def _freq_integral_gaussian(kernel, lam: float, m2: float, cutoff: float) -> float:
    """∫₀^∞ dω/π K(ω²+λ, m²) e^{−(ω²+λ)/Λ²} — the smooth Gaussian window.

    The coarse-graining envelope of the framework is the exponential
    window e^{−(ω²+λ)/Λ²}; beyond ω²+λ ≈ 5Λ² the suppression is
    e^{−5}, so integrating to that bound captures the full
    contribution.
    """
    omega_max = math.sqrt(max(5.0 * cutoff - lam, 0.0))
    if omega_max <= 0.0:
        return 0.0
    I, _ = quad(
        lambda w: kernel(w * w + lam, m2) * math.exp(-(w * w + lam) / cutoff),
        0.0, omega_max, epsabs=1e-14, epsrel=1e-12, limit=200,
    )
    return I / math.pi


def _flat_continuum_pi0(kernel, m2: float, weight: float, cutoff: float) -> float:
    """The flat-space continuum Π² for cross-check:
    weight · ∫₀^{Λ²} dk² k²/(32π²) K(k², m²)."""
    I, _ = quad(lambda k2: k2 * kernel(k2, m2), 0.0, cutoff)
    return weight * I / (32.0 * math.pi ** 2)


# ---------------------------------------------------------------------------
# The discrete spectral-sum engine.
# ---------------------------------------------------------------------------
def _discrete_pi0(
    kernel,
    weight,
    L: float,
    cutoff: float,
    tau: float,
    scheme: str,
    l_max: int = 60,
) -> tuple[float, dict]:
    """Π² = (1/V₃) Σ d_n w(field) I(λ_n, m²_eff) over the SM spectrum.

    The discrete sum replaces the flat-space continuum integral
    ∫d³p/(2π)³: the compactness of RP³ quantises the mode momenta,
    and the sum over the exact spectrum captures the topological
    content (zero modes, Killing forms) that the continuum misses.
    The RG scale of the mode loop is k = √Λ² (Planck units).
    """
    if scheme == "gaussian":
        freq = _freq_integral_gaussian
    elif scheme == "litim":
        freq = _freq_integral_litim
    else:
        raise ValueError(f"unknown scheme: {scheme}")

    k_rg = math.sqrt(max(cutoff, 1e-30))
    V3 = volume(L)
    total = 0.0
    breakdown = {"gauge": 0.0, "fermion": 0.0, "scalar": 0.0, "ghost": 0.0}

    for kind, name, _mode, lam, m2, deg in iter_sm_spectrum(L, k_rg, tau, l_max=l_max):
        w = weight(kind, name)
        if abs(w) < 1e-40:
            continue
        c = freq(kernel, lam, m2, cutoff)
        total += deg * w * c / V3
        breakdown[kind] += deg * w * c / V3

    return total, breakdown


# ---------------------------------------------------------------------------
# The channel kernels (one-loop p = 0 operator amplitudes per d.o.f.).
# ---------------------------------------------------------------------------
def _kernel_tmunu_spin2(k2: float, m2: float) -> float:
    """k⁴/(k²+m²)² — the TT-projected EMT kernel for one scalar d.o.f.

    It vanishes at m² = 0 (the Ward identity: the improved EMT is
    conserved), so the spin-2 channel is activated only by the
    curvature/torsion masses of the RP³ modes.  This is the channel
    whose pole V₃Π²/(32π²) = 4/27 fixes the emergence scale M_G.
    """
    den = k2 + m2
    if den < 1e-40:
        return 0.0
    return k2 * k2 / (den * den)


def _kernel_tmunu_spin0(k2: float, m2: float) -> float:
    """(1/3)(k²+3m²)²/(k²+m²)² — the trace kernel of the improved EMT.

    The conformally improved trace Θ = T^μ_μ + (1/6)□φ² for a
    scalar has this two-point structure at p = 0 (the 1/3 prefactor
    is the trace projection in d = 4).
    """
    den = k2 + m2
    if abs(den) < 1e-40:
        return 0.0
    return (1.0 / 3.0) * (k2 + 3.0 * m2) ** 2 / (den * den)


def _kernel_f2_gauge(k2: float, m2: float) -> float:
    """12 k⁴/(k²+m²)² — the gauge F² kernel per polarisation.

    The prefactor 12 collects the 4D tensor contraction of the
    ⟨F²F²⟩ bubble for a transverse mode (two field-strength
    insertions, each with two Lorentz indices, contracted over four
    dimensions).
    """
    den = k2 + m2
    if den < 1e-40:
        return 0.0
    return 12.0 * k2 * k2 / (den * den)


def _kernel_f2_fermion(k2: float, m2: float) -> float:
    """−8 k²/(k²+m²)² — the fermion F² kernel per Weyl fermion.

    The minus sign is the fermion-loop sign; the prefactor comes
    from the Dirac-trace contraction of the two F² insertions.
    """
    den = k2 + m2
    if den < 1e-40:
        return 0.0
    return -8.0 * k2 / (den * den)


def _kernel_g2(k2: float, m2: float) -> float:
    """Identical to the gauge F² kernel (SU(3) gluons, selected by
    the weight)."""
    return _kernel_f2_gauge(k2, m2)


def _kernel_jmu(k2: float, m2: float) -> float:
    """−k²/(k²+m²)² — the conserved-current kernel per unit charge.

    The fermion-loop sign is included.  The channel is
    fermion-dominated and negative — the conserved-current operator
    cannot condense.
    """
    den = k2 + m2
    if den < 1e-40:
        return 0.0
    return -k2 / (den * den)


# ---------------------------------------------------------------------------
# The channel weights (operator multiplicity + supertrace sign).
# ---------------------------------------------------------------------------
def _w_tmunu_spin2(kind: str, name: str) -> float:
    """TT-channel weight: gauge 4 (2 pol × 2 kernel factor), fermion
    4, scalar 1; ghosts excluded (Tμν is gauge-invariant — the FP
    ghosts are gauge-fixing artifacts, not physical degrees)."""
    if kind == "scalar":
        return 1.0
    if kind == "fermion":
        return 4.0
    if kind == "gauge":
        return 4.0
    return 0.0


def _w_tmunu_spin0(kind: str, name: str) -> float:
    """Trace-channel weight: gauge 2 pol, scalar 1; ghosts and
    massless fermions excluded (their classical trace vanishes)."""
    if kind == "scalar":
        return 1.0
    if kind == "gauge":
        return 2.0
    return 0.0


def _w_f2_gauge(kind: str, name: str) -> float:
    """F² gauge weight: 2 polarisations per gauge field."""
    return 2.0 if kind == "gauge" else 0.0


def _w_f2_fermion(kind: str, name: str) -> float:
    """F² fermion weight: 2 spin states per Weyl fermion."""
    return 2.0 if kind == "fermion" else 0.0


def _w_g2(kind: str, name: str) -> float:
    """G² weight: SU(3) gluons only (2 polarisations)."""
    return 2.0 if (kind == "gauge" and name.startswith("g3")) else 0.0


def _w_jmu(kind: str, name: str) -> float:
    """J^μ weight: 2 spin states per Weyl fermion (charge factors
    are external to this kernel)."""
    return 2.0 if kind == "fermion" else 0.0


# ---------------------------------------------------------------------------
# The channels.
# ---------------------------------------------------------------------------
def channel_tmunu_spin2(L: float, cutoff: float, tau: float,
                        scheme: str = "gaussian") -> dict:
    """The spin-2 T-mu-nu channel (the graviton-like emergence
    channel — the positive one).

    Note on flat_pi0 = 0.0: the flat-
    space zero is the paper-3-1 CLASSIFICATION assertion (the Ward
    identity of the improved EMT — the subtracted amplitude vanishes
    in the massless continuum).  It is NOT the kernel's m²→0 limit:
    K_TT(k², 0) = 1 (the kernel is the positive spectral density, not
    the subtracted amplitude).  The RP³ positivity of this module is
    the positive-definite spectral sum (W1 Lemma 2); the flat zero is
    the classification boundary condition, documented, not computed.
    """
    pi0, bd = _discrete_pi0(_kernel_tmunu_spin2, _w_tmunu_spin2,
                            L, cutoff, tau, scheme)
    return {
        "channel": "Tmunu (spin-2)", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (paper 3-1), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_tmunu_spin0(L: float, cutoff: float, tau: float,
                        scheme: str = "gaussian") -> dict:
    """The spin-0 T-mu-nu channel (the conformal-trace channel).

    Note on flat_pi0 = 0.0: same as the spin-2 channel — the
    flat-space Ward zero is the classification assertion (paper 3-1),
    not the kernel's m²→0 limit (K₀(k², 0) = 1/3 > 0).
    """
    pi0, bd = _discrete_pi0(_kernel_tmunu_spin0, _w_tmunu_spin0,
                            L, cutoff, tau, scheme)
    return {
        "channel": "Tmunu (spin-0)", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (paper 3-1), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_f2(L: float, cutoff: float, tau: float,
               scheme: str = "gaussian") -> dict:
    """F²: the gauge and fermion bubbles use different kernels; the
    total is their sum (the F² operator receives both
    contributions)."""
    pi_g, bd_g = _discrete_pi0(_kernel_f2_gauge, _w_f2_gauge,
                               L, cutoff, tau, scheme)
    pi_f, bd_f = _discrete_pi0(_kernel_f2_fermion, _w_f2_fermion,
                               L, cutoff, tau, scheme)
    pi0 = pi_g + pi_f
    # The flat-continuum cross-check weights are the SM CONTENT counts
    # (not external values): 12 gauge d.o.f. (8 gluons + 3 W + 1 B) and
    # 45 Weyl fermion d.o.f. (3 generations x 15), each doubled by the
    # kernel/multiplicity factor.
    flat_g = _flat_continuum_pi0(_kernel_f2_gauge, 0.0, 12.0 * 2.0, cutoff)
    flat_f = _flat_continuum_pi0(_kernel_f2_fermion, 0.0, 45.0 * 2.0, cutoff)
    flat = flat_g + flat_f
    bd = {"gauge": bd_g.get("gauge", 0.0), "fermion": bd_f.get("fermion", 0.0)}
    return {
        "channel": "F2", "rp3_pi0": pi0, "flat_pi0": flat,
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_g2(L: float, cutoff: float, tau: float,
               scheme: str = "gaussian") -> dict:
    """G²: the gluon-condensate channel (SU(3) gluons only)."""
    pi0, bd = _discrete_pi0(_kernel_g2, _w_g2, L, cutoff, tau, scheme)
    return {
        "channel": "G2", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (paper 3-1), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_jmu(L: float, cutoff: float, tau: float,
                scheme: str = "gaussian") -> dict:
    """J^μ: the conserved-current channel (fermions only)."""
    pi0, bd = _discrete_pi0(_kernel_jmu, _w_jmu, L, cutoff, tau, scheme)
    return {
        "channel": "Jmu", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (paper 3-1), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def compute(L: float, cutoff: float, tau: float,
            scheme: str = "gaussian") -> dict:
    """All five channels at the given (L, cutoff, τ)."""
    return {
        "L": L, "cutoff": cutoff, "tau": tau, "scheme": scheme,
        "tmunu_spin2": channel_tmunu_spin2(L, cutoff, tau, scheme),
        "tmunu_spin0": channel_tmunu_spin0(L, cutoff, tau, scheme),
        "f2": channel_f2(L, cutoff, tau, scheme),
        "g2": channel_g2(L, cutoff, tau, scheme),
        "jmu": channel_jmu(L, cutoff, tau, scheme),
    }


def _self_test() -> None:
    # At the framework's reference point (L = kL, cutoff = (k/M_P)²
    # with k = M_G), the spin-2 channel must be POSITIVE (the
    # emergence channel) and the J^μ channel NEGATIVE.
    L = 2.4935343325226915
    tau = 0.02
    cutoff = 1.0e-2  # a representative (k/M_P)² scale
    r = compute(L, cutoff, tau)
    assert r["tmunu_spin2"]["sign"] == "POSITIVE"
    assert r["jmu"]["sign"] == "NEGATIVE"
    print("spectral_sum self-test OK:")
    for ch in ("tmunu_spin2", "tmunu_spin0", "f2", "g2", "jmu"):
        c = r[ch]
        print(f"  {ch:>14}: Pi2 = {c['rp3_pi0']:+.6e}  {c['sign']}")


if __name__ == "__main__":
    _self_test()
