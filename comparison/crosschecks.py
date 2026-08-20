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
comparison/crosschecks.py ? V4.0: independent cross-checks of the
framework's internal closures against the SM comparison store
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
Two of the framework's closures admit an independent cross-check
against the SM comparison values (comparison only; the SM values
never enter the framework computation):

  kL CROSS-CHECK (2026-08-19, implemented from the paper's claim):
  ---------------------------------------------------------------
  The gauge-coupling conservation law
      1/alpha_SM = 1/alpha_W + 1/N_c - tau^2 pi/2 ,  alpha_W = 2/kL^5
  is INVERTED at the SM comparison coupling g2(M_G) = 0.508844967
  (sm_inputs.json, comparison only) to give an independent
  determination of the window capacity kL.  The framework's F_MG
  spectral-pole fixed point is kL = 2.49353; the inverted value is
  kL_cross = 2.49371, a deviation of +0.0072%.  This is the
  quantitative implementation of the cross-validation quoted in the
  paper; the deviation is reported at full precision.  The
  cross-check is non-circular: the F_MG closure fixes kL from the
  spin-2 spectral-pole condition alone, while the conservation law
  fixes kL from the SM weak coupling through the window-capacity
  form alpha_W = 2/kL^5.
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
    print(f"kL (F_MG spectral-pole fixed point)        = {kL:.9f}")
    print(f"kL (conservation law at SM g2_MG = {g2_sm:.9f}) = {kL_cross:.9f}")
    print(f"cross-check deviation                      = {dev:+.4f}%")
    assert abs(kL_cross - kL) / kL < 1e-3, "kL cross-check outside 0.1%"
    return 0


if __name__ == "__main__":
    sys.exit(main())
