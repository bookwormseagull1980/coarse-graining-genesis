# -*- coding: utf-8 -*-
"""Write the V5 structural-closure certificates.

Run after the numerical chain has populated the parameter store, because the
capacity/endpoint certificate reads the production endpoint `kL`.

This command is read-only with respect to `cg_params.json`; it writes only
`certificates/structure_certificates.json`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.structure import all_certificates  # noqa: E402


def main() -> int:
    result = all_certificates()
    statuses = {name: cert["status"] for name, cert in result.items()}
    failed = [name for name, status in statuses.items() if status != "PASS"]
    out_dir = _ROOT / "certificates"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "structure_certificates.json"
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"statuses": statuses, "output": str(out_path)}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
