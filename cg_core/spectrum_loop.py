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
cg_core/spectrum_loop.py — V5.0: the SM field spectrum on RP³
with the EC mass shifts
=================================================================

PURPOSE
-----------------------------------
The FRG trace density and the composite-operator amplitudes Π² are
sums over the modes of the SM fields on the internal RP³.  Each
field species enters with (a) the RP³ spectrum of its spin (scalar,
vector, spinor, TT), (b) an effective mass² from the Einstein-Cartan
(EC) connection on the internal space (the curvature and torsion
shifts), and (c) the field content (the multiplicity and the
statistics weight).  This module is the single iterator that emits
those modes; the trace kernels (trace_kernels) and the spectral-sum
engine (cg_frg/frg/spectral_sum) consume it.

THE EC MASS SHIFTS (derivation of each)
---------------------------------------
· Scalar: m² = ξR = 3/(4L²).  The conformal coupling in d = 3 is
  ξ = (d−2)/(4(d−1)) = 1/8; with R = 6/L² this is 3/(4L²).  The
  Higgs doublet (4 real DOF) carries this shift.

· Gauge: m² = C₂R/12 + τ²/(6L²) = C₂/(2L²) + τ²/(6L²).  The first
  term is the Camporesi curvature mass of a vector on the EC
  background (C₂ = the quadratic Casimir of the gauge generator's
  SO(4) content: 3.0 for the SU(3) Killing-type modes, 2.0 for
  SU(2), 0.0 for U(1)); the second is the EC-torsion shift
  τ²/(6L²).

· Fermion: m² = 3τ²/(8L²) — the EC-torsion shift only.  The
  curvature is ALREADY inside the Dirac² spectrum: the Lichnerowicz
  identity D² = ∇*∇ + R/4 folds the curvature into the spinor
  eigenvalues (the n-mode carries (n+3/2)²/L²), so adding another
  curvature term 3R/8 = 9/(4L²) would DOUBLE-COUNT the n = 0
  eigenvalue.  The torsion shift 3τ²/(8L²) is the only additional
  mass.

· Tensor response: the declared three-branch catalogue has eigenvalues
  (C₂+6)/L² and an additional response shift m² = 6/L². Its scalar
  diagonal branch and two off-diagonal branches enter the channel trace
  with the specified multiplicities.

THE STATISTICS WEIGHT
---------------------
The supertrace weight of each species (used by the trace density):
bosons +1 per real degree of freedom, fermions −1 per Weyl
component (each Weyl carries two real components, so the supertrace
weight of a Weyl fermion is −2 relative to a real boson).  The
Faddeev-Popov ghosts are complex scalars with Grassmann statistics:
−2 per ghost.

THE SPECIES PROJECTION
----------------------
For the selected spin lift, signed D has positive even n and negative
odd n; D² contains all n. Guo's (2026g) specified source assigns LH
species to P_minus (odd n), RH species to P_plus (even n). These are
source projections on one D² carrier, not separate spin structures.
The spin_structure argument selects this species-dependent source projection.
uniform_even changes the source prescription and is a diagnostic only.

TRUNCATION
----------
The finite response domain is explicit: only lambda < R k² is
enumerated. This is a measurement-domain definition, not an estimate
that omitted modes of a full Gaussian have zero contribution.
"""

from __future__ import annotations

import sys
import math
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.rp3_spectrum import (
    scalar_eigenvalue,
    scalar_multiplicity,
    vector_eigenvalue,
    vector_multiplicity,
    spinor_eigenvalue,
    spinor_multiplicity,
    response_tensor_eigenvalue,
    tt_multiplicity,
)
from cg_core.sm_content import N_GAUGE, N_WEYL_TOTAL, N_GENERATIONS, weyl_content
from cg_core.window_weights import ResponseDomain, DEFAULT_RESPONSE_DOMAIN


@dataclass(frozen=True)
class FieldSpec:
    """A field species: its spin kind, name, Casimir, and multiplicity.

    kind : scalar | gauge | fermion | ghost | tensor_TT
    c2   : the gauge Casimir (the SO(4) content of the generator)
    """
    kind: str
    name: str
    c2: float = 0.0
    n_components: int = 1


# ---------------------------------------------------------------------------
# The field content lists.
# ---------------------------------------------------------------------------
def sm_gauge_fields() -> list[FieldSpec]:
    """The 12 gauge fields with their SO(4) Casimir values.

    c2 = 3.0 for the 8 SU(3) Killing-type modes, 2.0 for the 3
    SU(2), 0.0 for the U(1) (the vector harmonics carry the Casimir
    of the generator's SO(4) content).
    """
    return (
        [FieldSpec("gauge", f"g3_{i}", c2=3.0) for i in range(N_GAUGE["su3"])]
        + [FieldSpec("gauge", f"g2_{i}", c2=2.0) for i in range(N_GAUGE["su2"])]
        + [FieldSpec("gauge", "g1", c2=0.0)]
    )


def sm_ghost_fields() -> list[FieldSpec]:
    """The 12 Faddeev-Popov ghosts (one complex ghost per gauge
    generator).

    Each ghost is a complex scalar (two real DOF) with Grassmann
    statistics, so its supertrace weight is −2.  It runs on the
    scalar spectrum with the gauge mass.
    """
    return (
        [FieldSpec("ghost", f"c3_{i}", c2=3.0) for i in range(N_GAUGE["su3"])]
        + [FieldSpec("ghost", f"c2_{i}", c2=2.0) for i in range(N_GAUGE["su2"])]
        + [FieldSpec("ghost", "c1", c2=0.0)]
    )


def sm_scalar_fields() -> list[FieldSpec]:
    """The Higgs doublet: one complex doublet, 4 real DOF.

    The doublet carries the conformal mass shift ξR = 3/(4L²).
    """
    return [FieldSpec("scalar", "H", n_components=4)]


def sm_fermion_fields() -> list[FieldSpec]:
    """The 45 Weyl fermions (3 generations).

    The names encode the chirality: the left-handed doublets
    (Q_L, L_L — 24 components) and the right-handed singlets
    (u_R, d_R, e_R — 21 components); the spin-structure assignment
    is applied in the iterator (see the module docstring).
    """
    fields = []
    components = {name:n for name, _, _, n in weyl_content()}
    for gen in range(1, N_GENERATIONS+1):
        for name in ("Q_L", "L_L", "u_R", "d_R", "e_R"):
            n_comp = components[name]
            fields.append(FieldSpec("fermion", f"{name}{gen}", n_components=n_comp))
    assert sum(f.n_components for f in fields) == N_WEYL_TOTAL
    return fields


# ---------------------------------------------------------------------------
# The EC mass shifts.
# ---------------------------------------------------------------------------
def m2_scalar(L: float) -> float:
    """m² = ξR = 3/(4L²) — the conformal scalar shift (ξ = 1/8, R = 6/L²)."""
    return 3.0 / (4.0 * L * L)


def m2_gauge(c2: float, L: float, tau: float) -> float:
    """m² = C₂/(2L²) + τ²/(6L²) — the Camporesi curvature mass plus
    the EC-torsion shift."""
    return c2 / (2.0 * L * L) + tau * tau / (6.0 * L * L)


def m2_fermion(L: float, tau: float) -> float:
    """m² = 3τ²/(8L²) — the EC-torsion shift only.

    The curvature is already inside the Dirac² spectrum (the
    Lichnerowicz identity D² = ∇*∇ + R/4); adding it again would
    double-count the n = 0 eigenvalue.
    """
    return 3.0 * tau * tau / (8.0 * L * L)


def m2_tt(L: float) -> float:
    """m² = 6/L² — the Lichnerowicz shift of the round S³ (spin-2)."""
    return 6.0 / (L * L)


# ---------------------------------------------------------------------------
# The spectrum iterator.
# ---------------------------------------------------------------------------
def _spinor_parity(name: str, spin_structure: str) -> int:
    """The spinor-tower parity of a fermion field.

    chiral: LH uses P_minus (odd n), RH uses P_plus (even n).
    uniform_even: all species use P_plus, a different source prescription.
    """
    if spin_structure == "uniform_even":
        return 0
    if spin_structure != "chiral":
        raise ValueError("source assignment must be chiral or uniform_even")
    if name.startswith(("Q_L", "L_L")):
        return 1  # LH → n odd
    return 0  # RH → n even


# ---------------------------------------------------------------------------
# The window truncation.
# ---------------------------------------------------------------------------
def _above_window(lam: float, edge: float) -> bool:
    """At the finite-domain edge the frequency interval has zero length."""
    return lam >= edge


def iter_sm_spectrum(
    L: float,
    k: float,
    tau: float,
    *,
    spin_structure: str = "chiral",
    l_max: int | None = None,
    domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN,
) -> Iterator[tuple[str, str, int, float, float, int]]:
    """Iterate the SM modes on RP³.

    Yields (kind, name, mode_label, lam, m2, deg) where lam is the
    RP³ eigenvalue, m2 is the EC mass shift (the kernel of the
    spectral sums receives the two separately: the frequency
    integral runs over ω² + lam with the mass m2 entering the
    kernel), and deg = multiplicity × field components (the total
    degree-of-freedom count per mode).  The supertrace weight and
    the operator-specific channel weight are applied by the channel
    engine, not here. All modes with lam < R*k² are enumerated;
    a supplied l_max is a safety cap and must cover that domain.
    """
    if not all(math.isfinite(x) for x in (L, k, tau)) or L <= 0 or k <= 0:
        raise ValueError("positive finite radius and scale, finite torsion required")
    cutoff_sq = domain.edge(k*k)
    # Each scalar/vector/spinor eigenvalue exceeds (label-1)^2/L².
    # Each tensor eigenvalue exceeds 2*jL²/L² and 2*jR²/L².
    bound = math.ceil(math.sqrt(cutoff_sq)*L)+2
    if l_max is not None and (not isinstance(l_max, int) or l_max < bound):
        raise ValueError(f"mode safety cap must be at least {bound} for this domain")
    l_max = bound

    # Scalars: the Higgs doublet (4 real DOF), conformal mass.
    m2_s = m2_scalar(L)
    for field in sm_scalar_fields():
        for l in range(0, l_max + 1, 2):
            lam = scalar_eigenvalue(l, L)
            if _above_window(lam, cutoff_sq):
                break
            d = scalar_multiplicity(l)
            yield ("scalar", field.name, l, lam, m2_s, field.n_components * d)

    # Gauge: the 12 gauge fields on the vector spectrum, EC mass.
    for field in sm_gauge_fields():
        m2_g = m2_gauge(field.c2, L, tau)
        for l in range(1, l_max + 1, 2):
            lam = vector_eigenvalue(l, L)
            if _above_window(lam, cutoff_sq):
                break
            d = vector_multiplicity(l)
            yield ("gauge", field.name, l, lam, m2_g, d)

    # Ghosts: the 12 Faddeev-Popov ghosts, scalar spectrum, gauge
    # mass.  (The ghosts are excluded from the gauge-invariant
    # operator channels by their weights; they are listed here so
    # the supertrace of the full measure is complete.)
    for field in sm_ghost_fields():
        m2_g = m2_gauge(field.c2, L, tau)
        for l in range(0, l_max + 1, 2):
            lam = scalar_eigenvalue(l, L)
            if _above_window(lam, cutoff_sq):
                break
            d = scalar_multiplicity(l)
            yield ("ghost", field.name, l, lam, m2_g, d)

    # Fermions: the 45 Weyl fermions, spinor spectrum, EC-torsion
    # mass.
    m2_f = m2_fermion(L, tau)
    for field in sm_fermion_fields():
        start = _spinor_parity(field.name, spin_structure)
        for n in range(start, l_max + 1, 2):
            lam = spinor_eigenvalue(n, L)
            if _above_window(lam, cutoff_sq):
                break
            d = spinor_multiplicity(n)
            yield ("fermion", field.name, n, lam, m2_f, field.n_components * d)

    # Three-branch tensor-response catalogue, with its separate
    # +6/L² mass insertion. The tensor_TT key is a compatibility label;
    # it is not the genuine rough-TT carrier or an external graviton pole.
    m2_t = m2_tt(L)
    j_max = math.ceil(math.sqrt(cutoff_sq/2)*L)+1
    for jL in range(j_max+1):
        for jR in range(j_max+1):
            if jL + jR < 2 or abs(jL - jR) > 2 or (jL + jR) % 2 != 0:
                continue
            lam = response_tensor_eigenvalue(jL, jR, L)
            if _above_window(lam, cutoff_sq):
                continue
            d = tt_multiplicity(jL, jR)
            yield ("tensor_TT", f"TT_{jL}{jR}", jL + jR, lam, m2_t, d)


def _self_test() -> None:
    L = 2.4935343325226915
    k = L  # a representative scale
    tau = 0.02
    modes = list(iter_sm_spectrum(L, k, tau))
    kinds = {}
    for kind, *_rest in modes:
        kinds[kind] = kinds.get(kind, 0) + 1
    assert kinds.get("scalar", 0) > 0
    assert kinds.get("gauge", 0) > 0
    assert kinds.get("ghost", 0) > 0
    assert kinds.get("fermion", 0) > 0
    assert kinds.get("tensor_TT", 0) > 0
    # The chiral assignment must put LH fermions on odd n.
    lh_modes = [m for m in modes if m[0] == "fermion" and m[1].startswith("Q_L")]
    assert all(m[2] % 2 == 1 for m in lh_modes)
    # The EC mass shifts: the scalar at 3/4L², the fermion at 3τ²/8L².
    m_s = next(m for m in modes if m[0] == "scalar")
    assert abs(m_s[4] - 3.0 / (4.0 * L * L)) < 1e-12
    m_f = next(m for m in modes if m[0] == "fermion")
    assert abs(m_f[4] - 3.0 * 0.02 * 0.02 / (8.0 * L * L)) < 1e-15
    print(f"spectrum_loop self-test OK ({len(modes)} modes, kinds: {kinds})")


if __name__ == "__main__":
    _self_test()
