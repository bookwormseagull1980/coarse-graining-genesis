# -*- coding: utf-8 -*-
"""Outward interval certificates for the Wetterich trace kernels."""

from __future__ import annotations

import math

from cg_core.interval_jet import Jet2
from cg_core.rational_interval import GRID, Interval, exp_negative
from cg_core.trace_kernels import _q0_range


def _constant(value: float) -> Jet2:
    return Jet2.point(Interval.point(value))


def _interval(low: float, high: float) -> Interval:
    return Interval(int(low * GRID), int(high * GRID))


def _exp_positive(jet: Jet2) -> Jet2:
    """exp(jet.v) for a nonnegative value interval.

    The value is formed by integer division of the outward ``exp(-v)``
    enclosure; this avoids the underflow of ``(exp(-v))**3`` in the generic
    reciprocal derivative at large v.
    """
    inverse = jet.exp_negative()
    lo = (GRID * GRID) // max(1, inverse.v.hi)
    hi = (GRID * GRID) // max(1, inverse.v.lo) + 1
    value = Interval(lo, hi)
    return Jet2(value, value * jet.d1, value * (jet.d2 + jet.d1 ** 2))


def _terms_jet(z: Jet2, k2: float, m2: float) -> Jet2:
    """The full (1/2pi) dR/den integrand as a second-order jet."""
    y = z / _constant(k2)
    y_lo, y_hi = y.v.lo / GRID, y.v.hi / GRID
    if y_hi < 1e-10:
        dR = _constant(2.0 * k2) * (_constant(1.0) - y * y / _constant(12.0))
        den = _constant(k2 + m2) + z / _constant(2.0)
        return dR / den / _constant(2 * math.pi)
    ey_neg = y.exp_negative()
    one_minus = _constant(1.0) - ey_neg
    if y_lo > 50.0:
        upper = _constant(3.0) * z * y * ey_neg / (z + _constant(m2))
        return Jet2.point(Interval(0, max(0, upper.v.hi))) / _constant(2 * math.pi)
    # dR/den = 2 z y e^-y / ((1-e^-y)(z+m2(1-e^-y))).
    integrand = (_constant(2.0) * z * y * ey_neg
                 / (one_minus * (z + _constant(m2) * one_minus)))
    return integrand / _constant(2 * math.pi)


def _frequency_interval(k: float, lam: float, m2: float, cells: int) -> Interval:
    k2 = k * k
    qmax = _q0_range(k, lam)
    start = 0.0
    if lam == 0.0:
        start = min(1e-1, 0.5 * qmax)
    total = Interval.point(0)
    if start > 0.0:
        bound = 2.0 * k2 / (k2 + m2) / (2.0 * math.pi) * start
        total = total + Interval(0, int(bound * GRID) + 1)
    width = (qmax - start) / cells
    for j in range(cells):
        left = start + j * width
        right = qmax if j == cells - 1 else start + (j + 1) * width
        def value_at(q: float) -> Interval:
            z = Interval.point(q) ** 2 + Interval.point(lam)
            return _terms_jet(Jet2.point(z), k2, m2).v
        f0, f1 = value_at(left), value_at(right)
        trapezoid = (f0 + f1) * Interval.point(right - left) / 2
        z = Jet2.variable(_interval(left, right)) ** 2 + _constant(lam)
        jet = _terms_jet(z, k2, m2)
        m2b = max(abs(jet.d2.lo), abs(jet.d2.hi))
        error = Interval.point(float(m2b) / GRID) * Interval.point(right - left) ** 3 / 12
        total = total + trapezoid + Interval(-error.hi, error.hi)
    return total * Interval.point(2.0)


def mode_contribution_intervals(k: float, lam: float, m2: float, *,
                               cells: int = 256) -> dict:
    integral = _frequency_interval(k, lam, m2, cells)
    boson = integral * Interval.point(0.5)
    fermion = -integral
    return {
        "k": k, "lambda": lam, "m2": m2, "cells": cells,
        "boson": {"lo": boson.lo / GRID, "hi": boson.hi / GRID},
        "fermion": {"lo": fermion.lo / GRID, "hi": fermion.hi / GRID},
    }
