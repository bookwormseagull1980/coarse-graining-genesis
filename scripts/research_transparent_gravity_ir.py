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
Historical linear-sector diagnostic for infrared gravity.

This read-only script checks the quasi-static scaling of the linear TT
propagator and the effect of changing the self-similar law L(k).  Its
result supplies the linear baseline for the nonlinear endpoint closure
implemented in cg_frg/cosmology/endpoint_residual.py.

Main facts being audited:

1. On the V4 trajectory L(k) = kL/k, the TT denominator has every term
   proportional to k^2.  Hence G_TT(k) is exactly proportional to k^-2
   and the static point-source response is Newtonian.

2. A linear three-dimensional static kernel K(q) proportional to q^-a
   gives phi(r) proportional to r^(a-3) and acceleration proportional
   to r^(a-4), with the special case a = 3 giving phi ~ log r and
   acceleration ~ 1/r.

3. Deep-MOND scaling for a point mass, a ~ sqrt(G M a0)/r, is nonlinear
   in the source mass.  A fixed linear propagator cannot generate that
   mass scaling.

4. The local endpoint branch uses the three-dimensional scale-invariant
   cubic gradient closure.  Its p=3 equation gives the deep-infrared
   point-source relation and the baryonic Tully-Fisher law v^4=GMa0.
   The linear TT result above and this nonlinear local branch occupy
   distinct parts of the current cosmology closure.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.params import get  # noqa: E402
from cg_frg.gravity.tt_tensor import tt_mode_propagator  # noqa: E402


def _slope(x: np.ndarray, y: np.ndarray) -> float:
    ok = (x > 0.0) & (y > 0.0) & np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3:
        return float("nan")
    return float(np.polyfit(np.log(x[ok]), np.log(y[ok]), 1)[0])


def _regulator(p2: np.ndarray, k2: np.ndarray) -> np.ndarray:
    y = p2 / k2
    out = np.zeros_like(y, dtype=np.float64)
    small = y < 100.0
    out[small] = p2[small] / np.expm1(y[small])
    return out


def scan_v4_trajectory(points: int = 320) -> dict[str, Any]:
    kL = float(get("kL"))
    M_G = float(get("M_G"))
    H0 = float(get("H0_GEV"))
    k_vals = np.geomspace(H0, M_G, points)
    G = np.zeros(points)
    Z = np.zeros(points)
    p2_over_k2 = np.zeros(points)
    den_over_k2 = np.zeros(points)

    for i, k in enumerate(k_vals):
        mode = tt_mode_propagator(k=k, J=2, L=kL / k)
        G[i] = mode["G_TT"]
        Z[i] = mode["Z"]
        p2_over_k2[i] = mode["p2"] / (k * k)
        den_over_k2[i] = 1.0 / (mode["G_TT"] * k * k)

    slope_g = _slope(k_vals, G)
    slope_z = _slope(k_vals, Z)
    alpha = -slope_g
    return {
        "kL": kL,
        "M_G_GeV": M_G,
        "H0_GeV": H0,
        "span_decades": math.log10(M_G / H0),
        "p2_over_k2_mean": float(np.mean(p2_over_k2)),
        "p2_over_k2_max_abs_dev": float(np.max(np.abs(p2_over_k2 - p2_over_k2[0]))),
        "den_over_k2_mean": float(np.mean(den_over_k2)),
        "den_over_k2_max_abs_dev": float(np.max(np.abs(den_over_k2 - den_over_k2[0]))),
        "slope_G": slope_g,
        "slope_Z": slope_z,
        "linear_kernel_alpha": alpha,
        "acceleration_power_r": alpha - 4.0,
        "rotation_velocity_power_r": 0.5 * (alpha - 3.0),
        "F_deep_mond_possible_with_fixed_linear_kernel": False,
    }


def scan_scale_law(beta_values: list[float], points: int = 400) -> list[dict[str, Any]]:
    """Toy audit: L(q) = kL/q^beta with q in (0, 1].

    This is not a proposed modification of V4.  It asks a narrower
    question: can a changed self-similar exponent alone make the linear
    TT kernel more infrared-singular than q^-2?
    """
    kL = float(get("kL"))
    q = np.geomspace(1.0e-30, 1.0, points)
    out: list[dict[str, Any]] = []
    for beta in beta_values:
        L = kL / (q ** beta)
        p2 = 8.0 / (L * L)
        m2 = 6.0 / (L * L)
        Rq = _regulator(p2, q * q)
        G = 1.0 / (p2 + m2 + Rq)
        Z = p2 * G
        slope_g = _slope(q, G)
        alpha = -slope_g
        out.append({
            "beta": beta,
            "slope_G": slope_g,
            "linear_kernel_alpha": alpha,
            "slope_Z": _slope(q, Z),
            "acceleration_power_r": alpha - 4.0,
            "rotation_velocity_power_r": 0.5 * (alpha - 3.0),
            "flat_rotation_linear_kernel": abs(alpha - 3.0) < 0.05,
        })
    return out


def linear_kernel_map() -> list[dict[str, Any]]:
    rows = []
    for alpha in (1.0, 2.0, 3.0, 4.0):
        if abs(alpha - 3.0) < 1.0e-12:
            phi = "log(r)"
            acc = "r^-1"
            v = "r^0"
        else:
            phi = f"r^{alpha - 3.0:+.1f}"
            acc = f"r^{alpha - 4.0:+.1f}"
            v = f"r^{0.5 * (alpha - 3.0):+.1f}"
        rows.append({
            "kernel_Kq": f"q^-{alpha:.0f}",
            "potential_phi": phi,
            "acceleration_a": acc,
            "circular_velocity_v": v,
        })
    return rows


def p_laplacian_scan(p_values: list[float], spatial_dim: int = 3) -> list[dict[str, Any]]:
    """Power laws for local nonlinear p-Laplacian IR closures.

    Equation:

        div(|grad phi|^(p-2) grad phi / a0^(p-2)) = 4 pi G rho .

    For a point source in d spatial dimensions:

        a(r) ~ (G M a0^(p-2))^(1/(p-1)) r^(-(d-1)/(p-1)).

    Flat circular velocity in d = 3 requires p = d = 3.
    """
    rows = []
    d = float(spatial_dim)
    for p in p_values:
        acc_power = -(d - 1.0) / (p - 1.0)
        vel_power = 0.5 * (1.0 + acc_power)
        mass_power = 1.0 / (p - 1.0)
        rows.append({
            "p": p,
            "spatial_dim": spatial_dim,
            "acceleration_power_r": acc_power,
            "circular_velocity_power_r": vel_power,
            "source_mass_power": mass_power,
            "flat_rotation": abs(vel_power) < 1e-12,
        })
    return rows


def build_report(result: dict[str, Any]) -> str:
    v4 = result["v4_trajectory"]
    beta_rows = result["scale_law_scan"]

    beta_table = "\n".join(
        "| {beta:.2f} | {linear_kernel_alpha:.6f} | {slope_G:.6f} | "
        "{slope_Z:.6f} | {acceleration_power_r:.6f} | {rotation_velocity_power_r:.6f} |".format(**r)
        for r in beta_rows
    )
    kernel_table = "\n".join(
        "| {kernel_Kq} | {potential_phi} | {acceleration_a} | {circular_velocity_v} |".format(**r)
        for r in result["linear_kernel_map"]
    )
    p_table = "\n".join(
        "| {p:.1f} | {acceleration_power_r:.6f} | {circular_velocity_power_r:.6f} | "
        "{source_mass_power:.6f} | {flat_rotation} |".format(**r)
        for r in result["p_laplacian_scan"]
    )

    return f"""<!--
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
-->

# Transparent Gravity IR Research Note

This note records a research audit, not a paper edit.  It asks whether
the present V4 linear TT propagator can by itself produce a MOND-like
rotation-curve interpolation function.

## Verdict

Within the present linear TT sector, the answer is no.

Along the V4 self-similar trajectory `L(k) = kL/k`, the TT momentum,
Lichnerowicz shift, and exponential regulator are all proportional to
`k^2`.  Therefore the TT propagator is a massless linear kernel
`G_TT(k) ~ k^-2`.  In three spatial dimensions this gives the ordinary
Newtonian point-source response `phi(r) ~ 1/r`, `a(r) ~ 1/r^2`, and a
rotation curve `v(r) ~ r^-1/2`.

The derived acceleration `a0 = c H0/(2 pi) sqrt(4/3)` is therefore a
real IR scale in the framework, but it is not a dynamics.  It does not,
by itself, produce a nontrivial interpolation function `F(a/a0)`.

## Direct V4 Scan

- scale span: `{v4["span_decades"]:.3f}` decades from `M_G` to `H0`
- `p^2/k^2`: `{v4["p2_over_k2_mean"]:.16g}`
- max drift in `p^2/k^2`: `{v4["p2_over_k2_max_abs_dev"]:.3e}`
- denominator/k^2: `{v4["den_over_k2_mean"]:.16g}`
- max drift in denominator/k^2: `{v4["den_over_k2_max_abs_dev"]:.3e}`
- `slope_G = d ln G_TT / d ln k`: `{v4["slope_G"]:.16g}`
- `slope_Z = d ln Z / d ln k`: `{v4["slope_Z"]:.16g}`
- linear kernel exponent `alpha = -slope_G`: `{v4["linear_kernel_alpha"]:.16g}`
- acceleration power: `a(r) ~ r^{v4["acceleration_power_r"]:.6f}`
- circular velocity power: `v(r) ~ r^{v4["rotation_velocity_power_r"]:.6f}`

## What A Linear Kernel Can Do

For a fixed linear static kernel `K(q) ~ q^-alpha` in three spatial
dimensions:

| Kernel | Potential | Acceleration | Circular velocity |
|---|---:|---:|---:|
{kernel_table}

Flat rotation curves require the `alpha = 3` row, or an equivalent
nonlinear field equation.  The present TT kernel is the `alpha = 2`
row.

## Scale-Law Scan

The next table tests the toy family `L(q) = kL/q^beta`.  This is not a
new proposal.  It checks whether changing only the self-similar scale
law can generate the missing IR power.

| beta | alpha=-slope_G | slope_G | slope_Z | acceleration power | velocity power |
|---:|---:|---:|---:|---:|---:|
{beta_table}

Result: this family never reaches `alpha = 3`.  For `beta >= 1`, the
regulator term enforces `G ~ q^-2`; for `beta < 1`, the kernel is less
IR-singular than Newtonian.  A scale-law change alone is not enough.

## Nonlinearity Requirement

Deep-MOND point-source scaling is

```text
a(r) = sqrt(G M a0) / r .
```

The source-mass dependence is `sqrt(M)`.  Any fixed linear propagator
has response proportional to `M`.  Therefore a true MOND interpolation
cannot come from the existing linear TT kernel, and cannot come from a
mass-independent linear replacement alone.  It requires at least one of:

- a nonlinear Poisson equation, e.g. `div[mu(|grad phi|/a0) grad phi] = 4 pi G rho`;
- a source-dependent or environment-dependent IR response;
- a new scalar/vector/auxiliary degree of freedom;
- a genuinely nonlocal IR closure with a clearly stated source law.

Each option is a new dynamical closure unless it can be derived from an
existing V4 identity without adding an adjustable function.

## Minimal Nonlinear Candidate

There is one especially clean candidate if the framework chooses to add
an IR dynamical closure openly rather than hiding it inside the linear
TT sector.

Assume only:

- a local quasi-static potential `phi`;
- a second-order Euler-Lagrange equation;
- the existing derived scale `a0`;
- deep-IR scale invariance in three spatial dimensions.

Then the local action density is forced to the cubic gradient form

```text
L_deep ~ |grad phi|^3 / a0 .
```

The corresponding equation is

```text
div(|grad phi| grad phi / a0) = 4 pi G rho .
```

For a point mass this gives

```text
a(r) = sqrt(G M a0) / r,
v^4 = G M a0 .
```

So the deep-MOND branch and the baryonic Tully-Fisher relation follow
from the cubic IR closure.  The uniqueness can be seen from the
general p-Laplacian family:

| p | acceleration power | velocity power | source-mass power | flat rotation |
|---:|---:|---:|---:|---:|
{p_table}

In three spatial dimensions, flat rotation selects `p = 3`.  This is
promising because the same number `3` is central to the compact
internal spectrum.  But it is not yet a V4 result.  The transition
function between Newtonian and deep-IR regimes, the relativistic
lensing completion, and the cosmological perturbation equations remain
open.

## Research Boundary

The current framework closes homogeneous background quantities such as
`H0`, `Omega_Lambda`, `Omega_b`, `T_CMB`, `eta_B`, flatness, and the
IR acceleration scale.  It does not yet close the structure sector:
galaxy rotation curves, lensing without particle dark matter,
`P(k)`, `sigma8`, `f sigma8`, BAO, or the full CMB angular spectrum.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path)
    ap.add_argument("--report", type=Path)
    args = ap.parse_args()

    result = {
        "v4_trajectory": scan_v4_trajectory(),
        "linear_kernel_map": linear_kernel_map(),
        "scale_law_scan": scan_scale_law([0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]),
        "p_laplacian_scan": p_laplacian_scan([2.0, 2.5, 3.0, 3.5, 4.0]),
        "conclusion": {
            "present_linear_tt_kernel": "Newtonian",
            "F_a_over_a0": "1 within the present linear TT sector",
            "a0_status": "derived IR scale, not a rotation-curve dynamics",
            "requires_new_closure_for_flat_rotation_curves": True,
            "minimal_new_ir_candidate": "local scale-invariant p-Laplacian with p=3",
            "candidate_status": "new dynamical closure, not present linear TT sector",
        },
    }

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(build_report(result), encoding="utf-8")

    v4 = result["v4_trajectory"]
    print("TRANSPARENT GRAVITY IR AUDIT")
    print(f"span_decades = {v4['span_decades']:.3f}")
    print(f"p2/k2        = {v4['p2_over_k2_mean']:.16g}")
    print(f"slope_G      = {v4['slope_G']:.16g}")
    print(f"slope_Z      = {v4['slope_Z']:.16g}")
    print(f"alpha        = {v4['linear_kernel_alpha']:.16g}")
    print(f"a(r) power   = {v4['acceleration_power_r']:.6f}")
    print("verdict      = Newtonian linear response; F(a/a0)=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
