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

"""The presentation reads completed verification without executing audits."""

import json
import re
import subprocess
import sys
from scripts import make_reviewer_dashboard as dashboard


def test_reviewer_dashboard_reads_one_structured_state_without_subprocesses(tmp_path, monkeypatch):
    out = tmp_path / "reviewer_dashboard.html"
    reads = []
    checks = [
        {"label": label, "ok": label != "path portability",
         "returncode": 0 if label != "path portability" else 1,
         "required": True, "cmd": "registered verification",
         "output": f"Recorded fixture: {label}"}
        for label in ("parameter provenance", "observation leakage",
                      "Lean source hygiene", "numeric precision", "path portability")]

    def saved_state(root, *, manifest):
        reads.append((root, manifest))
        return {"status": "FAIL", "checks": checks,
                "not_executed": ["Lean compilation"], "run_id": manifest.get("run_id")}

    def no_process(*args, **kwargs):
        raise AssertionError("dashboard generation must not execute a subprocess")

    monkeypatch.setattr(dashboard, "verification_state", saved_state)
    monkeypatch.setattr(subprocess, "run", no_process)
    monkeypatch.setattr(sys, "argv", ["make_reviewer_dashboard.py", "--output", str(out)])
    assert dashboard.main() == 0
    text = out.read_text(encoding="utf-8")
    assert "V5 Reviewer Dashboard" in text
    assert "Anchor-to-results tree" in text
    assert "treeSector" in text
    assert "anchor_tree" in text
    assert "G_N_PDG" in text
    assert "Recorded fixture: observation leakage" in text
    assert len(reads) == 1
    payload = json.loads(re.search(r"const DATA = (.*);", text).group(1))
    statuses = {item["label"]: item["ok"] for item in payload["audit_results"]}
    assert statuses["path portability"] is False
    assert statuses["observation leakage"] is True
    assert payload["verification_verdict"] == "FAIL"
    assert payload["not_executed"] == ["Lean compilation"]
    assert all("seconds" not in item for item in payload["audit_results"])


def test_dashboard_resolves_parameter_projections_in_memory(tmp_path, monkeypatch):
    (tmp_path / "comparison").mkdir()
    records = {
        "tensor_result": {"value": {"normalization": 4.0}, "provenance": "DERIVED"},
        "external_tensor_Z": {"reference": {"$ref": "tensor_result", "path": ["normalization"]},
                              "provenance": "DERIVED"},
    }
    path = tmp_path / "cg_params.json"
    path.write_text(json.dumps({"parameters": records}), encoding="utf-8")
    original = path.read_bytes()
    monkeypatch.setattr(dashboard, "ROOT", tmp_path)
    monkeypatch.setattr(dashboard, "scan_sources", lambda: {})
    monkeypatch.setattr(dashboard, "parse_reproduce_modules", lambda: [])
    monkeypatch.setattr(dashboard, "verification_state",
                        lambda *args, **kwargs: {"status": "not verified", "checks": [], "not_executed": []})
    data = dashboard.build_data()
    row = next(item for item in data["selected"] if item["key"] == "external_tensor_Z")
    assert row["value"] == "4.0"
    assert path.read_bytes() == original
