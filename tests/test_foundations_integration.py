"""Evidence binding between the independent proof audit and the V5 report.

The proof subprocesses use fixtures. These tests neither compile Lean nor
claim mathematical validation; compiler and dependency checks have their own
verification entry point.
"""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import verify_v5 as verify
from scripts.reproduce_v5 import verification_fingerprints


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def proof_root(tmp_path, monkeypatch):
    project = tmp_path / "proof-checkout"
    (project / "GeneratedFoundations" / "Nested").mkdir(parents=True)
    (project / "GeneratedFoundations.lean").write_text(
        "module\npublic import GeneratedFoundations.Nested.Basic\n", encoding="utf-8")
    (project / "GeneratedFoundations" / "Nested" / "Basic.lean").write_text(
        "module\n@[expose] public section\ntheorem identity : True := True.intro\n", encoding="utf-8")
    for name in ("lean-toolchain", "lakefile.lean", "lake-manifest.json", "theorem-index.json"):
        (project / name).write_text("fixture\n", encoding="utf-8")
    (project / ".lake").mkdir()
    (project / verify.foundations.AUDIT_LOG).write_text("fixture audit\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "verify_foundations.py").write_text("fixture adapter\n", encoding="utf-8")
    (project / "scripts").mkdir()
    (project / "scripts" / "verify_foundations.py").write_text(
        "import hashlib\n"
        "def fingerprint(project):\n"
        "    paths = [project / 'GeneratedFoundations.lean', *sorted((project / 'GeneratedFoundations').rglob('*.lean'))]\n"
        "    paths += [project / name for name in ('lean-toolchain', 'lakefile.lean', 'lake-manifest.json', 'theorem-index.json')]\n"
        "    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}\n",
        encoding="utf-8")
    for name in ("pyproject.toml", "requirements.txt"):
        (tmp_path / name).write_text("fixture\n", encoding="utf-8")
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setenv("FOUNDATIONS_PROJECT", str(project))
    pin = {"schema_version": 1, "name": verify.foundations.PUBLIC_NAME,
           "locator": verify.foundations.DEFAULT_LOCATOR,
           "source_files": fixture_fingerprint(project),
           "verifier": {"path": "scripts/verify_foundations.py", "sha256": hashlib.sha256(
               (project / "scripts" / "verify_foundations.py").read_bytes()).hexdigest()}}
    write_json(tmp_path / verify.foundations.REFERENCE_NAME, pin)
    publish_proof(tmp_path, "1" * 32)
    return tmp_path


def publish_proof(root, identity):
    project = root / "proof-checkout"
    record = {"kind": "generated-foundations-verification", "status": "passed",
              "scope": verify.FOUNDATIONS_SCOPE, "semantic_review": "not_certified",
              "verification_id": identity,
              "source_files": fixture_fingerprint(project),
              "verifier": {"path": "scripts/verify_foundations.py", "sha256": hashlib.sha256(
                  (project / "scripts" / "verify_foundations.py").read_bytes()).hexdigest()},
              "audit": {"path": verify.foundations.AUDIT_LOG, "sha256": hashlib.sha256(
                  (project / verify.foundations.AUDIT_LOG).read_bytes()).hexdigest()}}
    write_json(project / verify.foundations.MANIFEST_NAME, record)
    return record


def fixture_fingerprint(project):
    paths = [project / "GeneratedFoundations.lean",
             *sorted((project / "GeneratedFoundations").rglob("*.lean"))]
    paths += [project / name for name in ("lean-toolchain", "lakefile.lean",
                                         "lake-manifest.json", "theorem-index.json")]
    return {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def record_path(root):
    return root / "proof-checkout" / verify.foundations.MANIFEST_NAME


def successful_subprocess(label, command, **kwargs):
    return {"label": label, "cmd": kwargs.get("display_cmd", "fixture command"),
            "ok": True, "required": True, "returncode": 0, "output": "fixture success"}


def install_proof_run(root, monkeypatch):
    commands = []
    def execute(label, command, **kwargs):
        commands.append(command)
        if "--check-manifest" not in command:
            publish_proof(root, "2" * 32)
        return successful_subprocess(label, command, **kwargs)
    monkeypatch.setattr(verify, "run", execute)
    return commands


def test_new_full_audit_and_saved_record_check_are_both_required(proof_root, monkeypatch):
    commands = install_proof_run(proof_root, monkeypatch)
    result = verify.run_foundations("pinned-lake.exe")
    assert result["ok"]
    assert len(commands) == 2
    assert "--source-only" not in commands[0] and "--check-manifest" not in commands[0]
    assert commands[0][-2:] == ["--lake-exe", "pinned-lake.exe"]
    assert commands[1] == commands[0] + ["--check-manifest"]
    assert result["evidence"]["verification_id"] == "2" * 32
    assert result["evidence"]["scope"] == "current_implemented_library"
    assert not verify.foundations_reference_errors(result["evidence"], proof_root)
    assert "Full-chain" in result["summary"]
    assert all("verify_lean_archive.py" not in command for command in commands)


@pytest.mark.parametrize("failure", ["old_record", "missing_record", "failed_audit",
                                     "failed_record_check", "wrong_kind", "wrong_scope"])
def test_old_or_invalid_evidence_cannot_turn_subprocess_success_into_pass(
        proof_root, monkeypatch, failure):
    old = record_path(proof_root).read_bytes()
    def execute(label, command, **kwargs):
        result = successful_subprocess(label, command, **kwargs)
        if "--check-manifest" not in command:
            if failure == "missing_record":
                record_path(proof_root).unlink()
            elif failure in {"wrong_kind", "wrong_scope", "failed_record_check"}:
                record = publish_proof(proof_root, "2" * 32)
                if failure == "wrong_kind":
                    record["kind"] = "source-only"
                elif failure == "wrong_scope":
                    record["scope"] = "full-chain-certified"
                write_json(record_path(proof_root), record)
            elif failure == "failed_audit":
                result.update(ok=False, returncode=1, output="audit failed")
        elif failure == "failed_record_check":
            result.update(ok=False, returncode=1, output="record check failed")
        return result
    monkeypatch.setattr(verify, "run", execute)
    result = verify.run_foundations(None)
    assert not result["ok"] and result["returncode"] != 0
    assert "evidence" not in result
    if failure == "failed_audit":
        assert record_path(proof_root).read_bytes() == old


@pytest.mark.parametrize("target", ["GeneratedFoundations/Nested/Basic.lean", "lean-toolchain",
                                    "lakefile.lean", "lake-manifest.json", "theorem-index.json"])
def test_external_sources_and_locks_are_pinned_without_numeric_fingerprint_scanning(proof_root, target):
    before = verification_fingerprints(proof_root)
    path = proof_root / "proof-checkout" / target
    path.write_bytes(path.read_bytes() + b"\n")
    assert before == verification_fingerprints(proof_root)
    assert verify.foundations.REFERENCE_NAME in before
    with pytest.raises(verify.foundations.VerificationError, match="sources differ"):
        verify.foundations.load_project(proof_root)


def test_build_cache_and_verification_outputs_do_not_change_source_fingerprint(proof_root):
    before = verification_fingerprints(proof_root)
    project = proof_root / "proof-checkout"
    (project / ".lake" / "Dependency.lean").write_text("changed dependency fixture", encoding="utf-8")
    (project / verify.foundations.AUDIT_LOG).write_text("changed log", encoding="utf-8")
    (project / "verification-manifest.json").write_text("changed record", encoding="utf-8")
    assert before == verification_fingerprints(proof_root)


@pytest.mark.parametrize("target", ["proof-checkout/GeneratedFoundations/Nested/Basic.lean",
                                    "proof-checkout/.lake/foundations-audit.txt",
                                    "proof-checkout/scripts/verify_foundations.py",
                                    "proof-checkout/verification-manifest.json",
                                    "foundations-reference.json"])
def test_saved_proof_reference_rejects_changed_sources_logs_verifier_or_record(proof_root, monkeypatch, target):
    install_proof_run(proof_root, monkeypatch)
    result = verify.run_foundations(None)
    path = proof_root / target
    path.write_bytes(path.read_bytes() + b"\n")
    assert verify.foundations_reference_errors(result["evidence"], proof_root)


def test_aggregate_record_binds_proof_identity_and_rejects_later_proof_replacement(proof_root, monkeypatch):
    install_proof_run(proof_root, monkeypatch)
    result = verify.run_foundations(None)
    manifest = {"run_id": "numerical-fixture", "publication": verify.publication_metadata(),
                "source_sha256": {"example": "unchanged"}}
    write_json(proof_root / "run_manifest.json", manifest)
    monkeypatch.setattr(verify, "validate_run_manifest", lambda *args, **kwargs: {"ok": True})
    saved = verify.record_verification([result], [], proof_root)
    assert saved["checks"][0]["evidence"] == result["evidence"]
    assert verify.verification_state(proof_root)["status"] == "PASS"
    publish_proof(proof_root, "3" * 32)
    assert verify.verification_state(proof_root)["status"] == "stale proof evidence"
    current = json.loads((proof_root / "run_manifest.json").read_bytes())
    assert current["source_sha256"] == manifest["source_sha256"]


def test_proof_pass_does_not_override_failed_numerical_identity(proof_root, monkeypatch):
    install_proof_run(proof_root, monkeypatch)
    proof = verify.run_foundations(None)
    write_json(proof_root / "run_manifest.json", {"run_id": "old-numerical-run"})
    failed = {"label": "current run manifest", "cmd": "identity check", "ok": False,
              "required": True, "returncode": 1, "output": "numerical sources changed"}
    saved = verify.record_verification([proof, failed], [], proof_root)
    assert saved["status"] == "FAIL"
    assert saved["checks"][0]["ok"] is True


def test_proof_evidence_changed_before_publication_fails_the_actual_result(proof_root, monkeypatch):
    install_proof_run(proof_root, monkeypatch)
    result = verify.run_foundations(None)
    write_json(proof_root / "run_manifest.json", {"run_id": "numeric-fixture"})
    (proof_root / "proof-checkout" / verify.foundations.AUDIT_LOG).unlink()
    record = verify.record_verification([result], [], proof_root)
    assert record["status"] == "FAIL"
    assert not result["ok"] and result["returncode"] == 1
    assert "evidence" not in record["checks"][0]


def test_evidence_reference_cannot_carry_scientific_payload_or_external_path(proof_root, monkeypatch):
    install_proof_run(proof_root, monkeypatch)
    reference = verify.run_foundations(None)["evidence"]
    assert verify.foundations_reference_errors({**reference, "mass": 125}, proof_root)
    assert verify.foundations_reference_errors({**reference, "path": "../outside.json"}, proof_root)


def test_new_and_old_lean_cli_options_route_to_separate_verifiers(proof_root, monkeypatch):
    calls, omitted = [], []
    monkeypatch.delenv("FOUNDATIONS_PROJECT")
    project = proof_root / "proof-checkout"
    def archive(executable, *, key_only=False):
        calls.append(("archive", executable, key_only))
        return successful_subprocess("Lean proof archive", [])
    def generated(executable):
        assert os.environ["FOUNDATIONS_PROJECT"] == str(project)
        calls.append(("foundations", executable))
        return successful_subprocess(verify.FOUNDATIONS_LABEL, [])
    def save_results(results, absent):
        assert verify.foundations.project_path(proof_root) == project
        omitted.extend(absent)
    monkeypatch.setattr(verify, "run_lean_archive", archive)
    monkeypatch.setattr(verify, "run_foundations", generated)
    monkeypatch.setattr(verify, "run", successful_subprocess)
    monkeypatch.setattr(verify, "run_source_audits", lambda *args: [])
    monkeypatch.setattr(verify, "validate_run_manifest", lambda: successful_subprocess("identity", []))
    monkeypatch.setattr(verify, "record_verification", save_results)
    monkeypatch.setattr(verify, "report_text", lambda *args: "fixture report")
    monkeypatch.setattr(sys, "argv", ["verify_v5.py", "--no-reproduce", "--skip-full-comparison",
                                     "--lean", "--lean-exe", "old-lean.exe", "--foundations",
                                     "--foundations-lake-exe", "new-lake.exe",
                                     "--foundations-project", str(project),
                                     "--report", str(proof_root / "report.md")])
    assert verify.main() == 0
    assert calls == [("archive", "old-lean.exe", False), ("foundations", "new-lake.exe")]
    assert not any(verify.FOUNDATIONS_LABEL in item or "Lean archive" in item for item in omitted)


def test_release_reference_changes_numerical_verification_identity(proof_root):
    before = verification_fingerprints(proof_root)
    pin = proof_root / verify.foundations.REFERENCE_NAME
    pin.write_bytes(pin.read_bytes() + b"\n")
    assert before != verification_fingerprints(proof_root)


def test_default_sibling_and_explicit_project_resolve_independently(proof_root, monkeypatch):
    monkeypatch.delenv("FOUNDATIONS_PROJECT")
    assert verify.foundations.project_path(proof_root) == (
        proof_root / verify.foundations.DEFAULT_LOCATOR).resolve()
    project = proof_root / "proof-checkout"
    loaded, _, _ = verify.foundations.load_project(proof_root, project)
    assert loaded == project
    commands = install_proof_run(proof_root, monkeypatch)
    result = verify.run_foundations(None, project)
    assert result["ok"]
    assert commands[0][-2:] == ["--project", str(project)]
    assert not verify.foundations_reference_errors(result["evidence"], proof_root, project)
    assert str(project) not in json.dumps(result["evidence"])


def test_adapter_forwards_external_command_and_exit_status(proof_root, monkeypatch):
    calls = []
    monkeypatch.setattr(verify.foundations, "ROOT", proof_root)
    def invoke(command, **kwargs):
        calls.append((command, kwargs))
        return 7
    monkeypatch.setattr(verify.foundations.subprocess, "call", invoke)
    assert verify.foundations.main(["--source-only", "--lake-exe", "pinned-lake"]) == 7
    project = proof_root / "proof-checkout"
    assert calls == [([sys.executable, "-B", str(project / "scripts" / "verify_foundations.py"),
                      "--project-root", str(project), "--source-only", "--lake-exe", "pinned-lake"],
                     {"cwd": project})]


def test_missing_external_checkout_does_not_affect_numeric_import_or_fingerprints(proof_root, monkeypatch):
    monkeypatch.setenv("FOUNDATIONS_PROJECT", str(proof_root / "absent-proof-checkout"))
    assert verify.foundations.REFERENCE_NAME in verification_fingerprints(proof_root)
    result = verify.run_foundations(None)
    assert not result["ok"] and "Independent proof checkout is unavailable" in result["output"]
    code = ("from scripts import verify_v5, reproduce_v5; "
            "assert reproduce_v5.verification_fingerprints(); print('numeric imports available')")
    completed = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT,
                               env=os.environ.copy(), capture_output=True, text=True,
                               encoding="utf-8")
    assert completed.returncode == 0, completed.stderr
    assert "numeric imports available" in completed.stdout


def test_changed_verifier_is_rejected_before_external_code_executes(proof_root):
    verifier = proof_root / "proof-checkout" / "scripts" / "verify_foundations.py"
    verifier.write_text("raise AssertionError('unpinned code executed')\n", encoding="utf-8")
    with pytest.raises(verify.foundations.VerificationError, match="verifier differs"):
        verify.foundations.load_project(proof_root)


def test_report_sanitizes_external_checkout_paths(proof_root):
    project = proof_root / "proof-checkout"
    for rendered in (str(project), str(project).replace("\\", "/"),
                     str(project).replace("\\", "\\\\")):
        assert verify.sanitize_output(rendered + "/GeneratedFoundations.lean").startswith(
            "<foundations-project>/")


def test_explicit_checkout_path_is_redacted_even_without_environment(proof_root, monkeypatch):
    monkeypatch.delenv("FOUNDATIONS_PROJECT")
    project = proof_root / "proof-checkout"
    def execute(label, command, **kwargs):
        result = successful_subprocess(label, command, **kwargs)
        result.update(ok=False, returncode=1, output=str(project) + "/source.lean: check failed")
        return result
    monkeypatch.setattr(verify, "run", execute)
    result = verify.run_foundations(None, project)
    assert not result["ok"]
    assert result["output"].startswith("<foundations-project>/")
    assert str(project) not in json.dumps(result)


def test_project_root_alias_cannot_bypass_pinned_project_selection(proof_root, monkeypatch):
    monkeypatch.setattr(verify.foundations, "ROOT", proof_root)
    def unexpected_launch(*args, **kwargs):
        pytest.fail("Unpinned project must not reach the external process")
    monkeypatch.setattr(verify.foundations.subprocess, "call", unexpected_launch)
    assert verify.foundations.main(["--project", str(proof_root / "proof-checkout"),
                                    "--project-root", str(proof_root / "not-installed")]) == 1
