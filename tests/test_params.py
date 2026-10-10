# -*- coding: utf-8 -*-
# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""Unit tests: the parameter store API (cg_core.params).

The store is the framework's single parameter exchange mechanism
(cg_params.json); these tests verify the API contract and the audit
provenance requirements.
"""
import json
from pathlib import Path

import pytest
from cg_core.params import get

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_document_interface_uses_only_the_two_canonical_stores(tmp_path):
    from cg_core.params import read_store_document, prediction_inputs_only
    (tmp_path / "comparison").mkdir()
    scientific = {"parameters": {"calculated": {"value": 2}}}
    reference = {"parameters": {"observed": {"value": 3}}}
    (tmp_path / "cg_params.json").write_text(json.dumps(scientific), encoding="utf-8")
    (tmp_path / "comparison" / "reference_inputs.json").write_text(
        json.dumps(reference), encoding="utf-8")
    assert read_store_document(source_root=tmp_path) == scientific
    assert read_store_document("references", source_root=tmp_path) == reference
    with pytest.raises(ValueError, match="unknown store"):
        read_store_document("sidecar.json", source_root=tmp_path)
    for identity in ("parameters", "references"):
        with prediction_inputs_only(), pytest.raises(ValueError, match="document access"):
            read_store_document(identity, source_root=tmp_path)


def test_reference_document_has_no_alternative_file_fallback(tmp_path):
    from cg_core.params import read_store_document
    (tmp_path / "comparison").mkdir()
    (tmp_path / "comparison" / "alternative.json").write_text(
        '{"parameters": {"observed": {"value": 3}}}', encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        read_store_document("references", source_root=tmp_path)


# ---------------------------------------------------------------------------
# Store-file integrity (structure-level)
# ---------------------------------------------------------------------------
def test_store_file_exists_and_valid():
    path = _PROJECT_ROOT / "cg_params.json"
    assert path.exists(), "cg_params.json missing — run scripts/reproduce_v5.py first"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert "parameters" in data
    assert isinstance(data["parameters"], dict)
    assert len(data["parameters"]) > 100


def test_every_record_has_required_fields():
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, rec in data["parameters"].items():
        assert isinstance(rec, dict), f"{key}: record not a dict"
        for field in ("value", "provenance", "writer", "note"):
            if field == "value" and "reference" in rec:
                from cg_core.params import resolve_value
                assert "value" not in rec
                assert resolve_value(rec["reference"], data["parameters"], (key,)) is not None
                continue
            if field == "value" and rec.get("provenance") == "PENDING":
                assert rec["role"] == "informational" and rec["note"]
                with pytest.raises(KeyError):
                    get(key)
                continue
            assert field in rec and rec[field] not in (None, ""), \
                f"{key}: missing field '{field}'"


def test_anchor_provenance():
    """The single observed anchor (G_N_PDG) must be OBSERVED/anchor."""
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    g = data["parameters"]["G_N_PDG"]
    assert g["provenance"] == "OBSERVED"
    assert g["role"] == "anchor"


def test_record_writer_exists():
    """Every parameter identifies a source file distributed with the framework."""
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, record in data["parameters"].items():
        writer = (_PROJECT_ROOT / record["writer"]).resolve()
        assert writer.is_relative_to(_PROJECT_ROOT.resolve()), key
        assert writer.is_file(), f"{key}: missing source file {record['writer']}"


# ---------------------------------------------------------------------------
# API contract (cg_core.params)
# ---------------------------------------------------------------------------
def test_get_reads_store_value():
    from cg_core.params import get
    kL = get("kL")
    assert 2.0 < kL < 3.0          # the fixed point lies in the window band
    assert abs(kL - 2.4935343325226915) < 1e-9


def test_get_raises_on_missing_key():
    from cg_core.params import get
    with pytest.raises(KeyError):
        get("this_key_does_not_exist_xyz")


def test_compare_and_set_contract():
    """compare_and_set stores value+observed+deviation_pct together."""
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("Gamma_Z_pred", "M_W_pred", "m_H_pred"):
        rec = data["parameters"][key]
        assert "observed" in rec, f"{key}: comparison record missing observed"
        assert "deviation_pct" in rec, f"{key}: comparison record missing deviation_pct"


def test_gravity_readout_is_not_an_independent_newton_prediction():
    """The gravitational readout uses the declared dimensional anchor."""
    from cg_core.params import store_root
    records = json.loads((store_root() / "cg_params.json").read_text(encoding="utf-8"))["parameters"]
    for key in ("gravity_G_read", "gravity_Z_read"):
        assert key in records, f"required gravitational readout missing: {key}"
        record = records[key]
        assert record["provenance"] == "DERIVED"
        assert "observed" not in record
        assert "deviation_pct" not in record
        assert record["value"] > 0
    assert records["G_N_PDG"]["role"] == "anchor"


def test_sm_table_is_separate():
    """Reference data use the canonical isolated comparison store."""
    sm_path = _PROJECT_ROOT / "comparison" / "reference_inputs.json"
    assert sm_path.exists()
    data = json.loads(sm_path.read_text(encoding="utf-8"))
    sm = data["parameters"]
    # Spot-check: observed values present with SM_INPUT provenance.
    assert sm["M_Z"]["provenance"] == "SM_INPUT"
    assert sm["m_W_obs"]["provenance"] == "SM_INPUT"


def test_empty_store_initialization_reads_registered_references(tmp_path, monkeypatch):
    from cg_core import params
    from comparison.sm_rge import inputs, run_rge
    from scripts import init_v5

    source = tmp_path / "published"
    destination = tmp_path / "calculation"
    reference_path = source / "comparison" / "reference_inputs.json"
    reference_keys = set(inputs.SM_INPUT_KEYS) | set(init_v5.FOUNDATION_REFERENCE_KEYS)
    references = {key: {"value": params.published_sm_value(key)} for key in reference_keys}
    references["M_Z"]["value"] *= 1.01
    references["v_HIGGS"]["value"] *= 1.02
    params.write_json_atomic(reference_path, {"parameters": references})
    monkeypatch.setenv("V5_REFERENCE_DIR", str(source))
    monkeypatch.setattr(params, "_PARAM_FILE", destination / "cg_params.json")
    monkeypatch.setattr(params, "_SM_FILE", destination / "comparison" / "reference_inputs.json")
    flow_calls = []
    monkeypatch.setattr(run_rge, "run_sm_table", lambda *args: flow_calls.append(args))

    init_v5.init()
    assert flow_calls[0][0] == references["M_Z"]["value"]
    assert flow_calls[0][3] == references["v_HIGGS"]["value"]
    inputs.init_sm_table()
    assert all(params.sm_value(key) == references[key]["value"] for key in reference_keys)
    assert not (reference_keys & params.all_records().keys())


def test_prediction_snapshot_enforces_roles_and_tracks_exact_reads():
    from cg_core.params import PredictionRecords, prediction_inputs_only, input_scope, value_fingerprint
    records = {
        "input": {"value": 3., "provenance": "DERIVED", "role": "internal"},
        "measurement": {"value": 7., "provenance": "SM_INPUT", "role": "comparison"},
        "hidden_measurement": {"reference": {"$ref": "measurement"},
                               "provenance": "DERIVED", "role": "internal"},
        "diagnostic": {"value": 2., "provenance": "DERIVED", "role": "comparison"},
    }
    snapshot = PredictionRecords(records)
    with prediction_inputs_only(), input_scope() as reads:
        assert snapshot["input"]["value"] == 3.
        for key in ("measurement", "hidden_measurement", "diagnostic"):
            with pytest.raises(ValueError):
                snapshot[key]
        assert reads == {"input": value_fingerprint(3.)}
    snapshot["input"]["value"] = 9.
    assert snapshot["input"]["value"] == 3.


def test_parameter_projections_have_one_source_and_reject_cycles():
    from cg_core.params import resolve_value, resolved_records
    records = {"full": {"value": {"outputs": {"x": 2.}}},
               "x": {"reference": {"$ref": "full", "path": ["outputs", "x"]}}}
    assert resolved_records(records)["x"]["value"] == 2.
    records["full"]["value"]["outputs"]["x"] = 4.
    assert resolved_records(records)["x"]["value"] == 4.
    assert "value" not in records["x"]
    records["full"] = {"reference": {"$ref": "x"}}
    with pytest.raises(ValueError, match="cyclic"):
        resolve_value({"$ref": "x"}, records)


def test_checked_parameter_read_releases_source_records():
    import gc
    import weakref
    from cg_core.params import _checked_record

    class Records(dict):
        pass

    enabled = gc.isenabled()
    gc.disable()
    try:
        records = Records({
            "source": {"value": {"x": [3.]}, "provenance": "DERIVED", "role": "internal"},
            "alias": {"reference": {"$ref": "source", "path": ["x", 0]},
                      "provenance": "DERIVED", "role": "internal"},
        })
        reference = weakref.ref(records)
        result = _checked_record("alias", records)
        assert result["value"] == 3.
        del records
        assert reference() is None
    finally:
        if enabled:
            gc.enable()


def test_source_mode_change_marks_missing_and_chained_projections_pending(tmp_path, monkeypatch):
    from cg_core import params
    path = tmp_path / "parameters.json"
    params.write_json_atomic(path, {"parameters": {}})
    monkeypatch.setattr(params, "_PARAM_FILE", path)
    source = "endpoint_camb_record"
    full = {"outputs": {"r_drag_Mpc": 147., "S8_total_matter": .81}}
    params.record(source, full, role="comparison", note="Full propagation.")
    params.record_alias("endpoint_S8", source, ("outputs", "S8_total_matter"))
    params.record_alias("endpoint_r_drag_Mpc", source, ("outputs", "r_drag_Mpc"))
    params.record_alias("S8_display", "endpoint_S8")
    background = {"outputs": {"r_drag_Mpc": 146.9}}
    params.record(source, background, role="comparison", note="Thermal background.")
    records = params.all_records()
    assert records["endpoint_r_drag_Mpc"]["value"] == 146.9
    for key, parent, value in (("endpoint_S8", source, background),
                               ("S8_display", "endpoint_S8", None)):
        rec = records[key]
        assert rec["value"] is None and "reference" not in rec
        assert rec["provenance"] == "PENDING" and rec["role"] == "informational"
        assert rec["direct_inputs"] == rec["module_read_inputs"] == {
            parent: params.value_fingerprint(value)}
        with pytest.raises(KeyError, match="unavailable"):
            params.get(key)
    # A completed full calculation may publish its validated projections again.
    params.record(source, full, role="comparison", note="Full propagation.")
    params.record_alias("endpoint_S8", source, ("outputs", "S8_total_matter"))
    params.record_alias("S8_display", "endpoint_S8")
    assert params.get("S8_display") == .81
    assert params.get("endpoint_r_drag_Mpc") == 147.
    with pytest.raises(KeyError):
        params.record_alias("invalid_output", source, ("outputs", "missing"))
    assert "invalid_output" not in params.all_records()


def test_atomic_publication_fails_once_on_denied_access(tmp_path, monkeypatch):
    from cg_core import params
    attempts = []
    def denied(path, flags, mode):
        attempts.append(path)
        raise PermissionError("read-only destination")
    monkeypatch.setattr(params.os, "open", denied)
    with pytest.raises(PermissionError):
        params.write_bytes_atomic(tmp_path / "store.json", b"{}")
    assert len(attempts) == 1
    assert list(tmp_path.iterdir()) == []


def test_atomic_publication_preserves_complete_file_on_replace_failure(tmp_path, monkeypatch):
    from cg_core import params
    path = tmp_path / "store.json"
    path.write_bytes(b'{"value":1}')
    def denied(source, target):
        raise PermissionError("destination is locked")
    monkeypatch.setattr(params.os, "replace", denied)
    with pytest.raises(PermissionError):
        params.write_bytes_atomic(path, b'{"value":2}')
    assert path.read_bytes() == b'{"value":1}'
    assert list(tmp_path.iterdir()) == [path]
