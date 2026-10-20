# -*- coding: utf-8 -*-
"""Tests for the charged-lepton geometric-to-pole fixed point."""

from pathlib import Path
import math
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cg_frg.fermion.lepton_pole import (  # noqa: E402
    charged_lepton_conversions,
    geometric_to_pole_one_loop,
    solve_pole_mass,
)


LABELS = ("e", "mu", "tau")
GEOM = {"e": 0.5e-3, "mu": 0.105, "tau": 1.77}
SCHEME = "MSbar input at the stated scale; on-shell pole fixed point"
BOUNDARY = "generated charged-lepton vertex"


def test_zero_self_energy_is_tree_identification():
    result = solve_pole_mass(
        GEOM["e"], lambda _m: 0.0,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    assert result["G"] == pytest.approx(1.0, rel=1e-15)
    assert result["residual_GeV"] == pytest.approx(0.0, abs=1e-18)


def test_constant_relative_shift_reaches_exact_fixed_point():
    shift = 0.01
    result = solve_pole_mass(
        GEOM["mu"], lambda m: shift * m,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    expected = GEOM["mu"] / (1.0 - shift)
    assert result["pole_mass_GeV"] == pytest.approx(expected, rel=2e-13)
    assert result["G"] == pytest.approx(1.0 / (1.0 - shift), rel=2e-13)


def test_common_conversion_cancels_in_delta_L():
    shift = 0.02
    self_energies = {k: (lambda m, s=shift: s * m) for k in LABELS}
    result = charged_lepton_conversions(
        GEOM, self_energies,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    for label in LABELS:
        assert result["leptons"][label]["G"] == pytest.approx(1.0 / 0.98, rel=1e-11)
    assert result["Delta_L"] == pytest.approx(0.0, abs=5e-12)
    assert result["nonuniversal_log_spread"] == pytest.approx(0.0, abs=5e-12)


def test_nonuniversal_conversion_has_expected_delta_L():
    shifts = {"e": 0.01, "mu": 0.02, "tau": 0.03}
    self_energies = {k: (lambda m, s=shifts[k]: s * m) for k in LABELS}
    result = charged_lepton_conversions(
        GEOM, self_energies,
        scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)
    expected = math.log(1.0 / 0.99) * -1.0 \
        + math.log(1.0 / 0.98) * 2.0 \
        + math.log(1.0 / 0.97) * -1.0
    assert result["Delta_L"] == pytest.approx(expected, rel=1e-11)


def test_scheme_and_boundary_are_required():
    with pytest.raises(ValueError):
        solve_pole_mass(
            GEOM["e"], lambda _m: 0.0,
            scheme="", scale_GeV=91.0, boundary_source=BOUNDARY)
    with pytest.raises(ValueError):
        solve_pole_mass(
            GEOM["e"], lambda _m: 0.0,
            scheme=SCHEME, scale_GeV=91.0, boundary_source="")


def test_nonconvergent_or_negative_branch_is_rejected():
    with pytest.raises(RuntimeError):
        solve_pole_mass(
            GEOM["e"], lambda m: m,
            scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY,
            max_iterations=8)
    with pytest.raises(ValueError):
        solve_pole_mass(
            GEOM["e"], lambda m: -2.0 * m,
            scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY)


def test_weights_must_sum_to_zero():
    self_energies = {k: (lambda _m: 0.0) for k in LABELS}
    with pytest.raises(ValueError):
        charged_lepton_conversions(
            GEOM, self_energies,
            scheme=SCHEME, scale_GeV=91.0, boundary_source=BOUNDARY,
            weights=(1.0, 1.0, 1.0))



def test_one_loop_geometric_to_pole_uses_existing_kernel():
    geometric = {
        "e": 0.0005103542513564916,
        "mu": 0.10531446305553036,
        "tau": 1.772105081689173,
    }
    result = geometric_to_pole_one_loop(
        geometric,
        [0.4615882289132695, 0.6482117683683781],
        246.18969645238943,
        higgs_mass_GeV=124.98344026878286,
        scale_GeV=91.12483998892053,
        input_scheme="MSbar_at_scale",
        action_source="generated five-coupling charged-lepton action",
    )
    assert result["iterations"] >= 1
    assert result["convergence"] <= 2e-10
    assert math.isfinite(result["Delta_L"])
    for label in LABELS:
        entry = result["leptons"][label]
        assert entry["G"] > 0.0
        assert abs(entry["running_residual"]) <= 2e-10


def test_one_loop_conversion_requires_declared_input_scheme():
    with pytest.raises(ValueError):
        geometric_to_pole_one_loop(
            GEOM,
            [0.46, 0.65],
            246.0,
            higgs_mass_GeV=125.0,
            scale_GeV=91.0,
            input_scheme="pole_mass_input",
            action_source="test action",
        )

