# -*- coding: utf-8 -*-
"""Outward interval enclosure of the native relative potential integral."""

from __future__ import annotations

import math

import mpmath as mp
from mpmath.ctx_iv import MPIntervalContext

from cg_frg.ewsb.native_condensate import complete_relative_potential

_IV = MPIntervalContext()
_IV.dps = 50


def _mpf(value: float):
    return _IV.mpf(value)


def _h_interval(z):
    """Enclosure of H(z)=J'(z) on a nonnegative interval."""
    if z.b < 0.25:
        b = _IV.sqrt(0.25 - z)
        return _IV.pi / 8 - _IV.pi * b / 4 * _IV.tan(_IV.pi * b / 2)
    if z.a > 0.25:
        s = _IV.sqrt(z - 0.25)
        angle = _IV.pi * s / 2
        e = _IV.exp(2 * angle)
        tanh = (e - 1) / (e + 1)
        return _IV.pi / 8 + _IV.pi * s / 4 * tanh
    # H is increasing and continuous; use the endpoint enclosures.
    left = _h_point(float(mp.mpf(z.a)))
    right = _h_point(float(mp.mpf(z.b)))
    return _IV.mpf((mp.mpf(left.a), mp.mpf(right.b)))


def _h_point(z: float):
    if z == 0:
        return _IV.mpf(0)
    if z < 0.25:
        b = _IV.sqrt(0.25 - z)
        return _IV.pi / 8 - _IV.pi * b / 4 * _IV.tan(_IV.pi * b / 2)
    if z == 0.25:
        return _IV.pi / 8
    s = _IV.sqrt(z - 0.25)
    angle = _IV.pi * s / 2
    e = _IV.exp(2 * angle)
    return _IV.pi / 8 + _IV.pi * s / 4 * (e - 1) / (e + 1)


def relative_potential_interval(*, amplitude_squared: float, L: float,
                                g: float, cells: int = 4096) -> dict:
    """Enclose I(u)=int_0^u H(z) dz and the full relative potential."""
    if amplitude_squared < 0 or L <= 0 or g <= 0 or cells < 8:
        raise ValueError("nonnegative amplitude, positive L/g and cells>=8 required")
    u = g * L * L * amplitude_squared
    if u == 0:
        return {"u": 0.0, "spectral_potential": {"lo": 0.0, "hi": 0.0},
                "value": {"lo": 0.0, "hi": 0.0}}
    width = u / cells
    lo = mp.mpf(0)
    hi = mp.mpf(0)
    for j in range(cells):
        left = j * width
        right = u if j == cells - 1 else (j + 1) * width
        h = _h_interval(_IV.mpf((left, right)))
        lo += mp.mpf(h.a) * width
        hi += mp.mpf(h.b) * width
    linear = 8 * (1 / (L * L) - 1 / math.pi) * amplitude_squared
    value_lo = linear + float(lo)
    value_hi = linear + float(hi)
    return {
        "u": u, "cells": cells,
        "spectral_potential": {"lo": float(lo), "hi": float(hi)},
        "value": {"lo": value_lo, "hi": value_hi},
    }


if __name__ == "__main__":
    print(relative_potential_interval(amplitude_squared=1e-3, L=math.sqrt(2*math.pi), g=1.0))
