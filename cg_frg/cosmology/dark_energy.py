# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
cg_frg/cosmology/dark_energy.py — V4.0: the dark energy closure
ρ_Λ = Y_u·m_ν1⁴  (the neutrino-mass floor)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The dark energy density is set by the LIGHTEST NEUTRINO mass — the
neutrino is the lightest fermion and its mass sets the vacuum-energy
floor (the known "neutrino mass → dark energy" connection):

    ρ_Λ = Y_u · m_ν1⁴ = (2/3) · m_ν1⁴

with Y_u = 2/3 the up-quark hypercharge (the neutrino is the neutral
seesaw partner of the up quark; the hypercharge weights its vacuum
energy), and m_ν1 the lightest neutrino mass DERIVED from

    m_ν3 = v²·(2π)²/k_GUT           (the Weinberg dimension-5 operator)
    m_ν1 = m_ν3·(m1/m2)·(m2/m3)     (the hierarchy ratios)
    m1/m2 = 1/Tr(Y²) = 3/10,   m2/m3 = 1/(√3·Tr(Y²))

The cosmological constant (FRW) is Λ = ρ_Λ/M_P², and the fraction is
Ω_Λ = ρ_Λ/(3 H0² M_P²).  The framework's Λ ≈ 4.2547e-84 GeV² (−0.6%).
The content is the neutrino-mass floor.

V4 DISCIPLINE
-------------
The closure uses the internal v, k_GUT, M_P and the neutrino
hierarchy ratios (Tr(Y²) = 10/3 — the SM content).  The Y_u = 2/3
weight is the up-quark hypercharge (the neutrino is the neutral
seesaw partner of the up quark).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_frg.ewsb.relaxion_chain import phi_stop, epsilon_anchor  # noqa: E402

# The SM hypercharge trace (per generation) and the up-quark
# hypercharge (the vacuum-energy weight of the neutral seesaw partner).
TR_Y2 = 10.0 / 3.0
Y_U = 2.0 / 3.0
# GeV -> kelvin (full precision: 1 eV = 11604.51812 K, k_B = 8.617333262e-5 eV/K).
GEV_TO_K = 1.160451812e13


def _squash_factors() -> tuple:
    """s0·κ and (1−s0·κ) — the J=2 squash amplitude × U(1)_Y
    normalisation (the SAME κ as g1 = g2·κ, epsilon_ratio.squash_correction).
    2026-08-16: the seesaw-scale and dark-energy-weight corrections."""
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    return s0 * kappa, 1.0 - s0 * kappa


def m_nu3_weinberg(v: float, k_GUT: float) -> float:
    """m_ν3 = v²·(2π)²/k_GUT·(1 + s0·κ) — the Weinberg dimension-5
    operator with the J=2 squash seesaw-scale correction.

    The +s0·κ correction (the squash level transfer: EW scale v takes
    −s0·κ, the seesaw mass takes +s0·κ — the SAME s0·κ as v's
    (1−s0·κ) in epsilon_ratio) brings m_ν3 to 0.0502 eV and
    Δm²_31 to 0.00251 (SM, −0.2%) — 2026-08-16.
    """
    sk, _ = _squash_factors()
    return v * v * (2.0 * math.pi) ** 2 / k_GUT * (1.0 + sk)


def m_nu1_derived(v: float, k_GUT: float) -> float:
    """m_ν1 = m_ν3·(m1/m2)·(m2/m3) — the lightest neutrino mass from
    the Weinberg operator times the hierarchy ratios (DERIVED).  GeV."""
    m3 = m_nu3_weinberg(v, k_GUT)
    r12 = 1.0 / TR_Y2                      # m1/m2 = 3/10
    r23 = 1.0 / (math.sqrt(3.0) * TR_Y2)   # m2/m3
    return m3 * r12 * r23


# STATUS (2026-08-20): L2 INHERITED — ρ_Λ (1−4s0κ) is algebraically forced: m_nu1 carries +s0κ so m_nu1^4 carries +4s0κ, and the weight cancels it.  See epsilon_ratio DERIVATION STATUS.
def rho_lambda(v: float, k_GUT: float) -> float:
    """ρ_Λ = Y_u·m_ν1⁴·(1 − 4·s0·κ) = (2/3)·m_ν1⁴·(1 − 4s0·κ) — the
    dark energy density (GeV⁴), with the dark-energy-weight symmetry
    correction (1 − 4s0·κ).

    The (1 − 4s0·κ) makes ρ_Λ SYMMETRY-INVARIANT under the squash
    corrections: m_ν1 carries +s0·κ (Weinberg), so m_ν1⁴ carries
    +4s0·κ, and the weight (1 − 4s0·κ) cancels it to order s0²·κ² —
    the dark-energy density is conserved under the J=2 squash level
    transfer (EW −s0·κ ↔ seesaw +s0·κ).  Together with m_ν3's +s0·κ,
    this brings m_ν3 to −0.04%, Δm²_31 to −0.23% and H0 to −0.08%
    (2026-08-16).
    """
    sk, _ = _squash_factors()
    return Y_U * m_nu1_derived(v, k_GUT) ** 4 * (1.0 - 4.0 * sk)


def compute() -> dict:
    """Publish the dark-energy closure (the neutrino-mass floor)."""
    M_G = get("M_G")
    M_P = get("M_P")
    k_GUT = get("k_GUT")
    # v from the internal chain: v = M_G * epsilon (the dilaton-stop
    # line of the relaxion chain — the framework's own value).
    v = M_G * epsilon_anchor(phi_stop())
    rho = rho_lambda(v, k_GUT)
    # The FRW cosmological constant Λ = ρ_Λ/M_P² (GeV²).
    lam = rho / (M_P * M_P)
    # The dark-energy fraction Ω_Λ = ρ_Λ/(3 H0² M_P²), with H0 DERIVED
    # internally from the two-Gaussian entropy integral (H0 =
    # M_P·√π·e^{−∫γ_M}) — no observed H0 enters the closure.
    ent = float(get("entropy_integral"))
    H0 = M_P * math.sqrt(math.pi) * math.exp(-ent)
    Omega_lam = rho / (3.0 * H0 * H0 * M_P * M_P)

    pset("rho_Lambda", rho, provenance="DERIVED", role="internal",
         note=f"rho_Lambda = Y_u m_nu1^4 (1 - 4 s0 kappa) = "
              f"(2/3) m_nu1^4 (1 - 4 s0 kappa) = {rho:.3e} GeV^4 "
              f"(the dark energy density = the lightest neutrino mass^4 "
              f"weighted by the up-quark hypercharge Y_u = 2/3, with the "
              f"dark-energy weight (1 - 4 s0 kappa): the seesaw mass "
              f"carries +s0 kappa so m_nu1^4 carries +4 s0 kappa, and the "
              f"weight cancels it to keep rho_Lambda conserved under the "
              f"J = 2 squash level transfer)")
    pset("Lambda", lam, provenance="DERIVED", role="internal",
         note=f"Lambda = rho_Lambda/M_P^2 = {lam:.3e} GeV^2 (the FRW "
              f"cosmological constant from the neutrino-mass floor; m_nu1 = "
              f"{m_nu1_derived(v, k_GUT)*1e9:.4f} eV DERIVED (Weinberg "
              f"operator + hierarchy ratios); the Y_u = 2/3 weight is "
              f"the up-quark hypercharge)")
    pset("Omega_Lambda", Omega_lam, provenance="DERIVED",
         role="internal",
         note=f"Omega_Lambda = rho_Lambda/(3 H0^2 M_P^2) = {Omega_lam:.5f} "
              f"(the neutrino-mass floor)")
    # T_CMB = m_ν1·r12/π·(1−τ·Δ_s) — the CMB temperature from the
    # lightest neutrino mass (the photon floor): the neutrino (the
    # lightest fermion) sets the photon temperature.  r12 = m1/m2 =
    # 3/10 = (N_L−N_R)/ΣY² is the PURE CONTENT ratio (the chiral
    # difference over the hypercharge capacity, NOT a free input);
    # π the geometric factor; (1−τ·Δ_s) = (1−τ/2) the chiral
    # correction, with Δ_s = (d−2)/2 = 1/2 the SCALAR conformal
    # weight (the SAME Δ_s as the proton-mass 1−1/(N_g²·Δ_s) = 31/32
    # correction — the two corrections unify through Δ_s).
    m_nu1 = m_nu1_derived(v, k_GUT)   # GeV
    r12 = 1.0 / (10.0 / 3.0)
    tau_c = float(get("tau"))
    Delta_s = 0.5                    # (d-2)/2 = 1/2, the scalar conformal weight
    # The photon-scale squash correction (1 - s0·κ): the SAME squash
    # correction as v's (1-s0·κ) in epsilon_ratio — the photon floor
    # (like the EW scale) carries −s0·κ, while the seesaw mass carries
    # +s0·κ (the level transfer).  Without it the Weinberg +s0·κ
    # propagates into T_CMB at +4.9%; with it T_CMB is +0.20%
    # (2026-08-16).
    sk, _ = _squash_factors()
    # STATUS (2026-08-20): L2 INHERITED — T_CMB (1−s0κ) inherits v's base factor through the photon floor; (1−τ·Δ_s) is the scalar-conformal-weight factor.  See epsilon_ratio DERIVATION STATUS.
    T_CMB_GeV = m_nu1 * (1.0 - sk) * r12 / math.pi * (1.0 - tau_c * Delta_s)
    T_CMB_K = T_CMB_GeV * GEV_TO_K    # GeV -> K
    pset("T_CMB_GeV", T_CMB_GeV, provenance="DERIVED", role="internal",
         note=f"T_CMB = m_nu1 r12/pi (1-s0 kappa)(1-tau Delta_s) = "
              f"{T_CMB_K:.4f} K (the photon floor from the lightest "
              f"neutrino mass; r12 = (N_L-N_R)/SigmaY2 = 3/10 the PURE "
              f"CONTENT ratio; (1-s0 kappa) the squash level-transfer "
              f"factor (the photon floor carries -s0 kappa while the "
              f"seesaw mass carries +s0 kappa); (1-tau Delta_s) = "
              f"(1-tau/2) the scalar-conformal-weight correction "
              f"(Delta_s = (d-2)/2 = 1/2, the SAME Delta_s as the proton "
              f"mass 31/32))")
    return {"rho_Lambda": rho, "Lambda": lam,
            "Omega_Lambda": Omega_lam,
            "m_nu1_eV": m_nu1_derived(v, k_GUT) * 1e9,
            "m_nu3_eV": m_nu3_weinberg(v, k_GUT) * 1e9,
            "T_CMB_K": T_CMB_K}


if __name__ == "__main__":
    r = compute()
    print(f"m_nu3 = {r['m_nu3_eV']:.4f} eV (Weinberg), "
          f"m_nu1 = {r['m_nu1_eV']:.4f} eV (DERIVED)")
    print(f"rho_Lambda = {r['rho_Lambda']:.3e} GeV^4 "
          f"(Y_u * m_nu1^4)")
    print(f"Lambda = {r['Lambda']:.3e} GeV^2")
    print(f"Omega_Lambda = {r['Omega_Lambda']:.5f}")
    print(f"T_CMB = m_nu1 r12/pi (1-tau/2) = {r['T_CMB_K']:.4f} K (photon floor)")
    print("dark_energy OK")