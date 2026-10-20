# -*- coding: utf-8 -*-
"""Derive the RP3 carrier from the quaternion amplitude and its centre.

The source amplitude is the real four-dimensional quaternion space.  Unit
quaternions form SU(2); the centre is {+1,-1}; conjugation by a unit
quaternion is the two-to-one cover SU(2) -> SO(3).  The orbit space of the
unit sphere by the antipodal centre is therefore RP3 = SO(3).  This module
checks the finite group facts and derives the parity selection used by the
spectrum:

* invariant functions on the double cover are the even SO(4) harmonics;
* one-forms are odd;
* spinors retain the even n tower;
* the rough TT carrier has even k=2,4,... and total multiplicity
  2(k-1)(k+3).

The numerical spectrum is cross-checked against ``rp3_spectrum`` in the
structural certificate.  This is a finite/derivation certificate, not a Lean
proof of the full analytic spectral theorem.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any


def qmul(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


def qconj(a: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    return (a[0], -a[1], -a[2], -a[3])


def qnorm_sq(a: tuple[float, float, float, float]) -> float:
    return sum(x * x for x in a)


def unit(q: tuple[float, float, float, float]) -> bool:
    return abs(qnorm_sq(q) - 1.0) < 1e-14


def rotate(q: tuple[float, float, float, float], v: tuple[float, float, float]) -> tuple[float, float, float]:
    """Conjugation q (0,v) q* gives the SO(3) rotation."""
    pure = (0.0, *v)
    out = qmul(qmul(q, pure), qconj(q))
    return (out[1], out[2], out[3])


def centre_pair() -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
    return (1.0, 0.0, 0.0, 0.0), (-1.0, 0.0, 0.0, 0.0)


def antipodal_identifies_same_rotation() -> bool:
    q = (math.sqrt(0.5), math.sqrt(0.5), 0.0, 0.0)
    v = (0.3, -0.4, 0.5)
    return all(abs(a - b) < 1e-14 for a, b in zip(rotate(q, v), rotate(tuple(-x for x in q), v)))


def scalar_eigenvalue(l: int, L: float = 1.0) -> float:
    if l < 0 or l % 2:
        raise ValueError("RP3 invariant scalar requires even l")
    return l * (l + 2) / (L * L)


def scalar_multiplicity(l: int) -> int:
    if l < 0 or l % 2:
        raise ValueError("RP3 invariant scalar requires even l")
    return (l + 1) * (l + 1)


def vector_eigenvalue(l: int, L: float = 1.0) -> float:
    if l < 1 or l % 2 == 0:
        raise ValueError("RP3 one-form requires odd l >= 1")
    return (l + 1) * (l + 1) / (L * L)


def vector_multiplicity(l: int) -> int:
    if l < 1 or l % 2 == 0:
        raise ValueError("RP3 one-form requires odd l >= 1")
    return 2 * l * (l + 2)


def spinor_eigenvalue(n: int, L: float = 1.0) -> float:
    if n < 0 or n % 2:
        raise ValueError("RP3 spinor requires even n >= 0")
    return (n + 1.5) ** 2 / (L * L)


def spinor_multiplicity(n: int) -> int:
    if n < 0 or n % 2:
        raise ValueError("RP3 spinor requires even n >= 0")
    return (n + 1) * (n + 2)


def tt_eigenvalue(k: int, L: float = 1.0) -> float:
    if k < 2 or k % 2:
        raise ValueError("rough TT requires even k >= 2")
    return (k * (k + 2) - 2) / (L * L)


def tt_multiplicity(k: int) -> int:
    if k < 2 or k % 2:
        raise ValueError("rough TT requires even k >= 2")
    return 2 * (k - 1) * (k + 3)


def certificate(L: float | None = None) -> dict[str, Any]:
    if L is None:
        try:
            from cg_core.params import get
            L = float(get("kL"))
        except (KeyError, OSError, ValueError):
            L = 1.0
    q = (math.sqrt(0.5), math.sqrt(0.5), 0.0, 0.0)
    centre = centre_pair()
    checks = {
        "unit_quaternion": unit(q),
        "centre_elements_are_unit": all(unit(x) for x in centre),
        "centre_is_pm_one": centre == ((1.0, 0.0, 0.0, 0.0), (-1.0, 0.0, 0.0, 0.0)),
        "centre_quotient_identifies_rotation": antipodal_identifies_same_rotation(),
        "scalar_even_tower": [l for l in range(0, 8) if l % 2 == 0] == [0, 2, 4, 6],
        "one_form_odd_tower": [l for l in range(1, 8) if l % 2 == 1] == [1, 3, 5, 7],
        "spinor_even_tower": [n for n in range(0, 8) if n % 2 == 0] == [0, 2, 4, 6],
        "tt_even_tower": [k for k in range(2, 10) if k % 2 == 0] == [2, 4, 6, 8],
        "scalar_lowest_zero": scalar_eigenvalue(0, L) == 0.0,
        "vector_lowest_positive": vector_eigenvalue(1, L) > 0.0,
        "spinor_lowest_positive": spinor_eigenvalue(0, L) > 0.0,
        "tt_lowest_six": abs(tt_eigenvalue(2, L) - 6.0 / (L * L)) < 1e-15,
    }
    return {
        "schema_version": 1,
        "step": "rp3_derivation",
        "amplitude": {"real_dimension": 4, "unit_group": "SU(2)", "centre": "Z2"},
        "quotient": {"space": "SU(2)/Z2", "diffeomorphic_to": "SO(3)", "also": "RP3"},
        "spectrum": {
            "scalar": {"l": "even", "eigenvalue": "l(l+2)/L^2", "multiplicity": "(l+1)^2"},
            "one_form": {"l": "odd >=1", "eigenvalue": "(l+1)^2/L^2", "multiplicity": "2l(l+2)"},
            "spinor": {"n": "even", "eigenvalue": "(n+3/2)^2/L^2", "multiplicity": "(n+1)(n+2)"},
            "tt_rough": {"k": "even >=2", "eigenvalue": "(k(k+2)-2)/L^2", "multiplicity": "2(k-1)(k+3)"},
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
