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

"""Compare the finite-response endpoint with the weak-coupling relation.

The production endpoint solves the specified R=5 response equation.
The comparison inverts

    1/alpha_SM = 1/alpha_W + 1/N_c - tau^2*pi/2,
    alpha_W = 2/(kL)^5,

at the independently extrapolated comparison coupling g2(M_G). The
reported difference compares these two determinations of kL. The
comparison coupling is read after the production endpoint is computed.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, sm_value  # noqa: E402


def kL_from_conservation_law(g2_target: float, tau: float) -> float:
    """kL solved from the conservation law at a target weak coupling.

    1/alpha_SM = 1/alpha_W + 1/N_c - tau^2 pi/2 with alpha_W = 2/kL^5
    and alpha_SM = g2_target^2/(4 pi).  Returns kL = (2/alpha_W)^(1/5).
    """
    alpha_sm = g2_target ** 2 / (4.0 * math.pi)
    inv_alpha_w = 1.0 / alpha_sm - 1.0 / 3.0 + tau ** 2 * math.pi / 2.0
    return (2.0 * inv_alpha_w) ** 0.2


def main() -> int:
    kL = float(get("kL"))
    tau = float(get("tau"))
    g2_sm = float(sm_value("g2_MG"))
    kL_cross = kL_from_conservation_law(g2_sm, tau)
    dev = (kL_cross / kL - 1.0) * 100.0
    print(f"kL (R=5 finite-response endpoint)          = {kL:.9f}")
    print(f"kL (conservation law at SM g2_MG = {g2_sm:.9f}) = {kL_cross:.9f}")
    print(f"cross-check deviation                      = {dev:+.4f}%")
    assert abs(kL_cross - kL) / kL < 1e-3, "kL cross-check outside 0.1%"
    return 0


if __name__ == "__main__":
    sys.exit(main())
