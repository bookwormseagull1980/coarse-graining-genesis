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
cg_core/frg_regulator.py — V4.0: the FRG regulator reference
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The coarse-graining window can be implemented by different
regulators.  The primary regulator of the framework is the
exponential window R_k(z) = k²/(e^{z/k²}−1) (trace_kernels); the
Litim sharp cutoff is the alternative used for scheme-independence
cross-checks (the classification conclusions — the signs of the
channel amplitudes — must not depend on the regulator).  This
module is the reference implementation of both.

THE REGULATORS
--------------
· Exponential window: R_k(z) = k²/(e^{z/k²} − 1) (smooth).
· Litim sharp cutoff: R_k(z) = (k² − z) θ(k² − z) (the sharp
  regulator; the derivative ∂_t R_k = 2k² θ(k²−z)).

STATUS
------
Reference module: the exponential window is the production
regulator (trace_kernels); the Litim cutoff is the cross-check.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def exponential_regulator(z: float, k2: float) -> float:
    """R_k(z) = k²/(e^{z/k²} − 1) — the exponential window."""
    if z < 1e-10 * k2:
        # The small-y Taylor branch avoids the 0/0 limit.
        return k2 - 0.5 * z
    return k2 / (math.exp(z / k2) - 1.0)


def exponential_dR_dt(z: float, k2: float) -> float:
    """∂_t R_k (t = ln k) for the exponential window."""
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
    # The exponential regulator: R(0) = k², R → 0 for z ≫ k².
    assert abs(exponential_regulator(0.0, k2) - 1.0) < 1e-9
    assert exponential_regulator(100.0, k2) < 1e-40
    # The Litim regulator: R(0) = k², R = 0 for z ≥ k².
    assert abs(litim_regulator(0.0, k2) - 1.0) < 1e-15
    assert litim_regulator(2.0, k2) == 0.0
    print("frg_regulator self-test OK")


if __name__ == "__main__":
    _self_test()
