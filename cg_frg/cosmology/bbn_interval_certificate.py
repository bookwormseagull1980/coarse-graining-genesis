# -*- coding: utf-8 -*-
"""Publish the validated interval enclosure of the BBN beta phase space."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_frg.cosmology.bbn_helium import beta_phase_space  # noqa: E402
from cg_frg.cosmology.bbn_interval import beta_phase_space_interval  # noqa: E402


def compute() -> dict:
    dm = float(get("bbn_dm_np"))
    m_e = float(get("m_e_pred")) * 1e-3
    alpha = float(get("alpha_em_0_pred"))
    centre = beta_phase_space(dm, m_e, alpha)
    interval = beta_phase_space_interval(dm, m_e, alpha, cells=2048,
                                         endpoint_cell=1e-3)
    if not interval["lo"] <= centre["value"] <= interval["hi"]:
        raise RuntimeError("phase-space interval does not contain the production centre")
    pset(
        "bbn_beta_phase_space_interval", {
            "lo": interval["lo"],
            "hi": interval["hi"],
            "width": interval["hi"] - interval["lo"],
            "production_centre": centre["value"],
            "cells": interval["cells"],
            "method": interval["method"],
        },
        provenance="DERIVED", role="internal",
        dependencies=("bbn_dm_np", "m_e_pred", "alpha_em_0_pred"),
        definition=QuantityDefinition(
            object="beta phase-space interval", unit="1",
            carrier="static-nucleon beta decay",
            operator="normalized Coulomb-regular phase-space integral",
            source="generated mass splitting and QED coupling",
            projection="same readout as beta_phase_space",
            normalization="d^3 times the normalized integral on [0,1]",
            scheme="composite trapezoid with outward second-derivative remainder",
            order="one-dimensional phase space",
            assumptions=("Coulomb point interaction", "constant nuclear matrix element"),
            error_kind="outward interval; quadrature remainder included",
        ),
        note="Strict outward enclosure of the BBN beta phase-space integral.",
    )
    return {"centre": centre["value"], **interval}


if __name__ == "__main__":
    print(compute())
