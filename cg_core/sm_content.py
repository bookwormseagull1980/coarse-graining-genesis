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
cg_core/sm_content.py — V5.0: the Standard Model field content and
hypercharge statistics
=================================================================

PURPOSE
-----------------------------------
Every spectral sum of the framework weights the RP³ modes by the
field content: the FRG trace density counts bosons with +1 and
fermions with −1 per mode, and the composite-operator amplitudes
(Π²) weight each species by its representation.  This module is the
single source of that content: the 45 Weyl fermions (15 per
generation × 3), the 12 gauge bosons, the Higgs doublet, the
hypercharge table, and the hypercharge statistics that enter the
torsion parameter τ.

THE FOUR DUALITIES (the framework's unified emergence principle)
---------------------------------------------------------------
The framework unifies four dualities as faces of one duality
emergence (spectrum → duality → gauge/geometry/entropy → emergence
→ 4D physics):
  (1) conformal-gauge  N_g·ξ = 1     (the conformal coupling × the
                                      generator count, ξ = 1/8, N_g = 8);
  (2) geometric-gauge  d = N_c = 3    (the internal-space dimension =
                                      the colour rank, d = rank(G)+1);
  (3) UV-IR            e^S = window span (the entropy-encoded
                                      scale duality, S = ln W);
  (4) spectral-physical spectral sum = physical content (the spectral
                                      representation of the SM).
The endpoint entropy S = ln W relates the UV Gaussian window to the
specified IR readout. The scale-dependent trajectory is supplied by
the separately declared evolution law.

FIELD CONTENT FROM THE MINIMAL REPRESENTATIONS
------------------------------------------------------
One charged-response generation (15 Weyl components, charge convention
Q = T₃ + Y):
    Q_L = (u_L, d_L)  (3, 2)_{1/6}   6 Weyl (3 colours × 2)
    u_R               (3, 1)_{2/3}   3 Weyl
    d_R               (3, 1)_{−1/3}  3 Weyl
    L_L = (ν_L, e_L)  (1, 2)_{−1/2}  2 Weyl
    e_R               (1, 1)_{−1}    1 Weyl
    — 15 Weyl per generation; 45 after the joint screening selection.
      The upstream 16-component joint module and its charged 15-component
      quotient are distinct: the neutral right singlet is not counted
      in this charged-response trace. The endpoint window verifies
      the selected copy count; its capacity alone does not select it.
Gauge: 12 (8 gluons + 3 W + 1 B).  Scalar: one complex doublet
(4 real DOF).

DERIVATION OF THE FIVE REPRESENTATIONS (the framework's minimality
principle — the SAME principle that selects SU(2) over U(2), su(3)
over B2/G2, and RP³ over other spherical quotients):

  1. SU(2)_L doublet (theorem, lem:clifford + thm:dim): the chiral
     clause (A2) of the disorder axiom is realised by the two
     semispinor representations of Spin(4); the left-handed one
     (1/2,0) is an SU(2)_L doublet.

  2. Colour = the minimal non-trivial representation 3 (minimality):
     the colour algebra su(3) is selected by minimality (prop:colour,
     8 < 10 < 14); the fermion sits in its smallest non-trivial
     irreducible representation, the fundamental 3 (dimension 3) —
     the SAME economy criterion, applied to the matter content.

  3. Colour vectoriality (anomaly cancellation): the left-handed
     fermion is in 3 and the right-handed in 3̄ (the conjugate), so
     the SU(3)³ anomaly cancels — colour is vector-like.

  4. The five representations = chirality × colour assignment (the
     minimal combination): the left-handed doublet carries either
     colour (Q_L) or no colour (L_L); the right-handed singlets
     mirror the doublet components — u_L,d_L → u_R,d_R (colour 3̄),
     e_L → e_R (colour 1), while ν_L has no light right partner
     (Majorana).  Hence 2 left doublets + 3 right singlets.

     MINIMAL REPRESENTATION CONTENT:
     the chiral clause (A2) fixes the left sector as the single
     semispinor (1/2,0), an SU(2)_L doublet — no other left
     representation is selected.  The colour assignment has exactly
     two options for this doublet: the minimal non-trivial 3
     (colour, giving Q_L) or the trivial 1 (colourless, giving L_L);
     colour vectoriality (the SU(3)³ anomaly cancellation) then pairs
     each coloured left component with a right conjugate.  The right
     sector is the Yukawa mirror of the left: each CHARGED left
     component acquires exactly one right singlet — u_L,d_L → u_R,d_R
     and e_L → e_R — while the neutral ν_L acquires none (Majorana).
     The counting is therefore 2 left doublets (one coloured, one
     colourless) and 3 right singlets (the two charged components of
     Q_L plus the one charged component of L_L), which is exactly five,
     and no other representation is produced by the minimal
     combination.  This closes the uniqueness step.

  5. Hypercharge: DERIVED uniquely from anomaly cancellation + the
     Yukawa structure (Lean: hypercharge_derivation.lean).

HYPERCHARGE STATISTICS (the input to τ)
---------------------------------------
The charged-sector response modulus τ = (N_L − N_R)/(N_f · ΣY²) uses
the hypercharge sums on the 15-coordinate gauge-active quotient:
    ΣY²  = Σ over the 15 Weyl fermions of Y² (per generation)
    N_L − N_R = 1 (the quotient index: 8 left vs 7 charged right
    components per generation — N_LEFT = 8, N_RIGHT = 7)
The specific values (ΣY² = 10/3 per generation, τ = 1/50) are the
charged-response content used by the EC torsion modules.  The complete
matter carrier also contains neutral nu_R and has 8 left plus 8 right
coordinates; it has no intrinsic center bias.

IMPLEMENTATION
-------------
The five fermion representations are DERIVED from the framework's
minimality principle (colour = the minimal non-trivial
representation 3), the chiral clause (A2 → SU(2)_L doublet), and
colour vectoriality (anomaly cancellation); the hypercharge
assignment is DERIVED from anomaly cancellation + the Yukawa
structure (Lean hypercharge_derivation.lean).  The generation
count n_g = 3 follows from the joint extensive-source and colour
screening prescriptions implemented in content_response. The endpoint
then verifies the platform (n+3/2)<(kL)² in window_capacity. The
charged-response quotient and its source normalization are inherited
inputs, not rederived merely from this numerical table.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.content_response import (
    CHARGED_GENERATION, chiral_anomalies, finite_source_response,
    screening_compatibility,
)

# ---------------------------------------------------------------------------
# The one-generation Weyl content: (name, (SU(3), SU(2)), Y, components).
# ---------------------------------------------------------------------------
# The five representations follow from the stated minimality conditions
# (colour = minimal non-trivial rep 3), chirality (A2 -> SU(2)_L doublet),
# and colour vectoriality (anomaly cancellation).  The content counting is
# proved in Lean: lean_proofs/fermion_content.lean
# (charged quotient: N_L = 8 = N_g = N_c²−1; N_R = 7 = N_g−1).
# components counts the Weyl fermions: colour × weak-doublet members
# (for Q_L: 3 × 2 = 6; for singlets: 3 or 1).
_ONE_GENERATION = [(name, rep, float(y), n)
                   for name, rep, y, n, _ in CHARGED_GENERATION]

N_C, N_WEAK = next(rep for name, rep, _, _, _ in CHARGED_GENERATION
                   if name == "Q_L")
N_GENERATIONS = screening_compatibility(N_C)["generations"]
# Joint screening selects the replication count before endpoint evaluation.
# window_capacity then verifies its compatibility with the selected branch.

N_WEYL_PER_GENERATION = sum(c for _, _, _, c in _ONE_GENERATION)  # 15
N_WEYL_TOTAL = N_WEYL_PER_GENERATION * N_GENERATIONS  # 45

N_GAUGE = {"su3": N_C**2-1, "su2": N_WEAK**2-1, "u1": 1}
N_GAUGE_TOTAL = sum(N_GAUGE.values())  # 12
SCALAR_DOF = 2 * N_WEAK  # real components of the complex Higgs doublet

# The identity N_L = N_g (verified in lean_proofs/fermion_content.lean):
# the left-handed Weyl
# components per generation equal the COLOUR generator count, and the
# RIGHT-handed components are one less:
#
#   N_L = Q_L + L_L = 3·2 + 1·2 = 6 + 2 = 8  =  N_g = N_c² − 1 = 8
#   N_R = u_R + d_R + e_R = 3 + 3 + 1 = 7    =  N_g − 1
#
# The specified charged representations give N_L = 8, N_R = 7,
# N_f = 15 and ΣY² = 10/3. These counts enter the torsion readout
# and the neutrino ratio r12 = (N_L−N_R)/ΣY².  They are quotient
# observables; adding neutral nu_R restores the complete 8+8 carrier.
N_LEFT = sum(n for _, _, _, n, sign in CHARGED_GENERATION if sign == 1)
N_RIGHT = sum(n for _, _, _, n, sign in CHARGED_GENERATION if sign == -1)
N_G_COLOR = N_GAUGE["su3"]


def weyl_content() -> list[tuple[str, tuple[int, int], float, int]]:
    """The one-generation Weyl content (name, reps, Y, components)."""
    return list(_ONE_GENERATION)


def hypercharge_sum_sq() -> float:
    """ΣY² per generation — the hypercharge capacity.

    Derivation: the sum of Y² over the 15 Weyl fermions of one
    generation, weighted by the component count:
        6·(1/6)² + 3·(2/3)² + 3·(−1/3)² + 2·(−1/2)² + 1·(−1)²
      = 6/36 + 12/9 + 3/9 + 2/4 + 1
      = 1/6 + 4/3 + 1/3 + 1/2 + 1 = 10/3.

    THE FIRST NON-ZERO HYPERCHARGE MOMENT : the
    hypercharge TRACE vanishes, ΣY = 0 (the gravitational mixed
    anomaly cancels — the U(1)_Y is anomaly-free), so ΣY² = 10/3 is
    the FIRST non-zero hypercharge moment and therefore the natural
    normalisation of the torsion parameter τ (the τ-theorem layer: a
    vanishing ΣY cannot normalise, so the framework uses ΣY²).

    WINDOW-CAPACITY GEOMETRY : kL²/ΣY² = sqrt(N_R/2) =
    sqrt(7/2) to +0.009% — the window capacity over the hypercharge
    capacity equals the right-singlet half-count sqrt(N_R/2).
    """
    return sum(c * y * y for _, _, y, c in _ONE_GENERATION)


def hypercharge_sum() -> float:
    """Ordinary unsigned hypercharge trace ΣY = 0 for this content.

    Derivation: 6·(1/6) + 3·(2/3) + 3·(−1/3) + 2·(−1/2) + 1·(−1)
    = 1 + 2 − 1 − 1 − 1 = 0. The gravitational mixed anomaly instead
    uses the LH-minus-RH trace, checked exactly by chiral_anomalies().
    Both vanish here but they are different trace operations.
    """
    return sum(c * y for _, _, y, c in _ONE_GENERATION)


def hypercharge_sum_cube() -> float:
    """Unsigned ordinary third moment ΣY³ = −4/9, not a chiral anomaly.

    Derivation: 6·(1/6)³ + 3·(2/3)³ + 3·(−1/3)³ + 2·(−1/2)³ + 1·(−1)³
    = 1/36 + 8/9 − 1/9 − 1/4 − 1 = −4/9.
    """
    return sum(c * y ** 3 for _, _, y, c in _ONE_GENERATION)


def charged_quotient_index() -> int:
    """Charged-quotient index N_L − N_R per generation = 1.

    Derivation: the left-handed doublets Q_L, L_L carry 6 + 2 = 8
    components; the right-handed singlets u_R, d_R, e_R carry
    3 + 3 + 1 = 7; the difference is 1.  This charged response index
    enters τ.  It is not the center bias of the complete carrier, whose
    additional neutral right coordinate gives 8+8.

    THE CONTENT IDENTITY N_L = N_g: the LEFT-handed
    component count per generation is EXACTLY the colour generator
    count — N_L = 8 = N_g = N_c² − 1 — and the right-handed count is
    one less, N_R = 7 = N_g − 1.  The fermion content is thus
    fixed by the gauge structure (the chiral carrier lives in the
    same 8-fold content as the colour adjoint), not an independent
    datum.  Lean: AXIOM_PROOF_SERIES/fermion_content.lean (9 theorems).

    THE CHARGED-QUOTIENT Z₂ INDEX: N_L − N_R = 1 is odd, the
    non-trivial element of π₁(RP³) = Z₂ (the antipodal loop winds
    once).  RP³ = S³/Z₂ has TWO spin structures (H¹(RP³, Z₂) = Z₂):
    the trivial one (even winding, P=+) and the non-trivial one (odd
    winding, P=−).  The per-generation charged-quotient index = 1 selects
    the non-trivial quotient class used by the charged response.  It does
    not turn the complete 8+8 matter carrier into a center-biased source.
    """
    n_left = sum(c for name, _, _, c in _ONE_GENERATION if name in ("Q_L", "L_L"))
    n_right = N_WEYL_PER_GENERATION - n_left
    return n_left - n_right


def chiral_asymmetry() -> int:
    """Backward-compatible name for :func:`charged_quotient_index`.

    The returned integer belongs to the 15-coordinate gauge-active quotient.
    It is not a center bias of the complete 8+8 matter carrier.
    """
    return charged_quotient_index()


def tau_statistical() -> float:
    """Charged-response modulus τ = (N_L − N_R)/(N_f · ΣY²) = 1/50.

    Derivation: the charged-quotient index is N_L − N_R = 1
    (the left doublets carry 8 components, the right singlets 7);
    N_f = 15 is the number of Weyl fermions per generation; ΣY² =
    10/3 is the hypercharge capacity per generation.  Hence
    τ = 1/(15 · 10/3) = 1/50 = 0.02.

    Equivalently, tau is the charged-quotient index per gauge-active Weyl
    degree of freedom, normalized by the first non-zero hypercharge moment. This dimensionless
    content ratio supplies the modulus used by the homogeneous EC ansatz and
    the squash-response chain.
    """
    # Select the gauge channel by the support of the actual Y operator on
    # all sixteen coordinates.  No coordinate is discarded from the carrier.
    from cg_core.ec_variation import full_carrier_response
    return float(full_carrier_response()["gauge_conditioned_tau"])


def _self_test() -> None:
    assert N_WEYL_PER_GENERATION == 15
    assert N_WEYL_TOTAL == 45
    assert abs(hypercharge_sum_sq() - 10.0 / 3.0) < 1e-12
    assert abs(hypercharge_sum()) < 1e-15           # ΣY = 0 (anomaly)
    assert abs(hypercharge_sum_cube() + 4.0 / 9.0) < 1e-12  # ΣY³ = -4/9
    assert all(value == 0 for value in chiral_anomalies().values())
    assert abs(float(finite_source_response()["tau"]) - tau_statistical()) < 1e-15
    assert chiral_asymmetry() == 1
    assert abs(tau_statistical() - 0.02) < 1e-15
    # The content identity N_L = N_g: left-handed content =
    # colour generators, right-handed = N_g − 1.
    assert N_LEFT == N_G_COLOR == 8, "N_L = N_g = 8 (deep symmetry)"
    assert N_RIGHT == N_G_COLOR - 1 == 7, "N_R = N_g − 1 = 7"
    print("sm_content self-test OK")


if __name__ == "__main__":
    _self_test()
