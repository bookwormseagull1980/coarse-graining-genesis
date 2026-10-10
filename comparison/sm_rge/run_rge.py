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

"""Two-loop Standard-Model running for the reference comparison table.

Classical fourth-order Runge--Kutta integration uses t=ln(mu), with
400 steps per unit t. The routes M_Z -> M_G -> k_GUT and
M_Z -> v -> k_GUT evaluate the semigroup consistency of the numerical
flow at the same final scale. The maximum relative route difference
must be below 1e-12. The results are written to the comparison store.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import sm_set  # noqa: E402
from cg_core.beta_functions import derivatives5  # noqa: E402
from cg_core.rk4 import rk4_integrate  # noqa: E402


def run_rge(y0: list[float], ln_mu0: float, ln_mu1: float,
            steps_per_efold: int = 400) -> list[float]:
    """Integrate over ln(mu1/mu0) at the specified steps per unit ln(mu)."""
    dt_total = ln_mu1 - ln_mu0
    n_steps = max(1, int(round(abs(dt_total) * steps_per_efold)))
    return rk4_integrate(derivatives5, y0, dt_total, n_steps)


def run_sm_table(M_Z: float, M_G: float, k_GUT: float, v: float) -> float:
    """Run the SM couplings along the two routes and write the
    comparison/coupling-closure values to reference_inputs.json.

    Route A: M_Z → M_G → k_GUT.  Route B: M_Z → v → k_GUT.  The two
    routes must agree at k_GUT to 1e-12 (the consistency check).
    """
    from comparison.sm_rge.inputs import sm_value

    y0 = [sm_value("g1_MZ"), sm_value("g2_MZ"), sm_value("g3_MZ"),
          sm_value("yt_MZ"), sm_value("lam_MZ")]
    ln_mz = math.log(M_Z)

    # Route A: M_Z → M_G → k_GUT.
    y_MG_A = run_rge(y0, ln_mz, math.log(M_G))
    y_GUT_A = run_rge(y_MG_A, math.log(M_G), math.log(k_GUT))

    # Route B: M_Z → v → k_GUT.
    y_v = run_rge(y0, ln_mz, math.log(v))
    y_GUT_B = run_rge(y_v, math.log(v), math.log(k_GUT))

    # Relative semigroup defect at the common final scale.
    max_dev = max(abs(a - b) / max(abs(a), 1e-30)
                  for a, b in zip(y_GUT_A, y_GUT_B))
    if max_dev > 1e-12:
        raise RuntimeError(f"SM RGE routes disagree: max relative dev {max_dev}")

    names = ["g1_MG", "g2_MG", "g3_MG", "yt_MG", "lambda_MG"]
    for name, val in zip(names, y_MG_A):
        sm_set(name, val, note="SM two-loop extrapolation at M_G (comparison)")
    names_gut = ["g1_sm_GUT", "g2_sm_GUT", "g3_sm_GUT", "yt_sm_GUT", "lambda_sm_GUT"]
    for name, val in zip(names_gut, y_GUT_A):
        sm_set(name, val, note="SM two-loop extrapolation at k_GUT (comparison)")
    return max_dev


if __name__ == "__main__":
    # Compare at the generated emergence and GUT scales.
    from comparison.sm_rge.inputs import init_sm_table, sm_value
    from cg_core.params import get

    init_sm_table()
    M_Z = sm_value("M_Z")
    M_G = get("M_G")        # the chain's own emergence scale
    k_GUT = get("k_GUT")    # the chain's own GUT scale
    v = sm_value("v_HIGGS_obs")  # observed VEV for the intermediate comparison scale
    dev = run_sm_table(M_Z, M_G, k_GUT, v)
    print(f"SM RGE table refreshed from the store chain "
          f"(route agreement: max rel dev {dev:.2e})")
    print("sm_rge/run_rge OK")
