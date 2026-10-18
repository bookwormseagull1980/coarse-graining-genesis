# -*- coding: utf-8 -*-
# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# =============================================================================

"""Checks for the generated Yang--Mills response of Paper 4."""

import math

import pytest

from cg_frg.qcd.mass_gap_scale import (
    conformal_restoring_curvature,
    conformal_restoring_response,
    generated_yang_mills_gap,
)


def test_conformal_response_endpoints_and_curvature():
    assert conformal_restoring_response(0.0) == pytest.approx(0.0, abs=1e-15)
    assert conformal_restoring_curvature(0.0) == pytest.approx(
        math.pi * (math.pi + 2.0) / 8.0, rel=2e-15)
    assert conformal_restoring_response(0.25) == pytest.approx(
        math.pi / 8.0, rel=2e-15)
    assert conformal_restoring_curvature(0.25) == pytest.approx(
        math.pi ** 2 / 8.0, rel=2e-15)


@pytest.mark.parametrize("z", [1e-6, 0.1, 0.24, 0.26, 1.0, 10.0])
def test_conformal_response_is_strictly_restoring(z):
    step = max(1e-8, z * 1e-6)
    derivative = (
        conformal_restoring_response(z + step)
        - conformal_restoring_response(max(0.0, z - step))
    ) / (step if z < step else 2.0 * step)
    assert conformal_restoring_curvature(z) > 0.0
    assert derivative == pytest.approx(
        conformal_restoring_curvature(z), rel=3e-6, abs=2e-8)


def test_generated_yang_mills_gap_closes_both_mass_blocks():
    L = 2.4935343325226915
    L_c = math.sqrt(math.pi)
    mass_unit = 1.7310765000475023e18
    result = generated_yang_mills_gap(L, L_c=L_c, mass_unit=mass_unit)

    assert result["phase"] == "condensed"
    assert result["reference_drive"] < 0.0
    assert result["feedback_coefficient"] > 0.0
    assert result["intensity_q"] > 0.0
    assert result["radial_metric"] > 0.0
    assert result["normalized_score_variance"] == pytest.approx(
        1.0, abs=2e-15)
    assert result["curvature_radial_coefficient"] > 0.0
    assert result["curvature_score_overlap"] > 0.0
    assert result["scalar_constant_mode_mass_squared"] == pytest.approx(
        result["radial_mass_squared"], rel=2e-15)
    assert result["radial_intertwining_residual"] == pytest.approx(
        0.0, abs=1e-15)
    assert result["response_coordinate"] == pytest.approx(
        result["kappa"] * result["intensity_q"], rel=2e-15)
    assert result["stationarity_residual"] == pytest.approx(0.0, abs=2e-12)
    assert abs(result["radial_identity_residual"]) <= (
        3e-15 * result["radial_mass_squared"])
    assert result["gap_squared"] == pytest.approx(
        min(result["radial_mass_squared"],
            result["transverse_mass_squared"]), rel=2e-15)
    assert result["gap_squared"] > 0.0
    assert result["gap"] == pytest.approx(
        math.sqrt(result["gap_squared"]) * mass_unit, rel=2e-15)


@pytest.mark.parametrize("L", [0.0, math.sqrt(math.pi), 1.0])
def test_generated_gap_rejects_noncondensed_radius(L):
    with pytest.raises(ValueError):
        generated_yang_mills_gap(L, L_c=math.sqrt(math.pi))
