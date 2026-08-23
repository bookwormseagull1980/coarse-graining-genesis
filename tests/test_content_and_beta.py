# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""Unit tests: the content source (sm_content) and the β-functions.

Theoretical reference values are marked EXPECTED_BY_THEORY — analytic
results of the framework's content derivation, not observed inputs.
"""
import math

import pytest


# ---------------------------------------------------------------------------
# sm_content — the single content source
# ---------------------------------------------------------------------------
def test_generation_count_is_three():
    from cg_core.sm_content import N_GENERATIONS
    assert N_GENERATIONS == 3          # EXPECTED_BY_THEORY (window_capacity)


def test_weyl_content_counts():
    from cg_core.sm_content import (N_LEFT, N_RIGHT, N_WEYL_TOTAL,
                                    N_GAUGE_TOTAL, SCALAR_DOF)
    # EXPECTED_BY_THEORY: 8 left vs 7 right per generation (15 Weyl),
    # 45 total, 12 gauge, 4 Higgs real dof.
    assert N_LEFT == 8
    assert N_RIGHT == 7
    assert N_LEFT + N_RIGHT == 15
    assert N_WEYL_TOTAL == 45
    assert N_GAUGE_TOTAL == 12
    assert SCALAR_DOF == 4


def test_hypercharge_square_sum():
    from cg_core.sm_content import hypercharge_sum_sq
    # EXPECTED_BY_THEORY: Sum Y^2 = 10/3 per generation.
    assert abs(hypercharge_sum_sq() - 10.0 / 3.0) < 1e-12


def test_chiral_asymmetry():
    from cg_core.sm_content import chiral_asymmetry
    # EXPECTED_BY_THEORY: N_L - N_R = 1 (the chiral drive of tau).
    assert chiral_asymmetry() == 1


# ---------------------------------------------------------------------------
# beta_functions — the gauge beta coefficients
# ---------------------------------------------------------------------------
def test_one_loop_gauge_coefficients():
    from cg_core.beta_functions import _B_GAUGE
    # EXPECTED_BY_THEORY (Buttazzo GUT-normalised, derived from content):
    #   b1 = 41/10,  b2 = -19/6,  b3 = -7
    assert abs(_B_GAUGE[0] - 41.0 / 10.0) < 1e-12
    assert abs(_B_GAUGE[1] + 19.0 / 6.0) < 1e-12
    assert abs(_B_GAUGE[2] + 7.0) < 1e-12


def test_content_constants_come_from_sm_content():
    """N_G / SumY2 are imported from sm_content (single source, 2026-08-21)."""
    from cg_core import beta_functions as bf
    from cg_core.sm_content import N_GENERATIONS, hypercharge_sum_sq
    assert bf.N_G == float(N_GENERATIONS)
    assert bf.SIGMA_Y2 == float(hypercharge_sum_sq())
    assert bf.TF_SU2 == 2.0 * bf.N_G      # EXPECTED_BY_THEORY: 3 gen x 2 doublets
    assert bf.TF_SU3 == 2.0 * bf.N_G


# ---------------------------------------------------------------------------
# frg_regulator — the exponential window (production regulator)
# ---------------------------------------------------------------------------
def test_exponential_regulator_convention():
    from cg_core.frg_regulator import exponential_regulator, exponential_dR_dt
    k2 = 1.0
    # R(0) = k^2 (the regulator convention, finite — NOT k^4/z divergent).
    assert abs(exponential_regulator(0.0, k2) - 1.0) < 1e-9
    # R -> 0 for z >> k^2.
    assert exponential_regulator(100.0, k2) < 1e-40
    # The small-y Taylor branch matches the full form.
    z = 1e-6 * k2
    full = z / (math.exp(z / k2) - 1.0)
    assert abs(exponential_regulator(z, k2) - full) / full < 1e-9


def test_regulator_agrees_with_trace_kernels():
    """frg_regulator and trace_kernels implement the SAME window."""
    from cg_core.frg_regulator import exponential_regulator, exponential_dR_dt
    from cg_core.trace_kernels import _exponential_terms
    for k2 in (0.5, 1.0, 4.0):
        for z in (0.05 * k2, 0.5 * k2, 1.0 * k2, 3.0 * k2, 8.0 * k2):
            dR_tk, den_tk = _exponential_terms(z, k2, 0.0)
            R_tk = den_tk - z
            assert abs(R_tk - exponential_regulator(z, k2)) / abs(R_tk) < 1e-9
            assert abs(dR_tk - exponential_dR_dt(z, k2)) / abs(dR_tk) < 1e-9


def test_litim_sharp_cutoff():
    from cg_core.frg_regulator import litim_regulator, litim_dR_dt
    k2 = 1.0
    assert abs(litim_regulator(0.0, k2) - 1.0) < 1e-15
    assert litim_regulator(2.0, k2) == 0.0
    assert litim_dR_dt(0.5, k2) == 2.0
    assert litim_dR_dt(2.0, k2) == 0.0
