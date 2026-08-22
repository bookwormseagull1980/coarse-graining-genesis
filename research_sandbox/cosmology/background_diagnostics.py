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

"""Sandbox study 3: background cosmology and rough growth diagnostics.

This module deliberately uses standard FRW/GR background formulae as a
baseline comparison.  It is not a transparent-gravity perturbation
solver and is not part of the V4 reproduction chain.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_sandbox.cosmology.common import (  # noqa: E402
    C_KM_S,
    SEC_PER_GYR,
    bannered_markdown,
    v4_background,
    write_json,
    write_text,
)


def simpson_integral(fn: Callable[[float], float], a: float, b: float, n: int) -> float:
    if n <= 0:
        raise ValueError("n must be positive")
    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * fn(a + i * h)
    return total * h / 3.0


def e_of_z(z: float, bg: dict[str, float]) -> float:
    zp1 = 1.0 + z
    return math.sqrt(
        bg["Omega_r"] * zp1**4
        + bg["Omega_m"] * zp1**3
        + bg["Omega_Lambda"]
    )


def stable_density_sum_a(a: float, bg: dict[str, float]) -> float:
    return bg["Omega_r"] + bg["Omega_m"] * a + bg["Omega_Lambda"] * a**4


def e_of_a(a: float, bg: dict[str, float]) -> float:
    if a <= 0.0:
        return math.inf
    return math.sqrt(stable_density_sum_a(a, bg)) / (a * a)


def hubble_distance_mpc(bg: dict[str, float]) -> float:
    return C_KM_S / bg["H0_km_s_Mpc"]


def age_gyr(bg: dict[str, float]) -> float:
    def integrand(a: float) -> float:
        if a <= 0.0:
            return 0.0
        return a / math.sqrt(stable_density_sum_a(a, bg))

    age_seconds = simpson_integral(integrand, 0.0, 1.0, 40000) / bg["H0_s"]
    return age_seconds / SEC_PER_GYR


def recombination_redshift(bg: dict[str, float]) -> float:
    """Hu-Sugiyama fitting formula for z_star."""
    wb = bg["Omega_b"] * bg["h"] ** 2
    wm = bg["Omega_m"] * bg["h"] ** 2
    g1 = 0.0783 * wb ** (-0.238) / (1.0 + 39.5 * wb**0.763)
    g2 = 0.560 / (1.0 + 21.1 * wb**1.81)
    return 1048.0 * (1.0 + 0.00124 * wb ** (-0.738)) * (1.0 + g1 * wm**g2)


def sound_horizon_mpc(z_star: float, bg: dict[str, float]) -> float:
    a_star = 1.0 / (1.0 + z_star)
    rb = 3.0 * bg["Omega_b"] / (4.0 * bg["Omega_gamma"])

    def integrand(a: float) -> float:
        denom = math.sqrt(stable_density_sum_a(a, bg))
        cs_factor = math.sqrt(3.0 * (1.0 + rb * a))
        return 1.0 / (denom * cs_factor)

    return hubble_distance_mpc(bg) * simpson_integral(integrand, 0.0, a_star, 20000)


def comoving_distance_mpc(z: float, bg: dict[str, float]) -> float:
    return hubble_distance_mpc(bg) * simpson_integral(lambda x: 1.0 / e_of_z(x, bg), 0.0, z, 40000)


def bao_distance_ratio(z: float, r_s: float, bg: dict[str, float]) -> dict[str, float]:
    dm = comoving_distance_mpc(z, bg)
    hz = bg["H0_km_s_Mpc"] * e_of_z(z, bg)
    dh_z = C_KM_S / hz
    dv = (dm * dm * z * dh_z) ** (1.0 / 3.0)
    return {
        "z": z,
        "D_M_Mpc": dm,
        "D_H_Mpc": dh_z,
        "D_V_Mpc": dv,
        "D_V_over_r_s": dv / r_s,
    }


def growth_unnormalized(a: float, bg: dict[str, float]) -> float:
    if a <= 0.0:
        return 0.0

    def integrand(x: float) -> float:
        if x <= 0.0:
            return 0.0
        return x**3 / stable_density_sum_a(x, bg) ** 1.5

    return e_of_a(a, bg) * simpson_integral(integrand, 0.0, a, 24000)


def growth_factor(a: float, bg: dict[str, float]) -> float:
    return growth_unnormalized(a, bg) / growth_unnormalized(1.0, bg)


def omega_m_of_z(z: float, bg: dict[str, float]) -> float:
    return bg["Omega_m"] * (1.0 + z) ** 3 / e_of_z(z, bg) ** 2


def growth_rate(z: float, bg: dict[str, float]) -> float:
    a = 1.0 / (1.0 + z)
    h = 1.0e-3
    ap = min(1.0, a * math.exp(h))
    am = max(1.0e-5, a * math.exp(-h))
    if ap == am:
        return omega_m_of_z(z, bg) ** 0.55
    dp = growth_factor(ap, bg)
    dm = growth_factor(am, bg)
    return (math.log(dp) - math.log(dm)) / (math.log(ap) - math.log(am))


def transfer_bbks_sugiyama(k_mpc: float, bg: dict[str, float]) -> float:
    omega_m = bg["Omega_m"]
    omega_b = bg["Omega_b"]
    h = bg["h"]
    shape = omega_m * h * math.exp(-omega_b * (1.0 + math.sqrt(2.0 * h) / omega_m))
    q = k_mpc / (shape * h)
    if q <= 0.0:
        return 1.0
    log_term = math.log(1.0 + 2.34 * q) / (2.34 * q)
    poly = (
        1.0
        + 3.89 * q
        + (16.1 * q) ** 2
        + (5.46 * q) ** 3
        + (6.71 * q) ** 4
    ) ** (-0.25)
    return log_term * poly


def growth_suppression_today(bg: dict[str, float]) -> float:
    omega_m = bg["Omega_m"]
    omega_l = bg["Omega_Lambda"]
    denom = (
        omega_m ** (4.0 / 7.0)
        - omega_l
        + (1.0 + omega_m / 2.0) * (1.0 + omega_l / 70.0)
    )
    return 5.0 * omega_m / (2.0 * denom)


def top_hat_window(x: float) -> float:
    ax = abs(x)
    if ax < 1.0e-3:
        return 1.0 - x * x / 10.0 + x**4 / 280.0
    return 3.0 * (math.sin(x) - x * math.cos(x)) / x**3


def sigma8_bbks(bg: dict[str, float]) -> dict[str, float]:
    a_s = bg["A_s"]
    n_s = bg["n_s"]
    omega_m = bg["Omega_m"]
    h = bg["h"]
    k_pivot = 0.05
    h0_mpc = bg["H0_km_s_Mpc"] / C_KM_S
    g0 = growth_suppression_today(bg)
    radius = 8.0 / h

    def delta_m2(k: float) -> float:
        transfer = transfer_bbks_sugiyama(k, bg)
        primordial = a_s * (k / k_pivot) ** (n_s - 1.0)
        matter_factor = (2.0 / 5.0) * g0 * k * k * transfer / (omega_m * h0_mpc**2)
        return primordial * matter_factor * matter_factor

    log_k_min = math.log(1.0e-5)
    log_k_max = math.log(1.0e2)

    def integrand(log_k: float) -> float:
        k = math.exp(log_k)
        window = top_hat_window(k * radius)
        return delta_m2(k) * window * window

    variance = simpson_integral(integrand, log_k_min, log_k_max, 8000)
    sigma8 = math.sqrt(variance)
    return {
        "sigma8_rough": sigma8,
        "S8_rough": sigma8 * math.sqrt(omega_m / 0.3),
        "growth_suppression_g0": g0,
        "R8_Mpc": radius,
        "transfer_model": "BBKS with Sugiyama shape parameter; no BAO wiggles",
        "status": "rough GR baseline, not a V4 transparent-gravity prediction",
    }


def run() -> dict[str, Any]:
    bg = v4_background()
    z_star = recombination_redshift(bg)
    r_s = sound_horizon_mpc(z_star, bg)
    dm_star = comoving_distance_mpc(z_star, bg)
    theta_star = r_s / dm_star
    bao_rows = [bao_distance_ratio(z, r_s, bg) for z in (0.35, 0.57, 1.0, 2.0)]
    growth_rows = []
    for z in (0.0, 0.5, 1.0, 2.0, 3.0):
        a = 1.0 / (1.0 + z)
        growth_rows.append(
            {
                "z": z,
                "D_GR_baseline": growth_factor(a, bg),
                "f_GR_baseline": growth_rate(z, bg),
                "Omega_m_z": omega_m_of_z(z, bg),
            }
        )
    return {
        "study": "background_diagnostics",
        "input_status": "reads V4 background only; writes no V4 parameters",
        "background": {
            "H0_km_s_Mpc": bg["H0_km_s_Mpc"],
            "h": bg["h"],
            "Omega_b": bg["Omega_b"],
            "Omega_dm": bg["Omega_dm"],
            "Omega_m": bg["Omega_m"],
            "Omega_Lambda": bg["Omega_Lambda"],
            "Omega_gamma": bg["Omega_gamma"],
            "Omega_r": bg["Omega_r"],
            "T_CMB_K": bg["T_CMB_K"],
            "n_s": bg["n_s"],
            "A_s": bg["A_s"],
        },
        "derived": {
            "age_Gyr": age_gyr(bg),
            "z_eq": bg["Omega_m"] / bg["Omega_r"] - 1.0,
            "z_star_Hu_Sugiyama": z_star,
            "r_s_star_Mpc": r_s,
            "D_M_star_Mpc": dm_star,
            "theta_star_rad": theta_star,
            "hundred_theta_star": 100.0 * theta_star,
        },
        "bao_baseline": bao_rows,
        "growth_baseline": growth_rows,
        "sigma8_baseline": sigma8_bbks(bg),
        "verdict": {
            "closed_by_this_module": [
                "background age",
                "matter-radiation equality",
                "Hu-Sugiyama recombination redshift",
                "sound-horizon and BAO distance ratios under standard background assumptions",
                "rough GR+BBKS sigma8 baseline",
            ],
            "not_closed_by_this_module": [
                "transparent-gravity perturbation equations",
                "full matter power spectrum with baryon wiggles",
                "CMB angular spectra",
                "nonlinear structure formation",
            ],
            "status": "baseline diagnostic only",
        },
    }


def report(result: dict[str, Any]) -> str:
    bg = result["background"]
    derived = result["derived"]
    bao_rows = "\n".join(
        "| {z:.2f} | {D_M_Mpc:.3f} | {D_H_Mpc:.3f} | {D_V_Mpc:.3f} | "
        "{D_V_over_r_s:.6f} |".format(**row)
        for row in result["bao_baseline"]
    )
    growth_rows = "\n".join(
        "| {z:.2f} | {D_GR_baseline:.6f} | {f_GR_baseline:.6f} | "
        "{Omega_m_z:.6f} |".format(**row)
        for row in result["growth_baseline"]
    )
    sigma = result["sigma8_baseline"]
    body = f"""This sandbox note evaluates standard background and rough
growth diagnostics from the V4 background parameter set.

It is a baseline comparison, not a transparent-gravity perturbation
solver.  No V4 parameter is written by this calculation.

## Background Inputs Read From V4

| quantity | value |
|---|---:|
| H0 | {bg["H0_km_s_Mpc"]:.6f} km/s/Mpc |
| h | {bg["h"]:.8f} |
| Omega_b | {bg["Omega_b"]:.10f} |
| Omega_dm | {bg["Omega_dm"]:.10f} |
| Omega_m | {bg["Omega_m"]:.10f} |
| Omega_Lambda | {bg["Omega_Lambda"]:.10f} |
| Omega_r | {bg["Omega_r"]:.10e} |
| T_CMB | {bg["T_CMB_K"]:.6f} K |
| n_s | {bg["n_s"]:.6f} |
| A_s | {bg["A_s"]:.6e} |

## Derived Background Diagnostics

| quantity | value |
|---|---:|
| age | {derived["age_Gyr"]:.6f} Gyr |
| z_eq | {derived["z_eq"]:.3f} |
| z_star, Hu-Sugiyama | {derived["z_star_Hu_Sugiyama"]:.3f} |
| r_s(z_star) | {derived["r_s_star_Mpc"]:.6f} Mpc |
| D_M(z_star) | {derived["D_M_star_Mpc"]:.6f} Mpc |
| 100 theta_star | {derived["hundred_theta_star"]:.6f} |

## BAO Distance-Ratio Baseline

| z | D_M (Mpc) | D_H (Mpc) | D_V (Mpc) | D_V/r_s |
|---:|---:|---:|---:|---:|
{bao_rows}

## Linear-Growth Baseline

The growth column below is the standard GR matter-Lambda baseline,
normalized to `D(0)=1`.  It is the control case against which a future
transparent-gravity perturbation equation should be compared.

| z | D(z) | f(z) | Omega_m(z) |
|---:|---:|---:|---:|
{growth_rows}

## Rough sigma8 Diagnostic

| quantity | value |
|---|---:|
| sigma8, rough | {sigma["sigma8_rough"]:.6f} |
| S8, rough | {sigma["S8_rough"]:.6f} |
| growth suppression g0 | {sigma["growth_suppression_g0"]:.6f} |

The sigma8 number uses a BBKS transfer function with Sugiyama's shape
parameter and no BAO wiggles.  It is useful as a first warning light,
not as a final spectrum prediction.

## Status

This module closes only baseline calculations.  The genuinely open
work remains: derive transparent-gravity perturbation equations,
compute the full matter power spectrum, and compute the CMB angular
spectra.
"""
    return bannered_markdown("Background Cosmology Diagnostics", body)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, default=Path("research_sandbox/cosmology/outputs"))
    args = ap.parse_args()
    result = run()
    write_json(args.output_dir / "background_diagnostics.json", result)
    write_text(args.output_dir / "BACKGROUND_DIAGNOSTICS.md", report(result))
    print("background cosmology diagnostics complete")
    print("verdict: baseline only; transparent-gravity perturbations remain open")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
