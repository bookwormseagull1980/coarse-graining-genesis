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

"""Exact local Ward identities of the Einstein--scalar effective action.

The torsion-free Palatini density is q^{mu nu} R_{mu nu}(Gamma), where
q=sqrt(-g) g^{-1}.  It is cubic in q-eta and Gamma after removal of a
boundary term.  Scalar matter uses the same density.  The routines evaluate
the off-shell density identity delta L = partial_mu(xi^mu L) on arbitrary
rational jets; no field equations or discretized derivatives are used.
The affine-dilation comparison below determines the relative cubic
self-coupling uniquely inside the unit-normalized first-order family.
The full generally covariant action remains the declared effective class.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import product
import numpy as np


def _exact_array(value, shape, name):
    result = np.array(value, dtype=object, copy=True)
    if result.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    for index in np.ndindex(shape):
        entry = result[index]
        if isinstance(entry, (bool, float, np.floating)):
            raise TypeError("exact jets require integers, fractions or rational strings")
        result[index] = Fraction(entry)
    return result


def _density_variation(q, dq, xi, dxi):
    """Lie derivative of a symmetric contravariant density of weight one."""
    n = len(xi)
    divergence = sum(dxi[a, a] for a in range(n))
    return np.array([[sum(xi[a]*dq[a, i, j]-q[a, j]*dxi[a, i]
                         -q[i, a]*dxi[a, j] for a in range(n))
                      +q[i, j]*divergence
                      for j in range(n)] for i in range(n)], dtype=object)


def palatini_ward_residual(metric_density, density_gradient, connection,
                          connection_gradient, connection_hessian, gauge,
                          gauge_gradient, gauge_hessian, gauge_third,
                          *, background=None, cubic_weight=1):
    """Evaluate the exact off-shell Palatini density identity at one point.

    Indices are q[i,j], dq[a,i,j], Gamma[r,i,j], dGamma[a,r,i,j],
    ddGamma[a,b,r,i,j], xi[r], dxi[a,r], ddxi[a,b,r].  Lower
    connection indices and coordinate derivative indices must be symmetric.
    With a constant background, cubic_weight multiplies (q-background)
    Gamma Gamma only.  Its variation uses the same gauge transformations,
    making it a direct test of the required cubic self-coupling.
    """
    n = len(gauge)
    if n < 3:
        raise ValueError("the effective tensor realization uses dimension at least three")
    q = _exact_array(metric_density, (n, n), "metric density")
    dq = _exact_array(density_gradient, (n, n, n), "density gradient")
    a = _exact_array(connection, (n, n, n), "connection")
    da = _exact_array(connection_gradient, (n, n, n, n), "connection gradient")
    dda = _exact_array(connection_hessian, (n, n, n, n, n), "connection Hessian")
    xi = _exact_array(gauge, (n,), "gauge vector")
    dx = _exact_array(gauge_gradient, (n, n), "gauge gradient")
    ddx = _exact_array(gauge_hessian, (n, n, n), "gauge Hessian")
    dddx = _exact_array(gauge_third, (n, n, n, n), "third gauge derivative")
    if (not np.array_equal(q, q.T)
            or not np.array_equal(dq, dq.swapaxes(1, 2))
            or not np.array_equal(a, a.swapaxes(1, 2))
            or not np.array_equal(da, da.swapaxes(2, 3))
            or not np.array_equal(dda, dda.swapaxes(0, 1))
            or not np.array_equal(dda, dda.swapaxes(3, 4))
            or not np.array_equal(ddx, ddx.swapaxes(0, 1))
            or not np.array_equal(dddx, dddx.swapaxes(0, 1))
            or not np.array_equal(dddx, dddx.swapaxes(1, 2))):
        raise ValueError("torsion-free connection and commuting coordinate jets required")
    if isinstance(cubic_weight, (bool, float, np.floating)):
        raise TypeError("the cubic weight must be exact")
    weight = Fraction(cubic_weight)
    bg = (_exact_array(background, (n, n), "background") if background is not None
          else np.zeros((n, n), dtype=object))
    qe = bg+weight*(q-bg)
    deltaq = _density_variation(q, dq, xi, dx)
    deltaa = np.empty_like(a)
    deltada = np.empty_like(da)
    for r, i, j in product(range(n), repeat=3):
        deltaa[r, i, j] = ddx[i, j, r]+sum(
            xi[s]*da[s, r, i, j]-a[s, i, j]*dx[s, r]
            +a[r, s, j]*dx[i, s]+a[r, i, s]*dx[j, s] for s in range(n))
        for b in range(n):
            deltada[b, r, i, j] = dddx[b, i, j, r]+sum(
                dx[b, s]*da[s, r, i, j]+xi[s]*dda[b, s, r, i, j]
                -da[b, s, i, j]*dx[s, r]-a[s, i, j]*ddx[b, s, r]
                +da[b, r, s, j]*dx[i, s]+a[r, s, j]*ddx[b, i, s]
                +da[b, r, i, s]*dx[j, s]+a[r, i, s]*ddx[b, j, s]
                for s in range(n))
    density = variation = Fraction(0)
    gradient = [Fraction(0) for _ in range(n)]
    for i, j in product(range(n), repeat=2):
        rd = sum(da[r, r, i, j]-da[j, r, i, r] for r in range(n))
        rq = sum(a[r, r, s]*a[s, i, j]-a[r, j, s]*a[s, i, r]
                 for r, s in product(range(n), repeat=2))
        vrd = sum(deltada[r, r, i, j]-deltada[j, r, i, r] for r in range(n))
        vrq = sum(deltaa[r, r, s]*a[s, i, j]+a[r, r, s]*deltaa[s, i, j]
                  -deltaa[r, j, s]*a[s, i, r]-a[r, j, s]*deltaa[s, i, r]
                  for r, s in product(range(n), repeat=2))
        density += q[i, j]*rd+qe[i, j]*rq
        variation += deltaq[i, j]*(rd+weight*rq)+q[i, j]*vrd+qe[i, j]*vrq
        for b in range(n):
            drd = sum(dda[b, r, r, i, j]-dda[b, j, r, i, r] for r in range(n))
            drq = sum(da[b, r, r, s]*a[s, i, j]+a[r, r, s]*da[b, s, i, j]
                      -da[b, r, j, s]*a[s, i, r]-a[r, j, s]*da[b, s, i, r]
                      for r, s in product(range(n), repeat=2))
            gradient[b] += dq[b, i, j]*(rd+weight*rq)+q[i, j]*drd+qe[i, j]*drq
    total_divergence = sum(xi[b]*gradient[b]+dx[b, b]*density for b in range(n))
    return {"density": density, "gauge_variation": variation,
            "total_divergence": total_divergence,
            "ward_residual": variation-total_divergence}


def scalar_ward_residual(metric_density, density_gradient, scalar_gradient,
                         scalar_hessian, gauge, gauge_gradient):
    """Density identity for massless scalar matter on the same metric.

    L_m = q^{mu nu} partial_mu phi partial_nu phi / 2.  The scalar
    gradient may be off shell; its Hessian is any symmetric rational jet.
    """
    n = len(gauge)
    q = _exact_array(metric_density, (n, n), "metric density")
    dq = _exact_array(density_gradient, (n, n, n), "density gradient")
    p = _exact_array(scalar_gradient, (n,), "scalar gradient")
    dp = _exact_array(scalar_hessian, (n, n), "scalar Hessian")
    xi = _exact_array(gauge, (n,), "gauge vector")
    dx = _exact_array(gauge_gradient, (n, n), "gauge gradient")
    if (not np.array_equal(q, q.T) or not np.array_equal(dq, dq.swapaxes(1, 2))
            or not np.array_equal(dp, dp.T)):
        raise ValueError("symmetric metric and scalar Hessian required")
    deltaq = _density_variation(q, dq, xi, dx)
    deltap = [sum(dx[b, a]*p[a]+xi[a]*dp[b, a] for a in range(n))
              for b in range(n)]
    density = sum(q[i, j]*p[i]*p[j] for i, j in product(range(n), repeat=2))/2
    variation = sum(deltaq[i, j]*p[i]*p[j]/2+q[i, j]*deltap[i]*p[j]
                    for i, j in product(range(n), repeat=2))
    gradient = [sum(dq[b, i, j]*p[i]*p[j]/2+q[i, j]*dp[b, i]*p[j]
                    for i, j in product(range(n), repeat=2)) for b in range(n)]
    divergence = sum(xi[b]*gradient[b]+dx[b, b]*density for b in range(n))
    return {"density": density, "gauge_variation": variation,
            "total_divergence": divergence,
            "ward_residual": variation-divergence}


def _coefficient_at(points, values, degree):
    """Exact coefficient of the interpolating polynomial, without fitting."""
    result = Fraction(0)
    for i, x in enumerate(points):
        coefficients = [Fraction(1)]
        denominator = Fraction(1)
        for j, y in enumerate(points):
            if i == j:
                continue
            expanded = [Fraction(0)]*(len(coefficients)+1)
            for k, coefficient in enumerate(coefficients):
                expanded[k] -= y*coefficient
                expanded[k+1] += coefficient
            coefficients = expanded
            denominator *= x-y
        result += values[i]*coefficients[degree]/denominator
    return result


def homogeneous_ward_coefficients(metric_perturbation, density_gradient,
                                  connection, connection_gradient,
                                  connection_hessian, gauge, gauge_gradient,
                                  gauge_hessian, gauge_third, *, cubic_weight=1):
    """Exact coefficients of the cubic action's Ward polynomial.

    q=eta+epsilon*f, Gamma=epsilon*A and xi=epsilon*v give a
    polynomial of degree at most four.  Five rational evaluations recover
    every coefficient exactly.  Each output concerns the supplied jets;
    the general identity is established by the tensor-density derivation.
    """
    n = len(gauge)
    eta = np.diag([1]+[-1]*(n-1)).astype(object)
    h = _exact_array(metric_perturbation, (n, n), "metric perturbation")
    jets = [np.asarray(a, dtype=object) for a in
            (density_gradient, connection, connection_gradient,
             connection_hessian, gauge, gauge_gradient, gauge_hessian, gauge_third)]
    points = [Fraction(v) for v in (0, 1, -1, 2, -2)]
    values = [palatini_ward_residual(eta+v*h, *(v*a for a in jets),
                                   background=eta, cubic_weight=cubic_weight)
              ["ward_residual"] for v in points]
    return [_coefficient_at(points, values, degree) for degree in range(5)]


def verify_classical_completion():
    """Rational verification instances for the analytic Noether identity.

    Sparse nonzero jets exercise the inhomogeneous connection variation,
    its derivative, cubic self-coupling and the common scalar vertex.
    Polynomial coefficients are recovered exactly.  The arbitrary-field
    proof follows from the tensor-density transformation of the action.
    """
    eta = np.diag([1, -1, -1, -1]).astype(object)
    h = np.diag([1, 2, 3, 4]).astype(object)
    dh = np.zeros((4, 4, 4), dtype=object)
    dh[0] = np.diag([2, -1, 3, 1])
    a = np.zeros((4, 4, 4), dtype=object)
    a[0, 1, 1] = 1
    a[1, 0, 1] = a[1, 1, 0] = 2
    a[2, 2, 3] = a[2, 3, 2] = 3
    da = np.zeros((4, 4, 4, 4), dtype=object)
    da[2, 0, 1, 1] = 2
    da[1, 2, 2, 3] = da[1, 2, 3, 2] = 1
    dda = np.zeros((4, 4, 4, 4, 4), dtype=object)
    dda[0, 1, 2, 3, 3] = dda[1, 0, 2, 3, 3] = 1
    xi = np.array([1, -2, 3, 1], dtype=object)
    dx = np.diag([1, 2, -1, 3]).astype(object)
    dx[0, 2] = 2
    ddx = np.zeros((4, 4, 4), dtype=object)
    ddx[0, 1, 2] = ddx[1, 0, 2] = 1
    dddx = np.zeros((4, 4, 4, 4), dtype=object)
    dddx[0, 0, 0, 1] = 3
    data = (h, dh, a, da, dda, xi, dx, ddx, dddx)
    coefficients = homogeneous_ward_coefficients(*data)
    omitted = homogeneous_ward_coefficients(*data, cubic_weight=0)
    scalar = scalar_ward_residual(eta+h, dh, [1, 2, 3, 4],
                                  np.diag([2, 3, 1, -1]), xi, dx)
    passed = (all(value == 0 for value in coefficients)
              and omitted[:3] == [0, 0, 0] and omitted[3] != 0
              and scalar["ward_residual"] == 0)
    if not passed:
        raise ArithmeticError("the common Einstein--scalar Ward verification failed")
    return {"scope": "rational jet instances of the classical covariant action identity",
            "analytic_basis": "delta L=partial_mu(xi^mu L) for the Palatini and scalar densities",
            "gravitational_ward_coefficients": [str(v) for v in coefficients],
            "cubic_omission_residual": str(omitted[3]),
            "scalar_ward_residual": str(scalar["ward_residual"]),
            "arithmetic": "exact rational; polynomial degree at most four",
            "jet_evaluations": 11, "passed": passed}


def affine_dilation_completion():
    """Exact nonlinear self-coupling test on the generated four-carrier.

    At the coordinate origin xi=0 and dxi=I, tensor-density transport gives
    delta q=2q, delta Gamma=Gamma and delta(dGamma)=2dGamma. If c multiplies
    (q-eta) Gamma Gamma, the actual density residual is

        delta L_c - div(xi L_c) = 2(c-1) eta.R_quadratic.

    The torsion-free witness below has eta.R_quadratic=-2. Thus this
    necessary covariance identity forces c=1. These exact evaluations are
    the executable counterpart of SourceNonlinearTensorAction in Lean;
    they do not replace its arbitrary-configuration derivative theorem.
    """
    from cg_core.canonical_matter_bundle import generated_matter_bundle
    dimension = generated_matter_bundle()["base_dimension"]
    eta = np.diag([1, -1, -1, -1]).astype(object)
    connection = np.zeros((dimension,) * 3, dtype=object)
    connection[0, 1, 1] = 1
    connection[1, 0, 1] = connection[1, 1, 0] = 2
    zeros = lambda rank: np.zeros((dimension,) * rank, dtype=object)

    def evaluate(coefficient):
        return palatini_ward_residual(
            eta, zeros(3), connection, zeros(4), zeros(5),
            zeros(1), np.eye(dimension, dtype=object), zeros(3), zeros(4),
            background=eta, cubic_weight=coefficient,
        )["ward_residual"]

    residual_zero = evaluate(Fraction(0))
    residual_one = evaluate(Fraction(1))
    slope = residual_one - residual_zero
    if slope == 0:
        raise ArithmeticError("the chosen torsion-free jet did not detect self-coupling")
    coefficient = -residual_zero / slope
    if evaluate(coefficient) != 0:
        raise ArithmeticError("the derived self-coupling fails the density identity")
    return {
        "coefficient": coefficient,
        "ward_residual": residual_one,
        "omitted_cubic_residual": residual_zero,
        "residual_slope": slope,
        "dimension": dimension,
        "root_argument_count": 0,
        "comparison_class": "unit-normalized first-order quadratic plus cubic density",
        "identity": "delta L_c-div(xi L_c)=2(c-1) eta.R_quadratic",
    }
