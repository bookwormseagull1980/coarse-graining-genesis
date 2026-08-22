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

"""Sandbox study 2: possible redshift evolution of the a0 scale.

The present V4 chain derives a present-day acceleration scale.  This
diagnostic keeps the formal question open: is that scale frozen after
the IR endpoint is selected, or does it track H(z)?
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_sandbox.cosmology.common import (  # noqa: E402
    bannered_markdown,
    v4_background,
    write_json,
    write_text,
)


DEFAULT_Z_GRID = (0.0, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0)


def e_of_z(z: float, bg: dict[str, float]) -> float:
    zp1 = 1.0 + z
    return math.sqrt(
        bg["Omega_r"] * zp1**4
        + bg["Omega_m"] * zp1**3
        + bg["Omega_Lambda"]
    )


def branch_rows(z_grid: tuple[float, ...] = DEFAULT_Z_GRID) -> list[dict[str, float]]:
    bg = v4_background()
    a0_today = bg["a0_today_m_s2"]
    rows = []
    for z in z_grid:
        e = e_of_z(z, bg)
        frozen = a0_today
        tracking = a0_today * e
        rows.append(
            {
                "z": z,
                "E_z": e,
                "a0_frozen_m_s2": frozen,
                "a0_tracking_m_s2": tracking,
                "tracking_over_frozen": e,
                "deep_ir_acceleration_ratio": math.sqrt(e),
                "deep_ir_velocity_ratio": e**0.25,
            }
        )
    return rows


def run() -> dict[str, Any]:
    bg = v4_background()
    rows = branch_rows()
    return {
        "study": "a0_evolution",
        "input_status": "reads V4 background only; writes no V4 parameters",
        "a0_today_m_s2": bg["a0_today_m_s2"],
        "branch_definitions": {
            "frozen": "a0(z) = a0(today)",
            "tracking": "a0(z) = a0(today) * H(z)/H0",
        },
        "deep_ir_scaling_if_cubic": {
            "acceleration": "a_deep proportional to sqrt(a0)",
            "velocity": "v_flat proportional to a0^(1/4)",
        },
        "rows": rows,
        "verdict": {
            "status": "open discriminator",
            "recommended_observables": [
                "high-redshift BTFR zero-point evolution",
                "high-redshift rotation curves and dispersion-supported systems",
                "cluster-scale lensing if a relativistic completion is derived",
            ],
            "paper_discipline": (
                "V4 currently has a present-day a0 scale.  A time-evolution "
                "law is an additional cosmological dynamics question."
            ),
        },
    }


def report(result: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {z:.2f} | {E_z:.6f} | {a0_frozen_m_s2:.6e} | "
        "{a0_tracking_m_s2:.6e} | {deep_ir_velocity_ratio:.6f} |".format(**row)
        for row in result["rows"]
    )
    body = f"""This sandbox note keeps the `a0` time-dependence question
separate from the present V4 reproduction chain.

The present V4 value is

```text
a0(today) = {result["a0_today_m_s2"]:.12e} m/s^2 .
```

Two internally simple branches are compared:

```text
frozen:   a0(z) = a0(today)
tracking: a0(z) = a0(today) H(z)/H0 .
```

If the cubic deep-IR closure is later justified, then
`a_deep` scales as `sqrt(a0)` and `v_flat` scales as `a0^(1/4)`.

| z | E(z)=H(z)/H0 | a0 frozen | a0 tracking | tracking velocity ratio |
|---:|---:|---:|---:|---:|
{rows}

## Interpretation

The two branches coincide at `z = 0` and separate quickly at high
redshift.  Therefore this is not a semantic convention: it becomes an
observable prediction once a rotation-curve or lensing dynamics is
closed.

## Status

This diagnostic does not decide between the branches.  It makes the
branch choice explicit so that any later cosmological claim can be
tested against high-redshift BTFR zero-point evolution, galaxy
kinematics, and lensing data.
"""
    return bannered_markdown("a0 Evolution Sandbox", body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("research_sandbox/cosmology/outputs"))
    args = ap.parse_args()
    result = run()
    write_json(args.output_dir / "a0_evolution.json", result)
    write_text(args.output_dir / "A0_EVOLUTION.md", report(result))
    print("a0 evolution sandbox complete")
    print("verdict: frozen and H(z)-tracking are distinct observational branches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
