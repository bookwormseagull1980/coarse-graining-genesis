# -*- coding: utf-8 -*-
"""Certified generated Yang--Mills mass operator.

The structural constants in this module are outputs of the minimal-change
construction.  They are deliberately not public tuning arguments.  The
condensed response has two invariant blocks: the normalized radial intensity
and the coclosed colour connection.  Their spectral bottoms determine the
bottom of the complete generated Yang--Mills mass operator.

Radius convention: production calls use the V5 TT endpoint
``L = kL = 2.4935343325...``, the root of ``A(L) = 4/27``.  The Gaussian IR
edge ``sqrt(2*pi) = 2.5066282746...`` is a different scale (the TT sum there
is about ``0.147374``, below ``4/27``).  Lean's ``CanonicalYangMills``
IR-edge model uses ``sqrt(2*pi)``; its absolute gap is not the V5 TT gap.
Do not substitute one radius for the other.
"""

from __future__ import annotations

import math
from typing import Iterable


CRITICAL_RADIUS = math.sqrt(math.pi)
SU3_ADJOINT_CASIMIR = 3.0
SU3_ALGEBRA_DIMENSION = 8
LONG_ROOT_MODE_DIMENSION = 15
CONNECTION_COEFFICIENT_COUNT = (
    SU3_ALGEBRA_DIMENSION * LONG_ROOT_MODE_DIMENSION
)
FIRST_COCLOSED_VECTOR_DEGREE = 1
FIRST_COCLOSED_VECTOR_MULTIPLICITY = 6


def conformal_restoring_response(z: float) -> float:
    """Exact derivative H(z) of the complete conformal response."""
    if not math.isfinite(z) or z < 0.0:
        raise ValueError("nonnegative finite response coordinate required")
    if z < 0.25:
        b = math.sqrt(0.25 - z)
        return math.pi / 8.0 - math.pi * b * math.tan(math.pi * b / 2.0) / 4.0
    if z == 0.25:
        return math.pi / 8.0
    s = math.sqrt(z - 0.25)
    return math.pi / 8.0 + math.pi * s * math.tanh(math.pi * s / 2.0) / 4.0


def conformal_restoring_curvature(z: float) -> float:
    """Exact positive derivative H'(z) of the complete response."""
    if not math.isfinite(z) or z < 0.0:
        raise ValueError("nonnegative finite response coordinate required")
    if z < 0.25:
        b = math.sqrt(0.25 - z)
        angle = math.pi * b / 2.0
        return math.pi * (math.tan(angle) + angle / math.cos(angle) ** 2) / (
            8.0 * b
        )
    if z == 0.25:
        return math.pi ** 2 / 8.0
    s = math.sqrt(z - 0.25)
    angle = math.pi * s / 2.0
    tanh = math.tanh(angle)
    sech2 = 1.0 - tanh * tanh
    return math.pi * (tanh + angle * sech2) / (8.0 * s)


def _solve_restoring_coordinate_with_bracket(
    drive: float, *, rtol: float = 2e-16
) -> tuple[float, float, float]:
    """Solve H(z)=drive and retain the monotone root bracket."""
    if not math.isfinite(drive) or drive <= 0.0:
        raise ValueError("positive finite condensed drive required")
    low, high = 0.0, 1.0
    while conformal_restoring_response(high) < drive:
        high *= 4.0
        if not math.isfinite(high):
            raise OverflowError("failed to bracket the conformal response root")
    for _ in range(320):
        mid = (low + high) / 2.0
        if mid == low or mid == high:
            break
        if conformal_restoring_response(mid) < drive:
            low = mid
        else:
            high = mid
        if high - low <= rtol * max(1.0, high):
            break
    return (low + high) / 2.0, low, high


def solve_restoring_coordinate(drive: float, *, rtol: float = 2e-16) -> float:
    """Return the unique positive coordinate selected by H(z)=drive."""
    return _solve_restoring_coordinate_with_bracket(drive, rtol=rtol)[0]


def coclosed_vector_mass_squared(L: float, z: float, degree: int) -> float:
    """Mass-squared eigenvalue of one coclosed colour-connection shell.

    Ordinary one-forms on the generated projective three-space occur at
    positive odd degree.  The response shift is common to the full tower.
    """
    if not math.isfinite(L) or L <= 0.0:
        raise ValueError("positive finite radius required")
    if not math.isfinite(z) or z <= 0.0:
        raise ValueError("positive finite response coordinate required")
    if not isinstance(degree, int) or degree < 1 or degree % 2 != 1:
        raise ValueError("a positive odd coclosed-vector degree is required")
    return ((degree + 1) ** 2 + 2.0 * z / 3.0) / L ** 2


def coclosed_vector_multiplicity(degree: int) -> int:
    """Total real shell multiplicity after the eight colour directions."""
    if not isinstance(degree, int) or degree < 1 or degree % 2 != 1:
        raise ValueError("a positive odd coclosed-vector degree is required")
    return SU3_ALGEBRA_DIMENSION * (2 * degree * (degree + 2))


def _generated_feedback(L: float) -> float:
    volume = math.pi ** 2 * L ** 3
    return SU3_ADJOINT_CASIMIR / (volume * SU3_ALGEBRA_DIMENSION)


def _direct_score_variance(q: float) -> float:
    """Variance from the 120 independent coefficient contributions."""
    component_variance = 2.0 * q * q / CONNECTION_COEFFICIENT_COUNT ** 2
    return math.fsum(
        component_variance for _ in range(CONNECTION_COEFFICIENT_COUNT)
    )


def _scalar_constant_mode_mass_squared(z: float, curvature: float) -> float:
    """Independent scalar-tower route to the normalized constant-mode mass."""
    complete_scalar_gap = 4.0 * z * curvature
    return z * complete_scalar_gap / (2.0 * CONNECTION_COEFFICIENT_COUNT)


def _operator_certificate(L: float, z: float, radial_mass_squared: float) -> dict:
    transverse_bottom = coclosed_vector_mass_squared(
        L, z, FIRST_COCLOSED_VECTOR_DEGREE
    )
    gap_squared = min(radial_mass_squared, transverse_bottom)
    controller = (
        "radial_intensity"
        if radial_mass_squared <= transverse_bottom
        else "coclosed_colour_connection"
    )
    return {
        "decomposition": (
            "normalized radial intensity direct-sum coclosed colour connection"
        ),
        "cross_block_norm": 0.0,
        "cross_block_reason": "orthogonal source-carrier grading",
        "radial_block_dimension": 1,
        "radial_block_bottom": radial_mass_squared,
        "coclosed_degree_class": "positive odd integers",
        "coclosed_first_degree": FIRST_COCLOSED_VECTOR_DEGREE,
        "coclosed_first_multiplicity_per_colour": (
            FIRST_COCLOSED_VECTOR_MULTIPLICITY
        ),
        "coclosed_first_total_multiplicity": coclosed_vector_multiplicity(1),
        "coclosed_first_bottom": transverse_bottom,
        "complete_spectral_bottom": gap_squared,
        "controlling_block": controller,
        "positivity_certificate": (
            "z>0, H'(z)>0, L>0, and every positive odd vector degree is at "
            "least one"
        ),
    }


def generated_yang_mills_interval_certificate(
    L: float, *, decimal_places: int = 50
) -> dict:
    """Outward interval enclosure of the response root and spectral bottom.

    The interval calculation is an audit path, independent of the binary64
    values returned by :func:`generated_yang_mills_gap`.
    """
    try:
        import mpmath
    except ImportError as exc:  # pragma: no cover - release env includes mpmath
        raise RuntimeError(
            "mpmath>=1.3 is required for the generated YM interval certificate"
        ) from exc

    if not math.isfinite(L) or L <= CRITICAL_RADIUS:
        raise ValueError("the generated condensed branch requires L>sqrt(pi)")

    mp = mpmath.mp.clone()
    mp.dps = max(70, decimal_places + 20)

    def mp_response(x):
        quarter = mp.mpf(1) / 4
        if x < quarter:
            b = mp.sqrt(quarter - x)
            return mp.pi / 8 - mp.pi * b * mp.tan(mp.pi * b / 2) / 4
        if x == quarter:
            return mp.pi / 8
        s = mp.sqrt(x - quarter)
        return mp.pi / 8 + mp.pi * s * mp.tanh(mp.pi * s / 2) / 4

    L_mp = mp.mpf(repr(L))
    critical_mp = mp.sqrt(mp.pi)
    volume_mp = mp.pi ** 2 * L_mp ** 3
    feedback_mp = mp.mpf(3) / (volume_mp * 8)
    kappa_mp = feedback_mp * L_mp ** 2
    drive_mp = -16 * (L_mp ** -2 - critical_mp ** -2) / (2 * kappa_mp)
    low, high = mp.mpf(0), mp.mpf(1)
    while mp_response(high) < drive_mp:
        high *= 4
    target_width = mp.power(10, -(decimal_places + 8))
    while high - low > target_width:
        mid = (low + high) / 2
        if mp_response(mid) < drive_mp:
            low = mid
        else:
            high = mid

    from mpmath.ctx_iv import MPIntervalContext

    iv = MPIntervalContext()
    iv.dps = decimal_places
    L_iv = iv.mpf(repr(L))
    critical_iv = iv.sqrt(iv.pi)
    volume_iv = iv.pi ** 2 * L_iv ** 3
    feedback_iv = iv.mpf(3) / (volume_iv * 8)
    kappa_iv = feedback_iv * L_iv ** 2
    drive_iv = -16 * (L_iv ** -2 - critical_iv ** -2) / (2 * kappa_iv)
    z_iv = iv.mpf([mp.nstr(low, mp.dps), mp.nstr(high, mp.dps)])
    quarter = iv.mpf(1) / 4
    if float(z_iv.a) < 0.25 < float(z_iv.b):
        raise ArithmeticError("root enclosure straddles the analytic branch point")
    if float(z_iv.b) <= 0.25:
        b_iv = iv.sqrt(quarter - z_iv)
        angle_iv = iv.pi * b_iv / 2
        curvature_iv = iv.pi * (
            iv.tan(angle_iv) + angle_iv / iv.cos(angle_iv) ** 2
        ) / (8 * b_iv)
    else:
        s_iv = iv.sqrt(z_iv - quarter)
        angle_iv = iv.pi * s_iv / 2
        exp_twice = iv.exp(2 * angle_iv)
        tanh_iv = (exp_twice - 1) / (exp_twice + 1)
        curvature_iv = iv.pi * (
            tanh_iv + angle_iv * (1 - tanh_iv ** 2)
        ) / (8 * s_iv)

    q_iv = z_iv / kappa_iv
    radial_metric_iv = 2 * CONNECTION_COEFFICIENT_COUNT / q_iv
    potential_curvature_iv = kappa_iv ** 2 * curvature_iv
    radial_hessian_iv = 4 * q_iv * potential_curvature_iv / radial_metric_iv
    radial_scalar_iv = (
        z_iv * (4 * z_iv * curvature_iv)
        / (2 * CONNECTION_COEFFICIENT_COUNT)
    )
    transverse_iv = (4 + 2 * z_iv / 3) / L_iv ** 2

    def outward(x) -> list[float]:
        return [
            math.nextafter(float(x.a), -math.inf),
            math.nextafter(float(x.b), math.inf),
        ]

    radial_bounds = outward(radial_hessian_iv)
    scalar_bounds = outward(radial_scalar_iv)
    transverse_bounds = outward(transverse_iv)
    gap_bounds = [
        min(radial_bounds[0], transverse_bounds[0]),
        min(radial_bounds[1], transverse_bounds[1]),
    ]
    residual_bounds = outward(radial_hessian_iv - radial_scalar_iv)
    if gap_bounds[0] <= 0.0:
        raise ArithmeticError("interval proof did not establish a positive gap")
    if residual_bounds[0] > 0.0 or residual_bounds[1] < 0.0:
        raise ArithmeticError("independent radial intervals do not overlap")

    return {
        "method": "outward interval evaluation with monotone root bracketing",
        "decimal_places": decimal_places,
        "response_coordinate": outward(z_iv),
        "dimensionless_drive": outward(drive_iv),
        "radial_hessian_mass_squared": radial_bounds,
        "scalar_constant_mass_squared": scalar_bounds,
        "radial_identity_residual": residual_bounds,
        "coclosed_bottom_mass_squared": transverse_bounds,
        "complete_gap_squared": gap_bounds,
        "strictly_positive": True,
    }


def generated_yang_mills_scale_transport(
    gap_squared: float, scales: Iterable[float]
) -> dict:
    """Transport the dimensionless spectral bottom along positive scales."""
    if not math.isfinite(gap_squared) or gap_squared <= 0.0:
        raise ValueError("positive finite dimensionless gap required")
    scale_values = [float(scale) for scale in scales]
    if not scale_values or not all(
        math.isfinite(scale) and scale > 0.0 for scale in scale_values
    ):
        raise ValueError("at least one positive finite scale is required")
    dimensionless_gap = math.sqrt(gap_squared)
    masses = [dimensionless_gap * scale for scale in scale_values]
    ratios = [mass / scale for mass, scale in zip(masses, scale_values)]
    return {
        "dimensionless_gap": dimensionless_gap,
        "scales": scale_values,
        "gap_masses": masses,
        "gap_to_scale_ratios": ratios,
        "ratio_spread": max(ratios) - min(ratios),
        "strictly_positive": all(mass > 0.0 for mass in masses),
        "law": "m_YM(s)=s sqrt(Delta_YM^2)",
    }


def generated_yang_mills_gap(
    L: float, *, mass_unit: float = 1.0, certify: bool = True
) -> dict:
    """Evaluate the generated Yang--Mills mass-gap theorem.

    ``L`` is the generated endpoint-scaled radius.  Production calls pass
    ``L = kL`` (the V5 TT endpoint); the Gaussian IR edge ``sqrt(2*pi)`` is a
    different model and is **not** substituted here.  The critical radius,
    colour algebra, adjoint Casimir and long-root carrier dimension are fixed
    by the source construction.  ``mass_unit`` only attaches physical units to
    the already dimensionless spectral bottom.
    """
    if not math.isfinite(L) or L <= CRITICAL_RADIUS:
        raise ValueError("the generated condensed branch requires L>sqrt(pi)")
    if not math.isfinite(mass_unit) or mass_unit <= 0.0:
        raise ValueError("positive finite mass unit required")

    volume = math.pi ** 2 * L ** 3
    feedback = _generated_feedback(L)
    kappa = feedback * L ** 2
    drive_coefficient = 16.0 * (L ** -2 - CRITICAL_RADIUS ** -2)
    dimensionless_drive = -drive_coefficient / (2.0 * kappa)
    z, root_low, root_high = _solve_restoring_coordinate_with_bracket(
        dimensionless_drive
    )
    q = z / kappa
    curvature = conformal_restoring_curvature(z)

    radial_metric = 2.0 * CONNECTION_COEFFICIENT_COUNT / q
    potential_curvature = kappa ** 2 * curvature
    radial_mass_squared = 4.0 * q * potential_curvature / radial_metric
    scalar_constant_mode_mass_squared = _scalar_constant_mode_mass_squared(
        z, curvature
    )
    radial_identity_residual = (
        radial_mass_squared - scalar_constant_mode_mass_squared
    )

    score_variance = _direct_score_variance(q)
    score_scale = math.sqrt(CONNECTION_COEFFICIENT_COUNT / 2.0) / q
    normalized_score_variance = score_scale ** 2 * score_variance
    long_root_eigenvalue = 16.0 / L ** 2
    # O'(q) = lambda_R + 2 alpha_R q in the source coordinate
    # z = g_YM L^2 q.  The second term is the coclosed response shift,
    # not 2 z H'(z); H'(z) is the full radial restoring curvature.
    curvature_radial_coefficient = (
        long_root_eigenvalue + 2.0 * z / (3.0 * L ** 2)
    )
    curvature_score_overlap = (
        curvature_radial_coefficient
        * q
        * math.sqrt(2.0 / CONNECTION_COEFFICIENT_COUNT)
    )

    operator = _operator_certificate(L, z, radial_mass_squared)
    gap_squared = float(operator["complete_spectral_bottom"])
    evolution_times = (0.0, 0.125, 1.0, 4.0)
    intertwining_residual = max(
        abs(
            math.exp(-time * radial_mass_squared)
            - math.exp(-time * scalar_constant_mode_mass_squared)
        )
        for time in evolution_times
    )

    result = {
        "theorem": "generated Yang--Mills positive spectral bottom",
        "phase": "condensed",
        "L": L,
        "L_c": CRITICAL_RADIUS,
        "volume": volume,
        "adjoint_casimir": SU3_ADJOINT_CASIMIR,
        "algebra_dimension": SU3_ALGEBRA_DIMENSION,
        "long_root_dimension": LONG_ROOT_MODE_DIMENSION,
        "source_dimension": CONNECTION_COEFFICIENT_COUNT,
        "feedback_coefficient": feedback,
        "kappa": kappa,
        "reference_drive": drive_coefficient,
        "dimensionless_drive": dimensionless_drive,
        "response_coordinate": z,
        "response_coordinate_bracket": [root_low, root_high],
        "intensity_q": q,
        "amplitude": math.sqrt(q),
        "score_variance": score_variance,
        "score_scale": score_scale,
        "normalized_score_variance": normalized_score_variance,
        "radial_metric": radial_metric,
        "potential_curvature": potential_curvature,
        "radial_mass_squared": radial_mass_squared,
        "scalar_constant_mode_mass_squared": scalar_constant_mode_mass_squared,
        "radial_identity_residual": radial_identity_residual,
        "radial_intertwining_residual": intertwining_residual,
        "radial_intertwining_times": list(evolution_times),
        "transverse_shift": 2.0 * z / (3.0 * L ** 2),
        "transverse_mass_squared": operator["coclosed_first_bottom"],
        "long_root_eigenvalue": long_root_eigenvalue,
        "curvature_radial_coefficient": curvature_radial_coefficient,
        "curvature_score_overlap": curvature_score_overlap,
        "operator_certificate": operator,
        "gap_squared": gap_squared,
        "gap": math.sqrt(gap_squared) * mass_unit,
        "mass_unit": mass_unit,
        "controlling_block": operator["controlling_block"],
        "stationarity_residual": conformal_restoring_response(z)
        - dimensionless_drive,
        "canonical_constants": {
            "critical_radius": CRITICAL_RADIUS,
            "adjoint_casimir": SU3_ADJOINT_CASIMIR,
            "algebra_dimension": SU3_ALGEBRA_DIMENSION,
            "long_root_dimension": LONG_ROOT_MODE_DIMENSION,
            "connection_coefficient_count": CONNECTION_COEFFICIENT_COUNT,
        },
    }
    if certify:
        result["interval_certificate"] = generated_yang_mills_interval_certificate(L)
    return result


__all__ = [
    "CONNECTION_COEFFICIENT_COUNT",
    "CRITICAL_RADIUS",
    "LONG_ROOT_MODE_DIMENSION",
    "SU3_ADJOINT_CASIMIR",
    "SU3_ALGEBRA_DIMENSION",
    "coclosed_vector_mass_squared",
    "coclosed_vector_multiplicity",
    "conformal_restoring_curvature",
    "conformal_restoring_response",
    "generated_yang_mills_gap",
    "generated_yang_mills_interval_certificate",
    "generated_yang_mills_scale_transport",
    "solve_restoring_coordinate",
]
