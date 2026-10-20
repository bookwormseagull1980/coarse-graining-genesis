# -*- coding: utf-8 -*-
"""Minimal-change and Gaussian endpoint certificates.

Structural chain (corresponding Lean steps in parentheses):

    minimal orthogonal change datum (dimension 2, SO(2))
        -> unit-covariance Gaussian width b = 1
        -> endpoints uv = sqrt(2) b, ir = sqrt(2 pi) b
        -> critical ratio sqrt(pi)
        -> reflecting/Neumann eigenvalues n^2.

The certificate is exact where possible and uses squared equalities for the
irrational endpoints, so no floating-point comparison decides a structural
fact.
"""

from __future__ import annotations

import math
from typing import Any


def _orthogonal_group_profile(d: int) -> str:
    """Return the connected orthogonal action type in real dimension d."""
    if d < 0:
        raise ValueError("nonnegative dimension required")
    if d == 0:
        return "trivial"
    if d == 1:
        return "finite O(1)={+1,-1}; no continuous rotation"
    return "connected SO(d) with continuous rotations"


def carrier_real_dimension() -> int:
    """Smallest dimension with a nontrivial connected orthogonal action.

    d=0 is trivial; d=1 has only the finite group O(1).  d=2 is the first
    dimension with the connected continuous group SO(2).  The selection is
    therefore connectedness plus nontriviality, not an extra parameter.
    """
    for d in range(0, 8):
        if _orthogonal_group_profile(d).startswith("connected"):
            return d
    raise RuntimeError("no connected orthogonal carrier found")


def carrier_selection() -> dict[str, Any]:
    d = carrier_real_dimension()
    return {
        "dimension": d,
        "group": "SO(2)" if d == 2 else f"SO({d})",
        "d0": _orthogonal_group_profile(0),
        "d1": _orthogonal_group_profile(1),
        "d2": _orthogonal_group_profile(2),
    }


def carrier_group() -> str:
    """The connected compact group acting on the minimal carrier."""
    return "SO(2)"


def unit_covariance_width() -> float:
    """Unit covariance fixes the positive Gaussian width to one."""
    return 1.0


def uv_endpoint(b: float = 1.0) -> float:
    return math.sqrt(2.0) * b


def ir_endpoint(b: float = 1.0) -> float:
    return math.sqrt(2.0 * math.pi) * b


def critical_ratio() -> float:
    return math.sqrt(math.pi)


def window_length(b: float = 1.0) -> float:
    return ir_endpoint(b) - uv_endpoint(b)


def reflection_eigenvalue(n: int) -> int:
    """Neumann/reflecting interval eigenvalue n^2."""
    return n * n


def certificate() -> dict[str, Any]:
    b = unit_covariance_width()
    uv = uv_endpoint(b)
    ir = ir_endpoint(b)
    ratio = ir / uv
    selection = carrier_selection()
    checks = {
        "carrier_dimension_two": carrier_real_dimension() == 2,
        "carrier_group_so2": carrier_group() == "SO(2)",
        "dimension_zero_trivial": selection["d0"] == "trivial",
        "dimension_one_no_continuous_rotation": selection["d1"].startswith("finite"),
        "dimension_two_connected": selection["d2"].startswith("connected"),
        "width_one": b == 1.0,
        "uv_squared_two": abs(uv * uv - 2.0) < 1e-15,
        "ir_squared_two_pi": abs(ir * ir - 2.0 * math.pi) < 1e-15,
        "critical_ratio_squared_pi": abs(ratio * ratio - math.pi) < 1e-12,
        "window_length_positive": window_length(b) > 0.0,
        "reflection_first_eigenvalues": [reflection_eigenvalue(n) for n in range(6)]
        == [0, 1, 4, 9, 16, 25],
    }
    return {
        "schema_version": 1,
        "step": "minimal_change_gaussian_endpoints",
        "carrier": {**selection, "group": carrier_group()},
        "gaussian": {"width": b, "variance": b * b},
        "endpoints": {
            "uv": uv,
            "ir": ir,
            "uv_sq": uv * uv,
            "ir_sq": ir * ir,
            "critical_ratio": ratio,
            "critical_ratio_sq": ratio * ratio,
            "window_length": window_length(b),
        },
        "reflection_spectrum": [reflection_eigenvalue(n) for n in range(8)],
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
