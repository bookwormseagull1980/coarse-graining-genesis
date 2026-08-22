# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
scripts/verify_lean_archive.py -- strict Lean proof-archive verifier
===================================================================

Reviewer-grade Lean verification means more than source hygiene.  This script
compiles every lean_proofs/*.lean file with Lean itself and fails on:

  * a missing Lean executable;
  * a Lean version mismatch (default target: 4.7.0);
  * any Lean compilation error;
  * any compiler output in strict mode, including warnings and #eval prints.

It is intentionally independent of Lake/Mathlib so the proof archive remains
auditable with a stock Lean 4.7 binary.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LEAN_ROOT = ROOT / "lean_proofs"
DEFAULT_EXPECT_VERSION = "4.7.0"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def find_lean(explicit: str | None) -> tuple[str | None, str, list[str]]:
    searched: list[str] = []
    if explicit:
        searched.append("--lean-exe")
        return (explicit if Path(explicit).exists() else None, "--lean-exe", searched)
    env_path = os.environ.get("LEAN_EXE")
    if env_path:
        searched.append("LEAN_EXE")
        return (env_path if Path(env_path).exists() else None, "LEAN_EXE", searched)
    found = shutil.which("lean") or shutil.which("lean.exe")
    if found:
        searched.append("PATH")
        return found, "PATH", searched
    searched.append("PATH")
    return None, "not found", searched


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def command_text(cmd: list[str]) -> str:
    return " ".join(f'"{part}"' if " " in part else part for part in cmd)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile and audit lean_proofs/*.lean.")
    parser.add_argument("--lean-exe", help="explicit lean.exe path")
    parser.add_argument("--expect-version", default=DEFAULT_EXPECT_VERSION,
                        help="Lean version substring required in --version output")
    parser.add_argument("--allow-version-mismatch", action="store_true",
                        help="warn instead of fail if the Lean version differs")
    parser.add_argument("--allow-output", action="store_true",
                        help="allow warnings or #eval output from successful files")
    args = parser.parse_args()

    lean, lean_source, searched = find_lean(args.lean_exe)
    if not lean:
        print("LEAN ARCHIVE VERIFY FAILED")
        print("  Lean executable not found.")
        print("  Set LEAN_EXE, pass --lean-exe, or add lean/lean.exe to PATH.")
        print("  locations checked:")
        for item in searched:
            print(f"    - {item}")
        return 1

    version_proc = run_cmd([lean, "--version"])
    version_text = ((version_proc.stdout or "") + (version_proc.stderr or "")).strip()
    if version_proc.returncode != 0:
        print("LEAN ARCHIVE VERIFY FAILED")
        print("  command failed: lean --version")
        print(version_text or "  (no output)")
        return 1

    if args.expect_version and args.expect_version not in version_text:
        status = "WARNING" if args.allow_version_mismatch else "FAILED"
        print(f"LEAN ARCHIVE VERIFY {status}")
        print(f"  expected Lean version containing: {args.expect_version}")
        print(f"  actual: {version_text or '(unknown)'}")
        if not args.allow_version_mismatch:
            return 1

    files = sorted(LEAN_ROOT.glob("*.lean"))
    if not files:
        print("LEAN ARCHIVE VERIFY FAILED")
        print(f"  no Lean files found under {LEAN_ROOT}")
        return 1

    t0 = time.time()
    failures: list[tuple[Path, int, str]] = []
    noisy: list[tuple[Path, str]] = []
    for file in files:
        rel_file = rel(file)
        proc = run_cmd([lean, "--trust=0", "--root=.", rel_file])
        output = ((proc.stdout or "") + (proc.stderr or "")).strip()
        if proc.returncode != 0:
            failures.append((file, proc.returncode, output))
        elif output and not args.allow_output:
            noisy.append((file, output))

    if failures or noisy:
        print("LEAN ARCHIVE VERIFY FAILED")
        print(f"  lean source: {lean_source}")
        print(f"  version: {version_text or '(unknown)'}")
        print(f"  files checked: {len(files)}")
        if failures:
            print(f"  compile failures: {len(failures)}")
            for file, code, output in failures:
                print(f"\nFAIL {rel(file)} (exit {code})")
                print(output or "(no output)")
        if noisy:
            print(f"  unexpected output from successful files: {len(noisy)}")
            for file, output in noisy:
                print(f"\nNOISY {rel(file)}")
                print(output)
        return 1

    print("LEAN ARCHIVE VERIFY CLEAN")
    print(f"  lean source: {lean_source}")
    print(f"  version: {version_text or '(unknown)'}")
    print(f"  files compiled: {len(files)}")
    print(f"  trust level: 0")
    print(f"  strict output: {'no' if args.allow_output else 'yes'}")
    print(f"  seconds: {time.time() - t0:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
