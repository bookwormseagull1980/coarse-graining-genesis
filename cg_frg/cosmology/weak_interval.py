# -*- coding: utf-8 -*-
"""Outward interval bounds for the six thermal weak-rate channels.

The production ``thermal_weak.weak_rates`` remains the reporting value.  This
module adds an independent enclosure on a finite window plus an explicit
Fermi-tail upper bound.  It is the weak-rate analogue of ``bbn_interval.py``.
"""

from __future__ import annotations

import math

from cg_core.interval_jet import Jet2
from cg_core.rational_interval import GRID, Interval, exp_negative

HBAR_GEV_S = 6.582119569e-25


def _constant(value: float) -> Jet2:
    return Jet2.point(Interval.point(value))


def _interval(low: float, high: float) -> Interval:
    return Interval(int(low * GRID), int(high * GRID))


def _fermi_jet(energy: Jet2, temperature: float,
               chemical_potential: float) -> Jet2:
    if temperature <= 0:
        raise ValueError("positive temperature required")
    z = (energy - _constant(chemical_potential)) / _constant(temperature)
    if z.v.lo >= 0:
        e = z.exp_negative()
        return e / (_constant(1.0) + e)
    if z.v.hi <= 0:
        e = (-z).exp_negative()
        return _constant(1.0) / (_constant(1.0) + e)
    return Jet2(Interval(0, GRID), Interval.point(0), Interval.point(0))


def _one_minus_fermi(energy: Jet2, temperature: float,
                     chemical_potential: float) -> Jet2:
    return _constant(1.0) - _fermi_jet(energy, temperature, chemical_potential)


def _electron_phase_jet(W: Jet2, alpha: float) -> Jet2:
    p = (W * W - _constant(1.0)).sqrt()
    if alpha == 0.0:
        return W * p
    x = 2.0 * math.pi * alpha
    z = _constant(x) * W / p
    return _constant(x) * W * W / (_constant(1.0) - z.exp_negative())


def _channel_jet(W: Jet2, channel: str, reverse: bool,
                 m: float, delta: float, alpha: float,
                 T: float, Tnu: float, mue: float, munu: float) -> Jet2:
    E = W * _constant(m)
    if channel == "capture":
        e_nu = (W - _constant(delta)) * _constant(m)
        f1 = _fermi_jet(e_nu, Tnu, munu)
        f2 = _fermi_jet(E, T, mue)
        statistical = f2 * (_constant(1.0) - f1) if reverse else f1 * (_constant(1.0) - f2)
        phase = _electron_phase_jet(W, alpha) * (W - _constant(delta)) ** 2
    elif channel == "positron":
        e_nu = (W + _constant(delta)) * _constant(m)
        f1 = _fermi_jet(E, T, -mue)
        f2 = _fermi_jet(e_nu, Tnu, -munu)
        statistical = f2 * (_constant(1.0) - f1) if reverse else f1 * (_constant(1.0) - f2)
        phase = _electron_phase_jet(W, 0.0) * (W + _constant(delta)) ** 2
    elif channel == "decay":
        e_nu = (_constant(delta) - W) * _constant(m)
        f1 = _fermi_jet(E, T, mue)
        f2 = _fermi_jet(e_nu, Tnu, -munu)
        statistical = f1 * f2 if reverse else (_constant(1.0) - f1) * (_constant(1.0) - f2)
        phase = _electron_phase_jet(W, alpha) * (_constant(delta) - W) ** 2
    else:
        raise ValueError("unknown weak channel")
    return phase * statistical


def _channel_finite(low: float, high: float, channel: str, reverse: bool,
                    m: float, delta: float, alpha: float,
                    T: float, Tnu: float, mue: float, munu: float,
                    cells: int) -> Interval:
    width = (high - low) / cells
    total = Interval.point(0)
    for j in range(cells):
        left = low + j * width
        right = high if j == cells - 1 else low + (j + 1) * width
        if j == 0 and low <= 1.0 + 1e-9:
            # phase vanishes at W=1; bound the first cell conservatively.
            c_e = 1.0
            if alpha > 0:
                x = 2 * math.pi * alpha
                c_e = x / (1 - math.exp(-x))
            upper = c_e * right * right * (right + delta) ** 2 * (right - left)
            total = total + Interval(0, int(upper * GRID) + 1)
            continue
        f0 = _channel_jet(Jet2.point(Interval.point(left)), channel, reverse,
                          m, delta, alpha, T, Tnu, mue, munu).v
        f1 = _channel_jet(Jet2.point(Interval.point(right)), channel, reverse,
                          m, delta, alpha, T, Tnu, mue, munu).v
        trapezoid = (f0 + f1) * Interval.point(right - left) / 2
        jet = _channel_jet(Jet2.variable(_interval(left, right)), channel,
                           reverse, m, delta, alpha, T, Tnu, mue, munu)
        m2 = max(abs(jet.d2.lo), abs(jet.d2.hi))
        error = Interval.point(float(m2) / GRID) * Interval.point(right - left) ** 3 / 12
        total = total + trapezoid + Interval(-error.hi, error.hi)
    return total


def _tail_upper(Wmax: float, m: float, delta: float, alpha: float,
                T: float) -> Interval:
    """Upper bound for int_Wmax^inf phase*statistical dW."""
    if T <= 0:
        raise ValueError("positive temperature required for a tail bound")
    c = Interval.point(m / T)
    d = Interval.point(delta)
    x = 2 * math.pi * alpha
    if alpha == 0:
        c_e = Interval.point(1.0)
    else:
        c_e = Interval.point(x) / (Interval.point(1.0) - exp_negative(Interval.point(x)))
    w = Interval.point(Wmax)
    e = exp_negative(c * w)
    inv_decay = Interval.point(1.0) / exp_negative(c * d)
    # M_n = int W^n exp(-c W) dW, with M_0=e/c and
    # M_n = W^n e/c + n/c M_{n-1}.
    moments = [e / c]
    for n in (1, 2, 3, 4):
        moments.append((w ** n) * e / c + Interval.point(n) / c * moments[-1])
    polynomial = moments[4] + 2 * d * moments[3] + (d ** 2) * moments[2]
    return c_e * inv_decay * polynomial


def weak_rate_intervals(inputs, temperature: float, neutrino_temperature: float | None = None,
                        *, electron_chemical_potential: float = 0.0,
                        neutrino_chemical_potential: float = 0.0,
                        cells: int = 1024, tail_width: float = 30.0) -> dict:
    T = float(temperature)
    Tnu = T if neutrino_temperature is None else float(neutrino_temperature)
    m = inputs.electron_mass
    delta = inputs.neutron_proton_split / m
    coefficient = (inputs.G_F ** 2 * inputs.V_ud ** 2 * (1 + 3 * inputs.g_A ** 2)
                   * m ** 5 * inputs.rate_multiplier
                   / (2 * math.pi ** 3 * HBAR_GEV_S))
    if T <= 0 or Tnu <= 0:
        raise ValueError("positive temperatures required")
    wmax = max(1.0, delta) + tail_width * T / m
    rates = {}
    for channel, low, high in (("capture", max(1.0, delta), wmax),
                               ("positron", 1.0, wmax),
                               ("decay", 1.0, delta)):
        for reverse in (False, True):
            name = channel + ("_p_to_n" if reverse else "_n_to_p")
            finite = _channel_finite(low, high, channel, reverse, m, delta,
                                     inputs.alpha_em, T, Tnu,
                                     electron_chemical_potential,
                                     neutrino_chemical_potential, cells)
            tail = _tail_upper(wmax, m, delta, inputs.alpha_em, T)
            interval = (finite + tail) * Interval.point(coefficient)
            rates[name] = {"lo": interval.lo / GRID, "hi": interval.hi / GRID}
    return {"temperature_GeV": T, "neutrino_temperature_GeV": Tnu,
            "wmax": wmax, "cells": cells, "rates": rates}
