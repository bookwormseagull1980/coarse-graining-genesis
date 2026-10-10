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
cg_frg/generation/lz_dynamics.py — V5.0: the Landau-Zener extrusion
dynamics — the declared sector indices in a two-level interpretation
=================================================================

PURPOSE
-----------------------------------
The sector indices alpha_up / alpha_down / alpha_lepton are
specified by the content rules in sector_alpha.py. This
module expresses these prescribed indices in a two-level
interpretation. The adiabatic part is assigned the window width kL
and the non-adiabatic part the Einstein-Cartan torsion. A microscopic
Hamiltonian, gap and sweep must be supplied to derive that assignment
from real-time dynamics; no such extra data are computed here.

THE TWO-LEVEL STRUCTURE
-----------------------
The scale flow L(k) = C/k extrudes the generation modes n = {0,2,4}
out of the coarse-graining window.  Each extrusion is a Landau-
Zener two-level system

    H(t) = ( v t   Δ  )
           (  Δ   -v t )

with the avoided-crossing gap Δ and the sweep rate v.  The
single-crossing diabatic survival probability is exp(-pi*Delta²/v)
for this diagonal ±v*t convention and hbar=1, v>0. Diagonal ±v*t/2
would instead give exp(-2*pi*Delta²/v). The functions below use the
declared framework index; they do not compute a microscopic sweep
rate or avoided-crossing gap. The assigned index decomposes
into the adiabatic window width and the non-adiabatic torsion:

    α_up = kL − 2τ = kL − n_broken·τ ,

    · kL      — the adiabatic part: the window width, the extrusion
                of a mode across the full coarse-graining window;
    · 2τ      — the non-adiabatic part: the EC torsion makes the
                crossing non-adiabatic, and n_broken = 2 = (d+1)/2
                is the number of broken SU(2)_R generators (the
                Goldstone directions of the squash), each carrying
                the torsion modulus τ.

In the assigned ladder, subtracting 2τ from the index increases the
positive n=2 transfer weight exp(-2 alpha_up) by exp(4τ) relative to
exp(-2 kL). The identity kL-alpha_up=2τ is exact for this rule.
Interpreting it as a real-time transition requires the independently
specified avoided-crossing gap, sweep and passage phases.

The assigned sector step Δ = 6(1−n_s)·kL_CMB combines
the six so(4) generators (the extrusion coupling), the
spectral tilt 1−n_s (the closed window-evolution rate
τ·[(1+2+1+3)/(d+1)]=τ·7/4), and the CMB window kL_CMB (the scale of
the extrusion).  The 9/8 split
is the hypercharge weight Y_d = 1/3 vs Y_l = 1 in the covariant
derivative on RP³ shifting the LZ exponent of the down/lepton
doublets.

IMPLEMENTATION
-------------
The module evaluates prescribed LZ indices using the two-level interpretation
(kL, τ, 1−n_s, kL_CMB, the 9/8 identity) — the same content ratios
as sector_alpha, now exposed as the adiabatic + non-adiabatic
decomposition of the Landau-Zener crossing.  No observed ratio
enters.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get  # noqa: E402
from cg_frg.generation.sector_alpha import (  # noqa: E402
    alpha_up, sector_step, ladder_down, ladder_lepton,
)


def lz_survival(index: float) -> float:
    """The assigned n=2 ladder weight exp(-2*index).

    A coherent two-passage transition also depends on its interference
    phase; this scalar weight specifies the framework's mass transfer.
    """
    return math.exp(-2.0 * index)


def adiabatic_index(kL: float) -> float:
    """γ_adia = kL — the adiabatic part, the window width."""
    return kL


def nonadiabatic_deficit(tau: float) -> float:
    """γ_non = 2τ = n_broken·τ — the non-adiabatic deficit, the
    torsion content of the two broken generators."""
    return 2.0 * tau


def compute() -> dict:
    """Verify the current stored ladder and its assigned two-level weights."""
    kL = float(get("kL"))
    tau = float(get("tau"))
    ns_tilt = float(get("ns_tilt"))
    kL_cmb = float(get("kL_CMB"))

    au = alpha_up(kL, tau)
    Delta = sector_step(ns_tilt, kL_cmb)
    ad = ladder_down(au, Delta)
    al = ladder_lepton(au, Delta)

    expected = {"alpha_up": au, "alpha_down": ad, "alpha_lepton": al,
                "sector_alpha_delta": Delta,
                "m_t_over_m_c": 1/lz_survival(au),
                "m_b_over_m_s": 1/lz_survival(ad)}
    for key, value in expected.items():
        if not math.isclose(float(get(key)), value, rel_tol=2e-12, abs_tol=0.):
            raise ValueError(f"current ladder record is inconsistent: {key}")
    adiabatic, deficit = adiabatic_index(kL), nonadiabatic_deficit(tau)
    if not math.isclose(adiabatic-au, deficit, rel_tol=2e-12, abs_tol=0.):
        raise ValueError("the two-level decomposition fails the current ladder")
    ratio = (au-ad)/(ad-al)
    if not math.isclose(ratio, 9/8, rel_tol=2e-12, abs_tol=0.):
        raise ValueError("the current ladder fails the hypercharge step relation")
    return {"alpha_up": au, "alpha_down": ad, "alpha_lepton": al,
            "delta": Delta, "adiabatic": adiabatic,
            "nonadiabatic": deficit, "step_ratio": ratio}


if __name__ == "__main__":
    result = compute()
    for key, value in result.items():
        print(f"{key:16s} = {value:.12g}")
    print("Current stored ladder and assigned two-level weights verified")
