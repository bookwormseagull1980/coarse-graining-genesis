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

"""Shared helpers for the isolated cosmology research sandbox.

The sandbox is deliberately read-only with respect to the V4 parameter
store.  It reads `cg_params.json` directly, never imports `pset`, and
never writes framework parameters.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PARAM_FILE = ROOT / "cg_params.json"

GEV_TO_S = 1.519267447e24
C_KM_S = 299792.458
MPC_KM = 3.0856775814913673e19
GEV_TO_K = 1.160451812e13
SEC_PER_GYR = 31557600.0 * 1.0e9


def load_param_records() -> dict[str, dict[str, Any]]:
    with PARAM_FILE.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["parameters"]


def value(key: str) -> Any:
    records = load_param_records()
    if key not in records:
        raise KeyError(key)
    return records[key]["value"]


def v4_background() -> dict[str, float]:
    H0_GeV = float(value("H0_GEV"))
    H0_s = H0_GeV * GEV_TO_S
    H0_km_s_Mpc = H0_s * MPC_KM
    T_CMB_GeV = float(value("T_CMB_GeV"))
    Omega_b = float(value("Omega_b"))
    Omega_dm = float(value("Omega_DM"))
    Omega_l = float(value("Omega_Lambda"))
    Omega_m = Omega_b + Omega_dm
    M_P = float(value("M_P"))
    rho_crit = 3.0 * H0_GeV * H0_GeV * M_P * M_P
    rho_gamma = (math.pi ** 2 / 15.0) * T_CMB_GeV ** 4
    Omega_gamma = rho_gamma / rho_crit
    N_eff = float(value("bbn_Neff"))
    Omega_nu_rel = Omega_gamma * (7.0 / 8.0) * (4.0 / 11.0) ** (4.0 / 3.0) * N_eff
    Omega_r = Omega_gamma + Omega_nu_rel
    return {
        "H0_GeV": H0_GeV,
        "H0_s": H0_s,
        "H0_km_s_Mpc": H0_km_s_Mpc,
        "h": H0_km_s_Mpc / 100.0,
        "Omega_b": Omega_b,
        "Omega_dm": Omega_dm,
        "Omega_Lambda": Omega_l,
        "Omega_m": Omega_m,
        "Omega_gamma": Omega_gamma,
        "Omega_nu_rel": Omega_nu_rel,
        "Omega_r": Omega_r,
        "T_CMB_GeV": T_CMB_GeV,
        "T_CMB_K": T_CMB_GeV * GEV_TO_K,
        "N_eff": N_eff,
        "a0_today_m_s2": float(value("a0_MOND")),
        "A_s": float(value("perturbation_amplitude")),
        "n_s": 1.0 - float(value("ns_tilt")),
        "gw_ratio": float(value("gw_ratio")),
    }


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def bannered_markdown(title: str, body: str) -> str:
    return f"""<!--
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
-->

# {title}

{body}
"""
