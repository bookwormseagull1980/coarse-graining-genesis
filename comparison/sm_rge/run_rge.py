# -*- coding: utf-8 -*-
"""
comparison/sm_rge/run_rge.py — V4.0: the SM RGE running (RK4)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The SM couplings are extrapolated from M_Z to the high scales
(M_G, k_GUT) for the comparison table: the framework's geometric
couplings are compared against the SM running at the same scale.
This module integrates the two-loop SM beta functions with RK4
(400 steps per decade) along two routes — M_Z → M_G → k_GUT and
M_Z → v → k_GUT — which must agree to 1e-12 (a numerical
consistency check).  The outputs are written into sm_inputs.json
(the SM comparison table), never into the physics store.

V4 DISCIPLINE
-------------
The SM running produces comparison values only (SM_INPUT
provenance).  The physics modules read the framework's own
parameters; the SM table is referenced only by the comparison
records.
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
            steps_per_decade: int = 400) -> list[float]:
    """Integrate the couplings from μ0 to μ1 with the generic RK4
    integrator (cg_core.rk4) over t = ln μ.

    t = ln μ; the integration is over dt = ln(μ1/μ0), with
    steps_per_decade steps per e-fold of the scale.
    """
    dt_total = ln_mu1 - ln_mu0
    n_steps = max(1, int(round(abs(dt_total) * steps_per_decade)))
    return rk4_integrate(derivatives5, y0, dt_total, n_steps)


def run_sm_table(M_Z: float, M_G: float, k_GUT: float, v: float) -> None:
    """Run the SM couplings along the two routes and write the
    comparison/coupling-closure values to sm_inputs.json.

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

    # The consistency check (the two routes must agree).  The
    # threshold is 1e-12 (the docstring's stated precision); the
    # measured agreement is ~4.5e-13 (RK4, 400 steps/decade).
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
    # Smoke: run the RGE along the M_Z -> M_G -> k_GUT route using the
    # STORE's own chain values (never placeholders — writing a stale
    # table would corrupt every downstream closure).
    from comparison.sm_rge.inputs import init_sm_table, sm_value
    from cg_core.params import get

    init_sm_table()
    M_Z = sm_value("M_Z")
    M_G = get("M_G")        # the chain's own emergence scale
    k_GUT = get("k_GUT")    # the chain's own GUT scale
    v = sm_value("v_HIGGS")  # the observed EW VEV (the route-B anchor)
    dev = run_sm_table(M_Z, M_G, k_GUT, v)
    print(f"SM RGE table refreshed from the store chain "
          f"(route agreement: max rel dev {dev:.2e})")
    print("sm_rge/run_rge OK")
