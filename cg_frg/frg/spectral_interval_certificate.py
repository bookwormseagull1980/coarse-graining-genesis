# -*- coding: utf-8 -*-
"""Publish outward intervals for the finite-domain spectral channels."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_frg.frg.spectral_interval import channel_intervals  # noqa: E402
from cg_frg.frg.spectral_sum import compute  # noqa: E402


def compute_records() -> dict:
    L = 2.4935343325226915
    cutoff = 1.0e-2
    tau = 0.02
    centre = compute(L, cutoff, tau)
    intervals = channel_intervals(L, cutoff, tau, cells=64)
    names = ("tmunu_spin2", "tmunu_spin0", "f2", "g2", "jmu")
    for name in names:
        low = intervals["channels"][name]["lo"]
        high = intervals["channels"][name]["hi"]
        value = centre[name]["rp3_pi0"]
        if not low <= value <= high:
            raise RuntimeError(f"spectral interval misses {name}")
    payload = {
        "L": L, "cutoff": cutoff, "tau": tau,
        "cells": intervals["cells"],
        "channels": intervals["channels"],
        "production_channels": {name: centre[name]["rp3_pi0"] for name in names},
        "method": "Gaussian finite-domain trapezoid with second-derivative remainder",
    }
    pset(
        "spectral_channel_intervals", payload,
        provenance="DERIVED", role="internal",
        definition=QuantityDefinition(
            object="finite-domain spectral channel intervals", unit="1",
            carrier="RP3 projected Standard-Model spectrum",
            operator="summed zero-external-momentum channel responses",
            source="generated spectrum and Gaussian response domain",
            projection="same readout as spectral_sum.compute",
            normalization="V3^-1 sum deg*weight*I(lambda,m2)",
            scheme="Gaussian finite-domain trapezoid",
            order="one-loop p=0 channel readout",
            assumptions=("R=5 finite response domain", "Gaussian window"),
            error_kind="outward interval; quadrature remainder included",
        ),
        note="Outward intervals for tmunu_spin2, tmunu_spin0, f2, g2 and jmu.",
    )
    return payload


if __name__ == "__main__":
    print(compute_records())
