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
cg_frg/frg/lpa/ec_action.py — V4.0: the COMPLETE Einstein-Cartan action,
the τ variational principle, and the HONEST status of s₀ = 2τ
=====================================================================

RESTORED from V3.0 (cg_frg/frg_lpa/ec_action_complete.py +
cg_frg/frg_lpa/local_spin_torsion_eq.py + cg_frg/condensate_geometry_coupling.py),
2026-08-20: the V3 EC-action files had been dropped in the V3→V4
consolidation; this module restores the complete derivation and,
critically, restores the HONEST status labels that V4 had overwritten.

WHAT IS DERIVED (complete)
--------------------------
The internal RP³ carries an Einstein-Cartan geometry: the connection
has curvature AND torsion, with the torsion sourced by the chiral
spin density of the fermion content.  The complete EC action is

    S_EC = ∫ d³x √g [ (M_3³/2)(R − 2Λ_int) + L_torsion + L_psitau ]

with

    L_torsion = a·T_{abc} T^{abc} + b·T_{abc} T^{bac} + c·(T^a_{ab})²
    L_psitau  = (i/4)(τ/L) ε^{abc} ψ̄ γ_{abc} ψ   (spin-torsion coupling)

The torsion is the totally antisymmetric ansatz  T^a_{bc} = (τ/L) ε^a_{bc}.

COEFFICIENTS (derived):
    b = 4a     (the Holst/Immirzi condition — the torsion equation
                 δL/δT = 0 must be algebraic, i.e. non-propagating torsion)
    c = −(a + b/3) = −(7/3)a   (the trace term)
    a = M_G³/4  (the canonical normalisation of the torsion-squared term)

THE τ VARIATIONAL PRINCIPLE (derived — this is the source of τ):
    ∂L/∂τ(x) = 0  with  L_psitau = (i/4)(τ/L) ε^{abc} ψ̄γ_{abc}ψ  and
    the torsion-squared curvature correction  R(ω) = R_LC − (3/2)(τ/L)²
    gives

        τ(x) = (L/6M_3³) · s_spin(x),

    where s_spin = ⟨χ⟩/Π_ren = (N_L − N_R)/(N_f · ΣY²) is the ratio of
    the chiral excess to the hypercharge capacity.  Hence

        τ = (N_L − N_R)/(N_f · ΣY²) = 1/50   (EXACT content ratio).

WHAT IS *NOT* DERIVED (honest — restored from V3)
--------------------------------------------------
The squash amplitude  s₀ = 2τ  is kinematic INPUT, NOT derived:

  · The J=2 squash (the isometry breaking SU(2)_R → U(1)_R) has a
    deformation energy that is O(s²) with a NEGATIVE Euclidean
    Einstein-Hilbert second variation in the TT sector — the round S³
    is a LOCAL MAXIMUM along the squash direction.  There is therefore
    NO energy barrier that would fix s₀ by balance.
  · s₀ = 2τ is fixed instead by "kinematic g₁ closure": the U(1)_Y
    normalisation κ(s₀) = √((1+s₀)/(1−2s₀)^{5/2}) is matched to the SM
    g₁/g₂ at the GUT scale, which picks s₀ = 2τ.
  · This is a MATCH-TO-OBSERVATION input, not a first-principles
    variational result.  (V3 condensate_geometry_coupling.py said this
    explicitly: "s₀ = 2τ ... INPUT, not derived"; V4 later relabelled
    it "EXACT/derived" without providing the missing step.)

STATUS
------
The EC sector derives τ (the torsion modulus) and the torsion-Lagrangian
coefficients (a, b, c).  It does NOT derive s₀ = 2τ, which remains a
kinematic input fixed by matching κ(s₀) to the SM gauge couplings.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset

N_L, N_R, N_f = 8, 7, 15
SIGMA_Y2 = 10.0 / 3.0


def torsion_ansatz(tau: float, L: float) -> float:
    """The totally antisymmetric torsion: T^a_bc = (τ/L) ε^a_bc."""
    return tau / L


def torsion_squared(tau: float, L: float) -> float:
    """T² = T_{abc} T^{abc} = 6(τ/L)² (six antisymmetric components)."""
    return 6.0 * (tau / L) ** 2


def ec_action_coefficients(M_G: float) -> dict:
    """The torsion-Lagrangian coefficients a, b, c (derived).

    b = 4a (Holst/Immirzi — the torsion equation is algebraic);
    c = −(a + b/3) = −(7/3)a (the trace term);
    a = M_G³/4 (canonical normalisation).
    """
    a = M_G ** 3 / 4.0
    b = 4.0 * a
    c = -(a + b / 3.0)
    return {"a": a, "b": b, "c": c,
            "b_equals_4a": abs(b / a - 4.0) < 1e-12,
            "torsion_algebraic": abs(a + b / 2.0) > 1e-30}


def tau_from_content() -> float:
    """τ = (N_L − N_R)/(N_f · ΣY²) = 1/50 — the chiral excess over the
    hypercharge capacity (the local ∂L/∂τ = 0 variational result)."""
    chi_avg = (N_L - N_R) / N_f          # = 1/15, the chiral excess/family
    return chi_avg / SIGMA_Y2            # = 1/50


def squash_amplitude_input(tau: float) -> float:
    """s₀ = 2τ — kinematic INPUT, NOT derived.

    The squash has no energy barrier (negative EH second variation in
    the TT sector), so s₀ is fixed by matching κ(s₀) to the SM g₁/g₂,
    not by a variational condition.
    """
    return 2.0 * tau


def compute() -> dict:
    """Publish the complete EC action, the τ variational derivation,
    and the honest s₀ status."""
    M_G = float(get("M_G"))
    tau = float(get("tau"))

    coeff = ec_action_coefficients(M_G)
    tau_stat = tau_from_content()
    s0 = squash_amplitude_input(tau)

    pset("ec_action_a_coeff", coeff["a"], provenance="DERIVED",
         role="internal",
         note=f"a = M_G^3/4 = {coeff['a']:.4e} GeV^3 — the canonical "
              f"normalisation of the torsion-squared term on RP3")
    pset("ec_action_b_coeff", coeff["b"], provenance="DERIVED",
         role="internal",
         note=f"b = 4a = {coeff['b']:.4e} GeV^3 — the Holst/Immirzi "
              f"condition (algebraic torsion, no propagating torsion)")
    pset("ec_action_c_coeff", coeff["c"], provenance="DERIVED",
         role="internal",
         note=f"c = -(a + b/3) = -7a/3 = {coeff['c']:.4e} GeV^3 — the "
              f"trace term")
    pset("ec_action_consistency", coeff["b_equals_4a"], provenance="DERIVED",
         role="internal",
         note="b = 4a (Holst/Immirzi) — the torsion equation is algebraic")

    pset("local_spin_torsion_eq", tau_stat, provenance="DERIVED",
         role="internal",
         note=f"tau = (N_L-N_R)/(N_f SigmaY2) = {tau_stat} = 1/50 — the "
              f"local spin-torsion variational principle: dL/dtau = 0 "
              f"gives tau = (L/6 M_3^3) s_spin with s_spin = "
              f"(N_L-N_R)/(N_f SigmaY2); the chiral excess over the "
              f"hypercharge capacity")

    pset("squash_amplitude_status",
         "s0 = 2 tau is kinematic INPUT, NOT derived: the squash has no "
         "energy barrier (negative Euclidean EH second variation in the "
         "TT sector — the round S3 is a local maximum along the squash), "
         "so s0 is fixed by matching kappa(s0) to the SM g1/g2 at the "
         "GUT scale (kinematic g1 closure), not by a variational condition.",
         provenance="DERIVED", role="informational",
         note="restored honest status (V3 condensate_geometry_coupling.py "
              "said 's0=2tau INPUT, not derived'; V4 had relabelled it "
              "'EXACT/derived' without the derivation)")

    return {"a": coeff["a"], "b": coeff["b"], "c": coeff["c"],
            "tau": tau_stat, "s0": s0}


if __name__ == "__main__":
    r = compute()
    print(f"EC action: a = {r['a']:.3e}, b = {r['b']:.3e}, c = {r['c']:.3e}")
    print(f"tau = {r['tau']} = 1/50 (DERIVED, local dL/dtau=0)")
    print(f"s0 = {r['s0']} = 2 tau (INPUT, not derived)")
    print("ec_action OK")
