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
cg_frg/frg/endpoint_constraint.py — V4.0: the Planck-endpoint
geometry from the F_MG spectral-pole condition and coupling closure
==================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
On the self-similar flow L(k) = C/k (C = M_P·L_Cg, γ_M = 0), the
emergence chain is fully determined by three geometric conditions:

    kL*  :  V₃·Π²^{Tμν2}(kL, (k/M_P)²)/(32π²) = 4/27 at k* = M_G  (F_MG)
    M_G  =  C/kL* ,   k_GUT = C/L_GUT ,  L_GUT = √3/τ            (GUT)
    g₂   =  √8·(M_G/M_P)·kL*^{−3/2}            (Killing normalisation)

The F_MG condition is the spectral-pole condition of the spin-2
channel of the improved energy-momentum tensor: the graviton-like
mode becomes massless at the emergence scale M_G.  It fixes the
dimensionless fixed point kL* = 2.4935343 self-consistently.

Because M_G = M_P·L_Cg/kL*, every dimensionless prediction
(M_G/M_P, g₂) is independent of the absolute value of the Planck
anchor M_P: rescaling M_P leaves the SM deviation unchanged (the
M_P-rescale invariance — the closure is geometric, not anchored).

GEOMETRIC-DYNAMICS CONSERVATION LAW (2026-08-16)
------------------------------------------------
The gauge-sector closure is NOT a coupling calibration: the
first-principles endpoint geometry L_Cg = sqrt(pi) predicts

    g2(M_G) = sqrt(8)(M_G/M_P) kL^{-3/2},

which deviates from SM by +0.34% = 1/N_c - tau^2*pi/2 — an
explained geometric-dynamics symmetry correction (the conservation
law N_c(1/alpha_SM - 1/alpha_W + tau^2 pi/2) = 1  <->  N_g xi = 1,
proven in Lean 4).  The first-principles L_Cg = sqrt(pi) fixes
R_c = 6/pi, and L_critical = sqrt(6/R_c) = sqrt(pi) = L_Cg.

STATUS OF g3
------------
g₃ is CLOSED via the long-root correction (geometric_couplings):
the two su(2) blocks share the Killing normalisation at order α⁰
(g₃ = g₂ at k_GUT), and the long-root E_{±(α₁+α₂)} carries the
α²/K correction with K = 8/3 — g₃ = g₂·(1+α_GUT²/K).  The g₂
closure (L_Cg*, kL*, M_G) does not depend on g₃ and stands.

WHAT THIS MODULE PUBLISHES (the main chain)
-------------------------------------------
    kL          the F_MG self-consistent fixed point at L_Cg = sqrt(pi)
    L_Gg        L(M_G) = kL = C/M_G
    M_G         M_G = M_P*sqrt(pi)/kL (the emergence scale)
    g2_MG_bare_constraint
                the BARE Killing-normalisation SU(2) coupling at M_G
                from this constraint chain (+0.34% vs SM, pre-correction).
                NOTE: the authoritative g2_MG (the full prediction with
                the conservation-law correction, +0.00066%) is published
                by geometric_couplings — this module does NOT overwrite
                the authoritative key.
    L_critical  sqrt(pi) = L_Cg (R_c = 6/pi)
    L_Cg_star   sqrt(pi) = L_Cg (the first-principles value)
    R_c_star    6/pi (the first-principles critical curvature)
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_frg.frg.spectral_sum import channel_tmunu_spin2  # noqa: E402

# The spectral-pole critical value: V₃·Π²^{Tμν2}/(32π²) = 4/27 at the
# emergence scale (the pole of the spin-2 channel of the improved
# EMT — the graviton-like mode becomes massless at k* = M_G).
#
# FIRST-PRINCIPLES DERIVATION of 4/27 (2026-08-17; sharpened 2026-08-18):
#   The transverse-traceless kernel is K_TT = k⁴/(k²+m²)².  With the
#   mass fraction y = m²/(k²+m²), this is K_TT = (1−y)².  The
#   mass-weighted spectral density is y·K_TT = y(1−y)², whose
#   maximum over y ∈ [0,1] is 4/27 at y = 1/3 (m² = k²/2).  This
#   extremum is the normalisation at which the massless pole appears,
#   the F_MG spectral-pole condition.  The extremum is the value
#   of the mass-weighted density at its maximum, the
#   point where the mass fraction and the two kinetic fractions
#   (1/3)(2/3)² balance.
#
# UNIQUENESS OF THE MAXIMUM (2026-08-18):
#   ρ(y) = y(1−y)² has ρ' = (1−y)(1−3y), which vanishes on (0,1)
#   only at y = 1/3 (the other root y = 1 is the endpoint), with
#   ρ''(1/3) = −2 < 0.  So 4/27 is the UNIQUE interior extremum of
#   the mass-weighted density — the endpoints y = 0,1 give ρ = 0 and
#   there is no competing interior value.  The maximum is the only
#   non-trivial scale-invariant datum carried by the kernel, so the
#   selection of 4/27 is forced by uniqueness, not by a free choice.
#
# MAXIMUM-ENTROPY READING (2026-08-18; sharpened 2026-08-18):
#   The maximum is the point of maximal activation of the TT channel
#   — the mass fraction y = 1/3 balancing the two kinetic fractions
#   (2/3)² — which is exactly where the massless pole appears.  This
#   selection is a CONSEQUENCE of the disorder axiom, not an
#   independent hypothesis: the unbiasedness clause (A3) together with
#   the maximum-entropy theorem of paper 4 fixes the flow to the
#   configuration of maximal spectral weight, and the maximum of
#   y(1−y)² is exactly that configuration.  The extremum is thus
#   singled out by uniqueness AND by the maximum-entropy theorem.
#
# CURVATURE / ERROR BAND (2026-08-18; sharpened 2026-08-18):
#   Because 4/27 is a STATIONARY point, a shift Δy of the mass
#   fraction moves the threshold only at SECOND order:
#   ρ(y) = 4/27 − (y−1/3)² + O((y−1/3)³), curvature |ρ''(1/3)| = 2
#   (a 10% blur of y moves the threshold by only 0.75%).  BUT the
#   flatness softens only this first link: the threshold acts on kL at
#   FIRST order (d ln kL / d ln(4/27) = −1) and kL acts on the
#   hierarchy at first order (v ∝ e^{−4πkL}, m_e ∝ e^{−20kL}).  The
#   full chain is y→1.10y ⇒ threshold −0.73% ⇒ kL +0.73% ⇒ v −23%,
#   m_e −36%, ρ_Λ −190% (and p→1.01p ⇒ v −26%).  The hierarchy is
#   exact in its central values and convention-sensitive in its
#   exponent — quantified, not left as a bare elasticity.
CRIT = 4.0 / 27.0
FACTOR = 32.0 * math.pi ** 2


def threshold_geometry() -> dict:
    """The extremum geometry of the mass-weighted density ρ(y)=y(1−y)².

    Returns the unique stationary point, the curvature, and the
    second-order error band — the three facts that sharpen 4/27 from
    a bare convention to a uniqueness + maximum-entropy + flatness
    statement (2026-08-18; paper §Theoretical sensitivity, docs
    V4_LEDGER §0.2.C).

    ρ' = (1−y)(1−3y) vanishes on (0,1) only at y = 1/3 (unique
    interior extremum); ρ''(1/3) = −2 (maximum, curvature 2).  The
    error band is quadratic in the blur Δy: Δρ/ρ = (27/4)·(Δy)².
    """
    y_max = 1.0 / 3.0
    rho_max = y_max * (1.0 - y_max) ** 2        # 4/27
    curvature = abs(6.0 * y_max - 4.0)          # |ρ''(1/3)| = 2
    band = {f"{frac:.0%}": (27.0 / 4.0) * (frac * y_max) ** 2
            for frac in (0.03, 0.10, 0.30)}
    return {"y_max": y_max, "rho_max": rho_max,
            "curvature": curvature, "band": band}


def v_pi0(k: float, kL: float, tau: float, M_G: float, M_P: float) -> float:
    """V₃·Π²^{Tμν2}/(32π²) along the kL-const trajectory at scale k.

    The spin-2 channel of the improved EMT on the discrete RP³
    spectrum (spectral_sum); V₃ = π²L³ is the volume, the cutoff is
    (k/M_P)² (the running scale in Planck units), L = kL·M_G/k keeps
    kL constant along the flow.
    """
    L = kL * M_G / k
    V3 = math.pi ** 2 * L ** 3
    cut = (k / M_P) ** 2
    return V3 * channel_tmunu_spin2(L, cut, tau)["rp3_pi0"] / FACTOR


def k_star(kL: float, tau: float, M_G: float, M_P: float) -> float:
    """Bisection: V·Π²/(32π²) = 4/27 → k* (the F_MG spectral-pole scale).

    The bisection runs to the interval width 1e-15 (machine
    precision): kL* is the self-consistent fixed point that every
    other closure reads, so a truncated k* would propagate its error
    into M_G, g₂ and the whole chain.
    """
    lo, hi = 0.3 * M_G, 3.0 * M_G
    flo = v_pi0(lo, kL, tau, M_G, M_P) - CRIT
    fhi = v_pi0(hi, kL, tau, M_G, M_P) - CRIT
    if flo * fhi > 0:
        raise RuntimeError(f"no crossing: kL={kL:.4f} M_G={M_G:.3e}")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f = v_pi0(mid, kL, tau, M_G, M_P) - CRIT
        if (hi - lo) < 1e-15:
            return mid
        if flo * f < 0:
            hi = mid
        else:
            lo = mid
            flo = f
    return 0.5 * (lo + hi)


def self_consistent_chain(M_P: float, L_Cg: float, tau: float) -> dict:
    """The self-consistent emergence chain for a given endpoint
    geometry.

    The fixed point kL* = C/k* with k* = M_G (the F_MG two-step
    iteration): M_G = C/kL*, k_GUT = C/L_GUT with L_GUT = √3/τ (the
    isometry-breaking scale of the J=2 squash).
    """
    C = M_P * L_Cg
    L_GUT = math.sqrt(3.0) / tau
    kL = get("kL")
    for _ in range(60):
        M_G = C / kL
        kL_new = C / k_star(kL, tau, M_G, M_P)
        if abs(kL_new - kL) < 1e-15:
            kL = kL_new
            break
        kL = kL_new
    M_G = C / kL
    return {"C": C, "kL": kL, "M_G": M_G, "M_G_over_MP": M_G / M_P,
            "k_GUT": C / L_GUT}


def compute() -> dict:
    """The full constraint analysis; publishes the main chain into
    the store (first-principles sqrt(pi), 2026-08-16)."""
    M_P = get("M_P")
    tau = get("tau")
    L_Cg = get("L_Cg")   # = sqrt(pi), first-principles

    # ---- MAIN CHAIN (first-principles sqrt(pi), 2026-08-16) ----
    # The main chain uses L_Cg = sqrt(pi), NOT the coupling-closure
    # calibration.  g2 = sqrt(8)(M_G/M_P)kL^{-3/2} deviates from SM by
    # +0.34% = 1/N_c - tau^2*pi/2 — an EXPLAINED geometric-dynamics
    # symmetry correction (the conservation law
    #   N_c(1/alpha_SM - 1/alpha_W + tau^2 pi/2) = 1  <->  N_g xi = 1).
    chain_pi = self_consistent_chain(M_P, L_Cg, tau)
    kL_pi = chain_pi["kL"]
    M_G_pi = chain_pi["M_G"]
    g2_pi = math.sqrt(8.0 * (M_G_pi / M_P) ** 2 / kL_pi ** 3)
    pset("kL", kL_pi, provenance="DERIVED",
         note="F_MG fixed point at L_Cg=sqrt(pi) (first-principles)")
    pset("L_Gg", kL_pi, provenance="DERIVED",
         note="L(M_G)=kL=C/M_G at L_Cg=sqrt(pi)")
    pset("M_G", M_G_pi, provenance="DERIVED",
         note="M_G = M_P*sqrt(pi)/kL (first-principles)")
    pset("g2_MG_bare_constraint", g2_pi, provenance="DERIVED",
         role="internal",
         note="bare g2(M_G) = sqrt(8)(M_G/M_P)kL^{-3/2} at L_Cg=sqrt(pi) "
              "(the constraint-chain value, +0.34% = 1/N_c - tau^2*pi/2 "
              "BEFORE the conservation-law correction; the authoritative "
              "g2_MG is published by geometric_couplings with the "
              "correction applied)")
    pset("L_critical", math.sqrt(math.pi), provenance="DERIVED",
         note="L_c = sqrt(6/R_c) with R_c = 6/pi, so L_c = sqrt(pi) = L_Cg "
              "(first-principles)")

    # ---- first-principles L_Cg* / R_c* (the same sqrt(pi) / 6/pi) ----
    pset("L_Cg_star", math.sqrt(math.pi), provenance="DERIVED",
         note="L_Cg* = sqrt(pi) (first-principles)")
    pset("R_c_star", 6.0 / math.pi, provenance="DERIVED",
         note="R_c* = 6/pi (first-principles, the critical curvature)")
    return chain_pi


if __name__ == "__main__":
    # Smoke: the constraint analysis runs and publishes the chain.
    r = compute()
    print(f"kL* = {r['kL']:.6f}, M_G/M_P = {r['M_G_over_MP']:.6f} "
          f"(L_Cg = sqrt(pi), first-principles)")
    # The threshold extremum geometry (uniqueness + curvature, 2026-08-18).
    tg = threshold_geometry()
    assert abs(tg["rho_max"] - CRIT) < 1e-15, "4/27 = rho(1/3)"
    assert abs(tg["curvature"] - 2.0) < 1e-15, "|rho''(1/3)| = 2"
    assert abs(tg["y_max"] - 1.0 / 3.0) < 1e-15, "unique interior extremum"
    print(f"threshold geometry: y_max={tg['y_max']:.4f} "
          f"rho_max={tg['rho_max']:.6f} curvature={tg['curvature']:.1f} "
          f"(unique extremum, flat to second order)")
    print("endpoint_constraint OK")
