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

"""Finite Gaussian TT response domain and the three-position certificate.

The production endpoint is evaluated at the fixed response domain ``R=5``.
This module keeps ``R`` explicit, solves the self-consistent endpoint

    V3 * Pi2_TT(R; c) / (32 pi^2) = 4/27,   M_G = M_P * sqrt(pi) / c

for ``c(R)``, and evaluates the three-position bounds.  It is read-only: no
parameter store is written, and no observational value is read.

Radii (different objects; do not conflate):

* ``R = 5`` is the finite response-domain **level** in
  ``q^2 < R*Lambda^2``, not an internal-space radius.
* ``c(5) = kL = 2.493534...`` is the V5 **TT endpoint** internal-radius
  coordinate, the root solved here.
* ``sqrt(2*pi) = 2.506628...`` is the Gaussian correlation window's IR
  **edge**; it is not a TT root (``A`` there is about ``0.147374 < 4/27``).
  Lean's ``CanonicalYangMills`` IR-edge model uses this edge; V5 does not.
* ``sqrt(pi) = 1.772454...`` is the **critical ratio** ``ir/uv``, not an
  endpoint.

The key correction recorded here is that the upper edge of the platform is
the shell-support bound ``R <= 16/pi``, not a crossing
``c(R) = sqrt(15/2)``.  In the production realization ``c(6)`` is still below
``sqrt(15/2)``, so ``c(6)`` cannot be used as the upper certificate.
"""

from __future__ import annotations

import math
from typing import Any

from cg_core.params import get
from cg_core.window_weights import ResponseDomain
from cg_frg.frg.spectral_sum import channel_tmunu_spin2


CRITICAL_RESPONSE = 4.0 / 27.0
FACTOR = 32.0 * math.pi ** 2


def _response(R: float, c: float, tau: float, M_P: float) -> float:
    """Return ``V3 * Pi2_TT(R) / (32 pi^2)`` at the endpoint radius ``c``.

    The self-consistent chain sets ``M_G = M_P * sqrt(pi) / c`` and
    ``L = c`` at ``k = M_G``; hence ``(M_G / M_P)^2 = pi / c^2``.
    """
    if not (math.isfinite(R) and R > 0.0):
        raise ValueError("a positive finite response-domain radius is required")
    if not (math.isfinite(c) and c > 0.0):
        raise ValueError("a positive finite endpoint coordinate is required")
    if not (math.isfinite(tau) and tau >= 0.0):
        raise ValueError("a nonnegative finite torsion modulus is required")
    if not (math.isfinite(M_P) and M_P > 0.0):
        raise ValueError("a positive finite Planck mass is required")

    cutoff = math.pi / (c * c)
    pi0 = channel_tmunu_spin2(
        c, cutoff, tau, domain=ResponseDomain(radius=R)
    )["rp3_pi0"]
    return math.pi ** 2 * c ** 3 * pi0 / FACTOR


def endpoint_coordinate(
    R: float,
    *,
    tau: float | None = None,
    M_P: float | None = None,
    bracket: tuple[float, float] = (2.0, 3.0),
    iterations: int = 96,
) -> float:
    """Solve ``_response(R, c) = 4/27`` for the positive endpoint ``c``.

    The response is monotone decreasing in ``c`` on the production branch;
    the bracket is checked explicitly.  The returned value is a floating-point
    centre, not an interval certificate.

    At ``R=5`` the returned value is the V5 TT endpoint ``kL``.  It is not
    the Gaussian IR edge ``sqrt(2*pi)``; the edge is not a root of this
    equation.
    """
    tau_value = float(get("tau")) if tau is None else float(tau)
    M_P_value = float(get("M_P")) if M_P is None else float(M_P)

    lo, hi = float(bracket[0]), float(bracket[1])
    flo = _response(R, lo, tau_value, M_P_value) - CRITICAL_RESPONSE
    fhi = _response(R, hi, tau_value, M_P_value) - CRITICAL_RESPONSE
    if not (flo > 0.0 and fhi < 0.0):
        raise ValueError(
            f"endpoint bracket does not separate the root at R={R}: "
            f"f({lo})={flo:.6e}, f({hi})={fhi:.6e}"
        )
    for _ in range(int(iterations)):
        mid = 0.5 * (lo + hi)
        fmid = _response(R, mid, tau_value, M_P_value) - CRITICAL_RESPONSE
        if fmid > 0.0:
            lo = mid
            flo = fmid
        else:
            hi = mid
            fhi = fmid
    return 0.5 * (lo + hi)


def response_edge(
    *,
    tau: float | None = None,
    M_P: float | None = None,
    bracket: tuple[float, float] = (4.0, 5.0),
    iterations: int = 64,
) -> float:
    """Solve ``c(R) = sqrt(11/2)`` for the lower platform edge ``R_*``."""
    target = math.sqrt(11.0 / 2.0)
    lo, hi = float(bracket[0]), float(bracket[1])
    clo = endpoint_coordinate(lo, tau=tau, M_P=M_P)
    chi = endpoint_coordinate(hi, tau=tau, M_P=M_P)
    if not (clo < target < chi):
        raise ValueError(
            "the lower platform edge is not bracketed by the requested interval"
        )
    for _ in range(int(iterations)):
        mid = 0.5 * (lo + hi)
        cmid = endpoint_coordinate(mid, tau=tau, M_P=M_P)
        if cmid < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def certificate(
    *,
    tau: float | None = None,
    M_P: float | None = None,
) -> dict[str, Any]:
    """Evaluate the three-position certificate for the finite response domain."""
    tau_value = float(get("tau")) if tau is None else float(tau)
    M_P_value = float(get("M_P")) if M_P is None else float(M_P)

    values = {
        R: endpoint_coordinate(R, tau=tau_value, M_P=M_P_value)
        for R in (4, 5, 6)
    }
    R_star = response_edge(tau=tau_value, M_P=M_P_value)
    c_upper = endpoint_coordinate(16.0 / math.pi, tau=tau_value, M_P=M_P_value)
    first = math.sqrt(11.0 / 2.0)
    second = math.sqrt(15.0 / 2.0)
    upper = 16.0 / math.pi

    checks = {
        "c4_below_first_position": values[4] < first,
        "R_star_between_4_and_5": 4.0 < R_star < 5.0,
        "upper_shell_bound_below_6": upper < 6.0,
        "c5_inside_three_position_platform": first < values[5] < second,
        # Recorded correction: the upper edge is the shell-support bound
        # R <= 16/pi, not the crossing c(R) = sqrt(15/2).
        "c6_above_next_position": values[6] >= second,
        "c_upper_below_next_position": c_upper < second,
    }
    levels = [
        R for R in range(1, 7)
        if R_star < R <= upper
    ]
    return {
        "response_domain": {
            "R": "explicit finite Gaussian domain",
            "weight": "exp(-q^2/Lambda^2)",
            "upper_shell_bound": upper,
        },
        "radii": {
            "response_domain_level": 5,
            "tt_endpoint_at_R5": values[5],
            "gaussian_ir_edge": math.sqrt(2.0 * math.pi),
            "critical_ratio": math.sqrt(math.pi),
            "note": (
                "tt_endpoint_at_R5 is V5's L=kL; gaussian_ir_edge is "
                "Lean's CanonicalYangMills IR-edge model. They are different "
                "scales and must not be substituted for one another."
            ),
        },
        "endpoint_coordinates": {str(R): value for R, value in values.items()},
        "endpoint_at_upper_shell_bound": c_upper,
        "response_edge_R_star": R_star,
        "positions": {
            "sqrt(11/2)": first,
            "sqrt(15/2)": second,
        },
        "checks": checks,
        "integer_levels_in_platform": levels,
        "unique_integer_level": levels[0] if len(levels) == 1 else None,
        "verdict": (
            "R=5 is the unique integer level in (R_*, 16/pi]"
            if levels == [5]
            else "the platform does not select a unique integer level"
        ),
        "upper_certificate": (
            "shell support R <= 16/pi; c(6) < sqrt(15/2), so the c(6) "
            "crossing is NOT an upper certificate"
        ),
        "scope": (
            "floating-point centre values from the production spectral sum; "
            "an outward interval certificate is a separate calculation"
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2, sort_keys=True))
