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
cg_frg/cosmology/perturbation_amplitude.py — V5.0: the primordial
perturbation AMPLITUDE closed (no inflation)
=================================================================

PURPOSE
-----------------------------------
The framework predicts the CMB scalar amplitude Δ²_R WITHOUT
inflation: the fluctuations are the spin-1/2 Gaussian zero-point
of the minimal unbiased change, suppressed by the emergence
window's Euclidean period:

    Δ²_R = Δ²_0 · e^{−2π·kL_CMB}

    Δ²_0 = (1/2)·(1/2π)² = 1.267e-2   (the spin-1/2 zero-point)
    e^{−2π·kL_CMB} = e^{−15.59} = 1.68e-7  (the window suppression)
    Δ²_R = 2.10e-9  (no inflation)

THE SUPPRESSION FAMILY (the common thread 2π)
---------------------------------------------
The hierarchy v/ε/Λ are dilaton powers {1,1,10}; the family's
common thread is the 2π (the Euclidean period):

    ε  = e^{1/2π}   (the zero-point — the EW ratio)
    a0 = sqrt(4/3) cH0/(2π)   (the endpoint RMS acceleration)
    2L = √(2π)      (the entropy-min distance)
    kL ≈ √(2π)      (2.4935343 vs 2.5066 — 0.52% — the window)

The amplitude uses the CMB-scale window width kL_CMB = 2.4810667
(NOT the local kL = 2.4935343 at M_G): the amplitude is a CMB-scale
observable, and the window evolves between M_G and the CMB.

IMPLEMENTATION
-------------
kL_CMB is the framework's CMB-scale window: this module is its
publisher (computed from the local kL and the torsion quarter,
kL_CMB = kL·(1 − τ/4)).  Δ²_R uses only internal quantities.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def delta_squared(kL_cmb: float) -> dict:
    """Δ²_R = (1/2)(1/2π)²·e^{−2π·kL_CMB}."""
    D0 = 0.5 * (1.0 / (2.0 * math.pi)) ** 2
    supp = math.exp(-2.0 * math.pi * kL_cmb)
    D_R = D0 * supp
    return {"D_R": D_R, "D0": D0, "suppression": supp}


def compute() -> dict:
    """Publish the CMB-window width (COMPUTED) and the amplitude."""
    # kL_CMB is COMPUTED from the local kL and the torsion:
    # kL_CMB = kL*(1 - tau/4), the torsion-quarter reduction of the
    # window at the CMB pivot.
    tau = float(get("tau"))
    kL = float(get("kL"))
    kL_cmb = kL * (1.0 - tau / 4.0)
    pset("kL_CMB", kL_cmb, provenance="DERIVED", role="cg",
         dependencies=("kL", "tau"),
         note=f"kL_CMB = kL*(1 - tau/4) = {kL_cmb:.10f} (the CMB-pivot "
              f"window: the local kL reduced by the torsion quarter "
              f"tau/4 = {tau/4.0}; computed, not a scale choice)")
    r = delta_squared(kL_cmb)
    # ---- chiral x squash correction  ----
    # The spin-1/2 zero-point D0 is chiral (the minimal unbiased change
    # is a spinor), so the amplitude carries +tau·kappa (the charged-quotient
    # quotient modulus tau x the squash normalisation kappa) — the same charged-
    # squash content as eta_B and T_deconf.  (1 - tau·kappa) brings
    # Delta2_R to -0.19%.
    # the chiral-level (1-tau*kappa) factor
    # is the chiral-restoration charge c=−1/2 (τ=s0/2) of squash_level_transfer;
    # the spin-1/2 zero-point channel couples to the charged-quotient modulus τ.
    # See epsilon_ratio SOURCE OF THE CORRECTION FACTORS.
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    D_R = r["D_R"] * (1.0 - tau * kappa)
    pset("perturbation_amplitude", D_R, provenance="DERIVED",
         dependencies=("kL", "tau"),
         role="internal",
         note=f"Delta2_R = (1/2)(1/2pi)^2 e^(-2pi kL_CMB) (1 - tau*kappa) = "
              f"{D_R:.3e} (the spin-1/2 zero-point x the Euclidean "
              f"suppression x the chiral-squash correction, no inflation)")
    return {**r, "kL_CMB": kL_cmb, "D_R": D_R}


if __name__ == "__main__":
    r = compute()
    print(f"Delta2_0 = {r['D0']:.3e}, suppression e^(-2pi kL_CMB) = "
          f"{r['suppression']:.3e}")
    print(f"Delta2_R = {r['D_R']:.3e} (no inflation)")
    print("perturbation_amplitude OK")
