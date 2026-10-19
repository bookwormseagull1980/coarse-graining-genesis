"""Actual source fibres, passive frames and nonlinear coefficient detection."""

from fractions import Fraction
import inspect

import numpy as np
import pytest
from scipy.linalg import expm

from cg_core.canonical_matter_bundle import (
    components, generated_matter_bundle, relative_transition,
)
from cg_frg.gravity.nonlinear_tensor import affine_dilation_completion


def test_generated_bundle_has_no_supplied_realization():
    assert not inspect.signature(generated_matter_bundle).parameters
    result = generated_matter_bundle()
    assert result["base_dimension"] == 4
    assert result["fibre_dimension"] == 16
    assert result["source_skew_adjoint_residual"] == 0
    assert np.trace(result["neutral_projector"]) == 1
    assert np.trace(result["charged_projector"]) == 15
    for operator in result["source_generators"].values():
        assert np.count_nonzero(operator @ result["neutral_projector"]) == 0


def test_hermitian_source_coordinates_give_the_lorentz_determinant():
    basis = generated_matter_bundle()["hermitian_basis"]
    q = np.asarray([2, 3, -4, 5])
    matrix = np.einsum("a,aij->ij", q, basis)
    assert np.linalg.det(matrix).real == pytest.approx(q[0] ** 2 - q[1:] @ q[1:])
    assert np.array_equal(matrix.conj().T, matrix)


def test_actual_source_frames_have_cocycle_and_compatible_components():
    generators = generated_matter_bundle()["source_generators"]
    first = expm(.31 * generators["weak_1"])
    second = expm(-.27 * generators["hypercharge"])
    third = expm(.41 * generators["colour_2"])
    section = np.arange(16) + 1j * np.arange(16)[::-1]
    np.testing.assert_allclose(
        relative_transition(first, second) @ relative_transition(second, third),
        relative_transition(first, third), atol=2e-15,
    )
    np.testing.assert_allclose(
        components(first, section),
        relative_transition(first, second) @ components(second, section), atol=1e-14,
    )
    assert np.linalg.norm(components(first, section)) == pytest.approx(np.linalg.norm(section))
    with pytest.raises(ValueError, match="unitary"):
        relative_transition(2 * np.eye(16), second)


def test_nonlinear_cubic_coefficient_is_detected_by_the_density_variation():
    result = affine_dilation_completion()
    assert result["coefficient"] == Fraction(1)
    assert result["ward_residual"] == 0
    assert result["omitted_cubic_residual"] == 4
    assert result["residual_slope"] == -4
