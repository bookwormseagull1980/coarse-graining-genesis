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

"""Verification must bind the current run and isolate calculation scratch data."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import audit_numeric_stability as stability
from scripts import verify_v5 as verify


def test_stability_ignores_only_execution_identity():
    before = {"cg_params.json": {"x": {"value": 1., "run_id": "a", "note": "source rule"}}}
    after = {"cg_params.json": {"x": {"value": 1., "run_id": "b", "note": "source rule"}}}
    assert stability.compare_records(before, after) == []
    after["cg_params.json"]["x"]["note"] = "another rule"
    assert stability.compare_records(before, after)
    after["cg_params.json"]["x"]["note"] = "source rule"
    after["cg_params.json"]["x"]["value"] = 1.00000001
    assert stability.compare_records(before, after)


def test_stability_subprocess_has_explicit_temporary_destination(monkeypatch, tmp_path):
    captured = []
    def fake_run(command, **kwargs):
        captured.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")
    monkeypatch.setattr(stability.subprocess, "run", fake_run)
    stability.run_reproduce(tmp_path)
    command = captured[0]
    assert command[-2:] == ["--output-dir", str(tmp_path)]
    assert "--recompute-responses" in command
    assert tmp_path != ROOT


def test_stability_snapshot_includes_structured_response_records(tmp_path):
    (tmp_path / "comparison").mkdir()
    records = {
        "scale": {"value": 1., "run_id": "first"},
        "response_example": {
            "value": {"eigenvalues": [1., 3.], "certified": True},
            "run_id": "first",
            "calculation": {"run_id": "first", "source_sha256": {"operator.py": "abc"}}},
    }
    path = tmp_path / "cg_params.json"
    path.write_text(json.dumps({"parameters": records}), encoding="utf-8")
    (tmp_path / "comparison/reference_inputs.json").write_text(
        json.dumps({"parameters": {"observation": {"value": 2.}}}), encoding="utf-8")
    before = stability.snapshot(tmp_path)
    assert set(before) == {"cg_params.json", "comparison/reference_inputs.json"}
    assert "response_example" in before["cg_params.json"]
    records["response_example"]["run_id"] = "second"
    records["response_example"]["calculation"]["run_id"] = "second"
    path.write_text(json.dumps({"parameters": records}), encoding="utf-8")
    assert stability.compare_records(before, stability.snapshot(tmp_path)) == []
    records["response_example"]["value"]["eigenvalues"][1] = 4.
    path.write_text(json.dumps({"parameters": records}), encoding="utf-8")
    changes = stability.compare_records(before, stability.snapshot(tmp_path))
    assert len(changes) == 1
    assert "cg_params.json:response_example:" in changes[0]


def _refresh_output_hashes(root):
    manifest_path = root / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["output_sha256"] = {
        name: hashlib.sha256((root/name).read_bytes()).hexdigest()
        for name in ("cg_params.json", "comparison/reference_inputs.json")}
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def _fake_manifest(root, monkeypatch):
    (root / "cg_core").mkdir()
    source = root / "cg_core" / "example.py"
    source.write_text("value = 1\n", encoding="utf-8")
    def sources():
        return {"cg_core/example.py": hashlib.sha256(source.read_bytes()).hexdigest()}
    monkeypatch.setattr(verify, "RESPONSE_NAMES", ("example",))
    monkeypatch.setattr(verify, "response_source_identities", lambda: {"example": sources()})
    response = {"amplitude": 2.0}
    records = {
        "x": {"value": 1., "provenance": "DERIVED", "run_id": "test-run"},
        "response_example": {
            "value": response, "provenance": "DERIVED", "run_id": "test-run",
            "calculation": {"source_sha256": sources()},
            "direct_inputs": {"x": verify.value_fingerprint(1.)}},
        "response_validation": {
            "value": {"checks": {"example": True}, "all_checks_passed": True},
            "provenance": "DERIVED", "run_id": "test-run",
            "direct_inputs": {"response_example": verify.value_fingerprint(response)}},
    }
    files = {"cg_params.json": {"parameters": records},
             "comparison/reference_inputs.json": {"parameters": {}}}
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
    verification_sources = {
        "tests/test_example.py": "def test_example():\n    assert True\n",
        "lean_proofs/example.lean": "theorem identity : 1 = 1 := rfl\n",
        "pyproject.toml": '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n',
        "requirements.txt": "numpy>=1.24\n",
    }
    for name, text in verification_sources.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    manifest = {
        "publication": verify.publication_metadata(),
        "storage_contract": verify.storage_contract(),
        "solver_execution_identity": verify.solver_execution_identity(root),
        "run_id": "test-run", "status": "complete computational run",
        "source_sha256": sources(),
        "verification_source_sha256": {
            name: hashlib.sha256((root/name).read_bytes()).hexdigest()
            for name in verification_sources},
        "external_input_sha256": verify.external_input_fingerprints(root),
        "output_sha256": {
            name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}}
    (root / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return source


def test_current_manifest_detects_source_or_output_changes(tmp_path, monkeypatch):
    source = _fake_manifest(tmp_path, monkeypatch)
    assert verify.validate_run_manifest(tmp_path)["ok"]
    source.write_text("value = 2\n", encoding="utf-8")
    assert not verify.validate_run_manifest(tmp_path)["ok"]
    source.write_text("value = 1\n", encoding="utf-8")
    records_path = tmp_path / "cg_params.json"
    records = json.loads(records_path.read_text(encoding="utf-8"))
    records["parameters"]["x"]["run_id"] = "other"
    records_path.write_text(json.dumps(records), encoding="utf-8")
    result = verify.validate_run_manifest(tmp_path)
    assert not result["ok"]
    assert "another run" in result["output"]


def test_manifest_rejects_external_identity_mismatch(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["external_input_sha256"]["CAMB_execution"] = "another-execution"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = verify.validate_run_manifest(tmp_path)
    assert not result["ok"]
    assert "external input fingerprints differ" in result["output"]


def test_current_report_has_one_stable_location():
    assert verify.DEFAULT_REPORT == ROOT / "V5_VERIFICATION_REPORT.md"


def _audit_reproduction(root):
    path = root / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["audits"] = {
        name: {"returncode": 0, "ok": True, "cmd": "python scripts/" + name,
               "summary": "Completed the declared audit."}
        for name in ("audit_param_writers.py", "audit_observation_leakage.py")}
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return {"ok": True, "returncode": 0,
            "output": "COMPLETE: test-run; outputs published\n"}


def test_source_audits_reuse_only_the_same_validated_reproduction(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    reproduction = _audit_reproduction(tmp_path)
    executed = []
    monkeypatch.setattr(verify, "run", lambda label, cmd: executed.append(label))
    results = verify.run_source_audits(reproduction, tmp_path)
    assert all(item["ok"] for item in results)
    assert not executed
    assert all("Executed once" in item["summary"] for item in results[1:])
    saved = verify.record_verification(results, [], tmp_path)
    assert all("Executed once" in item["summary"] for item in saved["checks"][1:])
    assert verify.verification_state(tmp_path)["status"] == "PASS"


def test_source_audits_execute_without_reproduction_or_with_stale_identity(tmp_path, monkeypatch):
    source = _fake_manifest(tmp_path, monkeypatch)
    reproduction = _audit_reproduction(tmp_path)
    executed = []
    def actual_audit(label, command):
        executed.append(label)
        return {**_executed_check(), "label": label, "cmd": " ".join(command)}
    monkeypatch.setattr(verify, "run", actual_audit)
    for previous in (None, {**reproduction, "ok": False, "returncode": 1},
                     {**reproduction, "output": "COMPLETE: previous-run; outputs published\n"}):
        executed.clear()
        checks = verify.run_source_audits(previous, tmp_path)
        assert len(executed) == 2
        assert checks[0]["ok"]
    source.write_text("value = 2\n", encoding="utf-8")
    executed.clear()
    checks = verify.run_source_audits(reproduction, tmp_path)
    assert len(executed) == 2
    assert not checks[0]["ok"]


def test_source_audit_reuse_requires_successful_exact_command_metadata(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    reproduction = _audit_reproduction(tmp_path)
    path = tmp_path / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    saved = dict(manifest["audits"]["audit_param_writers.py"])
    executed = []
    def actual_audit(label, command):
        executed.append(label)
        return {**_executed_check(), "label": label, "cmd": " ".join(command)}
    monkeypatch.setattr(verify, "run", actual_audit)
    for change in ({"returncode": 1, "ok": False}, {"returncode": False},
                   {"cmd": "python another_script.py"}, {"summary": ""}):
        manifest["audits"]["audit_param_writers.py"] = {**saved, **change}
        path.write_text(json.dumps(manifest), encoding="utf-8")
        executed.clear()
        checks = verify.run_source_audits(reproduction, tmp_path)
        assert checks[0]["ok"]
        assert executed == ["parameter provenance audit"]
        assert "Executed once" in checks[2]["summary"]


def test_core_scope_is_explicit_and_does_not_claim_full_test_coverage(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    commands, published = [], []
    def actual_check(label, command, **kwargs):
        commands.append((label, command))
        return {**_executed_check(), "label": label, "cmd": " ".join(command),
                "output": "12 passed, 8 deselected"}
    original_record = verify.record_verification
    def save(results, omitted):
        published.append(original_record(results, omitted, tmp_path))
    monkeypatch.setattr(verify, "record_verification", save)
    monkeypatch.setattr(verify, "run", actual_check)
    monkeypatch.setattr(verify, "run_source_audits", lambda reproduction: [_executed_check()])
    monkeypatch.setattr(verify, "validate_run_manifest", lambda *a, **k: _executed_check())
    monkeypatch.setattr(verify, "report_text", lambda results, omitted: "Checks recorded.")
    monkeypatch.setattr(sys, "argv", ["verify_v5.py", "--no-reproduce", "--pytest",
                                     "--test-scope", "core", "--skip-full-comparison",
                                     "--report", str(tmp_path / "report.md")])
    assert verify.main() == 0
    label, command = next(item for item in commands if item[0].startswith("pytest"))
    assert label == "pytest (core)"
    assert command[command.index("-m", command.index("pytest")) + 1] == (
        "not release_audit and not numerical and not auxiliary")
    record = published[0]
    assert any("Numerical-certification and auxiliary" in item for item in record["not_executed"])
    test_check = next(item for item in record["checks"] if item["label"].startswith("pytest"))
    assert test_check["summary"] == "Core suite: 12 passed; 8 deselected."


def test_scope_option_requires_test_execution(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["verify_v5.py", "--test-scope", "core"])
    with pytest.raises(SystemExit) as stopped:
        verify.main()
    assert stopped.value.code == 2


def test_report_sanitizes_temporary_paths_in_failure_output():
    temporary = str(Path(tempfile.gettempdir()) / "verification-case" / "result.html")
    for path in (temporary, temporary.replace("\\", "/"), temporary.replace("\\", "\\\\")):
        sanitized = verify.sanitize_output("failed at " + path)
        assert "<temporary>" in sanitized
        assert tempfile.gettempdir() not in sanitized


def test_report_sanitizes_python_library_paths_in_failure_output():
    for runtime_root in {Path(sys.executable).resolve().parent, Path(sys.prefix), Path(sys.base_prefix)}:
        library_path = str(runtime_root / "Lib" / "json" / "encoder.py")
        for path in (library_path, library_path.replace("\\", "/"),
                     library_path.replace("\\", "\\\\")):
            sanitized = verify.sanitize_output(path + ":203: MemoryError")
            assert "<python-runtime>" in sanitized
            assert "encoder.py:203: MemoryError" in sanitized
            assert str(runtime_root) not in sanitized
            assert runtime_root.as_posix() not in sanitized


def test_report_sanitizes_json_escaped_unicode_paths(monkeypatch):
    root = Path.cwd() / "用户" / "论文" / "Framework"
    monkeypatch.setattr(verify, "ROOT", root)
    for separator in ("\\", "/"):
        path = str(root / "certificates" / "structure_certificates.json")
        path = path.replace("\\", separator).replace("/", separator)
        for ascii_only in (True, False):
            output = json.dumps({"output": path}, ensure_ascii=ascii_only)
            sanitized = verify.sanitize_output(output)
            relative = json.loads(sanitized)["output"]
            assert relative == "." + separator + "certificates" + separator + "structure_certificates.json"
            assert "用户" not in sanitized
            assert "\\u7528" not in sanitized


def test_manifest_detects_changed_verification_sources(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    assert verify.validate_run_manifest(tmp_path)["ok"]
    for name in ("tests/test_example.py", "lean_proofs/example.lean",
                 "pyproject.toml", "requirements.txt"):
        path = tmp_path / name
        original = path.read_bytes()
        path.write_bytes(original+b"\n")
        assert not verify.validate_run_manifest(tmp_path)["ok"], name
        path.write_bytes(original)
    added = tmp_path / "tests/test_additional.py"
    added.write_text("def test_additional():\n    assert True\n", encoding="utf-8")
    assert not verify.validate_run_manifest(tmp_path)["ok"]
    added.unlink()
    (tmp_path / "tests/test_example.py").unlink()
    assert not verify.validate_run_manifest(tmp_path)["ok"]


def test_manifest_requires_actual_response_success_even_with_current_hash(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    result_path = tmp_path / "cg_params.json"
    records = json.loads(result_path.read_text(encoding="utf-8"))
    records["parameters"]["response_validation"]["value"]["checks"]["example"] = False
    result_path.write_text(json.dumps(records), encoding="utf-8")
    _refresh_output_hashes(tmp_path)
    result = verify.validate_run_manifest(tmp_path)
    assert not result["ok"]
    assert "unpassed required check" in result["output"]


def test_manifest_binds_each_response_to_its_actual_scientific_inputs(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    path = tmp_path / "cg_params.json"
    store = json.loads(path.read_text(encoding="utf-8"))
    store["parameters"]["x"]["value"] = 1.25
    path.write_text(json.dumps(store), encoding="utf-8")
    _refresh_output_hashes(tmp_path)
    result = verify.validate_run_manifest(tmp_path)
    assert not result["ok"]
    assert "response direct-input mismatch: response_example <- x" in result["output"]


def test_manifest_checks_response_content_and_completeness(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    path = tmp_path / "cg_params.json"
    store = json.loads(path.read_text(encoding="utf-8"))
    store["parameters"]["response_example"]["value"]["amplitude"] = 4.
    path.write_text(json.dumps(store), encoding="utf-8")
    _refresh_output_hashes(tmp_path)
    assert "response direct-input mismatch: response_validation" in verify.validate_run_manifest(tmp_path)["output"]
    del store["parameters"]["response_example"]
    path.write_text(json.dumps(store), encoding="utf-8")
    _refresh_output_hashes(tmp_path)
    assert "missing unified response record" in verify.validate_run_manifest(tmp_path)["output"]


def test_manifest_checks_response_calculation_identity(tmp_path, monkeypatch):
    source = _fake_manifest(tmp_path, monkeypatch)
    source.write_text("value = 2\n", encoding="utf-8")
    path = tmp_path / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["source_sha256"]["cg_core/example.py"] = hashlib.sha256(source.read_bytes()).hexdigest()
    path.write_text(json.dumps(manifest), encoding="utf-8")
    result = verify.validate_run_manifest(tmp_path)
    assert not result["ok"]
    assert "response calculation source mismatch" in result["output"]


def _executed_check(ok=True):
    return {"label": "independent identity", "cmd": "fixture verification",
            "required": True, "ok": ok, "returncode": 0 if ok else 1,
            "output": "identity checked", "seconds": 3.0}


def test_structured_verification_records_executed_scope_and_rejects_stale_binding(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    omitted = ["Lean archive compilation"]
    published = verify.record_verification([_executed_check()], omitted, tmp_path)
    assert published["status"] == "PASS"
    assert "seconds" not in published["checks"][0]
    state = verify.verification_state(tmp_path)
    assert state["status"] == "PASS"
    assert state["not_executed"] == omitted
    assert len(state["checks"]) == 1
    path = tmp_path / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["output_sha256"]["cg_params.json"] = "different-output"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify.verification_state(tmp_path)["status"] == "stale run"


def test_structured_verification_rejects_false_pass_and_changed_science(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    verify.record_verification([_executed_check()], [], tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["verification"]["checks"][0].update(ok=False, returncode=1)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify.verification_state(tmp_path)["status"] == "invalid verification"
    manifest["verification"]["status"] = "FAIL"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    assert verify.verification_state(tmp_path)["status"] == "FAIL"
    result_path = tmp_path / "cg_params.json"
    store = json.loads(result_path.read_text(encoding="utf-8"))
    store["parameters"]["x"]["value"] = 2.
    result_path.write_text(json.dumps(store), encoding="utf-8")
    assert verify.verification_state(tmp_path)["status"] == "stale run"


def test_structured_verification_needs_no_markdown_report(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    assert verify.verification_state(tmp_path)["status"] == "not verified"
    verify.record_verification([_executed_check()], [], tmp_path)
    assert not (tmp_path / "V5_VERIFICATION_REPORT.md").exists()
    assert verify.verification_state(tmp_path)["status"] == "PASS"


@pytest.mark.parametrize("field", ["parameters", "response_results", "comparison_results"])
def test_manifest_rejects_scientific_payload_with_matching_store_hashes(tmp_path, monkeypatch, field):
    _fake_manifest(tmp_path, monkeypatch)
    path = tmp_path / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest[field] = {"physical_value": 1.25}
    result = verify.validate_run_manifest(tmp_path, manifest=manifest)
    assert not result["ok"]
    assert "unsupported payload fields" in result["output"]


def test_manifest_rejects_third_scientific_store_even_with_valid_hash(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    sidecar = tmp_path / "sector_results.json"
    sidecar.write_text('{"parameters":{"density":{"value":1.25}}}', encoding="utf-8")
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    manifest["output_sha256"][sidecar.name] = hashlib.sha256(sidecar.read_bytes()).hexdigest()
    result = verify.validate_run_manifest(tmp_path, manifest=manifest)
    assert not result["ok"]
    assert "two unified output stores" in result["output"]
    manifest["storage_contract"]["scientific_stores"][sidecar.name] = "computed density"
    result = verify.validate_run_manifest(tmp_path, manifest=manifest)
    assert "exactly the two scientific stores" in result["output"]


def test_manifest_rejects_payload_inside_verification_check(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    verify.record_verification([_executed_check()], [], tmp_path)
    manifest = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    manifest["verification"]["checks"][0]["scientific_results"] = {"density": 1.25}
    result = verify.validate_run_manifest(tmp_path, manifest=manifest)
    assert not result["ok"]
    assert "check contains unsupported payload fields" in result["output"]


def test_manifest_success_omits_calculation_tables_and_failure_keeps_diagnostics(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    check = _executed_check()
    check["output"] = "physical-value-table: Y_p=0.25; H_0=70"
    saved = verify.record_verification([check], [], tmp_path)
    assert "output" not in saved["checks"][0]
    assert "physical-value-table" not in json.dumps(saved)
    assert saved["checks"][0]["cmd"] == check["cmd"]
    check.update(ok=False, returncode=1, output="mass conservation residual exceeds tolerance")
    saved = verify.record_verification([check], [], tmp_path)
    assert saved["checks"][0]["output"] == check["output"]
    assert verify.verification_state(tmp_path)["status"] == "FAIL"


def test_all_reference_values_are_fingerprinted_and_camb_identity_uses_computed_store(tmp_path, monkeypatch):
    _fake_manifest(tmp_path, monkeypatch)
    reference_path = tmp_path / "comparison/reference_inputs.json"
    observations = {"DESI_DR2_BAO": {"value": {"observed": [1., 2.]}},
                    "CMB_MONOPOLE": {"value": {"temperature": 2.7}},
                    "mass_reference": {"value": 1.25}}
    reference_path.write_text(json.dumps({"parameters": observations}), encoding="utf-8")
    computed_path = tmp_path / "cg_params.json"
    computed = json.loads(computed_path.read_text(encoding="utf-8"))
    computed["parameters"]["endpoint_camb_record"] = {
        "value": {"execution_sha256": "a"*64, "result": {"density": 2.}}}
    computed_path.write_text(json.dumps(computed), encoding="utf-8")
    identity = verify.solver_execution_identity(tmp_path)
    assert identity == {"CAMB": {"store": "cg_params.json", "record": "endpoint_camb_record",
                                 "field": "execution_sha256", "sha256": "a"*64}}
    fingerprints = verify.external_input_fingerprints(tmp_path)
    assert fingerprints["CAMB_execution"] == "a"*64
    assert fingerprints["reference_records"] == {
        key: verify.value_fingerprint(record["value"]) for key, record in observations.items()}
    assert fingerprints["DESI_DR2_BAO"] == fingerprints["reference_records"]["DESI_DR2_BAO"]
    observations["CMB_MONOPOLE"]["value"]["temperature"] = 2.8
    reference_path.write_text(json.dumps({"parameters": observations}), encoding="utf-8")
    changed = verify.external_input_fingerprints(tmp_path)
    assert changed["reference_records"]["CMB_MONOPOLE"] != fingerprints["reference_records"]["CMB_MONOPOLE"]
    assert verify.solver_execution_identity(tmp_path) == identity
    from cg_core.params import prediction_inputs_only
    with prediction_inputs_only(), pytest.raises(ValueError, match="document access"):
        verify.external_input_fingerprints(tmp_path)
