# -*- coding: utf-8 -*-
"""Outward interval enclosure of the V5 TT endpoint response.

This module is the first step of the strict endpoint programme:

* the finite RP3 spectrum is enumerated explicitly (scalars, gauge fields,
  fermions; the TT catalogue is excluded from the Tmunu spin-2 weight);
* each Gaussian frequency integral is enclosed by monotone cell envelopes;
* the finite mode sum is enclosed with outward rational interval arithmetic;
* a sign-changing bracket gives a rigorous root-existence certificate;
* an interval derivative bound on the same bracket gives uniqueness.

The response and its derivative are evaluated with outward rational intervals.
The derivative must have one definite sign across the bracket; the mode set is
checked to be stable there (no shell-threshold crossing).
"""

from __future__ import annotations

import math
from fractions import Fraction
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
    return _pi() / (c * c)


def _scalar_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = []
    edge = R_DOMAIN * cutoff
    max_l = int(math.sqrt(float(edge.hi) / 1e-40)) + 4
    for l in range(0, max_l + 1, 2):
        lam = _f(Fraction(l * (l + 2), 1)) / (c * c)
        if lam.lo >= edge.hi:
            break
        m2 = _f(Fraction(3, 4)) / (c * c)
        rows.append((lam, m2, 4 * (l + 1) ** 2, 1))
    return rows


def _gauge_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = []
    edge = R_DOMAIN * cutoff
    max_l = int(math.sqrt(float(edge.hi) / 1e-40)) + 4
    tau2 = _f(TAU) * _f(TAU)
    for c2, count in ((3, 8), (2, 3), (0, 1)):
        for l in range(1, max_l + 1, 2):
            lam = _f(Fraction((l + 1) ** 2, 1)) / (c * c)
            if lam.lo >= edge.hi:
                break
            m2 = (_f(Fraction(c2, 2)) + tau2 / _f(Fraction(6, 1))) / (c * c)
            rows.append((lam, m2, count * 2 * l * (l + 2), 4))
    return rows


def _fermion_rows(c: Interval, cutoff: Interval) -> list[tuple[Interval, Interval, int, int]]:
    rows = []
    edge = R_DOMAIN * cutoff
    max_n = int(math.sqrt(float(edge.hi) / 1e-40)) + 4
    tau2 = _f(TAU) * _f(TAU)
    m2 = _f(Fraction(3, 8)) * tau2 / (c * c)
    # Three generations: left doublets contribute 24 components on odd n;
    # right singlets contribute 21 components on even n.
    for n in range(0, max_n + 1, 2):
        lam = _f(Fraction(4 * n * n + 12 * n + 9, 4)) / (c * c)
        if lam.lo >= edge.hi:
            break
        rows.append((lam, m2, 21 * (n + 1) * (n + 2), 4))
    for n in range(1, max_n + 1, 2):
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
    """
    omega2 = R_DOMAIN * cutoff - lam
    if omega2.hi <= 0:
        return Interval.point(0)
    omega = omega2.sqrt()
    if omega.hi <= 0:
        return Interval.point(0)
    width = max(1, omega.hi // max(1, cells))
    count = omega.hi // width
    if count * width < omega.hi:
        count += 1
    total = Interval.point(0)
    for j in range(count):
        wlo = j * width
        whi = min((j + 1) * width, omega.hi)
        if wlo >= omega.hi:
            break
        f0 = _f_value(Interval(wlo, wlo), lam, m2, cutoff)
        f1 = _f_value(Interval(whi, whi), lam, m2, cutoff)
        h = Interval(whi - wlo, whi - wlo)
        trapezoid = (f0 + f1) * h / 2
        second = _f_second_derivative(
            Interval(wlo, whi), lam, m2, cutoff)
        m2bound = Interval(max(abs(second.lo), abs(second.hi)),
                          max(abs(second.lo), abs(second.hi)))
        error = m2bound * (h ** 3) / 12
        total = total + trapezoid + Interval(-error.hi, error.hi)
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


def _cell_integral_derivative(lam: Interval, m2: Interval, cutoff: Interval,
                              c: Interval, cells: int) -> Interval:
    """Enclose d/dc of (1/pi) int K exp(-q^2/cutoff) dw on one cell row."""
    dlam = -2 * lam / c
    dm2 = -2 * m2 / c
    dcut = -2 * cutoff / c
    omega2 = R_DOMAIN * cutoff - lam
    if omega2.hi <= 0:
        return Interval.point(0)
    omega = omega2.sqrt()
    if omega.lo <= 0:
        return Interval.point(0)
    domega = (5 * dcut - dlam) / (2 * omega)
    width = max(1, omega.hi // max(1, cells))
    count = omega.hi // width
    if count * width < omega.hi:
        count += 1
    total = Interval.point(0)
    for j in range(count):
        wlo = j * width
        whi = min((j + 1) * width, omega.hi)
        if wlo >= omega.hi:
            break
        w_lo = Interval(wlo, wlo)
        w_hi = Interval(whi, whi)
        q2_lo = w_lo * w_lo + Interval(lam.lo, lam.lo)
        q2_hi = w_hi * w_hi + Interval(lam.hi, lam.hi)
        den_lo = q2_lo + Interval(m2.hi, m2.hi)
        den_hi = q2_hi + Interval(m2.lo, m2.lo)
        if den_lo.lo <= 0 or den_hi.lo <= 0:
            continue
        q2 = Interval(q2_lo.lo, q2_hi.hi)
        den = Interval(q2_lo.lo + m2.lo, q2_hi.hi + m2.hi)
        k_lo = (q2_lo / den_lo) ** 2
        k_hi = (q2_hi / den_hi) ** 2
        k_iv = Interval(k_lo.lo, k_hi.hi)
        g_lo = exp_negative(q2_hi / Interval(cutoff.lo, cutoff.lo))
        g_hi = exp_negative(q2_lo / Interval(cutoff.hi, cutoff.hi))
        g_iv = Interval(g_lo.lo, g_hi.hi)
        dden = dlam + dm2
        dk = 2 * q2 * dlam / (den ** 2) - 2 * (q2 ** 2) * dden / (den ** 3)
        dg = -g_iv * (dlam / cutoff - q2 * dcut / (cutoff * cutoff))
        df = dk * g_iv + k_iv * dg
        total = total + df * Interval(whi - wlo, whi - wlo)
    # Leibniz boundary term, evaluated at q^2 = 5*cutoff.
    q2b = R_DOMAIN * cutoff
    denb = q2b + m2
    kb = (q2b / denb) ** 2
    gb = exp_negative(_f(5))
    dq2b = R_DOMAIN * dcut
    dkb = 2 * kb * (dq2b / q2b - (dq2b + dm2) / denb)
    dgb = -gb * (dq2b / cutoff - q2b * dcut / (cutoff * cutoff))
    boundary = (dkb * gb + kb * dgb) * domega
    total = total + boundary
    return total / _pi()


def response_derivative_interval(c: Interval, *, cells: int = 256) -> Interval:
    """Outward enclosure of d/dc of the finite TT response on an interval c."""
    cutoff = _cutoff(c)
    total = Interval.point(0)
    for lam, m2, deg, weight in _mode_rows(c, cutoff):
        total = total + Interval.point(deg * weight) * _cell_integral_derivative(
            lam, m2, cutoff, c, cells)
    return total / (32 * _pi() * _pi())


def response_interval(c: Fraction | int | float, *, cells: int = 256) -> Interval:
    """Outward enclosure of V3 Pi2(Tmunu spin-2)/(32 pi^2) at endpoint c."""
    cq = c if isinstance(c, Fraction) else Fraction(str(c))
    c_iv = _f(cq)
    cutoff = _cutoff(c_iv)
    total = Interval.point(0)
    for lam, m2, deg, weight in (
        _scalar_rows(c_iv, cutoff)
        + _gauge_rows(c_iv, cutoff)
        + _fermion_rows(c_iv, cutoff)
    ):
        total = total + Interval.point(deg * weight) * _cell_integral(
            lam, m2, cutoff, cells)
    return total / (32 * _pi() * _pi())


def certify_uniqueness(c_lo: Fraction, c_hi: Fraction,
                       *, cells: int = 256) -> dict[str, Any]:
    """Prove one derivative sign on [c_lo,c_hi] with outward intervals."""
    left = Interval.point(c_lo)
    right = Interval.point(c_hi)
    c_iv = Interval(left.lo, right.hi)
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
    }


def certify_root(c_lo: Fraction = Fraction(23, 10),
                 c_hi: Fraction = Fraction(26, 10),
                 *, cells: int = 256) -> dict[str, Any]:
    """Bracket a sign change of response-4/27 and prove it unique."""
    a_lo = response_interval(c_lo, cells=cells)
    a_hi = response_interval(c_hi, cells=cells)
    lo, hi = c_lo, c_hi
    # The response decreases on the production branch: positive at the left,
    # negative at the right.
    if not (a_lo.lo > _f(CRIT).hi and a_hi.hi < _f(CRIT).lo):
        raise ValueError(
            "initial bracket does not separate: "
            f"A(lo)={a_lo.decimal_bounds()} A(hi)={a_hi.decimal_bounds()}")
    # Bisection: only make a step when the midpoint interval separates.
    for _ in range(80):
        if hi - lo <= Fraction(1, 10**18):
            break
        mid = (lo + hi) / 2
        a_mid = response_interval(mid, cells=cells)
        if a_mid.lo > _f(CRIT).hi:
            lo = mid
        elif a_mid.hi < _f(CRIT).lo:
            hi = mid
        else:
            # Cannot decide with this cell resolution; stop with the current
            # certified sign bracket rather than pretending to contract.
            break
    left = response_interval(lo, cells=cells)
    right = response_interval(hi, cells=cells)
    existence = left.lo > _f(CRIT).hi and right.hi < _f(CRIT).lo
    uniqueness = certify_uniqueness(lo, hi, cells=min(cells, 256))
    return {
        "schema_version": 1,
        "status": "PASS" if existence and uniqueness["status"] == "PASS" else "FAIL",
        "bracket": [str(lo), str(hi)],
        "bracket_decimal": [float(lo), float(hi)],
        "response_left": left.decimal_bounds(),
        "response_right": right.decimal_bounds(),
        "critical": "4/27",
        "cells": cells,
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
