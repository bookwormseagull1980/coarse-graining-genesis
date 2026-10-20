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

"""One-loop geometric-to-pole conversion for charged leptons.

The geometric masses are generated readouts.  They are not pole masses and
must not be identified with pole masses by numerical proximity.  This module
solves the on-shell fixed-point condition

    M_l = m_l^geom + delta M_l(M_l),

where ``delta M_l`` is the finite on-shell mass shift supplied by the same
generated action.  The caller must state the renormalization/matching scheme,
the scale at which the geometric readout is defined, and the physical
boundary source.  No observed pole mass is read here.

The self-energy is intentionally a callable: the weak, Higgs and threshold
terms belong to the action-level calculation and are not reconstructed from
target masses.  A missing scheme or boundary source is an error, not a
silent tree-level identification.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import math


DEFAULT_LABELS = ("e", "mu", "tau")
DEFAULT_WEIGHTS = (-1.0, 2.0, -1.0)


def _positive(name: str, value: float) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite positive number") from exc
    if not math.isfinite(x) or x <= 0.0:
        raise ValueError(f"{name} must be a finite positive number")
    return x


def _text(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value.strip()


def solve_pole_mass(
    geometric_mass_GeV: float,
    self_energy: Callable[[float], float],
    *,
    scheme: str,
    scale_GeV: float,
    boundary_source: str,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> dict:
    """Solve ``M = m_geom + delta M(M)`` for one charged lepton.

    ``self_energy(M)`` returns the finite on-shell mass shift in GeV.  The
    fixed point is evaluated by functional iteration because the shift
    depends on the pole mass being solved for.  A non-positive or
    non-finite iterate is rejected, as is failure to converge.

    The result is a derived readout: ``G = M/m_geom`` and
    ``Delta_L``-style quantities are assembled by
    :func:`charged_lepton_conversions`.
    """
    m_geom = _positive("geometric_mass_GeV", geometric_mass_GeV)
    scale = _positive("scale_GeV", scale_GeV)
    scheme = _text("scheme", scheme)
    boundary_source = _text("boundary_source", boundary_source)
    tol = float(tolerance)
    if not math.isfinite(tol) or tol <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    if not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("max_iterations must be a positive integer")
    if not callable(self_energy):
        raise TypeError("self_energy must be callable")

    mass = m_geom
    for iteration in range(1, max_iterations + 1):
        shift = self_energy(mass)
        try:
            shift = float(shift)
        except (TypeError, ValueError) as exc:
            raise ValueError("self_energy must return a finite real shift") from exc
        if not math.isfinite(shift):
            raise ValueError("self_energy returned a non-finite shift")
        new_mass = m_geom + shift
        if not math.isfinite(new_mass) or new_mass <= 0.0:
            raise ValueError("self-energy iteration left the positive mass branch")
        scale_check = max(abs(new_mass), abs(mass), 1.0)
        if abs(new_mass - mass) <= tol * scale_check:
            return {
                "geometric_mass_GeV": m_geom,
                "pole_mass_GeV": new_mass,
                "G": new_mass / m_geom,
                "self_energy_GeV": shift,
                "residual_GeV": new_mass - (m_geom + self_energy(new_mass)),
                "iterations": iteration,
                "scheme": scheme,
                "scale_GeV": scale,
                "boundary_source": boundary_source,
                "order": "one-loop on-shell fixed point",
            }
        mass = new_mass

    raise RuntimeError("charged-lepton pole iteration did not converge")


def charged_lepton_conversions(
    geometric_masses_GeV: Mapping[str, float],
    self_energies: Mapping[str, Callable[[float], float]],
    *,
    scheme: str,
    scale_GeV: float,
    boundary_source: str,
    labels: Sequence[str] = DEFAULT_LABELS,
    weights: Sequence[float] = DEFAULT_WEIGHTS,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> dict:
    """Solve all three charged-lepton poles and form ``Delta_L``.

    The default weight is ``(-1, 2, -1)`` in the order ``(e, mu, tau)``.
    A common multiplicative conversion cancels exactly because the weights
    sum to zero; only non-universal ``G_l`` can change ``Delta_L``.  The
    returned diagnostics expose that cancellation explicitly.
    """
    labels = tuple(labels)
    weights = tuple(float(w) for w in weights)
    if len(labels) != 3 or len(weights) != 3:
        raise ValueError("exactly three charged-lepton labels and weights are required")
    if len(set(labels)) != 3:
        raise ValueError("charged-lepton labels must be distinct")
    if abs(sum(weights)) > 1e-15:
        raise ValueError("Delta_L weights must sum to zero")
    if set(geometric_masses_GeV) != set(labels):
        raise ValueError("geometric mass map must contain exactly the requested labels")
    if set(self_energies) != set(labels):
        raise ValueError("self-energy map must contain exactly the requested labels")

    results = {}
    logs = {}
    for label, weight in zip(labels, weights):
        result = solve_pole_mass(
            geometric_masses_GeV[label],
            self_energies[label],
            scheme=scheme,
            scale_GeV=scale_GeV,
            boundary_source=boundary_source,
            tolerance=tolerance,
            max_iterations=max_iterations,
        )
        result["weight"] = weight
        result["log_G"] = math.log(result["G"])
        results[label] = result
        logs[label] = result["log_G"]

    delta_L = sum(weight * logs[label] for label, weight in zip(labels, weights))
    mean_log_G = sum(logs.values()) / 3.0
    spread = max(logs.values()) - min(logs.values())
    return {
        "leptons": results,
        "Delta_L": delta_L,
        "common_log_G": mean_log_G,
        "nonuniversal_log_spread": spread,
        "weights": dict(zip(labels, weights)),
        "scheme": scheme,
        "scale_GeV": float(scale_GeV),
        "boundary_source": boundary_source,
        "order": "one-loop on-shell fixed point for each charged lepton",
    }
