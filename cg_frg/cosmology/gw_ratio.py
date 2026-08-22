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
cg_frg/cosmology/gw_ratio.py — V4.0: the GW ratio, the 2π-window
IR anchors (2L, σ_C) and the Hubble-scale closure
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The IR end of the framework's window is anchored by the same 2π
family that closes the UV: the tensor-to-scalar ratio, the
entropy-minimum window width, and the Hubble endpoint.  This
module publishes the three IR anchors together:

  GW — the primordial tensor-to-scalar ratio (the Euclidean
       zero-point squared):

        r = (1/2π)² = 0.02533
        Δ²_t = r·Δ²_s = 0.02533 × 2.100e-9 = 5.32e-11

       (the same (1/2π)² Euclidean factor as the scalar zero-point
       Δ²_0 = (1/2)(1/2π)² of perturbation_amplitude; the tensor
       amplitude follows from the scalar one.  TESTABLE: CMB-S4
       should detect r ≈ 0.025 or tighten the bound below it.)

  2L — the Gaussian entropy minimum distance:

        2L = √(2π) = 2.5066

       (the window width that resolves exactly one spectral mode
       per entropy unit — C_window = 2L/√(2π) = 1, the foundation
       of the window-capacity counting; the discriminator:
       kL = 2.4935343 vs 2L — 0.52%, the same family).

  H0/σ_C — the Hubble endpoint and the IR window anchor:

        H0   = M_P·√π·e^{−∫γ_M} = 1.4393e-42 GeV
             = kL·M_G·e^{−∫γ_M} (the two forms agree 0.036% —
             the anchor-chain cross-check kL·M_G = M_P·√π)
        σ_C  = 1/H0 = 6.948e41 GeV⁻¹   (the IR window endpoint)

       (∫γ_M = 139.253 — the entropy integral, gamma_M/ir_flow:
       the emergence window's total entropy accumulation from M_G
       to H0.)

DERIVATION CHAIN
----------------
1. r = (1/2π)²: the tensor sector's zero-point is the Euclidean
   factor (1/2π)² — the same structure as the scalar's Δ²_0
   (perturbation_amplitude); the ratio is structural (2π, the Euclidean
   period).

2. 2L = √(2π): for the Gaussian window W(pσ) = exp(−p²σ²/2),
   the entropy-minimum separation of two distinguishable modes is
   Δ(kL) = √2 in the dimensionless coordinate; the spectral modes
   are quantised in units of 1/L, so the window width satisfies
   2L·k = √(2π) — the Gaussian normalisation ∫exp(−x²/2)dx.

3. H0 = M_P·√π·e^{−∫γ_M}: the IR end of the emergence window —
   the Planck anchor M_P × the Gaussian-width endpoint √π (L_Cg)
   × the entropy suppression e^{−∫γ_M}.  The identity
   kL·M_G = M_P·√π (0.036%) is the anchor chain's cross-check.

PARAMETERS
----------
Reads : M_P, M_G, kL, entropy_integral, perturbation_amplitude
Writes: gw_ratio, gw_tensor_amplitude, twoL_entropy_min_distance,
        H0_GEV, sigma_C_hubble, gw_status (DERIVED — this module
        is their writer)

V4 DISCIPLINE
-------------
Every quantity is computed from internal anchors (M_P, M_G, kL,
∫γ_M) and the structural 2π.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

# Physical constants (full precision, unit conversions only — never
# observed inputs):
C_MS = 2.99792458e8        # the speed of light (exact, m/s)
GEV_TO_S = 1.519267447e24  # GeV -> s^-1 (hbar = 6.582119569e-25 GeV·s)


def gw_ratio() -> float:
    """r = (1/2π)² — the tensor-to-scalar ratio (the Euclidean
    zero-point of the tensor sector)."""
    return 1.0 / (2.0 * math.pi) ** 2


def two_L() -> float:
    """2L = √(2π) — the Gaussian entropy minimum distance."""
    return math.sqrt(2.0 * math.pi)


def hubble(M_P: float, L_Cg: float, entropy_int: float) -> float:
    """H0 = M_P·√π·e^{−∫γ_M} — the Hubble endpoint of the window.

    The Planck anchor × the Gaussian-width endpoint √π (L_Cg) ×
    the entropy suppression of the emergence window.
    """
    return M_P * L_Cg * math.exp(-entropy_int)


def compute() -> dict:
    """Publish the GW ratio and the 2π-window IR anchors."""
    M_P = float(get("M_P"))
    M_G = float(get("M_G"))
    kL = float(get("kL"))
    L_Cg = float(get("L_Cg"))               # √π (the Gaussian endpoint)
    ent = float(get("entropy_integral"))    # ∫γ_M = 139.253 (ir_flow)
    d2_s = float(get("perturbation_amplitude"))  # 2.100e-9 (A-level)

    r = gw_ratio()
    d2_t = r * d2_s
    two_l = two_L()
    H0 = hubble(M_P, L_Cg, ent)
    H0_alt = kL * M_G * math.exp(-ent)      # the cross-check form
    sigma_C = 1.0 / H0
    cross = (H0 / H0_alt - 1.0) * 100.0
    discr = (kL / two_l - 1.0) * 100.0      # kL vs 2L discriminator

    pset("gw_ratio", r, provenance="DERIVED", role="cg",
         note=f"r = (1/2pi)^2 = {r:.5f} (the Euclidean zero-point of "
              f"the tensor sector; the CMB-S4 testable prediction)")
    pset("gw_tensor_amplitude", d2_t, provenance="DERIVED", role="internal",
         note=f"Delta2_t = r*Delta2_s = {d2_t:.3e} (r = (1/2pi)^2 x the "
              f"scalar amplitude {d2_s:.3e})")
    pset("twoL_entropy_min_distance", two_l, provenance="DERIVED", role="cg",
         note=f"2L = sqrt(2pi) = {two_l:.6f} — the Gaussian entropy "
              f"minimum distance (the window capacity 2L/sqrt(2pi) = 1; "
              f"kL vs 2L: {discr:+.3f}% — the same family)")
    pset("H0_GEV", H0, provenance="DERIVED", role="internal",
         note=f"H0 = M_P*sqrt(pi)*e^(-int gamma_M) = {H0:.4e} GeV (the IR "
              f"endpoint of the emergence window; cross-check "
              f"kL*M_G = M_P*sqrt(pi): {cross:+.3f}%)")
    pset("sigma_C_hubble", sigma_C, provenance="DERIVED", role="internal",
         note=f"sigma_C = 1/H0 = {sigma_C:.4e} GeV^-1 — the IR window "
              f"endpoint (the Hubble scale)")
    # The IR acceleration scale a0: the Euclidean-period acceleration
    # c·H0/(2π) with the 3-ball coefficient √(4/3).  This is a DERIVED
    # SCALE from the IR endpoint H0, reproducing the Milgrom coincidence
    # a0 ≈ c·H0/(2π) to +0.36%.  NOTE (2026-08-22 audit): the TT
    # propagator is massless 1/k² at ALL scales (slope_G = -2 exactly),
    # so gravity is NEWTONIAN and a0 carries NO dynamics (F(a/a0) = 1).
    H0_s = H0 * GEV_TO_S                    # GeV -> s^-1
    a0 = C_MS * H0_s / (2.0 * math.pi)
    a0_eff = a0 * math.sqrt(4.0 / 3.0)      # 2/sqrt(3) = sqrt(4/3)
    pset("a0_MOND", a0_eff, provenance="DERIVED", role="internal",
         note=f"a0 = c H0/(2 pi) sqrt(4/3) = {a0_eff:.4e} m/s^2 (a "
              f"DERIVED SCALE from the IR endpoint H0, reproducing the "
              f"Milgrom coincidence a0 ~ c H0/(2 pi); the TT propagator "
              f"is massless 1/k^2 at all scales (Newtonian), so a0 "
              f"carries NO dynamics: F(a/a0) = 1, no flat rotation curves)")
    # The DM sector: Omega_DM = 1 - Omega_Lambda - Omega_b is the
    # flatness-closure remainder (a NUMBER).  AUDIT (2026-08-22): the
    # framework's gravity is the TT spectral POLE (n_grav = 0), whose
    # propagator G_TT = kL^2/(17.05 k^2) is EXACTLY massless 1/k^2 at
    # all scales (p^2, m^2, R_k all ∝ k^2 on L = kL/k), i.e. NEWTONIAN
    # 1/r at all scales.  Hence F(a/a0) = 1: the framework does NOT
    # produce flat rotation curves, and a0 is a derived NUMBER (Milgrom
    # coincidence) with no dynamics.  The "transparent gravity / no dark
    # matter" reading is NOT supported by the spectral structure and is
    # retracted here; Omega_DM is left as the standard Newtonian
    # dark-matter discrepancy.
    # Ω_b = η_B·n_γ·m_p/ρ_crit — η_B (Sakharov), m_p (constituent quark),
    # ρ_crit (H0, M_P) and T_CMB (the photon floor) are all INTERNAL.
    eta_B = float(get("eta_b"))
    m_p = float(get("m_p"))
    T_GeV = float(get("T_CMB_GeV"))             # the DERIVED CMB temperature
    n_gamma = 2.0 * 1.2020569031595942 * T_GeV ** 3 / math.pi ** 2   # GeV^3
    rho_crit = 3.0 * H0 * H0 * M_P * M_P
    rho_b = eta_B * n_gamma * m_p
    Omega_b = rho_b / rho_crit
    pset("Omega_b", Omega_b, provenance="DERIVED", role="internal",
         note=f"Omega_b = eta_B n_gamma m_p / rho_crit = {Omega_b:.5f} "
              f"(eta_B = {eta_B:.2e} (Sakharov J alpha_W^2/56), m_p = "
              f"{m_p:.4f} (constituent quark 279/64 Lambda_QCD), rho_crit "
              f"from the DERIVED H0; T_CMB DERIVED from the neutrino floor)")
    # The Omega_Lambda from the store (the dark_energy closure) and
    # the Omega_DM from the closure relation.
    Omega_lam = float(get("Omega_Lambda"))
    Omega_DM = 1.0 - Omega_lam - Omega_b
    pset("Omega_DM", Omega_DM, provenance="DERIVED", role="internal",
         note=f"Omega_DM = 1 - Omega_Lambda - Omega_b = {Omega_DM:.4f} "
              f"(the flatness closure remainder; a NUMBER, not a "
              f"particle species — but the framework's gravity is "
              f"Newtonian 1/r at all scales, so this remainder is left "
              f"UNEXPLAINED by the framework (the standard dark-matter "
              f"discrepancy)")
    pset("dm_verdict",
         {"rotation_scale": "derived SCALE only: a0 = c H0/(2 pi) "
                            "sqrt(4/3) reproduces the Milgrom coincidence "
                            "a0 ~ c H0/(2 pi) (+0.36%); NOT a dynamics",
          "rotation_shape": "F(a/a0) = 1 (NEWTONIAN): the TT propagator "
                            "is massless 1/k^2 at all scales (slope_G = "
                            "-2.0000000000, slope_Z = 0.0000000000), so "
                            "gravity is Newtonian 1/r at all scales — no "
                            "flat rotation curves",
          "Omega_DM": Omega_DM,
          "bullet": "not established (Newtonian gravity gives standard "
                    "lensing; no spectral zero-mode lensing)"},
         provenance="DERIVED", role="informational",
         note="AUDIT 2026-08-22: the framework's gravity is the TT "
              "spectral POLE (n_grav = 0), massless 1/k^2 at all scales "
              "(Newtonian).  a0 is a DERIVED scale (Milgrom coincidence) "
              "with NO dynamics.  The 'transparent gravity / no dark "
              "matter' reading is RETRACTED: Omega_DM is the flatness-"
              "closure remainder, left UNEXPLAINED by Newtonian gravity.")

    return {"r": r, "Delta2_t": d2_t, "two_L": two_l, "H0": H0,
            "H0_alt": H0_alt, "sigma_C": sigma_C,
            "cross_pct": cross,
            "kL_vs_2L_pct": discr}


if __name__ == "__main__":
    r = compute()
    print(f"r        = {r['r']:.5f}")
    print(f"Delta2_t = {r['Delta2_t']:.3e}")
    print(f"2L       = {r['two_L']:.6f}  (kL vs 2L: {r['kL_vs_2L_pct']:+.3f}%)")
    print(f"H0       = {r['H0']:.4e} GeV (cross-check {r['cross_pct']:+.3f}%)")
    print(f"sigma_C  = {r['sigma_C']:.4e} GeV^-1")
    print("gw_ratio OK")
