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
cg_core/frg_regulator.py — V5.0: the FRG regulator reference
=================================================================

PURPOSE
-----------------------------------
The coarse-graining window can be implemented by different
regulators.  The primary regulator of the framework is the
exponential window R_k(z) = z/(e^{z/k²}−1) (trace_kernels); the
Litim sharp cutoff is the alternative used for scheme-independence
cross-checks (the classification conclusions — the signs of the
channel amplitudes — must not depend on the regulator).  This
module is the reference implementation of both.

THE REGULATORS
--------------
· Exponential window: R_k(z) = z/(e^{z/k²} − 1) (smooth; R(0) = k²).
· Litim sharp cutoff: R_k(z) = (k² − z) θ(k² − z) (the sharp
  regulator; the derivative ∂_t R_k = 2k² θ(k²−z)).

STATUS
------
Reference module: the exponential window is the production
regulator (trace_kernels); the Litim cutoff is the cross-check.
Both implementations use this exponential window and its analytic
scale derivative.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def exponential_regulator(z: float, k2: float) -> float:
    """R_k(z) = z/(e^{z/k²} − 1) — the exponential window.

    The z/(e^{z/k²}−1) form satisfies the regulator convention
    R(0) = k² (finite) and decays R → 0 for z ≫ k²; it is the SAME
    window as trace_kernels._exponential_terms (the production
    regulator).
    """
    if z < 1e-10 * k2:
        # The small-y Taylor branch avoids the 0/0 limit:
        # z/(e^y−1) → k² − z/2 (finite, R(0) = k²).
        return k2 - 0.5 * z
    return z / (math.exp(z / k2) - 1.0)


def exponential_dR_dt(z: float, k2: float) -> float:
    """∂_t R_k (t = ln k) for the exponential window R = z/(e^{z/k²}−1).

    ∂_t R_k = 2zy e^y/(e^y−1)² with y = z/k² (the analytic derivative
    of the implemented window; matches trace_kernels).
    """
    y = z / k2
    if y < 1e-10:
        return 2.0 * k2 * (1.0 - y * y / 12.0)
    if y > 500.0:
        return 0.0
    ey = math.exp(y)
    em1 = ey - 1.0
    return 2.0 * z * y * ey / (em1 * em1)


def litim_regulator(z: float, k2: float) -> float:
    """R_k(z) = (k² − z) θ(k² − z) — the Litim sharp cutoff."""
    return (k2 - z) if z < k2 else 0.0


def litim_dR_dt(z: float, k2: float) -> float:
    """∂_t R_k = 2k² θ(k² − z) for the Litim cutoff."""
    return (2.0 * k2) if z < k2 else 0.0


def _self_test() -> None:
    k2 = 1.0
    # The exponential regulator: R(0) = k² (finite, the regulator
    # convention — NOT k⁴/z divergent), R → 0 for z ≫ k².
    assert abs(exponential_regulator(0.0, k2) - 1.0) < 1e-9
    assert exponential_regulator(100.0, k2) < 1e-40
    # The small-y Taylor branch must agree with the full form:
    z = 1e-6 * k2
    full = z / (math.exp(z / k2) - 1.0)
    assert abs(exponential_regulator(z, k2) - full) / full < 1e-9
    # The Litim regulator: R(0) = k², R = 0 for z ≥ k².
    assert abs(litim_regulator(0.0, k2) - 1.0) < 1e-15
    assert litim_regulator(2.0, k2) == 0.0
    print("frg_regulator self-test OK")


if __name__ == "__main__":
    _self_test()
