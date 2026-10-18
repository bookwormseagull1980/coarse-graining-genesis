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
cg_frg/ewsb/epsilon_ratio.py — V5.0: the electroweak scale ratio
ε_L/ε_R
=================================================================

PURPOSE
-----------------------------------
The electroweak breaking scale is set by the ratio ε of the
left-right hierarchy: the EW scale v = M_G·ε with ε ≈ 1.4e-16.
The current implementation evaluates two algebraically identical
parameterizations of the specified corrected window readout. They are
an internal identity check, not independent physical evidence:

  LINE 1 — the window-squared channel (the dynamical line):
      ε = (3α/π)·e^{−4πkL},   α = 1/16π²
    Both current functions include the common factor (1-s0*kappa).
    The mechanism: the J=2 squash bifurcation contributes 3α/2; the
    mode crosses the coarse-graining window TWICE (creation and
    stabilisation), each crossing contributing e^{−2πkL} (the same
    factor as the CMB perturbation Δ²_s); the Fourier prefactor
    contributes 1/π.  Product: (3α/2)·(1/π)·e^{−4πkL}·2 = 3α/π.

  LINE 2 — the dilaton-stop line (the zero-point line):
      ε = e^{1/(2π)}·e^{−φ_R3},   φ_R3 = 4πkL − ln(3α/π) + 1/(2π)
    The 1/(2π) is the Euclidean zero-point (the causal-horizon
    temperature T_eff = k/(2π)); φ_R3 is the dilaton stop position.
    The current stop also includes -log(1-s0*kappa), so substitution
    cancels the zero-point factor and reproduces LINE 1 exactly.

THE WINDOW-SQUARED MECHANISM (why e^{−4πkL})
--------------------------------------------
The LZ non-adiabatic extrusion of the J=2 squash mode across the
coarse-graining window suppresses the amplitude twice: the mode is
created at the window edge and stabilised there, each with the
LZ survival e^{−2πkL} — the same exponential that governs Δ²_s
(perturbation_amplitude: D0·e^{−2πkL_CMB}).

IMPLEMENTATION
-------------
The ε closure uses only internal quantities (kL, α = 1/16π²).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

# The fine-structure constant: α = 1/16π² (the one-loop weight).
_ALPHA = 1.0 / (16.0 * math.pi ** 2)


def squash_correction() -> float:
    """(1 − s0·κ(2τ)) — the J=2 squash correction to the EW ratio ε.

    s0 = 2τ = n_broken·τ is the squash amplitude (n_broken = 2 = (d+1)/2
    the broken SU(2)_R generators); κ(2τ) = √((1+s0)/(1−2s0)^{5/2}) is
    the U(1)_Y normalisation (the SAME κ that enters g1 = g2·κ).  The
    EW hierarchy ratio ε is corrected multiplicatively by (1 − s0·κ):
    the isometry-breaking squash shifts the dilaton-stop line — the
    EW-hierarchy analogue of the g₂ conservation law (1/N_c − τ²π/2).

    THE SQUASH LEVEL-TRANSFER RULE (the unified sign/multiplier):
    s0·κ = N_g·τ·κ/(d+1) is the unified correction source (the λ_EC
    first-order torsion N_g·τ divided by d+1, times the squash metric
    κ).  Its sign/multiplier across the levels is fixed by content:
      · geometric levels (v, g₁, α_s, V_cb): −s0·κ (the squash shrinks
        the geometric quantity);
      · chiral levels (T_deconf, Δ²_R, V_ub, m_p): ±τ·κ (the chiral
        asymmetry τ = s0/2);
      · seesaw level transfer (m_ν3): +s0·κ (the sign reversal of the
        EW ↔ seesaw transfer);
      · power level (ρ_Λ): −4s0·κ (4 = m_ν1⁴, the dark-energy weight).
    Paired conservation: v·m_ν3 and m_ν1⁴·weight are conserved to first
    order (the level transfer preserves the total content).

    SOURCE OF THE CORRECTION FACTORS:
      L1  κ(2τ)=√((1+2τ)/(1−4τ)^{5/2}) is the squashed-S³
          metric Killing normalisation (geometric integral, see
          geometric_couplings.squash_metric); s0 = 2τ = n_broken·τ with
          n_broken = 2 = dim SU(2)_R − dim U(1)_R (broken-generator
          count); τ = 1/50 is the content ratio.
      L2  ρ_Λ's (1−4s0κ) follows from m_ν1
          carrying +s0κ so m_ν1⁴ carries +4s0κ and the weight cancels;
          m_e and T_CMB inherit v's (1−s0κ) through the cascade/photon
          floor.
      L3  The specific sign and multiplier of v (−s0κ, the
          traceless shear), m_ν3 (+s0κ, the level-transfer conservation
          v·m_ν3 = const), T_d and Δ²_R (−τκ, the charged-quotient modulus τ = s0/2),
          m_p (+5τκ/3 = +τκ·ΣY²·Δ_s, the constituent content ratio), α_s
          (−s0κ/N_g = −s0κ·ξ, the Yukawa-difference conformal normalisation)
          are computed moments c_Q=a_Q r_Q.  The amplitude fraction a_Q
          comes from n_broken=2 and N_L−N_R=1.  The constituent and generator
          ratios reduce to ΣY² Δ_s=5/3 and ξ=1/N_g=1/8, respectively.
    """
    tau = get("tau")
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    return 1.0 - s0 * kappa


def epsilon_window(kL: float) -> float:
    """ε = (3α/π)·e^{−4πkL}·(1 − s0·κ(2τ)) — the window-squared line
    with the J=2 squash correction.

    (3α/2)·(1/π)·e^{−4πkL}·2 = 3α/π·e^{−4πkL}: the squash
    bifurcation, the Fourier prefactor, and the double window
    crossing; times (1 − s0·κ) the isometry-breaking squash
    correction (s0 = 2τ the amplitude, κ the U(1)_Y normalisation).
    """
    return (3.0 * _ALPHA / math.pi) * math.exp(-4.0 * math.pi * kL) \
        * squash_correction()


def dilaton_stop(kL: float) -> float:
    """φ_R3 = 4πkL − ln(3α/π) + 1/(2π) − ln(1 − s0·κ(2τ)) — the
    implied dilaton stop, including the J=2 squash correction (so the
    dilaton-stop line reproduces the corrected window-squared line).
    """
    return 4.0 * math.pi * kL - math.log(3.0 * _ALPHA / math.pi) \
        + 1.0 / (2.0 * math.pi) - math.log(squash_correction())


def epsilon_dilaton(kL: float) -> float:
    """ε = e^{1/(2π)}·e^{−φ_R3} — the dilaton-stop line.

    The 1/(2π) is the Euclidean zero-point (T_eff = k/(2π)); φ_R3
    is the stop position of the relaxion/dilaton line.
    """
    return math.exp(1.0 / (2.0 * math.pi)) * math.exp(-dilaton_stop(kL))


def compute() -> dict:
    """Publish the two ε lines and their comparison."""
    kL = get("kL")
    ew = epsilon_window(kL)
    # The dilaton stop includes the same -ln(1-s0*kappa) squash term
    # as the window-squared expression, using the common kL and tau.
    ed = epsilon_dilaton(kL)

    pset("epsilon_L_over_R", ed, provenance="DERIVED",
         note="epsilon = (3 alpha/pi) e^{-4 pi kL} (1-s0*kappa), "
              "with alpha=1/(16 pi^2), s0=2 tau and kappa=kappa(2 tau); "
              "the dilaton-stop form e^{1/(2pi)} e^{-phi} is identical")
    pset("phi_R3", dilaton_stop(kL), provenance="DERIVED",
         note="the dilaton stop position 4*pi*kL - ln(3*alpha/pi) + "
              "1/(2*pi) - ln(1-s0*kappa), with s0=2 tau")
    return {"epsilon_window": ew, "epsilon_dilaton": ed,
            "phi_R3": dilaton_stop(kL)}


if __name__ == "__main__":
    r = compute()
    print(f"epsilon_window = {r['epsilon_window']:.6e}")
    print(f"epsilon_dilaton = {r['epsilon_dilaton']:.6e}")
    print(f"phi_R3 = {r['phi_R3']:.6f}")
    print("epsilon_ratio OK")
