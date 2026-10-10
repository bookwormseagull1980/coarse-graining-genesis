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

"""Unitary completion of the declared mixing textures; no parameter writes.

The Dirac phases are inherited prescriptions, not inferred from a fit.
Majorana phases are explicit free inputs. The retained production CKM
readout uses its leading-angle J; the exact completion is reported separately.
"""
from __future__ import annotations

import math
import numpy as np


def mixing_matrix(s12: float, s23: float, s13: float, delta: float,
                  majorana=(0.0, 0.0)) -> np.ndarray:
    """PDG convention U=R23 U13(delta) R12 diag(e^(ia1/2),e^(ia2/2),1)."""
    if len(majorana) != 2 or not all(
            math.isfinite(x) for x in (s12, s23, s13, delta, *majorana)):
        raise ValueError("finite angles and two finite Majorana phases required")
    if not all(0.0 <= s <= 1.0 for s in (s12, s23, s13)):
        raise ValueError("sines must lie in [0,1]")
    c12, c23, c13 = (math.sqrt(1-s*s) for s in (s12, s23, s13))
    z = np.exp(1j * delta)
    u = np.array([
        [c12*c13, s12*c13, s13/z],
        [-s12*c23-c12*s23*s13*z, c12*c23-s12*s23*s13*z, s23*c13],
        [s12*s23-c12*c23*s13*z, -c12*s23-s12*c23*s13*z, c23*c13],
    ], dtype=complex)
    return u @ np.diag([np.exp(0.5j*majorana[0]),
                        np.exp(0.5j*majorana[1]), 1.0])


def ckm_from_moduli(vus, vcb, vub, delta):
    """Preserve exactly the three input entry magnitudes, not angle sines."""
    if not all(math.isfinite(x) and 0 <= x < 1 for x in (vus, vcb, vub)):
        raise ValueError("finite entry magnitudes in [0,1) required")
    c13 = math.sqrt(1-vub*vub)
    return mixing_matrix(vus/c13, vcb/c13, vub, delta)


def jarlskog(u):
    return float(np.imag(u[0, 0]*u[1, 1]*u[0, 1].conjugate()*u[1, 0].conjugate()))


def pmns_texture(delta=8*math.pi/7, majorana=(0.0, 0.0)):
    zp2 = 1/(2*math.pi)**2
    return mixing_matrix(math.sqrt(3/10), math.sqrt(0.5+2*zp2),
                         math.sqrt(zp2*math.sqrt(3)/2), delta, majorana)


def neutrino_operators(masses_eV, *, delta=8*math.pi/7, majorana=(0.0, 0.0)):
    """Majorana Takagi texture M and vacuum oscillation numerator H2.

    U.T M U = diag(m_i); H_vac=H2/(2E), in consistent energy units.
    The scalar solar-tilt comparison is deliberately not substituted into
    this rest-mass operator: such a propagation correction needs its own
    Hamiltonian. H2 is independent of the two Majorana phases.
    """
    masses = np.asarray(masses_eV, dtype=float)
    if masses.shape != (3,) or not np.all(np.isfinite(masses)) or np.any(masses < 0):
        raise ValueError("three finite nonnegative labelled masses required")
    u = pmns_texture(delta, majorana)
    m = u.conj() @ np.diag(masses) @ u.conj().T
    h2 = u @ np.diag(masses**2) @ u.conj().T
    return {"U": u, "M_eV": m, "H2_eV2": h2,
            "takagi_residual_eV": float(np.max(np.abs(u.T @ m @ u-np.diag(masses)))),
            "unitarity_residual": float(np.max(np.abs(u.conj().T @ u-np.eye(3)))),
            "J": jarlskog(u)}


def evaluate_records(records):
    """Read-only extension of one completed run, using zero Majorana phases."""
    def v(key):
        return float(records[key]["value"])
    alpha, tau = v("alpha_up"), v("tau")
    kappa = math.sqrt((1+2*tau)/(1-4*tau)**2.5)
    vus = math.sqrt(v("md_over_ms_geo"))
    vcb = math.exp(-alpha)/2*(1-2*tau*kappa)
    vub = math.exp(-2*alpha)/2*(1+tau*kappa)
    ck = ckm_from_moduli(vus, vcb, vub, v("ckm_delta_direction"))
    nu = neutrino_operators([v("m_nu1"), v("m_nu2"), v("m_nu3")],
                           delta=math.pi*v("cp_pmns_87_pattern"))
    exact_j = jarlskog(ck)
    return {
        "scope": "unitary completion of the retained texture; zero Majorana phases as an explicit example",
        "ckm_unitarity_residual": float(np.max(np.abs(ck.conj().T@ck-np.eye(3)))),
        "ckm_moduli": np.abs(ck).tolist(),
        "ckm_J_exact": exact_j,
        "ckm_J_retained": v("cp_jarlskog_magnitude"),
        "ckm_J_relative_change": exact_j/v("cp_jarlskog_magnitude")-1,
        "pmns_moduli": np.abs(nu["U"]).tolist(),
        "pmns_J": nu["J"],
        "pmns_unitarity_residual": nu["unitarity_residual"],
        "takagi_residual_eV": nu["takagi_residual_eV"],
        "mass_matrix_real_eV": nu["M_eV"].real.tolist(),
        "mass_matrix_imag_eV": nu["M_eV"].imag.tolist(),
        "oscillation_H2_real_eV2": nu["H2_eV2"].real.tolist(),
        "oscillation_H2_imag_eV2": nu["H2_eV2"].imag.tolist(),
    }
