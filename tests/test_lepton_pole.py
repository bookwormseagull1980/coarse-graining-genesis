# -*- coding: utf-8 -*-
"""Tests for the charged-lepton geometric-to-pole fixed point."""

from pathlib import Path
import math
import sys

import pytest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cg_frg.fermion.lepton_pole import (  # noqa: E402
    charged_lepton_conversions,
    geometric_to_pole_one_loop,
    lepton_mass_vertex_response,
    solve_pole_mass,
)


LABELS = ("e", "mu", "tau")
GEOM = {"e": 0.5e-3, "mu": 0.105, "tau": 1.77}
SCHEME = "MSbar input at the stated scale; on-shell pole fixed point"
BOUNDARY = "generated charged-lepton vertex"


def test_zero_self_energy_is_tree_identification():
    result = solve_pole_mass(
        GEOM["e"], lambda _m: 0.0,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    assert result["G"] == pytest.approx(1.0, rel=1e-15)
    assert result["residual_GeV"] == pytest.approx(0.0, abs=1e-18)


def test_constant_relative_shift_reaches_exact_fixed_point():
    shift = 0.01
    result = solve_pole_mass(
        GEOM["mu"], lambda m: shift * m,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    expected = GEOM["mu"] / (1.0 - shift)
    assert result["pole_mass_GeV"] == pytest.approx(expected, rel=2e-13)
    assert result["G"] == pytest.approx(1.0 / (1.0 - shift), rel=2e-13)


@pytest.mark.parametrize("mass", [5e-9, 5e-4, .105, 1.77, 100.])
def test_fixed_point_precision_has_no_implicit_GeV_floor(mass):
    tolerance = 1e-12
    result = solve_pole_mass(
        mass, lambda m: .5 * m,
        scheme=SCHEME, scale_GeV=91., boundary_source=BOUNDARY,
        tolerance=tolerance)
    expected = 2 * mass
    assert abs(result["pole_mass_GeV"] / expected - 1) <= 2 * tolerance
    assert result["relative_step"] <= tolerance
    assert result["relative_residual"] <= tolerance
    actual_residual = result["pole_mass_GeV"] - (mass + .5 * result["pole_mass_GeV"])
    assert result["residual_GeV"] == actual_residual


def test_fixed_point_rejects_nonfinite_final_self_energy():
    mass = GEOM["e"]

    def shift(value):
        return mass * 1e-13 if value == mass else math.nan

    with pytest.raises(ValueError, match="non-finite shift"):
        solve_pole_mass(
            mass, shift, scheme=SCHEME, scale_GeV=91., boundary_source=BOUNDARY)


def test_common_conversion_cancels_in_delta_L():
    shift = 0.02
    self_energies = {k: (lambda m, s=shift: s * m) for k in LABELS}
    result = charged_lepton_conversions(
        GEOM, self_energies,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    for label in LABELS:
        assert result["leptons"][label]["G"] == pytest.approx(1.0 / 0.98, rel=1e-11)
    assert result["Delta_L"] == pytest.approx(0.0, abs=5e-12)
    assert result["nonuniversal_log_spread"] == pytest.approx(0.0, abs=5e-12)


def test_nonuniversal_conversion_has_expected_delta_L():
    shifts = {"e": 0.01, "mu": 0.02, "tau": 0.03}
    self_energies = {k: (lambda m, s=shifts[k]: s * m) for k in LABELS}
    result = charged_lepton_conversions(
        GEOM, self_energies,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    expected = math.log(1.0 / 0.99) * -1.0 \
        + math.log(1.0 / 0.98) * 2.0 \
        + math.log(1.0 / 0.97) * -1.0
    assert result["Delta_L"] == pytest.approx(expected, rel=1e-11)


def test_scheme_and_boundary_are_required():
    with pytest.raises(ValueError):
        solve_pole_mass(
            GEOM["e"], lambda _m: 0.0,
            scheme="", scale_GeV=91.0, boundary_source=BOUNDARY)
    with pytest.raises(ValueError):
        solve_pole_mass(
            GEOM["e"], lambda _m: 0.0,
            scheme=SCHEME, scale_GeV=91.0, boundary_source="")


def test_nonconvergent_or_negative_branch_is_rejected():
    with pytest.raises(RuntimeError):
        solve_pole_mass(
            GEOM["e"], lambda m: m,
            scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY,
            max_iterations=8)
    with pytest.raises(ValueError):
        solve_pole_mass(
            GEOM["e"], lambda m: -2.0 * m,
            scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)


@pytest.mark.parametrize("weights", [(1.0, 1.0, 1.0),
                                   (math.nan, 0.0, 0.0),
                                   (math.inf, -math.inf, 0.0)])
def test_weights_must_be_finite_and_sum_to_zero(weights):
    self_energies = {k: (lambda _m: 0.0) for k in LABELS}
    with pytest.raises(ValueError):
        charged_lepton_conversions(
            GEOM, self_energies,
            scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY,
            weights=weights)



def test_one_loop_geometric_to_pole_uses_existing_kernel():
    geometric = {
        "e": 0.0005103542513564916,
        "mu": 0.10531446305553036,
        "tau": 1.772105081689173,
    }
    result = geometric_to_pole_one_loop(
        geometric,
        [0.4615882289132695, 0.6482117683683781],
        246.18969645238943,
        higgs_mass_GeV=124.98344026878286,
        scale_GeV=91.12483998892053,
        input_scheme="MSbar_at_scale",
        action_source="generated five-coupling charged-lepton action",
    )
    assert result["iterations"] >= 1
    assert result["convergence"] <= 2e-10
    assert math.isfinite(result["Delta_L"])
    # The inverse of the independently evaluated first-order log conversion
    # has the opposite sign. The implicit mass equation retains higher terms.
    assert result["first_order"]["Delta_L"] == pytest.approx(
        -0.00933751775404148, abs=5e-15)
    assert result["implicit_minus_first_order_Delta_L"] == pytest.approx(
        -0.00050566271622846, abs=5e-13)
    assert result["generated_vertex_matching_derived"] is False
    assert result["production_replacement"] is False
    for label in LABELS:
        entry = result["leptons"][label]
        assert entry["G"] > 0.0
        assert abs(entry["running_residual"]) <= 2e-10


def test_one_loop_conversion_requires_declared_input_scheme():
    with pytest.raises(ValueError):
        geometric_to_pole_one_loop(
            GEOM,
            [0.46, 0.65],
            246.0,
            higgs_mass_GeV=125.0,
            scale_GeV=91.0,
            input_scheme="pole_mass_input",
            action_source="test action",
        )


@pytest.mark.parametrize("weights", [(math.nan, 0.0, 0.0),
                                   (math.inf, -math.inf, 0.0)])
def test_one_loop_conversion_rejects_nonfinite_weights(weights):
    with pytest.raises(ValueError, match="weights must be finite"):
        geometric_to_pole_one_loop(
            GEOM, [0.46, 0.65], 246.0,
            higgs_mass_GeV=125.0, scale_GeV=91.0,
            input_scheme="MSbar_at_scale", action_source="test action",
            weights=weights,
        )


def test_mass_vertex_response_in_canonical_coordinates():
    masses = np.array([.0005, .105, 1.77])
    vertex = np.diag(masses)
    db = np.diag(masses * [.01, -.02, .03])
    dl, dr = np.diag([.002, .004, .006]), np.diag([-.003, .005, -.007])
    result = lepton_mass_vertex_response(
        vertex, np.eye(3), np.eye(3), delta_mass_vertex_GeV=db,
        delta_left_gram=dl, delta_right_gram=dr, action_source="test action derivative")
    expected = np.array([.01, -.02, .03]) - .5 * (np.diag(dl) + np.diag(dr))
    np.testing.assert_allclose(list(result["dlog_masses"].values()), expected, atol=2e-17)
    assert result["weighted_log_response"] == pytest.approx(expected @ [-1, 2, -1], abs=3e-17)


def test_mass_vertex_response_with_noncommuting_kinetic_forms():
    from cg_core.matter_matching import canonical_vertex
    vertex = np.array([[.03, .01j, .002], [.004, .3, .02], [.006j, .01, 1.7]])
    left = np.array([[1.2, .1j, .02], [-.1j, .9, .03], [.02, .03, 1.1]])
    right = np.array([[.8, .04, 0], [.04, 1.3, -.05j], [0, .05j, 1.]])
    db = np.array([[.004, .002j, .001], [.003j, -.005, .002], [.001, .003, .007]])
    dl = np.array([[.02, .01j, .004], [-.01j, -.03, .002], [.004, .002, .01]])
    dr = np.array([[.03, -.006j, .001], [.006j, .01, .004], [.001, .004, -.02]])
    assert np.linalg.norm(left @ dl - dl @ left) > 1e-4
    result = lepton_mass_vertex_response(
        vertex, left, right, delta_mass_vertex_GeV=db,
        delta_left_gram=dl, delta_right_gram=dr, action_source="test noncommuting derivative")
    step = 2e-5
    plus = canonical_vertex(vertex + step*db, left + step*dl, right + step*dr, 1.)
    minus = canonical_vertex(vertex - step*db, left - step*dl, right - step*dr, 1.)
    np.testing.assert_allclose(result["delta_canonical_mass_vertex_GeV"],
                               (plus - minus) / (2*step), rtol=2e-7, atol=5e-11)
    log_plus = np.log(np.linalg.svd(plus, compute_uv=False)[::-1])
    log_minus = np.log(np.linalg.svd(minus, compute_uv=False)[::-1])
    np.testing.assert_allclose(list(result["dlog_masses"].values()),
                               (log_plus - log_minus) / (2*step), rtol=2e-7, atol=5e-11)
    # Transform raw action and both variations together, without refitting.
    a = np.array([[1., .2j, 0], [.1, 1.1, .05], [0, .1j, .9]])
    b = np.array([[.9, .03, .02j], [0, 1.2, .05], [.02, 0, 1.]])
    changed = lepton_mass_vertex_response(
        a.conj().T @ vertex @ b, a.conj().T @ left @ a, b.conj().T @ right @ b,
        delta_mass_vertex_GeV=a.conj().T @ db @ b,
        delta_left_gram=a.conj().T @ dl @ a, delta_right_gram=b.conj().T @ dr @ b,
        action_source="same action in changed coordinates")
    np.testing.assert_allclose(list(changed["dlog_masses"].values()),
                               list(result["dlog_masses"].values()), rtol=2e-11, atol=1e-14)


@pytest.mark.parametrize("direction, expected", [("vertex", 1.), ("left", -.5), ("right", -.5)])
def test_common_action_normalizations_cannot_change_lepton_invariant(direction, expected):
    vertex, identity, zero = np.diag([.0005, .105, 1.77]), np.eye(3), np.zeros((3, 3))
    result = lepton_mass_vertex_response(
        vertex, identity, identity,
        delta_mass_vertex_GeV=vertex if direction == "vertex" else zero,
        delta_left_gram=identity if direction == "left" else zero,
        delta_right_gram=identity if direction == "right" else zero,
        action_source="common normalization derivative")
    np.testing.assert_allclose(list(result["dlog_masses"].values()), expected, atol=2e-16)
    assert abs(result["weighted_log_response"]) < 2e-16


def test_mass_response_rejects_unresolved_labels_and_invalid_kinetic_variation():
    identity, zero = np.eye(3), np.zeros((3, 3))
    with pytest.raises(ValueError, match="distinct"):
        lepton_mass_vertex_response(
            identity, identity, identity, delta_mass_vertex_GeV=zero,
            delta_left_gram=zero, delta_right_gram=zero, action_source="degenerate test")
    with pytest.raises(ValueError, match="Hermitian"):
        lepton_mass_vertex_response(
            np.diag([.001, .1, 1.]), identity, identity, delta_mass_vertex_GeV=zero,
            delta_left_gram=np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]]),
            delta_right_gram=zero, action_source="invalid kinetic test")


@pytest.mark.parametrize("basepoint", [(0., 0., 0.), (.23, -.31, .19), (-.11, .17, .07)])
def test_native_source_transport_requires_complete_complement_feedback(basepoint):
    from scripts.diagnose_lepton_vertex_matching import native_frame_transport_diagnostic
    result = native_frame_transport_diagnostic((.0005, .105, 1.77), basepoint=basepoint)
    assert result["ambient_dimension"] == 44
    assert result["retained_dimension"] == 6
    assert result["full_mass_relative_residual"] < 1e-12
    assert result["transported_vertex_relative_residual"] < 1e-12
    assert result["schur_projected_resolvent_relative_residual"] < 1e-12
    assert max(result["schur_nonzero_spectral_position_relative_residuals"]) < 1e-11
    assert result["transfer_weights_changed"] is False
    assert result["generated_source_loop_correction_computed"] is False
    if any(basepoint):
        # A sizeable change from a frozen subspace disappears when its
        # complement is eliminated exactly. It cannot be used as Delta_C.
        assert result["fixed_subspace_apparent_log_shift"] > .01
        assert result["complement_feedback_norm_GeV2"] > 0
    else:
        assert abs(result["fixed_subspace_apparent_log_shift"]) < 1e-13


@pytest.mark.store
def test_current_native_lepton_diagnostic_keeps_references_separate():
    from cg_core.params import prediction_inputs_only
    from comparison.lepton_vertex_matching import compare_lepton_vertex_matching
    from scripts.diagnose_lepton_vertex_matching import evaluate_lepton_vertex_diagnostic
    result = evaluate_lepton_vertex_diagnostic()
    assert result["geometric_identity_residual"] == pytest.approx(0., abs=2e-15)
    assert result["native_source"]["ambient_dimension"] == 44
    np.testing.assert_allclose(result["native_source"]["canonical_mass_singular_values_GeV"],
                               list(result["geometric_masses_GeV"].values()), rtol=2e-14)
    assert result["native_source"]["complement_mass_vertex_norm_GeV"] < 1e-14
    transport = result["native_frame_transport"]
    assert transport["full_mass_relative_residual"] < 1e-12
    assert max(transport["schur_nonzero_spectral_position_relative_residuals"]) < 1e-11
    np.testing.assert_allclose(list(result["family_projector_weighted_sensitivities"].values()),
                               [-1., 2., -1.], atol=3e-14)
    assert result["lepton_transfer_directions"]["common_rung_alpha"]["weighted_log_response"] == pytest.approx(0., abs=3e-14)
    assert result["lepton_transfer_directions"]["light_period"]["weighted_log_response"] == pytest.approx(1., abs=3e-14)
    kernel = result["pole_to_MSbar"]
    assert abs(kernel["photon_log_invariant_identity_residual"]) < 3e-17
    assert sum(kernel["weighted_log_components"].values()) == pytest.approx(
        kernel["Delta_D_first_order"], abs=5e-17)
    common = result["common_action_two_point"]
    assert abs(common["on_shell_recombination_residual"]) < 3e-17
    assert common["on_shell"]["generated_action_factors"]["direct_one_loop_colour_self_energy_zero"]
    assert common["generated_source_excess_computed"] is False
    for terms in common["spacelike_shared_terms_to_subtract"].values():
        assert all(math.isfinite(x) for x in terms.values())
    comparison = compare_lepton_vertex_matching(result)
    assert comparison["required_Delta_C_first_order_at_generated_mass_arguments"] == pytest.approx(
        comparison["required_Delta_pole"] + kernel["Delta_D_first_order"], abs=1e-17)
    with prediction_inputs_only(), pytest.raises(ValueError, match="observational"):
        compare_lepton_vertex_matching(result)

