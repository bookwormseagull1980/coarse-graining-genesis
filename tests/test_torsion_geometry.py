"""Action derivatives, moving spectral boundaries and common stationarity."""
import math
from fractions import Fraction as Q

import mpmath as mp
import numpy as np
import pytest

from cg_core.window_weights import ResponseDomain
from cg_core.rational_interval import Interval as I, GRID, log_positive
from cg_frg.ewsb.torsion_response import fermion_window_response
from cg_frg.ewsb.torsion_geometry import (
    _reference_jet, fermion_geometry_response, torsion_geometry_response,
    trace_matched_curvature_response, solve_joint_window_saddle,
    certify_joint_window_saddle,
    content_fixed_geometry_response, solve_content_fixed_radius,
    certify_content_fixed_radius,
)


@pytest.mark.parametrize("z", (1e-8, .02, .05, .1, 2., 6.))
def test_reference_propagator_derivatives_against_high_precision(z):
    ctx = mp.mp.clone()
    ctx.dps = 55
    point = ctx.mpf(str(z))
    f = lambda x: x/(1-ctx.exp(-x))
    expected = (f(point), ctx.diff(f, point), ctx.diff(f, point, 2))
    np.testing.assert_allclose(_reference_jet(z, 1.), list(map(float, expected)),
                               atol=3e-13, rtol=2e-12)


@pytest.mark.parametrize("tau,length", ((-.08, 1.8), (.02, 2.4935343325226915)))
def test_two_variable_jets_differentiate_the_same_volume_integrated_action(tau, length):
    opts = dict(scale=1., generations=1)
    center = fermion_geometry_response(tau, radius=length, **opts)
    # Perturb two independent coordinates, retaining the moving endpoints.
    step = 3e-6
    for index in (0, 1):
        plus = fermion_geometry_response(tau+(step if index == 0 else 0),
                                         radius=length*math.exp(step if index == 1 else 0), **opts)
        minus = fermion_geometry_response(tau-(step if index == 0 else 0),
                                          radius=length*math.exp(-step if index == 1 else 0), **opts)
        for key in ("full", "reference", "relative"):
            first = (plus[key]["integrated_action"]-minus[key]["integrated_action"])/(2*step)
            assert first == pytest.approx(center[key]["integrated_gradient"][index],
                                          rel=2e-7, abs=2e-8)
            second = (np.array(plus[key]["integrated_gradient"])
                      -np.array(minus[key]["integrated_gradient"]))/ (2*step)
            np.testing.assert_allclose(second, np.array(center[key]["integrated_hessian"])[:, index],
                                       rtol=1e-6, atol=1e-7)


def test_reference_and_relative_actions_recover_full_action_and_boundary_force():
    data = fermion_geometry_response(.02, radius=2., scale=1., generations=1)
    for key in data["full"]:
        np.testing.assert_allclose(data["full"][key],
                                   np.array(data["reference"][key])+np.array(data["relative"][key]),
                                   atol=3e-13, rtol=2e-13)
    previous = fermion_window_response(.02, radius=2., scale=1., generations=1)
    assert data["relative"]["density"] == pytest.approx(previous["relative_action"], abs=1e-15)
    assert data["relative"]["density_gradient"][0] == pytest.approx(previous["tau_current"], abs=1e-15)
    assert data["relative"]["density_hessian"][0][0] == pytest.approx(previous["tau_curvature"], abs=1e-15)
    for name in ("full", "reference", "relative"):
        row = data[name]
        assert row["density_radius_bulk"]+row["density_radius_boundary"] == pytest.approx(
            row["density_gradient"][1], rel=2e-13, abs=1e-13)
        assert row["integrated_radius_bulk"]+row["integrated_radius_boundary"] == pytest.approx(
            row["integrated_gradient"][1], rel=2e-13, abs=1e-13)
    assert data["full"]["integrated_radius_boundary"] != 0


def test_independent_frequency_integral_includes_the_actual_leibniz_edge():
    # Reconstruct every signed shell and its moving frequency interval in
    # a separate high-precision context, without u-coordinate derivatives.
    ctx = mp.mp.clone()
    ctx.dps = 45
    tau, length, level = map(ctx.mpf, ("0.02", "2", "5"))

    def action(eta):
        l = length*ctx.exp(eta)
        value = ctx.mpf(0)
        n = 0
        while ((n+ctx.mpf('1.5'))/l)**2 < level:
            d = (-1)**n*(n+ctx.mpf('1.5'))/l
            width = ctx.sqrt(level-d*d)
            def integrand(w):
                z = w*w+d*d
                den = z/(1-ctx.exp(-z))+(d-3*tau/(4*l))**2-d*d
                return -ctx.log(den)
            value += 8*(n+1)*(n+2)/ctx.pi*ctx.quad(integrand, [0, width])
            n += 1
        return value

    expected = ctx.diff(action, ctx.mpf(0))
    row = fermion_geometry_response(float(tau), radius=float(length), scale=1.,
                                    generations=1)["full"]
    assert row["integrated_gradient"][1] == pytest.approx(float(expected), rel=2e-13)
    assert abs(row["integrated_radius_bulk"]-float(expected)) > 1  # edge cannot be omitted


def test_zero_torsion_keeps_the_reference_geometry_force():
    data = fermion_geometry_response(0., radius=2., scale=1., generations=1)
    assert data["relative"]["density"] == 0
    assert data["relative"]["integrated_gradient"][1] == 0
    assert data["reference"]["integrated_gradient"][1] != 0
    assert data["full"]["integrated_gradient"][1] == data["reference"]["integrated_gradient"][1]
    assert data["relative"]["integrated_gradient"][0] != 0  # torsion source is differentiated


def test_volume_measure_and_curvature_completion_are_varied_before_stationarity():
    tau, length, step = .03, 1.8, 3e-6
    opts = dict(scale=1., generations=1)
    data = trace_matched_curvature_response(tau, radius=length, **opts)
    assert data["trace_matched_curvature_coefficient"] == 3
    assert data["lc_geometry"]["integrated_action"] == pytest.approx(18*math.pi**2*length)
    for index in (0, 1):
        plus = trace_matched_curvature_response(tau+(step if index == 0 else 0),
                                                radius=length*math.exp(step if index == 1 else 0), **opts)
        minus = trace_matched_curvature_response(tau-(step if index == 0 else 0),
                                                 radius=length*math.exp(-step if index == 1 else 0), **opts)
        for key in ("common", "curvature_completed"):
            first = (plus[key]["integrated_action"]-minus[key]["integrated_action"])/(2*step)
            assert first == pytest.approx(data[key]["integrated_gradient"][index],
                                          rel=2e-7, abs=2e-8)
            column = (np.array(plus[key]["integrated_gradient"])
                      -np.array(minus[key]["integrated_gradient"]))/ (2*step)
            np.testing.assert_allclose(column, np.array(data[key]["integrated_hessian"])[:, index],
                                       atol=2e-7, rtol=1e-6)
    bare = data["bare_torsion"]
    assert bare["integrated_gradient"][1] == pytest.approx(bare["integrated_action"])
    assert bare["density_gradient"][1] == pytest.approx(-2*bare["density"])


def test_independent_connection_comparison_keeps_the_content_value_separate():
    data = solve_joint_window_saddle(radius_bracket=(1.65, 1.95), scale=1., generations=3)
    np.testing.assert_allclose(data["integrated_gradient"], 0, atol=1e-7)
    assert data["tau_estimate"] != pytest.approx(1/50, rel=.1)
    assert 1.65 < data["radius_estimate"] < 1.95
    assert min(abs(x) for x in data["hessian_eigenvalues"]) > 1e-3
    assert data["neutral_reference_multiplicity"] > 0
    assert abs(data["relative_only_radius_force"]) > 1
    assert not data["interval_existence_or_uniqueness_certificate"]


def test_content_pullback_differentiates_the_same_action_without_a_schur_elimination():
    length, step = 1.8, 3e-6
    opts = dict(scale=1., generations=1)
    data = content_fixed_geometry_response(radius=length, **opts)
    assert data["content_balance"]["tau_content"] == Q(1, 50)
    assert data["tau_content_exact"] == "1/50"
    restricted = data["content_fixed"]
    plus = trace_matched_curvature_response(.02, radius=length*math.exp(step), **opts)
    minus = trace_matched_curvature_response(.02, radius=length*math.exp(-step), **opts)
    pj, mj = plus["curvature_completed"], minus["curvature_completed"]
    first = (pj["integrated_action"]-mj["integrated_action"])/(2*step)
    second = (pj["integrated_gradient"][1]-mj["integrated_gradient"][1])/(2*step)
    assert first == pytest.approx(restricted["integrated_gradient"], rel=3e-7)
    assert second == pytest.approx(restricted["integrated_hessian"], rel=3e-7)
    assert abs(restricted["ambient_connection_derivative"]) > 1
    assert abs(restricted["connection_elimination_correction"]) > 1
    assert restricted["integrated_hessian"] == data["curvature_completed"]["integrated_hessian"][1][1]
    with pytest.raises(TypeError):
        content_fixed_geometry_response(tau=.1, radius=length, **opts)


def test_fixed_content_radius_solution_and_exact_interval_certificate():
    result = solve_content_fixed_radius(radius_bracket=(1.65, 1.95), scale=1.)
    assert result["tau_content_exact"] == "1/50"
    assert result["radius_estimate"] == pytest.approx(1.7996569055591913, abs=1e-10)
    assert abs(result["content_fixed"]["integrated_gradient"]) < 1e-7
    assert result["content_fixed"]["integrated_hessian"] > 3000
    assert result["content_fixed"]["ambient_connection_derivative"] > 10
    assert abs(result["frequency_boundary_radius_force"]) > 500
    certificate = certify_content_fixed_radius(
        radius_interval=(1.794, 1.805), scale=1., cells=256)
    assert certificate["tau_content_exact"] == "1/50"
    assert certificate["opposite_endpoint_signs"]
    assert certificate["positive_restricted_curvature"]
    assert certificate["unique_restricted_radius_minimum_certified"]
    assert float(certificate["restricted_radius_hessian"][0]) > 900
    # A nonzero normal derivative is consistent with the restricted
    # minimum, and must not be reported as zero by the certificate.
    assert float(certificate["ambient_connection_derivative"][0]) > 10
    unresolved = certify_content_fixed_radius(
        radius_interval=(1.79965, 1.79966), scale=1., cells=8)
    assert not unresolved["unique_restricted_radius_minimum_certified"]


@pytest.mark.parametrize("low,high", ((Q(1, 10**12), Q(1, 7)), (Q(1), Q(1)),
                                     (Q(5, 4), Q(7)), (Q(2**100), Q(2**101))))
def test_rational_logarithm_encloses_high_precision_endpoints(low, high):
    ctx = mp.mp.clone()
    ctx.dps = 75
    bound = log_positive(I.bounds(low, high))
    for value in (low, (low+high)/2, high):
        expected = ctx.log(ctx.mpf(value.numerator)/value.denominator)
        assert ctx.mpf(bound.lo)/GRID <= expected <= ctx.mpf(bound.hi)/GRID
    with pytest.raises(ValueError):
        log_positive(I.bounds(-1, 2))


def test_outward_newton_map_proves_joint_existence_and_uniqueness():
    result = certify_joint_window_saddle(
        tau_interval=(.111, .122), radius_interval=(1.790, 1.801), scale=1.,
        generations=3, cells=256, center=(.11619682549993063, 1.7956264727915705))
    assert result["newton_image_strictly_inside"]
    assert result["strict_contraction"]
    assert result["unique_joint_stationary_point_certified"]
    assert float(result["contraction_norm_bound"][1]) < .14
    assert result["one_negative_one_positive_direction_certified"]
    assert float(result["reduced_radius_curvature_box"][0]) > 900
    # Check the box Hessian against independently evaluated analytic jets
    # at separated parameter corners, using the proper L-coordinate change.
    for tau, length in ((.111, 1.790), (.122, 1.801), (.111, 1.801)):
        row = trace_matched_curvature_response(tau, radius=length, scale=1.)["curvature_completed"]
        h = np.array(row["integrated_hessian"])
        g = row["integrated_gradient"][1]
        hl = [[h[0, 0], h[0, 1]/length], [h[1, 0]/length, (h[1, 1]-g)/length**2]]
        for i, j in np.ndindex((2, 2)):
            lo, hi = map(float, result["hessian_box"][i][j])
            assert lo <= hl[i][j] <= hi


def test_unresolved_interval_inclusion_is_not_reported_as_a_proof():
    result = certify_joint_window_saddle(
        tau_interval=(.1161968, .1161969), radius_interval=(1.7956264, 1.7956265),
        scale=1., cells=8)
    assert not result["newton_image_strictly_inside"]
    assert not result["unique_joint_stationary_point_certified"]


@pytest.mark.parametrize("call", (
    lambda: fermion_geometry_response(.02, radius=1.5/math.sqrt(5), scale=1.),
    lambda: fermion_geometry_response(.02, radius=2., scale=1., domain=ResponseDomain(5, 'moving')),
    lambda: torsion_geometry_response(.25, radius=2., scale=1.),
    lambda: solve_joint_window_saddle(radius_bracket=(1.8, 2.1), scale=1.),
    lambda: solve_joint_window_saddle(radius_bracket=(2., 1.), scale=1.),
    lambda: solve_content_fixed_radius(radius_bracket=(1.8, 2.1), scale=1.),
    lambda: certify_content_fixed_radius(radius_interval=(1.7, 1.7), scale=1.),
    lambda: certify_content_fixed_radius(radius_interval=(1.5, 1.8), scale=1.),
    lambda: certify_joint_window_saddle(tau_interval=(.001, .02), radius_interval=(.4, .5),
                                        center=(.01, .45), scale=1., domain=ResponseDomain(9), cells=2),
))
def test_invalid_data_and_shell_crossing_are_explicit(call):
    with pytest.raises(ValueError):
        call()
