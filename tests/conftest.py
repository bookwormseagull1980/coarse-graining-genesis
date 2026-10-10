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

"""Shared pytest configuration: make the framework importable from tests/.

The framework modules use sys.path insertion relative to the project
root; tests run from the repository root, so adding the root to
sys.path makes both `cg_core` and `cg_frg` importable.
"""
import sys
from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# Extended verification uses independent quadrature, interval arithmetic,
# cutoff refinement or complete response examples. Selection concerns the
# work performed, not measured execution time. The full suite includes all
# these checks; the core suite omits this explicitly declared group.
_NUMERICAL_MODULES = {
    "test_spectral_contracts.py", "test_response_domains.py",
    "test_matter_source_response.py", "test_native_matter_matching.py",
}
_NUMERICAL_CASES = {
    "test_matter_extensions.py": {
        "test_lepton_matching_analytic_intervals_against_independent_integrals",
        "test_coupled_actual_beta_semigroup_and_boundary_residual",
        "test_qcd_finite_mass_matching_from_self_energy_integral",
        "test_decay_phase_space_regular_quadrature_and_threshold",
        "test_beta_phase_space_derivatives_against_analytic_born_integral",
        "test_joint_bbn_jacobian_matches_independent_full_chain_differences",
        "test_joint_bbn_shared_mass_matching_and_rate_directions",
        "test_joint_bbn_retains_scalar_centre_and_reuses_its_partition",
        "test_complete_capture_from_independent_conserved_neutron_proton_evolution",
        "test_thermal_equation_of_state_limits_and_evolution",
        "test_sourced_reaction_network_against_exact_capture_solution",
        "test_thermal_quadrature_convergence_is_required",
        "test_nuclear_evolution_keeps_free_weak_conversion_active",
        "test_fermi_readout_matching_preserves_weak_amplitude_series",
        "test_pole_two_point_integral_against_complex_parameter_integral",
        "test_generated_on_shell_inverse_conditions_and_reused_weak_kernel",
    },
    "test_propagation.py": {
        "test_actual_disk_source_weak_identity",
        "test_weak_source_decomposition_scales_with_the_solved_model",
        "test_characteristic_evolution_matches_growing_solution_and_stops_at_crossing",
        "test_nonlinear_plane_field_energy_and_actual_variational_force",
        "test_plane_feedback_mass_energy_and_time_step_convergence",
        "test_plane_feedback_time_dependent_boundary_work",
        "test_plane_feedback_zero_gradient_and_crossing_guard",
        "test_covariant_clock_conserved_charge_against_eds_exact_solution",
        "test_covariant_clock_dust_vacuum_background_and_effective_density",
    },
    "test_gravity_extensions.py": {
        "test_non_spherical_manufactured_grid_convergence",
        "test_regularization_limit", "test_zero_and_affine_boundary",
        "test_spherical_smooth_source_limit",
    },
    "test_numeric_contracts.py": {
        "test_observed_fourth_order_for_actual_gauge_flow",
        "test_reciprocal_variable_independent_solver",
    },
    "test_joint_response.py": {
        "test_finite_lepton_transfer_against_three_independent_running_equations",
        "test_finite_lepton_interval_is_outward_and_rejects_an_uncertified_denominator",
    },
}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    for item in items:
        module = item.path.name
        name = getattr(item, "originalname", None) or item.name.split("[", 1)[0]
        if module in _NUMERICAL_MODULES or name in _NUMERICAL_CASES.get(module, ()):
            item.add_marker(pytest.mark.numerical)
        if module == "test_reviewer_dashboard.py":
            item.add_marker(pytest.mark.auxiliary)
