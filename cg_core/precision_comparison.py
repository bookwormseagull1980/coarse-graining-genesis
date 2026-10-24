"""Finite centered-Gaussian precision comparison in the source convention."""
from __future__ import annotations

import math
import numpy as np


def _positive_matrix(value, name):
    matrix = np.asarray(value, dtype=float)
    if (matrix.ndim != 2 or matrix.shape[0] == 0
            or matrix.shape[0] != matrix.shape[1]
            or not np.all(np.isfinite(matrix))
            or not np.allclose(matrix, matrix.T, rtol=0., atol=1e-13)):
        raise ValueError(f"{name} must be a finite symmetric square matrix")
    try:
        factor = np.linalg.cholesky(matrix)
    except np.linalg.LinAlgError as error:
        raise ValueError(f"{name} must be positive definite") from error
    return matrix, float(2*np.log(np.diag(factor)).sum())


def gaussian_precision_comparison(precisions, weights, reference_covariance):
    """Evaluate E D(nu||nu_c)=D(nu||nu_comp)+C for finite Gaussians.

    Each supplied precision defines nu_c=N(0,K_c^-1). The comparison law
    has precision E K_c; the arithmetic covariance mixture is a different
    law. The q-dependent offset C is returned explicitly. Values are
    floating-point evaluations, without interval certification.
    """
    precisions = list(precisions)
    weights = np.asarray(weights, dtype=float)
    if (not precisions or weights.shape != (len(precisions),)
            or not np.all(np.isfinite(weights)) or np.any(weights < 0)
            or not math.isclose(float(weights.sum()), 1., rel_tol=0., abs_tol=1e-13)):
        raise ValueError("nonnegative finite probability weights are required")
    # Remove only the roundoff of the declared probability normalization.
    weights = weights/weights.sum()
    covariance, logdet_covariance = _positive_matrix(reference_covariance, "reference covariance")
    matrices, determinants = zip(*(_positive_matrix(k, "source precision") for k in precisions))
    if any(k.shape != covariance.shape for k in matrices):
        raise ValueError("source and reference dimensions must agree")
    mean = sum((w*k for w, k in zip(weights, matrices)), np.zeros_like(covariance))
    _, logdet_mean = _positive_matrix(mean, "mean precision")
    mean_logdet = float(np.dot(weights, determinants))
    trace = float(np.trace(mean@covariance))
    dimension = covariance.shape[0]
    mean_entropy = .5*(trace-dimension-logdet_covariance-mean_logdet)
    comparison_entropy = .5*(trace-dimension-logdet_covariance-logdet_mean)
    offset = .5*(logdet_mean-mean_logdet)
    return {
        "mean_precision": mean.tolist(),
        "comparison_covariance": np.linalg.solve(mean, np.eye(dimension)).tolist(),
        "mean_relative_entropy": mean_entropy,
        "comparison_relative_entropy": comparison_entropy,
        "precision_offset": offset,
        "identity_residual": mean_entropy-comparison_entropy-offset,
    }
