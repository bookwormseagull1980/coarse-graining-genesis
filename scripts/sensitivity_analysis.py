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
scripts/sensitivity_analysis.py — V4.0: theoretical-uncertainty
sensitivity (the "error budget" of the closure)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The 147 derived parameters have clean central values, but the paper
does not propagate the uncertainty of the inputs.  This script
quantifies the theoretical sensitivity of the main outputs to the
three inputs/conventions that carry uncertainty:

    kL  — the window-capacity fixed point, solved by bisection from
          the F_MG spectral-pole condition V·Π2/(32π²) = 4/27.  Its
          value depends on the kernel form (1-y)², the mass weight
          y(1-y)², and the normalisation threshold 4/27.  A small
          change of these conventions shifts kL.
    τ   — the torsion modulus τ = (N_L-N_R)/(N_f·ΣY²) = 1/50.  The
          content ratio itself is exact, but the window cancellation
          τ = τ_bare × screening = [1/(2πkL⁴)] × [2πkL⁴/(N_fΣY²)]
          depends on the exact form 2πkL⁴; a small deformation of
          that form shifts τ.
    M_P — the single observed anchor (from G_N).  Its PDG/CODATA
          relative uncertainty (~2.2e-5) is the only true experimental
          error; it propagates to every dimensionful quantity and
          leaves every dimensionless quantity unchanged (M_P-rescale
          invariance).

METHOD (elasticity matrix by central finite difference)
-------------------------------------------------------
For each input p ∈ {kL, τ, M_P} and each output O, the script
evaluates the closed form O(p) at p(1±ε) with ε = 1e-3 and reports
the elasticity

    E(O, p) = d ln O / d ln p  ≈  [O(p(1+ε)) - O(p(1-ε))] / (2ε O(p)).

E is dimensionless: an elasticity of -32 means "a 1% shift of kL
moves O by -32%".  The exponentials e^{-4πkL} (v) and e^{-20kL}
(m_e) produce large elasticities, which is the quantitative content
of the statement "the closure has no free parameter": the numbers
are exact, but they are exponentially sensitive to the conventions
that fix kL and τ.

V4 DISCIPLINE
-------------
This script only READS the store and re-evaluates the closed forms
written in the modules; it writes nothing.  The closed forms are
copied from the module docstrings (endpoint_constraint,
geometric_couplings, epsilon_ratio, sector_alpha, lz_ladder,
electron_mass, dark_energy, gamma_M, perturbation_amplitude) and are
self-tested against the store values before any difference is taken.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get  # noqa: E402

ALPHA = 1.0 / (16.0 * math.pi ** 2)


def squash(tau: float) -> tuple:
    """κ, s0·κ, (1-s0·κ), (1-4·s0·κ) — the J=2 squash factors."""
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    sk = s0 * kappa
    return kappa, sk, 1.0 - sk, 1.0 - 4.0 * sk


def outputs(kL: float, tau: float, M_P: float) -> dict:
    """The closed forms of the main outputs, copied from the module
    docstrings (self-tested against the store)."""
    kappa, sk, sq, sq4 = squash(tau)

    # --- emergence scale (endpoint_constraint) ---
    M_G = M_P * math.sqrt(math.pi) / kL

    # --- gauge couplings (geometric_couplings) ---
    alpha_W = 2.0 / kL ** 5
    inv_alpha = 1.0 / alpha_W + 1.0 / 3.0 - tau ** 2 * math.pi / 2.0
    g2 = math.sqrt(4.0 * math.pi / inv_alpha)
    # g1: the J=2 squash mixing kappa acts at k_GUT, then g1 runs down
    # to M_G (one-loop b1 = 41/10), with the U(1)_Y content correction
    # delta_g1 = -tau·r23·(ΣY²·Δ_f·ξ) = -tau·(3/(10√3))·(5/8).
    k_GUT = M_P * math.sqrt(math.pi) * tau / math.sqrt(3.0)
    b1 = 41.0 / 10.0
    b2 = -19.0 / 6.0
    ln_GUT_MG = math.log(k_GUT / (M_P * math.sqrt(math.pi) / kL))
    inv_g2_GUT2 = 1.0 / g2 ** 2 + (-b2 / (8.0 * math.pi ** 2)) * ln_GUT_MG
    g2_GUT = 1.0 / math.sqrt(inv_g2_GUT2)
    r23 = 3.0 / (10.0 * math.sqrt(3.0))
    delta_g1 = -tau * r23 * ((10.0 / 3.0) * (3.0 / 2.0) * (1.0 / 8.0))
    g1_GUT = g2_GUT * kappa * (1.0 + delta_g1)
    inv_g1_MG2 = 1.0 / g1_GUT ** 2 + (b1 / (8.0 * math.pi ** 2)) * ln_GUT_MG
    g1 = 1.0 / math.sqrt(inv_g1_MG2)

    # --- fermion ladder (sector_alpha + lz_ladder) ---
    ns_tilt = 7.0 * tau / 4.0            # 1 - n_s = τ·(7/4)
    kL_cmb = kL * (1.0 - tau / 4.0)      # perturbation_amplitude
    a_up = kL - 2.0 * tau
    Delta = 6.0 * ns_tilt * kL_cmb
    a_dn = a_up - (18.0 / 17.0) * Delta
    a_lp = a_up - 2.0 * Delta
    mt_mc = math.exp(2.0 * a_up)
    mb_ms = math.exp(2.0 * a_dn)
    mtau_mmu = math.exp(2.0 * a_lp)

    # --- electroweak scale and fermion masses ---
    eps = (3.0 * ALPHA / math.pi) * math.exp(-4.0 * math.pi * kL) * sq
    v = M_G * eps
    mt = v / math.sqrt(2.0)
    me = M_P * math.exp(-20.0 * kL) * sq

    # --- neutrino masses and cosmology (dark_energy + gamma_M) ---
    m3 = v * v * (2.0 * math.pi) ** 2 / k_GUT * (1.0 + sk)
    r12 = 3.0 / 10.0
    r23 = 3.0 / (10.0 * math.sqrt(3.0))
    m1 = m3 * r12 * r23
    rho = (2.0 / 3.0) * m1 ** 4 * sq4
    ent = math.log(M_P * M_P * math.sqrt(2.0 * math.pi + r23)
                   / math.sqrt(rho))
    H0 = M_P * math.sqrt(math.pi) * math.exp(-ent)
    Omega_L = rho / (3.0 * H0 * H0 * M_P * M_P)

    return {
        "M_G": M_G, "g2": g2, "g1": g1,
        "alpha_up": a_up, "alpha_dn": a_dn, "alpha_lp": a_lp,
        "mt_mc": mt_mc, "mb_ms": mb_ms, "mtau_mmu": mtau_mmu,
        "v": v, "mt": mt, "me": me,
        "m_nu3": m3, "m_nu1": m1, "rho_Lambda": rho,
        "H0": H0, "Omega_Lambda": Omega_L,
    }


def self_test(O: dict) -> None:
    """Check the closed forms against the store (baseline)."""
    ref = {
        "M_G": get("M_G"), "g2": get("g2_MG"), "g1": get("g1_MG_geo"),
        "alpha_up": get("alpha_up"), "alpha_dn": get("alpha_down"),
        "alpha_lp": get("alpha_lepton"),
        "mt_mc": get("m_t_over_m_c"), "mb_ms": get("m_b_over_m_s"),
        "v": get("v_HIGGS"), "me": get("m_e_pred") * 1e-3,   # MeV -> GeV
        "m_nu3": get("m_nu3") * 1e-9,   # eV -> GeV
        "rho_Lambda": get("rho_Lambda"),
        "H0": get("H0_GEV"), "Omega_Lambda": get("Omega_Lambda"),
    }
    print("SELF-TEST (closed form vs store):")
    ok = True
    for k, r in ref.items():
        if k in O:
            rel = (O[k] / r - 1.0) if r else float("nan")
            flag = "OK" if abs(rel) < 1e-6 else "MISMATCH"
            if abs(rel) >= 1e-6:
                ok = False
            print(f"  {k:16s} form={O[k]:.8g} store={r:.8g} rel={rel:+.2e} {flag}")
    if not ok:
        raise SystemExit("self-test failed — closed forms differ from the store")
    print("  (all closed forms reproduce the store to <1e-6)\n")


def elasticity(O: dict, kL: float, tau: float, M_P: float, eps: float = 1e-3):
    """Central-difference elasticity matrix for kL, τ, M_P."""
    base = outputs(kL, tau, M_P)
    inputs = {
        "kL": lambda f: (kL * (1.0 + f), tau, M_P),
        "tau": lambda f: (kL, tau * (1.0 + f), M_P),
        "M_P": lambda f: (kL, tau, M_P * (1.0 + f)),
    }
    E = {}
    for pname, mutate in inputs.items():
        lo = outputs(*mutate(-eps))
        hi = outputs(*mutate(+eps))
        E[pname] = {
            k: (hi[k] - lo[k]) / (2.0 * eps * base[k]) for k in base
        }
    return base, E


def main() -> int:
    kL = get("kL")
    tau = get("tau")
    M_P = get("M_P")
    base, E = elasticity(outputs(kL, tau, M_P), kL, tau, M_P)

    self_test(outputs(kL, tau, M_P))

    order = ["M_G", "g2", "g1", "alpha_up", "alpha_dn", "alpha_lp",
             "mt_mc", "mb_ms", "mtau_mmu", "v", "mt", "me",
             "m_nu3", "m_nu1", "rho_Lambda", "H0", "Omega_Lambda"]
    hdr = f"  {'quantity':14s} {'value':>12s} | {'dln/dln kL':>12s} {'dln/dln tau':>13s} {'dln/dln M_P':>12s}"
    print("=" * len(hdr))
    print("  ELASTICITY MATRIX  (a 1% input shift moves the output by E %)")
    print("=" * len(hdr))
    print(hdr)
    print("-" * len(hdr))
    for k in order:
        if k not in base:
            continue
        print(f"  {k:14s} {base[k]:12.5g} | "
              f"{E['kL'][k]:+12.2f} {E['tau'][k]:+13.2f} {E['M_P'][k]:+12.2f}")
    print("=" * len(hdr))

    print("\n  NOTES")
    print("  - E[kL] large and negative for v (e^-4pi kL) and me (e^-20kL):")
    print("    the hierarchy is exponentially sensitive to the window fixed point.")
    print("  - E[M_P] = 1 for dimensionful quantities, 0 for dimensionless ones")
    print("    (M_P-rescale invariance).  G_N's ~2.2e-5 error is negligible vs the")
    print("    kL/tau convention sensitivity — the theory is exact but convention-fragile.")
    print("  - The 4/27 threshold and the (1-y)^2 kernel that fix kL are the true")
    print("    upstream conventions; their elasticity into kL is computed by")
    print("    threshold_sensitivity() below.")
    return 0


def threshold_sensitivity() -> None:
    """How a shift of the normalisation threshold 4/27 moves kL, and how
    that propagates (the deepest convention layer).

    The F_MG condition is V·Π2/(32π²) = CRIT with CRIT = 4/27, the
    maximum of the mass-weighted TT kernel y(1-y)².  We measure
    d ln kL / d ln CRIT by re-solving the fixed point with a shifted
    threshold (calling the endpoint_constraint solver with CRIT(1+δ)).
    """
    from cg_frg.frg import endpoint_constraint as ec
    M_P = get("M_P")
    tau = get("tau")
    L_Cg = get("L_Cg")

    def solve(CRIT):
        saved = ec.CRIT
        ec.CRIT = CRIT
        try:
            chain = ec.self_consistent_chain(M_P, L_Cg, tau)
        finally:
            ec.CRIT = saved
        return chain["kL"]

    kL0 = get("kL")
    eps = 1e-3
    kL_lo = solve(ec.CRIT * (1.0 - eps))
    kL_hi = solve(ec.CRIT * (1.0 + eps))
    dkL = (kL_hi - kL_lo) / (2.0 * eps * kL0)

    print("\n  THRESHOLD SENSITIVITY  (the deepest convention layer)")
    print("  ------------------------------------------------------")
    print(f"  d ln kL / d ln(4/27)  = {dkL:+.3f}")
    print(f"  -> a 1% shift of the 4/27 threshold moves kL by {dkL:+.2f}%,")
    print(f"     and v by {dkL * -32.3:+.1f}%, m_e by {dkL * -49.9:+.1f}%")
    print("     (the elasticities of v and m_e from the matrix above).")


if __name__ == "__main__":
    if "--threshold" in sys.argv:
        threshold_sensitivity()
    else:
        sys.exit(main())
