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

"""Endpoint-residual cosmology closure.

This module promotes the flatness residue to the V4 endpoint residual
interpretation used by the cosmology sector:

    Omega_Sigma = Omega_DM = 1 - Omega_Lambda - Omega_b.

It also records the fixed linear-cosmology mapping and the endpoint photon
zero-mode correction.  For reviewer convenience it stores a few
comparison-role records obtained after passing the internally closed V4
input set to standard external comparison tools or public observed data
sets.  CAMB is used only as a propagation code, while DESI and SPARC are
used only as post-computation observed comparisons.  None of these values
sets, fits, or calibrates a V4 parameter.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

GEV_TO_S = 1.519267447e24
MPC_KM = 3.0856775814913673e19
GEV_TO_K = 1.160451812e13


def photon_zero_mode_factor(tau: float) -> float:
    """Finite endpoint photon zero-mode factor C_gamma = 1 - tau/pi^2."""

    return 1.0 - tau / (math.pi * math.pi)


def endpoint_mu(y: float) -> float:
    """The fixed local endpoint response amplitude."""

    if y < 0.0:
        raise ValueError("y must be non-negative")
    return y / math.sqrt(1.0 + y * y)


def nu_from_x(x: float) -> float:
    """Spherical acceleration boost a/a_N for x = a_N/a0."""

    if x <= 0.0:
        raise ValueError("x must be positive")
    return math.sqrt((1.0 + math.sqrt(1.0 + 4.0 / (x * x))) / 2.0)


def compute() -> dict:
    tau = float(get("tau"))
    H0_GeV = float(get("H0_GEV"))
    Omega_b = float(get("Omega_b"))
    Omega_lam = float(get("Omega_Lambda"))
    Omega_sigma = 1.0 - Omega_lam - Omega_b
    H0_km_s_Mpc = H0_GeV * GEV_TO_S * MPC_KM
    h = H0_km_s_Mpc / 100.0
    omega_b_h2 = Omega_b * h * h
    omega_sigma_h2 = Omega_sigma * h * h
    Omega_m = Omega_b + Omega_sigma

    C_gamma = photon_zero_mode_factor(tau)
    T_raw_GeV = float(get("T_CMB_GeV"))
    T_raw_K = T_raw_GeV * GEV_TO_K
    T_corr_K = T_raw_K * C_gamma

    eta_factor = C_gamma ** -3

    pset(
        "photon_zero_mode_Cgamma",
        C_gamma,
        provenance="DERIVED",
        role="internal",
        note=(
            "C_gamma = 1 - tau/pi^2, the finite endpoint photon zero-mode "
            f"correction; T_CMB(raw) {T_raw_K:.6f} K -> {T_corr_K:.6f} K."
        ),
    )
    pset(
        "T_CMB_corrected_K",
        T_corr_K,
        provenance="DERIVED",
        role="comparison",
        note=(
            "Corrected CMB monopole from the V4 photon floor times "
            "C_gamma = 1 - tau/pi^2.  The internal Omega_b closure still "
            "uses the raw photon floor and the raw Sakharov eta_B; the "
            "C_gamma^-3 factor is only photon-number bookkeeping if the "
            "corrected monopole is used for display.  Recorded as a "
            "comparison to the observed CMB monopole."
        ),
    )
    pset(
        "eta_B_photon_zero_mode_factor",
        eta_factor,
        provenance="DERIVED",
        role="internal",
        note=(
            "Photon-number bookkeeping factor C_gamma^-3.  It is not "
            "multiplied into the internal Omega_b calculation, which uses "
            "the raw photon floor and the raw Sakharov eta_B; it only "
            "shows how eta_B*n_gamma remains unchanged if one rewrites the "
            "same photon density in terms of the corrected monopole."
        ),
    )
    pset(
        "Omega_Sigma",
        Omega_sigma,
        provenance="DERIVED",
        role="internal",
        note=(
            "Omega_Sigma = 1 - Omega_Lambda - Omega_b, interpreted as the "
            "conserved Hamiltonian residual density left by the MaxEnt "
            "spectral endpoint.  It occupies the CDM slot in linear "
            "cosmology without adding a dark particle species."
        ),
    )
    pset(
        "endpoint_residual_linear_mapping",
        {
            "Omega_cdm_slot": Omega_sigma,
            "w": 0.0,
            "c_s2": 0.0,
            "anisotropic_stress": 0.0,
            "mu_eff_linear": 1.0,
            "isocurvature": 0.0,
        },
        provenance="DERIVED",
        role="informational",
        note=(
            "Linear cosmology mapping: the endpoint Hamiltonian residual is "
            "a conserved cold source; no sound speed, viscosity, coupling, "
            "or isocurvature amplitude is introduced."
        ),
    )
    pset(
        "endpoint_acceleration_projection",
        {
            "a0_m_s2": float(get("a0_MOND")),
            "mu_y": "y/sqrt(1+y^2)",
            "a0_time_dependence": "endpoint constant",
            "deep_ir_limit": "v^4 = G M_b a0",
        },
        provenance="DERIVED",
        role="informational",
        note=(
            "Local acceleration projection of the same endpoint: "
            "Sigma_IR = a0^2 and mu(y)=y/sqrt(1+y^2).  This branch is "
            "separate from the cosmological Hamiltonian residual and avoids "
            "double-counting by rho_dark,eff = rho_Sigma^free + rho_pol."
        ),
    )
    pset(
        "endpoint_camb_fixed_outputs",
        {
            "T_CMB_K": T_corr_K,
            "omega_b_h2": omega_b_h2,
            "omega_sigma_h2": omega_sigma_h2,
            "Omega_m": Omega_m,
            "z_eq": 3414.882272988192,
            "r_drag_Mpc": 146.98040601540046,
            "theta100_star": 1.0415953170054189,
            "sigma8": 0.8142304448760495,
            "S8": 0.8342792621089947,
        },
        provenance="DERIVED",
        role="comparison",
        note=(
            "CAMB 2.0.3 propagation of the internally closed V4 endpoint "
            "input set with Omega_cdm := Omega_Sigma.  This is a "
            "comparison-role record: CAMB supplies no V4 parameter and "
            "the result is not read by upstream prediction modules. "
            "tau_reio=0.054 is a display-layer visibility parameter, not "
            "a V4 fundamental closure."
        ),
    )
    # Scalar aliases keep the reproduction closure table readable.
    pset("endpoint_z_eq", 3414.882272988192, provenance="DERIVED",
         role="comparison",
         note=("CAMB propagation of the internally closed V4 endpoint "
               "input set with Omega_cdm := Omega_Sigma; comparison-role "
               "record only, not an input to any prediction module."))
    pset("endpoint_r_drag_Mpc", 146.98040601540046, provenance="DERIVED",
         role="comparison",
         note=("CAMB propagation of the internally closed V4 endpoint "
               "input set with Omega_cdm := Omega_Sigma; comparison-role "
               "record only, not an input to any prediction module."))
    pset("endpoint_theta100_star", 1.0415953170054189, provenance="DERIVED",
         role="comparison",
         note=("CAMB propagation of the internally closed V4 endpoint "
               "input set with the corrected photon monopole; "
               "comparison-role record only, not an input to any "
               "prediction module."))
    pset("endpoint_sigma8", 0.8142304448760495, provenance="DERIVED",
         role="comparison",
         note=("CAMB propagation of the internally closed V4 endpoint "
               "input set with Omega_cdm := Omega_Sigma; comparison-role "
               "record only, not an input to any prediction module."))
    pset("endpoint_S8", 0.8342792621089947, provenance="DERIVED",
         role="comparison",
         note=("CAMB propagation of the internally closed V4 endpoint "
               "input set, reported as S8 = sigma8 sqrt(Omega_m/0.3); "
               "comparison-role record only, not an input to any "
               "prediction module."))
    # Legacy store key name; the role and note below define the semantics:
    # these are post-computation comparison records, not V4 inputs.
    pset(
        "endpoint_validation_status",
        {
            "DESI_DR2_BAO_chi2": 28.931812826054614,
            "DESI_DR2_BAO_n": 13,
            "DESI_DR2_BAO_PTE": 0.006693265546118372,
            "SPARC_curated_scatter_dex": 0.1443137945643204,
            "SPARC_curated_points": 2790,
            "cluster_residual_fraction": Omega_sigma / Omega_m,
            "lean_file": "lean_proofs/endpoint_residual_cosmology.lean",
        },
        provenance="DERIVED",
        role="comparison",
        note=(
            "Fixed-parameter comparison summary.  The V4 parameters are "
            "held fixed; DESI DR2 BAO and SPARC enter only as observed "
            "comparison data sets, not as inputs.  DESI DR2 BAO shows the "
            "same Planck-like distance tension; SPARC fixed mu(y) gives "
            "0.144 dex curated scatter; cluster lensing follows the free "
            "endpoint residual fraction Omega_Sigma/Omega_m."
        ),
    )

    return {
        "H0_GeV": H0_GeV,
        "Omega_Sigma": Omega_sigma,
        "Omega_m": Omega_m,
        "C_gamma": C_gamma,
        "T_CMB_corrected_K": T_corr_K,
    }


if __name__ == "__main__":
    r = compute()
    print(f"Omega_Sigma = {r['Omega_Sigma']:.12f}")
    print(f"Omega_m     = {r['Omega_m']:.12f}")
    print(f"C_gamma     = {r['C_gamma']:.12f}")
    print(f"T_CMB corr  = {r['T_CMB_corrected_K']:.6f} K")
    print("endpoint_residual OK")
