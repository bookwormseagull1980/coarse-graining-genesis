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
scripts/audit_numeric_stability.py -- fresh-rebuild value stability audit
========================================================================

This audit reruns the official chain in an empty temporary output directory
and compares it with the published stores. It never deletes or overwrites
the published stores.

It compares the pre-run and post-run parameter records in:

  * cg_params.json
  * comparison/reference_inputs.json

The write log is intentionally excluded because its timestamps change on every
run. Scientific values and semantic metadata are compared by canonical JSON;
the per-execution run_id is excluded, while source/input fingerprints remain.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cg_core.params import read_store_document
PY = sys.executable
STORE_PATHS = [
    ROOT / "cg_params.json",
    ROOT / "comparison" / "reference_inputs.json",
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_records(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing generated store: {path.name}")
    if path.name == "cg_params.json":
        data = read_store_document(source_root=path.parent)
    elif path.name == "reference_inputs.json" and path.parent.name == "comparison":
        data = read_store_document("references", source_root=path.parent.parent)
    else:
        raise ValueError("stability comparison requires a canonical scientific store")
    params = data.get("parameters", {})
    if not isinstance(params, dict):
        raise RuntimeError(f"{path.name} has no object-valued 'parameters'")
    return params


def snapshot(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return {name: load_records(root / name)
            for name in ("cg_params.json", "comparison/reference_inputs.json")}


def canonical(value: Any) -> str:
    if isinstance(value, dict):
        value = {key: val for key, val in value.items() if key != "run_id"}
        if isinstance(value.get("calculation"), dict):
            value["calculation"] = {key: val for key, val in value["calculation"].items()
                                    if key != "run_id"}
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compare_records(before: dict[str, dict[str, Any]],
                    after: dict[str, dict[str, Any]]) -> list[str]:
    diffs: list[str] = []
    for store in sorted(set(before) | set(after)):
        old = before.get(store, {})
        new = after.get(store, {})
        for key in sorted(set(old) | set(new)):
            if key not in old:
                diffs.append(f"{store}:{key}: added")
                continue
            if key not in new:
                diffs.append(f"{store}:{key}: removed")
                continue
            if canonical(old[key]) != canonical(new[key]):
                old_val = old[key].get("value") if isinstance(old[key], dict) else old[key]
                new_val = new[key].get("value") if isinstance(new[key], dict) else new[key]
                diffs.append(
                    f"{store}:{key}: changed value {repr(old_val)} -> {repr(new_val)}"
                )
    return diffs


def run_reproduce(output_dir: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return subprocess.run(
        [PY, "-B", "scripts/reproduce_v5.py", "--recompute-responses", "--output-dir", str(output_dir)],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


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


def main() -> int:
    t0 = time.time()
    before = snapshot()
    with tempfile.TemporaryDirectory(prefix="v5-stability-") as temporary:
        proc = run_reproduce(Path(temporary))
        output = sanitize_output(((proc.stdout or "") + (proc.stderr or "")).strip())
        if proc.returncode != 0:
            print("NUMERIC STABILITY AUDIT FAILED; published stores unchanged")
            print("  command: python scripts/reproduce_v5.py --output-dir <temporary>")
            print(f"  exit: {proc.returncode}")
            print(output[-12000:] or "  (no output)")
            return 1
        after = snapshot(Path(temporary))
    diffs = compare_records(before, after)
    if diffs:
        print("NUMERIC STABILITY AUDIT FAILED")
        print("  fresh rebuild changed generated parameter records")
        for item in diffs[:80]:
            print(f"  - {item}")
        if len(diffs) > 80:
            print(f"  - ... {len(diffs) - 80} more")
        return 1

    counts = {store: len(records) for store, records in after.items()}
    print("NUMERIC STABILITY AUDIT CLEAN")
    print("  command: python scripts/reproduce_v5.py --output-dir <temporary>")
    print("  published stores unchanged; execution run_id excluded from comparison")
    for store, count in sorted(counts.items()):
        print(f"  {store}: {count} stable records")
    print(f"  seconds: {time.time() - t0:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
