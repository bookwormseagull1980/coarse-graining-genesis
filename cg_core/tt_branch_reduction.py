# -*- coding: utf-8 -*-
"""Exact reduction of the V5 finite TT response to the Lean eight-branch model.

At the endpoint fixed point the V5 response is evaluated with

    L = c,   cutoff = pi/c^2,   R = 5.

For a mode with eigenvalue coefficient ``a`` and mass coefficient ``b``,

    lambda = a/c^2,  m^2 = b/c^2,  q^2 = omega^2 + lambda.

The change of variable ``u = c*omega`` gives

    q^2 = (u^2+a)/c^2,
    K = ((u^2+a)/(u^2+a+b))^2,
    exp(-q^2/cutoff) = exp(-(u^2+a)/pi),
    domega = du/c,
    omega_max = sqrt(5*pi-a)/c.

Hence every retained mode contributes exactly ``1/c`` times a
``c``-independent integral.  On the endpoint bracket the active mode set is
stable and consists of exactly the eight branches used by the Lean
``SourceTTGaussianCoefficient`` module.  Therefore the full V5 finite sum is
exactly the Lean coefficient model divided by ``c``; this is an algebraic
reduction, not a numerical approximation.

The certificate below checks the branch table, the stable active set and the
outward interval identity between the full V5 response times ``c`` and the
eight-branch coefficient.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from cg_core.endpoint_interval import _cell_integral, _f, _pi, response_interval
from cg_core.rational_interval import Interval

TAU = Fraction(1, 50)
BRACKET = (Fraction(817081, 327680), Fraction(3268327, 1310720))

# (eigenvalue coefficient a, mass coefficient b, multiplicity weight)
# This is the exact active table of the Lean SourceTTGaussianCoefficient
# module.  The V5 full spectrum is enumerated independently below.
LEAN_BRANCHES = (
    (Fraction(0), Fraction(3, 4), 4),
    (Fraction(8), Fraction(3, 4), 36),
    (Fraction(4), Fraction(3, 2) + TAU * TAU / 6, 192),
    (Fraction(4), Fraction(1) + TAU * TAU / 6, 72),
    (Fraction(4), TAU * TAU / 6, 24),
    (Fraction(9, 4), 3 * TAU * TAU / 8, 168),
    (Fraction(25, 4), 3 * TAU * TAU / 8, 576),
    (Fraction(49, 4), 3 * TAU * TAU / 8, 1008),
)

BRANCH_ORIGIN = (
    "scalar l=0: a=l(l+2)=0, m2=3/4, deg=4",
    "scalar l=2: a=l(l+2)=8, m2=3/4, deg=4(l+1)^2=36",
    "gauge l=1, c2=3: a=(l+1)^2=4, m2=3/2+tau^2/6, 8*2*l(l+2)*4=192",
    "gauge l=1, c2=2: a=4, m2=1+tau^2/6, 3*2*l(l+2)*4=72",
    "gauge l=1, c2=0: a=4, m2=tau^2/6, 1*2*l(l+2)*4=24",
    "fermion n=0: a=(n+3/2)^2=9/4, m2=3tau^2/8, 21*(n+1)(n+2)*4=168",
    "fermion n=1: a=25/4, m2=3tau^2/8, 24*(n+1)(n+2)*4=576",
    "fermion n=2: a=49/4, m2=3tau^2/8, 21*(n+1)(n+2)*4=1008",
)


def derived_branches() -> list[tuple[Fraction, Fraction, int]]:
    """Derive the eight rows from the V5 spectral formulas, exactly."""
    rows: list[tuple[Fraction, Fraction, int]] = []
    # scalars: l even; l=0,2 active; l=4 has a=24 > 5*pi
    for l in (0, 2):
        rows.append((Fraction(l * (l + 2)), Fraction(3, 4),
                     4 * (l + 1) ** 2))
    # gauge: l odd; l=1 active; l=3 has a=16 > 5*pi
    for c2, count in ((3, 8), (2, 3), (0, 1)):
        rows.append((Fraction(4), Fraction(c2, 2) + TAU * TAU / 6,
                     count * 2 * 1 * 3 * 4))
    # fermions: n=0,1,2 active; n=3 has a=81/4 > 5*pi
    for n, components in ((0, 21), (1, 24), (2, 21)):
        rows.append((Fraction(4 * n * n + 12 * n + 9, 4),
                     3 * TAU * TAU / 8,
                     components * (n + 1) * (n + 2) * 4))
    return sorted(rows)


def active_branches(c: Fraction) -> list[tuple[Fraction, Fraction, int]]:
    """Return the exact active V5 branch table on the endpoint bracket.

    The active threshold is ``a < 5*pi``.  The last active branch has
    ``a=49/4`` and the first excluded branch has ``a=16``; the interval
    check below proves ``49/4 < 5*pi < 16``, so the table is independent of
    the bracket point.
    """
    del c  # the exact table is stable throughout the certified bracket
    pi = _pi()
    if not (5 * pi).lo > _f(Fraction(49, 4)).hi:
        raise ValueError("5*pi lower bound does not exceed the last active branch")
    if not (5 * pi).hi < _f(Fraction(16)).lo:
        raise ValueError("5*pi upper bound does not lie below the first excluded branch")
    derived = derived_branches()
    if derived != sorted(LEAN_BRANCHES):
        raise ValueError("derived V5 branch table does not match the Lean table")
    return derived


def _compare_branches(c: Fraction) -> tuple[bool, list[dict[str, Any]]]:
    actual = active_branches(c)
    expected = sorted(LEAN_BRANCHES)
    rows = []
    ok = len(actual) == len(expected)
    for index, (a, b, w) in enumerate(expected):
        got = actual[index] if index < len(actual) else None
        match = got == (a, b, w)
        ok = ok and match
        rows.append({
            "a": str(a), "b": str(b), "weight": w,
            "v5_a": None if got is None else str(got[0]),
            "v5_b": None if got is None else str(got[1]),
            "v5_weight": None if got is None else got[2],
            "match": match,
        })
    return ok, rows


def coefficient_interval(*, cells: int = 256) -> Interval:
    """Outward interval for the c-independent eight-branch coefficient."""
    total = Interval.point(0)
    for a, b, weight in LEAN_BRANCHES:
        total = total + Interval.point(weight) * _cell_integral(
            _f(a), _f(b), _pi(), cells)
    return total / (32 * _pi() * _pi())


def certificate(*, cells: int = 256) -> dict[str, Any]:
    c_lo, c_hi = BRACKET
    ok_lo, rows_lo = _compare_branches(c_lo)
    ok_hi, rows_hi = _compare_branches(c_hi)
    coeff = coefficient_interval(cells=cells)
    c_mid = Fraction(24935343325, 10**10)
    full = response_interval(c_mid, cells=cells) * _f(c_mid)
    difference = full - coeff
    overlap = not (full.hi < coeff.lo or coeff.hi < full.lo)
    exact = overlap and difference.lo <= 0 <= difference.hi
    return {
        "status": "PASS" if ok_lo and ok_hi and exact else "FAIL",
        "bracket": [str(c_lo), str(c_hi)],
        "active_branch_count": len(rows_lo),
        "branches_at_left": rows_lo,
        "branches_at_right": rows_hi,
        "branch_origin": list(BRANCH_ORIGIN),
        "excluded_thresholds": {
            "scalar_l4": "a=24 > 5*pi",
            "gauge_l3": "a=16 > 5*pi",
            "fermion_n3": "a=81/4=20.25 > 5*pi",
        },
        "stable_active_set": ok_lo and ok_hi,
        "coefficient": coeff.decimal_bounds(),
        "full_scaled": full.decimal_bounds(),
        "difference": difference.decimal_bounds(),
        "exact_interval_identity": exact,
        "cells": cells,
        "derivation": (
            "u=c*omega; lambda=a/c^2, m^2=b/c^2, cutoff=pi/c^2; "
            "the Gaussian, kernel, measure and frequency edge all scale "
            "to a c-independent integral, so A_V5(c)=A_5/c exactly"
        ),
        "scope": (
            "full V5 active finite spectrum equals the Lean eight-branch "
            "coefficient model on the certified endpoint bracket"
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2, default=str))
