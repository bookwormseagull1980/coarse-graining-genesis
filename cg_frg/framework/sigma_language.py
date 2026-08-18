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
cg_frg/framework/sigma_language.py — V4.0: the σ-language
kinematics — c as the correlation speed (the unit convention)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The framework's fundamental language is the σ field: a single-
valued scalar on the coarse-graining index space, with the
dimension of length.  The RG scale k and the σ distance are the
same physical axis in two units — the kinematic bridge is c:

    σ(k) = c/k ,   σ_C = c/H0 ,   T_eff = k/(2π)

This module formalises the σ-language kinematics and fixes the
status of c:

  · c is the CORRELATION PROPAGATION SPEED in the σ language —
    the internal velocity at which correlations propagate
    through the σ configuration;
  · c is a UNIT CONVENTION (c = 1 in natural units), NOT a third
    physical input: the framework's anchors are M_P (the identity
    anchor G_N = 1/(8πM_P²)) and the internal chain — H0 itself
    is DERIVED (gw_ratio: H0 = M_P·√π·e^{−∫γ_M}); the irreducible
    content is {M_P} + the structure (H0 and c are outputs of the
    internal chain / a unit choice);
  · c is NOT a metric property — the framework has no emergent
    spacetime metric; the speed is the σ-language's internal
    kinematics (the same statement as the no-emergent-geometry
    principle).

THE KINEMATIC BRIDGES (the derivation chain)
--------------------------------------------
1. σ(k) = c/k:  the RG scale k [mass] and the σ distance
   [length] are the same axis; c is the conversion (c = 1 in
   natural units).

2. σ_C = c/H0:  the causal horizon is the IR anchor of the
   window — the largest σ distance, set by the Hubble scale
   (gw_ratio publishes σ_C = 1/H0 with c = 1).

3. T_eff = k/(2π):  the Euclidean temperature of the window at
   scale k — the 2π thread shared with ε = e^{1/2π}, the
   perturbation zero-point Δ²_0 = (1/2)(1/2π)², and the GW ratio
   r = (1/2π)² (the same Euclidean period).

4. L(k) = kL·σ(k) = kL·c/k:  the geometry trajectory — the
   window capacity kL is constant along the flow (the
   self-similar trajectory; endpoint_constraint).

PARAMETERS
----------
Reads : H0_GEV, M_P, kL
Writes: sigma_language_status (DERIVED — this module is its
        writer)

V4 DISCIPLINE
-------------
No observed value enters the computation: c = 1 is the unit
convention, H0 is the internal chain's output (gw_ratio), M_P
is the identity anchor.  The irreducible content is M_P + the
structure.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def sigma_of_k(k: float, c: float = 1.0) -> float:
    """σ(k) = c/k — the σ distance of the RG scale k."""
    return c / k


def horizon_sigma(H0: float, c: float = 1.0) -> float:
    """σ_C = c/H0 — the causal horizon in σ units (the IR anchor)."""
    return c / H0


def eff_temperature(k: float) -> float:
    """T_eff = k/(2π) — the Euclidean temperature of the window."""
    return k / (2.0 * math.pi)


def compute() -> dict:
    """Publish the σ-language kinematics status."""
    H0 = float(get("H0_GEV"))
    M_P = float(get("M_P"))
    kL = float(get("kL"))
    M_G = float(get("M_G"))

    sigma_MG = sigma_of_k(M_G)          # σ at the emergence scale
    sigma_C = horizon_sigma(H0)         # the IR horizon anchor
    T_eff_MG = eff_temperature(M_G)     # the Euclidean temperature at M_G
    # The geometry L(k) = kL·σ(k)·k = kL·c = kL — the window capacity
    # is CONSTANT on the self-similar trajectory (L_Gg = kL = 2.4973;
    # k·σ(k) = c, so L = kL·c = kL exactly).
    L_const = kL * 1.0                   # L(k) = kL·c with c = 1

    pset("sigma_language_status",
         {"c": "unit convention (c = 1); the σ-language correlation "
               "propagation speed",
          "sigma(k)": "c/k",
          "sigma_C": sigma_C,
          "T_eff": "k/(2pi)",
          "L(k)": "kL*c = kL const — the self-similar trajectory "
                   "(k*sigma(k) = c)",
          "anchors": "M_P (identity) + the internal chain; H0 derived "
                     "(gw_ratio); c = 1 convention"},
         provenance="DERIVED", role="informational",
         note=f"the sigma-language kinematics: sigma(k) = c/k, "
              f"k*sigma(k) = c = 1 (the unit convention), "
              f"sigma_C = c/H0 = {sigma_C:.4e} GeV^-1, "
              f"T_eff = k/(2pi); L(k) = kL*c = {L_const:.6f} — the "
              f"window capacity constant on the self-similar trajectory; "
              f"c is the unit convention, NOT a third physical input "
              f"(H0 is derived, c is a unit choice); no emergent metric (the "
              f"no-emergent-geometry principle)")

    return {"sigma_MG": sigma_MG, "sigma_C": sigma_C, "T_eff_MG": T_eff_MG,
            "L_const": L_const, "k_times_sigma": M_G * sigma_MG}


if __name__ == "__main__":
    r = compute()
    print(f"sigma(M_G)  = {r['sigma_MG']:.4e} GeV^-1")
    print(f"sigma_C     = c/H0 = {r['sigma_C']:.4e} GeV^-1 (the IR anchor)")
    print(f"T_eff(M_G)  = k/(2pi) = {r['T_eff_MG']:.4e} GeV")
    print(f"k*sigma(k)  = {r['k_times_sigma']:.10f} = c = 1")
    print(f"L(k)        = kL*c = {r['L_const']:.6f} (the window constant)")
    print("sigma_language OK")
