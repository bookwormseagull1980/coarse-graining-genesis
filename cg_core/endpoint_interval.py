# -*- coding: utf-8 -*-
"""Outward rational enclosure of the finite TT response and its unique root.

For the fixed response domain, matter content and torsion, u=c*omega gives
response(c)=A/c.  The positive coefficient A is integrated once at c=1.
The root c=27*A/4 and derivative -A/c**2 then follow by interval arithmetic.
The scalar, gauge and projected spinor rows are enumerated from their spectra;
the auxiliary TT catalogue is not an additional matter contribution.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import count
from typing import Any

from cg_core.rational_interval import Interval, exp_negative, pi_interval

R_DOMAIN = 5
TAU = Fraction(1, 50)
CRIT = Fraction(4, 27)


def _f(value: Fraction) -> Interval:
    return Interval.point(value)


def _pi() -> Interval:
    return pi_interval()


def _cutoff(c: Interval) -> Interval:
    if c.lo <= 0:
        raise ValueError("strictly positive endpoint required")
    return _pi() / (c * c)


def _check_cells(cells: int) -> None:
    if isinstance(cells, bool) or not isinstance(cells, int) or cells <= 0:
        raise ValueError("cells must be a strictly positive integer")


def _scalar_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = []
    edge = R_DOMAIN * cutoff
    for l in count(0, 2):
        lam = _f(Fraction(l * (l + 2), 1)) / (c * c)
        if lam.lo >= edge.hi:
            break
        m2 = _f(Fraction(3, 4)) / (c * c)
        rows.append((lam, m2, 4 * (l + 1) ** 2, 1))
    return rows


def _gauge_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = []
    edge = R_DOMAIN * cutoff
    tau2 = _f(TAU) * _f(TAU)
    for c2, multiplicity in ((3, 8), (2, 3), (0, 1)):
        for l in count(1, 2):
            lam = _f(Fraction((l + 1) ** 2, 1)) / (c * c)
            if lam.lo >= edge.hi:
                break
            m2 = (_f(Fraction(c2, 2)) + tau2 / _f(Fraction(6, 1))) / (c * c)
            rows.append((lam, m2, multiplicity * 2 * l * (l + 2), 4))
    return rows


def _fermion_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = []
    edge = R_DOMAIN * cutoff
    tau2 = _f(TAU) * _f(TAU)
    m2 = _f(Fraction(3, 8)) * tau2 / (c * c)
    # Three generations: left doublets contribute 24 components on odd n;
    # right singlets contribute 21 components on even n.
    for n in count(0, 2):
        lam = _f(Fraction(4 * n * n + 12 * n + 9, 4)) / (c * c)
        if lam.lo >= edge.hi:
            break
        rows.append((lam, m2, 21 * (n + 1) * (n + 2), 4))
    for n in count(1, 2):
        lam = _f(Fraction(4 * n * n + 12 * n + 9, 4)) / (c * c)
        if lam.lo >= edge.hi:
            break
        rows.append((lam, m2, 24 * (n + 1) * (n + 2), 4))
    return rows


def _f_value(u: Interval, lam: Interval, m2: Interval,
             cutoff: Interval) -> Interval:
    q = u * u + lam
    den = q + m2
    return (q / den) ** 2 * exp_negative(q / cutoff)


def _f_second_derivative(u: Interval, lam: Interval, m2: Interval,
                         cutoff: Interval) -> Interval:
    """Outward enclosure of d^2/du^2 of the TT integrand."""
    q = u * u + lam
    den = q + m2
    q1 = 2 * u
    q2 = Interval.point(2)
    d1 = q1
    d2 = q2
    r = (q / den) ** 2
    r1 = 2 * q * q1 / (den ** 2) - 2 * (q ** 2) * d1 / (den ** 3)
    r2 = (
        2 * (q1 ** 2 + q * q2) / (den ** 2)
        - 8 * q * q1 * d1 / (den ** 3)
        - 2 * (q ** 2) * d2 / (den ** 3)
        + 6 * (q ** 2) * (d1 ** 2) / (den ** 4)
    )
    g = exp_negative(q / cutoff)
    g1 = -(q1 / cutoff) * g
    g2 = ((q1 / cutoff) ** 2 - q2 / cutoff) * g
    return r2 * g + 2 * r1 * g1 + r * g2


def _cell_integral(lam: Interval, m2: Interval, cutoff: Interval,
                   cells: int) -> Interval:
    """Enclose (1/pi) int K exp(-q^2/cutoff) dw.

    Composite trapezoid plus an outward second-derivative bound:
    on a cell of width h the error is at most max|F''| h^3/12.
    The square-root enclosure of the upper limit contributes its own cap
    error.  Adjacent trapezoids share their endpoint evaluation.
    """
    _check_cells(cells)
    omega2 = R_DOMAIN * cutoff - lam
    if omega2.hi <= 0:
        return Interval.point(0)
    omega = omega2.sqrt()
    if omega.hi <= 0:
        return Interval.point(0)
    total = Interval.point(0)
    f0 = _f_value(Interval.point(0), lam, m2, cutoff)
    for j in range(cells):
        wlo = omega.hi * j // cells
        whi = omega.hi * (j + 1) // cells
        if wlo == whi:
            continue
        f1 = _f_value(Interval(whi, whi), lam, m2, cutoff)
        h = Interval(whi - wlo, whi - wlo)
        trapezoid = (f0 + f1) * h / 2
        second = _f_second_derivative(
            Interval(wlo, whi), lam, m2, cutoff)
        m2bound = Interval(max(abs(second.lo), abs(second.hi)),
                          max(abs(second.lo), abs(second.hi)))
        error = m2bound * (h ** 3) / 12
        total = total + trapezoid + Interval(-error.hi, error.hi)
        f0 = f1
    # 0<=integrand<=1: integration to omega.hi overestimates the true
    # interval by at most omega.hi-omega.lo, before division by pi.
    total = Interval(total.lo - (omega.hi - omega.lo), total.hi)
    return total / _pi()


def _mode_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = (
        _scalar_rows(c, cutoff)
        + _gauge_rows(c, cutoff)
        + _fermion_rows(c, cutoff)
    )
    edge = R_DOMAIN * cutoff
    for lam, _m2, _deg, _weight in rows:
        if not lam.hi < edge.lo:
            raise ValueError("mode threshold lies inside the derivative interval")
    return rows


@lru_cache(maxsize=8, typed=True)
def coefficient_interval(*, cells: int = 256) -> Interval:
    """Enclose A using the actual finite spectrum at the reference scale.

    u=c*omega removes c from every eigenvalue, mass shift and integration
    edge.  Positive spectral thresholds are checked at this scale, so no
    moving-boundary derivative or new quadrature is needed at another c.
    """
    _check_cells(cells)
    reference = Interval.point(1)
    cutoff = _cutoff(reference)
    total = Interval.point(0)
    for lam, m2, deg, weight in _mode_rows(reference, cutoff):
        total = total + deg * weight * _cell_integral(lam, m2, cutoff, cells)
    return total / (32 * _pi() * _pi())


def response_derivative_interval(c: Interval, *, cells: int = 256) -> Interval:
    """Enclose -A/c**2, including the complete frequency-boundary motion."""
    if c.lo <= 0:
        raise ValueError("strictly positive endpoint required")
    return -coefficient_interval(cells=cells) / (c * c)


def response_interval(c: Fraction | int | float, *, cells: int = 256) -> Interval:
    """Enclose V3 Pi2/(32*pi**2)=A/c at a strictly positive endpoint."""
    cq = c if isinstance(c, Fraction) else Fraction(str(c))
    c_iv = _f(cq)
    if c_iv.lo <= 0:
        raise ValueError("strictly positive endpoint required")
    return coefficient_interval(cells=cells) / c_iv


def certify_uniqueness(c_lo: Fraction, c_hi: Fraction,
                       *, cells: int = 256) -> dict[str, Any]:
    """Prove one derivative sign on [c_lo,c_hi] with outward intervals."""
    if c_lo <= 0 or c_hi <= c_lo:
        raise ValueError("ordered strictly positive bracket required")
    c_iv = Interval.bounds(c_lo, c_hi)
    derivative = response_derivative_interval(c_iv, cells=cells)
    if derivative.hi < 0:
        sign = "negative"
        unique = True
    elif derivative.lo > 0:
        sign = "positive"
        unique = True
    else:
        sign = "undetermined"
        unique = False
    return {
        "status": "PASS" if unique else "FAIL",
        "derivative": derivative.decimal_bounds(),
        "sign": sign,
        "unique_on_bracket": unique,
        "cells": cells,
        "identity": "response(c)=A/c; derivative=-A/c^2; A>0",
    }


def certify_root(c_lo: Fraction = Fraction(23, 10),
                 c_hi: Fraction = Fraction(26, 10),
                 *, cells: int = 256) -> dict[str, Any]:
    """Enclose c=27*A/4 from one quadrature and certify a sign bracket."""
    if c_lo <= 0 or c_hi <= c_lo:
        raise ValueError("ordered strictly positive bracket required")
    coefficient = coefficient_interval(cells=cells)
    root = Fraction(27, 4) * coefficient
    if coefficient.lo <= 0:
        raise ValueError("coefficient enclosure must be strictly positive")
    if not (response_interval(c_lo, cells=cells).lo > _f(CRIT).hi
            and response_interval(c_hi, cells=cells).hi < _f(CRIT).lo):
        raise ValueError("initial bracket does not separate the response from 4/27")
    # Round outwards and leave a rational margin for strict endpoint signs.
    step = Fraction(1, 10**12)
    root_lo, root_hi = map(Fraction, root.decimal_bounds(12))
    lo, hi = max(c_lo, root_lo-step), min(c_hi, root_hi+step)
    left = response_interval(lo, cells=cells)
    right = response_interval(hi, cells=cells)
    existence = left.lo > _f(CRIT).hi and right.hi < _f(CRIT).lo
    uniqueness = certify_uniqueness(lo, hi, cells=cells)
    reference_rows = _mode_rows(Interval.point(1), _pi())
    return {
        "schema_version": 1,
        "status": "PASS" if existence and uniqueness["status"] == "PASS" else "FAIL",
        "bracket": [str(lo), str(hi)],
        "bracket_decimal": [float(lo), float(hi)],
        "response_left": left.decimal_bounds(),
        "response_right": right.decimal_bounds(),
        "critical": "4/27",
        "cells": cells,
        "coefficient": coefficient.decimal_bounds(40),
        "root_enclosure": root.decimal_bounds(40),
        "method": "reference-scale composite trapezoid with cellwise second-derivative bounds",
        "arithmetic_grid": "1e-40",
        "work": {
            "spectral_rows": len(reference_rows),
            "quadrature_cells": len(reference_rows)*cells,
            "exponential_enclosures": len(reference_rows)*(2*cells+1),
            "coefficient_evaluations": 1,
            "additional_derivative_quadratures": 0,
        },
        "uniqueness": uniqueness,
        "scope": (
            "strict root existence and uniqueness on the bracket"
            if existence and uniqueness["status"] == "PASS"
            else "root existence only; uniqueness not certified"
        ),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certify_root(cells=512), indent=2, default=str))
