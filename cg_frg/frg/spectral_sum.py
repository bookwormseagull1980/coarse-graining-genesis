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
cg_frg/frg/spectral_sum.py — V5.0: finite-domain channel responses on RP³.

The channel functions evaluate the assigned zero-external-momentum
readouts on the projected spectrum supplied by iter_sm_spectrum:

    Π² = (1/V₃) Σ_{fields, modes} d_n · w(field) · I(λ_n, m²_eff),

where V₃ = π²L³ and I is the frequency integral of the channel
kernel with the selected window.  The kernel argument q² = ω²+λ_n
is an internal spectral variable, not external momentum.

The Gaussian response is defined on q² < 5Λ² with weight
exp(−q²/Λ²), where cutoff = Λ².  The finite domain R = 5 is a
separate readout choice; it does not follow from Gaussian
composition.  Raising quadrature accuracy within this domain does
not recover the omitted full-Gaussian tail.  The alternative
scheme key "litim" selects the implemented sharp frequency step.

Radius conventions (different objects; do not conflate):

* ``L`` in this module is the internal RP³ radius.  Production TT
  endpoint calls use ``L = kL = 2.493534...``.
* ``R = 5`` is the finite response-domain level, not an internal radius.
* ``sqrt(2*pi) = 2.506628...`` is the Gaussian correlation window's IR
  edge; Lean's ``CanonicalYangMills`` IR-edge model uses it.  It is not
  the TT endpoint: at that edge the TT readout is about ``0.147374``,
  below ``4/27``.
* ``sqrt(pi) = 1.772454...`` is the critical endpoint ratio, not an edge.

The TT kernel is K_TT(q²,m²) = q⁴/(q²+m²)².  Its readout enters
the normalised endpoint V₃Π²/(32π²) = 4/27 in endpoint_constraint.
That equality alone does not establish a massless external-momentum
pole or a positive pole residue.  The returned sign and emergence
labels are compatibility diagnostics for the assigned channel
readouts, not independent proofs of condensation or propagation.

The frequency integrals request quad epsabs=1e-14 and epsrel=1e-12.
These tolerances concern finite-domain quadrature; the returned
quadrature error estimates are not propagated as certified bounds.
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
from cg_core.window_weights import ResponseDomain, DEFAULT_RESPONSE_DOMAIN


# ---------------------------------------------------------------------------
# Frequency integrals (the ω-integration of the trace).
# ---------------------------------------------------------------------------
def _freq_integral_litim(kernel, lam: float, m2: float, cutoff: float) -> float:
    """∫₀^{√(Λ²−λ)} dω/π K(ω²+λ, m²) — the sharp frequency step.

    Modes with ω²+λ ≥ Λ² are removed entirely (the hard momentum
    cutoff).  The public scheme key for this implementation is "litim".
    """
    if lam >= cutoff:
        return 0.0
    a = math.sqrt(cutoff - lam)
    if a < 1e-40:
        return 0.0
    I, _ = quad(lambda w: kernel(w * w + lam, m2), 0.0, a,
                epsabs=1e-14, epsrel=1e-12, limit=200)
    return I / math.pi


def _freq_integral_gaussian(kernel, lam: float, m2: float, cutoff: float,
                            domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> float:
    """Finite-domain Gaussian integral of K(ω²+λ,m²) exp(−(ω²+λ)/Λ²).

    The upper limit is sqrt(max(5Λ²−λ, 0)), with cutoff = Λ².
    Thus R = 5 defines the response domain; it is not a quadrature
    tolerance or the full Gaussian integral.  The omitted tail is
    not included in the quadrature error estimate.
    """
    omega_max = domain.frequency_edge(lam, cutoff)
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
    l_max: int | None = None,
    domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN,
) -> tuple[float, dict]:
    """Π² = (1/V₃) Σ d_n w(field) I(λ_n, m²_eff) over the SM spectrum.

    The discrete sum replaces the flat-space continuum integral
    ∫d³p/(2π)³: the compactness of RP³ quantises the mode momenta,
    and the sum over the exact spectrum captures the topological
    content (zero modes, Killing forms) that the continuum misses.
    The RG scale of the mode loop is k = √Λ² (Planck units).
    """
    if scheme == "gaussian":
        freq = lambda kernel, lam, m2, cutoff: _freq_integral_gaussian(
            kernel, lam, m2, cutoff, domain)
    elif scheme == "litim":
        freq = _freq_integral_litim
        domain = ResponseDomain(1.0, domain.projection)
    else:
        raise ValueError(f"unknown scheme: {scheme}")

    domain.edge(cutoff)
    k_rg = math.sqrt(cutoff)
    V3 = volume(L)
    total = 0.0
    breakdown = {"gauge": 0.0, "fermion": 0.0, "scalar": 0.0, "ghost": 0.0}

    for kind, name, _mode, lam, m2, deg in iter_sm_spectrum(
            L, k_rg, tau, l_max=l_max, domain=domain):
        w = weight(kind, name)
        if abs(w) < 1e-40:
            continue
        c = freq(kernel, lam, m2, cutoff)
        total += deg * w * c / V3
        breakdown[kind] = breakdown.get(kind, 0.0) + deg * w * c / V3

    return total, breakdown


# ---------------------------------------------------------------------------
# The channel kernels (one-loop p = 0 operator amplitudes per d.o.f.).
# ---------------------------------------------------------------------------
def _kernel_tmunu_spin2(k2: float, m2: float) -> float:
    """q⁴/(q²+m²)² — the assigned TT kernel per scalar degree of freedom.

    The argument k2 represents internal q² = ω²+λ.  Away from the
    denominator guard, K_TT(q²,0)=1 for q²>0 and the kernel is
    nonnegative for q²,m² >= 0.  Curvature and torsion enter through
    m².  This kernel supplies a normalised endpoint response.
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
                        scheme: str = "gaussian", *,
                        domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    """The assigned spin-2 EMT response at zero external momentum.

    The value flat_pi0=0 records the Ward-normalised subtracted
    flat-space reference.  The kernel itself obeys K_TT(q²,0)=1
    for q²>0 away from its denominator guard.  The RP³ readout is
    the discrete sum below; its sign alone is not a pole criterion.
    """
    pi0, bd = _discrete_pi0(_kernel_tmunu_spin2, _w_tmunu_spin2,
                            L, cutoff, tau, scheme, domain=domain)
    return {
        "channel": "Tmunu (spin-2)", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "Ward-normalised subtracted flat-space amplitude"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_tmunu_spin0(L: float, cutoff: float, tau: float,
                        scheme: str = "gaussian", *,
                        domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    """The spin-0 T-mu-nu channel (the conformal-trace channel).

    Note on flat_pi0 = 0.0: same as the spin-2 channel — the
    flat-space Ward zero is the classification assertion (Guo (2026b, 2026f)),
    not the kernel's m²→0 limit (K₀(k², 0) = 1/3 > 0).
    """
    pi0, bd = _discrete_pi0(_kernel_tmunu_spin0, _w_tmunu_spin0,
                            L, cutoff, tau, scheme, domain=domain)
    return {
        "channel": "Tmunu (spin-0)", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (Guo (2026b, 2026f)), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_f2(L: float, cutoff: float, tau: float,
               scheme: str = "gaussian", *,
               domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    """F²: the gauge and fermion bubbles use different kernels; the
    total is their sum (the F² operator receives both
    contributions)."""
    pi_g, bd_g = _discrete_pi0(_kernel_f2_gauge, _w_f2_gauge,
                               L, cutoff, tau, scheme, domain=domain)
    pi_f, bd_f = _discrete_pi0(_kernel_f2_fermion, _w_f2_fermion,
                               L, cutoff, tau, scheme, domain=domain)
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
               scheme: str = "gaussian", *,
               domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    """G²: the gluon-condensate channel (SU(3) gluons only)."""
    pi0, bd = _discrete_pi0(_kernel_g2, _w_g2, L, cutoff, tau, scheme, domain=domain)
    return {
        "channel": "G2", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (Guo (2026b, 2026f)), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def channel_jmu(L: float, cutoff: float, tau: float,
                scheme: str = "gaussian", *,
                domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    """J^μ: the conserved-current channel (fermions only)."""
    pi0, bd = _discrete_pi0(_kernel_jmu, _w_jmu, L, cutoff, tau, scheme, domain=domain)
    return {
        "channel": "Jmu", "rp3_pi0": pi0,
        "flat_pi0": {"value": 0.0,
                     "source": "classification assertion (Guo (2026b, 2026f)), "
                               "NOT computed"},
        "breakdown": bd,
        "sign": "POSITIVE" if pi0 > 0 else "NEGATIVE",
        "emergence": "POSSIBLE (Pi0>0 on RP3)" if pi0 > 0 else "IMPOSSIBLE",
    }


def compute(L: float, cutoff: float, tau: float,
            scheme: str = "gaussian", *,
            domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    """All five channels at the given (L, cutoff, τ)."""
    return {
        "L": L, "cutoff": cutoff, "tau": tau, "scheme": scheme,
        "response_radius": domain.radius if scheme == "gaussian" else 1.0,
        "source_projection": domain.projection,
        "tmunu_spin2": channel_tmunu_spin2(L, cutoff, tau, scheme, domain=domain),
        "tmunu_spin0": channel_tmunu_spin0(L, cutoff, tau, scheme, domain=domain),
        "f2": channel_f2(L, cutoff, tau, scheme, domain=domain),
        "g2": channel_g2(L, cutoff, tau, scheme, domain=domain),
        "jmu": channel_jmu(L, cutoff, tau, scheme, domain=domain),
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
