# -*- coding: utf-8 -*-
"""Derive the gauge matching condition from effective-action continuity.

For a quadratic gauge term written as

    S_gauge = - Z/(4 g^2) int F^2,

the physical gauge field is normalized by Z.  Matching across a threshold
requires the coefficient of F^2 to be continuous:

    Z_before / g_before^2 = Z_after / g_after^2,

hence

    g_after = g_before * sqrt(Z_after / Z_before).

This is a condition on the matching map, not a fitted number.  Mass and
Yukawa matching remain scheme-dependent and are stated separately.
"""

from __future__ import annotations

import math
from typing import Any


def gauge_matching(g_before: float, z_before: float, z_after: float) -> float:
    if not all(math.isfinite(x) and x > 0 for x in (g_before, z_before, z_after)):
        raise ValueError("positive finite gauge coupling and wavefunction factors required")
    return g_before * math.sqrt(z_after / z_before)


def certificate(g_before: float = 0.5, z_before: float = 1.0,
                z_after: float = 1.2) -> dict[str, Any]:
    g_after = gauge_matching(g_before, z_before, z_after)
    checks = {
        "positive_g_after": g_after > 0.0,
        "action_coefficient_continuous": math.isclose(
            z_before / g_before ** 2, z_after / g_after ** 2, rel_tol=1e-15),
        "identity_when_z_unchanged": math.isclose(
            gauge_matching(g_before, z_before, z_before), g_before, rel_tol=1e-15),
    }
    return {
        "schema_version": 1,
        "step": "gauge_matching_derivation",
        "condition": "Z_before/g_before^2 = Z_after/g_after^2",
        "g_before": g_before,
        "g_after": g_after,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
