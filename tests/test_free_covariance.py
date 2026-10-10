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

"""Free spectral covariance and actual random-unitary channel tests."""
import numpy as np
import pytest
from scipy.linalg import expm
from cg_core.free_covariance import free_covariance, reflection_gram, gaussian_phase_channel


def test_free_reflection_gram_with_noncommuting_same_time_filter():
    A = np.diag([0., 3., 8.])
    B = np.array([[1., 0.2j, 0.4], [0.3, 1., 0.7j]])
    times = np.array([0.1, 0.4, 1.2])
    sources = np.array([[1., 0.2j], [0.5j, 1.], [0.7, -0.2]])
    gram = reflection_gram(A, 0.7, times, sources, B)
    energies = np.sqrt(np.diag(A)+0.7**2)
    vectors = np.column_stack([np.exp(-t*energies)/np.sqrt(2*energies)*(B.conj().T@f)
                               for t, f in zip(times, sources)])
    np.testing.assert_allclose(gram, vectors.conj().T@vectors, atol=1e-14)
    assert np.linalg.eigvalsh(gram).min() >= -1e-14


def test_time_gaussian_is_not_a_reflection_positive_covariance():
    times = np.array([0.25, 0.75])
    gram = np.exp(-(times[:, None]+times[None, :])**2)
    assert np.linalg.det(gram) < -0.05


def test_positive_mass_time_decay_and_invalid_domain():
    c0, ct = free_covariance(np.diag([0., 3.]), 2., 0), free_covariance(np.diag([0., 3.]), 2., 2.)
    np.testing.assert_allclose(ct[0, 0]/c0[0, 0], np.exp(-4))
    assert np.linalg.norm(ct, ord=2) <= np.exp(-4)/4+1e-15
    for mass in (0., -1., np.nan):
        with pytest.raises(ValueError):
            free_covariance(np.eye(2), mass, 0.)
    with pytest.raises(ValueError):
        free_covariance(np.diag([-1., 2.]), 2., 0.)


def test_phase_channel_matches_independent_gaussian_unitary_integral():
    A = np.array([[0.4, 0.3j], [-0.3j, 1.]])
    rho = np.array([[0.6, 0.2j], [-0.2j, 0.4]])
    variance = 0.7
    nodes, weights = np.polynomial.hermite.hermgauss(60)
    integrated = sum(w*(expm(-1j*np.sqrt(2*variance)*x*A)@rho@
                         expm(1j*np.sqrt(2*variance)*x*A))
                     for x, w in zip(nodes, weights))/np.sqrt(np.pi)
    np.testing.assert_allclose(gaussian_phase_channel(rho, A, variance), integrated, atol=1e-14)


def test_phase_channel_choi_positivity_trace_and_composition():
    A = np.array([[0.4, 0.3j], [-0.3j, 1.]])
    choi = np.zeros((4, 4), complex)
    for i in range(2):
        for j in range(2):
            unit = np.zeros((2, 2)); unit[i, j] = 1
            out = gaussian_phase_channel(unit, A, 0.7)
            choi += np.kron(unit, out)
            np.testing.assert_allclose(np.trace(out), float(i == j), atol=1e-14)
    assert np.linalg.eigvalsh(choi).min() >= -1e-13
    rho = np.array([[0.6, 0.2j], [-0.2j, 0.4]])
    np.testing.assert_allclose(gaussian_phase_channel(gaussian_phase_channel(rho, A, 0.2), A, 0.5),
                               gaussian_phase_channel(rho, A, 0.7), atol=1e-14)
    np.testing.assert_allclose(gaussian_phase_channel(rho, A, 0), rho, atol=1e-14)


def test_covariance_and_phase_channel_respect_energy_units():
    A = np.array([[1., .3j], [-.3j, 2.]])
    B = np.array([[1., .2j], [.3, .7], [.2j, .1]])
    rho = np.array([[.6, .2j], [-.2j, .4]])
    covariance = free_covariance(A, .7, .4, B)
    phase_state = gaussian_phase_channel(rho, A, .6)
    for scale in (1e-6, 1e6):
        # H -> scale H, t -> t/scale implies C -> C/scale.
        changed = free_covariance(scale**2*A, scale*.7, .4/scale, B)
        np.testing.assert_allclose(scale*changed, covariance, rtol=1e-13, atol=1e-15)
        # The random phase theta*A is invariant under reciprocal scaling.
        np.testing.assert_allclose(gaussian_phase_channel(rho, scale*A, .6/scale**2),
                                   phase_state, rtol=1e-13, atol=1e-15)
