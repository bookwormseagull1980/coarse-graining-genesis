"""Independent Gaussian moments and actual spatial/colour source checks."""
from fractions import Fraction as F
import math

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.linalg import expm

from cg_core.native_colour_response import (
    colour_source_response, curvature_covariance, curvature_haar_constants,
    curvature_laplace, intensity_expectation, intensity_generator,
    intensity_polynomial, intensity_update,
)
from cg_frg.qcd.generated_yang_mills import generated_yang_mills_gap


def test_intensity_update_inherits_the_gaussian_joint_moments():
    def rising(x, n):
        return math.prod(x+j for j in range(n))
    def joint(a, b, r):
        # Independently expand the correlated chi-square generating function
        # [(1-2t)(1-2u)-4*r*t*u]^(-M/2).
        return sum(F(rising(alpha, k), math.factorial(k))*(4*r)**k
                   *F(2**(a-k)*rising(alpha+k, a-k), math.factorial(a-k))
                   *F(2**(b-k)*rising(alpha+k, b-k), math.factorial(b-k))
                   for k in range(min(a, b)+1))*math.factorial(a)*math.factorial(b)
    for M in (1, 2, 120):
        alpha = F(M, 2)
        for r in (F(0), F(1, 3), F(3, 4), F(1)):
            for a, b in ((1, 1), (2, 1), (2, 2), (3, 2), (1, 4)):
                updated = intensity_update([F(0)]*b+[F(1)], r, dimension=M)
                mixed = intensity_expectation([F(0)]*a+updated, dimension=M)
                assert mixed == joint(a, b, r)/M**(a+b)


def test_intensity_generator_eigenfunctions_stationarity_and_composition():
    for k in range(9):
        p = intensity_polynomial(k, dimension=120)
        assert intensity_generator(p, dimension=120) == [-k*x for x in p]
        monomial = [F(0)]*k+[F(1)]
        for r in (F(0), F(1, 3), F(3, 4), F(1)):
            updated = intensity_update(monomial, r, dimension=120)
            assert intensity_expectation(updated, dimension=120) == intensity_expectation(monomial, dimension=120)
            assert intensity_update(p, r, dimension=120) == [r**k*x for x in p]
            assert intensity_update(updated, F(2, 5), dimension=120) == intensity_update(monomial, r*F(2, 5), dimension=120)


def test_curvature_haar_contractions_against_actual_cg_modes_and_quadrature():
    from cg_core.modal_algebra import clebsch_gordan, spin_matrices
    cg = np.array([[[clebsch_gordan(2, m, 1, i, 1, j) for j in (-1, 0, 1)]
                    for i in (-1, 0, 1)] for m in range(-2, 3)])
    cart = np.array([[1, 0, -1], [-1j, 0, -1j], [0, math.sqrt(2), 0]])/math.sqrt(2)
    def kernel(theta):
        d1 = expm(-1j*theta*spin_matrices(1)[2])
        d2 = expm(-1j*theta*spin_matrices(2)[2])
        return cart@np.einsum('miu,nju,mn->ij', cg, cg, d2.conj())@cart.conj().T, cart@d1@cart.conj().T
    for theta in (0., .31, 1.7, math.pi):
        actual, rotation = kernel(theta)
        np.testing.assert_allclose(actual, .3*(np.trace(rotation)*rotation+rotation@rotation)-.2*np.eye(3), atol=2e-14)
    constants = curvature_haar_constants()
    for name in ("determinant", "wedge_square", "norm_square"):
        def integrand(theta):
            k, _ = kernel(theta)
            square = k@k.conj().T
            value = {"determinant": np.linalg.det(k).real,
                     "wedge_square": ((np.trace(square)**2-np.trace(square@square))/2).real,
                     "norm_square": np.trace(square).real}[name]
            return (1-math.cos(theta))*float(value)/math.pi
        assert quad(integrand, 0., math.pi, epsabs=1e-12)[0] == pytest.approx(float(constants[name]), abs=2e-13)


def test_complete_curvature_weights_from_actual_colour_wick_tensors():
    from itertools import permutations
    from cg_core.finite_connector import matter_generators
    colours = [g for name, g in matter_generators().items() if name.startswith("colour_")]
    f = np.array([[[-.5*np.trace((x@y-y@x)@z).real for z in colours]
                   for y in colours] for x in colours])
    cubic, quartic = np.zeros((24,)*3), np.zeros((24,)*4)
    cubic[:8, 8:16, 16:] = 6*f
    bracket = np.einsum('abe,cde->abcd', f, f)
    for i, j in ((0, 1), (0, 2), (1, 2)):
        a, b = np.arange(8*i, 8*(i+1)), np.arange(8*j, 8*(j+1))
        quartic[np.ix_(a, b, a, b)] += bracket
    for raw, expected in ((cubic, 36*24.), (quartic, 216*3.)):
        d = raw.ndim
        symmetric = sum(raw.transpose(p) for p in permutations(range(d)))/math.factorial(d)
        assert math.factorial(d)*np.sum(symmetric**2) == pytest.approx(expected, rel=2e-14)
    # Combine the independent local colour contractions and Haar factors.
    gap = generated_yang_mills_gap(2.4935343325226915, certify=False)
    r = colour_source_response(gap)
    q, v, lam = gap["intensity_q"], gap["volume"], gap["long_root_eigenvalue"]
    variance = q/(3*v*8)
    constants = curvature_haar_constants()
    assert r["curvature_Hermite_weights"]["degree_3"] == pytest.approx(36*24*lam*v*v*variance**3*float(constants["determinant"]), rel=2e-14)
    assert r["curvature_Hermite_weights"]["degree_4"] == pytest.approx(216*v*v*variance**4*float(constants["wedge_square"]), rel=2e-14)
    assert r["curvature_Hermite_weights"]["degree_2"] == pytest.approx(gap["curvature_score_overlap"]**2, rel=2e-14)


def test_full_memory_and_laplace_integral_keep_the_nonradial_terms():
    gap = generated_yang_mills_gap(2.49, certify=False)
    r = colour_source_response(gap)
    omega = r["coefficient_composition_rate"]
    variance = r["curvature_variance"]
    assert curvature_covariance(r, 0.) == variance
    assert curvature_covariance(r, .001) == curvature_covariance(r, -.001)
    for z in (0., .7, 4.):
        direct = quad(lambda u: math.exp(-z*u)*curvature_covariance(r, u/omega)/variance,
                      0., math.inf, epsabs=1e-12)[0]*variance/omega
        assert curvature_laplace(r, z*omega) == pytest.approx(direct, rel=3e-13)
    assert r["full_to_radial_fourth_weight_ratio"] == pytest.approx(14.823)
    assert r["full_variance_excess_over_radial"] > .1
    assert r["fixed_mean_partial_legendre_curvature_JJ"] < 0
    assert r["composition_clock_conversion_assigned"] is False
    assert r["lepton_mixed_vertex_assigned"] is False
    assert r["intensity_correlation_rate"] != r["collective_law_tangent_restoring_rate"]


def test_full_lepton_source_attachment_retains_neutral_weak_and_higgs_blocks():
    from cg_frg.fermion.native_source_attachment import native_lepton_attachment
    from cg_core.finite_connector import matter_generators, elementary_connector
    r = native_lepton_attachment()
    assert (r["left_lepton_dimension"], r["right_lepton_dimension"]) == (2, 2)
    assert r["direct_colour_vertex_norm"] < 1e-14
    assert r["weak_leakage_outside_complete_lepton_carrier"] < 1e-14
    assert r["higgs_leakage_outside_complete_lepton_carrier"] < 1e-14
    assert r["retained_weak_vertex_norm"] > 0
    assert r["retained_higgs_vertex_norm"] > 0
    # Directly invert the full pencil for distinct deterministic colour
    # connections: its complete lepton block is independent of them.
    generators = matter_generators()
    h = elementary_connector([.2+.1j, .7-.3j])["operator"]
    ew = 1j*(.2*generators["weak_1"]+.3*generators["hypercharge"])
    leptons = [6, 7, 14, 15]
    block = None
    for scale in (0., .4, 1.3):
        d = h+ew+1j*scale*generators["colour_2"]
        inverse = np.linalg.inv(d-.5j*np.eye(16))[np.ix_(leptons, leptons)]
        if block is not None:
            np.testing.assert_allclose(inverse, block, atol=2e-15)
        block = inverse


def test_source_response_rejects_changed_carrier_and_invalid_composition():
    with pytest.raises(ValueError):
        intensity_update([1, 2], F(3, 2), dimension=120)
    with pytest.raises(ValueError):
        intensity_polynomial(2, dimension=0)
    gap = generated_yang_mills_gap(2.49, certify=False)
    gap["source_dimension"] = 119
    with pytest.raises(ValueError, match="SU\\(3\\)"):
        colour_source_response(gap)
