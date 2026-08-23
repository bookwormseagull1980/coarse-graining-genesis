# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""Unit tests: the parameter store API (cg_core.params).

The store is the framework's single parameter exchange mechanism
(cg_params.json); these tests verify the API contract and the audit
provenance discipline.
"""
import json
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Store-file integrity (structure-level)
# ---------------------------------------------------------------------------
def test_store_file_exists_and_valid():
    path = _PROJECT_ROOT / "cg_params.json"
    assert path.exists(), "cg_params.json missing — run scripts/reproduce_v4.py first"
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
            assert field in rec and rec[field] not in (None, ""), \
                f"{key}: missing field '{field}'"


def test_anchor_provenance():
    """The single observed anchor (G_N_PDG) must be OBSERVED/anchor."""
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    g = data["parameters"]["G_N_PDG"]
    assert g["provenance"] == "OBSERVED"
    assert g["role"] == "anchor"


def test_no_orphan_writer_keys():
    """No record may claim a writer that no longer exists in the code.

    (Regression: V_us_gatto_obs, g2_conservation_lhs, g2_residual_1Nc,
    geometric_ewsb_ratio_obs were orphaned and removed 2026-08-21.)
    """
    path = _PROJECT_ROOT / "cg_params.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("V_us_gatto_obs", "g2_conservation_lhs",
                "g2_residual_1Nc", "geometric_ewsb_ratio_obs"):
        assert key not in data["parameters"], f"orphan key still present: {key}"


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
    for key in ("G_N_pred", "Gamma_Z_pred", "M_W_pred", "m_H_pred"):
        rec = data["parameters"][key]
        assert "observed" in rec, f"{key}: comparison record missing observed"
        assert "deviation_pct" in rec, f"{key}: comparison record missing deviation_pct"


def test_sm_table_is_separate():
    """The SM comparison table lives in sm_inputs.json, not cg_params.json."""
    sm_path = _PROJECT_ROOT / "comparison" / "sm_inputs.json"
    assert sm_path.exists()
    data = json.loads(sm_path.read_text(encoding="utf-8"))
    sm = data["parameters"]
    # Spot-check: observed values present with SM_INPUT provenance.
    assert sm["M_Z"]["provenance"] == "SM_INPUT"
    assert sm["m_W_obs"]["provenance"] == "SM_INPUT"
