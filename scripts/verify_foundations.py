#!/usr/bin/env python3
"""V5 adapter for the independently maintained arithmetic/physics proof library.

Importing this module does not require a proof checkout. Only an explicit proof
verification reads the release pin and loads the matching external verifier.
The complete proof audit belongs to that library, not to V5.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_NAME = "Lean Formalization of Arithmetic and Basic Physical Interfaces"
DEFAULT_LOCATOR = "../Foundations-from-Minimal-Change"
REFERENCE_NAME = "foundations-reference.json"
MANIFEST_NAME = "verification-manifest.json"
AUDIT_LOG = ".lake/foundations-audit.txt"
VERIFIER_RELATIVE = "scripts/verify_foundations.py"


class VerificationError(RuntimeError):
    """The external proof checkout does not match V5's declared reference."""


def project_path(root: Path = ROOT, project: Path | None = None) -> Path:
    selected = project if project is not None else os.environ.get("FOUNDATIONS_PROJECT")
    return (Path(selected) if selected else Path(root) / DEFAULT_LOCATOR).resolve()


def reference_hash(root: Path = ROOT) -> str:
    return hashlib.sha256((Path(root) / REFERENCE_NAME).read_bytes()).hexdigest()


def read_reference(root: Path = ROOT) -> dict:
    try:
        reference = json.loads((Path(root) / REFERENCE_NAME).read_bytes())
    except (OSError, ValueError) as exc:
        raise VerificationError("Missing or invalid foundations-reference.json") from exc
    fields = {"schema_version", "name", "locator", "source_files", "verifier"}
    if (not isinstance(reference, dict) or set(reference) != fields
            or type(reference["schema_version"]) is not int or reference["schema_version"] != 1
            or reference["name"] != PUBLIC_NAME
            or reference["locator"] != DEFAULT_LOCATOR):
        raise VerificationError("Unsupported independent proof reference")
    source_files = reference["source_files"]
    required = {"GeneratedFoundations.lean", "lean-toolchain", "lakefile.lean",
                "lake-manifest.json", "theorem-index.json"}
    if not isinstance(source_files, dict) or not required <= source_files.keys():
        raise VerificationError("Proof reference does not pin the source and dependency locks")
    for name, digest in source_files.items():
        if (not isinstance(name, str) or not name or "\\" in name or ":" in name
                or PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
            raise VerificationError("Invalid proof source fingerprint")
    verifier = reference["verifier"]
    if (not isinstance(verifier, dict) or set(verifier) != {"path", "sha256"}
            or verifier["path"] != VERIFIER_RELATIVE
            or not isinstance(verifier["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", verifier["sha256"])):
        raise VerificationError("Invalid external verifier fingerprint")
    return reference


def load_project(root: Path = ROOT, project: Path | None = None):
    """Load only the pinned verifier, then verify the complete pinned source set."""
    reference = read_reference(root)
    project = project_path(root, project)
    verifier = project / VERIFIER_RELATIVE
    try:
        verifier_source = verifier.read_bytes()
        digest = hashlib.sha256(verifier_source).hexdigest()
    except OSError as exc:
        raise VerificationError("Independent proof checkout is unavailable; set FOUNDATIONS_PROJECT") from exc
    if digest != reference["verifier"]["sha256"]:
        raise VerificationError("Independent proof verifier differs from the pinned release")
    module_name = "_v5_external_foundations_" + hashlib.sha256(str(verifier).encode()).hexdigest()
    specification = importlib.util.spec_from_file_location(module_name, verifier)
    if specification is None or specification.loader is None:
        raise VerificationError("Cannot load the independent proof verifier")
    module = importlib.util.module_from_spec(specification)
    sys.modules[module_name] = module
    try:
        # Execute exactly the bytes checked above, without trusting a cached .pyc.
        exec(compile(verifier_source, str(verifier), "exec"), module.__dict__)
        snapshot = module.fingerprint(project)
    except Exception as exc:
        sys.modules.pop(module_name, None)
        raise VerificationError("Independent proof verifier could not read its source inventory") from exc
    if snapshot != reference["source_files"]:
        raise VerificationError("Independent proof sources differ from the pinned release")
    return project, module, reference


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--project", "--project-root", dest="project", type=Path)
    selected, forwarded = parser.parse_known_args(argv)
    try:
        project, _, _ = load_project(ROOT, selected.project)
    except (OSError, ValueError, VerificationError) as exc:
        print("Foundations verification unavailable: " + str(exc), file=sys.stderr)
        return 1
    command = [sys.executable, "-B", str(project / VERIFIER_RELATIVE),
               "--project-root", str(project), *forwarded]
    return subprocess.call(command, cwd=project)


if __name__ == "__main__":
    raise SystemExit(main())
