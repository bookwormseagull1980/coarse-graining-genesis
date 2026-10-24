"""Finite Gaussian comparison checked by independent density quadrature."""
import numpy as np
import pytest
from numpy.polynomial.hermite import hermgauss

from cg_core.precision_comparison import gaussian_precision_comparison


def test_entropy_comparison_against_gauss_hermite_log_density_integrals():
    precisions = [np.array([[2., .3], [.3, 1.]]), np.array([[1., -.2], [-.2, 3.]])]
    covariance = np.array([[.8, .1], [.1, .6]])
    weights = [.4, .6]
    result = gaussian_precision_comparison(precisions, weights, covariance)
    mean_precision = np.array(result["mean_precision"])
    nodes, quadrature_weights = hermgauss(12)
    root = np.linalg.cholesky(covariance)
    def integral(target):
        value = 0.
        for i, x in enumerate(nodes):
            for j, y in enumerate(nodes):
                v = root@np.array([x, y])*np.sqrt(2)
                # Direct normalized log density ratio at the quadrature point.
                log_nu = -.5*np.linalg.slogdet(covariance)[1]-.5*v@np.linalg.solve(covariance, v)
                log_target = .5*np.linalg.slogdet(target)[1]-.5*v@target@v
                value += quadrature_weights[i]*quadrature_weights[j]*(log_nu-log_target)/np.pi
        return value
    assert result["mean_relative_entropy"] == pytest.approx(sum(w*integral(k) for w, k in zip(weights, precisions)), abs=2e-14)
    assert result["comparison_relative_entropy"] == pytest.approx(integral(mean_precision), abs=2e-14)
    assert abs(result["identity_residual"]) < 2e-14
    assert result["precision_offset"] > 0
    minimizer = gaussian_precision_comparison(precisions, weights, result["comparison_covariance"])
    assert abs(minimizer["comparison_relative_entropy"]) < 2e-14
    assert minimizer["mean_relative_entropy"] == pytest.approx(result["precision_offset"], abs=2e-14)


def test_precision_offset_changes_with_the_source_parameter():
    values = []
    for q in (0., .5, 2.):
        ks = [np.diag([1+q, 1+2*q]), np.array([[1+3*q, .2*q], [.2*q, 1+q]])]
        values.append(gaussian_precision_comparison(ks, [.5, .5], np.eye(2))["precision_offset"])
    assert values[0] == 0.
    assert values[2] > values[1] > values[0]


@pytest.mark.parametrize("precision", (np.array([[1., 2.], [2., 1.]]),
                                        np.array([[1., .1], [.2, 1.]])))
def test_invalid_precision_is_rejected(precision):
    with pytest.raises(ValueError, match="symmetric|positive definite"):
        gaussian_precision_comparison([precision], [1.], np.eye(2))
