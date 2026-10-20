# -*- coding: utf-8 -*-
"""Publish outward intervals for the six thermal weak-rate channels."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_frg.cosmology.bbn_helium import framework_weak_inputs  # noqa: E402
from cg_frg.cosmology.thermal_weak import weak_rates  # noqa: E402
from cg_frg.cosmology.weak_interval import weak_rate_intervals  # noqa: E402


def compute() -> dict:
    inputs = framework_weak_inputs()
    T = float(get("bbn_Tf"))
    centre = weak_rates(inputs, T)
    enclosure = weak_rate_intervals(inputs, T, cells=1024)
    for name, interval in enclosure["rates"].items():
        value = centre["channels"][name]
        if not interval["lo"] <= value <= interval["hi"]:
            raise RuntimeError(f"weak-rate interval misses {name}")
    payload = {
        "temperature_GeV": T,
        "wmax": enclosure["wmax"],
        "cells": enclosure["cells"],
        "rates": enclosure["rates"],
        "production_channels": centre["channels"],
        "method": "finite trapezoid with second-derivative remainder plus Fermi-tail bound",
    }
    pset(
        "bbn_weak_rate_intervals", payload,
        provenance="DERIVED", role="internal",
        dependencies=("bbn_Tf",),
        definition=QuantityDefinition(
            object="six thermal weak-rate intervals", unit="s^-1",
            carrier="static-nucleon weak channels",
            operator="six phase-space integrals",
            source="generated weak inputs at the BBN freeze-out temperature",
            projection="same channel readout as weak_rates",
            normalization="G_F^2 V_ud^2 (1+3g_A^2) m_e^5/(2*pi^3*hbar)",
            scheme="finite trapezoid plus exponential Fermi tail",
            order="leading static-nucleon Born approximation",
            assumptions=("point Coulomb factor", "no recoil or weak magnetism"),
            error_kind="outward interval; finite quadrature and Fermi-tail bound included",
        ),
        note="Outward intervals for the six thermal weak-rate channels at T_f.",
    )
    return payload


if __name__ == "__main__":
    print(compute())
