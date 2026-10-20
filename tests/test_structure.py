# -*- coding: utf-8 -*-
"""Structural-closure tests for the V5 minimal-change chain."""

from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.structure import all_certificates  # noqa: E402
from cg_core.tt_branch_reduction import certificate as branch_reduction  # noqa: E402
from cg_core.structure.content_capacity import torsion_tau  # noqa: E402
from cg_core.structure.internal_geometry import (  # noqa: E402
    scalar_eigenvalue,
    spinor_eigenvalue,
    tt_rough_eigenvalue,
    vector_eigenvalue,
)
from cg_core.structure.minimal_change import (  # noqa: E402
    critical_ratio,
    ir_endpoint,
    uv_endpoint,
    unit_covariance_width,
)


def test_all_structural_certificates_pass():
    certificates = all_certificates()
    assert {name: cert["status"] for name, cert in certificates.items()} == {
        "minimal_change": "PASS",
        "rp3_derivation": "PASS",
        "internal_geometry": "PASS",
        "content_capacity": "PASS",
        "response_level": "PASS",
        "normalization": "PASS",
        "projection": "PASS",
        "matching": "PASS",
        "capacity_closure": "PASS",
        "endpoint_interval": "PASS",
        "tt_branch_reduction": "PASS",
    }


def test_tt_branch_reduction_matches_full_response():
    cert = branch_reduction(cells=256)
    assert cert["status"] == "PASS"
    assert cert["active_branch_count"] == 8
    assert cert["stable_active_set"]
    assert cert["exact_interval_identity"]


def test_minimal_change_endpoints():
    b = unit_covariance_width()
    assert b == 1.0
    assert uv_endpoint(b) ** 2 == pytest.approx(2.0)
    assert ir_endpoint(b) ** 2 == pytest.approx(2.0 * math.pi)
    assert critical_ratio() ** 2 == pytest.approx(math.pi)


def test_internal_geometry_lowest_modes():
    L = 2.4935343325
    assert scalar_eigenvalue(0, L) == 0.0
    assert vector_eigenvalue(1, L) == pytest.approx(4.0 / L**2)
    assert spinor_eigenvalue(0, L) == pytest.approx((1.5 / L) ** 2)
    assert tt_rough_eigenvalue(2, L) == pytest.approx(6.0 / L**2)


def test_content_capacity_exact():
    assert torsion_tau() == Fraction(1, 50)


def test_content_is_derived_from_primitive_charge():
    from cg_core.content_derivation import certificate

    result = certificate()
    assert result["status"] == "PASS"
    assert result["relative_character"] == (1, -3)
    assert result["primitive_charge"] == (3, 1)
    assert result["N_L"] == 8
    assert result["N_R"] == 7
    assert result["N_f"] == 15
    assert result["sum_Y_squared"] == "10/3"
    assert result["tau"] == "1/50"


def test_default_response_domain_reads_derived_level():
    from cg_core.structure.response_level import certificate
    from cg_core.window_weights import DEFAULT_RESPONSE_DOMAIN

    assert DEFAULT_RESPONSE_DOMAIN.radius == certificate()["selected_R"] == 5


def test_rp3_comes_from_quaternion_centre():
    from cg_core.structure.rp3_derivation import certificate

    result = certificate()
    assert result["status"] == "PASS"
    assert result["quotient"]["space"] == "SU(2)/Z2"
    assert result["checks"]["centre_quotient_identifies_rotation"]
