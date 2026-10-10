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

"""Independent source derivatives, exact block algebra and critical limits."""
import numpy as np
import pytest
from fractions import Fraction
from scipy.optimize import root
from cg_core.source_response import (SourceResponse, differentiate_response,
                                     schur_reduce, restrict_variational_constraints,
                                     critical_residue, certify_affine_residue,
                                     evaluate_endpoint_response)


def test_nonlinear_solved_branch_against_actual_source_update():
    def E(x, h, z):
        return x+x**3-h
    def O(x, h, z):
        return x+x**2+0.2*h
    x, h = np.array([0.4]), np.array([0.4+0.4**3])
    data = differentiate_response(E, O, x, h, step=1e-5)
    eps = 1e-4
    plus = root(lambda y: E(y, h+eps, 0), x)
    minus = root(lambda y: E(y, h-eps, 0), x)
    assert plus.success and minus.success
    measured = (O(plus.x, h+eps, 0)-O(minus.x, h-eps, 0))/(2*eps)
    np.testing.assert_allclose(data.evaluate().ravel(), measured, rtol=2e-8)
    with pytest.raises(ValueError, match="solved"):
        differentiate_response(E, O, x+0.1, h)


def test_schur_keeps_two_source_columns_readout_and_direct_term():
    z = 0.3+0.2j
    L = np.array([[2+z, 0.4, 0.2], [0.4, 1+2*z, 0.3], [0.2, 0.3, 3+z]])
    S = np.array([[1, 0.2], [0.3j, 1], [0.7, 0.4]])
    R = np.array([[0.6, 0.2j, 0.8], [1, 0.3, 0.4j]])
    D = np.array([[0.2, 0.1j], [0.3, 0.4]])
    data = SourceResponse(L, S, R, D)
    reduced = schur_reduce(data, [1, 0])
    np.testing.assert_allclose(reduced.evaluate(), data.evaluate(), atol=1e-14)
    assert np.linalg.norm(reduced.D-D) > 0.1
    assert np.linalg.norm(reduced.R-reduced.S.conj().T) > 0.1


def test_state_residual_and_source_basis_covariance():
    L = np.array([[3., 1.], [1., 2.]])
    S = np.array([[1., 0.5], [2., 1.]])
    R = np.array([[1., 0.2]])
    D = np.array([[0.4, 0.7]])
    T = np.array([[2., 0.4], [-0.2, 0.6]])
    U = np.array([[0.8, 0.1], [0.3, 1.3]])
    J = np.array([[0.2, 2.], [1., 0.5]])
    original = SourceResponse(L, S, R, D).evaluate()
    transformed = SourceResponse(U@L@T, U@S@J, R@T, D@J).evaluate()
    np.testing.assert_allclose(transformed, original@J, atol=1e-14)


def test_variational_constraints_match_full_saddle_system():
    H = np.array([[3., 0.4, 0.2], [0.4, 2., 0.3], [0.2, 0.3, 4.]])
    S = np.array([[1., 0.2], [0.3, 1.], [2., -0.5]])
    R = np.array([[1., 2., 0.4], [0.3, 1., 0.7]])
    D = np.eye(2)*0.1
    C = np.array([[1., 1., -0.5]])
    reduced, basis = restrict_variational_constraints(SourceResponse(H, S, R, D), C)
    saddle = np.block([[H, C.T], [C, np.zeros((1, 1))]])
    solution = np.linalg.solve(saddle, np.vstack((S, np.zeros((1, 2)))))
    np.testing.assert_allclose(reduced.evaluate(), D+R@solution[:3], atol=1e-14)
    np.testing.assert_allclose(C@basis, 0, atol=1e-14)


def test_dark_critical_mode_is_not_an_observable_pole():
    H, K, S = np.diag([0., 2.]), np.eye(2), np.array([[0.], [1.]])
    result = critical_residue(H, K, S)
    assert result['kernel_dimension'] == 1 and result['visible_rank'] == 0
    np.testing.assert_array_equal(result['residue'], [[0.]])
    assert not result['physical_atom_established']
    for z in (1e-2, 1e-4, 1e-6):
        np.testing.assert_allclose(S.T@np.linalg.solve(H+z*K, S), [[1/(2+z)]])


def test_negative_or_zero_critical_slope_is_rejected():
    for K in (np.diag([-1., 1.]), np.diag([0., 1.])):
        with pytest.raises(ValueError, match="slope"):
            critical_residue(np.diag([0., 2.]), K, np.eye(2))


def test_visible_residue_limit_and_unitary_basis_invariance():
    H = np.diag([0., 0., 3.])
    K = np.array([[2., 0.2, 0.1], [0.2, 1., 0.3], [0.1, 0.3, 2.]])
    S = np.array([[1., 0.2], [0.3, 0.7], [0.8, -0.4]])
    result = critical_residue(H, K, S)
    assert result['visible_rank'] == 2 and result['positive_affine_measure']
    errors = []
    for z in (1e-3, 1e-4, 1e-5):
        errors.append(np.linalg.norm(z*S.T@np.linalg.solve(H+z*K, S)-result['residue']))
    assert errors[2] < errors[1]/9 < errors[0]/81
    U, _ = np.linalg.qr(np.array([[1., 2j, 3.], [2., 1., 4j], [3j, 4., 1.]]))
    other = critical_residue(U.conj().T@H@U, U.conj().T@K@U, U.conj().T@S)
    np.testing.assert_allclose(other['residue'], result['residue'], atol=1e-13)


def test_positive_local_residue_does_not_imply_positive_full_affine_measure():
    result = critical_residue(np.diag([0., 2.]), np.diag([1., -1.]), np.eye(2))
    assert result['visible_rank'] == 1
    assert not result['positive_affine_measure']


def test_critical_classification_respects_operator_and_source_units():
    for scale in (1e-20, 1., 1e20):
        massive = critical_residue(scale*np.diag([2., 5.]), scale*np.eye(2), np.eye(2))
        assert massive['kernel_dimension'] == 0
        visible = critical_residue(scale*np.diag([0., 2.]), scale*np.eye(2),
                                   scale*np.array([[1.], [0.]]))
        assert visible['visible_rank'] == 1 and visible['positive_affine_measure']
        np.testing.assert_allclose(visible['residue']/scale, [[1.]], rtol=1e-13)
        with pytest.raises(ValueError, match="Hermitian"):
            critical_residue(scale*np.array([[0., 1j], [0., 2.]]),
                             scale*np.eye(2), np.eye(2))


def test_tolerated_negative_eigenvalue_is_not_a_positive_affine_measure():
    result = critical_residue(np.diag([-1e-12, 2.]), np.eye(2), np.eye(2))
    assert result['kernel_dimension'] == 1
    assert not result['positive_affine_measure']


def test_massive_response_has_no_zero_residue_and_correct_bound():
    H, K, S = np.diag([2., 5.]), np.eye(2), np.eye(2)
    result = critical_residue(H, K, S)
    assert result['kernel_dimension'] == 0 and result['visible_rank'] == 0
    for z in (0., 0.1, 1.):
        measured = SourceResponse(H+z*K, S, S.T, np.zeros((2, 2))).evaluate()
        assert np.linalg.norm(measured, ord=2) <= 1/(2+z)+1e-14


def test_exact_certificate_distinguishes_small_positive_mass_from_zero():
    small_mass = Fraction(1, 10**12)
    candidate = critical_residue(np.diag([float(small_mass), 2.]), np.eye(2), [[1.], [0.]])
    assert candidate['kernel_dimension'] == 1
    assert candidate['classification'] == 'floating_point_candidate'
    assert not candidate['exact_zero_certified'] and not candidate['algebraic_pole_established']
    certificate = certify_affine_residue([[small_mass, 0], [0, 2]], [[1, 0], [0, 1]], [[1], [0]])
    assert certificate['kernel_dimension'] == 0
    assert not certificate['algebraic_pole_established']
    assert certificate['residue'][0, 0] == 0
    assert 0 < certificate['complement_gap_lower_bound'] <= small_mass
    # For any positive mass the exact infrared limit is zero; a finite
    # pre-asymptotic momentum range may still resemble a massless pole.
    z = small_mass / 10**6
    assert z/(small_mass+z) < Fraction(1, 10**6)


def test_exact_nonorthogonal_kernel_certificate_matches_resolvent():
    H = [[1, 1, 0], [1, 1, 0], [0, 0, 3]]
    K = [[2, 0, 1], [0, 1, 0], [1, 0, 2]]
    S = [[1, 0], [0, 1], [1, 1]]
    result = certify_affine_residue(H, K, S)
    assert result['kernel_identity_verified'] and result['exact_zero_certified']
    assert result['visible_rank'] == 1 and result['algebraic_pole_established']
    assert result['finite_positive_measure_certified']
    np.testing.assert_array_equal(result['residue'],
        [[Fraction(1, 3), Fraction(-1, 3)], [Fraction(-1, 3), Fraction(1, 3)]])
    assert 0 < result['complement_gap_lower_bound'] <= 2
    for z in (1e-4, 1e-6):
        measured = z*np.array(S).T@np.linalg.solve(np.array(H)+z*np.array(K), S)
        np.testing.assert_allclose(measured, np.asarray(result['residue'], float), atol=3*z)
    T = np.array([[1, 1, 0], [0, 2, 1], [1, 0, 1]], dtype=object)
    transformed = certify_affine_residue(T.T@np.array(H, object)@T,
        T.T@np.array(K, object)@T, T.T@np.array(S, object))
    np.testing.assert_array_equal(transformed['residue'], result['residue'])
    assert transformed['visible_rank'] == result['visible_rank']


def test_exact_multiple_and_invisible_critical_directions():
    H, K = [[0, 0, 0], [0, 0, 0], [0, 0, 3]], [[2, 1, 0], [1, 2, 0], [0, 0, 1]]
    result = certify_affine_residue(H, K, [[1, 0], [0, 1], [0, 0]])
    assert result['kernel_dimension'] == 2 and result['visible_rank'] == 2
    np.testing.assert_array_equal(result['residue'],
        [[Fraction(2, 3), Fraction(-1, 3)], [Fraction(-1, 3), Fraction(2, 3)]])
    dark = certify_affine_residue(H, K, [[0], [0], [1]])
    assert dark['exact_zero_certified'] and not dark['algebraic_pole_established']
    assert dark['visible_rank'] == 0 and dark['residue'][0, 0] == 0
    assert not dark['physical_atom_established']
    all_zero = certify_affine_residue([[0, 0], [0, 0]], [[2, 0], [0, 3]], [[1], [1]])
    assert all_zero['kernel_dimension'] == 2 and all_zero['complement_gap_lower_bound'] is None
    assert all_zero['residue'][0, 0] == Fraction(5, 6)


@pytest.mark.parametrize('value', [0.0, 1e-12, np.float64(1), True, 1j])
def test_exact_certificate_rejects_inexact_or_nonreal_input(value):
    with pytest.raises(TypeError):
        certify_affine_residue([[value]], [[1]], [[1]])


def test_exact_certificate_validates_signs_symmetry_and_visibility():
    for H in ([[Fraction(-1, 10**12), 0], [0, 2]], [[0, 1], [1, 0]]):
        with pytest.raises(ValueError, match='nonnegative'):
            certify_affine_residue(H, [[1, 0], [0, 1]], [[1], [0]])
    for slope in (-1, 0):
        with pytest.raises(ValueError, match='slope'):
            certify_affine_residue([[0, 0], [0, 2]], [[slope, 0], [0, 1]], [[1], [0]])
    with pytest.raises(ValueError, match='symmetric'):
        certify_affine_residue([[0, 1], [0, 0]], [[1, 0], [0, 1]], [[1], [0]])
    local = certify_affine_residue([['0', '0'], ['0', '2']], [['1', '0'], ['0', '-1']], [['1'], ['0']])
    assert local['algebraic_pole_established'] and not local['finite_positive_measure_certified']


def test_singular_elimination_and_invalid_inputs_fail():
    with pytest.raises(np.linalg.LinAlgError):
        schur_reduce(SourceResponse(np.diag([1., 0.]), np.eye(2), np.eye(2), np.zeros((2, 2))), [0])
    with pytest.raises(ValueError):
        critical_residue(np.diag([-1., 2.]), np.eye(2), np.eye(2))
    with pytest.raises(ValueError):
        SourceResponse(np.eye(2), np.ones((3, 1)), np.ones((1, 2)), [[0]])


def test_actual_full_matter_connector_matches_both_independent_response_engines():
    from cg_core.finite_connector import (elementary_connector, split_carrier,
                                          source_response as connector_response)
    data = elementary_connector([0.3+0.2j, 0.8-0.1j])
    operator, neutral = data['operator'], data['neutral_basis']
    basis = split_carrier(operator, neutral)['basis']
    source = np.column_stack((np.arange(1, 17)/17+0.2j, np.arange(16, 0, -1)/19-0.1j))
    readout = np.vstack((np.linspace(0.1, 0.9, 16)+0.3j, np.linspace(0.6, -0.2, 16)-0.15j))
    z = 0.23+0.7j
    full = SourceResponse(operator-z*np.eye(16), source, readout, np.zeros((2, 2)))
    local = SourceResponse(basis.conj().T@full.L@basis, basis.conj().T@source,
                           readout@basis, full.D)
    reduced = schur_reduce(local, np.arange(15))
    np.testing.assert_allclose(reduced.evaluate(), full.evaluate(), atol=1e-13)
    for i in range(2):
        for j in range(2):
            independent = connector_response(operator, z, source[:, j],
                                              readout=readout[i], neutral_basis=neutral)
            assert independent['relative_residual'] < 1e-13
            np.testing.assert_allclose(full.evaluate()[i, j], independent['value'], atol=1e-13)
    assert np.linalg.norm(reduced.D) > 0.01


def test_native_endpoint_feedback_uses_source_and_direct_hierarchy_response():
    from cg_core.joint_response import log_jacobian
    import json
    result = evaluate_endpoint_response(tau=0.02, response_radius=5.0)
    json.dumps(result, allow_nan=False)
    assert result['passed'] and not result['physical_atom_established']
    assert result['response_domain'] == {'radius': 5., 'projection': 'fixed'}
    c, tau, row = result['endpoint'], result['tau'], result['checks'][1]
    jacobian = log_jacobian(c, tau, 1.)['v_HIGGS']
    # Independent analytic readout derivatives: the direct torsion term
    # survives even before the endpoint state responds.
    assert row['R'] == pytest.approx(jacobian[0]/c, rel=1e-9)
    assert row['D'] == pytest.approx(jacobian[1]/tau, rel=1e-7)
    assert abs(row['response']-row['R']*row['S']/row['L']) > 2.
    assert row['response'] == pytest.approx(row['resolved_branch_derivative'], rel=1e-7)


def test_response_source_cache_invalidates_only_affected_calculations(monkeypatch):
    from pathlib import Path
    from scripts import evaluate_joint_extensions as extensions
    original_read = Path.read_bytes
    changes = {}
    def source_bytes(path):
        return original_read(path) + changes.get(path, b'')
    monkeypatch.setattr(Path, 'read_bytes', source_bytes)
    baseline = extensions.response_source_identities()
    changes[extensions.ROOT/'cg_frg/qcd/mass_gap_scale.py'] = b'\n# source change\n'
    assert extensions.response_source_identities() == baseline
    changes[extensions.ROOT/'cg_frg/gravity/local_response.py'] = b'\n# source change\n'
    updated = extensions.response_source_identities()
    assert {name for name in baseline if baseline[name] != updated[name]} == {
        'local_static_response', 'local_source_feedback',
        'finite_matter_source', 'native_scalar_intensity'}
    assert all(len(identity) < len(extensions.calculation_sources())
               for identity in baseline.values())


def test_response_source_cache_includes_shared_and_joint_dependencies(monkeypatch):
    from pathlib import Path
    from scripts import evaluate_joint_extensions as extensions
    original_read = Path.read_bytes
    changes = {}
    monkeypatch.setattr(Path, 'read_bytes',
                        lambda path: original_read(path)+changes.get(path, b''))
    baseline = extensions.response_source_identities()
    for common in ('scripts/evaluate_joint_extensions.py', 'cg_core/params.py',
                   'cg_core/sm_content.py', 'cg_core/__init__.py'):
        changes.clear()
        changes[extensions.ROOT/common] = b'\n# source change\n'
        updated = extensions.response_source_identities()
        assert all(updated[name] != baseline[name] for name in baseline)
    changes.clear()
    changes[extensions.ROOT/'cg_core/matter_matching.py'] = b'\n# source change\n'
    updated = extensions.response_source_identities()
    assert updated['joint_response'] != baseline['joint_response']
    assert updated['matter_extensions'] != baseline['matter_extensions']
    assert updated['finite_matter_source'] == baseline['finite_matter_source']
    assert 'cg_frg/gravity/__init__.py' in baseline['finite_matter_source']
    assert 'cg_core/modal_algebra.py' in baseline['finite_matter_source']
    assert 'cg_core/native_matter_matching.py' in baseline['matter_extensions']


def test_response_source_cache_follows_local_imports_and_conservatively_handles_loaders(monkeypatch):
    from pathlib import Path
    from scripts import evaluate_joint_extensions as extensions
    original_read = Path.read_bytes
    source = extensions.ROOT/'cg_frg/gravity/local_response.py'
    extra = b'\ndef dependency_probe():\n    from . import nonlinear_tensor\n'
    monkeypatch.setattr(Path, 'read_bytes',
                        lambda path: original_read(path)+(extra if path == source else b''))
    identity = extensions.response_calculation_sources('local_static_response')
    assert 'cg_frg/gravity/nonlinear_tensor.py' in identity
    extra = (b'\ndef dependency_probe(name):\n'
             b'    from importlib import import_module as load\n'
             b'    return load(name)\n')
    identity = extensions.response_calculation_sources('local_static_response')
    assert 'cg_frg/qcd/mass_gap_scale.py' in identity
    assert set(extensions.calculation_sources()) <= set(identity)
