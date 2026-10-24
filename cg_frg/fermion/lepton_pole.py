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

"""Conditional charged-lepton mass-conversion diagnostics.

This module does not derive the matching of a generated mass vertex to a
renormalized action.  The generic solver evaluates the supplied mass equation

    M_l = m_l^geom + delta M_l(M_l),

where ``delta M_l`` is supplied by the caller.  Scheme, scale and boundary
source identify the declared calculation; their presence does not prove that
its matching follows from the generated action.  No observed pole mass is
read here.

The self-energy is intentionally a callable: the weak, Higgs and threshold
terms belong to the action-level calculation and are not reconstructed from
target masses.  A missing scheme or boundary source is an error, not a
silent tree-level identification.  The MSbar diagnostic below reports the
strict first-order inverse separately from its implicit fixed point.  Solving
a one-loop-truncated equation does not supply the complete higher orders.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import math


DEFAULT_LABELS = ("e", "mu", "tau")
DEFAULT_WEIGHTS = (-1.0, 2.0, -1.0)


def lepton_mass_vertex_response(
    mass_vertex_GeV, left_gram, right_gram, *, delta_mass_vertex_GeV,
    delta_left_gram, delta_right_gram, action_source: str,
) -> dict:
    """Differentiate the same action's canonical three-family mass vertex.

    For B(eps), K_L(eps), K_R(eps), differentiate
    M = K_L**(-1/2) B K_R**(-1/2) at eps=0. B already contains the
    scalar amplitude; its variation belongs in delta_mass_vertex_GeV,
    and no additional Higgs/VEV normalization is inserted.
    The three supplied deltas must be derivatives with respect to the same
    parameter in the same fixed field coordinates. In a canonical tree
    basis this reduces to dM = dB - dK_L M/2 - M dK_R/2.

    Eigenvalue divided differences evaluate the inverse-square-root
    derivative, including noncommuting kinetic forms and repeated kinetic
    eigenvalues. For simple nonzero singular values m_i, dlog(m_i) is
    Re(u_i^dagger dM v_i)/m_i. Its (-1,2,-1) combination is independent
    of fixed invertible field coordinates. Degenerate mass labels are
    rejected, since their individual derivatives need a separate splitting.

    This computes a response, not its loop coefficients. It is a finite
    generated-to-EFT matching correction only when the supplied deltas are
    that independently calculated amplitude difference, with shared EFT
    loops subtracted. In particular a source susceptibility is not silently
    substituted for a spacetime kinetic coefficient.
    """
    import numpy as np
    from cg_core.matter_matching import inverse_sqrt_gram

    action_source = _text("action_source", action_source)

    def matrix(value, name):
        result = np.asarray(value, dtype=complex)
        if result.shape != (3, 3) or not np.isfinite(result).all():
            raise ValueError(f"{name} must be a finite 3 by 3 matrix")
        return result

    def kinetic_response(gram, delta, name):
        gram = matrix(gram, name)
        delta = matrix(delta, "delta " + name)
        if not np.allclose(delta, delta.conj().T, rtol=1e-11, atol=1e-13):
            raise ValueError(f"delta {name} must be Hermitian")
        inverse = inverse_sqrt_gram(gram)
        eigenvalues, vectors = np.linalg.eigh(gram)
        roots = np.sqrt(eigenvalues)
        # (x^(-1/2)-y^(-1/2))/(x-y), with its continuous diagonal value.
        divided = -1.0 / (roots[:, None] * roots[None, :]
                          * (roots[:, None] + roots[None, :]))
        derivative = vectors @ (divided * (vectors.conj().T @ delta @ vectors)) @ vectors.conj().T
        return inverse, derivative

    vertex = matrix(mass_vertex_GeV, "mass vertex")
    delta_vertex = matrix(delta_mass_vertex_GeV, "delta mass vertex")
    left, delta_left = kinetic_response(left_gram, delta_left_gram, "left kinetic form")
    right, delta_right = kinetic_response(right_gram, delta_right_gram, "right kinetic form")
    mass = left @ vertex @ right
    terms = {"mass_vertex": left @ delta_vertex @ right,
             "left_kinetic": delta_left @ vertex @ right,
             "right_kinetic": left @ vertex @ delta_right}
    u, values, vh = np.linalg.svd(mass, full_matrices=False)
    values, u, v = values[::-1], u[:, ::-1], vh.conj().T[:, ::-1]
    floor = 32 * np.finfo(float).eps * values[-1]
    if values[0] <= floor or np.any(np.diff(values) <= floor):
        raise ValueError("three resolved, positive, distinct mass singular values required")
    logs = {name: np.real(np.diag(u.conj().T @ term @ v)) / values
            for name, term in terms.items()}
    total = sum(logs.values())
    weighted = lambda x: math.fsum(w * float(a) for w, a in zip(DEFAULT_WEIGHTS, x))
    return {
        "species_order": list(DEFAULT_LABELS),
        "masses_GeV": dict(zip(DEFAULT_LABELS, map(float, values))),
        "dlog_masses": dict(zip(DEFAULT_LABELS, map(float, total))),
        "dlog_components": {name: dict(zip(DEFAULT_LABELS, map(float, value)))
                             for name, value in logs.items()},
        "weighted_log_response": weighted(total),
        "weighted_log_components": {name: weighted(value) for name, value in logs.items()},
        "canonical_mass_vertex_GeV": mass,
        "delta_canonical_mass_vertex_GeV": sum(terms.values()),
        "action_source": action_source,
        "scalar_amplitude_included_in_mass_vertex": True,
    }


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
    ``tolerance`` bounds both the relative last step and the relative
    equation residual; neither criterion introduces a fixed mass scale.

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

    def finite_shift(mass):
        shift = self_energy(mass)
        try:
            shift = float(shift)
        except (TypeError, ValueError) as exc:
            raise ValueError("self_energy must return a finite real shift") from exc
        if not math.isfinite(shift):
            raise ValueError("self_energy returned a non-finite shift")
        return shift

    mass = m_geom
    for iteration in range(1, max_iterations + 1):
        shift = finite_shift(mass)
        new_mass = m_geom + shift
        if not math.isfinite(new_mass) or new_mass <= 0.0:
            raise ValueError("self-energy iteration left the positive mass branch")
        relative_step = abs(new_mass - mass) / max(new_mass, mass)
        if relative_step <= tol:
            final_shift = finite_shift(new_mass)
            equation_mass = m_geom + final_shift
            if not math.isfinite(equation_mass) or equation_mass <= 0.0:
                raise ValueError("self-energy iteration left the positive mass branch")
            residual = new_mass - equation_mass
            relative_residual = abs(residual) / max(new_mass, equation_mass)
            if relative_residual <= tol:
                return {
                    "geometric_mass_GeV": m_geom,
                    "pole_mass_GeV": new_mass,
                    "G": new_mass / m_geom,
                    "self_energy_GeV": final_shift,
                    "residual_GeV": residual,
                    "relative_residual": relative_residual,
                    "relative_step": relative_step,
                    "iterations": iteration,
                    "scheme": scheme,
                    "scale_GeV": scale,
                    "boundary_source": boundary_source,
                    "order": "implicit mass equation; shift order supplied by caller",
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
    if not all(math.isfinite(w) for w in weights):
        raise ValueError("weights must be finite")
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
        "order": "implicit mass equations; shift order supplied by caller",
    }

def geometric_to_pole_one_loop(
    geometric_masses_GeV: Mapping[str, float],
    gauge_couplings,
    vev_GeV: float,
    *,
    higgs_mass_GeV: float,
    scale_GeV: float,
    input_scheme: str,
    action_source: str,
    labels: Sequence[str] = DEFAULT_LABELS,
    weights: Sequence[float] = DEFAULT_WEIGHTS,
    tolerance: float = 1e-11,
    max_iterations: int = 40,
) -> dict:
    """Conditional MSbar conversion using the existing one-loop mass kernel.

    This is the declared matching convention of this function: the generated
    geometric mass is the ``MSbar`` mass at ``scale_GeV`` in the common Landau
    action.  The pole mass is then the fixed point of the existing V5
    charged-lepton kernel,

        mbar_l(Q) = M_l * (1 + delta_l(M_l)),

    solved by iteration on M_l.  The kernel is the same one-loop V5
    calculation used for the pole-to-running factors; no observed mass enters.
    ``first_order`` contains the perturbatively expanded inverse, evaluated
    at the zeroth-order masses.  The top-level poles and ``Delta_L`` instead
    solve the truncated relation implicitly and retain some higher-order
    terms.  Their difference is a diagnostic, not a higher-order error bound.
    A different geometric-mass scheme must be implemented separately rather
    than hidden in this conversion.  This function does not establish that
    the generated vertex has the declared MSbar boundary value.
    """
    if input_scheme != "MSbar_at_scale":
        raise ValueError("input_scheme must be 'MSbar_at_scale'")
    labels = tuple(labels)
    weights = tuple(float(w) for w in weights)
    if len(labels) != 3 or len(weights) != 3:
        raise ValueError("exactly three charged-lepton labels and weights are required")
    if len(set(labels)) != 3:
        raise ValueError("charged-lepton labels must be distinct")
    if not all(math.isfinite(w) for w in weights):
        raise ValueError("weights must be finite")
    if abs(sum(weights)) > 1e-15:
        raise ValueError("Delta_L weights must sum to zero")
    if set(geometric_masses_GeV) != set(labels):
        raise ValueError("geometric mass map must contain exactly the requested labels")
    action_source = _text("action_source", action_source)
    scale_GeV = _positive("scale_GeV", scale_GeV)
    vev_GeV = _positive("vev_GeV", vev_GeV)
    higgs_mass_GeV = _positive("higgs_mass_GeV", higgs_mass_GeV)
    if not math.isfinite(float(tolerance)) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive")
    if not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("max_iterations must be a positive integer")

    from cg_core.matter_matching import charged_lepton_pole_matching_one_loop

    species = ("electron", "muon", "tau")
    mapping = dict(zip(labels, species))
    reverse = {v: k for k, v in mapping.items()}
    geometric = {name: _positive(f"geometric mass {name}", geometric_masses_GeV[label])
                 for label, name in mapping.items()}
    leading_kernel = charged_lepton_pole_matching_one_loop(
        geometric, gauge_couplings, vev_GeV,
        higgs_mass_GeV=higgs_mass_GeV, scale_GeV=scale_GeV,
        input_definition="generated_on_shell_conditions",
        action_source=action_source,
    )
    first_order_logs = {
        label: -leading_kernel["log_matching_factors"][name]
        for label, name in mapping.items()
    }
    first_order = {
        "leptons": {
            label: {
                "log_G_first_order": first_order_logs[label],
                "G_first_order": 1.0 + first_order_logs[label],
                "pole_mass_GeV_first_order": geometric[name] * (1.0 + first_order_logs[label]),
            }
            for label, name in mapping.items()
        },
        "Delta_L": math.fsum(weight * first_order_logs[label]
                             for label, weight in zip(labels, weights)),
        "order": "strict first order; inverse masses and logarithms expanded consistently",
    }
    poles = dict(geometric)
    kernel = None
    for iteration in range(1, max_iterations + 1):
        kernel = charged_lepton_pole_matching_one_loop(
            poles, gauge_couplings, vev_GeV,
            higgs_mass_GeV=higgs_mass_GeV, scale_GeV=scale_GeV,
            input_definition="generated_on_shell_conditions",
            action_source=action_source,
        )
        running = kernel["running_masses_GeV_first_order"]
        updated = {}
        for name in species:
            candidate = poles[name] * geometric[name] / float(running[name])
            if not math.isfinite(candidate) or candidate <= 0.0:
                raise ValueError("one-loop pole iteration left the positive branch")
            updated[name] = candidate
        change = max(abs(updated[name] - poles[name]) / max(abs(updated[name]), 1e-300)
                     for name in species)
        poles = updated
        if change <= tolerance:
            break
    else:
        raise RuntimeError("one-loop geometric-to-pole iteration did not converge")

    if kernel is None:
        raise RuntimeError("one-loop kernel was not evaluated")
    # Final kernel at the converged pole masses, for the residual and terms.
    kernel = charged_lepton_pole_matching_one_loop(
        poles, gauge_couplings, vev_GeV,
        higgs_mass_GeV=higgs_mass_GeV, scale_GeV=scale_GeV,
        input_definition="generated_on_shell_conditions",
        action_source=action_source,
    )
    running = kernel["running_masses_GeV_first_order"]
    leptons = {}
    logs = {}
    for name in species:
        label = reverse[name]
        G = poles[name] / geometric[name]
        residual = (float(running[name]) - geometric[name]) / geometric[name]
        leptons[label] = {
            "geometric_mass_GeV": geometric[name],
            "pole_mass_GeV": poles[name],
            "G": G,
            "log_G": math.log(G),
            "running_residual": residual,
            "log_matching_factor": kernel["log_matching_factors"][name],
            "log_matching_components": kernel["log_matching_components"][name],
        }
        logs[label] = math.log(G)
    delta_L = sum(weight * logs[label] for label, weight in zip(labels, weights))
    return {
        "leptons": leptons,
        "Delta_L": delta_L,
        "common_log_G": sum(logs.values()) / 3.0,
        "nonuniversal_log_spread": max(logs.values()) - min(logs.values()),
        "weights": dict(zip(labels, weights)),
        "input_scheme": input_scheme,
        "scale_GeV": float(scale_GeV),
        "action_source": action_source,
        "iterations": iteration,
        "convergence": change,
        "first_order": first_order,
        "implicit_minus_first_order_Delta_L": delta_L - first_order["Delta_L"],
        "pole_kernel_order": kernel["order"],
        "uncomputed_orders": kernel["uncomputed_orders"],
        "order": "implicit inversion of a one-loop-truncated mass relation",
        "generated_vertex_matching_derived": False,
        "production_replacement": False,
    }
