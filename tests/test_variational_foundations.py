"""Action derivatives, complete-carrier traces and zero-mode matching.

These checks compare actual matrix contractions or independent variations.
In particular they reject identifying a neutral gauge vertex with a neutral
spin vertex, or a profile maximum with an effective-action stationary point.
"""
from fractions import Fraction as Q
import math

import numpy as np
import pytest
from scipy.linalg import expm

from cg_core.ec_variation import (
    full_carrier_response, full_source_matrices, minimal_spin_connection_vertex,
    neutral_connector_schur, production_torsion_variation,
    quadratic_torsion_coefficients, torsion_invariants,
    minimal_internal_torsion_vertices, solve_algebraic_torsion,
    production_torsion_sector_contract,
    minimal_torsion_spectral_terms, minimal_coupled_action_variation,
    minimal_classical_stationarity,
)
from cg_frg.frg.endpoint_variation import (
    survival_stationary_geometry, gaussian_mode_action,
    gaussian_mode_action_derivative, mass_stationarity_terms,
    four_dimensional_loop_measure,
)
from cg_frg.gauge.zero_mode_reduction import (
    zero_mode_action, gauge_scale_factor, killing_coupling_squared,
    required_seven_dimensional_coefficient, register_gauge_scale_factor,
)


def test_full_carrier_projection_traces_and_response():
    result = full_carrier_response()
    assert result["dimension"] == 16
    assert result["gauge_support_rank"] == 15
    assert result["neutral_labels"] == ("nu_R",)
    assert result["center_trace"] == 0
    assert result["projected_center_trace"] == 1
    assert result["hypercharge_second_moment"] == Q(10, 3)
    assert result["gauge_conditioned_tau"] == Q(1, 50)
    assert result["unconditioned_center_response"] == 0
    assert result["projected_current_full_state_response"] == Q(3, 160)
    chi, y, *_ = full_source_matrices()
    p = np.diag(np.array(result["gauge_support_diagonal"], float))
    np.testing.assert_allclose(p@p, p, atol=1e-15)
    np.testing.assert_allclose(p@y, y, atol=1e-15)
    assert np.trace(p@chi).real == 1
    # A simultaneous basis change cannot change this response or select a
    # different neutral line. Compute the support anew in the changed basis.
    rng = np.random.default_rng(32)
    u, _ = np.linalg.qr(rng.normal(size=(16, 16))+1j*rng.normal(size=(16, 16)))
    yu, cu = u@y@u.conj().T, u@chi@u.conj().T
    eigenvalues, eigenvectors = np.linalg.eigh(yu@yu)
    pu = eigenvectors[:, eigenvalues > 1e-12] @ eigenvectors[:, eigenvalues > 1e-12].conj().T
    tau = np.trace(pu@cu)/(np.trace(pu)*np.trace(yu@yu))
    assert tau == pytest.approx(.02, abs=2e-14)


def test_full_log_partition_hessian_includes_neutral_coordinate():
    chi, y, *_ = full_source_matrices()
    result = full_carrier_response()
    eps = 3e-4
    def log_z(generator, h):
        return math.log(np.trace(expm(h*generator)).real/16)
    for generator, expected in ((chi, result["full_center_hessian"]),
                                 (y, result["full_hypercharge_hessian"])):
        second = (log_z(generator, eps)+log_z(generator, -eps))/eps**2
        assert second == pytest.approx(float(expected), rel=3e-7)


def test_clifford_variation_has_nonzero_neutral_spin_vertex():
    data = minimal_spin_connection_vertex()
    gammas = data["gammas"]
    for i, a in enumerate(gammas):
        for j, b in enumerate(gammas):
            np.testing.assert_allclose(a@b+b@a, 2*np.eye(4) if i == j else np.zeros((4, 4)))
    vertex = data["spin_vertex"]
    np.testing.assert_allclose(vertex, vertex.conj().T)
    np.testing.assert_allclose(vertex@vertex, np.eye(4)/16)
    assert np.linalg.norm(data["neutral_vertex"]) == pytest.approx(.5)
    full = np.kron(data["content_vertex"], vertex)
    np.testing.assert_allclose(full[-4:, -4:], vertex)


def test_actual_neutral_schur_feedback_is_nonzero():
    result = neutral_connector_schur()
    assert result["neutral_coupling_norm"] == pytest.approx(1)
    assert result["schur_feedback_norm"] == pytest.approx(1)
    assert np.linalg.matrix_rank(result["schur_feedback"]) == 1
    assert np.linalg.norm(result["resolvent_difference"]) < 2e-14


@pytest.mark.parametrize("seed", range(5))
def test_three_invariant_classification_against_tensor_contraction(seed):
    rng = np.random.default_rng(seed)
    b = rng.integers(-4, 5, size=(3, 3)).astype(object)
    b = np.array([[Q(int(x)) for x in row] for row in b], object)
    trace = sum(b[i, i] for i in range(3))
    isotropic = np.eye(3, dtype=object)*trace/3
    antisymmetric = (b-b.T)/2
    traceless = (b+b.T)/2-isotropic
    a, c1, c2 = Q(2, 7), Q(3, 5), Q(-4, 9)
    tensor_form = sum(c*i for c, i in zip((a, c1, c2), torsion_invariants(b)))
    irrep_form = sum(c*sum(x*x for x in block.flat) for c, block in zip(
        quadratic_torsion_coefficients(a, c1, c2), (isotropic, antisymmetric, traceless)))
    assert tensor_form == irrep_form


def test_contorsion_variation_of_production_action():
    from cg_frg.ewsb.squash_level_transfer import ec_action
    result = production_torsion_variation()
    a, b, c = result["action_coefficients"]
    actual = ec_action(1.)
    assert (float(a), float(b), float(c)) == pytest.approx(
        (actual["a"], actual["b"], actual["c"]), rel=3e-16)
    assert result["isotropic_hessian"] == -9
    assert result["matter_action_derivative_required_at_tau"] == Q(9, 50)
    h = Q(1, 127)
    t = Q(1, 50)
    def action(x):
        return sum(v*i for v, i in zip((a, b, c), torsion_invariants(
            ((x, 0, 0), (0, x, 0), (0, 0, x)))))
    assert (action(t+h)-action(t-h))/(2*h) == -Q(9, 50)
    # Same isotropic action, different trace-free action: ansatz uniqueness
    # cannot prove uniqueness of all same-order action invariants.
    isotropic = torsion_invariants(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    assert isotropic[2] == 0
    assert sum(v*i for v, i in zip((a, b, c), isotropic)) == sum(
        v*i for v, i in zip((a, b, c+1), isotropic))
    antisymmetric = torsion_invariants(((0, 1, 0), (-1, 0, 0), (0, 0, 0)))
    assert antisymmetric[2] == 4
    assert quadratic_torsion_coefficients(a, b, c) != quadratic_torsion_coefficients(a, b, c+1)


def test_internal_spin_variation_only_sources_isotropic_torsion():
    vertices = minimal_internal_torsion_vertices()
    # Diagonal and off-diagonal connection variations are evaluated by the
    # Clifford contraction. No trace-free vertex is removed by hand.
    expected = -np.einsum("ij,uv->ijuv", np.eye(3), np.eye(2))/4
    np.testing.assert_allclose(vertices, expected, atol=1e-15)
    rng = np.random.default_rng(44)
    for _ in range(5):
        b = rng.normal(size=(3, 3))
        vertex = np.einsum("ij,ijuv->uv", b, vertices)
        np.testing.assert_allclose(vertex, -np.trace(b)*np.eye(2)/4, atol=1e-15)


def test_full_algebraic_elimination_against_independent_tensor_action():
    coefficients = (.25, 1., -7/12)
    rng = np.random.default_rng(53)
    current = rng.normal(size=(3, 3))
    result = solve_algebraic_torsion(current, coefficients)
    b = result["stationary_dual_torsion"]
    def action(point):
        return sum(c*i for c, i in zip(coefficients, torsion_invariants(point)))+np.sum(current*point)
    for i in range(3):
        for j in range(3):
            delta = np.zeros((3, 3))
            delta[i, j] = 1e-5
            assert (action(b+delta)-action(b-delta))/(2e-5) == pytest.approx(0, abs=2e-9)
    np.testing.assert_allclose(result["gradient_residual"], 0, atol=1e-15)
    trace_current = .1*np.eye(3)
    minimal = solve_algebraic_torsion(trace_current, coefficients)
    np.testing.assert_allclose(minimal["trace_free_stationary_part"], 0, atol=1e-15)
    assert np.linalg.norm(result["trace_free_stationary_part"]) > .1
    # c changes only the transverse response. It cannot be fixed by the
    # trace-only background, but matters for a nonminimal spin source.
    changed = solve_algebraic_torsion(trace_current, (.25, 1., -.2))
    np.testing.assert_allclose(changed["stationary_dual_torsion"], minimal["stationary_dual_torsion"])
    changed_full = solve_algebraic_torsion(current, (.25, 1., -.2))
    assert np.linalg.norm(changed_full["stationary_dual_torsion"]-b) > .1


def test_common_dirac_torsion_action_all_euler_derivatives():
    rng = np.random.default_rng(74)
    b = rng.normal(size=(3, 3))
    # Spin times the complete content carrier, including its neutral line.
    dimension = 2*full_carrier_response()["dimension"]
    ket = rng.normal(size=dimension)+1j*rng.normal(size=dimension)
    bra = rng.normal(size=dimension)+1j*rng.normal(size=dimension)
    matrix = rng.normal(size=(dimension, dimension))+1j*rng.normal(size=(dimension, dimension))
    d0 = (matrix+matrix.conj().T)/2
    coefficients = (.25, 1., -7/12)
    result = minimal_coupled_action_variation(b, ket, bra, d0, coefficients)
    vertices = minimal_internal_torsion_vertices()
    def action(point, column, row):
        # Independently assemble the matter operator from all nine vertices
        # and the torsion action from all tensor components.
        operator = d0+np.kron(np.einsum("ij,ijuv->uv", point, vertices), np.eye(16))
        return sum(c*i for c, i in zip(coefficients, torsion_invariants(point)))+row@operator@column
    assert result["action"] == pytest.approx(action(b, ket, bra), abs=1e-11)
    h = 1e-5
    for i in range(3):
        for j in range(3):
            delta = np.zeros((3, 3))
            delta[i, j] = h
            derivative = (action(b+delta, ket, bra)-action(b-delta, ket, bra))/(2*h)
            assert derivative == pytest.approx(result["torsion_gradient"][i, j], abs=2e-8)
    for i in (0, dimension-1):
        delta = np.zeros(dimension)
        delta[i] = h
        row_derivative = (action(b, ket, bra+delta)-action(b, ket, bra-delta))/(2*h)
        column_derivative = (action(b, ket+delta, bra)-action(b, ket-delta, bra))/(2*h)
        assert row_derivative == pytest.approx(result["matter_row_equation"][i], abs=2e-8)
        assert column_derivative == pytest.approx(result["matter_column_equation"][i], abs=2e-8)


@pytest.mark.parametrize("n", (0, 1, 2, 7, 20))
def test_native_torsion_square_retains_the_signed_cross_term(n):
    tau, radius, h = .02, 1.7, 1e-6
    result = minimal_torsion_spectral_terms(n, tau, radius)
    scalar_vertex = sum(minimal_internal_torsion_vertices()[i, i] for i in range(3))*tau/radius
    full_operator = result["native_dirac"]*np.eye(32)+np.kron(scalar_vertex, np.eye(16))
    np.testing.assert_allclose(full_operator@full_operator,
                               result["coupled_dirac_square"]*np.eye(32), atol=3e-14)
    assert result["neutral_dirac_shift"] == result["torsion_dirac_shift"]
    plus = minimal_torsion_spectral_terms(n, tau+h, radius)["coupled_dirac_square"]
    minus = minimal_torsion_spectral_terms(n, tau-h, radius)["coupled_dirac_square"]
    assert (plus-minus)/(2*h) == pytest.approx(result["d_dirac_square_d_tau"], rel=1e-8)
    assert abs(result["production_minus_coupled_square"]) > .01
    d, v = result["native_dirac"], result["torsion_dirac_shift"]
    paired = ((d+v)**2+(-d+v)**2)/2
    assert paired-d*d == pytest.approx(9*tau*tau/(16*radius*radius), abs=5e-14)


def test_minimal_classical_equations_close_at_zero_not_at_gauge_response():
    data = minimal_classical_stationarity()
    assert data["stationary_tau"] == 0
    assert data["trace_action_derivative_at_gauge_tau"] == -Q(9, 50)
    assert data["required_matter_bilinear_times_radius_at_gauge_tau"] == -Q(6, 25)
    assert data["sign_averaged_quadratic_difference"] == Q(3, 16)
    assert not data["gauge_tau_is_a_minimal_classical_stationary_point"]
    coefficients = (.25, 1., -7/12)
    zero = np.zeros(32)
    for tau in (-.4999, 0., .02, .2499):
        result = minimal_coupled_action_variation(tau*np.eye(3), zero, zero,
                                                  1.5*np.eye(32), coefficients)
        singular = np.linalg.svd(result["coupled_dirac"], compute_uv=False)
        assert min(singular) >= float(data["uniform_coupled_gap_times_radius_lower_bound"])
        assert np.trace(result["torsion_gradient"]).real == pytest.approx(-9*tau)
    # The nonzero charge-derived value fails the trace equation even though
    # the two matter equations and all eight trace-free equations hold.
    at_gauge = minimal_coupled_action_variation(.02*np.eye(3), zero, zero,
                                                1.5*np.eye(32), coefficients)
    np.testing.assert_allclose(at_gauge["matter_row_equation"], 0)
    np.testing.assert_allclose(at_gauge["matter_column_equation"], 0)
    np.testing.assert_allclose(at_gauge["torsion_gradient"], -.06*np.eye(3), atol=1e-15)


def test_torsion_sector_contract_tracks_actual_downstream_formulas():
    from cg_core.spectrum_loop import m2_gauge, m2_fermion
    from cg_frg.ewsb.squash_level_transfer import killing_normalisation
    t, radius, step = .02, 2.4935343325226915, 1e-6
    result = production_torsion_sector_contract(t, radius)
    assert result["spin_source_trace_free_vertex_norm"] < 1e-15
    assert result["trace_hessian_eigenvalue"] == pytest.approx(-3)
    assert result["trace_free_hessian_eigenvalues"] == pytest.approx((2/3, 3))
    assert result["matter_action_derivative_required"] == pytest.approx(.18/radius**2)
    assert result["gauge_torsion_mass_squared"] == m2_gauge(0, radius, t)
    assert result["fermion_torsion_mass_squared"] == m2_fermion(radius, t)
    kplus = killing_normalisation(t+step)["kappa"]
    kminus = killing_normalisation(t-step)["kappa"]
    assert (math.log(kplus)-math.log(kminus))/(2*step) == pytest.approx(result["d_log_kappa_d_tau"], rel=1e-9)
    for key, function in (("d_gauge_mass_squared_d_tau", lambda x: m2_gauge(0, radius, x)),
                          ("d_fermion_mass_squared_d_tau", lambda x: m2_fermion(radius, x)),
                          ("d_lambda_ec_d_tau", lambda x: 14+8*x+2*x*x),
                          ("d_inverse_alpha_torsion_term_d_tau", lambda x: -math.pi*x*x/2)):
        assert (function(t+step)-function(t-step))/(2*step) == pytest.approx(result[key], rel=2e-9)


def test_profile_extremum_is_global_but_not_logdet_stationarity():
    result = survival_stationary_geometry()
    center = result["interior_stationary_point"]
    assert result["maximum"] == Q(4, 27)
    for j in range(101):
        y = Q(j, 100)
        assert Q(4, 27)-y*(1-y)**2 == (y-center)**2*(Q(4, 3)-y)
    assert gaussian_mode_action_derivative(center, Q(1)) == Q(3, 4)
    eps = 1e-6
    difference = (gaussian_mode_action(float(center)+eps)-gaussian_mode_action(float(center)-eps))/(2*eps)
    assert difference == pytest.approx(.75, abs=5e-11)


def test_mass_variation_keeps_different_mode_coordinates():
    result = mass_stationarity_terms([1., 4.], [1., 1.], .5)
    assert result["mode_y"] == pytest.approx((1/3, 1/9))
    assert result["mass_action_derivative"] > 0
    assert result["survival_mass_derivative"] != 0


def test_angular_and_logdet_factors_in_four_dimensional_measure():
    result = four_dimensional_loop_measure()
    assert result["coefficient"] == pytest.approx(1/(32*math.pi**2), rel=2e-15)


def test_zero_mode_normalization_cancels_only_with_charged_vertex():
    reference = zero_mode_action(2., 3.)
    normalized = zero_mode_action(2., 3., 1/math.sqrt(reference["volume"]))
    assert normalized["zero_mode_overlap"] == pytest.approx(1)
    assert reference["inverse_g4_squared"] != normalized["inverse_g4_squared"]
    assert reference["charge_normalized_g4_squared"] == pytest.approx(normalized["charge_normalized_g4_squared"])
    changed_action = zero_mode_action(2., 6.)
    assert changed_action["charge_normalized_g4_squared"] == pytest.approx(2*reference["charge_normalized_g4_squared"])


@pytest.mark.parametrize("k_l", [1.5, 2.4935343325, 5.])
def test_exact_required_seven_dimensional_matching(k_l):
    result = required_seven_dimensional_coefficient(3., 7., k_l)
    assert result["g7_squared_required"] == pytest.approx(result["g7_squared_simplified"], rel=3e-15)
    reduced = zero_mode_action(result["radius"], result["g7_squared_required"])
    assert reduced["charge_normalized_g4_squared"] == pytest.approx(result["g4_squared"], rel=3e-15)
    assert killing_coupling_squared(3., 7., k_l) == 8*gauge_scale_factor(3., 7.)/k_l**3


def test_gauge_prescription_has_store_identity_and_checked_parents(tmp_path, monkeypatch):
    from cg_core import params
    from cg_core.quantities import readout_definition
    from scripts.audit_param_writers import audit_file
    monkeypatch.setattr(params, "_PARAM_FILE", tmp_path/"cg_params.json")
    monkeypatch.setattr(params, "_SM_FILE", tmp_path/"reference_inputs.json")
    monkeypatch.setattr(params, "_READ_INPUTS", {})
    params.init_stores({"M_G": 3., "M_P": 7.}, {})
    value = register_gauge_scale_factor()
    record = params.all_records()["gauge_kinetic_scale_factor"]
    assert value == (3/7)**2
    assert record["provenance"] == "SCALE_CHOICE"
    assert set(record["direct_inputs"]) == {"M_G", "M_P"}
    for key in ("gauge_kinetic_scale_factor", "g2_MG", "g2_MG_geo", "g2_MG_bare_constraint"):
        assert readout_definition(key).unit == "1"
    assert audit_file(params._PARAM_FILE, "test", True) == []


def test_production_gauge_boundary_consumes_registered_factor(tmp_path, monkeypatch):
    import shutil
    from cg_core import params
    from cg_frg.gauge import geometric_couplings
    old_records = params.all_records()
    for name in ("_PARAM_FILE", "_SM_FILE"):
        original = getattr(params, name)
        target = tmp_path/original.name
        shutil.copy2(original, target)
        monkeypatch.setattr(params, name, target)
    monkeypatch.setattr(params, "_READ_INPUTS", {})
    geometric_couplings.compute()
    records = params.all_records()
    bare, screened = records["g2_MG_geo"], records["g2_MG"]
    assert set(bare["direct_inputs"]) == {"gauge_kinetic_scale_factor", "kL"}
    assert set(screened["direct_inputs"]) == {"g2_MG_geo", "tau"}
    assert records["gauge_kinetic_scale_factor"]["provenance"] == "SCALE_CHOICE"
    for key in ("g2_MG_geo", "g2_MG", "g1_MG_geo", "alpha_inv_MZ_pred"):
        assert records[key]["value"] == pytest.approx(old_records[key]["value"], rel=2e-12)


def test_production_order_parameter_publishes_three_sector_transfer(tmp_path, monkeypatch):
    import shutil
    from cg_core import params
    from cg_frg.ewsb import order_parameter
    for name in ("_PARAM_FILE", "_SM_FILE"):
        original = getattr(params, name)
        target = tmp_path/original.name
        shutil.copy2(original, target)
        monkeypatch.setattr(params, name, target)
    monkeypatch.setattr(params, "_READ_INPUTS", {})
    order_parameter.compute()
    records = params.all_records()
    contract = records["ec_torsion_sector_contract"]
    assert set(contract["direct_inputs"]) == {"tau", "kL"}
    assert contract["quantity_definition"]["order"] == "classical derivative-free quadratic torsion variation"
    assert contract["value"]["trace_free_hessian_eigenvalues"] == pytest.approx((2/3, 3))
    matching = contract["value"]["curvature_action_matching"]
    assert not matching["same_action_up_to_overall_normalization"]
    assert matching["extra_irreducible_weights_MG3"] == pytest.approx((0, 10/3, -1.5))
    assert matching["cartan_tau_from_existing_spin_tau"] == -1
    assert records["ec_action_torsion_coeffs"]["value"]["torsion_algebraic"]


@pytest.mark.parametrize("call", [
    lambda: gaussian_mode_action(1), lambda: gaussian_mode_action_derivative(-1),
    lambda: mass_stationarity_terms([], [], 1),
    lambda: zero_mode_action(0, 1), lambda: zero_mode_action(1, 1, 0),
    lambda: gauge_scale_factor(1, 0), lambda: killing_coupling_squared(1, 1, -1),
    lambda: solve_algebraic_torsion(np.eye(3), (1., 1., 0.)),
    lambda: production_torsion_sector_contract(.25, 1.),
])
def test_invalid_action_and_matching_domains_are_rejected(call):
    with pytest.raises(ValueError):
        call()
