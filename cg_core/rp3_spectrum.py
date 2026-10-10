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
cg_core/rp3_spectrum.py — V5.0: the exact spectral theory of RP³
=================================================================

PURPOSE
-----------------------------------
The internal space of the framework is RP³ = S³/Z₂, the antipodal
quotient of the unit sphere.  Every spectral sum in the framework —
the FRG trace density, the composite-operator amplitudes Π², the
generation window, the TT pole analysis — is a sum over the modes
of a field on RP³.  This module is the single source of those
spectra: the scalar, vector, spinor and transverse-traceless (TT)
eigenvalues with their multiplicities, the Z₂ projection rule, and
the geometric data (volume, Killing vectors, cohomology) that the
rest of the framework quotes.

The spectra are EXACT group theory: the eigenvalues are the
SO(4) = SU(2)_L × SU(2)_R Casimir data of the RP³ harmonics
(Camporesi 1990 for the spinor case).  No numerical input enters;
every formula carries its derivation.

THE Z₂ PROJECTION RULE (why the parity sectors differ)
-------------------------------------------------------
A field on S³ descends to RP³ iff it is even under the antipodal
map.  For a scalar the antipodal map acts with parity (−1)^l on the
degree-l harmonic, so the even sector l ∈ {0, 2, 4, ...} survives.
For a 1-form the pullback of the antipodal map carries an extra
factor −1 from the differential (dx ↦ −dx), so the surviving sector
is l odd.  For the spinor tower the antipodal lift (−1_L, +1_R) acts
with parity (−1)^n on the n-th mode (n even survives).  For the TT
tensors the surviving harmonics have j_L + j_R even.

THE SPECTRA (derivation of each)
--------------------------------
· Scalar Laplacian on S³ of radius L: λ_l = l(l+2)/L² with
  multiplicity (l+1)² (the standard S³ spectrum; the degree-l
  harmonics transform as (l/2, l/2) of SO(4), whose quadratic
  Casimir is 2[j_L(j_L+1)+j_R(j_R+1)] = l(l+2)).  On RP³: l even.
  The l = 0 mode is the constant function — the sole scalar zero
  mode, the carrier of the dilaton/order-parameter field.

· Vector Laplacian on S³: λ_l = (l+1)²/L² with multiplicity
  2l(l+2) (the 1-form harmonics of degree l ≥ 1).  The l = 1 sector
  has λ = 4/L² and multiplicity 6 — the Killing 1-forms (the
  isometry algebra so(4), 6 generators).  On RP³: l odd.  There are
  no harmonic 1-forms on RP³ (H¹(RP³; ℝ) = 0) — the Killing forms
  are not closed, so the 6 isometries survive the quotient even
  though the de Rham cohomology vanishes.

· Dirac: one selected spin lift has positive even n and negative odd
  n, with multiplicity (n+1)(n+2) at each signed eigenvalue. D² has
  every n. P_plus/P_minus select even/odd n as an additional source
  prescription, not two halves of different spin structures.

· Genuine TT: the two representations |j_L-j_R|=2, j_L+j_R even,
  carry the positive rough operator (C2-6)/L², minimum 6/L² and
  Weyl weight 2. The separate three-branch tensor-response catalogue
  also contains (j,j), uses (C2+6)/L², has minimum 14/L² and weight
  3. The response_tensor_* functions evaluate this three-branch catalogue;
  true_tt_modes evaluates the specified transverse-tracefree operator.

GEOMETRIC DATA
--------------
· Volume: Vol(RP³) = π² L³ (half the S³ volume 2π² L³).
· Killing vectors: 6 (dim so(4)); the Killing normalisation
  ∫ ω^a · ω^b = δ^{ab} · Vol · (2/L²) (used by the gauge coupling).
· Cohomology: H¹(RP³; ℝ) = 0 (no harmonic 1-forms); H⁰ = ℝ
  (connected); the second Stiefel-Whitney class selects the spin
  structures.

IMPLEMENTATION
-------------
No physics value is hard-coded: the only input is the radius L
(a function argument or a store read).  All computations are exact
closed forms (no numerical integration).  The module self-tests at
the framework's fixed point L = kL = 2.4935343.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# The structural constant 2π (the only non-integer constant used here).
_TWO_PI = 2.0 * math.pi


def volume(L: float) -> float:
    """Vol(RP³) = π² L³ — half the round S³ volume.

    The antipodal quotient halves the volume of the sphere.
    """
    return math.pi * math.pi * L ** 3


def n_killing_vectors() -> int:
    """The number of Killing vectors of RP³: dim so(4) = 6.

    The antipodal map is central in O(4), so every S³ isometry
    descends; the isometry group of RP³ is PO(4), dimension 6.
    """
    return 6


def h1_zero() -> bool:
    """H¹(RP³; ℝ) = 0 — no harmonic 1-forms on the quotient."""
    return True


# ---------------------------------------------------------------------------
# Scalar spectrum.
# ---------------------------------------------------------------------------
def scalar_eigenvalue(l: int, L: float) -> float:
    """λ_l = l(l+2)/L² — the degree-l scalar harmonic.

    Derivation: the harmonic transforms as (l/2, l/2) of SO(4),
    whose quadratic Casimir is 2[j_L(j_L+1)+j_R(j_R+1)] with
    j_L = j_R = l/2, giving l(l+2).
    """
    return float(l * (l + 2)) / (L * L)


def scalar_multiplicity(l: int) -> int:
    """d_l = (l+1)² — the dimension of the (l/2, l/2) representation."""
    return (l + 1) * (l + 1)


def scalar_modes(L: float, l_max: int) -> list[tuple[int, float, int]]:
    """The Z₂-even scalar modes: l even, up to l_max.

    Returns (l, λ_l, d_l).  The l = 0 mode is the constant function
    (the scalar zero mode).
    """
    out = []
    for l in range(0, l_max + 1, 2):
        out.append((l, scalar_eigenvalue(l, L), scalar_multiplicity(l)))
    return out


# ---------------------------------------------------------------------------
# Vector (1-form) spectrum.
# ---------------------------------------------------------------------------
def vector_eigenvalue(l: int, L: float) -> float:
    """λ_l = (l+1)²/L² — the degree-l 1-form harmonic (l ≥ 1).

    Derivation: the 1-form harmonics of degree l on S³ have the
    Hodge-Laplacian eigenvalues (l+1)²/L²; the l = 1 sector is the
    Killing sector (λ = 4/L², multiplicity 6).
    """
    if l < 1:
        raise ValueError("vector harmonics start at l = 1")
    return float((l + 1) * (l + 1)) / (L * L)


def vector_multiplicity(l: int) -> int:
    """d_l = 2l(l+2) for the 1-form harmonics of degree l ≥ 1."""
    return 2 * l * (l + 2)


def vector_modes(L: float, l_max: int) -> list[tuple[int, float, int]]:
    """The Z₂-odd 1-form modes: l odd (the antipodal differential
    flips the parity), up to l_max."""
    out = []
    for l in range(1, l_max + 1, 2):
        out.append((l, vector_eigenvalue(l, L), vector_multiplicity(l)))
    return out


# ---------------------------------------------------------------------------
# Spinor (Dirac) spectrum.
# ---------------------------------------------------------------------------
def spinor_eigenvalue(n: int, L: float) -> float:
    """λ_n = (n+3/2)²/L² — the n-th spinor harmonic (n even on RP³).

    Derivation (Camporesi 1990): the mode n carries (j_L, j_R) =
    (n/2 + 1/2, n/2), and the Dirac eigenvalue is j_L + j_R + 1 =
    n + 3/2 (in units of 1/L).  The squared eigenvalue is the
    Laplacian-type value used in the spectral sums.
    """
    return ((n + 1.5) / L) ** 2


def spinor_dirac_eigenvalue(n: int, L: float) -> float:
    """Selected spin lift: positive even n and negative odd n.

    The opposite spin structure reverses every sign; it does not remove
    half of the D-squared tower. Species projections are separate below.
    """
    if n < 0 or L <= 0:
        raise ValueError("n must be nonnegative and L positive")
    return (1 if n % 2 == 0 else -1) * (n + 1.5) / L


def spinor_multiplicity(n: int) -> int:
    """d_n = (n+1)(n+2) — the dimension of the spinor harmonic space."""
    return (n + 1) * (n + 2)


def spinor_quantum_numbers(n: int) -> tuple[float, float]:
    """Positive-branch label (n/2 + 1/2, n/2), without integer rounding."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return ((n + 1) / 2, n / 2)


def dirac_modes(L: float, n_max: int, *, opposite_lift: bool = False):
    """Complete signed Dirac tower for one spin lift: all n >= 0.

    Returns (n, signed eigenvalue, multiplicity). Negative modes carry
    the exchanged SU(2) labels. Each multiplicity appears once.
    """
    sign = -1 if opposite_lift else 1
    return [(n, sign * spinor_dirac_eigenvalue(n, L),
             spinor_multiplicity(n)) for n in range(n_max + 1)]


def dirac_squared_modes(L: float, n_max: int, *, projection: str = "full"):
    """D² full tower, or the separately specified P_plus/P_minus source.

    P_plus selects even n; P_minus selects odd n. Guo (2026g) assigns
    right species to P_plus and left species to P_minus for its trace.
    """
    starts = {"full": (0, 1), "P_plus": (0, 2), "P_minus": (1, 2)}
    if projection not in starts:
        raise ValueError("projection must be full, P_plus or P_minus")
    start, step = starts[projection]
    return [(n, spinor_eigenvalue(n, L), spinor_multiplicity(n))
            for n in range(start, n_max + 1, step)]


def spinor_modes(L: float, n_max: int) -> list[tuple[int, float, int]]:
    """The Z₂-even spinor modes: n even (the generation tower)."""
    out = []
    for n in range(0, n_max + 1, 2):
        out.append((n, spinor_eigenvalue(n, L), spinor_multiplicity(n)))
    return out


# ---------------------------------------------------------------------------
# TT tensor spectrum (the multi-tower).
# ---------------------------------------------------------------------------
def response_tensor_eigenvalue(jL: int, jR: int, L: float) -> float:
    """Three-branch response operator (C2 + 6)/L².

    This includes the (j,j) branch and is not the genuine rough-TT
    operator. The curvature shift is part of the declared readout.
    """
    casimir = 2.0 * (jL * (jL + 1) + jR * (jR + 1))
    return (casimir + 6.0) / (L * L)


def tt_multiplicity(jL: int, jR: int) -> int:
    """d = (2j_L+1)(2j_R+1) — the dimension of the SO(4) representation."""
    return (2 * jL + 1) * (2 * jR + 1)


def response_tensor_modes(L: float, j_max: int) -> list[tuple[int, int, float, int]]:
    """Response-catalogue modes: j_L + j_R even, |j_L − j_R| ≤ 2,
    j_L + j_R ≥ 2, up to j_max.

    Returns (j_L, j_R, λ, d).  The lowest mode is (1,1), with
    λ=14/L². No external momentum pole is inferred from this catalogue.
    """
    out = []
    for jL in range(0, j_max + 1):
        for jR in range(0, j_max + 1):
            if jL + jR < 2:
                continue
            if abs(jL - jR) > 2:
                continue
            if (jL + jR) % 2 != 0:
                continue
            out.append((jL, jR, response_tensor_eigenvalue(jL, jR, L), tt_multiplicity(jL, jR)))
    return out


def response_tensor_lowest_eigenvalue(L: float) -> float:
    """Response-catalogue minimum 14/L², at (1,1)."""
    return response_tensor_eigenvalue(1, 1, L)


def true_tt_modes(L: float, k_max: int, *, operator: str = "rough"):
    """Guo (2026d) genuine transverse-tracefree carrier, k=2,4,... .

    rough = C2 - 6; K6 = C2 + 6; K6_plus_6 = C2 + 12.
    The two representations have |jL-jR|=2 and total multiplicity
    2(k-1)(k+3). Their rough minimum is 6/L² and Weyl weight is 2.
    """
    shifts = {"rough": -6, "K6": 6, "K6_plus_6": 12}
    if L <= 0 or operator not in shifts:
        raise ValueError("positive L and an explicit supported operator required")
    out = []
    for k in range(2, k_max + 1, 2):
        for jL, jR in (((k + 2) // 2, (k - 2) // 2),
                       ((k - 2) // 2, (k + 2) // 2)):
            casimir = 2 * (jL * (jL + 1) + jR * (jR + 1))
            out.append((jL, jR, (casimir + shifts[operator]) / L**2,
                        tt_multiplicity(jL, jR)))
    return out


# The short tt_* names designate the three-branch response catalogue.
# true_tt_modes designates the transverse-tracefree carrier and operator.
tt_eigenvalue = response_tensor_eigenvalue
tt_modes = response_tensor_modes
tt_lowest_eigenvalue = response_tensor_lowest_eigenvalue


# ---------------------------------------------------------------------------
# Weyl-law self-consistency (the UV spectral density).
# ---------------------------------------------------------------------------
def weyl_coeff(L: float, dof: int) -> float:
    """The Weyl coefficient for `dof` degrees of freedom on RP³:
    dof × Vol/(6π²) = dof × L³/6 (the d = 3 spectral density).

    Derivation: the Weyl law N(λ) ~ [Vol/(4π)^{d/2} Γ(d/2+1)] λ^{d/2}
    with d = 3 gives Γ(5/2) = 3√π/4, so N(λ) ~ (Vol/6π²) λ^{3/2}
    per degree of freedom.
    """
    return dof * L ** 3 / 6.0


def weyl_dof() -> dict:
    """Response-catalogue weights; key 'tt' denotes the three tensor branches.

    The projected P_plus spinor weight is 1; full D² has weight 2.
    Genuine transverse-tracefree tensors have weight 2, not 3.
    """
    return {"scalar": 1, "vector": 2, "spinor": 1, "tt": 3}


def count_modes_below(kind: str, lam_cut: float, L: float,
                      l_max: int = 200) -> int:
    """Count the RP³ modes of `kind` with eigenvalue < lam_cut."""
    n = 0
    if kind == "scalar":
        for l in range(0, l_max, 2):
            if scalar_eigenvalue(l, L) < lam_cut:
                n += scalar_multiplicity(l)
    elif kind == "vector":
        for l in range(1, l_max, 2):
            if vector_eigenvalue(l, L) < lam_cut:
                n += vector_multiplicity(l)
    elif kind == "spinor":
        for m in range(0, l_max, 2):
            if spinor_eigenvalue(m, L) < lam_cut:
                n += spinor_multiplicity(m)
    elif kind == "tt":
        for jL in range(l_max // 2):
            for jR in range(l_max // 2):
                if jL + jR < 2 or abs(jL - jR) > 2 or (jL + jR) % 2:
                    continue
                if tt_eigenvalue(jL, jR, L) < lam_cut:
                    n += tt_multiplicity(jL, jR)
    return n


def kk_dof_running(E: float, L: float, l_max: int = 200) -> dict:
    """The KK effective degrees of freedom below the 4D energy E.

    This is the spectral-language reading of the KK reduction (the
    spectrum → 4D correspondence): a 4D field on M⁴ × RP³ is a KK
    tower with squared masses m_n² = λ_n, so the number of KK modes
    excited below the 4D scale E is

        N(E) = Σ_{λ_n < E²} d_n  ~  (Σ_s dof_s) · (L³/6) · E³

    (the Weyl law — the power-law running of the 4D effective
    degrees of freedom).  The sum over sectors gives the total
    d = 3 physical DOF count 1 + 2 + 1 + 3 = 7 (scalar / vector /
    spinor / TT).  Returns the per-sector mode counts and the total
    effective DOF.

    NOTE : this sharp-step count carries a boundary
    oscillation (the Weyl law's subleading term converges slowly,
    ~0.3% residual).  The framework's own regulator is the SMOOTH
    Gaussian window (see heat_kernel) — the heat-kernel expansion
    is analytic (no oscillation) and is the higher-precision
    spectral sum.
    """
    dof = weyl_dof()
    counts = {k: count_modes_below(k, E * E, L, l_max) for k in dof}
    # counts[k] already carries the physical DOF in d_l (e.g. the
    # vector 2l(l+2), the spinor (n+1)(n+2)), so the total effective
    # DOF is the plain sum (NOT counts*dof — that double-counts).
    total = sum(counts.values())
    return {"counts": counts, "total_dof": total,
            "weyl_asymptote": sum(dof.values()) * L ** 3 / 6.0 * E ** 3}


def heat_kernel(t: float, L: float, l_max: int = 200) -> dict:
    """The heat kernel K(t) = Σ_n d_n e^{−t λ_n} (the smooth Gaussian
    window — the framework's own regulator, NOT a sharp cutoff).

    Returns the explicit finite sum and per-sector sums of the
    response catalogue, with a0=7 Vol. The scalar heat coefficients
    cannot be multiplied by 7 to obtain coefficients of different
    operators and projected carriers. Consequently a2/a4 are None
    until separately derived; the sum itself remains available.
    """
    if t <= 0 or L <= 0:
        raise ValueError("t and L must be positive")
    Ktot = 0.0
    per = {}
    for kind in ("scalar", "vector", "spinor", "tt"):
        s = 0.0
        if kind == "scalar":
            for l in range(0, l_max, 2):
                s += scalar_multiplicity(l) * math.exp(
                    -t * scalar_eigenvalue(l, L))
        elif kind == "vector":
            for l in range(1, l_max, 2):
                s += vector_multiplicity(l) * math.exp(
                    -t * vector_eigenvalue(l, L))
        elif kind == "spinor":
            for m in range(0, l_max, 2):
                s += spinor_multiplicity(m) * math.exp(
                    -t * spinor_eigenvalue(m, L))
        elif kind == "tt":
            for jL in range(l_max // 2):
                for jR in range(l_max // 2):
                    if jL + jR < 2 or abs(jL - jR) > 2 or (jL + jR) % 2:
                        continue
                    s += tt_multiplicity(jL, jR) * math.exp(
                        -t * tt_eigenvalue(jL, jR, L))
        per[kind] = s
        Ktot += s
    # a₀ = Σ_s dof_s · Vol (each physical d.o.f. carries a heat-kernel
    # a₀ = Vol); the d_l in the sums already include the polarisation
    # count, so the total a₀ is dof_total × Vol.
    dof_total = sum(weyl_dof().values())
    a0 = dof_total * volume(L)
    return {"K": Ktot, "per_sector": per,
            "a0": a0, "a2": None, "a4": None,
            "coefficient_status": "a0 proved by sector Weyl weights; "
                                  "a2/a4 require operator-specific derivations",
            "carrier": "scalar + transverse vector + P_plus + three-branch tensor"}


# ---------------------------------------------------------------------------
# Self-test at the framework's fixed point.
# ---------------------------------------------------------------------------
def _self_test() -> None:
    kL = 2.4935343325226915  # the γ_M = 0 fixed point (endpoint_constraint)
    L = kL
    assert abs(scalar_eigenvalue(0, L) - 0.0) < 1e-12  # the zero mode
    assert abs(scalar_eigenvalue(2, L) - 8.0 / L ** 2) < 1e-12
    assert scalar_multiplicity(2) == 9
    assert vector_eigenvalue(1, L) == 4.0 / L ** 2  # the Killing sector
    assert vector_multiplicity(1) == 6
    assert abs(spinor_dirac_eigenvalue(0, L) - 1.5 / L) < 1e-12
    assert spinor_multiplicity(0) == 2
    assert spinor_quantum_numbers(2) == (1.5, 1)
    assert abs(tt_lowest_eigenvalue(L) - 14.0 / L ** 2) < 1e-12
    assert abs(volume(L) - math.pi ** 2 * L ** 3) < 1e-12
    assert n_killing_vectors() == 6 and h1_zero()
    # Weyl-law self-consistency: the UV spectral density of each
    # sector must reproduce its geometric DOF count (the spectral-
    # language statement that the mode multiplicity is complete).
    lam_cut = 6400.0
    for kind, dof in weyl_dof().items():
        n = count_modes_below(kind, lam_cut, L)
        coeff = n / lam_cut ** 1.5
        theory = weyl_coeff(L, dof)
        assert abs(coeff / theory - 1.0) < 0.02, (
            f"Weyl-law violation in {kind}: {coeff:.4f} vs {theory:.4f}")
    print(f"rp3_spectrum self-test OK at L = kL = {kL:.12f}")


if __name__ == "__main__":
    _self_test()
