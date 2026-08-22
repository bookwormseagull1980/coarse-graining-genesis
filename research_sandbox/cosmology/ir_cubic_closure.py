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

"""Sandbox study 1: the minimal cubic IR closure.

This is not part of the V4 reproduction chain.  It asks what kind of
new infrared dynamics would be minimally sufficient to turn the
derived scale a0 into flat rotation curves.
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

G_SI_DIAGNOSTIC = 6.67430e-11
M_SUN_KG_DIAGNOSTIC = 1.98847e30


def p_laplacian_power_law(p: float, spatial_dim: int = 3) -> dict[str, Any]:
    """Return point-source power laws for the p-Laplacian family.

    Equation:
        div(|grad Phi|^(p-2) grad Phi / a0^(p-2)) = 4 pi G rho.

    Spherical point-source solution in d dimensions:
        a(r) ~ (G M a0^(p-2))^(1/(p-1)) r^(-(d-1)/(p-1)).
    """
    d = float(spatial_dim)
    acc_power = -(d - 1.0) / (p - 1.0)
    vel_power = 0.5 * (1.0 + acc_power)
    source_mass_power = 1.0 / (p - 1.0)
    a0_power = (p - 2.0) / (p - 1.0)
    return {
        "p": p,
        "spatial_dim": spatial_dim,
        "acceleration_power_r": acc_power,
        "circular_velocity_power_r": vel_power,
        "source_mass_power": source_mass_power,
        "a0_power": a0_power,
        "flat_rotation": abs(vel_power) < 1.0e-12,
    }


def cubic_point_solution(G: float, M: float, a0: float, radii: list[float]) -> dict[str, Any]:
    """Spherical p = 3 solution for positive radii.

    Integrated equation:
        r^2 a(r)^2/a0 = G M.
    """
    rows = []
    v_flat = (G * M * a0) ** 0.25
    for r in radii:
        a = math.sqrt(G * M * a0) / r
        v = math.sqrt(a * r)
        rows.append({"r": r, "acceleration": a, "circular_velocity": v})
    return {
        "equation": "div(|grad Phi| grad Phi / a0) = 4 pi G rho",
        "integrated_spherical_law": "r^2 a(r)^2/a0 = G M",
        "acceleration": "a(r) = sqrt(G M a0)/r",
        "btfr": "v^4 = G M a0",
        "v_flat": v_flat,
        "samples": rows,
    }


def btfr_velocity_examples(a0: float) -> list[dict[str, float]]:
    """Diagnostic BTFR velocities for a few baryonic masses.

    The SI constants are unit-conversion aids for intuition only.  They
    are not written to the V4 parameter store and are not used as
    calibration data.
    """
    rows = []
    for mass_solar in (1.0e8, 1.0e9, 1.0e10, 1.0e11):
        M = mass_solar * M_SUN_KG_DIAGNOSTIC
        v_m_s = (G_SI_DIAGNOSTIC * M * a0) ** 0.25
        rows.append({
            "M_baryon_Msun": mass_solar,
            "v_flat_km_s": v_m_s / 1000.0,
            "diagnostic_only": True,
        })
    return rows


def run() -> dict[str, Any]:
    bg = v4_background()
    p_scan = [p_laplacian_power_law(p) for p in (2.0, 2.5, 3.0, 3.5, 4.0)]
    solution = cubic_point_solution(
        G=1.0, M=1.0, a0=1.0, radii=[1.0, 2.0, 4.0, 8.0]
    )
    return {
        "study": "ir_cubic_closure",
        "input_status": "reads V4 background only; writes no V4 parameters",
        "a0_today_m_s2": bg["a0_today_m_s2"],
        "p_laplacian_scan": p_scan,
        "cubic_solution_dimensionless": solution,
        "btfr_velocity_examples": btfr_velocity_examples(bg["a0_today_m_s2"]),
        "verdict": {
            "minimal_local_deep_ir_candidate": "p = 3 cubic-gradient closure",
            "deep_ir_action_density": "|grad Phi|^3/a0",
            "point_mass_result": "a(r)=sqrt(G M a0)/r and v^4=G M a0",
            "status": "candidate new IR dynamical closure, not an existing V4 result",
            "open_items": [
                "derive the closure from spectral identities rather than postulate it",
                "derive the Newtonian-to-deep-IR interpolation function",
                "construct a relativistic lensing completion",
                "derive linear perturbation equations",
            ],
        },
    }


def report(result: dict[str, Any]) -> str:
    p_rows = "\n".join(
        "| {p:.1f} | {acceleration_power_r:.6f} | {circular_velocity_power_r:.6f} | "
        "{source_mass_power:.6f} | {a0_power:.6f} | {flat_rotation} |".format(**row)
        for row in result["p_laplacian_scan"]
    )
    v_rows = "\n".join(
        "| {M_baryon_Msun:.3e} | {v_flat_km_s:.3f} |".format(**row)
        for row in result["btfr_velocity_examples"]
    )
    body = f"""This sandbox note studies the first follow-up item: whether a
minimal nonlinear IR closure can turn the already-derived acceleration
scale `a0` into flat rotation curves.

It does not modify `cg_params.json` and it is not part of the V4
reproduction chain.

## Result

The clean local candidate is the cubic-gradient deep-IR closure

```text
L_deep ~ |grad Phi|^3/a0
div(|grad Phi| grad Phi / a0) = 4 pi G rho .
```

For a spherical point source, integrating once gives

```text
r^2 a(r)^2/a0 = G M,
a(r) = sqrt(G M a0)/r,
v^4 = G M a0 .
```

Thus the deep-MOND branch and the baryonic Tully-Fisher scaling follow
from the cubic closure.

## Why p = 3

For the local p-Laplacian family

```text
div(|grad Phi|^(p-2) grad Phi / a0^(p-2)) = 4 pi G rho,
```

the point-source acceleration in three spatial dimensions scales as

```text
a(r) ~ (G M a0^(p-2))^(1/(p-1)) r^(-2/(p-1)).
```

| p | acceleration power | velocity power | source-mass power | a0 power | flat rotation |
|---:|---:|---:|---:|---:|---:|
{p_rows}

Only `p = 3` gives flat circular velocity and the required `sqrt(M)`
source scaling.

## Diagnostic BTFR Zero Point

Using the V4-derived present acceleration scale
`a0 = {result["a0_today_m_s2"]:.6e} m/s^2`, the cubic closure gives
the following illustrative BTFR velocities.  The SI values of `G` and
`M_sun` are used only for unit conversion in this sandbox diagnostic.

| baryonic mass (M_sun) | v_flat (km/s) |
|---:|---:|
{v_rows}

## Status

This is promising but not yet a closed V4 result.  The missing pieces
are the derivation of the cubic closure from spectral identities, the
Newtonian-to-deep-IR interpolation function, relativistic lensing, and
linear perturbation equations.
"""
    return bannered_markdown("IR Cubic Closure Sandbox", body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("research_sandbox/cosmology/outputs"))
    args = ap.parse_args()
    result = run()
    write_json(args.output_dir / "ir_cubic_closure.json", result)
    write_text(args.output_dir / "IR_CUBIC_CLOSURE.md", report(result))
    print("IR cubic closure sandbox complete")
    print("verdict: p=3 is the minimal local deep-IR candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
