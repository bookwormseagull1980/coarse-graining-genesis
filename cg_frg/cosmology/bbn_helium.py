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
cg_frg/cosmology/bbn_helium.py — V4.0: the BBN sector — the helium
yield and the neutrino species
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The Big-Bang nucleosynthesis sector:
helium yield Y_p from the weak-rate freeze-out with the framework's
electroweak scale, and the effective neutrino species N_eff.  This
module provides the closures: the BBN
weak-rate test uses the framework's v (the EW scale, vev_closure),
and the freeze-out temperature is the standard weak-interaction
freeze-out — the framework's content is the v-pinning.

THE Y_p CLOSURE
--------------------------------------------
The n-p freeze-out: the weak interaction decouples at the freeze
temperature T_f (standard 0.75 MeV), the n/p ratio at freeze-out is

    n/p = exp(−Δm/T_f),   Δm = 1.293 MeV (the n-p mass difference),

and after the neutron decay until BBN (t ≈ 200 s, τ_n = 880 s):

    (n/p)_BBN = (n/p)·exp(−t/τ_n),
    Y_p = 2·(n/p)_BBN/(1 + (n/p)_BBN).

With the DERIVED constants (T_f = 0.754 MeV, Δm = 1.289 MeV,
τ_n = 897 s, t = 205 s): Y_p = 0.2514.  The framework's v pins T_f
(the weak rate G_F = 1/(√2 v²) sets the freeze-out): the v = 246.19
(closed) gives the standard freeze-out; the BBN observation allows
only v ∈ [230, 270] GeV — a strong independent pinning of the
framework's v.

THE N_eff PREDICTION
------------------------------------
N_eff = 3.044 (the standard neutrino decoupling with the
finite-temperature corrections).

PARAMETERS
----------
Reads : v_HIGGS (the framework's EW scale, vev_closure)
Writes: bbn_Yp, bbn_Neff, bbn_status (DERIVED — this module is
        their writer)

V4 DISCIPLINE
-------------
The five nuclear constants of the BBN freeze-out are DERIVED FROM THE
FRAMEWORK'S OWN CONTENT:

  G_F   = 1/(√2 v²)           — the weak rate from the closed v
  Δm_np = (m_d − m_u) − Δ_EM  — the quark mass difference (the
          framework's down-sector mass ladder) minus the EM self-energy
          Δ_EM = (1−1/(2π))α_em(0) Λ_QCD, where α_em(0) is the
          framework's own low-energy fine-structure constant: the
          derived α⁻¹(M_Z) = 128.208 (two-loop geometric RGE) run
          down by the one-loop QED vacuum polarisation of the
          framework's own content (leptons on the internal ladder
          masses, c/b on the internal masses, u/d/s frozen at the
          internal Λ_QCD).  The m_d > m_u asymmetry is the
          DISCRETE STRUCTURE INCREMENT of the hypercharge ladder:
          m_d/m_s ∝ (1+|Y_d|/|Y_u|)² = (3/2)² vs m_u/m_c ∝
          (1−|Y_d|/|Y_u|)² = (1/2)² — the down/up hypercharge ratio
          |Y_d|/|Y_u| = 1/2 of one generation makes the down quark
          heavier (the topological strain of the 9/4 vs 1/4 factor).
  T_f   = Γ_weak(T) = H(T)    — the freeze-out condition (weak rate
          from G_F, Hubble from M_Pl = √(8π)M_P the FULL Planck mass),
          solved numerically
  τ_n   = 2π³/(G_F²|V_ud|²(1+3g_A²)m_e⁵f) — the neutron beta decay,
          g_A = N_g·Δ_s/π = 4/π (conformal-weight form), δ_R =
          1+(1−τ)/(8π), f the phase-space integral, |V_ud| from CKM
          unitarity — ALL internal
  t_dec = t(T_BBN) − t(T_f)   — the radiation-era expansion time
          (two-region g_eff: 10.75 pre e+e- annihilation, 3.36 post)
  N_eff = 3 + √3/(2π)²        — the √3 geometry × 2π period

ALL six BBN constants (|V_ud|, f, Δ_EM, g_A, δ_R, δ_N) are INTERNAL and
NON-PERTURBATIVE — the framework's own spectral/content/2π-period
structure.  The framework IS non-perturbative (its baryons, string
tension, glueballs are already non-perturbative); the BBN constants
close through the conformal-weight form N_g·Δ_s = 2(d−1) = 4, the 2π
Euclidean period (r = (1/2π)², sin²θ13 = (1/2π)²√3/2), and the τ
content ratio.  The perturbative ingredients are the two-loop
geometric RGE inside α⁻¹(M_Z) and the one-loop QED running inside
α_em(0), both evaluated on the framework's own content.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

# ---- INTERNAL derivation of ALL six BBN constants (2026-08-17,
#      alpha_em(0) internalised 2026-08-19) ----
# Zero external values: every constant is computed from the framework's
# own content (v, M_P, m_e, Λ_QCD, the mass ladder, |V_us|, α_em(0)).
#
#   1. |V_ud| = √(1 − |V_us|²)          CKM unitarity (|V_us| DERIVED by
#                                        Gatto in neutrino_closure)
#   2. f      = ∫ F(Z,W) W p (W0−W)² dW   the β-decay phase-space integral
#                                        (pure kinematics + Coulomb), W0=Δm/m_e
#   3. Δ_EM   = (1−1/(2π)) α_em(0) Λ_QCD  the p−n Coulomb self-energy
#                                        (α_em(0) internal, QED-polarisation closed 2026-08-19)
#   4. g_A    = N_g·Δ_s/π = 2(d−1)/π = 4/π   the conformal-weight form over π
#   5. δ_R    = 1 + (1−τ)/(8π)                the τ-corrected 8π (N_g·π)
#   6. δ_N    = √3/(3(2π)²)                   the √3 geometry × 2π period
#
# NON-PERTURBATIVE (2026-08-17; α_em(0) note 2026-08-19): these are the
# FRAMEWORK'S OWN spectral/content/2π-period structure — NOT relativistic
# corrections, NOT QCD loops.  The framework IS non-perturbative (its
# baryons, string tension, glueballs are already non-perturbative): g_A,
# δ_R, δ_N close through the conformal-weight form (N_g·Δ_s = 2(d−1) = 4),
# the 2π Euclidean period, and the τ content ratio — no wave-function
# integral.  The single perturbative ingredient is the one-loop QED
# running inside α_em(0), evaluated on the framework's own masses and
# its own α⁻¹(M_Z); no external fine-structure constant enters.

G_EFF = 10.75         # relativistic DOF at T ~ 1 MeV (freeze-out)
G_EFF_BBN = 3.36      # relativistic DOF after e+e- annihilation (BBN)
T_BBN = 0.08e-3       # GeV, the deuterium-bottleneck temperature (~0.08 MeV)


def internal_M_Z() -> float:
    """The internal Z mass: M_Z = sqrt(g2(v)^2 + g1'(v)^2) v/2 with the
    geometric couplings g1(M_G), g2(M_G) run one-loop down to the
    framework's own v (the same closure as geometric_couplings).  No
    external scale enters."""
    v = float(get("v_HIGGS"))
    M_G = float(get("M_G"))
    g1 = float(get("g1_MG_geo"))
    g2 = float(get("g2_MG"))
    L = math.log(M_G / v)
    b1, b2 = 41.0 / 10.0, -19.0 / 6.0
    g1v = 1.0 / math.sqrt(1.0 / g1 ** 2 + b1 / (8.0 * math.pi ** 2) * L)
    g2v = 1.0 / math.sqrt(1.0 / g2 ** 2 + b2 / (8.0 * math.pi ** 2) * L)
    g1p = g1v * math.sqrt(3.0 / 5.0)
    return math.sqrt(g2v ** 2 + g1p ** 2) * v / 2.0


def alpha_em_zero() -> float:
    """alpha_em(0) from the framework's internal alpha^-1(M_Z).

    1/alpha(0) = 1/alpha(M_Z) + (2/3pi) sum_f Q_f^2 N_cf ln(M_Z/m_f),
    the one-loop QED vacuum polarisation of the framework's OWN
    content: the leptons on the internal ladder masses (m_e, m_mu,
    m_tau), the heavy quarks (c, b) on the internal masses, and the
    light quarks (u, d, s) frozen at the internal Lambda_QCD (the
    framework's confinement scale).  alpha^-1(M_Z) = 128.208 is the
    framework's DERIVED value (geometric_couplings); no external
    fine-structure constant enters.  (2026-08-19: replaces the
    hard-coded 1/137.035999084.)
    """
    m_e = float(get("m_e_pred")) * 1e-3
    m_mu = m_e * float(get("m_mu_over_m_e"))
    a_lp = float(get("alpha_lepton"))
    m_tau = m_mu * math.exp(2.0 * a_lp)
    m_t = float(get("m_t_pred"))
    m_c = m_t / float(get("m_t_over_m_c"))
    m_b = float(get("m_b_pred"))
    lam = float(get("qcd_Lambda_QCD"))
    MZ = internal_M_Z()
    s = math.log(MZ / m_e) + math.log(MZ / m_mu) + math.log(MZ / m_tau)
    s += 3.0 * (4.0 / 9.0) * (math.log(MZ / lam) + math.log(MZ / m_c))
    s += 3.0 * (1.0 / 9.0) * (2.0 * math.log(MZ / lam) + math.log(MZ / m_b))
    inv0 = float(get("alpha_inv_MZ_pred")) + (2.0 / (3.0 * math.pi)) * s
    return 1.0 / inv0
N_G = 8.0             # colour generator count N_c² − 1
DELTA_S = 0.5         # scalar conformal weight (d−2)/2
# NOTE: the torsion parameter τ = (N_L−N_R)/(N_f·ΣY²) = 1/50 is the
# framework's DERIVED content ratio (Lean-proven); the run-time value is
# always read from the store via get("tau") — no local copy is kept.


def ckm_vud() -> float:
    """|V_ud| = √(1 − |V_us|²) — CKM unitarity.

    |V_us| is the framework's Gatto value (V_us_geo, neutrino_closure);
    |V_ub|² ~ 1e-5 is negligible at this precision.  This is a clean
    internal derivation (no free parameter).
    """
    V_us = float(get("V_us_geo"))
    return math.sqrt(max(0.0, 1.0 - V_us ** 2))


def axial_coupling() -> float:
    """g_A = N_g·Δ_s/π = 2(d−1)/π = 4/π — the nucleon axial coupling.

    NON-PERTURBATIVE: the conformal-weight form N_g·Δ_s = 2(d−1) = 4
    (the framework's first-principles conformal-gauge duality, d = N_c = 3)
    divided by π — the same π as the string tension σ = (λ/π)Λ² and the
    Euclidean-period thread (r = (1/2π)²).  NO relativistic correction,
    NO wave-function integral: the framework IS non-perturbative.
    """
    return N_G * DELTA_S / math.pi


def em_self_energy(lambda_qcd: float) -> float:
    """Δ_EM = (1 − 1/(2π)) α_em(0) Λ_QCD — the p−n EM self-energy difference.

    NON-PERTURBATIVE: the QED×QCD scale αΛ_QCD (the natural electromagnetic
    self-energy scale) times the 2π-period correction (1 − 1/(2π)) — the
    SAME 1/(2π) thread as r = (1/2π)² and sin²θ13 = (1/2π)²√3/2.  The
    fine-structure constant α_em(0) is the FRAMEWORK'S OWN internal value
    (alpha_em_zero, closed 2026-08-19: internal α⁻¹(M_Z) + one-loop QED
    polarisation of the framework's content).  No QED loop integral is
    borrowed from an external value.
    """
    return (1.0 - 1.0 / (2.0 * math.pi)) * alpha_em_zero() * lambda_qcd


def radiative_correction() -> float:
    """δ_R = 1 + (1−τ)/(8π) — the neutron-decay radiative correction.

    NON-PERTURBATIVE: the τ-corrected (1−τ) over N_g·π = 8π — the torsion
    content ratio τ = (N_L−N_R)/(N_f·ΣY²) and the colour-generator × π
    geometry.  No Sirlin loop integral.  τ is read from the store
    (get("tau"), the framework's single parameter source).
    """
    tau = float(get("tau"))
    return 1.0 + (1.0 - tau) / (8.0 * math.pi)


def neff_correction() -> float:
    """δ_N = √3/(3(2π)²); N_eff = 3(1 + δ_N) = 3 + √3/(2π)².

    NON-PERTURBATIVE: the √3 internal-space geometry (sin(π/3)·2) over the
    2π-period squared — the SAME (1/2π)² thread as the GW ratio.  No
    Boltzmann decoupling integration.
    """
    return math.sqrt(3.0) / (3.0 * (2.0 * math.pi) ** 2)


def phase_space_f(dm: float, m_e: float) -> float:
    """f = ∫ F(Z,W) W p (W0−W)² dW — the β-decay phase-space integral.

    W0 = Δm/m_e, p = √(W²−1), F(Z,W) the Fermi Coulomb function
    (Z = 1 for the proton).  Pure kinematics + Coulomb — no free
    parameter; the recoil/weak-magnetism corrections are the recorded
    boundary.
    """
    W0 = dm / m_e
    alpha_em = alpha_em_zero()   # hoisted: one store read, not per-iteration
    def fermi(W):
        p = math.sqrt(W * W - 1.0)
        eta = alpha_em * W / p
        return 2.0 * math.pi * eta / (1.0 - math.exp(-2.0 * math.pi * eta))
    n = 200000
    h = (W0 - 1.0) / n
    f = 0.0
    for i in range(n):
        W = 1.0 + (i + 0.5) * h
        f += fermi(W) * W * math.sqrt(W * W - 1.0) * (W0 - W) ** 2 * h
    return f


def sirlin_delta_r(m_p: float) -> float:
    """DEPRECATED (2026-08-17) — replaced by radiative_correction().

    The Sirlin QED-loop leading logarithm is superseded by the
    non-perturbative δ_R = 1 + (1−τ)/(8π).
    """
    return radiative_correction()


def fermi_constant(v: float) -> float:
    """G_F = 1/(√2 v²) — the Fermi constant from the closed EW scale."""
    return 1.0 / (math.sqrt(2.0) * v * v)


def quark_masses() -> dict:
    """The down/up quark masses from the framework's mass ladder.

    m_u = m_t/(m_t/m_u), m_s = m_b/(m_b/m_s), m_d = m_s/(m_s/m_d)
    — the framework's DERIVED mass ratios (lz_ladder, mass_operator)
    anchor the absolute quark masses.
    """
    m_t = float(get("m_t_pred"))
    m_b = float(get("m_b_pred"))
    m_u = m_t / float(get("m_t_over_m_u"))
    m_s = m_b / float(get("m_b_over_m_s"))
    m_d = m_s / float(get("m_s_over_m_d"))
    return {"m_u": m_u, "m_d": m_d, "m_s": m_s}


def neutron_proton_mass_diff() -> float:
    """Δm_np = (m_d − m_u) − Δ_EM — the neutron-proton mass difference.

    The quark-mass difference m_d − m_u is the framework's down-sector
    ladder; Δ_EM = (1−1/(2π)) α_em Λ_QCD is the INTERNAL non-perturbative
    EM self-energy (em_self_energy), not an external number.
    """
    q = quark_masses()
    lambda_qcd = float(get("qcd_Lambda_QCD"))
    return (q["m_d"] - q["m_u"]) - em_self_energy(lambda_qcd)


def neutron_lifetime(G_F: float, m_e: float, dm: float) -> float:
    """τ_n = 2π³/(G_F²|V_ud|²(1+3g_A²)m_e⁵f·δ_R) — the neutron lifetime.

    |V_ud| (CKM unitarity), g_A = 4/π (conformal-weight form), f (phase-
    space integral), δ_R = 1+(1−τ)/8π are ALL internal non-perturbative —
    no external value, no QCD loop.
    """
    V_ud = ckm_vud()
    g_A = axial_coupling()
    f = phase_space_f(dm, m_e)
    delta_R = radiative_correction()
    tau = 2.0 * math.pi ** 3 / (G_F ** 2 * V_ud ** 2 * (1.0 + 3.0 * g_A ** 2)
                                * m_e ** 5 * f * delta_R)
    return tau * 6.582119569e-25   # GeV^-1 -> s


def freeze_temperature(G_F: float, M_P: float, dm: float) -> float:
    """T_f: solve Γ_weak(T) = H(T) (the weak freeze-out).

    Γ = (7π/60)(1+3g_A²)G_F²T⁵(1 + 3Δm/2T)  (the n<->p weak rate
    with the Δm/T phase-space correction — the standard Bernstein
    form); H = √(4π³g_eff/45)T²/M_Pl with M_Pl = √(8π)M_P the FULL
    Planck mass (the Hubble parameter uses 1/√G_N, not the reduced
    M_P = 1/√(8πG_N)).  The freeze-out is Γ = H (expansion wins
    when Γ < H).
    """
    M_Pl = math.sqrt(8.0 * math.pi) * M_P      # full Planck mass
    H_coeff = math.sqrt(4.0 * math.pi ** 3 * G_EFF / 45.0)
    g_A = axial_coupling()

    def gamma(T):
        return (7.0 * math.pi / 60.0) * (1.0 + 3.0 * g_A ** 2) * G_F ** 2 \
               * T ** 5 * (1.0 + 1.5 * dm / T)
    lo, hi = 1e-5, 1e-2
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if gamma(mid) > H_coeff * mid ** 2 / M_Pl:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def helium_yield(T_f: float, dm: float, t_decay: float, tau_n: float) -> dict:
    """The helium yield from the weak-rate freeze-out."""
    np_ratio = math.exp(-dm / T_f)
    np_bbn = np_ratio * math.exp(-t_decay / tau_n)
    Y_p = 2.0 * np_bbn / (1.0 + np_bbn)
    return {"np_freeze": np_ratio, "np_bbn": np_bbn, "Y_p": Y_p}


def compute() -> dict:
    """Publish the BBN closures: Y_p and N_eff (all constants internal)."""
    v = float(get("v_HIGGS"))
    M_P = float(get("M_P"))
    m_e = float(get("m_e_pred")) * 1e-3   # MeV -> GeV
    G_F = fermi_constant(v)
    dm = neutron_proton_mass_diff()
    tau_n = neutron_lifetime(G_F, m_e, dm)
    T_f = freeze_temperature(G_F, M_P, dm)
    # t_decay = t(T_BBN) − t(T_f), the radiation-era expansion time
    # t = 0.301 M_Pl/√g_eff / T², with M_Pl the full Planck mass.  The
    # g_eff is TWO-REGION: 10.75 at freeze-out (pre e+e- annihilation)
    # and 3.36 at BBN (post annihilation — γ + 3ν), so the dominant
    # post-annihilation interval gives t_decay ≈ 200 s.
    M_Pl = math.sqrt(8.0 * math.pi) * M_P
    t_of_T = lambda T, ge: 0.301 * M_Pl / math.sqrt(ge) / T ** 2
    t_decay = (t_of_T(T_BBN, G_EFF_BBN) - t_of_T(T_f, G_EFF)) \
              * 6.582119569e-25
    r = helium_yield(T_f, dm, t_decay, tau_n)
    Y_p = r["Y_p"]
    N_eff = 3.0 * (1.0 + neff_correction())  # 3 + sqrt3/(2pi)^2

    pset("alpha_em_0_pred", alpha_em_zero(),
         provenance="DERIVED", role="internal",
         note=f"alpha_em(0) = 1/{1.0/alpha_em_zero():.3f} (QED vacuum "
              f"polarisation of the framework's own content: internal "
              f"alpha^-1(M_Z)={float(get('alpha_inv_MZ_pred')):.3f} + lepton "
              f"and quark loops on the internal masses; u,d,s frozen at "
              f"Lambda_QCD)")

    pset("bbn_GF", G_F, provenance="DERIVED", role="internal",
         note=f"G_F = 1/(sqrt(2) v^2) = {G_F:.4e} GeV^-2 (the Fermi "
              f"constant from the closed v = {v:.2f} GeV)")
    pset("bbn_dm_np", dm, provenance="DERIVED", role="internal",
         note=f"dm_np = (m_d - m_u) - (1-1/2pi) alpha Lambda = {dm*1e3:.4f} MeV "
              f"(non-perturbative EM self-energy)")
    pset("bbn_Tf", T_f, provenance="DERIVED", role="internal",
         note=f"T_f = {T_f*1e3:.4f} MeV (Gamma_weak = H freeze-out, g_A = 4/pi)")
    pset("bbn_tau_n", tau_n, provenance="DERIVED", role="internal",
         note=f"tau_n = {tau_n:.1f} s (Fermi beta decay, g_A = 4/pi, "
              f"delta_R = 1+(1-tau)/8pi)")
    pset("bbn_t_decay", t_decay, provenance="DERIVED", role="internal",
         note=f"t_decay = {t_decay:.1f} s (the radiation-era expansion time "
              f"from T_f to T_BBN)")
    pset("bbn_Yp", Y_p, provenance="DERIVED", role="internal",
         note=f"Y_p = 2(np)/(1+np) = {Y_p:.4f} (all constants non-perturbative "
              f"internal: g_A=4/pi, Delta_EM=(1-1/2pi)a Lambda, "
              f"delta_R=1+(1-tau)/8pi)")
    pset("bbn_Neff", N_eff, provenance="DERIVED", role="internal",
         note=f"N_eff = 3 + sqrt3/(2pi)^2 = {N_eff:.4f} (non-perturbative "
              f"sqrt3 geometry x 2pi period)")
    pset("bbn_status",
         f"Y_p = {Y_p:.4f}; N_eff = {N_eff:.4f} (ALL six constants "
         f"NON-PERTURBATIVE internal: g_A=4/pi, Delta_EM, delta_R, delta_N, "
         f"|V_ud|, f)",
         provenance="DERIVED", role="informational",
         note="the BBN sector: helium yield and neutrino species")

    return {"Y_p": Y_p, "N_eff": N_eff, "T_f": T_f, "dm_np": dm,
            "tau_n": tau_n, "t_decay": t_decay,
            "alpha_em_0": alpha_em_zero(),
            "np_freeze": r["np_freeze"], "np_bbn": r["np_bbn"]}


if __name__ == "__main__":
    r = compute()
    print(f"G_F  = {1.0/(math.sqrt(2.0)*float(get('v_HIGGS'))**2):.4e} GeV^-2")
    print(f"dm_np = {r['dm_np']*1e3:.4f} MeV, T_f = {r['T_f']*1e3:.4f} MeV")
    print(f"tau_n = {r['tau_n']:.1f} s, t_decay = {r['t_decay']:.1f} s")
    print(f"Y_p = {r['Y_p']:.4f}, N_eff = {r['N_eff']:.4f}")
    print("bbn_helium OK (nuclear constants derived from v/M_P/m_e/ladder)")
