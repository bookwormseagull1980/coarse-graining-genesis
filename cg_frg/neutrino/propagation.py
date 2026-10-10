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

"""Labelled three-flavour propagation with explicit environmental sources.

Masses and energies are in eV; distances are in eV^-1 (hbar=c=1).
The input rest spectrum is never replaced by the solar comparison multiplier.
Extra propagation terms require an explicit source prescription, including
its antineutrino transformation. No matter-density data are supplied here.
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm


def _hermitian(matrix):
    a = np.asarray(matrix, complex)
    if a.shape != (3, 3) or not np.all(np.isfinite(a)):
        raise ValueError("finite 3 by 3 propagation matrix required")
    scale = float(np.max(np.abs(a)))
    if np.max(np.abs(a-a.conj().T)) > 2e-12*scale:
        raise ValueError("propagation Hamiltonian must be Hermitian")
    return a.copy()


def vacuum_hamiltonian(masses_eV, mixing, energy_eV, *, antineutrino=False):
    m, u = np.asarray(masses_eV, float), np.asarray(mixing, complex)
    if (m.shape != (3,) or np.any(m < 0) or not np.all(np.isfinite(m))
            or not np.isfinite(energy_eV) or energy_eV <= 0):
        raise ValueError("labelled nonnegative masses and positive energy required")
    if u.shape != (3, 3) or not np.allclose(u.conj().T@u, np.eye(3), atol=2e-12, rtol=0):
        raise ValueError("unitary labelled mixing matrix required")
    if antineutrino:
        u = u.conj()
    # Removing a common mass-squared leaves oscillation probabilities unchanged.
    return _hermitian((u*((m*m-m[0]**2)/(2*energy_eV)))@u.conj().T)


def hamiltonian(masses_eV, mixing, energy_eV, *, matter_eV=None,
                extra_eV=None, extra_antineutrino_eV=None, antineutrino=False):
    """Vacuum plus vector forward-scattering matter potential and explicit extra.

    The standard matter argument has the transformation V -> -V*.
    Other couplings must use the two explicit extra-source arguments.
    """
    h = vacuum_hamiltonian(masses_eV, mixing, energy_eV, antineutrino=antineutrino)
    if matter_eV is not None:
        v = _hermitian(matter_eV)
        h += -v.conj() if antineutrino else v
    if antineutrino:
        if extra_eV is not None and extra_antineutrino_eV is None:
            raise ValueError("extra source requires its explicit antineutrino coupling")
        if extra_antineutrino_eV is not None:
            h += _hermitian(extra_antineutrino_eV)
    elif extra_eV is not None:
        h += _hermitian(extra_eV)
    return _hermitian(h)


def mass_squared_source(shifts_eV2, mixing, energy_eV, *, amplitude,
                        antineutrino=False):
    """Hermitian scalar self-energy diagonal in the supplied vacuum basis.

    The real profile amplitude is explicit environmental data. This source
    has scalar transformation Delta H_bar=Delta H*, rather than the sign
    reversal of vector forward scattering. It represents a supplied squared-
    mass self-energy; no environmental mechanism or profile is inferred.
    """
    vacuum_hamiltonian([0., 0., 0.], mixing, energy_eV)
    shifts = np.asarray(shifts_eV2, float)
    if shifts.shape != (3,) or not np.isfinite(shifts).all() or not np.isfinite(amplitude):
        raise ValueError("three finite squared-mass shifts and a finite real amplitude required")
    u = np.asarray(mixing, complex)
    if antineutrino:
        u = u.conj()
    return _hermitian((u*(amplitude*shifts/(2*energy_eV)))@u.conj().T)


def _result(evolution):
    # Rows are detected flavours, columns are produced flavours.
    return {"evolution": evolution, "probabilities": np.abs(evolution)**2,
            "unitarity_residual": float(np.linalg.norm(
                evolution.conj().T@evolution-np.eye(3), ord=2)),
            "probability_convention": "P[detected, produced]"}


def propagate_layers(layers):
    """Ordered (length_eV_inverse, Hermitian_H_eV) layers, exactly exponentiated."""
    evolution = np.eye(3, dtype=complex)
    for distance, h in layers:
        if not np.isfinite(distance) or distance < 0:
            raise ValueError("finite nonnegative layer length required")
        h = _hermitian(h)
        evolution = expm(-1j*distance*(h-np.trace(h)*np.eye(3)/3))@evolution
    return _result(evolution)


def propagate_profile(profile, length_eV_inverse, *, rtol=2e-10, atol=2e-12):
    """Integrate an explicitly supplied Hamiltonian profile over natural distance.

    This solves propagation for the supplied source; it does not infer
    an environmental mechanism from a requested mass-squared splitting.
    """
    if not np.isfinite(length_eV_inverse) or length_eV_inverse < 0:
        raise ValueError("finite nonnegative propagation length required")
    if not np.isfinite(rtol) or not np.isfinite(atol) or rtol <= 0 or atol <= 0:
        raise ValueError("positive finite integration tolerances required")
    if length_eV_inverse == 0:
        return _result(np.eye(3, dtype=complex))
    # Unit interval avoids an integration-step convention tied to the energy unit.
    def rhs(t, vector):
        h = _hermitian(profile(t*length_eV_inverse))
        h -= np.trace(h)*np.eye(3)/3
        return (-1j*length_eV_inverse*h@vector.reshape(3, 3)).ravel()
    solution = solve_ivp(rhs, (0, 1), np.eye(3, dtype=complex).ravel(),
                         method="DOP853", rtol=rtol, atol=atol)
    if not solution.success:
        raise RuntimeError(solution.message)
    result = _result(solution.y[:, -1].reshape(3, 3))
    result["function_evaluations"] = solution.nfev
    if result["unitarity_residual"] > max(1e-8, 100*rtol):
        raise ArithmeticError("propagation failed its independent unitarity check")
    return result


def beta_mass_observables(masses_eV, mixing):
    """m_beta and the full range of m_beta_beta under two free Majorana phases."""
    vacuum_hamiltonian(masses_eV, mixing, 1.0)
    m, u = np.asarray(masses_eV, float), np.asarray(mixing, complex)
    weights = np.abs(u[0])**2
    lengths = weights*m
    maximum = float(lengths.sum())
    minimum = max(0.0, float(2*lengths.max()-maximum))
    return {"m_beta_eV": float(np.sqrt(weights@(m*m))),
            "m_beta_beta_min_eV": minimum, "m_beta_beta_max_eV": maximum,
            "m_beta_beta_at_supplied_phases_eV": float(abs((u[0]**2)@m)),
            "phase_scope": "two free Majorana phases; no phase selection inferred"}


def dirac_yukawa(masses_GeV, left, right, vev_GeV, *, scale_GeV, scheme):
    """Explicit effective matrix representation, not a new mass derivation."""
    if (not isinstance(scheme, str) or not scheme.strip()
            or not np.isfinite(scale_GeV) or scale_GeV <= 0
            or not np.isfinite(vev_GeV) or vev_GeV <= 0):
        raise ValueError("positive scales and an explicit mass/matching scheme required")
    vacuum_hamiltonian(masses_GeV, left, 1.0)
    vacuum_hamiltonian(masses_GeV, right, 1.0)
    y = np.asarray(left)@np.diag(np.asarray(masses_GeV)*np.sqrt(2)/vev_GeV)@np.asarray(right).conj().T
    return {"Y": y, "scale_GeV": float(scale_GeV), "scheme": scheme,
            "scope": "canonical effective representation of supplied masses and bases"}


def flavour_invariants(y_up, y_down):
    """Weak-basis invariants; no inferred right-handed mixing is assumed."""
    u, d = np.asarray(y_up, complex), np.asarray(y_down, complex)
    if u.shape != (3, 3) or d.shape != (3, 3) or not np.all(np.isfinite(u+d)):
        raise ValueError("finite three-family Yukawa matrices required")
    hu, hd = u@u.conj().T, d@d.conj().T
    commutator = hu@hd-hd@hu
    return {"up_singular_values": np.linalg.svd(u, compute_uv=False),
            "down_singular_values": np.linalg.svd(d, compute_uv=False),
            "imag_trace_commutator_cubed": float(np.imag(np.trace(commutator@commutator@commutator))),
            "trace_up_squared": float(np.trace(hu).real),
            "trace_down_squared": float(np.trace(hd).real)}
