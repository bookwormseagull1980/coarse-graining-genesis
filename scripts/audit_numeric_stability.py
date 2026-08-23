# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#
#  DOI records:
#    [Software] 10.5281/zenodo.22067006
#    [Paper I]  10.5281/zenodo.22067118
#    [Paper II] 10.5281/zenodo.22067469
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#         DOI: 10.5281/zenodo.22067118
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
#         DOI: 10.5281/zenodo.22067469
# =============================================================================

"""
scripts/audit_numeric_stability.py -- fresh-rebuild value stability audit
========================================================================

This audit answers the release question: if the generated stores are removed
and the official V4 chain is rerun, do the parameter values come back exactly?

It compares the pre-run and post-run parameter records in:

  * cg_params.json
  * comparison/sm_inputs.json

The write log is intentionally excluded because its timestamps change on every
run.  Parameter values and metadata are compared by canonical JSON.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
STORE_PATHS = [
    ROOT / "cg_params.json",
    ROOT / "comparison" / "sm_inputs.json",
]
GENERATED_STORES = STORE_PATHS + [ROOT / "params_write_log.json"]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def load_records(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing generated store: {rel(path)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    params = data.get("parameters", {})
    if not isinstance(params, dict):
        raise RuntimeError(f"{rel(path)} has no object-valued 'parameters'")
    return params


def snapshot() -> dict[str, dict[str, Any]]:
    return {rel(path): load_records(path) for path in STORE_PATHS}


def canonical(value: Any) -> str:
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


def remove_generated_stores() -> list[str]:
    removed: list[str] = []
    for path in GENERATED_STORES:
        if path.exists():
            path.unlink()
            removed.append(rel(path))
    return removed


def run_reproduce() -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return subprocess.run(
        [PY, "scripts/reproduce_v4.py"],
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
    removed = remove_generated_stores()
    proc = run_reproduce()
    output = sanitize_output(((proc.stdout or "") + (proc.stderr or "")).strip())
    if proc.returncode != 0:
        print("NUMERIC STABILITY AUDIT FAILED")
        print("  command: python scripts/reproduce_v4.py")
        print(f"  exit: {proc.returncode}")
        print(output[-12000:] or "  (no output)")
        return 1

    after = snapshot()
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
    print("  command: python scripts/reproduce_v4.py")
    print(f"  removed stores: {', '.join(removed) if removed else 'none'}")
    for store, count in sorted(counts.items()):
        print(f"  {store}: {count} stable records")
    print(f"  seconds: {time.time() - t0:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
