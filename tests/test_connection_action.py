"""Independent tensor, connection and determinant checks for action matching."""
from fractions import Fraction as Q
from itertools import combinations, product

import numpy as np
import pytest

from cg_core.connection_action import (
    cartan_connection, scalar_curvature_difference, production_curvature_matching,
    cartan_spin_connection_vertices, minimal_gauge_curvature, paired_dirac_determinants,
    minimal_algebraic_torsion_span,
)
from cg_core.ec_variation import (
    minimal_internal_torsion_vertices, torsion_invariants, quadratic_torsion_coefficients,
)
from cg_core.ec_structure import ec_scalar_curvature, scalar_curvature_LC


def _zero(shape):
    return np.full(shape, Q(0), dtype=object)


def _dual_basis():
    basis = []
    for a, b in product(range(3), repeat=2):
        item = _zero((3, 3))
        item[a, b] = Q(1)
        basis.append(item)
    return basis


def test_complete_quadratic_identity_by_exact_polarization():
    # A quadratic polynomial on all nine components is fixed by its values
    # on e_i and e_i+e_j. This checks every mixed coefficient exactly.
    basis = _dual_basis()
    for b in basis+[x+y for x, y in combinations(basis, 2)]:
        result = scalar_curvature_difference(b)
        c = result["connection"]
        # Independently use connection-matrix commutators before tracing.
        matrices = tuple(c[:, :, i] for i in range(3))
        scalar = sum((matrices[i]@matrices[j]-matrices[j]@matrices[i])[i, j]
                     for i, j in product(range(3), repeat=2))
        compact = np.trace(b@b)-np.trace(b)**2/2
        assert scalar == compact == result["invariant_polynomial"]
        assert result["quadratic_identity_residual"] == 0
        for a, i, j in product(range(3), repeat=3):
            assert c[a, i, j] == -c[i, a, j]
            assert c[a, j, i]-c[a, i, j] == result["torsion"][a, i, j]


def test_covariant_divergence_retains_every_derivative_direction():
    zero = _zero((3, 3))
    for d, a, e in product(range(3), repeat=3):
        derivative = _zero((3, 3, 3))
        derivative[d, a, e] = Q(1)
        result = scalar_curvature_difference(zero, derivative)
        # The derivative of the boundary current can be read off from the
        # independent torsion trace; no curvature formula is reused here.
        dt = cartan_connection(derivative[d])["torsion"]
        expected = -2*sum(dt[b, b, d] for b in range(3))
        assert result["scalar_difference"] == expected
        assert result["quadratic_scalar"] == 0
    witness = _zero((3, 3, 3))
    witness[0, 1, 2] = Q(1)
    assert scalar_curvature_difference(zero, witness)["covariant_divergence"] != 0


def test_curvature_tensor_under_nontrivial_rational_frame_rotation():
    rotation = np.array([[Q(3, 5), Q(-4, 5), 0],
                         [Q(4, 5), Q(3, 5), 0], [0, 0, 1]], dtype=object)
    b = np.array([[Q(2, 7), 1, -3], [4, -2, Q(1, 3)], [0, 5, 6]], dtype=object)
    original = scalar_curvature_difference(b)
    rotated = scalar_curvature_difference(rotation@b@rotation.T)
    r = original["curvature_difference"]
    expected = _zero((3, 3, 3, 3))
    for a, v, i, j in product(range(3), repeat=4):
        expected[a, v, i, j] = sum(rotation[a, e]*rotation[v, f]*rotation[i, g]*rotation[j, h]
                                   *r[e, f, g, h]
                                   for e, f, g, h in product(range(3), repeat=4))
    assert np.array_equal(rotated["curvature_difference"], expected)
    assert rotated["scalar_difference"] == original["scalar_difference"]


@pytest.mark.parametrize("tau,length", ((Q(1, 50), Q(1)), (Q(-2, 7), Q(3, 2))))
def test_isotropic_connection_reproduces_existing_geometric_curvature(tau, length):
    b = np.eye(3, dtype=object)*(tau/length)
    result = scalar_curvature_difference(b)
    assert result["scalar_difference"] == -Q(3, 2)*(tau/length)**2
    assert float(result["scalar_difference"]) == pytest.approx(
        ec_scalar_curvature(float(tau), float(length))-scalar_curvature_LC(float(length)),
        rel=1e-10)


def test_production_action_requires_transverse_terms_after_trace_matching():
    matching = production_curvature_matching()
    assert matching["trace_matched_curvature_normalization"] == 3
    assert matching["extra_irreducible_weights"] == (0, Q(10, 3), -Q(3, 2))
    assert not matching["same_action_up_to_overall_normalization"]
    # Test arbitrary fields directly in the tensor action, not just the
    # specially selected trace on which equality holds by construction.
    for b in _dual_basis()+[np.eye(3, dtype=object)]:
        norms = (np.eye(3, dtype=object)*np.trace(b)/3, (b-b.T)/2,
                 (b+b.T)/2-np.eye(3, dtype=object)*np.trace(b)/3)
        production = sum(c*i for c, i in zip(matching["production_invariant_coefficients"],
                                              torsion_invariants(b)))
        curvature = scalar_curvature_difference(b)["quadratic_scalar"]
        transverse = sum(w*sum(v*v for v in x.flat)
                         for w, x in zip(matching["extra_irreducible_weights"], norms))
        assert production == 3*curvature+transverse
    curvature_weights = quadratic_torsion_coefficients(*matching["curvature_invariant_coefficients"])
    assert curvature_weights == (-Q(1, 2), -Q(1), Q(1))


def test_curvature_and_spin_use_the_same_connection_with_explicit_orientation():
    vertices = cartan_spin_connection_vertices()
    retained = minimal_internal_torsion_vertices()
    np.testing.assert_allclose(vertices, -retained, rtol=0, atol=0)
    for a, b in product(range(3), repeat=2):
        np.testing.assert_array_equal(vertices[a, b], np.eye(2)*(Q(1, 4) if a == b else 0))
    assert production_curvature_matching()["cartan_dual_from_existing_spin_dual"] == -1


def test_minimal_nonabelian_gauge_curvature_cancels_connection_before_squaring():
    # Exact skew generators in a noncommutative real gauge representation.
    gauge = np.array([[[0, -1, 0], [1, 0, 0], [0, 0, 0]],
                      [[0, 0, -1], [0, 0, 0], [1, 0, 0]],
                      [[0, 0, 0], [0, 0, -1], [0, 1, 0]]], dtype=object)
    derivative = _zero((3, 3, 3, 3))
    derivative[0, 1], derivative[2, 0] = 2*gauge[2], -3*gauge[1]
    fields = _dual_basis()+[Q(1, 50)*np.eye(3, dtype=object)]
    for b in fields:
        result = minimal_gauge_curvature(b, gauge, derivative)
        assert np.count_nonzero(result["connection_cancellation_residual"]) == 0
        # Dropping the torsion correction really changes F on these fields.
        assert np.count_nonzero(result["torsion_correction"]) > 0
        direct = result["exterior_curvature"]
        complete = result["curvature"]
        assert sum(np.trace(x@x) for row in direct for x in row) == sum(
            np.trace(x@x) for row in complete for x in row)


def test_two_sign_average_cannot_replace_the_actual_fermion_determinant():
    a, d, length = Q(4), Q(3, 2), Q(1)
    for tau in (Q(-1, 5), Q(1, 50), Q(1, 10)):
        result = paired_dirac_determinants(a, d, tau, length)
        v = -3*tau/(4*length)
        # Independent multiplication of the two actual squared operators.
        direct = (a+(d+v)**2-d*d)*(a+(-d+v)**2-d*d)
        assert direct == result["exact_pair_determinant"]
        assert direct-result["mean_square_determinant"] == -4*d*d*v*v
        assert result["exact_to_mean_determinant_ratio"] < 1
        assert result["same_parameter_quadratic_shift_ratio"] == Q(2, 3)
    zero = paired_dirac_determinants(a, d, 0, length)
    assert zero["exact_to_mean_determinant_ratio"] == 1


def test_minimal_quadratic_action_span_has_an_exact_production_obstruction():
    span = minimal_algebraic_torsion_span()
    assert span["curvature_annihilator_pairing"] == span["spin_annihilator_pairing"] == 0
    assert span["production_annihilator_pairing"] == Q(11, 6)
    assert not span["production_in_this_span"]
    # The all-nine-component Clifford table annihilates a basis of the
    # whole trace-free subspace, not just the isotropic trace slice.
    basis = _dual_basis()
    vertices = minimal_internal_torsion_vertices()
    trace_free = [b for i, b in enumerate(basis) if i not in (0, 4, 8)]
    trace_free += [basis[0]-basis[4], basis[4]-basis[8]]
    for b in trace_free:
        vertex = sum(float(b[i, j])*vertices[i, j] for i, j in product(range(3), repeat=2))
        np.testing.assert_array_equal(vertex, np.zeros((2, 2)))


@pytest.mark.parametrize("call", (
    lambda: cartan_connection([[1., 0, 0], [0, 1, 0], [0, 0, 1]]),
    lambda: cartan_connection([[1, 2], [3, 4]]),
    lambda: scalar_curvature_difference(np.eye(3, dtype=int), [1, 2]),
    lambda: minimal_gauge_curvature(np.eye(3, dtype=int), [1, 2], [1, 2]),
    lambda: paired_dirac_determinants(0, 1, 1, 1),
    lambda: paired_dirac_determinants(1, 2, 1, 0),
    lambda: paired_dirac_determinants(1, 2, 1, 1),
))
def test_invalid_geometry_or_nonpositive_determinant_is_rejected(call):
    with pytest.raises((ValueError, TypeError)):
        call()
