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

"""Reference inputs for Standard-Model running and observational comparisons.

The two-loop comparison flow uses the listed couplings at M_Z in the
stated PDG/Buttazzo reference convention, with GUT-normalized hypercharge
g1=sqrt(5/3)*g'. Masses, widths, cosmological quantities and lattice
benchmarks supply the separate comparison table. Each is used with the
scale, scheme or reference interpretation stated in Guo (2026g).

The comparison store records these values with SM_INPUT provenance.
Production quantities are computed before their observational comparison.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import published_sm_value, sm_set  # noqa: E402

# Registered reference identifiers. Values and datasets have one authority:
# comparison/reference_inputs.json, read through the common parameter interface.
SM_INPUT_KEYS = (
    "running_mass_reference",
    "charged_lepton_pole_reference",
    "CMB_MONOPOLE",
    "CAMB_PROPAGATION_SETTINGS",
    "nucleon_qcd_qed_lattice",
    "M_Z",
    "M_Pl",
    "g1_MZ",
    "g2_MZ",
    "g3_MZ",
    "yt_MZ",
    "lam_MZ",
    "lambda_H_MZ",
    "ye_MZ",
    "yu_MZ",
    "yd_MZ",
    "alpha_inv_obs",
    "alpha_inv_MZ_obs",
    "alpha_s_MZ_obs",
    "tau_n_obs",
    "tau_n_obs_sigma",
    "dm_np_obs_GeV",
    "dm_np_obs_sigma_GeV",
    "v_HIGGS_obs",
    "m_W_obs",
    "G_F_obs",
    "m_H_obs",
    "Gamma_Z_obs",
    "Gamma_had_obs",
    "Gamma_l_obs",
    "Gamma_b_obs",
    "Gamma_inv_obs",
    "sigma_had_obs",
    "R_l_obs",
    "R_b_obs",
    "sin2thetaW_eff_obs",
    "sin2thetaW_MSbar_obs",
    "rho_obs",
    "m_glueball_obs",
    "Lambda_QCD_obs",
    "T_deconf_obs",
    "string_tension_obs",
    "m_p_obs",
    "m_glueball_2pp_ratio_obs",
    "m_glueball_0ppstar_ratio_obs",
    "m_glueball_0mp_ratio_obs",
    "m_e_obs",
    "m_mu_obs",
    "m_mu_over_m_e_obs",
    "m_t_obs",
    "m_b_obs",
    "m_tau_obs",
    "m_t_over_m_c_obs",
    "m_b_over_m_s_obs",
    "m_t_over_m_u_obs",
    "m_tau_over_m_mu_obs",
    "Delta_m21_sq_obs",
    "Delta_m31_sq_obs",
    "V_us_obs",
    "pmns_delta_over_pi_obs",
    "s23_pmns_obs",
    "s13_pmns_obs",
    "s12_pmns_obs",
    "jarlskog_J_obs",
    "ckm_delta_deg_obs",
    "lambda_C_obs",
    "A_ckm_obs",
    "eta_ckm_obs",
    "rho_bar_ckm_obs",
    "m_d_over_m_s_obs",
    "m_u_over_m_c_obs",
    "H0_GeV_obs",
    "r_bound_obs",
    "a0_MOND_obs",
    "c_m_s_obs",
    "Omega_b_obs",
    "T_CMB_K",
    "Omega_Lambda_obs",
    "Lambda_obs",
    "eta_b_obs",
    "Delta2_R_obs",
    "one_minus_ns_obs",
    "Y_p_obs",
    "N_eff_obs",
    "Omega_DM_obs",
    "epsilon_obs",
)


def init_sm_table() -> None:
    """Copy registered comparison inputs into the calculation's reference store."""
    notes = {
        "running_mass_reference": "Huang-Zhou (2021), Tables 2, 3, 8; correlated full-SM MSbar reference",
        "charged_lepton_pole_reference": "Huang-Zhou (2021), Eq. (5); independent QED comparison inputs",
        "CMB_MONOPOLE": "Fixsen (2009); CMB monopole temperature with quoted standard deviation",
        "nucleon_qcd_qed_lattice": (
            "Borsanyi et al. (2015), Table 1; independent QCD+QED comparison, "
            "with the original total splitting and Sigma-based separation convention"
        ),
        "CAMB_PROPAGATION_SETTINGS": (
            "Declared propagation convention: CAMB tanh reionization with registered optical depth; "
            "external comparison setting, not an endogenous prediction"
        ),
        "Delta_m21_sq_obs": (
            "observed solar neutrino mass-squared splitting, comparison only"
        ),
        "Delta_m31_sq_obs": (
            "observed atmospheric neutrino mass-squared splitting, comparison only"
        ),
        "N_eff_obs": (
            "Standard-Model theoretical thermal-neutrino benchmark"
        ),
        "tau_n_obs": (
            "PDG 2024 neutron listing, registered mean life and uncertainty; "
            "ultracold-neutron average, including the reported scale factor. "
            "S. Navas et al., Phys. Rev. D 110, 030001 (2024)."
        ),
        "tau_n_obs_sigma": "PDG 2024 neutron mean-life standard uncertainty in seconds",
        "dm_np_obs_GeV": (
            "PDG 2024 neutron listing, neutron-minus-proton mass difference; "
            "2018 CODATA value, converted from MeV to GeV."
        ),
        "dm_np_obs_sigma_GeV": "PDG 2024 neutron-proton mass-difference standard uncertainty in GeV",
    }
    for key in SM_INPUT_KEYS:
        sm_set(key, published_sm_value(key),
               note=notes.get(key, "Reference input for the stated comparison convention"),
               comparison_kind="declared_convention" if key == "CAMB_PROPAGATION_SETTINGS" else "observed_target")


def sm_value(key: str):
    """Read an SM input value (comparison only)."""
    from cg_core.params import sm_value as _sm_value

    return _sm_value(key)


def joint_comparison_input_fingerprints():
    """Bind joint likelihoods to the registered observations used by them."""
    from cg_core.params import value_fingerprint
    return {key: value_fingerprint(sm_value(key)) for key in
            ('running_mass_reference', 'charged_lepton_pole_reference',
             'CMB_MONOPOLE', 'DESI_DR2_BAO', 'tau_n_obs', 'tau_n_obs_sigma',
             'dm_np_obs_GeV', 'dm_np_obs_sigma_GeV', 'Y_p_obs',
             'nucleon_qcd_qed_lattice')}


def neutron_helium_benchmark(generated, *, generated_joint_response=None):
    """Compare completed weak-chain values; no theory covariance is fitted."""
    import math
    rows = []
    definitions = (
        ("neutron_proton_mass_difference", "bbn_dm_np", "dm_np_obs_GeV", "dm_np_obs_sigma_GeV", "GeV"),
        ("free_neutron_lifetime", "bbn_tau_n", "tau_n_obs", "tau_n_obs_sigma", "s"),
        ("helium_baryon_fraction", "bbn_Yp", "Y_p_obs", None, "1"),
    )
    for name, key, reference_key, error_key, units in definitions:
        prediction, reference = float(generated[key]), float(sm_value(reference_key))
        if not all(math.isfinite(x) and x > 0 for x in (prediction, reference)):
            raise ValueError("positive finite generated and comparison values required")
        rows.append({"quantity": name, "prediction": prediction, "reference": reference,
                     "reference_standard_uncertainty": None if error_key is None else float(sm_value(error_key)),
                     "relative_percent": 100*(prediction/reference-1), "units": units,
                     "prediction_key": key, "reference_key": reference_key})
    result = {"rows": rows,
            "reference": "S. Navas et al. (PDG), Phys. Rev. D 110, 030001 (2024), neutron listing; registered helium benchmark",
            "comparison_scope": "central values at the declared weak-rate, hadronic and capture approximations",
            "theory_covariance_supplied": False, "joint_significance_calculated": False,
            "production_parameters_updated": False}
    if generated_joint_response is not None:
        result["mass_gap_substitution"] = neutron_mass_gap_diagnostic(
            generated_joint_response, rows)
        result["independent_lattice_matching"] = nucleon_lattice_benchmark(
            generated_joint_response)
    return result


def nucleon_lattice_benchmark(generated_joint_response):
    """Propagate one independently calculated QCD+QED splitting after production."""
    from cg_frg.cosmology.bbn_helium import weak_mass_difference_ranges

    reference = sm_value('nucleon_qcd_qed_lattice')
    mass_inputs = {'m_down', 'm_up', 'scalar_isovector_matrix_element',
                   'electromagnetic_split'}
    fixed_inputs = {key: value for key, value in generated_joint_response['inputs'].items()
                    if key not in mass_inputs}
    fixed_inputs.update(generated_joint_response['fixed_thermal_inputs'])
    total = reference['total']
    forward = weak_mass_difference_ranges(
        central_split=total['central'], statistical_error=total['statistical'],
        systematic_error=total['systematic'], **fixed_inputs)
    return {
        'reference_key': 'nucleon_qcd_qed_lattice',
        'reference': reference,
        'generated_values': generated_joint_response['values'],
        'fixed_weak_and_thermal_inputs': fixed_inputs,
        'weak_chain': forward,
        'matching_scope': 'independent QCD+QED total at its physical point; generated weak and thermal inputs retained',
        'component_comparison': 'QCD and QED terms retain the published Sigma convention; comparison of separate native terms requires a matching separation convention',
        'production_parameters_updated': False,
        'component_errors_combined_as_independent': False,
        'theory_covariance_assigned': False,
    }


def neutron_mass_gap_diagnostic(generated_joint_response, benchmark_rows):
    """Propagate the registered neutron mass gap through one comparison chain.

    The generated weak and thermal inputs are retained exactly. Only the
    mass gap is replaced, consistently in the decay phase space, freeze-out,
    elapsed decay interval and helium yield. The generated centre and its
    derivatives are reused from their completed joint-response record.
    """
    import math
    from cg_frg.cosmology.bbn_helium import instantaneous_weak_chain

    original = generated_joint_response
    baseline = original['values']
    dm = float(sm_value('dm_np_obs_GeV'))
    sigma_dm = float(sm_value('dm_np_obs_sigma_GeV'))
    if not math.isfinite(sigma_dm) or sigma_dm < 0:
        raise ValueError("finite nonnegative reference mass-gap uncertainty required")
    mass_inputs = {'m_down', 'm_up', 'scalar_isovector_matrix_element',
                   'electromagnetic_split'}
    fixed_inputs = {key: value for key, value in original['inputs'].items()
                    if key not in mass_inputs}
    fixed_inputs.update(original['fixed_thermal_inputs'])
    chain = instantaneous_weak_chain(neutron_proton_split=dm, **fixed_inputs,
                                     include_phase_derivatives=True)
    values, phase = chain['values'], chain['phase_space']
    for row in benchmark_rows:
        key = {'bbn_dm_np': 'dm_np', 'bbn_tau_n': 'tau_n', 'bbn_Yp': 'Y_p'}[row['prediction_key']]
        if baseline[key] != row['prediction']:
            raise ValueError("weak comparison and its generated input record must share one centre")
    comparisons = [dict(quantity=row['quantity'],
                        conditional_value=values[{'bbn_dm_np': 'dm_np',
                            'bbn_tau_n': 'tau_n', 'bbn_Yp': 'Y_p'}[row['prediction_key']]],
                        reference=row['reference'], units=row['units'])
                   for row in benchmark_rows]
    for row in comparisons:
        row['relative_percent'] = 100*(row['conditional_value']/row['reference']-1)

    me = fixed_inputs['electron_mass']
    baseline_phase = original['phase_space']
    elasticity = (-baseline['dm_np']/me*
                  baseline_phase['derivative_splitting_ratio']/baseline_phase['value'])
    tau_n, T_f, interval, Yp = (values[key] for key in ('tau_n', 'T_f', 't_decay', 'Y_p'))
    log_tau_derivative = -phase['derivative_splitting_ratio']/(me*phase['value'])
    temperature_derivative = -T_f/(2*(T_f+dm))
    interval_derivative = 2*chain['freeze_time']/T_f*temperature_derivative
    initial_fraction = chain['helium_fractions']['neutron_fraction_freeze']
    log_helium_derivative = (-(1-initial_fraction)*(1/T_f-dm/T_f**2*temperature_derivative)
        -interval_derivative/tau_n+interval/tau_n*log_tau_derivative)
    input_standard_uncertainties = dict(dm_np=sigma_dm,
        tau_n=abs(tau_n*log_tau_derivative)*sigma_dm,
        T_f=abs(temperature_derivative)*sigma_dm,
        t_decay=abs(interval_derivative)*sigma_dm,
        Y_p=abs(Yp*log_helium_derivative)*sigma_dm)
    phase_relative_error = phase['estimated_abs_error']/phase['value']
    return {
        "scope": "external mass-gap condition at otherwise fixed generated weak and thermal inputs",
        "substituted_quantity": "neutron_proton_split", "reference_key": "dm_np_obs_GeV",
        "fixed_inputs": fixed_inputs, "generated_values": dict(baseline),
        "conditional_values": values, "conditional_comparisons": comparisons,
        "generated_splitting_ratio": baseline['dm_np']/me,
        "conditional_splitting_ratio": dm/me,
        "generated_phase_space": baseline_phase['value'], "conditional_phase_space": phase,
        "conditional_helium_fractions": chain['helium_fractions'],
        "generated_lifetime_gap_elasticity": elasticity,
        "linear_lifetime_bias_from_gap_percent": elasticity*100*(baseline['dm_np']/dm-1),
        "linear_conditional_lifetime_change_percent": elasticity*100*(dm/baseline['dm_np']-1),
        "finite_conditional_relative_changes_percent": {
            key: 100*(values[key]/baseline[key]-1) for key in baseline},
        "reference_mass_gap_uncertainty": {
            "standard_uncertainty_GeV": sigma_dm,
            "propagated_standard_uncertainties": input_standard_uncertainties,
            "method": "first-order propagation of the registered mass-gap uncertainty only"},
        "numerical_error_estimates": {
            "phase_space_abs": phase['estimated_abs_error'],
            "tau_n_abs_s": tau_n*phase_relative_error,
            "Y_p_abs": Yp*interval/tau_n*phase_relative_error,
            "method": "adaptive quadrature estimate with first-order lifetime and capture propagation",
            "rigorous_interval_bound": False},
        "physical_approximation_uncertainty": {
            "quantified": False,
            "components": ["hadronic scalar and axial matrix elements",
                "electromagnetic mass separation", "weak radiative and recoil corrections",
                "instantaneous freeze-out and complete nuclear capture"]},
        "operation_counts": {"reused_generated_joint_responses": 1,
            "additional_phase_space_quadratures": 1,
            "integrand_evaluations": phase['integrand_evaluations'],
            "freeze_root_iterations": 120},
        "production_parameters_updated": False,
        "strong_and_electromagnetic_terms_fitted": False,
        "joint_significance_calculated": False}


def published_running_mass_benchmark(generated_lepton_matching=None):
    """Evaluate the registered correlated full-SM mass reference.

    The Huang-Zhou tables supply converted MSbar masses and their total
    covariance at M_Z. Reading these comparison inputs does not rerun
    SMDR or determine the generated action's finite Yukawa counterterms.
    Production quantities receive none of these reference masses.
    """
    import math
    import numpy as np
    from cg_core.joint_response import (
        RUNNING_MASS_SPECIES, running_mass_sum_rules,
        mass_sum_rule_beta_one_loop, charged_lepton_qed_log_matching,
        lepton_matching_spread_bound,
    )
    reference = sm_value("running_mass_reference")
    pole_reference = sm_value("charged_lepton_pole_reference")
    if tuple(reference["species_order"]) != RUNNING_MASS_SPECIES:
        raise ValueError("running_mass_reference has an incompatible species order")
    masses = np.asarray(reference["masses_GeV"], dtype=float)
    errors = np.asarray(reference["standard_deviations_GeV"], dtype=float)
    correlation = np.asarray(reference["correlation"], dtype=float)
    if (masses.shape != (7,) or errors.shape != (7,) or correlation.shape != (7, 7)
            or not np.all(np.isfinite(masses)) or np.any(masses <= 0)
            or not np.all(np.isfinite(errors)) or np.any(errors < 0)
            or not np.allclose(np.diag(correlation), 1., rtol=0., atol=1e-12)):
        raise ValueError("running_mass_reference must supply seven positive masses and valid errors")
    covariance = correlation*np.outer(errors/masses, errors/masses)
    citation = reference["citation"]
    result = running_mass_sum_rules(dict(zip(RUNNING_MASS_SPECIES, masses)), covariance,
        scale_GeV=reference["scale_GeV"], mass_definition=reference["mass_definition"],
        covariance_source=citation+", Tables 2, 3 and 8; delta method for log masses")
    result.update(reference=citation, reference_tables=list(reference["tables"]),
                  mass_standard_deviations_GeV=dict(zip(RUNNING_MASS_SPECIES, errors.tolist())),
                  mass_correlation=correlation.tolist(),
                  reference_error_model=reference["error_model"],
                  native_finite_matching_calculated=False)
    vev = float(reference["v_F_GeV"])
    if not math.isfinite(vev) or vev <= 0:
        raise ValueError("running_mass_reference v_F_GeV must be finite and positive")
    conversion = math.sqrt(2)/vev
    other = reference["additional_running_masses_GeV"]
    result["one_loop_scale_derivatives"] = mass_sum_rule_beta_one_loop(
        conversion*np.array([other["up"], masses[1], masses[0]]),
        conversion*np.array([other["down"], masses[5], masses[4]]),
        conversion*np.array([masses[6], masses[3], masses[2]]))
    result["charged_lepton_QED_check"] = charged_lepton_qed_log_matching(
        pole_reference["masses_GeV"], scale_GeV=reference["scale_GeV"],
        alpha=pole_reference["alpha_zero"])
    result["charged_lepton_QED_check"]["reference"] = pole_reference["citation"]
    central = result["weighted_finite_matching_constraints"]["charged_lepton"]
    sigma = result["standard_deviations"][1]
    qed = result["charged_lepton_QED_check"]["matching_log_correction"]
    result["remaining_lepton_matching"] = {
        "conversion_sequence": "geometric readout to pole level, followed by the displayed leading QED conversion to MSbar; remaining terms combined",
        "central_constraint": lepton_matching_spread_bound(
            (central, central), known_correction_interval=(qed, qed)),
        "three_sigma_reference_interval": lepton_matching_spread_bound(
            (central-3*sigma, central+3*sigma), known_correction_interval=(qed, qed)),
        "known_correction": qed,
        "uncertainty_scope": "reference covariance with the displayed QED central correction held fixed; no matching-theory error assigned",
        "production_parameters_updated": False,
    }
    result["comparison_input_keys"] = ["running_mass_reference", "charged_lepton_pole_reference"]
    if generated_lepton_matching is not None:
        match = generated_lepton_matching
        shift = match["weighted_one_loop_log_scale_derivative"]*math.log(
            reference["scale_GeV"]/match["scale_GeV"])
        prediction = match["charged_lepton_log_correction"]+shift
        source_bounds = match["charged_lepton_log_correction_interval"]
        bounds = [math.nextafter(source_bounds[0]+shift, -math.inf),
                  math.nextafter(source_bounds[1]+shift, math.inf)]
        result["generated_pole_lepton_test"] = {
            "input_definition": match["input_definition"],
            "production_scale_GeV": match["scale_GeV"],
            "comparison_scale_GeV": reference["scale_GeV"],
            "one_loop_near_scale_transfer": shift,
            "predicted_weighted_matching": prediction,
            "numerical_interval_at_comparison_scale": bounds,
            "numerical_interval_scope": "loop-kernel enclosure translated by the recorded fixed near-scale correction, with outward rounding; running and perturbative truncation errors are separate",
            "required_weighted_matching": central,
            "reference_standard_uncertainty": sigma,
            "required_minus_predicted": central-prediction,
            "uncomputed_orders": match["uncomputed_orders"],
            "theory_uncertainty_assigned": False,
            "comparison_significance_calculated": False,
            "scale_transfer_convention": "one-loop beta times log(Qref/Q); couplings fixed at the generated scale; coefficient running contributes at two loops",
            "production_parameters_updated": False,
        }
    return result


if __name__ == "__main__":
    init_sm_table()
    print("sm_rge/inputs OK")
