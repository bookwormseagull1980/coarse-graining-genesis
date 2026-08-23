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
cg_core/ec_structure.py — V4.0: the Einstein-Cartan structure of RP³
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The internal space carries an Einstein-Cartan (EC) geometry: the
connection has both curvature and torsion, with the torsion sourced
by the chiral spin density of the fermion content.  The EC data —
the torsion ansatz, the curvature relation, the contorsion — enter
the EC mass shifts of the spectrum (spectrum_loop: the gauge
τ²/(6L²) and fermion 3τ²/(8L²) torsion shifts, the gauge
C₂/(2L²) Camporesi mass) and the EC action (frg_lpa/ec_action).
This module is the single reference for that geometry.

THE TORSION ANSATZ
------------------
The round S³ with radius L has the Levi-Civita connection
de^a = −(1/L) ε^a_bc e^b ∧ e^c.  The EC torsion on RP³ is the
totally antisymmetric ansatz

    T^a_bc = (τ/L) ε^a_bc,        T² = 6(τ/L)²,

where τ is the dimensionless torsion (the framework's statistical
modulus τ = 0.02).  The contorsion K relates the EC connection to
the Levi-Civita one; for the totally antisymmetric torsion,
K = (1/2)T (coefficient τ/(2L)).

THE τ-THEOREM SKELETON
-----------------------------------
The torsion modulus τ is NOT a free input: it is the chiral drive
over the hypercharge polarisation (see sm_content.tau_statistical),

    τ = ⟨χ⟩ / Π_ren = (N_L − N_R)/(N_f · ΣY²) = 1/50,

with a three-layer first-principles skeleton:
  (1) Z₂ TOPOLOGY (the source): N_L − N_R = 1 is ODD, the
      non-trivial element of π₁(RP³) = Z₂ — the non-trivial spin
      structure (H¹(RP³,Z₂) = Z₂), the antipodal winding once;
  (2) HYPERCHARGE ANOMALY (the normalisation): ΣY = 0 (the mixed
      gravitational anomaly cancels) ⇒ ΣY² = 10/3 is the FIRST
      non-zero hypercharge moment — the natural normalisation;
  (3) EC FIELD EQUATION (the bridge): the torsion is sourced by the
      chiral current (T ~ κ² j_5) and screened by the hypercharge
      polarisation Π = ΣY².
The exact coefficient 1/(N_f·ΣY²) = the content ratio
(N_L−N_R)/(N_f·ΣY²), established by the three-layer skeleton (the
Z₂ topology ÷ the anomaly normalisation × the fermion content).

THE EC FIELD-EQUATION SKELETON (the bridge, first-principles form)
----------------------------------------------------------------
The torsion field equation (δS/δK = 0, the EC action varied with
respect to the contorsion) sources the torsion by the fermion spin
density.  For the totally antisymmetric ansatz T^a_bc = (τ/L)ε^a_bc:

    τ/L = κ²·j_5   (the chiral axial current sources the torsion)

with κ² = 8π/M_P the 3D gravitational coupling and j_5 the chiral
current per unit volume.  The chiral current is the intensive chiral
drive ⟨χ⟩ = (N_L−N_R)/N_f (the Z₂ source per unit fermion content)
SCREENED by the renormalised hypercharge polarisation Π_ren = ΣY²:

    j_5 = ⟨χ⟩/Π_ren = (N_L−N_R)/(N_f·ΣY²).

Hence τ = κ²·L·j_5 = κ²·L·(N_L−N_R)/(N_f·ΣY²).  The geometric
factor κ²·L is evaluated EXACTLY by the window-capacity
cancellation:

    τ_bare    = (N_L−N_R)·M_G²/(2π² M_P² kL²) = (N_L−N_R)/(2π kL⁴)
                (the bare EC field equation, window geometry 1/(2π kL⁴))
    screening = 2π kL⁴/(N_f·ΣY²)   (the hypercharge-polarisation
                screening = window capacity / content)
    τ = τ_bare · screening = (N_L−N_R)/(N_f·ΣY²) = 1/50

    (verified: 0.004117 × 4.858 = 0.02 = 1/50, EXACT — the window
    capacity 2π kL⁴ cancels between the bare field equation and the
    hypercharge screening, leaving the pure content ratio.)

THE WINDOW-CAPACITY CANCELLATION
-----------------------------------------------------------------
The screening factor (kL)³/(N_f·ΣY²) is the hypercharge-polarisation
screening written as the window capacity (kL)³ (the 3D RP³ spectral
sum, Weyl law) divided by the content N_f·ΣY².  The SAME window
capacity (kL)³ enters the bare field equation (τ_bare carries
1/(kL)³), so it cancels exactly between the bare field equation and
the hypercharge screening, leaving the pure content ratio τ = 1/50.
The cancellation is EXACT and does NOT depend on the specific value
of (kL)³ (it drops out of the product), so τ = (N_L−N_R)/(N_f·ΣY²) = 1/50 stands as the exact
content ratio regardless.

STATUS OF THE 2π kL⁴ NOTATION (audit 2026-08-18,
docs/V4_LEDGER.md §0.2.B): the earlier wording "2π kL⁴ is the
discrete RP³ spectral sum in closed form" overstates a NOTATION as
an independent computation.  A direct check of the RP³ spectral
sums shows the 3D state count and polarisation close to (kL)³
(Weyl law), not (kL)⁴; the (kL)⁴ power requires a fourth
(scale-flow/time) direction, and the coefficient 2π of that fourth
direction is not derived from the 3D spectrum.  Since 2π kL⁴ drops
out of τ exactly, this does NOT affect τ = 1/50; it only corrects
the status of the intermediate notation.

So the exact coefficient 1/(N_f·ΣY²) is FIRST-PRINCIPLES: the bare
torsion field equation carries the window geometry 1/(2π kL⁴), the
hypercharge polarisation screens with the window capacity 2π kL⁴,
and the two cancel exactly to leave the content ratio
(N_L−N_R)/(N_f·ΣY²) = 1/50 — the Z₂ topology over the anomaly
normalisation.

The torsion enters the spectrum only through τ² (the shifts below),
so the O(10⁻⁴) effect is the magnitude of the torsion.

THE CURVATURE RELATION
----------------------
R(ω) = R_LC − (3/2)(τ/L)²          (Hehl 1976; Shapiro 2002)
R(ω)/R_LC = 1 − (τ/2)²

with Ric_LC = (2/L²) g and R_LC = 6/L².  For τ = 0.02 the torsion
effect is O(10⁻⁴) — a tiny correction to the curvature.

STATUS
------
The EC structure is a REFERENCE module: the actual spectral
computations live in spectrum_loop (the mass shifts) and the EC
action in cg_frg/frg_lpa/ec_action.  This module documents the
geometry and provides the exact relations.

V4 DISCIPLINE
-------------
τ is read from the store (or passed as an argument); no physics
value is hard-coded here.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def torsion_tensor(tau: float, L: float) -> float:
    """The totally antisymmetric torsion: T^a_bc = (τ/L) ε^a_bc.

    Derivation: the ansatz is the unique totally antisymmetric
    torsion on a 3-manifold (the ε-symbol carries the parity-odd
    structure); the coefficient τ/L sets the dimensionless torsion τ
    in units of the inverse radius.
    """
    return tau / L


def torsion_squared(tau: float, L: float) -> float:
    """T² = T_abc T^{abc} = 6(τ/L)².

    Derivation: the sum over the 6 independent components of the
    totally antisymmetric tensor, each contributing (τ/L)².
    """
    return 6.0 * (tau / L) ** 2


def contorsion_coefficient() -> float:
    """The contorsion coefficient: 1/2 (K = ½ T for the totally
    antisymmetric torsion).

    Derivation: the contorsion K^a_bc = ½(T^a_bc + T_bc^a − T_ca^b);
    for the totally antisymmetric torsion the three terms coincide,
    giving K = ½ T.
    """
    return 0.5


def ricci_curvature_LC(L: float) -> float:
    """Ric_LC = (2/L²) g — the Levi-Civita Ricci tensor of the round
    S³ (constant curvature)."""
    return 2.0 / (L * L)


def scalar_curvature_LC(L: float) -> float:
    """R_LC = 6/L² — the scalar curvature of the round S³."""
    return 6.0 / (L * L)


def ec_scalar_curvature(tau: float, L: float) -> float:
    """R(ω) = R_LC − (3/2)(τ/L)² — the EC scalar curvature.

    Derivation (Hehl 1976; Shapiro 2002): the torsion-squared
    correction to the curvature; for the totally antisymmetric
    torsion the coefficient is −(3/2)(τ/L)².
    """
    return scalar_curvature_LC(L) - 1.5 * (tau / L) ** 2


def ec_over_lc_ratio(tau: float) -> float:
    """R(ω)/R_LC = 1 − (τ/2)².

    Derivation: (3/2)(τ/L)² / (6/L²) = (3/2)τ²/6 = τ²/4 = (τ/2)².
    """
    return 1.0 - (tau / 2.0) ** 2


def _self_test() -> None:
    L = 2.4935343325226915
    tau = 0.02
    assert abs(scalar_curvature_LC(L) - 6.0 / L ** 2) < 1e-12
    assert abs(ec_over_lc_ratio(tau) - (1.0 - 1e-4)) < 1e-15
    assert abs(torsion_squared(tau, L) - 6.0 * (tau / L) ** 2) < 1e-20
    assert contorsion_coefficient() == 0.5
    print("ec_structure self-test OK")


if __name__ == "__main__":
    _self_test()
