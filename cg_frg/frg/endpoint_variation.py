"""Differentiate the TT survival profile and the Gaussian action separately.

A mass-dependent kernel extremum is not an equation of motion for that mass.
The functions below retain the variable being varied and the actual trace
weight.  A common physical mass gives a different y for each spectral q^2.
"""
from fractions import Fraction as Q
import math


def survival_stationary_geometry():
    """Exact profile data: rho=y-2y^2+y^3, rho'=(1-y)(1-3y).

    On [0,1], the only interior stationary point is 1/3, and
    4/27-rho=(y-1/3)^2*(4/3-y) proves the unique global maximum.
    The endpoint 1 is stationary too; it has response zero.
    """
    return {"profile_coefficients": (Q(0), Q(1), Q(-2), Q(1)),
            "derivative_coefficients": (Q(1), Q(-4), Q(3)),
            "interior_stationary_point": Q(1, 3),
            "maximum": Q(4, 27), "curvature": Q(-2),
            "boundary_stationary_point": Q(1)}


def gaussian_mode_action(y, weight=1.0):
    """Relative 1/2 Tr log(q^2+m^2) at fixed q^2>0.

    y=m^2/(q^2+m^2), so S(y)-S(0)=-weight*log(1-y)/2.
    A signed weight can represent a supertrace contribution; the scalar
    example alone suffices to distinguish a determinant from its TT kernel.
    """
    if not (math.isfinite(y) and 0 <= y < 1 and math.isfinite(weight)):
        raise ValueError("finite weight and 0 <= y < 1 required")
    return -weight*math.log1p(-y)/2


def gaussian_mode_action_derivative(y, weight=1.0):
    if not (math.isfinite(y) and 0 <= y < 1 and math.isfinite(weight)):
        raise ValueError("finite weight and 0 <= y < 1 required")
    return weight/(2*(1-y))


def mass_stationarity_terms(q_squared, weights, mass_squared):
    """Actual mass derivative and TT response of a finite Gaussian trace.

    S'=1/2 sum w/(q^2+m^2) and rho(q)=m^2*q^4/(q^2+m^2)^3.
    The trace is a fixed finite set here; moving cutoffs require their
    boundary derivative in addition to this finite-dimensional variation.
    """
    if len(q_squared) != len(weights) or not q_squared:
        raise ValueError("nonempty spectral values and matching weights required")
    if not math.isfinite(mass_squared) or mass_squared < 0:
        raise ValueError("nonnegative finite mass squared required")
    if any(not math.isfinite(q) or q <= 0 for q in q_squared):
        raise ValueError("positive finite spectral values required")
    if any(not math.isfinite(w) for w in weights):
        raise ValueError("finite trace weights required")
    ys = tuple(mass_squared/(q+mass_squared) for q in q_squared)
    return {
        "mode_y": ys,
        "mass_action_derivative": sum(w/(q+mass_squared)/2
                                      for q, w in zip(q_squared, weights)),
        "survival_response": sum(w*y*(1-y)**2 for y, w in zip(ys, weights)),
        "survival_mass_derivative": sum(
            w*(1-y)*(1-3*y)*q/(q+mass_squared)**2
            for q, w, y in zip(q_squared, weights, ys)),
    }


def four_dimensional_loop_measure():
    """Derive the radial 1/2-logdet measure, including the angular Jacobian.

    (1/2) * area(S^3)/(2*pi)^4 * r^3 dr
    = (1/(32*pi^2)) * z dz, z=r^2.
    This loop measure does not fix a gravitational kinetic coefficient,
    a TT vertex, or the endpoint equation's separate normalization.
    """
    sphere_area = 2*math.pi**2
    radial_coefficient = Q(1, 2)*sphere_area/(2*math.pi)**4*Q(1, 2)
    return {"unit_three_sphere_area": sphere_area,
            "logdet_factor": Q(1, 2), "r3_dr_to_z_dz_factor": Q(1, 2),
            "coefficient": radial_coefficient,
            "coefficient_times_pi_squared": Q(1, 32)}
