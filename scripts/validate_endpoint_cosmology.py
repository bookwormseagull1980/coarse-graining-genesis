# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""Fixed-parameter comparison checks for endpoint-residual cosmology.

This optional script performs three checks without fitting V4 parameters:

1. DESI DR2 BAO Gaussian likelihood using public mean/covariance files.
2. SPARC rotation-curve residuals with fixed M/L and fixed endpoint mu(y).
3. A bullet-like cluster centroid diagnostic for free endpoint residuals.

The script prints JSON to stdout.  Use ``--output path.json`` only when a
saved result is needed.  It is deliberately outside ``reproduce_v4`` so
the main chain remains offline and deterministic.  The public data sets
are read only after the V4 parameters are fixed.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2_dist

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.params import get  # noqa: E402

DESI_MEAN_URL = (
    "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/"
    "desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt"
)
DESI_COV_URL = (
    "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/"
    "desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt"
)
SPARC_URL = (
    "https://zenodo.org/records/16284118/files/"
    "MassModels_Lelli2016c.mrt?download=1"
)

C_KM_S = 299792.458


def get_float(key: str, fallback: str | None = None) -> float:
    """Read a generated V4 parameter with an optional legacy-key fallback."""

    try:
        return float(get(key))
    except KeyError:
        if fallback is None:
            raise
        return float(get(fallback))


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def v4_values() -> dict[str, float]:
    Omega_b = get_float("Omega_b")
    Omega_sigma = get_float("Omega_Sigma", "Omega_DM")
    Omega_m = Omega_b + Omega_sigma
    H0 = get_float("H0_GEV") * 1.519267447e24 * 3.0856775814913673e19
    return {
        "H0": H0,
        "Omega_b": Omega_b,
        "Omega_Sigma": Omega_sigma,
        "Omega_m": Omega_m,
        "r_drag_Mpc": get_float("endpoint_r_drag_Mpc"),
        "a0_m_s2": get_float("a0_MOND"),
    }


def parse_bao_mean(text: str) -> list[tuple[float, float, str]]:
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        z, val, quantity = line.split()
        rows.append((float(z), float(val), quantity))
    return rows


def bao_chi2(rows, cov, H0: float, Omega_m: float, r_drag: float):
    obs = np.array([r[1] for r in rows])

    def ez(z: float) -> float:
        return math.sqrt(Omega_m * (1.0 + z) ** 3 + (1.0 - Omega_m))

    def dm(z: float) -> float:
        return C_KM_S / H0 * quad(lambda zz: 1.0 / ez(zz), 0.0, z, epsabs=1e-10)[0]

    def dh(z: float) -> float:
        return C_KM_S / (H0 * ez(z))

    def dv(z: float) -> float:
        d_m = dm(z)
        d_h = dh(z)
        return (z * d_m * d_m * d_h) ** (1.0 / 3.0)

    pred = []
    for z, _, quantity in rows:
        if quantity == "DM_over_rs":
            pred.append(dm(z) / r_drag)
        elif quantity == "DH_over_rs":
            pred.append(dh(z) / r_drag)
        elif quantity == "DV_over_rs":
            pred.append(dv(z) / r_drag)
        else:
            raise ValueError(quantity)
    pred = np.array(pred)
    resid = pred - obs
    return float(resid @ np.linalg.inv(cov) @ resid), pred, resid


def bao_best_fit(rows, cov):
    obs = np.array([r[1] for r in rows])
    cinv = np.linalg.inv(cov)

    def dimless(Omega_m: float):
        def ez(z: float) -> float:
            return math.sqrt(Omega_m * (1.0 + z) ** 3 + (1.0 - Omega_m))

        def iofz(z: float) -> float:
            return quad(lambda zz: 1.0 / ez(zz), 0.0, z, epsabs=1e-10)[0]

        out = []
        for z, _, quantity in rows:
            d_m = iofz(z)
            d_h = 1.0 / ez(z)
            d_v = (z * d_m * d_m * d_h) ** (1.0 / 3.0)
            out.append({"DM_over_rs": d_m, "DH_over_rs": d_h, "DV_over_rs": d_v}[quantity])
        return np.array(out)

    def objective(x):
        Omega_m, scale = x
        if Omega_m <= 0.05 or Omega_m >= 0.60 or scale <= 0.0:
            return 1.0e99
        resid = scale * dimless(Omega_m) - obs
        return float(resid @ cinv @ resid)

    v4 = v4_values()
    x0 = np.array([v4["Omega_m"], C_KM_S / (v4["H0"] * v4["r_drag_Mpc"])])
    fit = minimize(objective, x0, method="Nelder-Mead",
                   options={"xatol": 1e-9, "fatol": 1e-9})
    Omega_m, scale = [float(x) for x in fit.x]
    chi2 = float(fit.fun)
    dof = len(rows) - 2
    return {
        "Omega_m": Omega_m,
        "distance_scale_c_over_H0_rd": scale,
        "chi2": chi2,
        "dof": dof,
        "pte": float(chi2_dist.sf(chi2, dof)),
        "implied_H0_if_rdrag_fixed_to_V4": C_KM_S / (scale * v4["r_drag_Mpc"]),
    }


def run_bao() -> dict:
    rows = parse_bao_mean(fetch_text(DESI_MEAN_URL))
    cov = np.loadtxt(io.StringIO(fetch_text(DESI_COV_URL)))
    v4 = v4_values()
    chi2, pred, _ = bao_chi2(rows, cov, v4["H0"], v4["Omega_m"], v4["r_drag_Mpc"])
    n = len(rows)
    comparisons = {}
    for name, model in {
        "V4_endpoint": (v4["H0"], v4["Omega_m"], v4["r_drag_Mpc"]),
        "Planck2018_base_like": (67.36, 0.3153, 147.09),
        "Planck2018_BAO_like": (67.66, 0.3111, 147.57),
    }.items():
        c2, _, _ = bao_chi2(rows, cov, *model)
        comparisons[name] = {
            "H0": model[0],
            "Omega_m": model[1],
            "r_drag_Mpc": model[2],
            "chi2": c2,
            "n_data": n,
            "pte": float(chi2_dist.sf(c2, n)),
        }
    return {
        "source": {"mean": DESI_MEAN_URL, "cov": DESI_COV_URL},
        "chi2": chi2,
        "n_data": n,
        "pte": float(chi2_dist.sf(chi2, n)),
        "comparisons": comparisons,
        "bao_only_best_fit": bao_best_fit(rows, cov),
        "rows": [
            {
                "z": z,
                "quantity": q,
                "observed": val,
                "predicted": float(p),
                "pull_diagonal": float((p - val) / math.sqrt(cov[i, i])),
            }
            for i, ((z, val, q), p) in enumerate(zip(rows, pred))
        ],
    }


def signed_square(v: float) -> float:
    return math.copysign(v * v, v)


def parse_sparc(text: str):
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 10:
            continue
        try:
            yield {
                "id": parts[0],
                "R_kpc": float(parts[2]),
                "Vobs": float(parts[3]),
                "e_Vobs": float(parts[4]),
                "Vgas": float(parts[5]),
                "Vdisk": float(parts[6]),
                "Vbul": float(parts[7]),
            }
        except ValueError:
            continue


def sparc_point(row: dict, a0: float, ydisk=0.5, ybul=0.7):
    if row["R_kpc"] <= 0.0 or row["Vobs"] <= 0.0 or row["e_Vobs"] <= 0.0:
        return None
    vbar2 = (
        signed_square(row["Vgas"])
        + ydisk * signed_square(row["Vdisk"])
        + ybul * signed_square(row["Vbul"])
    )
    if vbar2 <= 0.0:
        return None
    conv = 1.0e6 / 3.0856775814913673e19
    gbar = vbar2 / row["R_kpc"] * conv
    x = gbar / a0
    y2 = 0.5 * (x * x + x * math.sqrt(x * x + 4.0))
    gpred = a0 * math.sqrt(y2)
    gobs = row["Vobs"] ** 2 / row["R_kpc"] * conv
    return {
        "id": row["id"],
        "Vobs": row["Vobs"],
        "frac_v_err": row["e_Vobs"] / row["Vobs"],
        "resid_log10g": math.log10(gobs) - math.log10(gpred),
    }


def sparc_stats(points):
    resid = np.array([p["resid_log10g"] for p in points])
    return {
        "n_points": len(points),
        "n_galaxies": len({p["id"] for p in points}),
        "mean_log10g_resid_dex": float(np.mean(resid)),
        "rms_log10g_resid_dex": float(np.sqrt(np.mean(resid ** 2))),
        "scatter_about_mean_dex": float(np.std(resid)),
        "median_log10g_resid_dex": float(np.median(resid)),
    }


def run_sparc() -> dict:
    v4 = v4_values()
    points = [
        p for row in parse_sparc(fetch_text(SPARC_URL))
        if (p := sparc_point(row, v4["a0_m_s2"])) is not None
    ]
    curated = [p for p in points if p["frac_v_err"] < 0.1 and p["Vobs"] > 20.0]
    return {
        "source": SPARC_URL,
        "assumptions": {"Y_disk": 0.5, "Y_bulge": 0.7, "mu": "y/sqrt(1+y^2)"},
        "all_points": sparc_stats(points),
        "curated_points": sparc_stats(curated),
    }


def run_cluster_diagnostic() -> dict:
    v4 = v4_values()
    f_sigma = v4["Omega_Sigma"] / v4["Omega_m"]
    f_b = v4["Omega_b"] / v4["Omega_m"]
    x_residual = 720.0
    x_gas = 120.0
    x_lensing = (f_sigma * x_residual + f_b * x_gas) / (f_sigma + f_b)
    return {
        "residual_fraction": f_sigma,
        "baryon_fraction": f_b,
        "x_residual_kpc": x_residual,
        "x_gas_kpc": x_gas,
        "x_lensing_centroid_kpc": x_lensing,
        "distance_to_residual_kpc": abs(x_lensing - x_residual),
        "distance_to_gas_kpc": abs(x_lensing - x_gas),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="optional JSON output path")
    args = parser.parse_args()
    result = {
        "v4": v4_values(),
        "bao_desi_dr2": run_bao(),
        "sparc": run_sparc(),
        "cluster_residual_diagnostic": run_cluster_diagnostic(),
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
