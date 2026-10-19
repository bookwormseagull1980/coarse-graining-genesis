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
cg_frg/frg/endpoint_constraint.py — V5.0: the finite-domain TT endpoint.

This module computes the Guo (2026g) endpoint for the retained projected
content, torsion, and Gaussian response domain R = 5:

    V₃·Π²^{Tμν2}/(32π²) = 4/27 at k* = M_G,
    M_G = M_P·L_Cg/kL*,   k_GUT = M_P·L_Cg/L_GUT,   L_GUT = √3/τ,
    g₂ = √8·(M_G/M_P)·kL*^{−3/2}.

The value 4/27 = max_{0≤y≤1} y(1−y)² normalises the specified
zero-external-momentum TT response.  This endpoint calculation does
not compute an external-momentum massless pole or its residue.
The Gaussian composition law fixes the envelope, not the separate
choice R = 5; the full Gaussian domain defines a different response.

Radii used here (these are different objects; do not conflate them):

* ``R = 5``: the finite response-domain level in ``q^2 < R*Lambda^2``.
  It is not an internal-space radius.
* ``L_Cg = sqrt(pi)``: the critical endpoint **ratio**, not an edge and
  not the TT endpoint.
* ``kL``: the TT endpoint internal-radius coordinate, the root of
  ``A(L) = 4/27`` at ``k = M_G``.  The V5 production value is
  ``kL = 2.4935343325...``.
* ``irEndpoint = sqrt(2*pi)`` and ``uvEndpoint = sqrt(2)``: the IR and UV
  edges of the Gaussian correlation window.  ``sqrt(2*pi)`` is **not**
  the TT endpoint: at that edge the TT sum is about ``0.147374``, below
  ``4/27``.  The Lean ``CanonicalYangMills`` IR-edge model uses
  ``sqrt(2*pi)``; V5 uses ``kL`` and never substitutes the edge.

On a fixed content and projection branch, the endpoint equation has
the form F_R(c) = A_R/c − 4/27 with A_R > 0, and hence one positive
root c = 27 A_R/4.  This is conditional uniqueness for that response
definition.  The floating-point iteration below is not an interval
certificate of the root or of the quadrature error.

With L_Cg = sqrt(pi), the module publishes kL, L_Gg, M_G, and the
bare Killing-normalisation coupling g2_MG_bare_constraint.  The
corrected g2_MG is published separately by geometric_couplings.
It also records L_critical = L_Cg_star = sqrt(pi) and R_c_star = 6/pi.
The dimensionless outputs M_G/M_P and g₂ are independent of the
absolute Planck anchor for fixed dimensionless inputs.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_frg.frg.spectral_sum import channel_tmunu_spin2  # noqa: E402
from cg_frg.gauge.zero_mode_reduction import register_gauge_scale_factor  # noqa: E402

# Normalised TT-response endpoint.  For internal spectral q²,
# y = m²/(q²+m²) gives K_TT = (1−y)² and max y(1−y)² = 4/27.
# A massless pole additionally requires an external-momentum response
# with the appropriate inverse-response zero and positive source residue.
CRIT = 4.0 / 27.0
FACTOR = 32.0 * math.pi ** 2


def threshold_geometry() -> dict:
    """The extremum geometry of the mass-weighted density ρ(y)=y(1−y)².

    Returns the unique interior maximum, its curvature, and the
    quadratic approximation to the relative threshold decrease.
    The exact expansion is ρ(1/3+Δy) = 4/27 − (Δy)² + (Δy)³.
    The returned band retains only (27/4)·(Δy)², with
    Δy = frac·y_max.  It is not a rigorous two-sided error bound.
    """
    y_max = 1.0 / 3.0
    rho_max = y_max * (1.0 - y_max) ** 2        # 4/27
    curvature = abs(6.0 * y_max - 4.0)          # |ρ''(1/3)| = 2
    band = {f"{frac:.0%}": (27.0 / 4.0) * (frac * y_max) ** 2
            for frac in (0.03, 0.10, 0.30)}
    return {"y_max": y_max, "rho_max": rho_max,
            "curvature": curvature, "band": band}


def v_pi0(k: float, kL: float, tau: float, M_G: float, M_P: float,
          domain=None) -> float:
    """V₃·Π²^{Tμν2}/(32π²) along the kL-const trajectory at scale k.

    The spectral arguments are L = kL·M_G/k and cutoff = (k/M_P)²,
    with V₃ = π²L³.  The default spectral_sum response uses the
    finite Gaussian domain R = 5 and zero external momentum.  Passing a
    ``ResponseDomain`` evaluates the same readout at an explicit finite
    response domain; the production callers keep the default.

    At ``k = M_G`` this readout uses ``L = kL``, the TT endpoint.  It does
    **not** use the Gaussian IR edge ``sqrt(2*pi)``; the two differ by about
    0.5% and the edge does not satisfy the endpoint equation.
    """
    L = kL * M_G / k
    V3 = math.pi ** 2 * L ** 3
    cut = (k / M_P) ** 2
    if domain is None:
        pi0 = channel_tmunu_spin2(L, cut, tau)["rp3_pi0"]
    else:
        pi0 = channel_tmunu_spin2(L, cut, tau, domain=domain)["rp3_pi0"]
    return V3 * pi0 / FACTOR


def k_star(kL: float, tau: float, M_G: float, M_P: float,
           domain=None) -> float:
    """Find the endpoint crossing V·Π²/(32π²) = 4/27 by bisection.

    The initial bracket is [0.3 M_G, 3 M_G].  Iteration stops at
    absolute width 1e-15 or after 200 steps; floating-point
    stagnation can occur before that width is reached.  The returned
    midpoint is not an interval certificate: signs and quadrature
    errors are not bounded by interval arithmetic here.
    """
    lo, hi = 0.3 * M_G, 3.0 * M_G
    flo = v_pi0(lo, kL, tau, M_G, M_P, domain=domain) - CRIT
    fhi = v_pi0(hi, kL, tau, M_G, M_P, domain=domain) - CRIT
    if flo * fhi > 0:
        raise RuntimeError(f"no crossing: kL={kL:.4f} M_G={M_G:.3e}")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f = v_pi0(mid, kL, tau, M_G, M_P, domain=domain) - CRIT
        if (hi - lo) < 1e-15:
            return mid
        if flo * f < 0:
            hi = mid
        else:
            lo = mid
            flo = f
    return 0.5 * (lo + hi)


def self_consistent_chain(M_P: float, L_Cg: float, tau: float,
                          domain=None) -> dict:
    """The self-consistent emergence chain for a given endpoint
    geometry.

    The fixed point kL* = C/k* with k* = M_G (the F_MG two-step
    iteration): M_G = C/kL*, k_GUT = C/L_GUT with L_GUT = √3/τ (the
    isometry-breaking scale of the J=2 squash).

    ``kL*`` is the **TT endpoint**, not the Gaussian IR edge
    ``sqrt(2*pi)`` and not the critical ratio ``sqrt(pi)``.  The latter
    two are separate scales; substituting either for ``kL*`` changes the
    endpoint equation and all downstream masses.

    The floating-point update stops when successive kL values differ
    by less than 1e-15 or after 60 steps.  This stopping rule does
    not certify a root enclosure.
    """
    C = M_P * L_Cg
    L_GUT = math.sqrt(3.0) / tau
    kL = get("kL")
    for _ in range(60):
        M_G = C / kL
        kL_new = C / k_star(kL, tau, M_G, M_P, domain=domain)
        if abs(kL_new - kL) < 1e-15:
            kL = kL_new
            break
        kL = kL_new
    M_G = C / kL
    return {"C": C, "kL": kL, "M_G": M_G, "M_G_over_MP": M_G / M_P,
            "k_GUT": C / L_GUT}


def compute() -> dict:
    """Compute and publish the endpoint chain for the stored inputs."""
    M_P = get("M_P")
    tau = get("tau")
    L_Cg = get("L_Cg")   # retained framework value: sqrt(pi)

    # The endpoint determines the bare Killing-normalisation coupling.
    # geometric_couplings supplies the separate inverse-coupling correction.
    chain_pi = self_consistent_chain(M_P, L_Cg, tau)
    kL_pi = chain_pi["kL"]
    M_G_pi = chain_pi["M_G"]
    pset("kL", kL_pi, provenance="DERIVED",
         definition=QuantityDefinition(
             "finite-response endpoint kL", "1", "three-copy charged RP3 spectrum",
             "specified spin-2 channel mode sum", "fixed channel source",
             "R=5 fixed frequency domain and species projectors",
             "V*Pi/32=4/27", "declared Gaussian response", "finite spectral sum",
             assumptions=("fixed content branch and response domain",),
             error_kind="floating-point centre; interval certificate supplied separately"),
         evidence_kind="computed root of the declared response",
         note="F_MG fixed point for the specified R=5 response at L_Cg=sqrt(pi)")
    pset("L_Gg", kL_pi, provenance="DERIVED",
         note="L(M_G)=kL=C/M_G at L_Cg=sqrt(pi)")
    get("kL")  # Record the current root used in the dimensional matching.
    pset("M_G", M_G_pi, provenance="DERIVED", dependencies=("M_P", "L_Cg", "kL"),
         definition=QuantityDefinition(
             "emergence matching scale", "GeV", "declared endpoint branch",
             "dimensional scale transfer", "Newton dimensional anchor",
             "same finite-response endpoint", "M_P*L_Cg/kL",
             "specified framework scale matching", "algebraic",
             scale_GeV=M_G_pi, error_kind="propagated numerical centre"),
         note="M_G = M_P*L_Cg/kL with L_Cg=sqrt(pi)")
    scale_factor = register_gauge_scale_factor()
    g2_pi = math.sqrt(8.0 * scale_factor / kL_pi ** 3)
    pset("g2_MG_bare_constraint", g2_pi, provenance="DERIVED",
         role="internal",
         dependencies=("gauge_kinetic_scale_factor", "kL"),
         note="bare g2(M_G) = sqrt(8)(M_G/M_P)kL^{-3/2} at L_Cg=sqrt(pi) "
              "(geometric boundary value; the physical g2_MG incorporates "
              "the inverse-coupling term 1/N_c - tau^2*pi/2 in "
              "geometric_couplings)")
    pset("L_critical", math.sqrt(math.pi), provenance="DERIVED",
         note="L_c = sqrt(6/R_c) with R_c = 6/pi, so L_c = sqrt(pi) = L_Cg "
              "(first-principles)")

    # Record the retained endpoint geometry and corresponding curvature.
    pset("L_Cg_star", math.sqrt(math.pi), provenance="DERIVED",
         note="L_Cg* = sqrt(pi) (first-principles)")
    pset("R_c_star", 6.0 / math.pi, provenance="DERIVED",
         note="R_c* = 6/pi (first-principles, the critical curvature)")
    return chain_pi


if __name__ == "__main__":
    # Smoke: the constraint analysis runs and publishes the chain.
    r = compute()
    print(f"kL* = {r['kL']:.6f}, M_G/M_P = {r['M_G_over_MP']:.6f} "
          f"(L_Cg = sqrt(pi), first-principles)")
    # The threshold extremum geometry (uniqueness + curvature).
    tg = threshold_geometry()
    assert abs(tg["rho_max"] - CRIT) < 1e-15, "4/27 = rho(1/3)"
    assert abs(tg["curvature"] - 2.0) < 1e-15, "|rho''(1/3)| = 2"
    assert abs(tg["y_max"] - 1.0 / 3.0) < 1e-15, "unique interior extremum"
    print(f"threshold geometry: y_max={tg['y_max']:.4f} "
          f"rho_max={tg['rho_max']:.6f} curvature={tg['curvature']:.1f} "
          f"(unique extremum, flat to second order)")
    print("endpoint_constraint OK")
