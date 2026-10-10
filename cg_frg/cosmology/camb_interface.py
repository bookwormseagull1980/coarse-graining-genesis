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

"""Explicit CAMB propagation and input-bound current comparison records.

A completed run records its propagation assumptions, density dictionary and
full-background distances. Endpoint fractions and propagated species have
separate, explicit definitions.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from collections.abc import Mapping
from pathlib import Path

INPUT_KEYS = ("H0_GEV", "Omega_b", "Omega_Lambda", "T_CMB_GeV", "tau",
              "perturbation_amplitude", "ns_tilt", "bbn_Yp", "bbn_Neff",
              "m_nu1", "m_nu2", "m_nu3")
ROOT = Path(__file__).resolve().parents[2]
CAMB_RECORD_KEY = "endpoint_camb_record"
BAO_DATA_KEY = "DESI_DR2_BAO"
DISTANCE_REDSHIFTS = (.295, .51, .706, .934, 1.321, 1.484, 2.33)
DISTANCE_PRESCRIPTION = "flat CAMB background with radiation and three massive neutrino eigenstates"
BOLTZMANN_EV_K = 1.380649e-23/1.602176634e-19


def validate_neutrino_resolution(cfg, resolution, omega):
    """Check actual static masses, thermal fractions and an independent FD integral."""
    from scipy.integrate import quad
    masses = cfg["neutrino_masses_eV"]
    densities = resolution["omega_h2_per_state"]
    fractions = resolution["energy_density_fractions"]
    temperatures = resolution["temperature_K"]
    ratios = resolution["mass_over_temperature"]
    recovered = resolution["reconstructed_masses_eV"]
    if any(len(values) != 3 for values in (masses, densities, fractions, temperatures, ratios, recovered)):
        raise ValueError("three resolved neutrino states required")
    if any(not math.isfinite(x) or x <= 0 for values in
           (masses, densities, fractions, temperatures, ratios, recovered) for x in values):
        raise ValueError("positive finite neutrino data required")
    total = math.fsum(densities)
    temperature = cfg["cosmology"]["TCMB"]*(4/11)**(1/3)*(cfg["cosmology"]["nnu"]/3)**.25
    h2 = (cfg["cosmology"]["H0"]/100)**2
    for i, mass in enumerate(masses):
        if not math.isclose(fractions[i], densities[i]/total, rel_tol=1e-13):
            raise ValueError("neutrino thermal density fraction mismatch")
        if not math.isclose(temperatures[i], temperature, rel_tol=1e-13):
            raise ValueError("neutrino temperature convention mismatch")
        if not math.isclose(recovered[i], ratios[i]*BOLTZMANN_EV_K*temperature, rel_tol=1e-13) or \
                not math.isclose(recovered[i], mass, rel_tol=1e-7):
            raise ValueError("resolved neutrino static mass mismatch")
        y = mass/(BOLTZMANN_EV_K*temperature)
        integral = quad(lambda q: q*q*math.sqrt(q*q+y*y)*math.exp(-q)/(1+math.exp(-q)),
                        0., math.inf, epsabs=1e-8, epsrel=2e-11)[0]
        thermal = omega["photon"]*15/math.pi**4*(temperature/cfg["cosmology"]["TCMB"])**4*integral
        if not math.isclose(densities[i]/h2, thermal, rel_tol=2e-6):
            raise ValueError("neutrino density disagrees with independent Fermi-Dirac energy integral")
    if not math.isclose(total/h2, omega["nu"], rel_tol=2e-7):
        raise ValueError("neutrino thermal density does not match the full background")


def constrained_cold_fraction(omega_lambda, omega_b, visible_components):
    """Solve the common-action Friedmann constraint at the reference epoch.

    The three-component endpoint residual is resolved into a cold source,
    photons and neutrinos while preserving H0, the vacuum coefficient and
    baryon density. All fractions use the same critical density.
    """
    species = ("photon", "neutrino", "nu")
    values = [float(omega_lambda), float(omega_b)] + [float(visible_components[k]) for k in species]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("finite nonnegative density fractions required")
    cold = 1-math.fsum(values)
    if cold <= 0:
        raise ValueError("the common-action density budget has no positive cold branch")
    return cold


def validate_background(record, redshifts):
    """Check distance units and the independent integration of the same H(z)."""
    if record["prescription"] != DISTANCE_PRESCRIPTION:
        raise ValueError("unrecognized background distance prescription")
    rows = record["rows"]
    if [row["z"] for row in rows] != list(redshifts):
        raise ValueError("background redshift requests do not match")
    for row in rows:
        for key in ("H_km_s_Mpc", "D_M_Mpc", "D_H_Mpc", "D_M_quad_Mpc"):
            if not math.isfinite(row[key]) or row[key] <= 0:
                raise ValueError("invalid background distance: " + key)
        error = row["D_M_quad_error_estimate_Mpc"]
        if not math.isfinite(error) or error < 0:
            raise ValueError("invalid distance quadrature error estimate")
        if not math.isclose(row["D_H_Mpc"] * row["H_km_s_Mpc"], 299792.458, rel_tol=1e-13):
            raise ValueError("Hubble distance unit mismatch")
        if abs(row["D_M_Mpc"]-row["D_M_quad_Mpc"]) > max(10*error, 2e-7*row["D_M_Mpc"]):
            raise ValueError("CAMB distance and independent H(z) integration disagree")
    return rows


def fingerprint(value):
    """Exact canonical-JSON fingerprint, rejecting NaN/Infinity."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    allow_nan=False).encode()).hexdigest()


def execution_fingerprint(record):
    """Bind the completed solver payload independently of publication metadata."""
    keys = ("identity", "execution_completed", "configuration", "configuration_sha256",
            "camb_version", "resolved_parameters", "neutrino_resolution",
            "resolved_cold_density", "density_dictionary", "outputs", "source_sha256")
    payload = {key: record[key] for key in keys}
    for key in ("calculation_mode", "atomic_physics", "work"):
        if key in record:
            payload[key] = record[key]
    return fingerprint(payload)


def current_camb_record(inputs, record=None, *, source_root=None):
    """Load only a complete saved comparison matching current endpoint inputs.

    No CAMB execution occurs here. Source hashes identify the actual execution;
    changing this reader does not rewrite those hashes. The unified published
    store supplies the completed payload, independently of a new run's output
    store. An in-memory mapping may also be supplied for checking.
    """
    try:
        if record is None:
            from cg_core.params import published_record
            record = published_record(CAMB_RECORD_KEY, source_root=source_root)
        if not isinstance(record, Mapping):
            raise TypeError("CAMB records must be in-memory mappings from the unified parameter store")
        cfg = record["configuration"]
        current = {k: float(inputs[k]) for k in INPUT_KEYS}
        if fingerprint(cfg["endpoint_inputs"]) != fingerprint(current):
            raise ValueError("endpoint inputs do not match the completed comparison")
        if record["configuration_sha256"] != fingerprint(cfg):
            raise ValueError("CAMB configuration fingerprint mismatch")
        expected = new_configuration(current, YHe=current["bbn_Yp"],
                                     N_eff=current["bbn_Neff"],
                                     tau_reio=cfg["cosmology"]["tau"],
                                     accuracy=cfg["accuracy"]["AccuracyBoost"],
                                     mode=cfg.get("calculation_mode","full"))
        if "calculation_mode" not in cfg:
            expected.pop("calculation_mode")
        if fingerprint(cfg) != fingerprint(expected):
            raise ValueError("CAMB configuration differs from the declared propagation mapping")
        if not record.get("execution_completed", record.get("fresh_run", False)):
            raise ValueError("CAMB execution is not marked complete")
        if not record.get("camb_version") or not record.get("source_sha256"):
            raise ValueError("missing CAMB execution identity")
        resolved = record["resolved_parameters"]
        expected_resolved = {k: cfg["cosmology"][k] for k in
                             ("H0", "ombh2", "omk", "TCMB", "YHe", "Alens")}
        expected_resolved["omch2"] = record["resolved_cold_density"]["omch2"]
        expected_resolved["omnuh2"] = math.fsum(record["neutrino_resolution"]["omega_h2_per_state"])
        expected_resolved.update(cfg["primordial"])
        expected_resolved.update(cfg["accuracy"])
        expected_resolved["optical_depth"] = cfg["cosmology"]["tau"]
        for key, value in expected_resolved.items():
            found = re.search(r"(?m)^\s*" + re.escape(key) + r" = ([^\n]+)$", resolved)
            if not found or not math.isclose(float(found[1]), value, rel_tol=1e-13, abs_tol=0):
                raise ValueError("resolved CAMB parameter mismatch: " + key)
        for key, value in {"nu_mass_eigenstates": 3, "num_nu_massive": 3,
                           "nu_mass_numbers": [1, 1, 1],
                           "nu_mass_fractions": record["neutrino_resolution"]["energy_density_fractions"],
                           "nu_mass_degeneracies": [current["bbn_Neff"]/3]*3}.items():
            found = re.search(r"(?m)^\s*" + key + r" = ([^\n]+)$", resolved)
            if not found or json.loads(found[1]) != value:
                raise ValueError("resolved CAMB neutrino mismatch: " + key)
        budget = record["density_dictionary"]
        omega = budget["components"]
        if set(omega) != {"K", "cdm", "baryon", "photon", "neutrino", "nu", "de"}:
            raise ValueError("incomplete CAMB density dictionary")
        if any(not math.isfinite(v) for v in omega.values()) or abs(math.fsum(omega.values())-1) > 1e-7:
            raise ValueError("CAMB density dictionary does not close")
        validate_neutrino_resolution(cfg, record["neutrino_resolution"], omega)
        cold = constrained_cold_fraction(current["Omega_Lambda"], current["Omega_b"], omega)
        for key, value in {"baryon": current["Omega_b"], "de": current["Omega_Lambda"],
                           "cdm": cold}.items():
            if not math.isclose(omega[key], value, rel_tol=1e-10, abs_tol=0):
                raise ValueError("CAMB matter slot mismatch: " + key)
        if not math.isclose(record["resolved_cold_density"]["omch2"],
                            cold*(cfg["cosmology"]["H0"]/100)**2, rel_tol=1e-10):
            raise ValueError("resolved cold density violates the common-action constraint")
        om = omega["baryon"]+omega["cdm"]+omega["nu"]
        if not math.isclose(om, budget["Omega_m_with_massive_neutrinos"], rel_tol=1e-13):
            raise ValueError("CAMB total-matter density mismatch")
        outputs = record["outputs"]
        mode = cfg.get("calculation_mode","full")
        if record.get("calculation_mode",mode) != mode:
            raise ValueError("CAMB execution mode differs from its configuration")
        required_outputs = ("z_eq", "r_drag_Mpc", "theta100_star")
        if mode == "full":
            required_outputs += ("sigma8", "S8_total_matter")
        elif any(key in outputs for key in ("sigma8", "S8_total_matter")):
            raise ValueError("background execution cannot contain power-spectrum outputs")
        if mode == "background":
            for flag in ("WantCls","WantTransfer","WantTensors"):
                found = re.search(r"(?m)^\s*"+flag+r" = ([^\n]+)$",resolved)
                if not found or found[1].strip() != "False":
                    raise ValueError("background execution has perturbation flag enabled: "+flag)
        if any(not math.isfinite(outputs[k]) or outputs[k] <= 0 for k in
               required_outputs):
            raise ValueError("invalid CAMB comparison output")
        if mode == "full" and not math.isclose(outputs["S8_total_matter"], outputs["sigma8"]*math.sqrt(om/.3), rel_tol=1e-13):
            raise ValueError("S8 density convention mismatch")
        validate_background(outputs["background_distances"], cfg["distance_redshifts"])
        execution_sha256 = execution_fingerprint(record)
        if "execution_sha256" in record and record["execution_sha256"] != execution_sha256:
            raise ValueError("completed CAMB payload fingerprint mismatch")
        response = record.get("background_response")
        if response is not None:
            if response.get("center_execution_sha256") != execution_sha256 or \
                    response.get("response_sha256") != fingerprint({
                        key:value for key,value in response.items() if key != "response_sha256"}):
                raise ValueError("background response does not match its completed centre")
        thermal = record.get("thermal_history_budget")
        if thermal is not None:
            if thermal.get("center_execution_sha256") != execution_sha256 or \
                    thermal.get("budget_sha256") != fingerprint({
                        key:value for key,value in thermal.items() if key != "budget_sha256"}):
                raise ValueError("thermal-history budget does not match its completed centre")
        return {**record, "status": "current_inputs_match", "fresh_run": False,
                "execution_sha256": execution_sha256,
                "input_sha256": fingerprint(current)}
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        return {"status": "PENDING", "fresh_run": False, "outputs": None, "reason": str(exc)}


def bao_inputs(camb_record):
    """Read the completed propagation's inputs for the downstream comparison."""
    return {"H0_km_s_Mpc": camb_record["configuration"]["cosmology"]["H0"],
            "Omega_m_total_including_massive_neutrinos":
                camb_record["density_dictionary"]["Omega_m_with_massive_neutrinos"],
            "r_drag_Mpc": camb_record["outputs"]["r_drag_Mpc"]}


def current_bao_record(camb_record, record=None, *, data=None, source_root=None):
    """Evaluate the zero-fit comparison against the separate observation store.

    The 13-dimensional likelihood is inexpensive and is evaluated from the
    retained solver distances. A supplied result is additionally checked
    against the current data and propagation identities.
    """
    try:
        if record is not None and not isinstance(record, Mapping):
            raise TypeError("BAO records must be in-memory mappings from the unified parameter store")
        if camb_record["status"] != "current_inputs_match":
            raise ValueError("current CAMB comparison is unavailable")
        if data is None:
            from cg_core.params import published_sm_value
            data = published_sm_value(BAO_DATA_KEY, source_root=source_root)
        if not data.get("sources"):
            raise ValueError("BAO dataset source identity is absent")
        background = camb_record["outputs"]["background_distances"]
        computed = evaluate_bao(bao_inputs(camb_record), data["rows"], data["covariance"], background)
        computed.pop("covariance")
        computed["rows"] = [{"observation_index": i, **{key: row[key] for key in
                            ("predicted", "residual", "diagonal_pull")}}
                            for i, row in enumerate(computed["rows"])]
        result = {"identity": "fixed-parameter-DESI-DR2", "status": "current_inputs_match",
                  "fresh_run": True, "dataset_key": BAO_DATA_KEY,
                  "dataset_sha256": fingerprint(data),
                  "camb_execution_sha256": camb_record["execution_sha256"],
                  "camb_configuration_sha256": camb_record["configuration_sha256"],
                  "background_distances_sha256": fingerprint(background),
                  "distance_prescription": DISTANCE_PRESCRIPTION, **computed}
        if "background_response" in camb_record:
            result["background_response_sha256"] = camb_record["background_response"]["response_sha256"]
        if record is not None:
            for key in ("dataset_sha256", "camb_execution_sha256", "camb_configuration_sha256",
                        "background_distances_sha256", "distance_prescription", "rows",
                        "n_data", "degrees_of_freedom", "fitted_parameters"):
                if record[key] != result[key]:
                    raise ValueError("BAO result identity or equation mismatch: " + key)
            if record.get("background_response_sha256") != result.get("background_response_sha256"):
                raise ValueError("BAO background-response identity mismatch")
            if not math.isclose(result["chi2"], record["chi2"], rel_tol=1e-11) or \
                    not math.isclose(result["pte"], record["pte"], rel_tol=1e-10):
                raise ValueError("BAO likelihood statistic mismatch")
            saved_scale = record.get("scale_diagnostic", {})
            if not isinstance(saved_scale,dict):
                raise ValueError("BAO common-scale diagnostic must be an object")
            for key,value in result["scale_diagnostic"].items():
                recorded = saved_scale.get(key)
                same = (isinstance(recorded,(int,float)) and not isinstance(recorded,bool)
                        and math.isclose(recorded,value,rel_tol=1e-10,abs_tol=1e-9)) \
                       if isinstance(value,float) else recorded == value
                if not same:
                    raise ValueError("BAO common-scale diagnostic mismatch: "+key)
        return result
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        return {"status": "PENDING", "fresh_run": False, "reason": str(exc)}


def evaluate_bao(inputs, rows, covariance, background, *, theory_covariance=None,
                 theory_uncertainty=None):
    """Evaluate full-background distances and the fixed-model likelihood.

    Observations appear only in residuals after distances have been calculated;
    neither the observations nor the likelihood update an endpoint parameter.
    A separately justified theoretical covariance may be supplied in the same
    observable order and units. Its independence from the measurement errors
    is an explicit caller assumption. Its tail probability uses a zero-mean
    Gaussian likelihood approximation. The fixed comparison remains unchanged.
    """
    import numpy as np
    from scipy.linalg import solve_triangular
    from scipy.stats import chi2
    covariance = np.asarray(covariance, dtype=float)
    if not rows or covariance.shape != (len(rows), len(rows)) or \
            not np.all(np.isfinite(covariance)) or not np.allclose(covariance, covariance.T, rtol=0, atol=1e-14):
        raise ValueError("invalid BAO covariance")
    try:
        cholesky = np.linalg.cholesky(covariance)
    except np.linalg.LinAlgError as exc:
        raise ValueError("BAO covariance is not positive definite") from exc
    om = inputs["Omega_m_total_including_massive_neutrinos"]
    H0, rd = inputs["H0_km_s_Mpc"], inputs["r_drag_Mpc"]
    if not all(math.isfinite(v) and v > 0 for v in (om, H0, rd)) or om >= 1:
        raise ValueError("invalid BAO cosmological inputs")
    samples = validate_background(background, sorted({float(row["z"]) for row in rows}))
    distances = {row["z"]: row for row in samples}
    output_rows = []
    quadrature_errors = []
    for i, row in enumerate(rows):
        z = float(row["z"])
        observed = float(row["observed"])
        if not math.isfinite(z) or z <= 0 or not math.isfinite(observed):
            raise ValueError("invalid BAO data row")
        sample = distances[z]
        dm, dh = sample["D_M_Mpc"]/rd, sample["D_H_Mpc"]/rd
        predicted = {"DM_over_rs": dm, "DH_over_rs": dh,
                     "DV_over_rs": (z*dm*dm*dh)**(1/3)}[row["quantity"]]
        residual = predicted-observed
        output_rows.append({"z": z, "quantity": row["quantity"], "observed": observed,
                            "predicted": predicted, "residual": residual,
                            "diagonal_pull": residual/math.sqrt(covariance[i, i])})
        quadrature_errors.append(sample["D_M_quad_error_estimate_Mpc"]/rd)
    residuals = np.array([row["residual"] for row in output_rows])
    predictions = np.array([row["predicted"] for row in output_rows])
    # Two right-hand sides share the already computed covariance factor.
    transformed = solve_triangular(cholesky, np.column_stack((residuals, predictions)), lower=True)
    whitened, direction = transformed.T
    statistic = float(whitened@whitened)
    direct = float(residuals@np.linalg.solve(covariance, residuals))
    curvature = float(direction@direction)
    if curvature <= 0 or not math.isfinite(curvature):
        raise ValueError("BAO common-scale direction must have finite positive norm")
    alpha = 1-float(direction@whitened)/curvature
    orthogonal = whitened+(alpha-1)*direction
    scale_statistic = (1-alpha)**2*curvature
    shape_statistic = float(orthogonal@orthogonal)
    scale_diagnostic = {
        "model": "alpha times the fixed prediction; observational diagnostic only",
        "alpha": alpha, "alpha_standard_error": 1/math.sqrt(curvature),
        "chi2_scale": scale_statistic, "chi2_orthogonal": shape_statistic,
        "degrees_of_freedom": len(rows)-1, "fitted_parameters": 1,
        "pte_orthogonal": float(chi2.sf(shape_statistic, len(rows)-1)) if len(rows)>1 else None,
        "prediction_parameters_updated": False,
        "covariance_orthogonality_residual": float(direction@orthogonal),
        "chi2_decomposition_abs_residual": abs(statistic-scale_statistic-shape_statistic),
        "work": {"additional_covariance_factorizations": 0,
                 "additional_triangular_right_hand_sides": 1,
                 "additional_inner_products": 4},
    }
    result = {"n_data": len(rows), "degrees_of_freedom": len(rows), "fitted_parameters": 0,
            "chi2": statistic, "pte": float(chi2.sf(statistic, len(rows))), "rows": output_rows,
            "scale_diagnostic": scale_diagnostic,
            "covariance": covariance.tolist(), "validation": {
                "positive_definite_covariance": True,
                "cholesky_direct_chi2_abs_difference": abs(statistic-direct),
                "max_DM_over_rd_quad_error_estimate": max(quadrature_errors)}}
    if theory_covariance is not None:
        if not isinstance(theory_uncertainty, dict) or any(
                not isinstance(theory_uncertainty.get(key),str) or
                not theory_uncertainty[key].strip() for key in ("source","approximation_order")) or \
                theory_uncertainty.get("independent_of_observations") is not True:
            raise ValueError("theoretical covariance requires its source, approximation order and independence assumption")
        theory = np.asarray(theory_covariance,dtype=float)
        if theory.shape != covariance.shape or not np.all(np.isfinite(theory)):
            raise ValueError("theoretical covariance must have the observation covariance shape")
        tolerance = 1e-12*max(float(np.max(np.abs(theory))),np.finfo(float).tiny)
        if np.max(np.abs(theory-theory.T)) > tolerance:
            raise ValueError("theoretical covariance must be symmetric")
        theory = (theory+theory.T)/2
        if np.linalg.eigvalsh(theory)[0] < -tolerance:
            raise ValueError("theoretical covariance must be positive semidefinite")
        combined = evaluate_bao(inputs,rows,covariance+theory,background)
        result["comparison_with_supplied_theory_covariance"] = {
            "assumptions": dict(theory_uncertainty),
            "theory_covariance": theory.tolist(),
            "covariance_definition": "observation plus independently supplied theoretical covariance",
            "likelihood_approximation": "zero-mean Gaussian observational and theoretical errors with zero cross covariance",
            "chi2": combined["chi2"], "pte": combined["pte"],
            "degrees_of_freedom": combined["degrees_of_freedom"], "fitted_parameters": 0,
            "scale_diagnostic": combined["scale_diagnostic"],
        }
    elif theory_uncertainty is not None:
        raise ValueError("theory uncertainty metadata requires a supplied covariance")
    return result


def new_configuration(inputs, *, YHe, N_eff, tau_reio, accuracy=1.0, mode="full"):
    """Declare propagation of one common-action density budget."""
    if not 0 < YHe < 1 or N_eff <= 0 or tau_reio < 0 or accuracy < 1:
        raise ValueError("invalid propagation settings")
    if mode not in ("full","background"):
        raise ValueError("calculation mode must be full or background")
    H0 = inputs["H0_GEV"]*1.519267447e24*3.0856775814913673e19
    h2 = (H0/100.)**2
    sigma = 1-inputs["Omega_Lambda"]-inputs["Omega_b"]
    masses = [inputs[k] for k in ("m_nu1", "m_nu2", "m_nu3")]
    if min(masses) <= 0 or sigma <= 0:
        raise ValueError("positive masses and cold slot required")
    ns = 1-inputs["ns_tilt"]
    r = 1/(2*math.pi)**2
    return {"identity": "explicit-camb-propagation", "calculation_mode": mode,
            "endpoint_inputs": dict(inputs),
            "density_mapping": "flat_common_action_vacuum",
            "cold_density_constraint": "Omega_cold=1-Omega_Lambda-Omega_b-Omega_photon-Omega_neutrino-Omega_nu",
            "cosmology": {"H0": H0, "ombh2": inputs["Omega_b"]*h2,
                          "omk": 0., "mnu": sum(masses),
                          "nnu": N_eff, "standard_neutrino_neff": N_eff,
                          "neutrino_hierarchy": "degenerate", "num_massive_neutrinos": 3,
                          "TCMB": inputs["T_CMB_GeV"]*1.160451812e13*(1-inputs["tau"]/math.pi**2),
                          "tau": tau_reio, "YHe": YHe, "meffsterile": 0., "Alens": 1.},
            "neutrino_masses_eV": masses,
            "neutrino_distribution": "three thermal Fermi-Dirac states at the common declared neutrino temperature",
            "tensor_spectrum_prescription": "second-order inflation consistency used for propagation",
            "primordial": {"As": inputs["perturbation_amplitude"], "ns": ns,
                           "nrun": 0., "nrunrun": 0., "r": r,
                           "nt": -r/8*(2-ns-r/8), "ntrun": r/8*(r/8+ns-1),
                           "pivot_scalar": .05, "pivot_tensor": .05},
            "dark_energy": {"w": -1., "wa": 0., "cs2": 1., "dark_energy_model": "fluid"},
            "accuracy": {"AccuracyBoost": accuracy, "lAccuracyBoost": accuracy, "lSampleBoost": accuracy},
            "lmax": 2500, "lens_potential_accuracy": 1,
            "matter_power": {"redshifts": [0.], "kmax": 2., "nonlinear": False,
                             "accurate_massive_neutrino_transfers": True},
            "distance_redshifts": list(DISTANCE_REDSHIFTS),
            "initial_condition": "adiabatic", "nonlinear": "none"}


def background_distances(results, redshifts):
    """Reuse one computed background; integrate c/H independently at each z.

    The redshifts request outputs only. Observations, residuals and covariance
    never enter the background solve. Quadrature estimates are numerical
    consistency diagnostics, not outward-rounded interval certificates.
    """
    from scipy.integrate import quad
    rows = []
    for z in redshifts:
        dm = float(results.comoving_radial_distance(z))
        hz = float(results.hubble_parameter(z))
        integral, error = quad(lambda t: 299792.458/float(results.hubble_parameter(t)),
                               0., z, epsabs=1e-7, epsrel=1e-10)
        rows.append({"z": float(z), "H_km_s_Mpc": hz, "D_M_Mpc": dm,
                     "D_H_Mpc": 299792.458/hz, "D_M_quad_Mpc": integral,
                     "D_M_quad_error_estimate_Mpc": error})
    record = {"prescription": DISTANCE_PRESCRIPTION, "rows": rows,
              "validation": "independent distance integration of the computed H(z)"}
    validate_background(record, redshifts)
    return record


def density_dictionary(results, endpoint_inputs, *, preserve_vacuum=True):
    names = ("K", "cdm", "baryon", "photon", "neutrino", "nu", "de")
    omega = {k: float(results.get_Omega(k, z=0)) for k in names}
    residual = math.fsum(omega.values())-1.
    if abs(residual) > 1e-7:
        raise RuntimeError(f"CAMB density sum failed: {residual}")
    if preserve_vacuum and not math.isclose(omega["de"], endpoint_inputs["Omega_Lambda"], rel_tol=1e-10):
        raise RuntimeError("propagated vacuum coefficient differs from the common action")
    return {"components": omega, "sum_minus_one": residual,
            "Omega_m_with_massive_neutrinos": omega["baryon"]+omega["cdm"]+omega["nu"],
            "endpoint_Omega_Lambda": endpoint_inputs["Omega_Lambda"],
            "endpoint_nonbaryon_residual": 1-endpoint_inputs["Omega_Lambda"]-endpoint_inputs["Omega_b"],
            "vacuum_coefficient_preserved": preserve_vacuum,
            "cold_density_from_common_action": omega["cdm"]}


def run(configuration):
    """Execute explicit configuration, returning serialized parameters/version."""
    import camb
    from camb import model
    cfg = json.loads(json.dumps(configuration, allow_nan=False))
    mode = cfg.get("calculation_mode","full")
    if mode not in ("full","background"):
        raise ValueError("calculation mode must be full or background")
    probe = cfg["density_mapping"] == "physical_background_probe"
    if cfg["density_mapping"] not in ("flat_common_action_vacuum","physical_background_probe"):
        raise ValueError("unknown density mapping")
    if probe and mode != "background":
        raise ValueError("physical-coordinate probes require background mode")
    pars = camb.CAMBparams()
    endpoint = cfg["endpoint_inputs"]
    h2 = (cfg["cosmology"]["H0"]/100)**2
    pars.set_cosmology(**cfg["cosmology"],
                       omch2=(1-endpoint["Omega_Lambda"]-endpoint["Omega_b"])*h2)
    pars.nu_mass_eigenstates = 3
    pars.nu_mass_numbers = [1, 1, 1]
    pars.nu_mass_degeneracies = [cfg["cosmology"]["nnu"]/3]*3
    densities = []
    for mass in cfg["neutrino_masses_eV"]:
        one = camb.CAMBparams()
        single = dict(cfg["cosmology"], omch2=float(pars.omch2), mnu=mass,
                      num_massive_neutrinos=1, nnu=cfg["cosmology"]["nnu"]/3)
        one.set_cosmology(**single)
        densities.append(float(one.omnuh2))
    pars.omnuh2 = math.fsum(densities)
    pars.nu_mass_fractions = [value/pars.omnuh2 for value in densities]
    pars.num_nu_massless = 0.
    pars.share_delta_neff = False
    pars.InitPower.set_params(**cfg["primordial"])
    pars.set_dark_energy(**cfg["dark_energy"])
    pars.set_accuracy(**cfg["accuracy"])
    if mode == "full":
        pars.set_for_lmax(cfg["lmax"], lens_potential_accuracy=cfg["lens_potential_accuracy"])
        pars.set_matter_power(**cfg["matter_power"])
    pars.NonLinear = model.NonLinear_none
    pars.WantTensors = mode == "full"
    pars.WantCls = mode == "full"
    pars.WantTransfer = mode == "full"
    # Radiation and massive-neutrino densities depend on the same temperature,
    # masses and distribution settings. Initialize their background densities
    # before the perturbation calculation.
    background_solves = 0
    if probe:
        matter = float(cfg["physical_coordinates"]["omega_m"])
        pars.omch2 = matter-float(pars.ombh2)-float(pars.omnuh2)
        if not math.isfinite(pars.omch2) or pars.omch2 <= 0:
            raise ValueError("physical-coordinate probe has no positive cold density")
    else:
        seed = camb.get_background(pars, no_thermo=True)
        background_solves += 1
        visible = {k: float(seed.get_Omega(k, z=0)) for k in ("photon", "neutrino", "nu")}
        cold = constrained_cold_fraction(endpoint["Omega_Lambda"], endpoint["Omega_b"], visible)
        pars.omch2 = cold*h2
    if mode == "background":
        results = camb.get_background(pars)
        background_solves += 1
    else:
        results = camb.get_results(pars)
    derived = results.get_derived_params()
    budget = density_dictionary(results, cfg["endpoint_inputs"],preserve_vacuum=not probe)
    if probe and not math.isclose(budget["Omega_m_with_massive_neutrinos"]*h2,
                                  cfg["physical_coordinates"]["omega_m"],rel_tol=2e-9):
        raise ValueError("resolved background probe differs from its physical matter density")
    visible = {key:budget["components"][key] for key in ("photon","neutrino","nu")}
    temperatures = [float(pars.TCMB*(4/11)**(1/3)*(deg/number)**.25)
                    for deg, number in zip(pars.nu_mass_degeneracies, pars.nu_mass_numbers)]
    mass_ratios = [float(results.nu_masses[i]) for i in range(3)]
    recovered = [y*BOLTZMANN_EV_K*t for y, t in zip(mass_ratios, temperatures)]
    neutrinos = {"omega_h2_per_state": densities,
                 "energy_density_fractions": list(pars.nu_mass_fractions),
                 "temperature_K": temperatures, "mass_over_temperature": mass_ratios,
                 "reconstructed_masses_eV": recovered,
                 "max_relative_mass_residual": max(abs(a/b-1) for a, b in zip(recovered, cfg["neutrino_masses_eV"]))}
    validate_neutrino_resolution(cfg, neutrinos, budget["components"])
    omega_m = budget["Omega_m_with_massive_neutrinos"]
    distances = background_distances(results, cfg["distance_redshifts"])
    outputs = {"z_eq":derived["zeq"],"r_drag_Mpc":derived["rdrag"],
               "theta100_star":derived["thetastar"],"background_distances":distances}
    if mode == "full":
        sigma8 = float(results.get_sigma8_0())
        outputs.update(sigma8=sigma8,S8_total_matter=sigma8*math.sqrt(omega_m/.3))
    from camb import constants
    atomic = {"recombination_model": type(pars.Recomb).__name__,
              "constant_convention": "standard atomic constants compiled into CAMB and its recombination model",
              "generated_electron_mass_applied": False,
              "generated_fine_structure_applied": False,
              "electron_mass_kg": float(constants.m_e),
              "thomson_cross_section_m2": float(constants.sigma_thomson)}
    return {"identity": cfg["identity"], "execution_completed": True,
            "calculation_mode": mode, "atomic_physics": atomic,
            "configuration": cfg, "configuration_sha256": fingerprint(cfg),
            "camb_version": camb.__version__, "resolved_parameters": str(pars),
            "neutrino_resolution": neutrinos,
            "resolved_cold_density": {"omch2": float(pars.omch2),
                                      "visible_components": visible,
                                      "constraint": "omega_cold=omega_m-omega_b-omega_nu" if probe
                                                    else cfg["cold_density_constraint"]},
            "density_dictionary": budget,
            "outputs": outputs,
            "work": {"explicit_background_solver_calls":background_solves,
                     "density_initializations":int(not probe),
                     "thermal_history_solves":1,
                     "full_perturbation_solver_calls":int(mode == "full"),
                     "distance_quadratures":len(cfg["distance_redshifts"]),
                     "neutrino_parameter_conversions":3}}


BACKGROUND_COORDINATES = ("YHe","omega_b","omega_m","TCMB","N_eff")
OPTIONAL_BACKGROUND_COORDINATES = ("H0","neutrino_mass_scale")


def drag_opacity_enclosure(optical_depth, sound_horizon, *, redshift_bracket,
                           relative_bound=0., absolute_bound=0.):
    """Propagate a finite optical-depth envelope through its monotone root.

    Assume |tau-tau0| <= relative_bound*tau0+absolute_bound, tau0 is
    increasing, and the sound horizon is decreasing on the bracket.
    The two inverse-depth thresholds bound every admissible drag root.
    This theorem does not establish the supplied physical envelope or
    the numerical accuracy of the callback functions.
    """
    from scipy.optimize import brentq
    lo, hi = map(float, redshift_bracket)
    if (not all(math.isfinite(x) for x in (lo, hi, relative_bound, absolute_bound))
            or not 0 <= relative_bound < 1 or not 0 <= absolute_bound < 1
            or not 0 <= lo < hi):
        raise ValueError("positive redshift bracket and optical-depth bounds below one required")
    levels = [(1-absolute_bound)/(1+relative_bound),
              (1+absolute_bound)/(1-relative_bound)]
    if optical_depth(lo) > levels[0] or optical_depth(hi) < levels[1]:
        raise ValueError("redshift bracket does not contain the finite drag envelope")
    roots = [float(brentq(lambda z: optical_depth(z)-level, lo, hi,
                          xtol=1e-8, rtol=1e-13)) for level in levels]
    sound = [float(sound_horizon(roots[1])), float(sound_horizon(roots[0]))]
    if not 0 < sound[0] <= sound[1]:
        raise ValueError("positive decreasing sound horizon required")
    return {"relative_opacity_bound": relative_bound,
            "absolute_optical_depth_bound": absolute_bound,
            "reference_depth_levels": levels, "drag_redshift_interval": roots,
            "sound_horizon_interval_Mpc": sound,
            "envelope_identity": "(1-delta)/(1+epsilon) <= tau0(z_drag) <= (1+delta)/(1-epsilon)"}


def late_ionization_drag_capacity(*, redshift_max, cosmology, components, atomic):
    """Electron-number bound at fixed expansion, baryon density and constants.

    All hydrogen and helium may be ionized below redshift_max. The lower
    expansion bound uses pressureless baryons plus cold matter; radiation,
    neutrinos and vacuum add nonnegative density. Interval arithmetic bounds
    the analytic capacity for the supplied numerical input values.
    """
    from mpmath import iv
    inputs = (redshift_max, cosmology['H0'], cosmology['YHe'], components['baryon'],
              components['cdm'], components['photon'], *atomic.values())
    if (not all(math.isfinite(x) for x in inputs) or redshift_max < 0
            or not 0 < cosmology['YHe'] < 1
            or min(cosmology['H0'], components['baryon'], components['cdm'],
                   components['photon'], *atomic.values()) <= 0):
        raise ValueError("positive background and atomic inputs and a finite nonnegative cutoff required")
    q = iv.mpf
    h0 = q(cosmology['H0'])*1000/q(atomic['Mpc_m'])
    baryon_density = 3*h0**2/(8*iv.pi*q(atomic['G_SI']))*q(components['baryon'])
    hydrogen = baryon_density*(1-q(cosmology['YHe']))/q(atomic['hydrogen_mass_kg'])
    helium_number_ratio = q(cosmology['YHe'])/(q(atomic['helium_hydrogen_mass_ratio'])*(1-q(cosmology['YHe'])))
    loading = 3*q(components['baryon'])/(4*q(components['photon']))
    coefficient = (q(atomic['speed_of_light_m_s'])*q(atomic['thomson_cross_section_m2'])
        *hydrogen*(1+2*helium_number_ratio)/(loading*h0*
        iv.sqrt(q(components['baryon'])+q(components['cdm']))))
    capacity = coefficient*2/5*((1+q(redshift_max))**q('2.5')-1)
    interval = [math.nextafter(float(capacity.a), -math.inf),
                math.nextafter(float(capacity.b), math.inf)]
    return {"redshift_max": redshift_max, "absolute_optical_depth_bound": interval[1],
            "capacity_interval": interval,
            "assumptions": ["fixed H(z), baryon loading and atomic constants",
                "unchanged recombination history above the stated redshift",
                "0 <= n_e <= n_H + 2 n_He below the stated redshift",
                "nonnegative radiation, neutrino and vacuum densities"],
            "formula": "A=2*c*sigma_T*n_H0*(1+2*f_He)*[(1+z_max)^(5/2)-1]/[5*R0*H0*sqrt(Omega_b+Omega_cold)]",
            "bound_kind": "outward interval for the analytic electron-capacity bound at supplied inputs"}


def evaluate_thermal_history_budget(center, *, tail_redshift, relative_opacity_bound,
                                    opacity_envelope_source, hyrec_runtime=None,
                                    generated_atomic=None):
    """Finite drag responses on one fixed background, with zero spectra solves.

    The direct CosmoRec and HyRec solvers are distinct from their RECFAST
    calibration sets. The three sets evaluated here are implementations
    supplied by the installed CAMB version. The finite electron-capacity
    theorem and the separately supplied relative-opacity scenario have
    separate coverage and neither is a fitted theory covariance.
    """
    import camb
    from camb import constants
    from scipy.integrate import quad
    checked = current_camb_record(center['configuration']['endpoint_inputs'], center)
    if checked.get('status') != 'current_inputs_match':
        raise ValueError('a validated fixed background is required')
    if not isinstance(opacity_envelope_source, str) or not opacity_envelope_source.strip():
        raise ValueError('an explicit source for the relative-opacity scenario is required')
    if (hyrec_runtime is None) != (generated_atomic is None):
        raise ValueError('the direct HYREC runtime and generated atomic inputs are supplied together')
    cfg, omega = checked['configuration'], checked['density_dictionary']['components']
    work = {'thermal_background_solves': 0, 'power_spectrum_solves': 0,
            'optical_depth_quadratures': 0, 'opacity_evaluations': 0,
            'reused_distance_rows': len(checked['outputs']['background_distances']['rows'])}

    def background(approximation):
        pars = camb.CAMBparams()
        pars.set_cosmology(**cfg['cosmology'], omch2=checked['resolved_cold_density']['omch2'])
        densities = checked['neutrino_resolution']['omega_h2_per_state']
        pars.nu_mass_eigenstates = 3
        pars.nu_mass_numbers = [1, 1, 1]
        pars.nu_mass_degeneracies = [cfg['cosmology']['nnu']/3]*3
        pars.omnuh2 = math.fsum(densities)
        pars.nu_mass_fractions = [value/pars.omnuh2 for value in densities]
        pars.num_nu_massless = 0.
        pars.share_delta_neff = False
        pars.set_dark_energy(**cfg['dark_energy'])
        pars.set_accuracy(**cfg['accuracy'])
        pars.WantCls = pars.WantTransfer = pars.WantTensors = False
        # CAMB defines its drag depth with the recombination history alone.
        # Expose that same history in the returned opacity samples.
        pars.Reion.Reionization = False
        pars.Recomb.set_params(recfast_approx_model=approximation)
        result = camb.get_background(pars)
        work['thermal_background_solves'] += 1
        return result

    solved = background('cosmorec')
    derived = solved.get_derived_params()
    rd = checked['outputs']['r_drag_Mpc']
    if not math.isclose(derived['rdrag'], rd, rel_tol=2e-10):
        raise ValueError('restored thermal background differs from the saved acoustic centre')
    z0 = float(derived['zdrag'])
    if not 0 <= tail_redshift < z0:
        raise ValueError('the late-ionization interval must end below the drag epoch')
    loading = 3*omega['baryon']/(4*omega['photon'])
    error_estimates = []
    def depth_integrand(z):
        work['opacity_evaluations'] += 1
        opacity = float(solved.get_background_redshift_evolution([z], ['opacity'])['opacity'][0])
        return opacity*299792.458/float(solved.hubble_parameter(z))*(1+z)/loading
    def integrate(left, right):
        if left == right:
            return 0.
        value, error = quad(depth_integrand, left, right, epsabs=1e-10, epsrel=1e-9, limit=160)
        work['optical_depth_quadratures'] += 1
        error_estimates.append(error)
        return float(value)
    center_depth = integrate(0., z0)
    depth_cache = {z0: center_depth}
    def depth(z):
        if z not in depth_cache:
            depth_cache[z] = center_depth+integrate(z0, z)
        return depth_cache[z]
    sound = lambda z: float(solved.sound_horizon(z))
    atomic = {'speed_of_light_m_s': float(constants.c), 'Mpc_m': float(constants.Mpc),
              'G_SI': float(constants.G), 'hydrogen_mass_kg': float(constants.m_H),
              'helium_hydrogen_mass_ratio': float(constants.mass_ratio_He_H),
              'thomson_cross_section_m2': float(constants.sigma_thomson)}
    capacity = late_ionization_drag_capacity(redshift_max=tail_redshift,
                cosmology=cfg['cosmology'], components=omega, atomic=atomic)
    bracket = (z0/2, 3*z0/2)
    tail = drag_opacity_enclosure(depth, sound, redshift_bracket=bracket,
                                  absolute_bound=capacity['absolute_optical_depth_bound'])
    tail.update(capacity=capacity, coverage='electron-history changes restricted to the stated late interval')
    scenario = drag_opacity_enclosure(depth, sound, redshift_bracket=bracket,
                                      relative_bound=relative_opacity_bound)
    scenario.update(source=opacity_envelope_source,
                    coverage='assumed pointwise relative recombination-opacity envelope over the entire drag integral',
                    envelope_verified_for_generated_background=False)
    calibrations = [{'recfast_calibration': 'cosmorec', 'r_drag_Mpc': float(derived['rdrag']),
                     'z_drag': z0}]
    for name in ('hyrec', 'planck'):
        alternative = background(name)
        data = alternative.get_derived_params()
        distance_residual = max(abs(float(alternative.hubble_parameter(row['z']))/row['H_km_s_Mpc']-1)
                               for row in checked['outputs']['background_distances']['rows'])
        if distance_residual > 2e-12:
            raise ValueError('a recombination comparison altered the fixed expansion background')
        calibrations.append({'recfast_calibration': name, 'r_drag_Mpc': float(data['rdrag']),
                             'z_drag': float(data['zdrag']),
                             'maximum_relative_H_residual': distance_residual})
    direct = (evaluate_hyrec_atomic_response(solved, checked, runtime=hyrec_runtime,
                    generated_atomic=generated_atomic,
                    late_depth_bound=capacity['absolute_optical_depth_bound'])
                    if hyrec_runtime is not None else None)
    result = {'center_execution_sha256': checked['execution_sha256'],
              'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'camb_version': camb.__version__, 'fixed_background_configuration_sha256': checked['configuration_sha256'],
              'atomic_constants': atomic, 'late_ionization': tail,
              'relative_opacity_scenario': scenario, 'recfast_calibration_comparisons': calibrations,
              'recfast_comparison_scope': 'three RECFAST calibration sets; direct HYREC, when supplied, is evaluated separately',
              'numerical_evaluation': {'depth_at_saved_drag_root': center_depth,
                  'largest_depth_quadrature_error_estimate': max(error_estimates),
                  'restored_r_drag_Mpc': float(derived['rdrag']),
                  'scope': 'quadrature/root estimates and CAMB thermal-solver output; no interval certificate of the RECFAST evolution'},
              'omitted_physical_uncertainty': ['recombination opacity above the late interval beyond the declared scenario',
                  'generated atomic constants and finite-temperature atomic corrections',
                  'upstream baryon/helium/temperature changes and nonstandard expansion histories'],
              'prediction_parameters_updated': False, 'theory_covariance_assigned': False,
              'work': work}
    if direct is not None:
        result['direct_hyrec_atomic_response'] = direct
        result['omitted_physical_uncertainty'] = [
            'a uniform physical remainder bound for the HYREC atomic and radiative-transfer approximation',
            'upstream baryon, helium and temperature changes, nuclear masses and nonstandard expansion histories']
        work['direct_recombination_solves'] = direct['work']['recombination_solves']
    result['budget_sha256'] = fingerprint(result)
    return result


def evaluate_hyrec_atomic_response(background, center, *, runtime, generated_atomic,
                                  late_depth_bound):
    """Direct HYREC-2 FULL histories at fixed expansion and finite atomic inputs.

    The caller supplies the official HYREC-2 shared library compiled with
    MODEL=FULL, its atomic tables, and generated alpha and electron mass.
    All paths identify solver resources; no observation is read or fitted.
    The published record retains resource fingerprints rather than local paths.
    HYREC-2's public 2020 C ABI and full-radiative-transfer step are used.
    """
    import ctypes as ct
    import numpy as np
    from camb import constants
    from scipy.integrate import quad
    from scipy.optimize import brentq
    if (set(generated_atomic) != {'alpha', 'electron_mass_GeV'} or
            not all(math.isfinite(v) and v > 0 for v in generated_atomic.values())):
        raise ValueError('positive generated alpha and electron mass in GeV required')
    if not math.isfinite(late_depth_bound) or not 0 <= late_depth_bound < 1:
        raise ValueError('a nonnegative finite late optical-depth bound below one is required')
    directory = Path(runtime['data_directory']).resolve()
    library = Path(runtime['library']).resolve()
    revision = runtime['repository_revision']
    if not isinstance(revision, str) or not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('the official HYREC source commit must accompany the solver resources')
    resources = ['Alpha_inf.dat', 'R_inf.dat', 'fit_swift.dat', 'two_photon_tables.dat']
    sources = ['history.c', 'history.h', 'hydrogen.c', 'hydrogen.h', 'helium.c',
               'helium.h', 'hyrectools.c', 'hyrectools.h', 'energy_injection.c', 'energy_injection.h']
    files = {name: hashlib.sha256((directory/name).read_bytes()).hexdigest()
             for name in resources+sources}
    files['shared_library'] = hashlib.sha256(library.read_bytes()).hexdigest()
    lib = ct.CDLL(str(library))
    class Injection(ct.Structure):
        _fields_ = ([(n, ct.c_double) for n in
            'odmh2 pann pann_halo ann_z ann_zmax ann_zmin ann_var ann_z_halo decay Mpbh fpbh'.split()]
            + [('on_the_spot', ct.c_int), ('ion', ct.c_double), ('exclya', ct.c_double)])
    class Cosmology(ct.Structure):
        _fields_ = ([(n, ct.c_double) for n in
            'h T0 obh2 ocbh2 odeh2 okh2 orh2 onuh2 w0 wa Neff Nur Nmnu'.split()]
            + [('mnu', ct.c_double*3)] + [(n, ct.c_double) for n in
            'fHe nH0 YHe fsR meR dlna nz'.split()] + [('inj_params', ct.POINTER(Injection))])
    class History(ct.Structure):
        _fields_ = [('atomic', ct.c_void_p), ('cosmo', ct.POINTER(Cosmology)),
            ('zmax', ct.c_double), ('zmin', ct.c_double), ('Nz', ct.c_long),
            ('xe_output', ct.POINTER(ct.c_double)), ('Tm_output', ct.POINTER(ct.c_double))]
        _fields_ += [(n, ct.c_int) for n in 'error quasi_eq loop_after_quasi Tm_evolve_implicit'.split()]
        _fields_ += [('error_message', ct.c_char_p), ('path_to_hyrec', ct.c_char_p),
                     ('rad', ct.c_void_p), ('fit', ct.c_void_p)]
    lib.hyrec_allocate.argtypes = [ct.POINTER(History), ct.c_double, ct.c_double]
    lib.hyrec_allocate.restype = None
    lib.rec_build_history.argtypes = [ct.POINTER(History), ct.c_int, ct.POINTER(ct.c_double)]
    lib.rec_build_history.restype = ct.c_char_p
    lib.hyrec_xe.argtypes = [ct.c_double, ct.POINTER(History)]
    lib.hyrec_xe.restype = ct.c_double
    lib.hyrec_free.argtypes = [ct.POINTER(History)]
    lib.hyrec_free.restype = None
    cfg = center['configuration']['cosmology']
    omega = center['density_dictionary']['components']
    h0 = cfg['H0']*1000/constants.Mpc
    nH = 3*h0**2/(8*math.pi*constants.G)*omega['baryon']*(1-cfg['YHe'])/constants.m_H
    fHe = cfg['YHe']/(constants.mass_ratio_He_H*(1-cfg['YHe']))
    loading = 3*omega['baryon']/(4*omega['photon'])
    alpha_standard = (math.sqrt(3*constants.sigma_thomson/(8*math.pi))
                      *constants.m_e*constants.c/constants.hbar)
    mass_standard = constants.m_e*constants.c**2/(1e9*constants.eV)
    ratios = {'alpha': generated_atomic['alpha']/alpha_standard,
              'electron_mass': generated_atomic['electron_mass_GeV']/mass_standard}
    trials = [('standard_atomic', 1., 1.),
              ('generated_atomic', ratios['alpha'], ratios['electron_mass'])]
    work = {'recombination_solves': 0, 'power_spectrum_solves': 0,
            'expansion_background_solves': 0, 'opacity_evaluations': 0,
            'optical_depth_quadratures': 0}
    rows = []
    expansion = None
    # On Windows the C runtime needs an ANSI-compatible resource path. An
    # explicit ASCII directory may be supplied for the official solver tables.
    try:
        data_path = (str(directory).replace('\\', '/')+'/').encode('ascii')
    except UnicodeEncodeError:
        if Path.cwd().resolve() != directory:
            raise ValueError('use an ASCII HYREC resource directory or invoke from its table directory')
        data_path = b''
    for name, alpha_ratio, mass_ratio in trials:
        history = History()
        history.path_to_hyrec = data_path
        lib.hyrec_allocate(ct.byref(history), 8000., 0.)
        if history.error:
            raise RuntimeError(history.error_message.decode(errors='replace'))
        try:
            if history.Nz != int(math.log(8001.)/8.49e-5)+2:
                raise ValueError('HYREC library must be compiled with MODEL=FULL and its standard integration step')
            cosmo = history.cosmo.contents
            injection = ct.cast(ct.cast(cosmo.inj_params, ct.c_void_p).value, ct.POINTER(Injection))
            ct.memset(history.cosmo, 0, ct.sizeof(Cosmology))
            ct.memset(injection, 0, ct.sizeof(Injection))
            cosmo.inj_params = injection
            cosmo.h, cosmo.T0, cosmo.obh2 = cfg['H0']/100, cfg['TCMB'], cfg['ombh2']
            cosmo.ocbh2 = cosmo.obh2+center['resolved_cold_density']['omch2']
            cosmo.YHe, cosmo.Neff = cfg['YHe'], cfg['nnu']
            cosmo.nH0, cosmo.fHe = nH*1e-6, fHe
            cosmo.fsR, cosmo.meR, cosmo.dlna = alpha_ratio, mass_ratio, 8.49e-5
            injection.contents.on_the_spot = 1
            injection.contents.Mpbh = 1.
            injection.contents.odmh2 = center['resolved_cold_density']['omch2']
            if expansion is None:
                grid = np.arange(history.Nz)*history.zmax/history.Nz
                expansion = np.asarray(background.hubble_parameter(grid), dtype=np.float64)*1000/constants.Mpc
                work['expansion_samples_reused'] = int(history.Nz)
            elif len(expansion) != history.Nz:
                raise ValueError('the direct histories require a common expansion grid')
            lib.rec_build_history(ct.byref(history), 3, expansion.ctypes.data_as(ct.POINTER(ct.c_double)))
            work['recombination_solves'] += 1
            if history.error:
                raise RuntimeError(history.error_message.decode(errors='replace'))
            sigma = constants.sigma_thomson*(alpha_ratio/mass_ratio)**2
            errors = []
            def integrand(z):
                work['opacity_evaluations'] += 1
                xe = lib.hyrec_xe(z, ct.byref(history))
                if history.error or not math.isfinite(xe) or xe < 0:
                    raise ValueError('invalid HYREC electron fraction')
                return constants.c*sigma*nH*xe*(1+z)**3/(float(background.hubble_parameter(z))*1000/constants.Mpc*loading)
            def integrate(left, right):
                value, error = quad(integrand, left, right, epsabs=1e-10, epsrel=1e-9, limit=160)
                work['optical_depth_quadratures'] += 1
                errors.append(error)
                return value
            reference_z = 1060.
            reference_depth = math.fsum(integrate(a, b) for a, b in
                                       ((0., 30.), (30., 500.), (500., 800.), (800., reference_z)))
            depth = lambda z: reference_depth+integrate(reference_z, z)
            root = brentq(lambda z: depth(z)-1,
                          900., 1200., xtol=1e-8, rtol=1e-13)
            late = drag_opacity_enclosure(depth, lambda z: float(background.sound_horizon(z)),
                redshift_bracket=(900., 1200.),
                absolute_bound=late_depth_bound*(alpha_ratio/mass_ratio)**2)
            rows.append({'atomic_inputs': name, 'alpha_ratio': alpha_ratio,
                'electron_mass_ratio': mass_ratio, 'thomson_ratio': (alpha_ratio/mass_ratio)**2,
                'z_drag': float(root), 'r_drag_Mpc': float(background.sound_horizon(root)),
                'x_e_at_1100': float(lib.hyrec_xe(1100., ct.byref(history))),
                'late_ionization': late,
                'largest_depth_quadrature_error_estimate': max(errors),
                'history_steps': int(history.Nz)})
        finally:
            lib.hyrec_free(ct.byref(history))
    return {'solver': 'HYREC-2, full radiative transfer (MODEL=FULL)',
            'source_repository': 'https://github.com/nanoomlee/HYREC-2',
            'repository_revision': revision,
            'build': {'model_selector': 'MODEL=FULL (3)',
                'integration_step_dln_a': 8.49e-5,
                'source_adaptation': 'history.h guards the default MODEL with ifndef; full transport selected at compilation',
                'integration_mode': 'original full radiative transfer, without the SWIFT correction approximation'},
            'resource_sha256': files, 'generated_atomic_inputs': dict(generated_atomic),
            'atomic_reference': {'alpha_from_CAMB_Thomson_relation': alpha_standard,
                'electron_mass_GeV': mass_standard,
                'convention': 'ratios rescale HYREC standard atomic rates and the same Thomson cross section'},
            'rows': rows, 'work': work,
            'scope': 'finite recombination response at fixed expansion, baryon loading and helium fraction',
            'error_interpretation': 'quadrature estimates and solver comparison; no uniform physical remainder bound',
            'production_parameters_updated': False}


def thermal_history_distance_budget(center, bao, *, generated_atomic=None):
    """Map saved finite drag intervals to all distance ratios and their statistic."""
    from scipy.stats import chi2
    thermal = center['thermal_history_budget']
    if (thermal['center_execution_sha256'] != center['execution_sha256'] or
            thermal['budget_sha256'] != fingerprint({k: v for k, v in thermal.items() if k != 'budget_sha256'})):
        raise ValueError('a matching thermal-history budget is required')
    if bao.get('camb_execution_sha256') != center['execution_sha256']:
        raise ValueError('the BAO comparison and thermal budget must share their background')
    if 'direct_hyrec_atomic_response' in thermal:
        if generated_atomic != thermal['direct_hyrec_atomic_response']['generated_atomic_inputs']:
            raise ValueError('current generated atomic inputs must match the retained direct recombination calculation')
    rd0 = center['outputs']['r_drag_Mpc']
    projection = bao['scale_diagnostic']
    alpha0, sigma = projection['alpha'], projection['alpha_standard_error']
    shape, dof = projection['chi2_orthogonal'], bao['degrees_of_freedom']
    def interval_result(sound_interval):
        lo, hi = map(float, sound_interval)
        if not 0 < lo <= hi:
            raise ValueError('positive ordered sound-horizon interval required')
        alpha = [rd0/hi, rd0/lo]
        optimum = min(max(alpha0, alpha[0]), alpha[1])
        statistic = lambda a: shape+((a-alpha0)/sigma)**2
        values = [statistic(optimum), max(map(statistic, alpha))]
        return {'sound_horizon_interval_Mpc': [lo, hi], 'common_ratio_interval': alpha,
                'chi2_interval': values, 'gaussian_reference_tail_probability_interval':
                    [float(chi2.sf(values[1], dof)), float(chi2.sf(values[0], dof))],
                'degrees_of_freedom': dof,
                'distance_ratio_intervals': [{'observation_index': row.get('observation_index', i),
                    'interval': [row['predicted']*a for a in alpha]}
                    for i, row in enumerate(bao['rows'])]}
    result = {name: interval_result(thermal[name]['sound_horizon_interval_Mpc'])
              for name in ('late_ionization', 'relative_opacity_scenario')}
    result['recfast_calibration_comparisons'] = [
        {'recfast_calibration': row['recfast_calibration'],
         **interval_result([row['r_drag_Mpc'], row['r_drag_Mpc']])}
        for row in thermal['recfast_calibration_comparisons']]
    if 'direct_hyrec_atomic_response' in thermal:
        result['direct_hyrec_atomic_response'] = [
            {'atomic_inputs': row['atomic_inputs'],
             **interval_result([row['r_drag_Mpc'], row['r_drag_Mpc']]),
             'with_late_ionization_capacity': interval_result(row['late_ionization']['sound_horizon_interval_Mpc'])}
            for row in thermal['direct_hyrec_atomic_response']['rows']]
    result.update(thermal_budget_sha256=thermal['budget_sha256'],
        fixed_chi2=bao['chi2'], fixed_tail_probability=bao['pte'],
        statistical_interpretation='range over a deterministic prediction set using the original observational covariance',
        theory_covariance_assigned=False, parameters_fitted=False,
        operation_counts={'new_thermal_background_solves': 0, 'power_spectrum_solves': 0,
                          'additional_covariance_factorizations': 0})
    return result


def background_physical_coordinates(record):
    """Independent physical coordinates of the completed thermal background."""
    cosmology = record["configuration"]["cosmology"]
    return {"YHe":float(cosmology["YHe"]), "omega_b":float(cosmology["ombh2"]),
            "omega_m":float(record["density_dictionary"]["Omega_m_with_massive_neutrinos"])
                      *(cosmology["H0"]/100)**2,
            "TCMB":float(cosmology["TCMB"]), "N_eff":float(cosmology["nnu"]),
            "H0":float(cosmology["H0"]), "neutrino_mass_scale":1.}


def background_probe_configuration(center, coordinate, log_displacement):
    """A local physical-coordinate derivative, with the other coordinates fixed.

    Total matter is omega_b+omega_cold+omega_nu; flatness determines vacuum.
    This derivative coordinate system does not change the production mapping.
    """
    if coordinate not in (*BACKGROUND_COORDINATES,*OPTIONAL_BACKGROUND_COORDINATES) or \
            not math.isfinite(log_displacement):
        raise ValueError("known background coordinate and finite displacement required")
    cfg = json.loads(json.dumps(center["configuration"]))
    values = background_physical_coordinates(center)
    values[coordinate] *= math.exp(log_displacement)
    if not 0 < values["YHe"] < 1:
        raise ValueError("helium fraction must lie strictly between zero and one")
    cfg["calculation_mode"] = "background"
    cfg["density_mapping"] = "physical_background_probe"
    cfg["physical_coordinates"] = values
    cfg["cosmology"].update(H0=values["H0"],ombh2=values["omega_b"],
                             TCMB=values["TCMB"],YHe=values["YHe"],
                             nnu=values["N_eff"],standard_neutrino_neff=values["N_eff"])
    cfg["neutrino_masses_eV"] = [m*values["neutrino_mass_scale"]
                                  for m in center["configuration"]["neutrino_masses_eV"]]
    cfg["cosmology"]["mnu"] = math.fsum(cfg["neutrino_masses_eV"])
    return cfg


def background_readouts(record):
    """Distances and drag scale from one solved background, without a likelihood."""
    rd = float(record["outputs"]["r_drag_Mpc"])
    values = {"r_drag_Mpc":rd,"H0_r_drag":record["configuration"]["cosmology"]["H0"]*rd}
    for row in record["outputs"]["background_distances"]["rows"]:
        z = row["z"]
        dm,dh = row["D_M_Mpc"]/rd,row["D_H_Mpc"]/rd
        values.update({f"DM_over_rd@{z:g}":dm,f"DH_over_rd@{z:g}":dh,
                       f"DV_over_rd@{z:g}":(z*dm*dm*dh)**(1/3)})
    if any(not math.isfinite(value) or value <= 0 for value in values.values()):
        raise ValueError("background response requires finite positive readouts")
    return values


def evaluate_background_response(center, *, coordinates=BACKGROUND_COORDINATES,
                                 log_step=1e-3, refine=(), previous=None, solver=None):
    """Finite differences of the thermal background, reusing a verified centre.

    Each requested coordinate costs two background solves. Only named refine
    coordinates add a second pair at half step. Completed stencil points can
    be reused after checking their centre, configuration and implementation
    identities. Neither observations nor a fitted endpoint enter this response.
    """
    checked = current_camb_record(center["configuration"]["endpoint_inputs"],center)
    if checked["status"] != "current_inputs_match":
        raise ValueError("background response centre is unavailable: "+checked["reason"])
    coordinates = tuple(dict.fromkeys(coordinates))
    refine = tuple(dict.fromkeys(refine))
    allowed = (*BACKGROUND_COORDINATES,*OPTIONAL_BACKGROUND_COORDINATES)
    if not coordinates or any(key not in allowed for key in coordinates) or \
            any(key not in coordinates for key in refine) or \
            not math.isfinite(log_step) or not 0 < log_step <= .05:
        raise ValueError("explicit background coordinates, valid refinement subset and 0<log_step<=.05 required")
    implementation = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    identity = {"center_execution_sha256":checked["execution_sha256"],
                "response_implementation_sha256":implementation,
                "coordinate_convention":"independent log physical densities, temperature and helium at flatness"}
    cache = {}
    if previous is not None:
        if any(previous.get(key) != value for key,value in identity.items()):
            raise ValueError("saved background response does not match the centre and implementation")
        for point in previous.get("stencil",[]):
            key = (point["coordinate"],point["log_displacement"])
            cfg = background_probe_configuration(checked,*key)
            if point["configuration_sha256"] != fingerprint(cfg):
                raise ValueError("saved background response point has a different configuration")
            if point["payload_sha256"] != fingerprint({k:v for k,v in point.items() if k != "payload_sha256"}):
                raise ValueError("saved background response point fingerprint mismatch")
            cache[key] = point
    solver = run if solver is None else solver
    evaluations = background_calls = full_calls = reused = 0
    def sample(coordinate,displacement):
        nonlocal evaluations,background_calls,full_calls,reused
        key = (coordinate,displacement)
        if key in cache:
            reused += 1
            return cache[key]["readouts"]
        cfg = background_probe_configuration(checked,coordinate,displacement)
        solved = solver(cfg)
        if solved.get("calculation_mode") != "background" or any(
                name in solved["outputs"] for name in ("sigma8","S8_total_matter")):
            raise ValueError("background response solver supplied power-spectrum outputs")
        if solved["configuration_sha256"] != fingerprint(cfg):
            raise ValueError("background response solver changed its configuration")
        point = {"coordinate":coordinate,"log_displacement":displacement,
                 "configuration_sha256":fingerprint(cfg),"camb_version":solved["camb_version"],
                 "readouts":background_readouts(solved),"work":solved["work"]}
        point["payload_sha256"] = fingerprint(point)
        cache[key] = point
        evaluations += 1
        background_calls += solved["work"]["explicit_background_solver_calls"]
        full_calls += solved["work"]["full_perturbation_solver_calls"]
        return point["readouts"]
    rows = {}
    center_values = background_readouts(checked)
    for coordinate in coordinates:
        plus,minus = sample(coordinate,log_step),sample(coordinate,-log_step)
        coarse = {key:(math.log(plus[key])-math.log(minus[key]))/(2*log_step) for key in center_values}
        entry = {"log_step":log_step,"log_derivative":coarse,
                 "half_step_checked":coordinate in refine,
                 "finite_difference_order":2}
        if coordinate in refine:
            plus_half,minus_half = sample(coordinate,log_step/2),sample(coordinate,-log_step/2)
            fine = {key:(math.log(plus_half[key])-math.log(minus_half[key]))/log_step for key in center_values}
            entry.update(log_derivative=fine,coarse_log_derivative=coarse,
                         half_step_abs_difference={key:abs(fine[key]-coarse[key]) for key in center_values})
        rows[coordinate] = entry
    result = {**identity,"center_readouts":center_values,
              "physical_coordinate_values":background_physical_coordinates(checked),
              "coordinates":list(coordinates),"responses":rows,
              "stencil":[cache[key] for key in sorted(cache)],
              "atomic_physics":checked.get("atomic_physics",{
                  "constant_convention":"standard CAMB recombination constants in the retained propagation",
                  "generated_electron_mass_applied":False,"generated_fine_structure_applied":False}),
              "production_parameters_updated":False,
              "theory_covariance_assigned":False,
              "work":{"center_solver_calls":0,"new_stencil_evaluations":evaluations,
                      "reused_stencil_evaluations":reused,
                      "explicit_background_solver_calls":background_calls,
                      "full_perturbation_solver_calls":full_calls},
              "derivative_accuracy":"central finite differences; half-step differences are consistency estimates for the named coordinates"}
    result["response_sha256"] = fingerprint(result)
    return result


def compose_background_directions(response, directions, *, source, held_fixed=()):
    """Compose supplied source derivatives; unavailable coordinates stay explicit."""
    if not isinstance(source,str) or not source.strip() or not isinstance(directions,dict):
        raise ValueError("explicit source and direction mapping required")
    output = {}
    for name,direction in directions.items():
        if not isinstance(direction,dict) or any(not math.isfinite(value) for value in direction.values()):
            raise ValueError("finite physical-coordinate log derivatives required")
        unknown = set(direction)-set((*BACKGROUND_COORDINATES,*OPTIONAL_BACKGROUND_COORDINATES))
        if unknown:
            raise ValueError("unknown physical-coordinate direction")
        missing = [key for key,value in direction.items() if value != 0 and key not in response["responses"]]
        output[name] = {"physical_coordinate_direction":direction,
                        "missing_response_coordinates":missing,
                        "status":"incomplete" if missing else "evaluated"}
        if not missing:
            output[name]["log_readout_derivative"] = {
                readout:math.fsum(value*response["responses"][key]["log_derivative"][readout]
                                 for key,value in direction.items() if value != 0)
                for readout in response["center_readouts"]}
    return {"source":source,"held_fixed":list(held_fixed),"directions":output,
            "response_sha256":response["response_sha256"],"parameters_fitted":False}
