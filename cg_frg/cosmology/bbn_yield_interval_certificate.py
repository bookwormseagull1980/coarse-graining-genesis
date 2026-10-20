# -*- coding: utf-8 -*-
"""Propagate the certified beta phase-space interval into production BBN values.

The production freeze-out temperature depends on G_F, g_A and the splitting,
not on the beta phase-space integral.  Hence, at fixed production inputs,
the lifetime and helium yield depend monotonically on the phase-space value
through

    tau_n = C / f,
    Y_p   = 2 X_f exp(-t_decay/tau_n).

This is an algebraic interval propagation of the existing beta certificate,
not a new physical model.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import annotate_interval, get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402


def compute() -> dict:
    joint = get("bbn_joint_response")
    beta = get("bbn_beta_phase_space_interval")
    f_centre = float(joint["phase_space"]["value"])
    f_lo, f_hi = float(beta["lo"]), float(beta["hi"])
    tau_centre = float(joint["values"]["tau_n"])
    Yp_centre = float(joint["values"]["Y_p"])
    X_f = float(joint["helium_fractions"]["neutron_fraction_freeze"])
    t_decay = float(joint["values"]["t_decay"])

    tau_lo = tau_centre * f_centre / f_hi
    tau_hi = tau_centre * f_centre / f_lo
    # Survival increases with tau; the lower Yp endpoint uses tau_lo.
    Yp_lo = 2.0 * X_f * math.exp(-t_decay / tau_lo)
    Yp_hi = 2.0 * X_f * math.exp(-t_decay / tau_hi)

    if not tau_lo <= tau_centre <= tau_hi:
        raise RuntimeError("lifetime interval misses production centre")
    if not Yp_lo <= Yp_centre <= Yp_hi:
        raise RuntimeError("helium interval misses production centre")
    if not Yp_centre == 2.0 * X_f * math.exp(-t_decay / tau_centre):
        raise RuntimeError("production helium formula does not match the record")

    payload = {
        "phase_space": {"lo": f_lo, "hi": f_hi, "centre": f_centre},
        "production_tau_n_s": tau_centre,
        "production_Yp": Yp_centre,
        "initial_neutron_fraction": X_f,
        "t_decay_s": t_decay,
        "tau_n_interval_s": {"lo": tau_lo, "hi": tau_hi},
        "Yp_interval": {"lo": Yp_lo, "hi": Yp_hi},
        "method": "monotone algebraic propagation of the beta phase-space interval",
    }
    pset(
        "bbn_yield_interval", payload,
        provenance="DERIVED", role="internal",
        dependencies=("bbn_joint_response", "bbn_beta_phase_space_interval"),
        definition=QuantityDefinition(
            object="BBN lifetime and helium interval from beta phase space",
            unit="s and dimensionless",
            carrier="instantaneous freeze-out plus complete neutron capture",
            operator="tau_n=C/f, Yp=2 X_f exp(-t_decay/tau_n)",
            source="certified beta phase-space interval",
            projection="same readout as bbn_tau_n and bbn_Yp",
            normalization="production freeze-out inputs fixed",
            scheme="monotone algebraic interval propagation",
            order="production BBN approximation",
            assumptions=("T_f independent of the phase-space normalisation",
                         "fixed production thermal inputs"),
            error_kind="outward interval from beta phase-space certificate",
        ),
        note="Production Yp/tau_n interval induced by the certified beta phase space.",
    )
    annotate_interval("bbn_tau_n", {"lo": tau_lo, "hi": tau_hi},
                      source="bbn_beta_phase_space_interval",
                      note="tau_n=C/f monotone interval propagation")
    annotate_interval("bbn_Yp", {"lo": Yp_lo, "hi": Yp_hi},
                      source="bbn_yield_interval",
                      note="Yp=2 X_f exp(-t_decay/tau_n) interval propagation")
    return payload


if __name__ == "__main__":
    print(compute())
