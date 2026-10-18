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

"""
scripts/verify_v5.py -- end-to-end verification
==============================================================

This is the one-command entry point for reviewers and Git browsers:

    py scripts/verify_v5.py --fresh --audit --lean --pytest

It can rebuild the generated stores from scratch, reproduce the full
V5 chain, audit parameter provenance, audit observed-value isolation,
audit Lean proof-source hygiene, optionally compile the Lean archive,
optionally compile and audit the separately pinned foundations library with
--foundations, optionally run the test suite, and write a Markdown report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cg_core.release import PUBLICATION_NOTICE, publication_metadata
from cg_core.params import (resolved_records, value_fingerprint, write_json_atomic,
                            read_store_document)
from scripts.evaluate_joint_extensions import RESPONSE_NAMES, response_source_identities, response_bundle
from scripts.reproduce_v5 import (verification_fingerprints, external_input_fingerprints,
                                 storage_contract, solver_execution_identity)
from scripts import verify_foundations as foundations

PY = sys.executable
DEFAULT_REPORT = ROOT / "V5_VERIFICATION_REPORT.md"
FOUNDATIONS_LABEL = foundations.PUBLIC_NAME
FOUNDATIONS_RECORD = "foundations:verification-manifest.json"
FOUNDATIONS_SCOPE = "current_implemented_library"


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    return env


def display_path(path_text: str) -> str:
    path = Path(path_text)
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        pass
    if path_text == PY:
        return "python"
    return path_text


def display_command(cmd: list[str]) -> str:
    parts = []
    for index, item in enumerate(cmd):
        if index == 0 and item == PY:
            parts.append("python")
        else:
            parts.append(display_path(item))
    return " ".join(parts)


def sanitize_output(text: str, *, proof_project: Path | None = None) -> str:
    out = text
    proof_root = foundations.project_path(ROOT, proof_project)
    for needle in {str(proof_root), str(proof_root).replace("\\", "/"),
                   str(proof_root).replace("\\", "\\\\")}:
        out = out.replace(needle, "<foundations-project>")
    for needle in {
        str(ROOT),
        str(ROOT).replace("\\", "/"),
        str(ROOT).replace("\\", "\\\\"),
    }:
        out = out.replace(needle, ".")
    for needle in {PY, PY.replace("\\", "/"), PY.replace("\\", "\\\\")}:
        out = out.replace(needle, "python")
    runtime_roots = {str(Path(PY).resolve().parent), sys.prefix, sys.base_prefix}
    runtime_paths = {variant for root in runtime_roots if root
                     for variant in (root, root.replace("\\", "/"), root.replace("\\", "\\\\"))}
    for needle in sorted(runtime_paths, key=len, reverse=True):
        out = out.replace(needle, "<python-runtime>")
    temporary_root = tempfile.gettempdir()
    for needle in {temporary_root, temporary_root.replace("\\", "/"),
                   temporary_root.replace("\\", "\\\\")}:
        out = out.replace(needle, "<temporary>")
    out = out.replace(".\\.deps", ".deps")
    return out


def run(label: str, cmd: list[str], *, required: bool = True,
        display_cmd: str | None = None) -> dict:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=base_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out = sanitize_output((proc.stdout or "") + (proc.stderr or ""))
    ok = proc.returncode == 0
    return {
        "label": label,
        "cmd": display_cmd or display_command(cmd),
        "returncode": proc.returncode,
        "ok": ok,
        "required": required,
        "output": out,
    }


def foundations_reference_errors(reference: dict, root: Path,
                                project: Path | None = None) -> list[str]:
    """Check saved proof evidence against local files without running a compiler.

    This checks the binding of a past verification, not current executables or
    dependency checkouts. A new proof run checks that environment separately.
    """
    fields = {"path", "sha256", "verification_id", "scope", "audit_sha256",
              "reference_sha256"}
    if (not isinstance(reference, dict) or set(reference) != fields
            or reference.get("path") != FOUNDATIONS_RECORD
            or reference.get("scope") != FOUNDATIONS_SCOPE):
        return ["invalid foundations evidence reference"]
    try:
        project, _, pin = foundations.load_project(root, project)
        if reference["reference_sha256"] != foundations.reference_hash(root):
            return ["foundations release reference changed"]
        raw = (project / foundations.MANIFEST_NAME).read_bytes()
        record = json.loads(raw)
        if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
            return ["foundations verification record changed"]
        if (record.get("kind") != "generated-foundations-verification"
                or record.get("status") != "passed"
                or record.get("scope") != FOUNDATIONS_SCOPE
                or record.get("semantic_review") != "not_certified"
                or record.get("verification_id") != reference["verification_id"]
                or not re.fullmatch(r"[0-9a-f]{32}", str(reference["verification_id"]))):
            return ["foundations record has invalid verification identity or scope"]
        if pin["source_files"] != record.get("source_files"):
            return ["foundations verification sources changed"]
        if record.get("verifier") != pin["verifier"]:
            return ["foundations verifier changed"]
        audit = record.get("audit", {})
        if (audit.get("path") != foundations.AUDIT_LOG
                or audit.get("sha256") != reference["audit_sha256"]
                or hashlib.sha256((project / foundations.AUDIT_LOG).read_bytes()).hexdigest()
                != reference["audit_sha256"]):
            return ["foundations audit log changed or missing"]
    except (OSError, ValueError, TypeError, AttributeError, foundations.VerificationError) as exc:
        return ["foundations evidence unavailable: " + str(exc)]
    return []


def manifest_contract_errors(manifest: dict) -> list[str]:
    """Reject additional scientific payloads in the identity-only manifest."""
    allowed = {"publication", "storage_contract", "solver_execution_identity", "run_id",
               "python", "status", "scope", "source_sha256", "audits",
               "verification_source_sha256", "external_input_sha256", "output_sha256",
               "verification"}
    errors = []
    extra = set(manifest)-allowed
    if extra:
        errors.append("manifest contains unsupported payload fields: " + ", ".join(sorted(extra)))
    if manifest.get("storage_contract") != storage_contract():
        errors.append("manifest storage contract must declare exactly the two scientific stores")
    audit_names = {"audit_param_writers.py", "audit_observation_leakage.py"}
    audit_fields = {"returncode", "ok", "cmd", "summary", "output"}
    audits = manifest.get("audits", {})
    if not isinstance(audits, dict) or set(audits)-audit_names:
        errors.append("manifest contains an unsupported audit record")
    else:
        for item in audits.values():
            if not isinstance(item, dict) or set(item)-audit_fields:
                errors.append("manifest audit contains unsupported payload fields")
            elif item.get("returncode") == 0 and "output" in item:
                errors.append("successful manifest audits retain summaries, not full output")
    verification = manifest.get("verification")
    if verification is not None:
        fields = {"run_id", "status", "binding_sha256", "checks", "not_executed"}
        if not isinstance(verification, dict) or set(verification)-fields:
            errors.append("manifest verification contains unsupported payload fields")
        else:
            checks = verification.get("checks", [])
            check_fields = {"label", "cmd", "returncode", "ok", "required", "summary", "output", "evidence"}
            if not isinstance(checks, list):
                errors.append("manifest verification checks must be a list")
            else:
                for item in checks:
                    if not isinstance(item, dict) or set(item)-check_fields:
                        errors.append("manifest check contains unsupported payload fields")
                    elif item.get("ok") is True and "output" in item:
                        errors.append("successful manifest checks retain summaries, not full output")
                    elif "evidence" in item and (item.get("label") != FOUNDATIONS_LABEL
                                                  or item.get("ok") is not True):
                        errors.append("only successful foundations checks may reference proof evidence")
                    elif item.get("label") == FOUNDATIONS_LABEL and item.get("ok") is True:
                        reference = item.get("evidence")
                        fields = {"path", "sha256", "verification_id", "scope", "audit_sha256",
                                  "reference_sha256"}
                        if not isinstance(reference, dict) or set(reference) != fields:
                            errors.append("foundations check must contain only an evidence identity")
    return errors


def validate_run_manifest(root: Path = ROOT, *, manifest: dict | None = None) -> dict:
    """Check unified scientific records against their inputs and current sources."""
    failures = []
    try:
        if manifest is None:
            manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
        failures.extend(manifest_contract_errors(manifest))
        if manifest.get("publication") != publication_metadata():
            failures.append("manifest software identity or bibliography does not match V5")
        run_id = manifest["run_id"]
        expected_sources = manifest["source_sha256"]
        expected_outputs = manifest["output_sha256"]
        if not run_id or not expected_sources or not expected_outputs:
            raise ValueError("manifest has empty identity or fingerprints")
        current_sources = {
            p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ("cg_core", "cg_frg", "scripts", "comparison")
            for p in (root / folder).rglob("*.py")}
        if current_sources != expected_sources:
            failures.append("current source fingerprints differ from this run")
        if verification_fingerprints(root) != manifest.get("verification_source_sha256"):
            failures.append("verification source fingerprints differ from this run")
        if external_input_fingerprints(root) != manifest.get("external_input_sha256"):
            failures.append("external input fingerprints differ from this run")
        if solver_execution_identity(root) != manifest.get("solver_execution_identity"):
            failures.append("solver execution identity differs from the computed store record")
        required = set(storage_contract()["scientific_stores"])
        if set(expected_outputs) != required:
            failures.append("manifest must fingerprint the two unified output stores")
        for name, expected in expected_outputs.items():
            target = (root / name).resolve()
            if not target.is_relative_to(root.resolve()):
                raise ValueError("manifest output escapes the framework directory")
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                failures.append(f"output fingerprint mismatch: {name}")
        raw = read_store_document("parameters", source_root=root)["parameters"]
        records = resolved_records(raw)
        stale = [key for key, rec in records.items()
                 if rec.get("provenance") == "DERIVED" and rec.get("run_id") != run_id]
        if stale:
            failures.append(f"derived records from another run: {stale[:12]}")
        response_sources = response_source_identities()
        response_keys = {"response_"+name for name in RESPONSE_NAMES}
        for key in sorted(response_keys | {"response_validation"}):
            rec = records.get(key)
            if not isinstance(rec, dict):
                failures.append(f"missing unified response record: {key}")
                continue
            if rec.get("provenance") != "DERIVED" or rec.get("run_id") != run_id:
                failures.append(f"response publication identity mismatch: {key}")
            if (key in response_keys and rec.get("calculation", {}).get("source_sha256")
                    != response_sources[key.removeprefix("response_")]):
                failures.append(f"response calculation source mismatch: {key}")
            direct = rec.get("direct_inputs")
            if not isinstance(direct, dict):
                failures.append(f"missing response direct inputs: {key}")
                continue
            if key == "response_validation" and set(direct) != response_keys:
                failures.append("response validation does not bind every response section")
            for parent, digest in direct.items():
                if parent not in records or value_fingerprint(records[parent]["value"]) != digest:
                    failures.append(f"response direct-input mismatch: {key} <- {parent}")
        validation = records.get("response_validation", {}).get("value", {})
        checks = validation.get("checks", {})
        if (validation.get("all_checks_passed") is not True or not checks
                or any(value is not True for value in checks.values())):
            failures.append("response result contains an unpassed required check")
        status = manifest.get("status", "")
        if status != "complete computational run":
            failures.append(f"manifest is not a complete computational run: {status}")
        detail = f"run_id: {run_id}\nsource files: {len(current_sources)}\n"
        detail += "\n".join(failures) if failures else "All run identities and fingerprints match."
    except (OSError, ValueError, TypeError, KeyError, AttributeError, foundations.VerificationError) as exc:
        failures.append(str(exc))
        detail = "Manifest verification failed: " + str(exc)
    return {"label": "current run manifest", "cmd": "verify existing run identity and fingerprints",
            "returncode": 1 if failures else 0, "ok": not failures, "required": True,
            "output": detail}


def verification_binding(manifest: dict) -> str:
    """Bind validation to run metadata and outputs without a self-hash cycle."""
    return value_fingerprint({key: value for key, value in manifest.items()
                              if key != "verification"})


def run_source_audits(reproduction: dict | None, root: Path = ROOT) -> list[dict]:
    """Reuse audits only from this invocation's fingerprint-validated reproduction.

    The completed subprocess identifies the published run. Its audit summaries
    belong to the same source and store fingerprints as that run; they are not
    independent cached scientific records. Verification without reproduction
    executes both audits against the current files.
    """
    try:
        manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        manifest = {}
    identity = validate_run_manifest(root, manifest=manifest)
    results = [identity]
    completed = (re.search(r"^COMPLETE: ([^;\s]+); outputs published\s*$",
                           reproduction.get("output", ""), re.MULTILINE)
                 if reproduction and reproduction.get("ok") is True
                 and type(reproduction.get("returncode")) is int
                 and reproduction["returncode"] == 0 else None)
    bound = bool(identity["ok"] and completed
                 and completed.group(1) == manifest.get("run_id"))
    for script, label in (("audit_param_writers.py", "parameter provenance audit"),
                          ("audit_observation_leakage.py", "observation leakage audit")):
        command = "python scripts/" + script
        audit = manifest.get("audits", {}).get(script, {}) if bound else {}
        if (isinstance(audit, dict) and audit.get("ok") is True
                and type(audit.get("returncode")) is int and audit["returncode"] == 0
                and audit.get("cmd") == command
                and isinstance(audit.get("summary"), str) and audit["summary"].strip()):
            summary = ("Executed once during this invocation's reproduction; reused after "
                       "run, source, reference and output fingerprints were verified.")
            results.append({"label": label, "cmd": command, "returncode": 0,
                            "ok": True, "required": True, "summary": summary,
                            "output": summary})
        else:
            results.append(run(label, [PY, "scripts/" + script]))
    return results


def record_verification(results: list[dict], not_executed: list[str],
                        root: Path = ROOT) -> dict | None:
    """Publish checks executed directly or by this invocation's reproduction."""
    path = root / "run_manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    checks = []
    for result in results:
        if result["label"] == FOUNDATIONS_LABEL and result["ok"]:
            errors = foundations_reference_errors(result.get("evidence"), root)
            if errors:
                result.update(ok=False, returncode=1, output="\n".join(errors))
        item = {key: result[key] for key in ("label", "cmd", "required", "ok", "returncode")}
        if item["ok"]:
            item["summary"] = result.get("summary", "Completed the declared check successfully.")
            if item["label"] == FOUNDATIONS_LABEL:
                item["evidence"] = dict(result["evidence"])
            if item["label"].startswith("pytest"):
                counts = re.findall(r"\b\d+ (?:subtests passed|passed|failed|skipped|deselected|xfailed|xpassed)\b",
                                    result.get("output", ""))
                if counts:
                    scope = "Core suite: " if item["label"] == "pytest (core)" else "Full suite: "
                    item["summary"] = scope + "; ".join(counts) + "."
            elif item["label"] == "Lean proof archive":
                count = re.search(r"files compiled:\s*(\d+)", result.get("output", ""))
                if count:
                    item["summary"] = count.group(1) + " formal-proof sources compiled successfully."
        else:
            item["output"] = result.get("output", "")
        checks.append(item)
    status = "FAIL" if any(item["required"] and not item["ok"] for item in checks) else "PASS"
    verification = {
        "run_id": manifest.get("run_id"),
        "status": status,
        "binding_sha256": verification_binding(manifest),
        "checks": checks,
        "not_executed": list(not_executed),
    }
    manifest["verification"] = verification
    write_json_atomic(path, manifest)
    return verification


def verification_state(root: Path = ROOT, *, manifest: dict | None = None) -> dict:
    """Read a fingerprint-bound verification state without executing audits."""
    state = {"status": "not verified", "run_id": None, "checks": [], "not_executed": []}
    try:
        if manifest is None:
            manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
        state["run_id"] = manifest.get("run_id")
        saved = manifest.get("verification")
        if not isinstance(saved, dict):
            return state
        if saved.get("run_id") != state["run_id"] or not state["run_id"]:
            return {**state, "status": "unmatched run"}
        if saved.get("binding_sha256") != verification_binding(manifest):
            return {**state, "status": "stale run"}
        checks = saved.get("checks")
        omitted = saved.get("not_executed")
        if (not isinstance(checks, list) or not checks or
                not isinstance(omitted, list) or any(not isinstance(item, str) for item in omitted)):
            return {**state, "status": "invalid verification"}
        for item in checks:
            if (not isinstance(item, dict) or not isinstance(item.get("label"), str)
                    or type(item.get("ok")) is not bool
                    or type(item.get("required")) is not bool
                    or type(item.get("returncode")) is not int
                    or item["ok"] != (item["returncode"] == 0)):
                return {**state, "status": "invalid verification"}
            if item["label"] == FOUNDATIONS_LABEL and item["ok"]:
                if foundations_reference_errors(item.get("evidence"), root):
                    return {**state, "status": "stale proof evidence"}
        status = "FAIL" if any(item["required"] and not item["ok"] for item in checks) else "PASS"
        if saved.get("status") != status:
            return {**state, "status": "invalid verification"}
        if not validate_run_manifest(root, manifest=manifest)["ok"]:
            return {**state, "status": "stale run"}
        return {**state, "status": status, "checks": checks, "not_executed": omitted}
    except (OSError, ValueError, TypeError, KeyError):
        return {**state, "status": "invalid verification"}


def run_lean_archive(lean_exe: str | None, *, key_only=False) -> dict:
    cmd = [PY, "scripts/verify_lean_archive.py"]
    display = "python scripts/verify_lean_archive.py"
    if lean_exe:
        cmd.extend(["--lean-exe", lean_exe])
        display += " --lean-exe <lean.exe>"
    if key_only:
        cmd.append("--key-only")
        display += " --key-only"
    return run("Lean proof archive", cmd, display_cmd=display)


def run_foundations(lake_exe: str | None, project: Path | None = None) -> dict:
    """Require a newly completed proof audit and bind its saved evidence."""
    try:
        project, _, _ = foundations.load_project(ROOT, project)
    except (OSError, ValueError, TypeError, AttributeError, foundations.VerificationError) as exc:
        return {"label": FOUNDATIONS_LABEL, "cmd": "python -B scripts/verify_foundations.py",
                "ok": False, "required": True, "returncode": 1,
                "output": sanitize_output("Independent proof library unavailable: " + str(exc))}
    path = project / foundations.MANIFEST_NAME
    try:
        old_id = json.loads(path.read_bytes()).get("verification_id")
    except (OSError, ValueError, AttributeError):
        old_id = None
    cmd = [PY, "-B", "scripts/verify_foundations.py", "--project", str(project)]
    display = "python -B scripts/verify_foundations.py --project <foundations-project>"
    if lake_exe:
        cmd.extend(["--lake-exe", lake_exe])
        display += " --lake-exe <lake.exe>"
    result = run(FOUNDATIONS_LABEL, cmd, display_cmd=display)
    result["output"] = sanitize_output(result["output"], proof_project=project)
    if not result["ok"]:
        return result
    checked = run("foundations record binding", cmd + ["--check-manifest"],
                  display_cmd=display + " --check-manifest")
    checked["output"] = sanitize_output(checked["output"], proof_project=project)
    if not checked["ok"]:
        result.update(ok=False, returncode=checked["returncode"],
                      output=result["output"] + "\n" + checked["output"])
        return result
    try:
        raw = path.read_bytes()
        record = json.loads(raw)
        if record.get("verification_id") == old_id:
            raise ValueError("no new foundations verification record was produced")
        reference = {"path": FOUNDATIONS_RECORD, "sha256": hashlib.sha256(raw).hexdigest(),
                     "verification_id": record.get("verification_id"),
                     "scope": record.get("scope"),
                     "audit_sha256": record.get("audit", {}).get("sha256"),
                     "reference_sha256": foundations.reference_hash(ROOT)}
        errors = foundations_reference_errors(reference, ROOT, project)
        if errors:
            raise ValueError("; ".join(errors))
        result["evidence"] = reference
        result["summary"] = ("Current implemented library compiled and audited; record "
                             + reference["verification_id"]
                             + ". Full-chain and manuscript coverage are not certified by this check.")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        result.update(ok=False, returncode=1, output=sanitize_output(
            result["output"] + "\n" + str(exc), proof_project=project))
    return result


def run_numeric_stability() -> dict:
    return run("numeric stability audit", [PY, "scripts/audit_numeric_stability.py"],
               display_cmd="python scripts/audit_numeric_stability.py")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def store_summary() -> str:
    cg = resolved_records(read_store_document("parameters", source_root=ROOT).get("parameters", {}))
    sm = read_store_document("references", source_root=ROOT).get("parameters", {})
    if not cg:
        return "Parameter store is missing.\n"

    prov = Counter(rec.get("provenance", "?") for rec in cg.values()
                   if isinstance(rec, dict))
    roles = Counter(rec.get("role", "?") for rec in cg.values()
                    if isinstance(rec, dict))
    lines = [
        "### Store Summary",
        "",
        f"- cg_params records: {len(cg)}",
        f"- Isolated reference records: {len(sm)}",
        "- provenance: " + ", ".join(f"{k}={v}" for k, v in sorted(prov.items())),
        "- roles: " + ", ".join(f"{k}={v}" for k, v in sorted(roles.items())),
        "- declared physical definitions: " + str(sum(
            isinstance(rec.get("quantity_definition"), dict) for rec in cg.values())),
        "- declared direct-input sets: " + str(sum(
            isinstance(rec.get("direct_inputs"), dict) for rec in cg.values())),
        "",
        "### Selected Closed Values",
        "",
        "| key | value | provenance | writer |",
        "|---|---:|---|---|",
    ]
    selected = [
        "kL", "M_G", "g2_MG", "g1_MG_geo", "g3_MG_geo",
        "generated_ym_gap_mass",
        "n_generations", "v_HIGGS", "M_Z_pred", "M_W_pred",
        "M_W_pred_lead1loop", "Gamma_b_pred_1loop",
        "Gamma_had_pred_lead1loop", "Gamma_Z_pred_lead1loop",
        "R_b_pred_lead1loop", "R_l_pred_lead1loop", "sigma_had_pred_lead1loop",
        "sin2_theta_eff_l_pred", "m_H_pred",
        "Omega_Lambda", "Omega_Sigma", "T_CMB_GeV",
        "T_CMB_corrected_K", "endpoint_sigma8", "endpoint_S8",
        "bbn_dm_np", "bbn_tau_n", "bbn_Yp", "bbn_Neff",
    ]
    for key in selected:
        rec = cg.get(key)
        if isinstance(rec, dict):
            val = rec.get("value")
            lines.append(
                f"| `{key}` | `{val}` | {rec.get('provenance')} | "
                f"`{rec.get('writer')}` |"
            )
    return "\n".join(lines) + "\n"


def report_text(results: list[dict], not_executed: list[str]) -> str:
    failed_required = [r for r in results if r["required"] and not r["ok"]]
    lines = ["<!--", *PUBLICATION_NOTICE, "-->", "",
        "# V5 Verification Report",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Python: `{platform.python_version()}`",
        "Root: `.`",
        "",
        "## Verdict",
        "",
        "PASS for the executed checks" if not failed_required else "FAIL",
        "",
    ]
    lines += ["A requested reproduction builds empty temporary stores and publishes only after success.",
              "The results below identify the checks executed in this invocation;",
              "a proof-library result does not certify a numerical run or the entire manuscript chain.", ""]
    if not_executed:
        lines += ["## Not Executed", ""]
        lines += [f"- {item}" for item in not_executed]
        lines += ["", "No PASS claim is made for these omitted checks.", ""]

    lines += ["## Steps", "", "| step | status | command |",
              "|---|---:|---|"]
    for result in results:
        status = "PASS" if result["ok"] else ("FAIL" if result["required"] else "WARN")
        lines.append(
            f"| {result['label']} | {status} | "
            f"`{result['cmd']}` |"
        )
    for result in results:
        if result["label"] == FOUNDATIONS_LABEL and result.get("ok"):
            evidence = result.get("evidence", {})
            lines += ["", "Foundations record: `" + evidence.get("verification_id", "")
                      + "`; scope: `" + evidence.get("scope", "") + "`.",
                      "This is separate from the Lean 4.7.0 archive and numerical verification."]
        if result["label"].startswith("pytest"):
            counts = re.findall(r"\b\d+ (?:subtests passed|passed|failed|skipped|deselected|xfailed|xpassed)\b",
                                result["output"])
            if counts:
                scope = "Core Python" if result["label"] == "pytest (core)" else "Full Python"
                lines += ["", scope + " test results: " + ", ".join(counts) + "."]
                lines += ["The complete release audits are executed in the steps above;",
                          "their duplicate test wrappers are deselected."]
    reused_audits = [result["label"] for result in results if result.get("summary", "").startswith(
        "Executed once during this invocation's reproduction;")]
    if reused_audits:
        lines += ["", "Audits executed once during reproduction and reused after current-run "
                  "fingerprint validation: " + ", ".join(reused_audits) + "."]
    manifest = load_json(ROOT / "run_manifest.json")
    if manifest:
        lines += ["", f"Run identity: `{manifest.get('run_id', '')}`.",
                  f"Bound calculation sources: {len(manifest.get('source_sha256', {}))}; "
                  f"verification sources: {len(manifest.get('verification_source_sha256', {}))}; "
                  f"outputs: {len(manifest.get('output_sha256', {}))}; "
                  f"reference identities: {len(manifest.get('external_input_sha256', {}).get('reference_records', {}))}; "
                  f"solver execution identities: {len(manifest.get('solver_execution_identity', {}))}."]
    lines.append("")
    lines.append(store_summary())

    records = read_store_document("parameters", source_root=ROOT).get("parameters", {})
    ym_record = records.get("generated_ym_mass_gap", {})
    ym = ym_record.get("value", {}) if isinstance(ym_record, dict) else {}
    if isinstance(ym, dict) and ym:
        interval = ym.get("interval_certificate", {})
        operator = ym.get("operator_certificate", {})
        transport = ym.get("scale_transport", {})
        lines += [
            "## Generated Yang--Mills Theorem Certificate",
            "",
            "The computed operator is the orthogonal direct sum of the normalized "
            "radial intensity block and the complete positive-odd coclosed colour-"
            "connection tower.  The value below is the minimum of their spectral "
            "bottoms.",
            "",
            f"- response coordinate: `{ym.get('response_coordinate')}`",
            f"- radial mass squared: `{ym.get('radial_mass_squared')}`",
            f"- coclosed-connection bottom: `{ym.get('transverse_mass_squared')}`",
            f"- complete Yang--Mills gap squared: `{ym.get('gap_squared')}`",
            f"- controlling block: `{ym.get('controlling_block')}`",
            f"- interval lower bound: `{(interval.get('complete_gap_squared') or [None])[0]}`",
            f"- first coclosed total multiplicity: `{operator.get('coclosed_first_total_multiplicity')}`",
            f"- radial/scalar semigroup residual: `{ym.get('radial_intertwining_residual')}`",
            f"- scale-transport ratio spread: `{transport.get('ratio_spread')}`",
            "",
        ]
    if "response_validation" in records:
        extension = response_bundle(records)
        affine = extension.get("exact_affine_certificates", {})
        branch = extension.get("undeformed_branch_margin", {})
        if affine and branch:
            lines += ["## Exact affine certificates", "",
                      "The following certificates refer to the explicitly supplied rational",
                      "matrices. Exact elimination verifies the kernel, slope and source overlap.",
                      "Physical tensor identification specifies the sourced action,",
                      "external momentum, constraints and polarization space.", "",
                      "| example | dimension | kernel dimension | visible rank | exact residue |",
                      "|---|---:|---:|---:|---|"]
            for name, result in affine["examples"].items():
                lines.append(f"| {name} | {len(result['inputs']['H'])} | "
                             f"{result['kernel_dimension']} | {result['visible_rank']} | "
                             f"`{result['residue']}` |")
            lines += ["", "## Fixed compact branch", "",
                      f"The undeformed ladder has x(0)={branch['x0']:.12g} and "
                      f"1-x(0)={branch['denominator_margin']:.12g}.",
                      "Its analytic denominator margin exceeds the exact rational bound "
                      f"`{branch['rational_denominator_margin_lower_bound']}`.",
                      "The radius and detuning are evaluated by A_R/c=4/27 and x(chi_c)=1.",
                      "For chi(Q^2)=chi_c-a Q^2+O(Q^4), a>0, the matched scalar",
                      "propagation residue is J(chi_c)/(c^4 a x'(chi_c)).",
                      "The external branch and its slope are determined from the sourced propagation action.", ""]

        tensor = extension.get("external_gauge_tensor", {})
        if tensor:
            match = tensor["ladder_matching"]
            lines += ["## External gauge-tensor realization", "",
                      "The specified quadratic Fierz-Pauli action has two physical helicities.",
                      "Its exact reduced kernel is Z Q^2 I_2; the source residue is g^2/Z.",
                      "The scope is the quadratic gauge action with leading conserved-source exchange.",
                      "Inverse-response matching to the compact ladder fixes the critical coordinate",
                      "and the external momentum conversion on the matched branch.", "",
                      f"- Z = {tensor['kinetic_GeV_squared']:.16g} GeV^2",
                      f"- residue = {tensor['residue_GeV_inverse_squared']:.16g} GeV^-2",
                      f"- G = {tensor['newton_GeV_inverse_squared']:.16g} GeV^-2",
                      f"- chi(0) = {match['chi_at_zero']:.16g}",
                      f"- -dchi/d(Q^2/M_P^2) = {match['minus_dchi_dq_squared']:.16g}",
                      "", "| Q^2/M_P^2 | chi | momentum times response | spectral evaluations |",
                      "|---:|---:|---:|---:|"]
            for row in match["resolved_momentum_branches"]:
                lines.append(f"| {row['q_squared']:.8g} | {row['chi']:.16g} | "
                             f"{row['momentum_times_response']:.16g} | {row['spectral_evaluations']} |")
            lines.append("")

            completion = tensor.get("classical_completion", {})
            if completion:
                ward = completion["verification"]
                lines += ["### Classical tensor and matter completion", "",
                          completion["action"], completion["normalization"],
                          completion["level"],
                          "The arbitrary-field Noether identity is proved in Guo (2026f).",
                          "The exact local field-derivative checks evaluate that identity",
                          "and its field-amplitude coefficients for specified rational data.",
                          "They include a nonzero missing-cubic-vertex control.",
                          "These checks concern the macroscopic classical effective action,",
                          "its collective tensor response and conserved-source coupling.",
                          f"Local Ward checks passed: {ward['passed']}", ""]

        native_matter = extension.get("finite_matter_source", {}).get(
            "canonical_matter_dynamics", {})
        if native_matter:
            lines += ["## Canonical internal matter-source dynamics", "",
                      native_matter["scope"], native_matter["action"],
                      "The source histories use the same operator, occupations and compression profiles",
                      "as the static matter response. Both frequency branches and their correlations",
                      "enter the causal response, including the direct second source variation.", "",
                      f"- source-charge relative residual: {native_matter['static_charge_relative_residual']:.12g}",
                      f"- causal-equation relative residual: {native_matter['causal_response_relative_residual']:.12g}",
                      f"- response cutoff comparison: {native_matter['response_relative_cutoff_residual']:.12g}",
                      f"- maximum canonical-form residual: {native_matter['maximum_canonical_form_residual']:.12g}",
                      f"- maximum source-work balance residual: {native_matter['maximum_energy_balance_residual']:.12g}",
                      f"- dominant operation counts: {native_matter['dominant_operation_counts']}", "",
                      "The exact finite source protocol has positive matter kinetic and spatial forms.",
                      "The external gravitational response additionally requires the collective metric",
                      "source map and the reduction of its common constraints.", ""]
            clock_chart = native_matter.get("clock_reparametrization", {})
            if clock_chart:
                lines += ["### Clock parametrization of the same source history", "",
                          clock_chart["clock_relation"], clock_chart["clock_role"],
                          f"- relative phase-covariance residual: {clock_chart['relative_phase_covariance_residual']:.12g}",
                          f"- source-work residual: {clock_chart['maximum_source_work_residual']:.12g}",
                          f"- additional source-family evaluations: {clock_chart['additional_source_family_evaluations']}",
                          f"- reused source families: {clock_chart['reused_source_families']}",
                          f"- additional exact propagators: {clock_chart['additional_exact_segment_propagators']}", ""]

        native_covariant = extension.get("finite_matter_source", {}).get(
            "native_covariant_interface", {})
        if native_covariant:
            lines += ["## Covariant native source and metric constraints", "",
                      native_covariant["scope"], native_covariant["covariant_action"],
                      native_covariant["source_exchange_identity"], "",
                      f"- stress-divergence residual: {native_covariant['maximum_ward_residual']:.12g}",
                      f"- normal stress / lapse-source residual: {native_covariant['normal_stress_residual']:.12g}",
                      f"- momentum stress / shift-source residual: {native_covariant['momentum_stress_residual']:.12g}",
                      f"- source-work charge residual: {native_covariant['source_work_charge_residual']:.12g}",
                      f"- Legendre-transform residual: {native_covariant['legendre_residual']:.12g}",
                      f"- dominant operation counts: {native_covariant['dominant_operation_counts']}", "",
                      "The source and matter equations enter the total covariant conservation law.",
                      "The uniform canonical dilation retains its mixed velocity form and primary constraint.", ""]
            polar = native_covariant.get('polar_source_congruence', {})
            if polar:
                lines += ["### Generated matter-phase congruence", "",
                          "The complex coordinate pairs two existing equal-mass real directions of the same carrier.",
                          "The polar equations determine its unit flow, stress, source exchange and acceleration remainder.",
                          f"Maximum residuals: {polar['maximum_residuals']}",
                          f"Operation counts: {polar['operation_counts']}", "",
                          "The local cases include a static accelerated phase, homogeneous expansion and a nonzero radial-pressure gradient.",
                          "Their existing field derivatives also determine the proper-time phase rate and the exterior derivative of the clock one-form.",
                          "Closure of that one-form supplies the local unit-gradient dust clock; the accelerated case retains proper time along each curve.", ""]
                for name, case in polar['cases'].items():
                    clock_readout = case.get('clock', {})
                    if clock_readout:
                        exterior = clock_readout['clock_covector_exterior_derivative']
                        lines.append(f"- {name}: phase rate = {clock_readout['phase_rate_per_proper_time']:.12g}; "
                                     f"maximum clock exterior-derivative component = {max(abs(x) for row in exterior for x in row):.12g}")
                lines.append("")

        weak_matching = extension.get("matter_extensions", {}).get(
            "electroweak_finite_matching", {}).get("generated_fermi_readout", {})
        if weak_matching:
            lines += ["## Generated Fermi-input matching", "",
                      "The same generated weak input is represented in the tadpole-free",
                      "Landau-gauge MSbar VEV convention through one loop.",
                      "Six stored readouts supply the leading couplings and reference scale;",
                      "the finite coefficient is evaluated once without additional RG evolution.", "",
                      f"- Q = {weak_matching['scale_GeV']:.16g} GeV",
                      f"- v_F = {weak_matching['input_fermi_vev_GeV']:.16g} GeV",
                      f"- G_F = {weak_matching['G_F_preserved_GeVminus2']:.16g} GeV^-2",
                      f"- v_L = {weak_matching['running_vev_GeV_first_order']:.16g} GeV",
                      f"- v_L squared = {weak_matching['running_vev_squared_GeV2_first_order']:.16g} GeV^2",
                      f"- Delta r = {weak_matching['delta_r_one_loop']:.16g}",
                      f"- one-loop tadpole term = {weak_matching['tadpole_one_loop_GeV2']:.16g} GeV^2", "",
                      "The VEV and its square are separately truncated series.",
                      "Finite native-source readout corrections retain their source-matching definitions.", ""]

        lepton_matching = extension.get("matter_extensions", {}).get(
            "electroweak_finite_matching", {}).get("generated_charged_lepton_realization", {})
        if lepton_matching:
            lines += ["## Charged-lepton finite matching", "",
                      "The generated masses define three pole conditions of the common electroweak action.",
                      "The photon, W, Z and Higgs terms retain finite charged-lepton masses.",
                      f"- matching scale: {lepton_matching['scale_GeV']:.16g} GeV",
                      f"- weighted one-loop correction: {lepton_matching['charged_lepton_log_correction']:.16g}",
                      f"- finite weak part: {lepton_matching['finite_weak_log_correction']:.16g}",
                      f"- numerical interval: {lepton_matching['charged_lepton_log_correction_interval']}",
                      f"- work: {lepton_matching['evaluation_work']}",
                      f"- uncomputed orders: {lepton_matching['uncomputed_orders']}", "",
                      "The interval encloses numerical evaluation at fixed input values; the perturbative remainder is separate.", ""]
            lepton_test = extension.get("joint_response", {}).get(
                "running_mass_comparison", {}).get("generated_pole_lepton_test", {})
            if lepton_test:
                lines += [f"- required weighted matching: {lepton_test['required_weighted_matching']:.16g}",
                          f"- reference standard uncertainty: {lepton_test['reference_standard_uncertainty']:.16g}",
                          f"- required minus predicted at the reference scale: {lepton_test['required_minus_predicted']:.16g}", "",
                          "The comparison retains the uncomputed perturbative remainder; no theory significance is assigned.", ""]

        weak_comparison = extension.get("joint_response", {}).get("neutron_helium_comparison", {})
        if weak_comparison:
            lines += ["## Common neutron and helium comparison", "", weak_comparison['reference'], "",
                      "| quantity | calculated | reference | central residual (%) |",
                      "|---|---:|---:|---:|"]
            for row in weak_comparison['rows']:
                lines.append(f"| {row['quantity']} ({row['units']}) | {row['prediction']:.12g} | "
                             f"{row['reference']:.12g} | {row['relative_percent']:+.6g} |")
            joint_weak = records.get('bbn_joint_response', {}).get('value', {})
            if joint_weak:
                lines += ["", "The shared-input Jacobian propagates independently supplied covariance or interval errors.",
                          f"Operation counts: {joint_weak['operation_counts']}"]
            lines += ["", "No joint significance is assigned without the weak-rate and hadronic theory covariance.", ""]
            lattice = weak_comparison.get('independent_lattice_matching', {})
            if lattice:
                forward = lattice['weak_chain']
                lines += ["### Independent QCD+QED comparison", "",
                          lattice['matching_scope'], "",
                          "| input variation | mass difference (GeV) | lifetime (s) | helium fraction |",
                          "|---|---|---|---|"]
                for name, item in forward['ranges'].items():
                    bounds = item['output_ranges']
                    lines.append(f"| {name} | {bounds['dm_np']} | {bounds['tau_n']} | {bounds['Y_p']} |")
                lines += ["", forward['range_interpretation'],
                          forward['numerical_error_status'],
                          f"Operation counts: {forward['operation_counts']}", ""]
        colour = extension.get('joint_response', {}).get('three_quark_source', {})
        if colour:
            lines += ["## Generated three-quark source channels", "", colour['scope'],
                      f"- colour-singlet multiplicity: {colour['colour_singlet_multiplicity']}",
                      f"- independent adjoint source channels: {colour['independent_adjoint_source_channels']}",
                      f"- exact source Gram matrix: {colour['adjoint_source_gram_exact']}",
                      f"- maximum finite algebra residual: {max(colour['residuals'].values()):.6g}",
                      f"- evaluated bound-state mass operator: {colour['mass_operator_computed']}",
                      f"- evaluation work: {colour['evaluation_work']}", ""]

        pole_matching = extension.get("matter_extensions", {}).get(
            "electroweak_finite_matching", {}).get("generated_on_shell_realization", {})
        if pole_matching:
            # Report the evaluated physical conditions and operation counts
            # from the saved result. Reporting performs no loop calculation.
            pole = pole_matching["pole_kernel"]
            matched = pole_matching["matched_couplings_first_order"]
            work = pole_matching["evaluation_work"]
            lines += ["## Generated on-shell matter conditions", "",
                      "The generated Fermi constant and real top/Higgs pole masses specify",
                      "physical renormalization conditions of this effective realization.",
                      "The finite Yukawa, quartic and quadratic coefficients are evaluated",
                      "in the Landau-gauge tadpole-free MSbar top-Yukawa truncation.",
                      "The three gauge coefficients remain specified leading boundaries.", "",
                      f"- Q = {pole_matching['scale_GeV']:.16g} GeV",
                      f"- y_t = {matched[3]:.16g}",
                      f"- lambda = {matched[4]:.16g}",
                      f"- m squared = {pole_matching['matched_quadratic_GeV2_first_order']:.16g} GeV^2",
                      f"- top mass correction = {pole['top_mass_correction_GeV']:.16g} GeV",
                      f"- Higgs squared-mass correction = {pole['higgs_squared_correction_GeV2']['real']:.16g} GeV^2",
                      f"- Born top width (m_b=0, |V_tb|=1) = {pole['top_width_GeV_first_order']:.16g} GeV",
                      f"- first-order condition residuals (GeV^2): {pole_matching['condition_residuals_GeV2_first_order']}",
                      f"- distinct A values: {work['distinct_A_values']}",
                      f"- distinct B values: {work['distinct_B_values']}",
                      f"- quadrature integrand evaluations: {work['quadrature_integrand_evaluations']}",
                      f"- additional Fermi-kernel calls: {work['fermi_kernel_calls']}", "",
                      "The source-identification interface is retained with its actual status.",
                      "These parameters and their physical conditions are recorded separately",
                      "from the production mass readouts.", ""]

        thermal = extension.get("matter_extensions", {}).get("thermal_weak", {})
        if thermal and "evaluation_work" in thermal:
            work = thermal["evaluation_work"]
            lines += ["## Continuous thermal evolution", "", thermal["scope"],
                      f"- final neutron fraction = {thermal['neutron_fraction_final']:.16g}",
                      f"- final neutrino temperature = {thermal['Tnu_final_GeV']:.16g} GeV",
                      f"- EOS evaluations / requests = {work['eos_evaluations']} / {work['eos_requests']}",
                      f"- weak-rate evaluations / requests = {work['weak_rates_evaluations']} / {work['weak_rates_requests']}",
                      f"- quadrature calls = {work['quadrature_calls']}",
                      f"- integrand evaluations = {work['integrand_evaluations']}",
                      f"- cache capacity per kernel = {work['cache_capacity_per_kernel']}", "",
                      "The call-local caches use exact temperature arguments and fixed physical inputs.",
                      "Operation counts come from existing quadrature diagnostics.", ""]

        joint = extension.get("joint_response", {}).get("geometric_mass_relation", {})
        if joint:
            lines += ["## Joint mass relation", "",
                      "The geometric mass combination uses weights 8, 9 and -17 on the three sector log ratios.",
                      f"Residual: {joint['residual']:.16g}.",
                      f"Shared log-input derivatives: {joint['input_log_derivative']}.",
                      "The physical-mass interface propagates the full joint covariance of six log masses",
                      "and their independently supplied matching coefficients.", ""]

        bandwidth = extension.get("bandwidth_response", {})
        if bandwidth:
            certificate = bandwidth["all_bandwidth_certificate"]
            lines += ["## Joint bandwidth response", "",
                      bandwidth["scope"], "",
                      "| R | c_R | v_R/v_5 | m_e,R/m_e,5 | joint relative residual |",
                      "|---:|---:|---:|---:|---:|"]
            for row in bandwidth["rows"]:
                lines.append(f"| {row['radius']:g} | {row['endpoint']:.12g} | "
                             f"{row['v_over_reference']:.12g} | {row['electron_over_reference']:.12g} | "
                             f"{row['mass_elimination_relative_residual']:.4g} |")
            lines += ["", f"All R>=5 endpoint enclosure: {certificate['all_bandwidth_endpoint']}.",
                      f"Three-position platform certified: {certificate['three_position_platform_certified']}.",
                      f"Certificate operations: {certificate['work']}.",
                      f"Response operations: {bandwidth['work']}.", ""]

        feedback = extension.get("local_source_feedback", {})
        if feedback:
            lines += ["## Local nonlinear source feedback", "", feedback["scope"],
                      "The fixed physical interval, initial masses and velocities, acceleration scale",
                      "and boundary values are registered with the calculation.", "",
                      "| steps | maximum energy-balance residual | mass residual | minimum cell length | field solves |",
                      "|---:|---:|---:|---:|---:|"]
            for row in feedback["evaluations"]:
                lines.append(f"| {row['time_steps']} | {row['maximum_energy_balance_residual']:.12g} | "
                             f"{row['mass_conservation_residual']:.4g} | {row['minimum_cell_length']:.12g} | "
                             f"{row['operation_counts']['field_solves']} |")
            lines += ["", f"Energy-error reduction factor: {feedback['energy_error_reduction_factor']:.12g}.",
                      f"Final-position difference: {feedback['final_position_difference']:.12g}.",
                      "Time-step refinement is evaluated at fixed material-cell resolution.", ""]
            foliation = feedback.get("covariant_clock", {})
            if foliation:
                kinetic = foliation['accelerated_static_kinetics']
                lines += ["## Independent-foliation effective realization", "",
                          foliation['action'], foliation['scope'],
                          f"Equation and evolution checks passed: {foliation['verification']['consistency_checks_passed']}",
                          f"Accelerated longitudinal threshold: {kinetic['parallel_threshold']:.12g}",
                          f"Minimum kinetic coefficient in its stated normalization: {kinetic['minimum_kinetic_over_twice_planck_gradient_metric']:.12g}",
                          "The positive dust-vacuum reduction and the negative accelerated direction belong to this action and their stated backgrounds.",
                          "The native theory is varied on its generated variables; its physical kinetic form follows from its own common constraint reduction.",
                          "The invariant-subsystem condition applies when this particular parent evolution is retained.", ""]

        bao = records.get("endpoint_bao_record", {}).get("value", {})
        scale = bao.get("scale_diagnostic", {})
        if scale:
            lines += ["## Correlated BAO comparison", "",
                      f"Fixed model: chi squared = {bao['chi2']:.12g}, "
                      f"degrees of freedom = {bao['degrees_of_freedom']}, p = {bao['pte']:.12g}.",
                      f"Common-scale diagnostic: alpha = {scale['alpha']:.12g} "
                      f"+/- {scale['alpha_standard_error']:.12g}.",
                      f"Scale contribution = {scale['chi2_scale']:.12g}; "
                      f"orthogonal contribution = {scale['chi2_orthogonal']:.12g}.",
                      "The diagnostic projection uses the retained distances and covariance factor.", ""]
        thermal_budget = extension.get('joint_response', {}).get('thermal_history_comparison', {})
        if thermal_budget:
            lines += ["## Finite thermal-history response", "",
                      thermal_budget['statistical_interpretation'],
                      f"- late-ionization sound horizon (Mpc): {thermal_budget['late_ionization']['sound_horizon_interval_Mpc']}",
                      f"- late-ionization chi-squared range: {thermal_budget['late_ionization']['chi2_interval']}"]
            for row in thermal_budget.get('direct_hyrec_atomic_response', []):
                lines += [f"- HYREC {row['atomic_inputs']}: sound horizon (Mpc) {row['sound_horizon_interval_Mpc']}; "
                          f"chi squared {row['chi2_interval']}"]
            lines += [f"Distance propagation work: {thermal_budget['operation_counts']}",
                      "The late-ionization range covers its stated redshift sector. The direct atomic-input response retains the atomic and radiative-transfer approximation of its solver.", ""]

        intensity = extension.get("native_scalar_intensity", {})
        if intensity:
            response = intensity["intensity"]
            lines += ["## Native scalar intensity", "", intensity["scope"],
                      f"Inputs: {intensity['inputs']}",
                      f"Pole mass squared: {response['pole_mass_squared']}",
                      f"Positive pole residue: {response['pole_residue']}",
                      f"Continuum threshold squared: {response['continuum_threshold_squared']}",
                      f"Subtracted complete response: {response['subtracted_response']}",
                      f"Omitted continuum upper bound: {response['continuum_tail_upper']}",
                      "The scalar root certificate is evaluated once and reused.",
                      "Independent two-particle dispersion integrals test the rational bubble bounds.",
                      "The spectrum belongs to the declared quadratic scalar realization.", ""]
            joint_source = intensity.get("joint_collective_source", {})
            if joint_source:
                lines += ["## Joint native amplitude and radius equilibrium", "",
                          joint_source["scope"],
                          joint_source["potential_normalization"], "",
                          f"- selected radius: {joint_source['selected_radius']}",
                          f"- scaled amplitude: {joint_source['scaled_amplitude_u']}",
                          f"- joint Hessian diagonal: {joint_source['joint_hessian_u_z_diagonal']}",
                          f"- relaxed compression curvature: {joint_source['relaxed_eta_curvature']}",
                          f"- distinct additional stationary certificates: {joint_source['stationary_certificate_evaluations']}",
                          f"- spectral tail reused: {joint_source['spectral_tail_reused']}", "",
                          "The same relative potential has a unique positive joint static minimum.",
                          "The source action supplies its physical density normalization and temporal terms.", ""]
            occupied = intensity.get("occupied_common_background", {})
            if occupied:
                rows = occupied["samples"]
                lines += ["## Occupied common source and metric background", "",
                          occupied["scope"], "", occupied["source_equation"],
                          f"- dimensionless duration: {occupied['inputs']['duration']}",
                          f"- minimum sampled velocity curvature: {min(r['velocity_source_curvature'] for r in rows)}",
                          f"- minimum sampled characteristic speed squared: {min(min(r['characteristic_speeds_squared']) for r in rows)}",
                          f"- maximum relative Friedmann residual: {occupied['maximum_relative_friedmann_residual']}",
                          f"- maximum relative phase-charge residual: {occupied['maximum_relative_charge_residual']}",
                          f"- independent phase reconstruction residual: {occupied['clock']['phase_reconstruction_residual']}",
                          f"- operation counts: {occupied['operation_counts']}", ""]
                certificate = occupied.get("finite_time_certificate", {})
                if certificate:
                    lines += ["Continuous interval certification uses a phase-space box and an exit-time bound.",
                              f"- certified dimensionless duration: {certificate['duration_in_inverse_energy_unit']}",
                              f"- constrained curvature enclosure: {certificate['constrained_curvature_h']}",
                              f"- characteristic speed squared lower bound: {certificate['sound_speed_squared_lower_bound']}",
                              f"- phase-clock rate enclosure: {certificate['phase_clock_rate']}",
                              f"- certification work: {certificate['work_counts']}", "",
                              "This interval is certified independently of the longer floating-point trajectory.", ""]
                plane = occupied.get('planar_evolution', {})
                if plane:
                    lines += ["## Nonuniform common source and metric evolution", "",
                              plane['scope'], f"Inputs: {plane['inputs']}",
                              f"Verification: {plane['checks']}",
                              f"Operation counts: {plane['operation_counts']}", ""]
        expanding = extension.get('local_source_feedback', {}).get('expanding_window', {})
        if expanding:
            lines += ["## Expanding nonlinear response window", "", expanding['scope'],
                      f"Inputs: {expanding['inputs']}",
                      f"Common constraint: {expanding['constraint']}",
                      f"Homogeneous limit: {expanding['homogeneous_limit']}",
                      f"Local response: {expanding['local_limit']}",
                      f"Verification: {expanding['checks']}",
                      f"State refinement difference: {expanding['maximum_state_refinement_difference']}",
                      f"Operation counts: {expanding['operation_counts']}", "",
                      "The retained variational equations and the omitted spatial-mode residuals are recorded separately.", ""]

    failures = [result for result in results if not result["ok"]]
    if failures:
        lines += ["## Failed checks", ""]
        for result in failures:
            lines += [f"### {result['label']}", "", result["output"].strip(), ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reviewer-grade V5 verification.")
    parser.add_argument("--fresh", action="store_true",
                        help="rebuild from empty temporary stores; publish only after success")
    parser.add_argument("--no-reproduce", action="store_true",
                        help="verify existing run manifest and current source hashes without rerunning")
    parser.add_argument("--audit", action="store_true",
                        help="accepted for readability; audits run by default")
    parser.add_argument("--lean", action="store_true",
                        help="compile every lean_proofs/*.lean file; fails if lean.exe is missing")
    parser.add_argument("--lean-exe",
                        help="optional lean.exe path passed through to the strict Lean verifier")
    parser.add_argument("--lean-key-only", action="store_true",
                        help="compile the selected matter, two-loop and cold-source proofs")
    parser.add_argument("--foundations", action="store_true",
                        help="compile and audit the separately pinned independent proof library")
    parser.add_argument("--foundations-lake-exe",
                        help="pinned Lake executable for --foundations; independent of --lean-exe")
    parser.add_argument("--foundations-project", type=Path,
                        help="independent proof checkout; otherwise FOUNDATIONS_PROJECT or the sibling directory")
    parser.add_argument("--pytest", action="store_true",
                        help="run the Python test suite")
    parser.add_argument("--test-scope", choices=("all", "core"),
                        help="with --pytest: all tests (default) or core tests excluding "
                             "numerical certification and auxiliary checks")
    parser.add_argument("--stability", action="store_true",
                        help="fresh-rerun the official chain and compare generated parameter records")
    parser.add_argument("--full-comparison", action="store_true", default=True,
                        help="run comparison/param_audit_full.py (default)")
    parser.add_argument("--skip-full-comparison", action="store_true",
                        help="skip the full observed-value comparison table")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT,
                        help="Markdown report path")
    args = parser.parse_args()
    if args.fresh and args.no_reproduce:
        parser.error("--fresh and --no-reproduce cannot be combined")
    if args.test_scope and not args.pytest:
        parser.error("--test-scope requires --pytest")
    if args.foundations_lake_exe and not args.foundations:
        parser.error("--foundations-lake-exe requires --foundations")
    if args.foundations_project and not args.foundations:
        parser.error("--foundations-project requires --foundations")
    if args.foundations_project:
        os.environ["FOUNDATIONS_PROJECT"] = str(args.foundations_project.resolve())

    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    results: list[dict] = []
    not_executed = []
    reproduction = None
    if args.no_reproduce:
        not_executed.append("Full reproduction during this verification invocation (--no-reproduce).")
    else:
        reproduction = run("full reproduction", [PY, "-B", "scripts/reproduce_v5.py"])
        results.append(reproduction)
    results.extend(run_source_audits(reproduction))
    results.append(run("Lean source audit", [PY, "scripts/audit_lean_sources.py"]))
    results.append(run("numeric precision audit", [PY, "scripts/audit_numeric_precision.py"]))
    results.append(run("path portability audit", [PY, "scripts/audit_path_portability.py"]))
    if not args.skip_full_comparison:
        results.append(run("full comparison table", [PY, "comparison/param_audit_full.py"]))
    if args.pytest:
        core = args.test_scope == "core"
        selection = "not release_audit and not numerical and not auxiliary" if core else "not release_audit"
        if core:
            not_executed.append("Numerical-certification and auxiliary Python tests "
                                "(--test-scope core; use --test-scope all for the full suite).")
        with tempfile.TemporaryDirectory(prefix="v5-test-run-") as temporary:
            results.append(run("pytest (core)" if core else "pytest", [PY, "-B", "-m", "pytest", "-q",
                                          "-o", "addopts=",
                                          "-m", selection,
                                          "-p", "no:cacheprovider",
                                          "--basetemp", str(Path(temporary) / "cases")],
                               display_cmd=f"python -B -m pytest -q -m '{selection}' -p no:cacheprovider --basetemp <temporary>"))
    else:
        not_executed.append("Python test suite (enable with --pytest).")
    if args.lean or args.lean_key_only:
        results.append(run_lean_archive(args.lean_exe, key_only=args.lean_key_only))
        if args.lean_key_only:
            not_executed.append("Lean files outside the selected four-file key-proof suite.")
    else:
        not_executed.append("Lean archive compilation (source audit alone is not compilation).")
    if args.foundations:
        results.append(run_foundations(args.foundations_lake_exe))
    else:
        not_executed.append(FOUNDATIONS_LABEL + " compilation and axiom audit (enable with --foundations).")
    if args.stability:
        results.append(run_numeric_stability())
    else:
        not_executed.append("Isolated full-chain numeric stability rerun (enable with --stability).")
    if args.skip_full_comparison:
        not_executed.append("Full external comparison table (--skip-full-comparison).")
    final_identity = validate_run_manifest()
    final_identity["label"] = "run identity after verification"
    results.append(final_identity)

    record_verification(results, not_executed)
    report = report_text(results, not_executed)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    failed_required = [r for r in results if r["required"] and not r["ok"]]
    try:
        shown_report = report_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        shown_report = str(report_path)
    print(f"verification report: {shown_report}")
    for result in results:
        status = "PASS" if result["ok"] else ("FAIL" if result["required"] else "WARN")
        print(f"{status:4s} {result['label']}")
    return 1 if failed_required else 0


if __name__ == "__main__":
    sys.exit(main())
