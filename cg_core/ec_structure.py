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
connection has both curvature and torsion.  The dimensionless torsion
modulus is fixed by the fermion-content ratio tau=1/50.  The EC data —
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

THE CONTENT CLOSURE FOR τ
-------------------------
The torsion modulus is the dimensionless fermion-content ratio
(see sm_content.tau_statistical)

    τ = ⟨χ⟩ / Π_ren = (N_L − N_R)/(N_f · ΣY²) = 1/50,

Here N_L-N_R=1 is the chiral excess of one selected generation,
N_f=15 is its Weyl-fermion count, and sum Y^2=10/3 is its quadratic
hypercharge moment.  This closure fixes the coefficient of the
homogeneous isotropic torsion ansatz T^a_bc=(tau/L) epsilon^a_bc.

The torsion enters the spectrum only through τ² (the shifts below),
so the O(10⁻⁴) effect is the magnitude of the torsion.

THE CURVATURE RELATION
----------------------
R(ω) = R_LC − (3/2)(τ/L)²          (Hehl 1976; Shapiro 2002)
R(ω)/R_LC = 1 − (τ/2)²

with Ric_LC = (2/L²) g and R_LC = 6/L².  For τ = 0.02 the torsion
effect is O(10⁻⁴) — a tiny correction to the curvature.

IMPLEMENTATION
--------------
This module records the EC geometry used by the spectral mass shifts and
curvature relations.  The functions receive tau and L explicitly.
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

    The homogeneous isotropic antisymmetric ansatz is proportional to the
    invariant epsilon tensor; tau/L supplies its inverse-length scale.
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
