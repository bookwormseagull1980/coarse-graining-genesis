"""Minimal V5 quickstart: generate a finite RP3 scalar-spectrum record."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cg_core.rp3_spectrum import scalar_modes, volume


def build_record() -> dict:
    radius = 1.0
    modes = scalar_modes(radius, 4)
    heat_time = 0.125
    scalar_heat = sum(
        multiplicity * math.exp(-heat_time * eigenvalue)
        for _, eigenvalue, multiplicity in modes
    )
    return {
        "space": "RP3",
        "radius": radius,
        "scalar_modes": [
            {
                "label": label,
                "eigenvalue": round(eigenvalue, 12),
                "multiplicity": multiplicity,
            }
            for label, eigenvalue, multiplicity in modes
        ],
        "mode_capacity": sum(multiplicity for _, _, multiplicity in modes),
        "volume": round(volume(radius), 12),
        "scalar_heat_kernel": round(scalar_heat, 12),
        "heat_time": heat_time,
    }


def main() -> int:
    expected_path = Path(__file__).with_name("expected_output.json")
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    actual = build_record()
    if actual != expected:
        print("quickstart verification failed")
        print(json.dumps(actual, indent=2, sort_keys=True))
        return 1
    print(json.dumps(actual, indent=2, sort_keys=True))
    print("quickstart verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
