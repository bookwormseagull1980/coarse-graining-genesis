# -*- coding: utf-8 -*-
"""Propagate the certified endpoint intervals into linear production readouts.

Only quantities whose production formula is linear in one certified input are
included here.  This is deliberately narrow: it adds real numeric intervals
without inventing error models for quantities whose uncertainty is not a
single certified input.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import annotate_interval, get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402


def _linear(name: str, value: float, source: str, denom: float,
            output_name: str, unit: str, object_name: str) -> dict:
    source_interval = get(source)
    factor = value / denom
    lo = factor * float(source_interval["lo"])
    hi = factor * float(source_interval["hi"])
    if not lo <= value <= hi:
        raise RuntimeError(f"{name} interval misses production")
    pset(
        output_name,
        {"lo": lo, "hi": hi, "relative_width": (hi - lo) / value,
         "source": source, "centre": value},
        provenance="DERIVED", role="internal",
        dependencies=(source,),
        definition=QuantityDefinition(
            object=object_name, unit=unit,
            carrier="production readout linear in the certified endpoint input",
            operator=f"scale the certified {source} by the central ratio",
            source=source,
            projection=f"same readout as {name}",
            normalization="central production ratio fixed",
            scheme="linear interval propagation",
            order="same order as the production formula",
            assumptions=(f"the production formula is linear in {source}",),
            error_kind="outward interval from the certified endpoint input",
        ),
        note=f"{name} interval induced by {source}.",
    )
    annotate_interval(name, {"lo": lo, "hi": hi}, source=source,
                      note=f"linear propagation from {source}")
    return {"lo": lo, "hi": hi, "relative_width": (hi - lo) / value}


def compute() -> dict:
    v = float(get("v_HIGGS"))
    v_interval = get("v_HIGGS_interval")
    M_G = float(get("M_G"))
    out = {}

    for name, output, unit, obj in (
        ("M_Z_pred", "M_Z_pred_interval", "GeV", "Z mass from the endpoint VEV"),
        ("m_t_pred", "m_t_pred_interval", "GeV", "top mass from the endpoint VEV"),
        ("m_b_pred", "m_b_pred_interval", "GeV", "bottom mass from the endpoint VEV"),
        ("m_mu_pred", "m_mu_pred_interval", "GeV", "muon mass from the endpoint VEV"),
        ("m_tau_pred", "m_tau_pred_interval", "GeV", "tau mass from the endpoint VEV"),
    ):
        value = float(get(name))
        out[output] = _linear(name, value, "v_HIGGS_interval", v,
                              output, unit, obj)

    # m_WR = g_R s0 M_G with g_R and s0 fixed at their production values.
    m_WR = float(get("geometric_ewsb_m_WR"))
    out["geometric_ewsb_m_WR_interval"] = _linear(
        "geometric_ewsb_m_WR", m_WR, "M_G_interval", M_G,
        "geometric_ewsb_m_WR_interval", "GeV",
        "right-handed W mass from the emergence scale")

    # kL_CMB = kL (1 - tau/4), tau fixed.
    kL = float(get("kL"))
    kL_cmb = float(get("kL_CMB"))
    factor = kL_cmb / kL
    kL_interval = get("kL_interval")
    lo = factor * float(kL_interval["lo"])
    hi = factor * float(kL_interval["hi"])
    if not lo <= kL_cmb <= hi:
        raise RuntimeError("kL_CMB interval misses production")
    pset(
        "kL_CMB_interval",
        {"lo": lo, "hi": hi, "relative_width": (hi - lo) / kL_cmb,
         "source": "kL_interval", "centre": kL_cmb},
        provenance="DERIVED", role="cg",
        dependencies=("kL_interval",),
        definition=QuantityDefinition(
            object="CMB-scale window interval", unit="1",
            carrier="local endpoint window with fixed torsion quarter",
            operator="kL_CMB = kL (1 - tau/4)",
            source="kL_interval",
            projection="same readout as kL_CMB",
            normalization="tau fixed at 1/50",
            scheme="linear interval propagation",
            order="same as the production window map",
            assumptions=("tau is fixed",),
            error_kind="outward interval from the endpoint bracket",
        ),
        note="CMB window interval induced by the certified endpoint bracket.",
    )
    annotate_interval("kL_CMB", {"lo": lo, "hi": hi}, source="kL_interval",
                      note="linear propagation from the endpoint bracket")
    out["kL_CMB_interval"] = {
        "lo": lo, "hi": hi, "relative_width": (hi - lo) / kL_cmb}
    out["v_HIGGS_source"] = v_interval
    return out


if __name__ == "__main__":
    print(compute())
