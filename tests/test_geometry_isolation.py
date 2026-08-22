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

"""Isolation tests: pure-geometry modules depend only on their inputs.

These modules take (L, tau, ...) as explicit arguments (no store
reads); the tests verify exact closed-form identities at the
framework's fixed point (EXPECTED_BY_THEORY).
"""
import math

import pytest

L = 2.4935343325226915      # kL* — the framework's fixed point
TAU = 0.02                  # the torsion content ratio


def test_rp3_scalar_spectrum():
    from cg_core.rp3_spectrum import (scalar_eigenvalue, scalar_multiplicity,
                                      vector_eigenvalue, spinor_dirac_eigenvalue)
    # EXPECTED_BY_THEORY: l=0 zero mode; l=2 gives 8/L^2 with
    # multiplicity 9; the l=1 Killing vector 4/L^2 (6 modes).
    assert abs(scalar_eigenvalue(0, L)) < 1e-12
    assert abs(scalar_eigenvalue(2, L) - 8.0 / L ** 2) < 1e-12
    assert scalar_multiplicity(2) == 9
    assert vector_eigenvalue(1, L) == 4.0 / L ** 2
    assert abs(spinor_dirac_eigenvalue(0, L) - 1.5 / L) < 1e-12


def test_rp3_tt_lowest_mode():
    from cg_core.rp3_spectrum import tt_lowest_eigenvalue, tt_eigenvalue
    # EXPECTED_BY_THEORY: the lowest TT mode is (jL,jR)=(1,1) with
    # lambda = 14/L^2 (the Lichnerowicz-shifted Casimir).
    assert abs(tt_lowest_eigenvalue(L) - 14.0 / L ** 2) < 1e-12
    assert abs(tt_eigenvalue(1, 1, L) - 14.0 / L ** 2) < 1e-12


def test_ec_structure_identities():
    from cg_core.ec_structure import (scalar_curvature_LC, ec_over_lc_ratio,
                                      torsion_squared)
    # EXPECTED_BY_THEORY: R_LC = 6/L^2; the EC/Lichnerowicz ratio
    # (1 - tau^2/4); torsion-squared = 6 (tau/L)^2.
    assert abs(scalar_curvature_LC(L) - 6.0 / L ** 2) < 1e-12
    assert abs(ec_over_lc_ratio(TAU) - (1.0 - 1e-4)) < 1e-15
    assert abs(torsion_squared(TAU, L) - 6.0 * (TAU / L) ** 2) < 1e-20


def test_squash_metric_first_principles():
    """kappa^2 = (1+s)/(1-2s)^{5/2} at s0 = 2tau — the geometric integral."""
    from cg_frg.gauge.geometric_couplings import squash_metric
    s0 = 2.0 * TAU
    m = squash_metric(TAU)
    assert abs(m["s"] - s0) < 1e-15
    kappa2_exp = (1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5   # EXPECTED_BY_THEORY
    assert abs(m["kappa2"] - kappa2_exp) < 1e-12
    assert abs(m["kappa"] - math.sqrt(kappa2_exp)) < 1e-12
    # kappa(2tau) = 1.131832...
    assert abs(m["kappa"] - 1.131832) < 1e-5


def test_spectral_sum_channels_signs():
    """The five spectral-sum channels: spin-2/0 positive on RP3."""
    from cg_frg.frg.spectral_sum import compute
    r = compute(L, 1e-2, TAU)
    assert r["tmunu_spin2"]["rp3_pi0"] > 0.0
    assert r["tmunu_spin0"]["rp3_pi0"] > 0.0
    # flat_pi0 carries an explicit source marker for the four
    # classification channels (paper 3-1 assertion, NOT computed).
    assert r["tmunu_spin2"]["flat_pi0"]["value"] == 0.0
    assert "NOT computed" in r["tmunu_spin2"]["flat_pi0"]["source"]


def test_discrete_flow_semigroup():
    from cg_frg.frg.discrete_flow import semigroup_check
    err = semigroup_check(1.0, 0.7)
    assert err < 1e-12             # the Gaussian semigroup (machine precision)
