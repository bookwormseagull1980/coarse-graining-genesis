# -*- coding: utf-8 -*-
"""Tests for the explicit-R finite Gaussian TT response domain."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402
from cg_frg.frg.tt_response_domain import (  # noqa: E402
    _response,
    certificate,
    endpoint_coordinate,
    response_edge,
)


def test_endpoint_five_matches_stored_kL():
    c5 = endpoint_coordinate(5)
    assert c5 == pytest.approx(float(get("kL")), rel=2e-13)


def test_lower_crossing_is_below_the_first_position():
    c4 = endpoint_coordinate(4)
    assert c4 < math.sqrt(11.0 / 2.0)


def test_lower_platform_edge_is_between_four_and_five():
    edge = response_edge()
    assert 4.0 < edge < 5.0


def test_upper_edge_is_the_shell_support_bound():
    upper = 16.0 / math.pi
    assert upper < 6.0
    assert endpoint_coordinate(upper) < math.sqrt(15.0 / 2.0)


def test_c6_is_not_an_upper_certificate():
    # The production c(6) is still below sqrt(15/2); the upper edge is the
    # shell-support bound R <= 16/pi, not a c crossing.
    assert endpoint_coordinate(6) < math.sqrt(15.0 / 2.0)


def test_tt_endpoint_is_not_the_gaussian_ir_edge():
    result = certificate()
    tt = result["radii"]["tt_endpoint_at_R5"]
    edge = math.sqrt(2.0 * math.pi)
    assert tt == pytest.approx(result["endpoint_coordinates"]["5"], rel=0.0, abs=1e-15)
    assert tt < edge
    assert _response(5, edge, float(get("tau")), float(get("M_P"))) < 4.0 / 27.0


def test_certificate_selects_the_unique_integer_level():
    result = certificate()
    assert result["unique_integer_level"] == 5
    assert result["integer_levels_in_platform"] == [5]
    assert result["checks"]["c4_below_first_position"]
    assert result["checks"]["R_star_between_4_and_5"]
    assert result["checks"]["upper_shell_bound_below_6"]
    assert result["checks"]["c6_below_next_position"]
