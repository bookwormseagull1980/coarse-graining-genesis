# -*- coding: utf-8 -*-
"""Production interval propagation contracts."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get, read_store_document  # noqa: E402


def test_bbn_yield_interval_contains_production():
    interval = get("bbn_yield_interval")
    tau = interval["tau_n_interval_s"]
    Yp = interval["Yp_interval"]
    assert tau["lo"] <= interval["production_tau_n_s"] <= tau["hi"]
    assert Yp["lo"] <= interval["production_Yp"] <= Yp["hi"]
    records = read_store_document("parameters")["parameters"]
    tau_record = records["bbn_tau_n"]
    Yp_record = records["bbn_Yp"]
    assert tau_record["interval"]["lo"] <= float(tau_record["value"])
    assert Yp_record["interval"]["hi"] >= float(Yp_record["value"])


def test_linear_production_intervals_contain_centres():
    for interval_name, value_name in (
            ("M_Z_pred_interval", "M_Z_pred"),
            ("m_t_pred_interval", "m_t_pred"),
            ("m_b_pred_interval", "m_b_pred"),
            ("m_mu_pred_interval", "m_mu_pred"),
            ("m_tau_pred_interval", "m_tau_pred"),
            ("geometric_ewsb_m_WR_interval", "geometric_ewsb_m_WR"),
            ("kL_CMB_interval", "kL_CMB")):
        interval = get(interval_name)
        value = float(get(value_name))
        assert interval["lo"] <= value <= interval["hi"]
        record = read_store_document("parameters")["parameters"][value_name]
        assert record["interval"]["lo"] <= value
