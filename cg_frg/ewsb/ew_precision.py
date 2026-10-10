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
cg_frg/ewsb/ew_precision.py —V5.0: the electroweak precision
observables (the M_G -> M_Z interface block)
=================================================================

PURPOSE
-----------------------------------
The interface between the framework and the Standard Model is a
boundary-condition problem, not an embedding: the spectral sums
fix the UV boundary conditions at the emergence scale M_G, the
geometric two-loop RGE flows the gauge couplings down to the
electroweak scale, and the low-energy observables are then the
standard derived quantities of the electroweak sector.  This
module publishes that third stage as a single output block:

  M_Z       —the internal Z mass: the self-consistent fixed point
              of the tree-level mass formula
                  M_Z = (v/2) sqrt(g2^2 + (3/5) g1^2)
              evaluated at mu = M_Z with the geometric two-loop
              RGE (beta_gauge, geometric Yukawa y_0 = 1).  No
              external scale enters: the couplings are the
              framework's geometric values at M_G run down by the
              framework's own beta content.
  M_W       —the on-shell Sirlin relation
                  s^2 c^2 = pi alpha(0) / (sqrt(2) G_F M_Z^2)
                            * 1 / (1 - Delta r) ,
                  Delta r = Delta alpha - (c^2/s^2) Delta rho ,
              with Delta alpha = 1 - alpha(0)/alpha(M_Z) from the
              framework's own alpha(0) (alpha_em_0_pred) and
              alpha(M_Z) (alpha_inv_MZ_pred), G_F = 1/(sqrt(2) v^2)
              from the closed VEV, and Delta rho the exact one-loop
              t-b doublet contribution (Veltman).
  mixing     —the MS-bar-like weak mixing angle
                  s^2(M_Z) = g'^2 / (g2^2 + g'^2),  g' = sqrt(3/5) g1,
              from the geometric couplings at the internal M_Z, and
              the on-shell angle s^2 = 1 - M_W^2/M_Z^2.
  rho        —the rho parameter rho = 1/(1 - Delta rho).
  Gamma_Z    —the partial and total Z widths: Born-level widths
              with the QCD radiator
                  alpha_s/pi + 1.409 (alpha_s/pi)^2        (quarks)
              and the QED radiator 3 Q_f^2 alpha(M_Z)/(4 pi)
              (charged fermions).
  sigma_had  —the hadronic peak cross-section 12 pi Gamma_e
              Gamma_had / (M_Z^2 Gamma_Z^2).
  m_H        —the tree-level Higgs mass sqrt(2 lambda_H) v with the
              framework's scale-invariant Higgs quartic lambda_H (the
              colour-singlet order parameter lambda is distinct).

LEVEL OF THE COMPUTATION
------------------------------------------
  * M_Z:      tree-level mass formula with two-loop running
              couplings (the running carries the dominant radiative
              content; the genuine one-loop self-energies at the Z
              pole are not included).
  * M_W:      Born + the running electromagnetic coupling and
              the one-loop rho-parameter correction. The retained
              Delta r contains these two contributions. A separate
              comparison diagnostic evaluates the same finite-order
              expression with the registered Standard-Model inputs.
  * Gamma_Z:  Born + massless non-singlet QCD/QED radiators. This
              baseline uses the running gauge-coupling angle. The
              companion neutral-current calculation publishes the
              common improved-Born angle and normalization, together
              with the leading non-universal bottom interference,
              as one consistent set of partial widths and ratios.
              Finite fermion masses require mass-scheme matching.
  * m_H:      tree-level (no radiative shift of the quartic).

IMPLEMENTATION
-------------
Production inputs are DERIVED framework values from cg_params.json.
The observed values are read from the SM comparison store
(reference_inputs.json) for the comparison tables and the separate
finite-order formula diagnostic.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset, sm_value, compare_and_set  # noqa: E402
from cg_core.gauge_running import run_geometric  # noqa: E402
from cg_core.electroweak import neutral_current_widths, veltman_delta_rho  # noqa: E402

# 1 GeV^-2 = 0.389379 mb = 3.89379e5 nb (the standard cross-section
# conversion; 1 mb = 1e-27 cm^2).
GEV2_TO_NB = 3.89379e5


def run_to(g1_MG: float, g2_MG: float, g3_MG: float, M_G: float,
           mu: float, steps_per_decade: int = 8) -> tuple:
    """Integrate the geometric two-loop RGE from M_G to mu.

    Checked RK4 with step doubling and geometric Yukawa y_0 = 1.
    The density argument specifies the initial steps per e-fold.
    Returns (g1, g2, g3) at mu.
    """
    return run_geometric((g1_MG, g2_MG, g3_MG), M_G, mu,
                         steps_per_efold=steps_per_decade)


def mz_formula(v: float, g1: float, g2: float) -> float:
    """M_Z = (v/2) sqrt(g2^2 + (3/5) g1^2) —the tree-level Z-mass
    formula with the GUT-normalised g1 (g' = sqrt(3/5) g1)."""
    return 0.5 * v * math.sqrt(g2 * g2 + 0.6 * g1 * g1)


def mz_fixed_point(v: float, g1_MG: float, g2_MG: float, g3_MG: float,
                   M_G: float, *, max_iterations: int = 40) -> tuple:
    """The self-consistent internal Z mass.

    Solve mu = (v/2) sqrt(g2(mu)^2 + (3/5) g1(mu)^2) with the
    geometric two-loop RGE by fixed-point iteration.  The map
    F(mu) = M_Z(g(mu)) is a contraction near the fixed point
    (|F'| ~ 0.005), so the iteration converges to machine
    precision in a handful of steps.  Returns (M_Z, g1, g2, g3) at
    the fixed point.
    """
    if not math.isfinite(v) or v <= 0:
        raise ValueError("v must be finite and positive")
    g1v, g2v, _ = run_to(g1_MG, g2_MG, g3_MG, M_G, v)
    mu = mz_formula(v, g1v, g2v)             # the first estimate
    for _ in range(max_iterations):
        g1, g2, g3 = run_to(g1_MG, g2_MG, g3_MG, M_G, mu)
        mu_new = mz_formula(v, g1, g2)
        if abs(mu_new - mu) / mu < 1e-12:
            mu = mu_new
            break
        mu = mu_new
    else:
        raise RuntimeError("self-consistent M_Z iteration did not converge")
    g1, g2, g3 = run_to(g1_MG, g2_MG, g3_MG, M_G, mu)
    if abs(mz_formula(v, g1, g2) / mu - 1.0) > 2e-12:
        raise RuntimeError("self-consistent M_Z failed its forward residual")
    return mu, g1, g2, g3


def delta_rho(G_F: float, mt: float, mb: float) -> float:
    """The exact one-loop t-b doublet contribution to the rho
    parameter (Veltman):

        Delta rho = (3 G_F/(8 pi^2 sqrt(2)))
                    [ mt^2 + mb^2 - 2 mt^2 mb^2/(mt^2 - mb^2)
                      ln(mt^2/mb^2) ].

    In the limit mb -> 0 this reduces to 3 G_F mt^2/(8 pi^2 sqrt(2)).
    """
    return veltman_delta_rho(G_F, mt, mb)


def solve_MW(M_Z: float, alpha0: float, alpha_MZ: float, G_F: float,
             d_rho: float, iters: int = 20) -> tuple:
    """Solve the on-shell relation for M_W.

        s^2 c^2 = pi alpha(0) / (sqrt(2) G_F M_Z^2) * 1/(1 - Delta r),
        Delta r = Delta alpha - (c^2/s^2) Delta rho,

    with Delta alpha = 1 - alpha(0)/alpha(M_Z).  The remaining
    one-loop Delta r_rem is omitted (documented). With x=s^2 this
    reduces exactly to (1-x)[x*(1-Delta alpha-Delta rho)+Delta rho]=A.
    The physical x<1/2 branch is solved algebraically and checked in
    the original equation. ``iters`` is retained for call compatibility.
    Returns (s^2, M_W); invalid/no-real-root inputs raise ValueError.
    """
    if not all(math.isfinite(x) and x > 0 for x in (M_Z, alpha0, alpha_MZ, G_F)):
        raise ValueError("M_Z, alpha0, alpha_MZ and G_F must be positive")
    if not math.isfinite(d_rho):
        raise ValueError("Delta rho must be finite")
    d_alpha = 1.0 - alpha0 / alpha_MZ
    A = math.pi * alpha0 / (math.sqrt(2.0) * G_F * M_Z * M_Z)
    B = 1.0 - d_alpha - d_rho
    linear = B - d_rho
    disc = linear * linear - 4.0 * B * (A - d_rho)
    if B <= 0 or disc < 0:
        raise ValueError("M_W relation has no admissible real weak-branch root")
    denominator = linear + math.sqrt(disc)
    if denominator <= 0:
        raise ValueError("M_W relation has no admissible weak-branch root")
    s2 = 2.0 * (A - d_rho) / denominator
    if not 0 < s2 <= 0.5:
        raise ValueError("M_W root lies outside 0 < sin²(theta_W) <= 1/2")
    d_r = d_alpha - (1.0 - s2) / s2 * d_rho
    if 1.0 - d_r <= 0:
        raise ValueError("M_W root has nonpositive Sirlin denominator")
    rhs = A / (1.0 - d_r)
    if abs(s2 * (1.0 - s2) - rhs) > 2e-12 * max(abs(rhs), 1e-15):
        raise RuntimeError("M_W root failed the original equation residual")
    return s2, M_Z * math.sqrt(1.0 - s2)


def z_widths(M_Z: float, s2_eff: float, G_F: float, alpha_MZ: float,
             alpha_s_MZ: float) -> dict:
    """Born partial widths with massless QCD/QED radiators, in GeV.

    The shared amplitude uses rho_NC=1 and no non-universal top term
    for this baseline. Effective neutral-current production uses the
    same function with its common rho_NC, angle and bottom interference.
    """
    return neutral_current_widths(M_Z, s2_eff, G_F, alpha_MZ, alpha_s_MZ)


def sigma_had_nb(M_Z: float, G_e: float, G_had: float, G_Z: float) -> float:
    """The hadronic peak cross-section (nb):

        sigma_had^0 = 12 pi Gamma_e Gamma_had / (M_Z^2 Gamma_Z^2).
    """
    return (12.0 * math.pi * G_e * G_had / (M_Z * M_Z * G_Z * G_Z)
            * GEV2_TO_NB)


def compute() -> dict:
    """Publish the electroweak precision observables."""
    v = float(get("v_HIGGS"))                   # the closed VEV (vev_closure)
    g1_MG = float(get("g1_MG_geo"))             # geometric g1 at M_G
    g2_MG = float(get("g2_MG"))                 # the full g2 prediction at M_G
    g3_MG = float(get("g3_MG_geo"))             # geometric g3 at M_G
    M_G = float(get("M_G"))
    alpha0 = float(get("alpha_em_0_pred"))      # alpha(0) = 1/137.049
    alpha_inv_MZ = float(get("alpha_inv_MZ_pred"))   # 128.2085 (two-loop)
    alpha_MZ = 1.0 / alpha_inv_MZ
    alpha_s_MZ = float(get("alpha_s_MZ_pred"))  # 0.117986
    mt = float(get("m_t_pred"))                 # 174.08 GeV
    mb = float(get("m_b_pred"))                 # 4.238 GeV
    lam_h = float(get("lambda_H_pseudo"))       # the scale-invariant quartic
    m_e = float(get("m_e_pred"))                # MeV
    mmu_me = float(get("m_mu_over_m_e"))
    al = float(get("alpha_lepton"))             # the lepton ladder index

    G_F = 1.0 / (math.sqrt(2.0) * v * v)        # 1/(sqrt(2) v^2)

    # ---- the internal M_Z (self-consistent fixed point) ----
    M_Z, g1_MZ, g2_MZ, g3_MZ = mz_fixed_point(v, g1_MG, g2_MG, g3_MG, M_G)

    # The MS-bar-like mixing and alpha(M_Z) at the internal M_Z
    # (the self-consistent values; cross-checked against the stored
    # alpha_inv_MZ_pred which was evaluated at the one-loop estimate
    # of the same fixed point).
    gp_MZ = math.sqrt(3.0 / 5.0) * g1_MZ
    s2_msbar = gp_MZ * gp_MZ / (g2_MZ * g2_MZ + gp_MZ * gp_MZ)
    alpha_inv_self = 4.0 * math.pi * (1.0 / g2_MZ ** 2
                                      + 5.0 / (3.0 * g1_MZ ** 2))
    cross = (alpha_inv_self / alpha_inv_MZ - 1.0) * 100.0

    # ---- M_W (on-shell, Delta rho one-loop) ----
    d_rho = delta_rho(G_F, mt, mb)
    s2_os, M_W = solve_MW(M_Z, alpha0, alpha_MZ, G_F, d_rho)
    rho = 1.0 / (1.0 - d_rho)

    # ---- Z widths ----
    w = z_widths(M_Z, s2_msbar, G_F, alpha_MZ, alpha_s_MZ)
    sig_had = sigma_had_nb(M_Z, w["e"], w["had"], w["Z"])
    R_l = w["had"] / w["e"]      # R_l = Gamma_had/Gamma_e (single species)
    R_b = w["b"] / w["had"]

    # ---- the Higgs mass (tree level) ----
    m_H = math.sqrt(2.0 * lam_h) * v

    # ---- the mu and tau masses (absolute, from the internal ladder) ----
    m_mu = m_e * 1e-3 * mmu_me                 # MeV -> GeV
    m_tau = m_mu * math.exp(2.0 * al)

    # ---- publish (DERIVED; observed values only as comparison) ----
    # These sets identify stored value inputs, following the actual formulas.
    # For example, the Higgs mass does not depend on the colour-condensate
    # quartic mentioned in its explanatory note, and lepton widths do not
    # depend on the separately supplied strong radiator.
    gauge_inputs = ("v_HIGGS", "g1_MG_geo", "g2_MG", "g3_MG_geo", "M_G")
    onshell_inputs = gauge_inputs + ("alpha_em_0_pred", "alpha_inv_MZ_pred",
                                    "m_t_pred", "m_b_pred")
    lepton_inputs = gauge_inputs + ("alpha_inv_MZ_pred",)
    hadron_inputs = lepton_inputs + ("alpha_s_MZ_pred",)
    pset("M_Z_pred", M_Z, provenance="DERIVED", role="internal",
         dependencies=gauge_inputs,
         note=f"M_Z = (v/2) sqrt(g2^2 + (3/5) g1^2) at the "
              f"self-consistent fixed point mu = M_Z with the geometric "
              f"two-loop RGE = {M_Z:.4f} GeV (no external scale; the "
              f"tree-level mass formula evaluated on the two-loop-run "
              f"geometric couplings)")
    pset("s2_thetaW_MZ", s2_msbar, provenance="DERIVED", role="internal",
         dependencies=gauge_inputs,
         note=f"s^2(M_Z) = g'^2/(g2^2+g'^2) at the internal M_Z = "
              f"{s2_msbar:.6f} (the MS-bar-like mixing from the geometric "
              f"couplings at the Z pole)")
    compare_and_set("M_W_pred", M_W, sm_value("m_W_obs"),
                    dependencies=onshell_inputs,
                    note=f"M_W = {M_W:.4f} GeV —the on-shell Sirlin relation "
                         f"with Delta r = Delta alpha - (c^2/s^2) Delta rho "
                         f"(the exact one-loop t-b Veltman rho); Delta r_rem "
                         f"omitted (see the module docstring).  Inputs all "
                         f"internal: M_Z = {M_Z:.3f}, alpha(0) = "
                         f"1/{1.0/alpha0:.3f}, alpha(M_Z)^-1 = "
                         f"{alpha_inv_MZ:.3f}, G_F = 1/(sqrt(2) v^2) = "
                         f"{G_F:.8e}")
    pset("s2_thetaW_os", s2_os, provenance="DERIVED", role="internal",
         dependencies=onshell_inputs,
         note=f"sin^2 theta_W (on-shell) = 1 - M_W^2/M_Z^2 = {s2_os:.6f} "
              f"from the internal M_Z = {M_Z:.3f} and M_W = {M_W:.3f}")
    pset("rho_param", rho, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "m_t_pred", "m_b_pred"),
         note=f"rho = 1/(1 - Delta rho) = {rho:.6f} with the exact "
              f"one-loop t-b Delta rho (Veltman) = {d_rho:.6f}; the "
              f"comparison target is the SM improved-Born value "
              f"1/(1 - Delta rho_SM) ~ 1.0094, NOT the PDG-fit "
              f"rho_eff = 1.0004 (the after-subtraction quantity)")
    compare_and_set("Gamma_Z_pred", w["Z"], sm_value("Gamma_Z_obs"),
                    dependencies=hadron_inputs,
                    note=f"Gamma_Z = {w['Z']:.4f} GeV —the sum of the Born "
                         f"partial widths with the QCD radiator alpha_s/pi "
                         f"+ 1.409 (alpha_s/pi)^2 (quarks) and the QED "
                         f"radiator 3 Q^2 alpha/(4 pi) (charged fermions); "
                         f"EW vertex corrections not included; the top is "
                         f"above threshold")
    pset("Gamma_had_pred", w["had"], provenance="DERIVED", role="internal",
         dependencies=hadron_inputs,
         note=f"Gamma_had = {w['had']:.4f} GeV (u,c,d,s,b at Born + "
              f"QCD/QED radiators)")
    pset("Gamma_b_pred", w["b"], provenance="DERIVED", role="internal",
         dependencies=hadron_inputs,
         note=f"Gamma_b = {w['b']:.4f} GeV (Born + QCD/QED radiators; "
              f"the bottom vertex belongs to the effective neutral-current readout)")
    pset("Gamma_l_pred", w["l"], provenance="DERIVED", role="internal",
         dependencies=lepton_inputs,
         note=f"Gamma_l = {w['l']:.4f} GeV (e + mu + tau, Born + QED "
              f"radiator)")
    pset("Gamma_inv_pred", w["nu"], provenance="DERIVED", role="internal",
         dependencies=gauge_inputs,
         note=f"Gamma_inv = {w['nu']:.4f} GeV (three neutrino species, "
              f"Born)")
    pset("sigma_had_pred", sig_had, provenance="DERIVED", role="internal",
         dependencies=hadron_inputs,
         note=f"sigma_had^0 = 12 pi Gamma_e Gamma_had/(M_Z^2 Gamma_Z^2) "
              f"= {sig_had:.3f} nb")
    pset("R_l_pred", R_l, provenance="DERIVED", role="internal",
         dependencies=hadron_inputs,
         note=f"R_l = Gamma_had/Gamma_e = {R_l:.3f} (single-species "
              f"leptonic definition, PDG convention)")
    pset("R_b_pred", R_b, provenance="DERIVED", role="internal",
         dependencies=hadron_inputs,
         note=f"R_b = Gamma_b/Gamma_had = {R_b:.5f}")
    compare_and_set("m_H_pred", m_H, sm_value("m_H_obs"),
                    dependencies=("lambda_H_pseudo", "v_HIGGS"),
                    note=f"m_H = sqrt(2 lambda_H) v = {m_H:.3f} GeV (tree "
                         f"level with the Higgs quartic lambda_H = {lam_h:.6f}, "
                         f"distinct from the colour-singlet order parameter "
                         f"lambda = {get('order_parameter_lambda'):.3f})")
    pset("m_mu_pred", m_mu, provenance="DERIVED", role="internal",
         dependencies=("m_e_pred", "m_mu_over_m_e"),
         note=f"m_mu = m_e (m_mu/m_e) = {m_mu:.6f} GeV (the absolute muon "
              f"mass from the internal ladder)")
    pset("m_tau_pred", m_tau, provenance="DERIVED", role="internal",
         dependencies=("m_e_pred", "m_mu_over_m_e", "alpha_lepton"),
         note=f"m_tau = m_mu e^(2 alpha_lp) = {m_tau:.6f} GeV (the "
              f"absolute tau mass from the internal lepton ladder)")

    return {"M_Z": M_Z, "g1_MZ": g1_MZ, "g2_MZ": g2_MZ,
            "s2_msbar": s2_msbar, "alpha_inv_self": alpha_inv_self,
            "cross_pct": cross, "M_W": M_W, "s2_os": s2_os,
            "rho": rho, "d_rho": d_rho, "Gamma_Z": w["Z"],
            "Gamma_had": w["had"], "Gamma_b": w["b"], "Gamma_l": w["l"],
            "Gamma_inv": w["nu"], "sigma_had_nb": sig_had,
            "R_l": R_l, "R_b": R_b, "m_H": m_H,
            "m_mu": m_mu, "m_tau": m_tau}


def formula_check() -> dict:
    """Evaluate the retained M_W formula with registered comparison inputs.

    The diagnostic uses the same electromagnetic running and top-bottom
    contribution to Delta rho as the production calculation. Its inputs
    and output remain in the isolated comparison calculation.
    """
    M_Z = sm_value("M_Z")
    G_F = sm_value("G_F_obs")
    alpha0 = 1.0 / sm_value("alpha_inv_obs")
    alpha_MZ = 1.0 / sm_value("alpha_inv_MZ_obs")
    mt = sm_value("m_t_obs")
    mb = sm_value("m_b_obs")
    d_rho = delta_rho(G_F, mt, mb)
    s2, M_W = solve_MW(M_Z, alpha0, alpha_MZ, G_F, d_rho)
    return {"M_W": M_W, "s2": s2, "d_rho": d_rho}


def main() -> int:
    r = compute()
    print("=" * 72)
    print("  V5 ELECTROWEAK PRECISION OBSERVABLES (M_G -> M_Z block)")
    print("=" * 72)
    print(f"  internal M_Z (self-consistent two-loop) = {r['M_Z']:.4f} GeV"
          f"   (obs {sm_value('M_Z'):.4f}, "
          f"{(r['M_Z']/sm_value('M_Z')-1)*100:+.3f}%)")
    print(f"  alpha(M_Z)^-1 (self-consistent)          = {r['alpha_inv_self']:.4f}"
          f"   (store {float(get('alpha_inv_MZ_pred')):.4f}, "
          f"cross {r['cross_pct']:+.4f}%)")
    print(f"  s^2(M_Z) (MS-bar-like)                   = {r['s2_msbar']:.6f}"
          f"   (obs {sm_value('sin2thetaW_MSbar_obs'):.5f}, "
          f"{(r['s2_msbar']/sm_value('sin2thetaW_MSbar_obs')-1)*100:+.3f}%)")
    print(f"  M_W (on-shell, Delta rho one-loop)       = {r['M_W']:.4f} GeV"
          f"   (obs {sm_value('m_W_obs'):.3f}, "
          f"{(r['M_W']/sm_value('m_W_obs')-1)*100:+.3f}%)")
    s2_os_obs = 1.0 - (sm_value("m_W_obs") / sm_value("M_Z")) ** 2
    print(f"  s^2_W (on-shell)                         = {r['s2_os']:.6f}"
          f"   (obs {s2_os_obs:.6f}, "
          f"{(r['s2_os']/s2_os_obs-1)*100:+.3f}%)")
    print(f"  rho parameter (improved Born)               = {r['rho']:.6f}"
          f"   (SM 1/(1-Delta rho_SM) = {1.0/(1.0-delta_rho(sm_value('G_F_obs'), sm_value('m_t_obs'), sm_value('m_b_obs'))):.6f}, "
          f"{(r['rho']/(1.0/(1.0-delta_rho(sm_value('G_F_obs'), sm_value('m_t_obs'), sm_value('m_b_obs'))))-1)*100:+.3f}%)")
    print(f"  Gamma_Z                                  = {r['Gamma_Z']:.4f} GeV"
          f"   (obs {sm_value('Gamma_Z_obs'):.4f}, "
          f"{(r['Gamma_Z']/sm_value('Gamma_Z_obs')-1)*100:+.3f}%)")
    print(f"  Gamma_had                                = {r['Gamma_had']:.4f} GeV"
          f"   (obs {sm_value('Gamma_had_obs'):.4f}, "
          f"{(r['Gamma_had']/sm_value('Gamma_had_obs')-1)*100:+.3f}%)")
    print(f"  Gamma_b                                  = {r['Gamma_b']:.4f} GeV"
          f"   (obs {sm_value('Gamma_b_obs'):.4f}, "
          f"{(r['Gamma_b']/sm_value('Gamma_b_obs')-1)*100:+.3f}%)")
    print(f"  Gamma_l (e+mu+tau)                       = {r['Gamma_l']:.4f} GeV"
          f"   (obs {3*sm_value('Gamma_l_obs'):.4f}, "
          f"{(r['Gamma_l']/(3*sm_value('Gamma_l_obs'))-1)*100:+.3f}%)")
    print(f"  Gamma_inv (3 nu)                         = {r['Gamma_inv']:.4f} GeV"
          f"   (obs {sm_value('Gamma_inv_obs'):.4f}, "
          f"{(r['Gamma_inv']/sm_value('Gamma_inv_obs')-1)*100:+.3f}%)")
    print(f"  sigma_had^0                              = {r['sigma_had_nb']:.3f} nb"
          f"   (obs {sm_value('sigma_had_obs'):.3f}, "
          f"{(r['sigma_had_nb']/sm_value('sigma_had_obs')-1)*100:+.3f}%)")
    print(f"  R_l                                      = {r['R_l']:.3f}"
          f"   (obs {sm_value('R_l_obs'):.3f}, "
          f"{(r['R_l']/sm_value('R_l_obs')-1)*100:+.3f}%)")
    print(f"  R_b                                      = {r['R_b']:.5f}"
          f"   (obs {sm_value('R_b_obs'):.5f}, "
          f"{(r['R_b']/sm_value('R_b_obs')-1)*100:+.3f}%)")
    print(f"  m_H (tree, sqrt(2 lambda_H) v)         = {r['m_H']:.3f} GeV"
          f"   (obs {sm_value('m_H_obs'):.2f}, "
          f"{(r['m_H']/sm_value('m_H_obs')-1)*100:+.3f}%)")
    print(f"  m_mu / m_tau (internal ladder)           = {r['m_mu']*1000:.2f}"
          f" MeV / {r['m_tau']:.4f} GeV"
          f"   (obs {1000*sm_value('m_mu_obs'):.2f} MeV / {sm_value('m_tau_obs'):.3f} GeV)")
    fc = formula_check()
    print("-" * 72)
    print(f"  formula check (SM inputs, Delta r_rem omitted): "
          f"M_W = {fc['M_W']:.3f} GeV")
    print("ew_precision OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
