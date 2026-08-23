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

"""
scripts/verify_v4.py -- reviewer-grade end-to-end verification
==============================================================

This is the one-command entry point for reviewers and Git browsers:

    py scripts/verify_v4.py --fresh --audit --lean --pytest

It can rebuild the generated stores from scratch, reproduce the full
V4 chain, audit parameter provenance, audit observed-value isolation,
audit Lean proof-source hygiene, optionally compile the Lean archive,
optionally run the test suite, and write a compact Markdown report.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
DEFAULT_REPORT = ROOT / "V4_VERIFICATION_REPORT.md"
GENERATED_STORES = [
    ROOT / "cg_params.json",
    ROOT / "comparison" / "sm_inputs.json",
    ROOT / "params_write_log.json",
]


def base_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
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


def sanitize_output(text: str) -> str:
    out = text
    for needle in {
        str(ROOT),
        str(ROOT).replace("\\", "/"),
        str(ROOT).replace("\\", "\\\\"),
    }:
        out = out.replace(needle, ".")
    for needle in {PY, PY.replace("\\", "/"), PY.replace("\\", "\\\\")}:
        out = out.replace(needle, "python")
    out = out.replace(".\\.deps", ".deps")
    return out


def run(label: str, cmd: list[str], *, required: bool = True,
        display_cmd: str | None = None) -> dict:
    t0 = time.time()
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
        "seconds": time.time() - t0,
        "output": out,
    }


def remove_generated_stores() -> list[str]:
    removed: list[str] = []
    for path in GENERATED_STORES:
        if path.exists():
            path.unlink()
            removed.append(path.relative_to(ROOT).as_posix())
    return removed


def run_lean_archive(lean_exe: str | None) -> dict:
    cmd = [PY, "scripts/verify_lean_archive.py"]
    display = "python scripts/verify_lean_archive.py"
    if lean_exe:
        cmd.extend(["--lean-exe", lean_exe])
        display += " --lean-exe <lean.exe>"
    return run("Lean proof archive", cmd, display_cmd=display)


def run_numeric_stability() -> dict:
    return run("numeric stability audit", [PY, "scripts/audit_numeric_stability.py"],
               display_cmd="python scripts/audit_numeric_stability.py")


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def store_summary() -> str:
    cg = load_json(ROOT / "cg_params.json").get("parameters", {})
    sm = load_json(ROOT / "comparison" / "sm_inputs.json").get("parameters", {})
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
        f"- sm_inputs comparison records: {len(sm)}",
        "- provenance: " + ", ".join(f"{k}={v}" for k, v in sorted(prov.items())),
        "- roles: " + ", ".join(f"{k}={v}" for k, v in sorted(roles.items())),
        "",
        "### Selected Closed Values",
        "",
        "| key | value | provenance | writer |",
        "|---|---:|---|---|",
    ]
    selected = [
        "kL", "M_G", "g2_MG", "g1_MG_geo", "g3_MG_geo",
        "n_generations", "v_HIGGS", "M_Z_pred", "M_W_pred",
        "M_W_pred_lead1loop", "Gamma_b_pred_1loop",
        "sin2_theta_eff_l_pred", "m_H_pred",
        "Omega_Lambda", "Omega_Sigma", "T_CMB_GeV",
        "T_CMB_corrected_K", "endpoint_sigma8", "endpoint_S8",
        "bbn_Neff",
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


def report_text(results: list[dict], fresh_removed: list[str]) -> str:
    failed_required = [r for r in results if r["required"] and not r["ok"]]
    lines = [
        "<!--",
        "# =============================================================================",
        "#  Coarse-Graining Genesis Framework V4.0",
        "#",
        "#  Author:      Jinku Guo guojk@nwpu.edu.cn",
        "#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China",
        "#  ORCID:       0009-0000-6600-6171
        "#  DOI:         10.5281/zenodo.22067006
        "#",
        "#  Part of the V4 spectral framework, whose physics is presented in the",
        "#  companion papers:",
        "#    [I]  \"The spectrum of a compact internal space.",
        "#          I. Gauge structure and fermion content\"",
        "#    [II] \"The spectrum of a compact internal space.",
        "#          II. Effective couplings and mass scales\"",
        "# =============================================================================",
        "-->",
        "",
        "# V4 Verification Report",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Python: `{platform.python_version()}`",
        "Root: `.`",
        "",
        "## Verdict",
        "",
        "PASS" if not failed_required else "FAIL",
        "",
    ]
    if fresh_removed:
        lines += ["## Fresh Rebuild", "", "Removed generated stores:"]
        lines += [f"- `{item}`" for item in fresh_removed]
        lines.append("")

    lines += ["## Steps", "", "| step | status | seconds | command |",
              "|---|---:|---:|---|"]
    for result in results:
        status = "PASS" if result["ok"] else ("FAIL" if result["required"] else "WARN")
        lines.append(
            f"| {result['label']} | {status} | {result['seconds']:.1f} | "
            f"`{result['cmd']}` |"
        )
    lines.append("")
    lines.append(store_summary())

    lines += ["## Command Output", ""]
    for result in results:
        lines += [
            f"### {result['label']}",
            "",
            "```text",
            result["output"].strip()[-12000:] or "(no output)",
            "```",
            "",
        ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reviewer-grade V4 verification.")
    parser.add_argument("--fresh", action="store_true",
                        help="remove generated stores before reproducing")
    parser.add_argument("--audit", action="store_true",
                        help="accepted for readability; audits run by default")
    parser.add_argument("--lean", action="store_true",
                        help="compile every lean_proofs/*.lean file; fails if lean.exe is missing")
    parser.add_argument("--lean-exe",
                        help="optional lean.exe path passed through to the strict Lean verifier")
    parser.add_argument("--pytest", action="store_true",
                        help="run the Python test suite")
    parser.add_argument("--stability", action="store_true",
                        help="fresh-rerun the official chain and compare generated parameter records")
    parser.add_argument("--full-comparison", action="store_true", default=True,
                        help="run comparison/param_audit_full.py (default)")
    parser.add_argument("--skip-full-comparison", action="store_true",
                        help="skip the full observed-value comparison table")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT,
                        help="Markdown report path")
    args = parser.parse_args()

    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    stale_artifacts = {report_path, ROOT / "docs" / "reviewer_dashboard.html"}
    for path in stale_artifacts:
        try:
            path.resolve().relative_to(ROOT.resolve())
            if path.exists():
                path.unlink()
        except (OSError, ValueError):
            pass

    removed: list[str] = []
    if args.fresh:
        removed = remove_generated_stores()

    results: list[dict] = []
    results.append(run("full reproduction", [PY, "scripts/reproduce_v4.py"]))
    results.append(run("parameter provenance audit", [PY, "scripts/audit_param_writers.py"]))
    results.append(run("observation leakage audit", [PY, "scripts/audit_observation_leakage.py"]))
    results.append(run("Lean source audit", [PY, "scripts/audit_lean_sources.py"]))
    results.append(run("numeric precision audit", [PY, "scripts/audit_numeric_precision.py"]))
    results.append(run("path portability audit", [PY, "scripts/audit_path_portability.py"]))
    if not args.skip_full_comparison:
        results.append(run("full comparison table", [PY, "comparison/param_audit_full.py"]))
    if args.pytest:
        results.append(run("pytest", [PY, "-m", "pytest", "-q", "-p", "no:cacheprovider"]))
    if args.lean:
        results.append(run_lean_archive(args.lean_exe))
    if args.stability:
        results.append(run_numeric_stability())

    report = report_text(results, removed)
    report_path.write_text(report, encoding="utf-8")

    failed_required = [r for r in results if r["required"] and not r["ok"]]
    try:
        shown_report = report_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        shown_report = str(report_path)
    print(f"verification report: {shown_report}")
    for result in results:
        status = "PASS" if result["ok"] else ("FAIL" if result["required"] else "WARN")
        print(f"{status:4s} {result['label']} ({result['seconds']:.1f}s)")
    return 1 if failed_required else 0


if __name__ == "__main__":
    sys.exit(main())
