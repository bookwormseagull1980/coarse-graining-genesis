# -*- coding: utf-8 -*-
"""Publish an outward interval for the native relative potential."""

from __future__ import annotations

import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_frg.ewsb.native_condensate import complete_relative_potential  # noqa: E402
from cg_frg.ewsb.native_condensate_interval import relative_potential_interval  # noqa: E402


def compute() -> dict:
    amplitude_squared = 1e-3
    L = math.sqrt(2 * math.pi)
    g = 1.0
    centre = complete_relative_potential(amplitude_squared=amplitude_squared,
                                         L=L, g=g)
    enclosure = relative_potential_interval(amplitude_squared=amplitude_squared,
                                            L=L, g=g, cells=4096)
    if not enclosure["value"]["lo"] <= centre["value"] <= enclosure["value"]["hi"]:
        raise RuntimeError("native potential interval misses production")
    payload = {
        "amplitude_squared": amplitude_squared, "L": L, "g": g,
        "cells": enclosure["cells"],
        "value": enclosure["value"],
        "spectral_potential": enclosure["spectral_potential"],
        "production_value": centre["value"],
        "method": "cellwise mpmath interval hull of the analytic restoring function",
    }
    pset(
        "native_relative_potential_interval", payload,
        provenance="DERIVED", role="internal",
        definition=QuantityDefinition(
            object="native relative potential interval", unit="1",
            carrier="native condensate shell tower",
            operator="integral of the analytic restoring response",
            source="native condensate reference point",
            projection="same readout as complete_relative_potential",
            normalization="linear term + integral_0^u H(z) dz",
            scheme="interval cell integration",
            order="one-loop shell sum",
            assumptions=("constant shell tower", "declared reference radius"),
            error_kind="outward interval; cell integration included",
        ),
        note="Outward enclosure of the native relative potential at a reference point.",
    )
    return payload


if __name__ == "__main__":
    print(compute())
