# -*- coding: utf-8 -*-
"""Outward interval certificates for the finite-domain spectral channels."""

from __future__ import annotations

import math

from cg_core.interval_jet import Jet2
from cg_core.rational_interval import GRID, Interval, exp_negative
from cg_core.spectrum_loop import iter_sm_spectrum
from cg_core.window_weights import DEFAULT_RESPONSE_DOMAIN, ResponseDomain
from cg_frg.frg.spectral_sum import (
    _w_f2_fermion, _w_f2_gauge, _w_g2, _w_jmu, _w_tmunu_spin0,
    _w_tmunu_spin2, volume,
)


def _constant(value: float) -> Jet2:
    return Jet2.point(Interval.point(value))


def _interval(low: float, high: float) -> Interval:
    return Interval(int(low * GRID), int(high * GRID))


def _kernel_jet(name: str, q2: Jet2, m2: Jet2) -> Jet2:
    den = q2 + m2
    if den.v.lo <= 0:
        raise ValueError("kernel denominator is not strictly positive")
    if name in ("tt2", "f2g", "g2"):
        prefactor = 1.0 if name == "tt2" else 12.0
        return _constant(prefactor) * q2 * q2 / (den * den)
    if name == "tt0":
        return (_constant(1.0 / 3.0) * (q2 + _constant(3.0) * m2) ** 2
                / (den * den))
    if name == "f2f":
        return _constant(-8.0) * q2 / (den * den)
    if name == "jmu":
        return -q2 / (den * den)
    raise ValueError("unknown spectral kernel")


def _frequency_interval(name: str, lam: float, m2: float, cutoff: float,
                        dom: ResponseDomain, cells: int, scheme: str) -> Interval:
    if scheme == "gaussian":
        edge = dom.frequency_edge(lam, cutoff)
    elif scheme == "litim":
        edge = math.sqrt(max(cutoff - lam, 0.0))
    else:
        raise ValueError("unknown spectral scheme")
    if edge <= 0:
        return Interval.point(0)
    width = edge / cells
    total = Interval.point(0)
    for j in range(cells):
        left = j * width
        right = edge if j == cells - 1 else (j + 1) * width

        def window(q: Interval) -> Interval:
            if scheme == "gaussian":
                return exp_negative(q / Interval.point(cutoff))
            return Interval.point(1)

        def value_at(w: float) -> Interval:
            q = Interval.point(w) ** 2 + Interval.point(lam)
            jet = _kernel_jet(name, Jet2.point(q), _constant(m2))
            return (jet * Jet2.point(window(q))).v

        f0, f1 = value_at(left), value_at(right)
        trapezoid = (f0 + f1) * Interval.point(right - left) / 2
        q = Jet2.variable(_interval(left, right)) ** 2 + _constant(lam)
        if scheme == "gaussian":
            window_jet = (q / _constant(cutoff)).exp_negative()
        else:
            window_jet = _constant(1.0)
        jet = _kernel_jet(name, q, _constant(m2)) * window_jet
        m2b = max(abs(jet.d2.lo), abs(jet.d2.hi))
        error = Interval.point(float(m2b) / GRID) * Interval.point(right - left) ** 3 / 12
        total = total + trapezoid + Interval(-error.hi, error.hi)
    return total / Interval.point(math.pi)


def _channel_interval(name: str, weight, L: float, cutoff: float, tau: float,
                      cells: int, dom: ResponseDomain, scheme: str) -> Interval:
    V3 = volume(L)
    k_rg = math.sqrt(cutoff)
    total = Interval.point(0)
    for kind, field, _mode, lam, m2, deg in iter_sm_spectrum(
            L, k_rg, tau, domain=dom):
        w = weight(kind, field)
        if abs(w) < 1e-40:
            continue
        freq = _frequency_interval(name, lam, m2, cutoff, dom, cells, scheme)
        total = total + Interval.point(float(deg * w) / V3) * freq
    return total


def channel_intervals(L: float, cutoff: float, tau: float, *,
                      cells: int = 64, scheme: str = "gaussian",
                      domain: ResponseDomain = DEFAULT_RESPONSE_DOMAIN) -> dict:
    specs = {
        "tmunu_spin2": ("tt2", _w_tmunu_spin2),
        "tmunu_spin0": ("tt0", _w_tmunu_spin0),
        "f2_gauge": ("f2g", _w_f2_gauge),
        "f2_fermion": ("f2f", _w_f2_fermion),
        "g2": ("g2", _w_g2),
        "jmu": ("jmu", _w_jmu),
    }
    out = {}
    for label, (kernel, weight) in specs.items():
        interval = _channel_interval(kernel, weight, L, cutoff, tau, cells,
                                     domain, scheme)
        out[label] = {"lo": interval.lo / GRID, "hi": interval.hi / GRID}
    out["f2"] = {
        "lo": out["f2_gauge"]["lo"] + out["f2_fermion"]["lo"],
        "hi": out["f2_gauge"]["hi"] + out["f2_fermion"]["hi"],
    }
    return {"L": L, "cutoff": cutoff, "tau": tau, "cells": cells,
            "scheme": scheme, "channels": out}
