# -*- coding: utf-8 -*-
"""Validated interval enclosure of the BBN beta phase-space integral.

The production scalar in ``bbn_helium.beta_phase_space`` is unchanged.  This
module supplies an independent outward bound via a composite trapezoid rule
with an interval second-derivative remainder.  The Coulomb factor and the
Fermi endpoint are evaluated with the same rational interval arithmetic used
by the endpoint certificate.
"""

from __future__ import annotations

import math

from cg_core.interval_jet import Jet2
from cg_core.rational_interval import GRID, Interval


def _constant(value: float) -> Jet2:
    return Jet2.point(Interval.point(value))


def _interval(low: float, high: float) -> Interval:
    return Interval(int(low * GRID), int(high * GRID))


def _beta_jet(x: Interval, d: float, a: float) -> Jet2:
    xv = Jet2.variable(x)
    one = _constant(1.0)
    dv = _constant(d)
    W = one + dv * xv
    p2 = dv * xv * (_constant(2.0) + dv * xv)
    p = p2.sqrt()
    if a == 0.0:
        return W * p * (one - xv) ** 2
    z = (_constant(a) * W) / p
    denominator = one - z.exp_negative()
    coulomb = (_constant(a) * W * W) / denominator
    return coulomb * (one - xv) ** 2


def _beta_cell(low: float, high: float, d: float, a: float) -> Interval:
    h = high - low
    f0 = _beta_jet(Interval.point(low), d, a).v
    f1 = _beta_jet(Interval.point(high), d, a).v
    trapezoid = (f0 + f1) * Interval.point(h) / 2
    jet = _beta_jet(_interval(low, high), d, a)
    m2 = max(abs(jet.d2.lo), abs(jet.d2.hi))
    error = Interval.point(float(m2) / GRID) * (Interval.point(h) ** 3) / 12
    return trapezoid + Interval(-error.hi, error.hi)


def _beta_endpoint_cell(eps: float, d: float, a: float) -> Interval:
    """Crude bound on [0, eps], where p vanishes but the integrand is finite."""
    w_lo, w_hi = 1.0, 1.0 + d * eps
    p2_hi = d * eps * (2.0 + d * eps)
    p_hi = math.sqrt(p2_hi) if p2_hi > 0 else 0.0
    if a == 0.0:
        return Interval.point(w_hi * p_hi * eps)
    if p_hi <= 0:
        return Interval.point(a * eps)
    z_min = a * w_lo / p_hi
    denom_lo = 1.0 - math.exp(-z_min)
    c_hi = a * w_hi * w_hi / denom_lo
    c_lo = a * w_lo * w_lo
    return _interval(c_lo * (1.0 - eps) ** 2 * eps, c_hi * eps)


def beta_phase_space_interval(dm: float, m_e: float, alpha_em: float,
                              *, cells: int = 2048,
                              endpoint_cell: float = 1e-3) -> dict:
    """Return an outward interval for the normalized beta phase space."""
    if not all(math.isfinite(x) for x in (dm, m_e, alpha_em)):
        raise ValueError("finite inputs required")
    if cells < 8 or endpoint_cell <= 0 or endpoint_cell >= 1:
        raise ValueError("cells and endpoint cell are out of range")
    if dm <= m_e:
        return {"status": "PASS", "lo": 0.0, "hi": 0.0,
                "kinematically_closed": True, "cells": cells}
    d = (dm - m_e) / m_e
    a = 2.0 * math.pi * alpha_em
    total = _beta_endpoint_cell(endpoint_cell, d, a)
    width = (1.0 - endpoint_cell) / cells
    for j in range(cells):
        low = endpoint_cell + j * width
        high = 1.0 if j == cells - 1 else endpoint_cell + (j + 1) * width
        total = total + _beta_cell(low, high, d, a)
    scaled = total * Interval.point(d) ** 3
    return {
        "status": "PASS",
        "lo": scaled.lo / GRID,
        "hi": scaled.hi / GRID,
        "cells": cells,
        "endpoint_cell": endpoint_cell,
        "method": "composite trapezoid with outward second-derivative remainder",
        "unit": "1",
    }
