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
cg_core/ec_structure.py — V5.0: the Einstein-Cartan structure of RP³
=================================================================

PURPOSE
-----------------------------------
The internal space carries an Einstein-Cartan (EC) geometry: the
connection has both curvature and torsion.  The dimensionless torsion
production modulus is the charged-quotient response ratio tau=1/50. The EC data —
the torsion ansatz, the curvature relation, the contorsion — enter
the EC mass shifts of the spectrum (spectrum_loop: the gauge
τ²/(6L²) and fermion 3τ²/(8L²) torsion shifts, the gauge
C₂/(2L²) Camporesi mass) and the EC action (squash_level_transfer.ec_action).
This module records the isotropic geometry; connection_action computes the
complete connection curvature and compares its action with the production
quadratic torsion response. Those functionals are distinct away from the
isotropic trace sector.

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

Here K denotes the legacy connection table satisfying
K_abc-K_acb=T_abc. In Cartan's convention T=de+omega wedge e the actual
connection difference is C=-K. The existing signed spin operator uses K;
thus its modulus has the opposite sign to the Cartan torsion coefficient.
Curvature and torsion norms, being quadratic, do not detect this sign.
connection_action.cartan_connection and cartan_spin_connection_vertices
keep the conversion explicit.

THE CONTENT CLOSURE FOR τ
-------------------------
The torsion modulus is the dimensionless charged-quotient response ratio
(see sm_content.tau_statistical)

    τ = ⟨χ⟩ / Π_ren = (N_L − N_R)/(N_f · ΣY²) = 1/50,

Here N_L-N_R=1 is the index of the 15-coordinate charged quotient,
N_f=15 is its Weyl-fermion count, and sum Y^2=10/3 is its quadratic
hypercharge moment.  The neutral right coordinate completes the full
8+8 carrier and does not enter this charged trace.  The same response is
computed on all sixteen coordinates using P=support(Y) in ec_variation.
The production spectrum uses it as the coefficient of
T^a_bc=(tau/L) epsilon^a_bc.  The separate contorsion variation and
minimal spin-current vertex are evaluated in ec_variation; a neutral
hypercharge vertex does not imply a neutral spin-connection vertex.
The minimal internal spin vertex has no trace-free dual-torsion component.
The three independent quadratic invariants have production Hessians
(-12a,8a/3,12a); their transverse parts eliminate uniquely at this
algebraic level. These coefficients are not fixed by rotational symmetry.
The minimal classical matter and torsion equations are evaluated together
in ec_variation.minimal_classical_stationarity. In the positive-metric
domain the coupled Dirac operator is invertible, so this action has only
the zero-field, zero-torsion stationary point. The charge response 1/50
is therefore not a nonzero stationary point of that minimal action.

The retained production response catalogue uses shifts quadratic in tau.
The minimally coupled Dirac operator instead has D_tau=D_0-3tau/(4L).
Its square also has the term -3tau D_0/(2L). The catalogue's fermion
insertion 3tau^2/(8L^2) is not that complete Dirac square. The comparison
is explicit in ec_variation.minimal_torsion_spectral_terms.

THE CURVATURE RELATION
----------------------
R(ω) = R_LC − (3/2)(τ/L)²          (Hehl 1976; Shapiro 2002)
R(ω)/R_LC = 1 − (τ/2)²

The full contraction is R(omega)-R_LC=div J+I1/4+I2/2-I3.
For smooth global fields on closed RP3 the divergence integrates to zero.
The production action a I1+4a I2-7a I3/3 is not proportional to this
curvature functional on the complete torsion space; the comparison and
its extra transverse terms are computed in connection_action.

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
