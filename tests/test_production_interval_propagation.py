# -*- coding: utf-8 -*-
"""Production interval propagation contracts."""

from __future__ import annotations

import sys
import math
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get, read_store_document  # noqa: E402
from cg_frg.framework.production_interval_propagation import lepton_endpoint_enclosures  # noqa: E402


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


def test_lepton_endpoint_intervals_enclose_the_actual_production_chain():
    from cg_frg.fermion.electron_mass import m_e_planck
    from cg_frg.generation.sector_alpha import alpha_up, sector_step, ladder_lepton

    endpoint = get("kL_interval")
    M_P, tau, tilt = (float(get(key)) for key in ("M_P", "tau", "ns_tilt"))
    bounds = lepton_endpoint_enclosures(endpoint, M_P=M_P, tau=tau, ns_tilt=tilt)
    s = 2*tau
    squash = 1-s*math.sqrt((1+s)/(1-2*s)**2.5)
    for c in (endpoint["lo"], float(get("kL")), endpoint["hi"]):
        electron = m_e_planck(M_P, c)*squash/1000
        alpha = ladder_lepton(alpha_up(c, tau), sector_step(tilt, c*(1-tau/4)))
        muon = electron*math.exp(2*alpha+math.sqrt(2*math.pi))
        actual = {"m_mu_pred": muon, "m_tau_pred": muon*math.exp(2*alpha)}
        for name, value in actual.items():
            assert bounds[name]["lo"] <= value <= bounds[name]["hi"]


def test_production_uses_the_complete_lepton_endpoint_bounds(monkeypatch):
    from cg_frg.framework import production_interval_propagation as module

    published, attached = {}, {}
    monkeypatch.setattr(module, "z_endpoint_response", lambda *args, **kwargs: {
        "samples": [{}, {"M_Z_GeV": float(get("M_Z_pred"))}, {}],
        "certified_enclosure": False})
    monkeypatch.setattr(module, "pset", lambda name, value, **metadata:
                        published.update({name: (value, metadata)}))
    monkeypatch.setattr(module, "annotate_interval", lambda name, value, **metadata:
                        attached.update({name: (value, metadata)}))
    result = module.compute()
    for name, (_, metadata) in published.items():
        assert metadata.get("note"), name
        assert metadata["definition"].error_kind, name
    expected = lepton_endpoint_enclosures(get("kL_interval"), **{
        key: get(key) for key in ("M_P", "tau", "ns_tilt")})
    for name, interval in expected.items():
        value, metadata = published[name+"_interval"]
        assert value["source"] == "kL_interval"
        assert result[name+"_interval"]["lo"] == interval["lo"]
        assert result[name+"_interval"]["hi"] == interval["hi"]
        assert metadata["dependencies"] == ("kL_interval", "M_P", "tau", "ns_tilt", name)
        assert attached[name][1]["source"] == "kL_interval"


def test_bottom_endpoint_interval_retains_the_down_ladder():
    from cg_frg.framework.production_interval_propagation import bottom_endpoint_enclosure
    from cg_core.joint_response import evaluate
    inputs = {key: float(get(key)) for key in ("M_P", "tau", "ns_tilt")}
    endpoint = get("kL_interval")
    bound = bottom_endpoint_enclosure(endpoint, **inputs)
    for c in (endpoint["lo"], float(get("kL")), endpoint["hi"]):
        p = evaluate(c, inputs["tau"], inputs["M_P"])
        actual = p["m_t_pred"]*math.exp(-2*p["alpha_down"]
                    +inputs["ns_tilt"]*(c*(1-inputs["tau"]/4)+2*inputs["tau"]))
        assert bound["lo"] <= actual <= bound["hi"]


def test_z_response_recomputes_all_three_gauge_boundaries(monkeypatch):
    from cg_core import gauge_running, joint_response
    from cg_frg.ewsb import ew_precision
    from cg_frg.framework.production_interval_propagation import z_endpoint_response
    evaluated, shot, solved = [], [], []
    def evaluate(c, tau, mp):
        evaluated.append(c)
        return {"g1_MG_geo": c, "g2_MG": c+1, "M_G": mp/c,
                "k_GUT": mp*tau, "v_HIGGS": c+2}
    def origin(g1, g2, mg, gut):
        shot.append((g1, g2, mg, gut))
        return {"g3_initial": g1+2, "relative_residual": 0.}
    def fixed(v, g1, g2, g3, mg):
        solved.append((v, g1, g2, g3, mg))
        return v+g1+g2+g3, g1, g2, g3
    monkeypatch.setattr(joint_response, "evaluate", evaluate)
    monkeypatch.setattr(gauge_running, "common_origin", origin)
    monkeypatch.setattr(ew_precision, "mz_fixed_point", fixed)
    result = z_endpoint_response({"lo": 2., "hi": 3.}, centre=2.5, M_P=100., tau=.02)
    assert evaluated == [2., 2.5, 3.]
    assert [row[3] for row in solved] == [4., 4.5, 5.]
    assert len(shot) == 3
    assert result["certified_enclosure"] is False
    assert result["sample_range_GeV"] == [13., 17.]


def test_right_weak_interval_retains_the_generated_weak_boundary():
    from cg_frg.framework.production_interval_propagation import right_weak_endpoint_enclosure
    from cg_core.joint_response import evaluate
    endpoint = get("kL_interval")
    M_P, tau = float(get("M_P")), float(get("tau"))
    bound = right_weak_endpoint_enclosure(endpoint, M_P=M_P, tau=tau)
    for c in (endpoint["lo"], float(get("kL")), endpoint["hi"]):
        p = evaluate(c, tau, M_P)
        assert bound["lo"] <= p["g2_MG"]*2*tau*p["M_G"] <= bound["hi"]
