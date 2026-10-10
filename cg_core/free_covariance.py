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

"""Finite positive free time covariances and Gaussian random-phase channels.

Internal same-time filtering is distinct from time-Gaussian covariance,
unitary evolution and tracing out a tensor factor. No interacting OS or
gravitational reconstruction is asserted by these finite constructions.
"""
from __future__ import annotations
import numpy as np
from cg_core.source_response import _hermitian, _matrix


def gaussian_phase_channel(rho, generator, variance):
    """E[e^-i theta A rho e^i theta A], theta~N(0,variance), A=A*.

    The channel is completely positive and trace preserving as a random
    unitary average. In the generator basis its multiplier is
    exp[-variance*(a_i-a_j)^2/2], not a field-amplitude heat multiplier.
    rho need not be a state: linearity on arbitrary matrices is preserved.
    """
    a, r = _hermitian(generator, "generator"), _matrix(rho, "rho")
    if r.shape != a.shape or not np.isfinite(variance) or variance < 0:
        raise ValueError("matching dimensions and finite nonnegative variance required")
    values, u = np.linalg.eigh(a)
    multiplier = np.exp(-0.5*variance*(values[:, None]-values[None, :])**2)
    return u @ (multiplier*(u.conj().T@r@u)) @ u.conj().T


def free_covariance(A, mass, time, filter_matrix=None):
    """B exp(-|t|sqrt(A+m²))/(2 sqrt(A+m²)) B*, A>=0, m>0.

    B may be rectangular and need not commute with A. It is a fixed
    same-time operator; a filter mixing positive and negative times is
    outside this definition. A finite mass gap avoids inverse-root domains.
    """
    a = _hermitian(A, "A")
    if not np.isfinite(mass) or mass <= 0 or not np.isfinite(time):
        raise ValueError("positive finite mass and finite time required")
    values, u = np.linalg.eigh(a)
    if np.min(values) < 0:
        raise ValueError("A must be nonnegative")
    b = np.eye(len(a)) if filter_matrix is None else _matrix(filter_matrix, "filter")
    if b.shape[1] != len(a):
        raise ValueError("filter has wrong input dimension")
    energies = np.sqrt(values+mass*mass)
    return (b@u) @ np.diag(np.exp(-abs(time)*energies)/(2*energies)) @ (b@u).conj().T


def reflection_gram(A, mass, times, sources, filter_matrix=None):
    """Gram entries f_i* C_B(t_i+t_j) f_j for finite t_i>=0 probes.

    With H=sqrt(A+m²), each vector is e^-tiH (2H)^-1/2 B* f_i,
    so the resulting matrix is positive. Its construction tests the whole
    matrix, not only one diagonal quadratic form.
    """
    times, sources = np.asarray(times, float), np.asarray(sources, complex)
    if (times.ndim != 1 or sources.ndim != 2 or len(times) != len(sources)
            or not np.all(np.isfinite(times)) or np.any(times < 0)
            or not np.all(np.isfinite(sources))):
        raise ValueError("finite nonnegative times and corresponding source rows required")
    covariance = free_covariance(A, mass, 0., filter_matrix)
    if sources.shape[1] != len(covariance):
        raise ValueError("source has wrong filtered dimension")
    return np.asarray([[np.vdot(fi, free_covariance(A, mass, ti+tj, filter_matrix)@fj)
                        for tj, fj in zip(times, sources)]
                       for ti, fi in zip(times, sources)])
