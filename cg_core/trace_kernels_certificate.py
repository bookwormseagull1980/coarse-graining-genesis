# -*- coding: utf-8 -*-
"""Publish an outward interval for the Wetterich trace kernels."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_core.trace_kernels import boson_mode_contribution, fermion_mode_contribution  # noqa: E402
from cg_core.trace_kernels_interval import mode_contribution_intervals  # noqa: E402


def compute() -> dict:
    k, lam, m2 = 1.0, 0.0, 0.1
    enclosure = mode_contribution_intervals(k, lam, m2, cells=1024)
    boson = boson_mode_contribution(k, lam, m2)
    fermion = fermion_mode_contribution(k, lam, m2)
    if not enclosure["boson"]["lo"] <= boson <= enclosure["boson"]["hi"]:
        raise RuntimeError("trace-kernel boson interval misses production")
    if not enclosure["fermion"]["lo"] <= fermion <= enclosure["fermion"]["hi"]:
        raise RuntimeError("trace-kernel fermion interval misses production")
    payload = {
        "k": k, "lambda": lam, "m2": m2, "cells": enclosure["cells"],
        "boson": enclosure["boson"], "fermion": enclosure["fermion"],
        "production_boson": boson, "production_fermion": fermion,
        "method": "finite q0 trapezoid with outward second-derivative remainder",
    }
    pset(
        "trace_kernel_intervals", payload,
        provenance="DERIVED", role="internal",
        definition=QuantityDefinition(
            object="Wetterich trace-kernel intervals", unit="1",
            carrier="single bosonic/fermionic mode",
            operator="q0 integral of the exponential regulator kernel",
            source="exponential Wetterich window",
            projection="boson and fermion mode contributions",
            normalization="C_b=(1/2) integral dq0/(2pi) dR/(q0^2+lambda+R+m2)",
            scheme="finite q0 trapezoid",
            order="one-loop mode contribution",
            assumptions=("exponential regulator", "static mode"),
            error_kind="outward interval; quadrature remainder included",
        ),
        note="Outward intervals for the reference trace-kernel mode.",
    )
    return payload


if __name__ == "__main__":
    print(compute())
