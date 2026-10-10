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
cg_frg/framework/sigma_language.py — V5.0: the σ-language
kinematics — c as the correlation speed (the unit convention)
=================================================================

PURPOSE
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
  · c = 1 fixes natural units. The dimensionful anchor is M_P (the identity
    anchor G_N = 1/(8πM_P²)) and the internal chain — H0 itself
    is derived (gw_ratio: H0 = M_P·√π·e^{−S}); the irreducible
    content is {M_P} + the structure (H0 and c are outputs of the
    internal chain / a unit choice);
  · The present identities specify the resolution and length conventions.
    The macroscopic metric response is determined by the Einstein--matter
    action in the gravitational sector.

THE KINEMATIC BRIDGES (the derivation chain)
--------------------------------------------
1. σ(k) = c/k:  the RG scale k [mass] and the σ distance
   [length] are the same axis; c is the conversion (c = 1 in
   natural units).

2. σ_C = c/H0:  the causal horizon is the IR anchor of the
   window — the largest σ distance, set by the Hubble scale
   (gw_ratio publishes σ_C = 1/H0 with c = 1).

3. T_eff = k/(2π) is a conditional thermal identification: it
   requires a state with the declared Euclidean/KMS period 2π/k.
   A resolution index alone does not define a temperature.

4. L(k) = kL·σ(k) = kL·c/k:  the geometry trajectory — the
   window capacity kL is constant along the flow (the
   self-similar trajectory; endpoint_constraint).

PARAMETERS
----------
Reads : H0_GEV, M_P, kL
Writes: sigma_language_status (DERIVED — this module is its
        writer)

IMPLEMENTATION
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
    if not math.isfinite(k) or not math.isfinite(c) or k <= 0 or c <= 0:
        raise ValueError("positive finite scale and unit conversion required")
    return c / k


def horizon_sigma(H0: float, c: float = 1.0) -> float:
    """σ_C = c/H0 — the causal horizon in σ units (the IR anchor)."""
    return sigma_of_k(H0, c)


def eff_temperature(k: float, *, assume_kms_period: bool = False) -> float:
    """Temperature conditional on an explicitly supplied period 2*pi/k."""
    sigma_of_k(k)
    if not assume_kms_period:
        raise ValueError("a resolution scale does not by itself specify a thermal state")
    return k / (2.0 * math.pi)


def physical_radius(k: float, capacity: float) -> float:
    """L_phys=capacity/k [GeV^-1] for k [GeV]; capacity=k*L_phys."""
    return sigma_of_k(k, capacity)


def compute() -> dict:
    """Publish the σ-language kinematics status."""
    H0 = float(get("H0_GEV"))
    M_P = float(get("M_P"))
    kL = float(get("kL"))
    M_G = float(get("M_G"))

    sigma_MG = sigma_of_k(M_G)          # σ at the emergence scale
    sigma_C = horizon_sigma(H0)         # the IR horizon anchor
    T_eff_MG = eff_temperature(M_G, assume_kms_period=True)
    L_MG = physical_radius(M_G, kL)

    pset("sigma_language_status",
         {"c": "unit convention (c = 1); the σ-language correlation "
               "propagation speed",
          "sigma(k)": "c/k",
          "sigma_C": sigma_C,
          "T_eff": "k/(2pi), conditional on the specified KMS period",
          "L_phys(k)": "capacity/k in GeV^-1; k in GeV",
          "capacity_kL": kL,
          "L_phys_at_MG_GeV_inverse": L_MG,
          "anchors": "M_P (identity) + the internal chain; H0 derived "
                     "(gw_ratio); c = 1 convention"},
         provenance="DERIVED", role="informational",
         note=f"the sigma-language kinematics: sigma(k) = c/k, "
              f"k*sigma(k) = c = 1 (the unit convention), "
              f"sigma_C = c/H0 = {sigma_C:.4e} GeV^-1, "
              f"conditional T_eff = k/(2pi); L_phys(k)=capacity/k; "
              f"capacity={kL:.6f} is dimensionless and constant; "
              f"c=1 specifies natural units and H0 is derived from the "
              f"endpoint entropy prescription",
         dependencies=("H0_GEV", "M_P", "kL", "M_G"),
         evidence_kind="dimensional identities and an explicit thermal-state assumption")

    return {"sigma_MG": sigma_MG, "sigma_C": sigma_C, "T_eff_MG": T_eff_MG,
            "capacity_kL": kL, "L_phys_MG_GeV_inverse": L_MG,
            "k_times_sigma": M_G * sigma_MG}


if __name__ == "__main__":
    r = compute()
    print(f"sigma(M_G)  = {r['sigma_MG']:.4e} GeV^-1")
    print(f"sigma_C     = c/H0 = {r['sigma_C']:.4e} GeV^-1 (the IR anchor)")
    print(f"T_eff(M_G)  = k/(2pi) = {r['T_eff_MG']:.4e} GeV")
    print(f"k*sigma(k)  = {r['k_times_sigma']:.10f} = c = 1")
    print(f"L_phys(M_G) = {r['L_phys_MG_GeV_inverse']:.6e} GeV^-1")
    print("sigma_language OK")
