# -*- coding: utf-8 -*-
"""Write the outward endpoint-root existence certificate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.endpoint_interval import certify_root  # noqa: E402
from cg_core.params import write_json_atomic  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells", type=int, default=2048)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "certificates" / "endpoint_interval.json")
    args = parser.parse_args()
    result = certify_root(cells=args.cells)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(args.output, result)
    print(json.dumps({"status": result["status"],
                      "bracket": result["bracket_decimal"],
                      "cells": result["cells"],
                      "output": str(args.output)}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
