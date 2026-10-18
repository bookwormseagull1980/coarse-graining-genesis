# -*- coding: utf-8 -*-
"""Independent checks for the generated Yang--Mills theorem certificate."""

import inspect
import math

import pytest

from cg_frg.qcd.generated_yang_mills import (
    CONNECTION_COEFFICIENT_COUNT,
    CRITICAL_RADIUS,
    LONG_ROOT_MODE_DIMENSION,
    SU3_ADJOINT_CASIMIR,
    SU3_ALGEBRA_DIMENSION,
    coclosed_vector_mass_squared,
    conformal_restoring_curvature,
    conformal_restoring_response,
    generated_yang_mills_gap,
    generated_yang_mills_interval_certificate,
    generated_yang_mills_scale_transport,
)


def test_conformal_response_endpoints_and_curvature():
    assert conformal_restoring_response(0.0) == pytest.approx(0.0, abs=1e-15)
    assert conformal_restoring_curvature(0.0) == pytest.approx(
        math.pi * (math.pi + 2.0) / 8.0, rel=2e-15
    )
    assert conformal_restoring_response(0.25) == pytest.approx(
        math.pi / 8.0, rel=2e-15
    )
    assert conformal_restoring_curvature(0.25) == pytest.approx(
        math.pi ** 2 / 8.0, rel=2e-15
    )


@pytest.mark.parametrize("z", [1e-6, 0.1, 0.24, 0.26, 1.0, 10.0])
def test_conformal_response_is_strictly_restoring(z):
    step = max(1e-8, z * 1e-6)
    derivative = (
        conformal_restoring_response(z + step)
        - conformal_restoring_response(max(0.0, z - step))
    ) / (step if z < step else 2.0 * step)
    assert conformal_restoring_curvature(z) > 0.0
    assert derivative == pytest.approx(
        conformal_restoring_curvature(z), rel=3e-6, abs=2e-8
    )


def test_public_api_has_no_structural_tuning_arguments():
    parameters = inspect.signature(generated_yang_mills_gap).parameters
    assert tuple(parameters) == ("L", "mass_unit", "certify")
    assert CRITICAL_RADIUS == pytest.approx(math.sqrt(math.pi), rel=0.0)
    assert SU3_ADJOINT_CASIMIR == 3.0
    assert SU3_ALGEBRA_DIMENSION == 8
    assert LONG_ROOT_MODE_DIMENSION == 15
    assert CONNECTION_COEFFICIENT_COUNT == 120


@pytest.mark.parametrize(
    "L",
    [
        CRITICAL_RADIUS * (1.0 + 1e-12),
        2.0,
        2.4935343325226915,
        5.0,
        20.0,
    ],
)
def test_generated_gap_closes_independent_mass_routes(L):
    result = generated_yang_mills_gap(L, certify=False)

    assert result["phase"] == "condensed"
    assert result["reference_drive"] < 0.0
    assert result["feedback_coefficient"] > 0.0
    assert result["intensity_q"] > 0.0
    assert result["radial_metric"] > 0.0
    assert result["normalized_score_variance"] == pytest.approx(
        1.0, abs=4e-15
    )
    assert result["curvature_radial_coefficient"] > 0.0
    assert result["curvature_score_overlap"] > 0.0
    assert result["scalar_constant_mode_mass_squared"] == pytest.approx(
        result["radial_mass_squared"], rel=4e-15
    )
    assert abs(result["radial_identity_residual"]) <= (
        5e-15 * result["radial_mass_squared"]
    )
    assert result["radial_intertwining_residual"] <= 2e-15
    assert result["response_coordinate"] == pytest.approx(
        result["kappa"] * result["intensity_q"], rel=2e-15
    )
    assert result["stationarity_residual"] == pytest.approx(
        0.0, abs=3e-12
    )
    assert result["gap_squared"] == pytest.approx(
        min(
            result["radial_mass_squared"], result["transverse_mass_squared"]
        ),
        rel=2e-15,
    )
    assert result["gap_squared"] > 0.0


def test_complete_operator_certificate_covers_the_coclosed_tower():
    result = generated_yang_mills_gap(2.4935343325226915, certify=False)
    operator = result["operator_certificate"]
    z = result["response_coordinate"]
    L = result["L"]

    assert operator["cross_block_norm"] == 0.0
    assert operator["radial_block_dimension"] == 1
    assert operator["coclosed_first_total_multiplicity"] == 48
    assert operator["complete_spectral_bottom"] == result["gap_squared"]
    bottom = coclosed_vector_mass_squared(L, z, 1)
    assert bottom == pytest.approx(result["transverse_mass_squared"], rel=1e-15)
    for degree in (3, 5, 9, 21):
        assert coclosed_vector_mass_squared(L, z, degree) > bottom


def test_interval_certificate_encloses_a_positive_complete_gap():
    L = 2.4935343325226915
    point = generated_yang_mills_gap(L, certify=False)
    certificate = generated_yang_mills_interval_certificate(L, decimal_places=55)
    lower, upper = certificate["complete_gap_squared"]

    assert certificate["strictly_positive"] is True
    assert lower > 0.0
    assert point["gap_squared"] == pytest.approx(
        (lower + upper) / 2.0, rel=5e-14
    )
    rlo, rhi = certificate["radial_identity_residual"]
    assert rlo <= 0.0 <= rhi


def test_scale_transport_preserves_the_dimensionless_gap():
    result = generated_yang_mills_gap(2.4935343325226915, certify=False)
    scales = (1.0, 1.7310765000475023e18, 2.435e18)
    transport = generated_yang_mills_scale_transport(
        result["gap_squared"], scales
    )
    assert transport["strictly_positive"] is True
    assert transport["ratio_spread"] <= 4e-15 * transport["dimensionless_gap"]
    assert all(
        ratio == pytest.approx(transport["dimensionless_gap"], rel=2e-15)
        for ratio in transport["gap_to_scale_ratios"]
    )


@pytest.mark.parametrize("L", [0.0, CRITICAL_RADIUS, 1.0])
def test_generated_gap_rejects_noncondensed_radius(L):
    with pytest.raises(ValueError):
        generated_yang_mills_gap(L, certify=False)


@pytest.mark.parametrize("degree", [0, 2, 4, -1])
def test_coclosed_spectrum_rejects_degrees_outside_the_projective_tower(degree):
    with pytest.raises(ValueError):
        coclosed_vector_mass_squared(2.5, 1.0, degree)
