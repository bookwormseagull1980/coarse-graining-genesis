"""Independent variations and continuous-integral checks of the common action."""
from fractions import Fraction as Q
import math

import mpmath as mp
import numpy as np
import pytest

from cg_core.ec_variation import (
    eliminate_minimal_trace_torsion, eliminate_auxiliary_hessian,
    minimal_coupled_action_variation, production_torsion_variation,
)
from cg_core.rational_interval import GRID
from cg_core.window_weights import ResponseDomain
from cg_frg.ewsb.torsion_response import (
    fermion_window_response, certify_fermion_window_response,
    torsion_window_action, solve_torsion_window, torsion_matrix_window_action,
)


@pytest.mark.parametrize("rho", (Q(0), Q(-6, 25), Q(2, 7)))
@pytest.mark.parametrize("length", (Q(1), Q(7, 3)))
def test_exact_auxiliary_completion_against_tensor_action(rho, length):
    coefficients = (Q(1, 4), Q(1), -Q(7, 12))
    result = eliminate_minimal_trace_torsion(rho, radius=length, coefficients=coefficients)
    assert result["induced_four_fermion_coefficient"] == Q(1, 32)
    assert result["trace_equation_residual"] == 0
    assert result["content_dimension"] == 16
    stationary = result["stationary_tau"]
    for tau in (Q(-1, 5), Q(0), Q(1, 50)):
        original = -Q(9, 2)*tau*tau/length**2-3*tau*rho/(4*length)
        square = result["completed_square_coefficient"]*(tau-stationary)**2
        assert original == square+result["induced_interaction"]
    # Compare the original all-nine-direction action, not its scalar rewrite.
    ket, bra = np.zeros(32), np.zeros(32)
    ket[31], bra[31] = 1., float(rho)  # neutral content coordinate is retained
    full = minimal_coupled_action_variation(
        float(stationary/length)*np.eye(3), ket, bra,
        np.zeros((32, 32)), coefficients)
    assert full["action"] == pytest.approx(float(result["induced_interaction"]), abs=1e-15)
    np.testing.assert_allclose(full["torsion_gradient"], 0, atol=1e-15)


def test_auxiliary_elimination_does_not_require_positive_auxiliary_hessian():
    h = np.array([[-3., 2., 1.], [2., 4., .2], [1., .2, 2.]])
    result = eliminate_auxiliary_hessian(h, (0,))
    assert min(result["reduced_eigenvalues"]) > 0
    for x in (np.array([.2, -.7]), np.array([1., 3.])):
        a = result["auxiliary_response"]@x
        state = np.r_[a, x]
        assert (h@state)[0] == pytest.approx(0, abs=1e-14)
        assert state@h@state == pytest.approx(x@result["reduced_hessian"]@x)
    with pytest.raises(np.linalg.LinAlgError):
        eliminate_auxiliary_hessian(np.diag([0., 1.]), (0,))


@pytest.mark.parametrize("tau", (-.12, 0., .02, .15))
def test_action_current_curvature_are_variations_of_the_same_determinant(tau):
    options = dict(radius=2., scale=1., generations=1)
    h = 2e-5
    center = fermion_window_response(tau, **options)
    plus = fermion_window_response(tau+h, **options)
    minus = fermion_window_response(tau-h, **options)
    assert (plus["relative_action"]-minus["relative_action"])/(2*h) == pytest.approx(
        center["tau_current"], rel=2e-8, abs=1e-11)
    assert (plus["tau_current"]-minus["tau_current"])/(2*h) == pytest.approx(
        center["tau_curvature"], rel=2e-8, abs=1e-11)
    assert center["matter_bilinear"] == pytest.approx(-4*options["radius"]*center["tau_current"]/3)
    assert center["neutral_tau_current"] != 0
    assert all(mode["neutral_degeneracy"] > 0 for mode in center["modes"] if mode["shell"] % 2 == 0)
    assert any("nu_R" in mode["content_labels"] for mode in center["modes"])


def _independent_integrals(tau, length, scale, level, generations):
    # Rebuild the determinant/current from the two chiral multiplicities and
    # the continuum frequency integral in an independent high-precision context.
    ctx = mp.mp.clone()
    ctx.dps = 45
    t, l, k, r = map(lambda x: ctx.mpf(str(x)), (tau, length, scale, level))
    total_j, total_h = ctx.mpf(0), ctx.mpf(0)
    n = 0
    while ((ctx.mpf(n)+ctx.mpf('1.5'))/l)**2 < r*k*k:
        d = (-1 if n % 2 else 1)*(ctx.mpf(n)+ctx.mpf('1.5'))/l
        lam, v = d*d, 3/(4*l)
        omega = ctx.sqrt(r*k*k-lam)
        multiplicity = 8*generations*(n+1)*(n+2)
        delta = (d-v*t)**2-lam
        first, second = -2*v*(d-v*t), 2*v*v
        def den(u):
            z = lam+omega*omega*u*u
            return z+z/ctx.expm1(z/(k*k))+delta
        coefficient = multiplicity*omega/(ctx.pi**3*l**3)
        total_j += coefficient*ctx.quad(lambda u: -first/den(u), [0, 1])
        total_h += coefficient*ctx.quad(lambda u: first**2/den(u)**2-second/den(u), [0, 1])
        n += 1
    return total_j, total_h


@pytest.mark.parametrize("tau", (-.15, .02, .18))
def test_rational_certificates_enclose_independent_continuous_integrals(tau):
    options = dict(radius=2., scale=1., generations=1, domain=ResponseDomain(5.))
    j, h = certify_fermion_window_response((tau, tau), cells=64, **options)
    expected_j, expected_h = _independent_integrals(tau, 2., 1., 5., 1)
    ctx = mp.mp.clone()
    ctx.dps = 50
    for bound, expected in ((j, expected_j), (h, expected_h)):
        assert ctx.mpf(bound.lo)/GRID <= expected <= ctx.mpf(bound.hi)/GRID
    # Also check a whole parameter interval, not only pointwise quadrature.
    ji, hi = certify_fermion_window_response((-.15, .18), cells=64, **options)
    assert ji.lo <= j.lo <= j.hi <= ji.hi
    assert hi.lo <= h.lo <= h.hi <= hi.hi


def test_generated_fermion_count_and_trace_normalization():
    one = fermion_window_response(.02, radius=2., scale=1., generations=1)
    three = fermion_window_response(.02, radius=2., scale=1., generations=3)
    for key in ("relative_action", "tau_current", "tau_curvature", "neutral_tau_current"):
        assert three[key] == pytest.approx(3*one[key], rel=2e-14)
    assert one["content_dimension_per_generation"] == 16
    for row in one["modes"]:
        n = row["shell"]
        assert row["degeneracy"] == 8*(n+1)*(n+2)


def test_common_ec_fermion_action_uses_actual_derivative_and_no_quartic_reconstruction():
    options = dict(radius=2., scale=1., generations=1)
    tau, step = .02, 2e-5
    center = torsion_window_action(tau, **options)
    plus, minus = (torsion_window_action(tau+d, **options) for d in (step, -step))
    assert (plus["relative_action"]-minus["relative_action"])/(2*step) == pytest.approx(
        center["stationarity_residual"], abs=2e-11)
    assert (plus["stationarity_residual"]-minus["stationarity_residual"])/(2*step) == pytest.approx(
        center["tau_hessian"], abs=2e-10)
    expected = production_torsion_variation()["isotropic_hessian"]
    assert center["bare_tau_hessian"] == pytest.approx(float(expected)/4)


def test_all_nine_torsion_variations_of_the_same_gaussian_action():
    from cg_core.ec_variation import torsion_invariants
    options = dict(radius=2., scale=1., generations=1)
    b = np.array([[.012, .017, -.011], [-.009, -.007, .021], [.003, -.013, .008]])
    data = torsion_matrix_window_action(b, **options)
    # Build the action independently from tensor contractions and the
    # determinant's actual trace vertex, without irreducible projectors.
    def action(point):
        scalar = sum(c*i for c, i in zip((.25, 1., -7/12), torsion_invariants(point)))
        tau = options["radius"]*np.trace(point)/3
        return scalar+fermion_window_response(tau, **options)["relative_action"]
    step = 2e-6
    for i, j in np.ndindex((3, 3)):
        delta = np.zeros((3, 3))
        delta[i, j] = step
        first = (action(b+delta)-action(b-delta))/(2*step)
        assert first == pytest.approx(data["dual_torsion_gradient"][i, j], abs=2e-10)
        gp = torsion_matrix_window_action(b+delta, **options)["dual_torsion_gradient"]
        gm = torsion_matrix_window_action(b-delta, **options)["dual_torsion_gradient"]
        np.testing.assert_allclose(((gp-gm)/(2*step)).reshape(9),
                                   data["dual_torsion_hessian"][:, 3*i+j], atol=2e-9, rtol=1e-8)
    expected = sorted(v for v, m in zip(data["auxiliary_eigenvalues"], (1, 3, 5)) for _ in range(m))
    np.testing.assert_allclose(np.linalg.eigvalsh(data["dual_torsion_hessian"]), expected, atol=1e-14)
    np.testing.assert_allclose(data["dual_torsion_hessian"], data["dual_torsion_hessian"].T, atol=0)
    assert data["content_dimension_per_generation"] == 16


def test_window_saddle_certificate_or_explicit_failure_to_certify():
    result = solve_torsion_window(radius=2., scale=1., generations=1, cells=128)
    assert result["strict_monotonicity_certified"]
    assert result["unique_root_certified"]
    lo, hi = map(float, result["root_enclosure"])
    assert lo <= result["root_estimate"] <= hi
    assert result["at_root"]["stationarity_residual"] == pytest.approx(0, abs=1e-11)
    assert result["gauge_tau_stationarity_excluded"]
    assert result["at_root"]["tau_hessian"] < 0  # auxiliary saddle, not a physical tachyon test
    full = result["nine_component_stationarity"]
    assert full["unique_stationary_point_certified"]
    assert (full["positive_directions_certified"], full["negative_directions_certified"]) == (8, 1)
    assert full["transverse_hessian_eigenvalues"] == ["2/3", "3"]
    b = result["root_estimate"]/2*np.eye(3)
    data = torsion_matrix_window_action(b, radius=2., scale=1., generations=1)
    np.testing.assert_allclose(data["dual_torsion_gradient"], 0, atol=1e-11)
    assert data["relative_action"] == pytest.approx(result["at_root"]["relative_action"], abs=1e-14)


@pytest.mark.parametrize("call", (
    lambda: eliminate_minimal_trace_torsion(1, radius=0, coefficients=(1, 2, 3)),
    lambda: eliminate_minimal_trace_torsion(1, radius=1, coefficients=(1, 1, 3)),
    lambda: eliminate_auxiliary_hessian(np.eye(2), (0, 0)),
    lambda: fermion_window_response(.25, radius=2., scale=1.),
    lambda: fermion_window_response(.02, radius=2., scale=1., domain=ResponseDomain(5., 'moving')),
    lambda: certify_fermion_window_response((.1, -.1), radius=2., scale=1.),
    lambda: solve_torsion_window(radius=2., scale=1., bracket=(.1, -.1)),
))
def test_invalid_action_data_are_rejected(call):
    with pytest.raises((ValueError, ZeroDivisionError)):
        call()
