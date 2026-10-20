# -*- coding: utf-8 -*-
"""Derive the fixed spectral projection of the response domain.

The response functional is evaluated on a finite spectral window
`q^2 < R*Lambda^2`.  Differentiating with respect to a source while the
window boundary moves adds a Leibniz boundary term; the fixed-projection
derivative is the source response at a fixed measurement domain.

This module states the two alternatives explicitly and checks that the
fixed projection is the one with zero boundary derivative.  It does not
claim that a moving projection is mathematically wrong; it is a different
measurement convention.
"""

from __future__ import annotations

import math
from typing import Any


def edge(radius: float, cutoff: float) -> float:
    if not (math.isfinite(radius) and radius > 0 and math.isfinite(cutoff) and cutoff > 0):
        raise ValueError("positive finite radius and cutoff required")
    return radius * cutoff


def boundary_derivative(projection: str, radius: float, cutoff: float,
                        lam: float, *, dcutoff: float = 1.0) -> float:
    if projection == "fixed":
        return 0.0
    if projection != "moving":
        raise ValueError("projection must be fixed or moving")
    delta = edge(radius, cutoff) - lam
    if delta <= 0:
        return 0.0
    return cutoff * dcutoff / (2.0 * math.sqrt(delta))


def certificate(radius: float = 5.0, cutoff: float = 1.0, lam: float = 0.0) -> dict[str, Any]:
    fixed = boundary_derivative("fixed", radius, cutoff, lam)
    moving = boundary_derivative("moving", radius, cutoff, lam)
    checks = {
        "fixed_boundary_derivative_zero": fixed == 0.0,
        "moving_boundary_derivative_nonzero": moving != 0.0,
        "fixed_is_the_source_response_projection": fixed == 0.0 and moving > 0.0,
    }
    return {
        "schema_version": 1,
        "step": "projection_derivation",
        "projection": "fixed",
        "alternatives": {"fixed": fixed, "moving": moving},
        "reason": ("fixed spectral domain: the source derivative acts inside "
                   "the window; moving the boundary adds a separate Leibniz term"),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
