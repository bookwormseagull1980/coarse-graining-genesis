"""Independent diagram recombination, chiral signs and subtraction checks."""

import math

import numpy as np
import pytest

from cg_core.matter_matching import charged_lepton_pole_matching_one_loop
from cg_frg.fermion.lepton_pole import lepton_mass_vertex_response
from cg_frg.fermion.lepton_self_energy import (
    charged_lepton_chiral_self_energy_one_loop, generated_lepton_action_factors,
)


MASSES = {"electron": .0005103542513564916, "muon": .10531446305553036,
          "tau": 1.772105081689173}
GAUGE = (.4615882289132695, .6482117683683781)
VEV, HIGGS, SCALE = 246.18969645238943, 124.98344026878286, 91.12483998892053


def evaluate(masses=MASSES, **kwargs):
    return charged_lepton_chiral_self_energy_one_loop(
        masses, GAUGE, VEV, higgs_mass_GeV=HIGGS, scale_GeV=SCALE,
        action_source="independent common-action diagram test", **kwargs)


@pytest.fixture(scope="module")
def pole_result():
    return evaluate()


def test_actual_complete_source_matrices_determine_lepton_vertices():
    result = generated_lepton_action_factors()
    assert result["electric_charge"] == -1.
    assert result["left_isospin"] == -.5
    assert result["right_isospin"] == 0.
    assert result["charged_current_transition_norm_squared"] == 1.
    assert result["colour_vertex_norm_squared"] == 0.
    assert result["direct_one_loop_colour_self_energy_zero"] is True


def test_six_diagrams_recover_independent_total_kernel(pole_result):
    old = charged_lepton_pole_matching_one_loop(
        MASSES, GAUGE, VEV, higgs_mass_GeV=HIGGS, scale_GeV=SCALE,
        action_source="independent aggregate kernel", input_definition="generated_on_shell_conditions")
    for name, result in pole_result["species"].items():
        total = result["total"]["mass_combination"]
        assert total["real"] == pytest.approx(-old["log_matching_factors"][name], abs=2e-17)
        assert abs(total["imag"]) < 1e-35
    assert pole_result["weighted_mass_combination"]["real"] == pytest.approx(
        -old["charged_lepton_log_correction"], abs=2e-17)


def test_goldstone_absorptive_terms_cancel_at_stable_pole(pole_result):
    for result in pole_result["species"].values():
        diagrams = result["diagrams"]
        w = diagrams["W"]["mass_combination"]["imag"]
        goldstone = diagrams["charged_Goldstone"]["mass_combination"]["imag"]
        assert abs(w) > 1e-15
        assert goldstone == pytest.approx(-w, rel=2e-14)
        assert diagrams["W"]["sigma_right"]["real"] == 0.
        assert diagrams["charged_Goldstone"]["sigma_left"]["real"] == 0.
        assert diagrams["neutral_Goldstone"]["omega_GeV"]["real"] > 0
        assert diagrams["Higgs"]["omega_GeV"]["real"] < 0


def test_photon_diagram_and_real_spacelike_canonical_forms():
    s = -SCALE**2
    result = evaluate(momentum_squared_GeV2={name: s for name in MASSES})
    gp2, g2 = 3*GAUGE[0]**2/5, GAUGE[1]**2
    e2 = g2*gp2/(g2+gp2)
    db, dl, dr = [], [], []
    for name, mass in MASSES.items():
        terms = result["species"][name]
        photon = terms["diagrams"]["photon"]
        b0 = 2-math.log(mass**2/SCALE**2)+(mass**2/s-1)*math.log1p(-s/mass**2)
        expected = e2*(3*b0-2)/(16*math.pi**2)
        assert photon["mass_combination"]["real"] == pytest.approx(expected, abs=2e-17)
        assert photon["sigma_left"]["real"] == photon["sigma_right"]["real"] == 0.
        total = terms["total"]
        for part in total.values():
            assert part["imag"] == 0.
        db.append(total["delta_mass_vertex_GeV"]["real"])
        dl.append(total["delta_left_kinetic"]["real"])
        dr.append(total["delta_right_kinetic"]["real"])
    response = lepton_mass_vertex_response(
        np.diag(list(MASSES.values())), np.eye(3), np.eye(3),
        delta_mass_vertex_GeV=np.diag(db), delta_left_gram=np.diag(dl),
        delta_right_gram=np.diag(dr), action_source=result["action_source"])
    assert response["weighted_log_response"] == pytest.approx(
        result["weighted_mass_combination"]["real"], abs=2e-17)


def test_precision_refinement_at_larger_yukawa():
    # A larger allowed mass makes Goldstone and massive-vector terms visible;
    # agreement is not only a consequence of photon dominance for the electron.
    masses = {"electron": .01, "muon": 5., "tau": 15.}
    lo, hi = evaluate(masses, decimal_precision=35), evaluate(masses, decimal_precision=55)
    old = charged_lepton_pole_matching_one_loop(
        masses, GAUGE, VEV, higgs_mass_GeV=HIGGS, scale_GeV=SCALE,
        action_source="larger Yukawa aggregate check", input_definition="generated_on_shell_conditions")
    for name in masses:
        for component in ("sigma_left", "sigma_right", "omega_GeV", "mass_combination"):
            for part in ("real", "imag"):
                a = lo["species"][name]["total"][component][part]
                b = hi["species"][name]["total"][component][part]
                assert a == pytest.approx(b, abs=2e-17)
        assert hi["species"][name]["total"]["mass_combination"]["real"] == pytest.approx(
            -old["log_matching_factors"][name], abs=2e-17)


@pytest.mark.parametrize("momenta", [
    {"electron": 0., "muon": -1., "tau": -1.},
    {name: float("nan") for name in MASSES}, {name: 10. for name in MASSES},
])
def test_rejects_singular_or_unsupported_momenta(momenta):
    with pytest.raises(ValueError, match="nonzero momenta"):
        evaluate(momentum_squared_GeV2=momenta)


def test_rejects_unresolved_action_input():
    with pytest.raises(ValueError, match="at least 30"):
        evaluate(decimal_precision=15)
    with pytest.raises(ValueError, match="lepton masses"):
        evaluate({name: 100. for name in MASSES})
