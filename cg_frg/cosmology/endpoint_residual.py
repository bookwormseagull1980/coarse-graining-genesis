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

"""Endpoint-residual cosmology closure.

This module records the flatness residual and its V5 cosmology prescription:

    Omega_Sigma = Omega_DM = 1 - Omega_Lambda - Omega_b.

It also records the fixed linear-cosmology mapping and the endpoint photon
zero-mode correction.  The cold-source form is conditional on vanishing
spatial and mixed projections of the residual stress tensor; conservation
also uses constant vacuum density, visible-matter conservation and the
Bianchi identity.  The projection conditions are retained for perturbations,
and adiabatic initial data and unit linear response are separate choices.

The local response uses a Gaussian variance ratio (equivalently, the
normalized susceptibility of the specified linear source), with its square
root assigned as the RMS-to-flux amplitude.  In this local subsystem,
rho_Sigma^free is interface data inherited from the closed cosmological
state and rho_pol is determined by the solution Phi.  It is not an
outside-universe source.  This module implements no evolution or averaging
map from the homogeneous rho_Sigma to either local density or their sum, so
that transfer remains an explicit subsystem boundary rather than a claimed
local derivation.

Records with role="comparison" are downstream
propagations of the closed parameter set through CAMB or evaluations
against the DESI and SPARC data sets.  The internal and comparison roles
therefore remain explicit in the common DERIVED provenance class.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import (get, set as pset, record_alias, published_sm_value,
                            sm_set)  # noqa: E402

GEV_TO_S = 1.519267447e24
MPC_KM = 3.0856775814913673e19
GEV_TO_K = 1.160451812e13
SPARC_DATA_KEY = "SPARC_MASS_MODELS"
SPARC_URL = "https://zenodo.org/records/16284118/files/MassModels_Lelli2016c.mrt?download=1"


def parse_sparc(text):
    """Read the published mass-model table in kpc and km/s."""
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 10:
            continue
        try:
            yield {"id": parts[0], "R_kpc": float(parts[2]),
                   "Vobs": float(parts[3]), "e_Vobs": float(parts[4]),
                   "Vgas": float(parts[5]), "Vdisk": float(parts[6]),
                   "Vbul": float(parts[7])}
        except ValueError:
            continue


def sparc_point(row, a0, ydisk=0.5, ybul=0.7):
    """Evaluate one observed point at fixed stellar mass-to-light ratios."""
    if row["R_kpc"] <= 0 or row["Vobs"] <= 0 or row["e_Vobs"] <= 0:
        return None
    signed_square = lambda value: math.copysign(value*value, value)
    vbar2 = (signed_square(row["Vgas"])+ydisk*signed_square(row["Vdisk"])
             + ybul*signed_square(row["Vbul"]))
    if vbar2 <= 0:
        return None
    conversion = 1.e6/MPC_KM
    gbar = vbar2/row["R_kpc"]*conversion
    x = gbar/a0
    gpred = a0*math.sqrt(.5*(x*x+x*math.sqrt(x*x+4.)))
    gobs = row["Vobs"]**2/row["R_kpc"]*conversion
    return {"id": row["id"], "Vobs": row["Vobs"],
            "frac_v_err": row["e_Vobs"]/row["Vobs"],
            "resid_log10g": math.log10(gobs)-math.log10(gpred)}


def sparc_stats(points):
    import numpy as np
    if not points:
        raise ValueError("SPARC selection contains no points")
    residuals = np.array([point["resid_log10g"] for point in points])
    return {"n_points": len(points), "n_galaxies": len({p["id"] for p in points}),
            "mean_log10g_resid_dex": float(np.mean(residuals)),
            "rms_log10g_resid_dex": float(np.sqrt(np.mean(residuals**2))),
            "scatter_about_mean_dex": float(np.std(residuals)),
            "median_log10g_resid_dex": float(np.median(residuals))}


def current_sparc_record(a0, *, data=None, source_root=None):
    """Recompute the finite comparison from registered, versioned observations."""
    from cg_frg.cosmology.camb_interface import fingerprint
    try:
        if data is None:
            data = published_sm_value(SPARC_DATA_KEY, source_root=source_root)
        if data["source"] != SPARC_URL or len(data["source_sha256"]) != 64:
            raise ValueError("SPARC source identity is incomplete")
        if not math.isfinite(a0) or a0 <= 0:
            raise ValueError("positive finite acceleration scale required")
        configuration = {
            "a0_m_s2": a0, "Y_disk": .5, "Y_bulge": .7,
            "mu": "y/sqrt(1+y^2)",
            "valid_selection": "R_kpc>0,Vobs>0,e_Vobs>0,vbar_squared>0",
            "curated_selection": "e_Vobs/Vobs<0.1,Vobs>20 km/s",
            "gas_convention": "signed squared velocities",
            "scatter_definition": "population standard deviation of log10(gobs/gpred)",
            "km_per_Mpc": MPC_KM,
        }
        points = [p for row in data["rows"]
                  if (p := sparc_point(row, a0, configuration["Y_disk"],
                                      configuration["Y_bulge"])) is not None]
        curated = [p for p in points if p["frac_v_err"] < .1 and p["Vobs"] > 20.]
        return {"status": "current_inputs_match", "fresh_run": True,
                "dataset_key": SPARC_DATA_KEY, "dataset_sha256": fingerprint(data),
                "configuration": configuration,
                "configuration_sha256": fingerprint(configuration),
                "all_points": sparc_stats(points), "curated_points": sparc_stats(curated)}
    except (OSError, KeyError, ValueError, TypeError, OverflowError) as exc:
        return {"status": "PENDING", "fresh_run": False, "reason": str(exc)}


def photon_zero_mode_factor(tau: float) -> float:
    """Finite endpoint photon zero-mode factor C_gamma = 1 - tau/pi^2."""

    return 1.0 - tau / (math.pi * math.pi)


def endpoint_mu(y: float) -> float:
    """Specified RMS amplitude sqrt(Z_IR), with Z_IR = y^2/(1+y^2).

    Z_IR is a Gaussian variance ratio and normalized same-source
    susceptibility, not an external-momentum pole residue.
    """

    if y < 0.0:
        raise ValueError("y must be non-negative")
    return y / math.sqrt(1.0 + y * y)


def nu_from_x(x: float) -> float:
    """Isolated spherical boost for x = a_N/a0 and rho_Sigma^free = 0."""

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
    Omega_nonvacuum_budget = Omega_b + Omega_sigma

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
            "Corrected CMB monopole from the photon floor times "
            "C_gamma = 1 - tau/pi^2.  The Omega_b closure uses the raw "
            "photon floor and raw Sakharov eta_B; this record supplies the "
            "monopole comparison value."
        ),
    )
    pset(
        "eta_B_photon_zero_mode_factor",
        eta_factor,
        provenance="DERIVED",
        role="internal",
        note=(
            "Photon-number bookkeeping factor C_gamma^-3.  Rewriting the "
            "raw photon density in terms of the corrected monopole preserves "
            "the product eta_B*n_gamma used by the Omega_b closure."
        ),
    )
    pset(
        "Omega_Sigma",
        Omega_sigma,
        provenance="DERIVED",
        role="internal",
        note=(
            "Omega_Sigma = 1 - Omega_Lambda - Omega_b is the endpoint "
            "nonbaryonic residual budget. The common-action propagation "
            "resolves it into photons, neutrinos and Omega_Sigma_cold."
        ),
    )
    eta_propagation = float(get("eta_b"))*eta_factor
    pset("eta_B_propagation", eta_propagation, provenance="DERIVED", role="internal",
         note="eta_B for the corrected photon temperature: eta_raw*C_gamma^-3. "
              "The conserved baryon density eta_B*n_gamma is invariant under this conversion.")
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
            "Sigma_IR = a0^2 and the specified RMS readout "
            "mu(y)=sqrt(Z_IR)=y/sqrt(1+y^2), where Z_IR is the variance "
            "ratio or normalized susceptibility.  In the local identity "
            "rho_dark,eff = rho_Sigma^free + rho_pol, rho_Sigma^free is "
            "closed-state interface data and rho_pol follows from the solution Phi. "
            "No evolution or averaging relation to homogeneous rho_Sigma "
            "is implemented here."
        ),
    )
    from cg_frg.cosmology.camb_interface import (
        INPUT_KEYS, BAO_DATA_KEY, current_camb_record, current_bao_record)
    for dataset_key in (BAO_DATA_KEY, SPARC_DATA_KEY):
        try:
            data = published_sm_value(dataset_key)
        except (OSError, KeyError):
            continue
        sm_set(dataset_key, data, note="Published observational dataset for fixed-parameter comparison.")
    cache = current_camb_record({key: float(get(key)) for key in INPUT_KEYS})
    pset("endpoint_camb_record", cache, provenance="DERIVED",
         role="comparison", dependencies=INPUT_KEYS,
         note="Current completed CAMB comparison, bound to endpoint "
         "inputs and the complete solver payload, with the actual execution's source identities.")
    bao = current_bao_record(get("endpoint_camb_record"))
    record_alias("endpoint_camb_status", "endpoint_camb_record", path=("status",),
                 role="informational", note="Availability of the completed propagation.")
    valid = cache["status"] == "current_inputs_match"

    def comparison_alias(key, source, path, available, note):
        if available:
            record_alias(key, source, path=path, role="comparison", note=note)
        else:
            pset(key, None, provenance="PENDING", role="informational", note=note)

    comparison_alias("Omega_Sigma_cold", "endpoint_camb_record",
                     ("density_dictionary", "components", "cdm"), valid,
                     "Cold-source density from the common-action Friedmann constraint.")
    pset("endpoint_residual_linear_mapping",
         {"Omega_endpoint_residual_key": "Omega_Sigma", "Omega_cdm_slot_key": "Omega_Sigma_cold",
          "w": 0., "c_s2": 0., "anisotropic_stress": 0.,
          "mu_eff_linear": 1., "isocurvature": 0.},
         provenance="DERIVED" if valid else "PENDING", role="informational",
         note="Common-action density constraint followed by dust propagation: "
              "vanishing spatial/mixed projections give zero pressure and anisotropic stress. "
              "Unit linear response and adiabatic initial data specify the perturbation comparison.")
    for suffix in ("nt", "ntrun"):
        comparison_alias("endpoint_tensor_"+suffix, "endpoint_camb_record",
                         ("configuration", "primordial", suffix), valid,
                         "Tensor-spectrum parameter at k=0.05 Mpc^-1 under second-order inflation consistency.")
    for suffix in ("z_eq", "r_drag_Mpc", "theta100_star", "sigma8", "S8"):
        output_key = "S8_total_matter" if suffix == "S8" else suffix
        available = valid and output_key in cache.get("outputs", {})
        comparison_alias("endpoint_"+suffix, "endpoint_camb_record", ("outputs", output_key), available,
                         "CAMB comparison projection; S8 includes all massive-neutrino matter.")
    pset("endpoint_bao_record", bao, provenance="DERIVED", role="comparison",
         dependencies=("endpoint_camb_record",),
         note="Current zero-fit DESI comparison, bound to the CAMB result; covariance and "
         "distance equations are evaluated against the separately registered observations.")
    bao_valid = bao["status"] == "current_inputs_match"
    for suffix, field in (("chi2", "chi2"), ("n", "n_data"), ("PTE", "pte")):
        comparison_alias("endpoint_bao_"+suffix, "endpoint_bao_record", (field,), bao_valid,
                         "Fixed-parameter DESI DR2 comparison projection.")
    sparc = current_sparc_record(float(get("a0_MOND")))
    pset("endpoint_sparc_record", sparc, role="comparison",
         dependencies=("a0_MOND",),
         note="Fixed-mass-to-light SPARC comparison with registered dataset and full selection conventions.")
    sparc_valid = sparc["status"] == "current_inputs_match"
    for suffix, field in (("scatter_dex", "scatter_about_mean_dex"), ("points", "n_points")):
        comparison_alias("endpoint_sparc_curated_"+suffix, "endpoint_sparc_record",
                         ("curated_points", field), sparc_valid,
                         "Curated SPARC sample comparison projection.")
    pset(
        "endpoint_validation_status",
        {
            "current_camb_status": cache["status"],
            "current_bao_status": bao["status"],
            "SPARC_status": sparc["status"],
            "comparison_records": ["endpoint_camb_record", "endpoint_bao_record", "endpoint_sparc_record"],
            "endpoint_nonbaryonic_budget_ratio": Omega_sigma / Omega_nonvacuum_budget,
            "lean_file": "lean_proofs/endpoint_residual_cosmology.lean",
        },
        provenance="DERIVED",
        role="comparison",
        note=(
            "Fixed-parameter comparison summary against DESI DR2 BAO and "
            "SPARC. CAMB retains its completed propagation; BAO and SPARC comparisons "
            "are evaluated from registered observations with fixed model parameters. "
            "The nonbaryonic-to-nonvacuum budget ratio describes the homogeneous "
            "endpoint decomposition."
        ),
    )

    return {
        "H0_GeV": H0_GeV,
        "Omega_Sigma": Omega_sigma,
        "Omega_nonvacuum_budget": Omega_nonvacuum_budget,
        "C_gamma": C_gamma,
        "T_CMB_corrected_K": T_corr_K,
    }


if __name__ == "__main__":
    r = compute()
    print(f"Omega_Sigma = {r['Omega_Sigma']:.12f}")
    print(f"Omega_nonvacuum_budget = {r['Omega_nonvacuum_budget']:.12f}")
    print(f"C_gamma     = {r['C_gamma']:.12f}")
    print(f"T_CMB corr  = {r['T_CMB_corrected_K']:.6f} K")
    print("endpoint_residual OK")
