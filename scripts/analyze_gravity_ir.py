# -*- coding: utf-8 -*-
# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""
Linear and nonlinear scaling relations for infrared gravity.

This read-only script checks the quasi-static scaling of the linear TT
propagator and the effect of changing the self-similar law L(k).  Its
result supplies the linear baseline for the nonlinear endpoint closure
implemented in cg_frg/cosmology/endpoint_residual.py.

Main facts being audited:

1. On the V5 trajectory L(k) = kL/k, the TT denominator has every term
   proportional to k^2.  Hence G_TT(k) is exactly proportional to k^-2
   on that internal trajectory. A Newtonian point-source response follows
   only if a separately specified external static kernel has that power.

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
from cg_core.release import PUBLICATION_NOTICE, publication_metadata
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


def scan_internal_trajectory(points: int = 320) -> dict[str, Any]:
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

    This is not a proposed modification of V5.  It asks a narrower
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
    v5 = result["v5_trajectory"]
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

    notice = "\n".join(PUBLICATION_NOTICE)
    return f"""<!--
{notice}
-->

# Infrared response scaling

The compact trajectory is evaluated with `L(k)=c/k` at fixed `c`.
The resulting internal response has `G_TT(k) proportional to k^-2`.
For an external static response proportional to `q^-2`, the Fourier
transform in three dimensions gives `phi proportional to 1/r`.
The external response and the internal scale trajectory are specified
as separate operators.

## Internal trajectory

- scale span: `{v5["span_decades"]:.3f}` decades
- mean `p^2/k^2`: `{v5["p2_over_k2_mean"]:.16g}`
- maximum variation in `p^2/k^2`: `{v5["p2_over_k2_max_abs_dev"]:.3e}`
- mean denominator divided by `k^2`: `{v5["den_over_k2_mean"]:.16g}`
- maximum variation in that ratio: `{v5["den_over_k2_max_abs_dev"]:.3e}`
- logarithmic response slope: `{v5["slope_G"]:.16g}`
- logarithmic normalization slope: `{v5["slope_Z"]:.16g}`

## Linear static kernels

For a specified external kernel `K(q) proportional to q^-alpha`,
radial Fourier scaling gives the following point-source powers.
At `alpha=3`, the potential is logarithmic, up to its additive constant.

| Kernel | Potential | Acceleration | Circular velocity |
|---|---:|---:|---:|
{kernel_table}

## Dependence on the internal scale law

The family `L(k)=c/k^beta` varies the compact scale while preserving
the same internal operator and regulator.

| beta | alpha | response slope | normalization slope | acceleration power | velocity power |
|---:|---:|---:|---:|---:|---:|
{beta_table}

## Nonlinear static response

The local infrared law used in the endpoint construction has
`div(|grad phi| grad phi/a0)=4 pi G rho`. In spherical symmetry,
its integrated flux gives `a(r)=sqrt(G M a0)/r` and
`v^4=G M a0`. This is the `p=3` member of the specified
p-Laplacian family. The general point-source acceleration is
proportional to `M^(1/(p-1)) r^(-2/(p-1))`.

| p | acceleration power | velocity power | source-mass power | flat rotation |
|---:|---:|---:|---:|---:|
{p_table}

The local source convention, the normalized susceptibility and the
interpolation law are specified in Guo (2026g). These calculations examine
the static scaling relations of that response.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="print the complete diagnostic")
    args = ap.parse_args()

    result = {
        "publication": publication_metadata(),
        "v5_trajectory": scan_internal_trajectory(),
        "linear_kernel_map": linear_kernel_map(),
        "scale_law_scan": scan_scale_law([0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]),
        "p_laplacian_scan": p_laplacian_scan([2.0, 2.5, 3.0, 3.5, 4.0]),
        "conclusion": {
            "present_linear_tt_kernel": "internal k^-2; Newtonian only for separately assigned external kernel",
            "F_a_over_a0": "1 within the present linear TT sector",
            "a0_status": "derived acceleration normalization of the specified local response",
            "nonlinear_ir_equation": "local scale-invariant p-Laplacian with p=3",
            "nonlinear_point_source": "a(r)=sqrt(G*M*a0)/r; v^4=G*M*a0",
        },
    }

    if args.full:
        print(json.dumps(result, indent=2))

    v5 = result["v5_trajectory"]
    print("INFRARED RESPONSE SCALING")
    print(f"span_decades = {v5['span_decades']:.3f}")
    print(f"p2/k2        = {v5['p2_over_k2_mean']:.16g}")
    print(f"slope_G      = {v5['slope_G']:.16g}")
    print(f"slope_Z      = {v5['slope_Z']:.16g}")
    print(f"alpha        = {v5['linear_kernel_alpha']:.16g}")
    print(f"a(r) power   = {v5['acceleration_power_r']:.6f}")
    print("verdict      = internal k^-2; external Newtonian example is conditional")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
