"""Verify the finite source-response supplement without changing production stores."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.native_colour_response import colour_source_response
from cg_core.params import read_store_document, write_json_atomic
from cg_core.precision_comparison import gaussian_precision_comparison
from cg_frg.qcd.generated_yang_mills import generated_yang_mills_gap

TESTS = ("tests/test_native_colour_response.py",
         "tests/test_native_curvature_susceptibility.py",
         "tests/test_precision_comparison.py")


def source_fingerprints():
    paths = [p for folder in ("cg_core", "cg_frg") for p in (ROOT/folder).rglob("*.py")]
    paths += [ROOT/p for p in (*TESTS, "tests/conftest.py", "scripts/verify_source_response.py",
                              "scripts/verify_v5.py")]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"certificates/source_response")
    parser.add_argument("--radius", type=float, help="internal radius; default is the current stored kL")
    args = parser.parse_args()
    output = args.output.resolve()
    protected = (ROOT/"cg_params.json", ROOT/"run_manifest.json", ROOT/"V5_VERIFICATION_REPORT.md")
    if output in protected or output.suffix:
        parser.error("output must be a dedicated verification directory")
    source_before = source_fingerprints()
    if args.radius is None:
        document = read_store_document("parameters", source_root=ROOT)
        radius = float(document["parameters"]["kL"]["value"])
        radius_origin = {"path": "cg_params.json", "key": "kL",
                         "sha256": hashlib.sha256((ROOT/"cg_params.json").read_bytes()).hexdigest()}
    else:
        radius, radius_origin = args.radius, {"kind": "command-line radius"}
    gap = generated_yang_mills_gap(radius, certify=False)
    response = colour_source_response(gap)
    finite_comparison = gaussian_precision_comparison(
        [[[2., .3], [.3, 1.]], [[1., -.2], [-.2, 3.]]], [.4, .6], [[.8, .1], [.1, .6]])
    with tempfile.TemporaryDirectory(prefix="source-response-tests-") as temporary:
        junit = Path(temporary)/"tests.xml"
        command = [sys.executable, "-m", "pytest", "-q", *TESTS, "-p", "no:cacheprovider",
                   f"--junitxml={junit}"]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                   encoding="utf-8", errors="replace",
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        print(completed.stdout, end="")
        if completed.returncode:
            print(completed.stderr, file=sys.stderr, end="")
            return completed.returncode
        suites = ET.parse(junit).getroot().findall("testsuite")
        counts = {key: sum(int(s.get(key, 0)) for s in suites)
                  for key in ("tests", "failures", "errors", "skipped")}
    if source_fingerprints() != source_before:
        raise RuntimeError("source changed during focused verification; no success record written")
    payload = {"radius": radius, "radius_origin": radius_origin, "generated_gap": gap,
               "native_colour_source_response": response, "finite_precision_example": finite_comparison}
    output.mkdir(parents=True, exist_ok=True)
    result_path = output/"source_response.json"
    write_json_atomic(result_path, payload)
    manifest = {
        "schema_version": 1, "status": "passed", "kind": "source-response-supplement",
        "verified_at": datetime.now(timezone.utc).isoformat(), "python": sys.version,
        "scope": "finite coefficient moments, complete curvature memory, joint static Schur response and finite Gaussian precision comparison",
        "tests": list(TESTS), "test_counts": counts, "source_sha256": source_before,
        "output_sha256": {"source_response.json": hashlib.sha256(result_path.read_bytes()).hexdigest()},
        "production_stores_modified": False, "full_production_run_repeated": False,
        "interval_certification": False,
    }
    write_json_atomic(output/"verification-manifest.json", manifest)
    print(json.dumps({"status": "passed", "test_counts": counts,
                      "susceptibility": response["joint_static_susceptibility"],
                      "manifest": str(output/"verification-manifest.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
