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
cg_core/rk4.py — V5.0: the generic RK4 integrator
=================================================================

PURPOSE
-----------------------------------
The framework's coupling running integrates an ordinary
differential system y' = f(y) over the scale parameter t = ln μ.
This is a GENERIC numerical algorithm (the classical 4th-order
Runge-Kutta scheme) — it is NOT part of any external model: the
derivative function f (the beta functions) is passed in as an
argument.  The framework's geometric RGE uses this integrator with
the gauge-coupling beta functions (cg_core/beta_functions).

IMPLEMENTATION
-------------
No physics value lives here: this module is a pure numerical
algorithm (a structural tool), independent of any model content.
"""

from __future__ import annotations


def rk4_integrate(f, y0, dt_total: float, steps: int):
    """Integrate y' = f(y) over dt_total with `steps` RK4 steps.

    Derivation: the classical RK4 weights (1, 2, 2, 1)/6 on the four
    slope evaluations at t, t+h/2, t+h/2, t+h.  `f` is any RHS
    (here the beta functions); the integrator is model-agnostic.

    Returns the state y at the end of the interval.
    """
    h = dt_total / steps
    y = list(y0)
    for _ in range(steps):
        k1 = f(y)
        k2 = f([yi + 0.5 * h * ki for yi, ki in zip(y, k1)])
        k3 = f([yi + 0.5 * h * ki for yi, ki in zip(y, k2)])
        k4 = f([yi + h * ki for yi, ki in zip(y, k3)])
        y = [yi + h / 6.0 * (a + 2.0 * b + 2.0 * c + d)
             for yi, a, b, c, d in zip(y, k1, k2, k3, k4)]
    return y


def rk4_run(y0, ln_mu0: float, ln_mu1: float,
            steps_per_decade: int = 400):
    """Integrate y' = f(y) over t = ln μ from ln_mu0 to ln_mu1 with a
    given steps-per-decade density (the framework's default: 400 steps
    per e-fold)."""
    dt_total = ln_mu1 - ln_mu0
    n_steps = max(1, int(round(abs(dt_total) * steps_per_decade)))
    return n_steps, dt_total


if __name__ == "__main__":
    # Smoke test: integrate a trivial linear system y' = y over one
    # e-fold — the result must be e to RK4 precision.
    import math
    y = rk4_integrate(lambda yy: yy, [1.0], 1.0, 400)
    print(f"rk4 self-test: e^(1) = {y[0]:.10f} vs {math.e:.10f} "
          f"(err {abs(y[0] - math.e):.2e})")
    print("rk4 OK")
