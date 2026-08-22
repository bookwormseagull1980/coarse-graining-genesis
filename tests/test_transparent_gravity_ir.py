# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""Regression tests for the transparent-gravity IR research audit."""

from scripts.research_transparent_gravity_ir import (
    p_laplacian_scan,
    scan_scale_law,
    scan_v4_trajectory,
)


def test_present_tt_kernel_is_newtonian():
    r = scan_v4_trajectory(points=120)
    assert abs(r["slope_G"] + 2.0) < 1e-12
    assert abs(r["slope_Z"]) < 1e-12
    assert abs(r["linear_kernel_alpha"] - 2.0) < 1e-12
    assert abs(r["acceleration_power_r"] + 2.0) < 1e-12
    assert r["F_deep_mond_possible_with_fixed_linear_kernel"] is False


def test_scale_law_change_alone_does_not_make_flat_curves():
    rows = scan_scale_law([0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
                          points=160)
    assert all(row["linear_kernel_alpha"] < 2.05 for row in rows)
    assert not any(row["flat_rotation_linear_kernel"] for row in rows)


def test_local_scale_invariant_ir_closure_selects_p_three():
    rows = p_laplacian_scan([2.0, 2.5, 3.0, 3.5, 4.0])
    flat = [row for row in rows if row["flat_rotation"]]
    assert [row["p"] for row in flat] == [3.0]
    assert abs(flat[0]["source_mass_power"] - 0.5) < 1e-12
    assert abs(flat[0]["acceleration_power_r"] + 1.0) < 1e-12
