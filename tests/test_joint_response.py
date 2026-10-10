# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""Shared-input derivatives and supplied covariance, without store mutation."""
from pathlib import Path
import math
import sys

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cg_core.joint_response import (
    MASS_SPECIES, MASS_COMPARISON_LOG_ORDER, compare_matched_mass_relation,
    RUNNING_MASS_SPECIES, MASS_SUM_RULE_WEIGHTS, running_mass_sum_rules,
    mass_sum_rule_beta_one_loop, charged_lepton_qed_log_matching,
    charged_lepton_finite_transfer, charged_lepton_transfer_enclosure,
    lepton_matching_spread_bound,
    evaluate, evaluate_records, log_jacobian, propagate_log_covariance,
)
from comparison.sm_rge import inputs as comparison_inputs

POINT = (2.4935343325226915, .02, 2.435323595526305e18)


@pytest.fixture
def published_mass_reference(monkeypatch):
    monkeypatch.setattr(comparison_inputs, "sm_value", comparison_inputs.published_sm_value)
    return comparison_inputs.published_running_mass_benchmark()


def test_analytic_log_jacobian_by_central_difference():
    rows = log_jacobian(*POINT)
    step = 1e-5
    for coordinate in range(3):
        plus, minus = list(POINT), list(POINT)
        plus[coordinate] *= math.exp(step)
        minus[coordinate] *= math.exp(-step)
        high, low = evaluate(*plus), evaluate(*minus)
        for key, row in rows.items():
            numerical = math.log(high[key]/low[key])/(2*step)
            assert numerical == pytest.approx(row[coordinate], rel=3e-8, abs=2e-9), key


def test_anchor_dimension_and_mass_elimination():
    base, doubled = evaluate(*POINT), evaluate(POINT[0], POINT[1], 2*POINT[2])
    assert doubled["rho_Lambda"]/base["rho_Lambda"] == pytest.approx(16.)
    for key in ("v_HIGGS", "m_e_pred", "m_nu1", "H0_GEV", "T_CMB_GeV"):
        assert doubled[key]/base[key] == pytest.approx(2.)
    assert log_jacobian(*POINT)["Omega_Lambda"] == (0., 0., 0.)
    jac = log_jacobian(*POINT)
    assert 2*jac["T_CMB_GeV"][0]-jac["H0_GEV"][0] == 0.


def test_rank_one_supplied_covariance_and_no_invented_error():
    result = propagate_log_covariance(*POINT, np.diag([0., 0., .01]),
                                     outputs=["v_HIGGS", "rho_Lambda", "Omega_Lambda"])
    expected = .01*np.outer([1., 4., 0.], [1., 4., 0.])
    assert np.asarray(result["output_log_covariance"]) == pytest.approx(expected)
    assert result["input_order"] == ["c", "tau", "M_P"]
    zero = propagate_log_covariance(*POINT, np.zeros((3, 3)))
    assert np.count_nonzero(zero["output_log_covariance"]) == 0


@pytest.mark.parametrize("bad", [np.diag([1., -1., 1.]), [[1, 2, 0], [2, 1, 0], [0, 0, 1]],
                                  [[1, 1, 0], [0, 1, 0], [0, 0, 1]], np.eye(2),
                                  np.diag([1., float("nan"), 1.])])
def test_invalid_covariance_rejected(bad):
    with pytest.raises(ValueError):
        propagate_log_covariance(*POINT, bad)


def _records():
    values = evaluate(*POINT)
    values.update(kL=POINT[0], tau=POINT[1], M_P=POINT[2], eta_b=6e-10, m_p=.94)
    values["eta_B_photon_zero_mode_factor"] = values["photon_zero_mode_Cgamma"]**-3
    ngamma = 2*1.2020569031595942*values["T_CMB_GeV"]**3/math.pi**2
    values["Omega_b"] = values["eta_b"]*ngamma*values["m_p"]/(3*values["H0_GEV"]**2*POINT[2]**2)
    values["Omega_Sigma"] = 1-values["Omega_b"]-values["Omega_Lambda"]
    return {key: {"value": value} for key, value in values.items()}


def test_record_cross_checks_detect_partial_update_and_missing_output():
    records = _records()
    assert evaluate_records(records)["passed"]
    records["m_nu2"]["value"] *= 1.01
    result = evaluate_records(records)
    assert not result["passed"]
    assert not result["checks"]["neutrino_ratio_12"]["passed"]
    records = _records()
    del records["T_CMB_corrected_K"]
    assert "T_CMB_corrected_K" in evaluate_records(records)["missing"]


def test_domain_is_explicit():
    with pytest.raises(ValueError):
        evaluate(POINT[0], .2, POINT[2])


def test_record_cross_checks_read_only_named_scientific_inputs():
    """A guarded store rejects a broad scan and any unrelated comparison read."""
    from collections.abc import Mapping

    class TargetedRecords(Mapping):
        def __init__(self, values):
            self.values = values

        def __getitem__(self, key):
            if key == "unrelated_observation":
                raise AssertionError("comparison was read by the shared response")
            return self.values[key]

        def __iter__(self):
            raise AssertionError("shared response must use named input reads")

        def __len__(self):
            raise AssertionError("shared response must use named input reads")

    records = _records()
    records["unrelated_observation"] = {"value": 999.}
    assert evaluate_records(TargetedRecords(records))["passed"]


def test_sensitivity_entry_uses_current_records_and_detects_partial_update(monkeypatch):
    from scripts import sensitivity_analysis

    values = {key: rec["value"] for key, rec in _records().items()}
    values["m_mu_pred"] = .1
    values["m_tau_pred"] = values["m_mu_pred"]*values.pop("m_tau_over_m_mu")
    monkeypatch.setattr(sensitivity_analysis, "get", values.__getitem__)
    central, rows = sensitivity_analysis.current_response()
    assert central["m_tau_over_m_mu"] == pytest.approx(values["m_tau_pred"]/values["m_mu_pred"])
    assert rows["rho_Lambda"][0] == 2*rows["H0_GEV"][0]
    values["g1_MG_geo"] *= 1.001
    with pytest.raises(ValueError, match="g1_MG_geo"):
        sensitivity_analysis.current_response()


def test_regime_comparison_reuses_the_current_gaussian_endpoint(monkeypatch):
    from scripts import regime_spread

    monkeypatch.setattr(regime_spread, "get", {"kL": 2.51}.__getitem__)

    def unnecessary_solve(*args):
        raise AssertionError("the current Gaussian endpoint must be reused")

    monkeypatch.setattr(regime_spread, "k_star", unnecessary_solve)
    assert regime_spread.solve_kL("gaussian") == 2.51


def test_current_ladder_verification_uses_stored_inputs_and_rejects_mismatch(monkeypatch):
    from cg_frg.generation import lz_dynamics, sector_alpha

    c, tau, tilt, cmb = 2.6, .03, .04, 2.52
    au = sector_alpha.alpha_up(c, tau)
    delta = sector_alpha.sector_step(tilt, cmb)
    ad, al = sector_alpha.ladder_down(au, delta), sector_alpha.ladder_lepton(au, delta)
    values = {"kL": c, "tau": tau, "ns_tilt": tilt, "kL_CMB": cmb,
              "alpha_up": au, "alpha_down": ad, "alpha_lepton": al,
              "sector_alpha_delta": delta, "m_t_over_m_c": math.exp(2*au),
              "m_b_over_m_s": math.exp(2*ad)}
    monkeypatch.setattr(lz_dynamics, "get", values.__getitem__)
    before = dict(values)
    result = lz_dynamics.compute()
    assert result["adiabatic"] == c
    assert result["step_ratio"] == pytest.approx(9/8)
    assert values == before
    values["m_b_over_m_s"] *= 1.01
    with pytest.raises(ValueError, match="m_b_over_m_s"):
        lz_dynamics.compute()


def test_geometric_mass_combination_and_common_input_derivatives():
    result = evaluate_records(_records())
    identity = result["geometric_mass_relation"]
    assert abs(identity["residual"]) < 2e-14
    assert identity["input_log_derivative"] == pytest.approx([0., 0., 0.], abs=2e-14)
    assert not identity["physical_mass_comparison_performed"]
    step = 1e-4
    for axis in range(3):
        residuals = []
        for sign in (-1, 1):
            point = list(POINT)
            point[axis] *= math.exp(sign*step)
            p = evaluate(*point)
            residuals.append(8*math.log(p["m_t_over_m_c"])
                             +9*math.log(p["m_tau_over_m_mu"])
                             -17*math.log(p["m_b_over_m_s"]))
        assert (residuals[1]-residuals[0])/(2*step) == pytest.approx(0., abs=2e-10)


def test_geometric_mass_combination_detects_inconsistent_stored_ratio():
    records = _records()
    records["m_t_over_m_c"]["value"] *= math.exp(.01)
    result = evaluate_records(records)
    assert result["geometric_mass_relation"]["residual"] == pytest.approx(.08, abs=2e-14)
    assert not result["checks"]["geometric_log_mass_relation"]["passed"]
    assert not result["passed"]


@pytest.mark.parametrize("value", [0., -1., math.inf, math.nan, True])
def test_geometric_mass_combination_requires_positive_finite_ratio(value):
    records = _records()
    records["m_b_over_m_s"]["value"] = value
    with pytest.raises(ValueError, match="m_b_over_m_s"):
        evaluate_records(records)


def _six_mass_inputs():
    # An algebraic input set with independently fixed matching coefficients.
    # The heavy/light log ratios are 2, 2 and 2, so 8*2+9*2-17*2=0.
    geometric = (math.exp(2), 1., 2*math.exp(2), 2., 3*math.exp(2), 3.)
    factors = (1.1, .9, 1.03, 1.02, 1.2, .8)
    return {name: {"mass_GeV": mass*factor,
                   "mass_definition": "synthetic common-scale running mass",
                   "mass_scheme": "MSbar", "scale_GeV": 100.,
                   "mass_source": "specified algebraic test inputs",
                   "matching_factor": factor,
                   "matching_source": "fixed independently of the mass-combination residual",
                   "matching_order": "exact algebraic test relation"}
            for name, mass, factor in zip(MASS_SPECIES, geometric, factors)}


def _compare_mass_inputs(species, covariance):
    return compare_matched_mass_relation(species, covariance,
        covariance_order=MASS_COMPARISON_LOG_ORDER,
        covariance_source="specified joint logarithmic covariance for an algebraic test")


def test_six_mass_comparison_subtracts_matching_before_comparison():
    species = _six_mass_inputs()
    covariance = np.zeros((12, 12))
    covariance[0, 0] = .02**2
    initial = _compare_mass_inputs(species, covariance)
    assert abs(initial["physical_log_combination"]) > .1
    assert abs(initial["corrected_residual"]) < 2e-14
    assert initial["standard_deviation"] == pytest.approx(8*.02)
    assert "passed" not in initial
    species["top"]["mass_GeV"] *= math.exp(.03)
    displaced = _compare_mass_inputs(species, covariance)
    assert displaced["status"] == "evaluated"
    assert displaced["corrected_residual"] == pytest.approx(.24, abs=2e-14)
    assert displaced["standardized_residual"] == pytest.approx(1.5, abs=2e-13)
    assert displaced["inputs"]["top"]["matching_factor"] == 1.1


def test_six_mass_comparison_keeps_mass_matching_cross_covariance():
    # Equal log uncertainty in m_top and C_top cancels, including their covariance.
    noise = np.zeros(12)
    noise[0] = noise[6] = .02
    correlated = _compare_mass_inputs(_six_mass_inputs(), np.outer(noise, noise))
    assert correlated["variance"] == 0.
    assert correlated["standardized_residual"] is None
    independent = _compare_mass_inputs(_six_mass_inputs(), np.diag(noise**2))
    assert independent["variance"] == pytest.approx(2*(8*.02)**2)
    # A common dimensionful normalization cancels within every mass ratio.
    shared_units = np.r_[np.full(6, .07), np.zeros(6)]
    units = _compare_mass_inputs(_six_mass_inputs(), np.outer(shared_units, shared_units))
    assert units["variance"] == pytest.approx(0., abs=1e-15)


def test_six_mass_comparison_is_common_scale_invariant_and_retains_definitions():
    species = _six_mass_inputs()
    before = _compare_mass_inputs(species, np.eye(12)*1e-4)
    for item in species.values():
        item["mass_GeV"] *= 1000.
        item["scale_GeV"] *= 1000.
    after = _compare_mass_inputs(species, np.eye(12)*1e-4)
    assert after["corrected_residual"] == pytest.approx(before["corrected_residual"], abs=5e-14)
    assert after["standard_deviation"] == before["standard_deviation"]
    assert after["inputs"]["bottom"]["mass_scheme"] == "MSbar"
    assert after["inputs"]["bottom"]["scale_GeV"] == 100000.


def test_six_mass_comparison_reports_missing_matching_and_covariance():
    species = _six_mass_inputs()
    species["strange"]["matching_factor"] = None
    species["muon"].pop("matching_source")
    result = compare_matched_mass_relation(species)
    assert result["status"] == "incomplete"
    assert not result["comparison_performed"]
    assert result["corrected_residual"] is None
    assert result["standard_deviation"] is None
    assert set(result["missing_inputs"]) == {
        "strange.matching_factor", "muon.matching_source", "joint_log_covariance",
        "covariance_order", "covariance_source"}
    assert "passed" not in result
    assert set(compare_matched_mass_relation({})["missing_inputs"]) >= set(MASS_SPECIES)


@pytest.mark.parametrize("field,value", [("mass_GeV", -1.), ("matching_factor", 0.),
                                         ("scale_GeV", math.inf), ("mass_scheme", 7)])
def test_six_mass_comparison_rejects_invalid_definitions(field, value):
    species = _six_mass_inputs()
    species["bottom"][field] = value
    with pytest.raises(ValueError, match="bottom"):
        _compare_mass_inputs(species, np.eye(12))


@pytest.mark.parametrize("bad", [np.eye(6), np.diag([-1.]+[1.]*11),
                                  np.diag([math.nan]+[1.]*11),
                                  np.eye(12)+np.triu(np.ones((12, 12)), 1)])
def test_six_mass_comparison_rejects_invalid_covariance(bad):
    with pytest.raises(ValueError, match="covariance"):
        _compare_mass_inputs(_six_mass_inputs(), bad)


@pytest.mark.parametrize("order", [tuple(reversed(MASS_COMPARISON_LOG_ORDER)), 7])
def test_six_mass_comparison_rejects_ambiguous_covariance_order(order):
    with pytest.raises(ValueError, match="covariance_order"):
        compare_matched_mass_relation(_six_mass_inputs(), np.eye(12),
            covariance_order=order,
            covariance_source="algebraic test")


def test_published_joint_mass_constraint_uses_correlated_converted_masses(published_mass_reference):
    result = published_mass_reference
    assert result["reference_tables"] == [2, 3, 8]
    assert result["scale_GeV"] == 91.1876
    assert not result["native_finite_matching_calculated"]
    assert not result["production_replacement"]
    assert result["residuals"] == pytest.approx([2.69536514, .01127358165], abs=1e-8)
    # Independent covariance contraction by the gradient in mass coordinates.
    masses = np.array([result["masses_GeV"][n] for n in RUNNING_MASS_SPECIES])
    errors = np.array([result["mass_standard_deviations_GeV"][n] for n in RUNNING_MASS_SPECIES])
    gradient = np.asarray(MASS_SUM_RULE_WEIGHTS)/masses
    physical_covariance = np.asarray(result["mass_correlation"])*np.outer(errors, errors)
    expected = gradient@physical_covariance@gradient.T
    assert np.asarray(result["residual_covariance"]) == pytest.approx(expected)
    assert result["standard_deviations"] == pytest.approx([1.48016920, .000581683884], rel=1e-8)
    assert abs(expected[0, 1]) > 1e-7
    assert "passed" not in result
    assert "matching_factors" not in result


def test_joint_mass_constraint_is_homogeneous_and_detects_an_independent_mass_shift(published_mass_reference):
    initial = published_mass_reference
    masses = {k: v*1000 for k, v in initial["masses_GeV"].items()}
    common = dict(log_covariance=initial["log_mass_covariance"], scale_GeV=initial["scale_GeV"],
                  mass_definition=initial["mass_definition"], covariance_source="test covariance")
    rescaled = running_mass_sum_rules(masses, **common)
    assert rescaled["residuals"] == pytest.approx(initial["residuals"], abs=3e-14)
    masses["muon"] *= math.exp(.001)
    shifted = running_mass_sum_rules(masses, **common)
    assert np.subtract(shifted["residuals"], initial["residuals"]) == pytest.approx([-.009, .002], abs=3e-14)


def test_one_loop_sum_rule_beta_cancels_full_gauge_and_trace_terms():
    up, down, leptons = np.array([.02, .05, .9]), np.array([.01, .03, .08]), np.array([.002, .004, .015])
    # Independently construct complete one-loop diagonal SM beta functions.
    g1, g2, g3 = .46, .65, 1.1  # GUT-normalized g1.
    trace = 3*np.dot(up, up)+3*np.dot(down, down)+np.dot(leptons, leptons)
    bu = (1.5*(up**2-down**2)+trace-17*g1**2/20-9*g2**2/4-8*g3**2)/(16*math.pi**2)
    bd = (1.5*(down**2-up**2)+trace-g1**2/4-9*g2**2/4-8*g3**2)/(16*math.pi**2)
    be = (1.5*leptons**2+trace-9*g1**2/4-9*g2**2/4)/(16*math.pi**2)
    expected = [8*(bu[2]-bu[1])+9*(be[2]-be[1])-17*(bd[2]-bd[1]),
                2*be[1]-be[0]-be[2]]
    result = mass_sum_rule_beta_one_loop(up, down, leptons)
    assert result["derivatives_per_log_scale"] == pytest.approx(expected, abs=5e-16)
    assert result["gauge_contributions"] == [0., 0.]
    assert expected[0] != 0.


def test_one_loop_sum_rule_beta_ckm_phase_and_top_only_limits():
    first = mass_sum_rule_beta_one_loop([0, 0, 1], [0, 0, 0], [0, 0, 0])
    assert first["derivatives_per_log_scale"] == pytest.approx([75/(32*math.pi**2), 0.])
    phases = np.diag(np.exp(1j*np.array([.2, .7, -.9])))
    phased = mass_sum_rule_beta_one_loop([0, 0, 1], [0, 0, 0], [0, 0, 0], ckm=phases)
    assert phased["derivatives_per_log_scale"] == pytest.approx(first["derivatives_per_log_scale"])
    # Exchange the strange and bottom partners: the top contribution changes sign
    # in the down-sector ratio, a check on row/column mass-label pairing.
    swapped = mass_sum_rule_beta_one_loop([0, 0, 1], [0, 0, 0], [0, 0, 0],
        ckm=np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]]))
    assert swapped["derivatives_per_log_scale"][0] == pytest.approx(-27/(32*math.pi**2))


def test_qed_finite_matching_combination_retains_threshold_and_cancels_common_scale():
    masses = {"electron": .0005109989461, "muon": .1056583745, "tau": 1.77686}
    alpha = 1/137.035999084
    lower = charged_lepton_qed_log_matching(masses, scale_GeV=10., alpha=alpha)
    higher = charged_lepton_qed_log_matching(masses, scale_GeV=100., alpha=alpha)
    expected = 3*alpha/(2*math.pi)*math.log(masses["muon"]**2/(masses["electron"]*masses["tau"]))
    assert lower["matching_log_correction"] == pytest.approx(expected, abs=1e-16)
    assert higher["running_log_combination"] == pytest.approx(lower["running_log_combination"], abs=1e-15)
    assert expected > .008
    zero = charged_lepton_qed_log_matching(masses, scale_GeV=100., alpha=0.)
    assert zero["matching_log_correction"] == 0.


def test_finite_lepton_transfer_against_three_independent_running_equations():
    from scipy.integrate import quad, solve_ivp
    initial = np.array([.02, .08, .3])
    duration = 3.
    common = lambda t: .02*math.sin(t)
    integrated_common = lambda t: .02*(1-math.cos(t))
    b = 3/(32*math.pi**2)
    integral = 2*b*quad(lambda t: math.exp(2*integrated_common(t)), 0, duration,
                        epsabs=1e-13, epsrel=1e-13)[0]
    result = charged_lepton_finite_transfer(initial,
        common_log_factor=integrated_common(duration), self_integral=integral)
    direct = solve_ivp(lambda t, y: y*(common(t)+b*y*y), (0, duration), initial,
                       method="DOP853", rtol=2e-12, atol=1e-14)
    assert direct.success
    assert result["final_yukawa"] == pytest.approx(direct.y[:, -1], rel=2e-12)
    weights = np.array([-1., 2., -1.])
    actual_shift = float(weights@np.log(direct.y[:, -1]/initial))
    assert result["charged_lepton_log_correction"] == pytest.approx(actual_shift, abs=1e-13)
    enclosure = charged_lepton_transfer_enclosure(initial, log_scale_span=duration,
                                                   common_coefficient_bounds=(0., .02))
    low, high = enclosure["charged_lepton_log_correction_interval"]
    assert low <= actual_shift <= high
    assert enclosure["minimum_denominator_lower_bound"] > 0


def test_finite_lepton_transfer_composes_and_reverses_without_a_matching_input():
    initial = [.02, .08, .3]
    first = charged_lepton_finite_transfer(initial, common_log_factor=.1, self_integral=.2)
    second = charged_lepton_finite_transfer(first["final_yukawa"],
                                            common_log_factor=-.03, self_integral=.1)
    total = charged_lepton_finite_transfer(initial, common_log_factor=.07,
                                           self_integral=.2+math.exp(.2)*.1)
    assert second["final_yukawa"] == pytest.approx(total["final_yukawa"], rel=2e-15)
    assert total["charged_lepton_log_correction"] == pytest.approx(
        first["charged_lepton_log_correction"]+second["charged_lepton_log_correction"], abs=2e-16)
    reversed_result = charged_lepton_finite_transfer(first["final_yukawa"],
        common_log_factor=-.1, self_integral=-.2*math.exp(-.2))
    assert reversed_result["final_yukawa"] == pytest.approx(initial, rel=2e-15)


def test_finite_lepton_interval_is_outward_and_rejects_an_uncertified_denominator():
    import mpmath as mp
    initial = [1e-5, 1e-3, 1e-2]
    enclosure = charged_lepton_transfer_enclosure(initial, log_scale_span=10.,
                                                   common_coefficient_bounds=(0., 0.))
    with mp.workdps(70):
        integral = 3*mp.mpf(10)/(16*mp.pi**2)
        logterms = [mp.log(1-integral*mp.mpf(y)**2) for y in initial]
        exact = (logterms[0]-2*logterms[1]+logterms[2])/2
        low, high = enclosure["charged_lepton_log_correction_interval"]
        assert mp.mpf(low) <= exact <= mp.mpf(high)
    for common in (-.1, 0., .1):
        bounded = charged_lepton_transfer_enclosure(initial, log_scale_span=10.,
                                                     common_coefficient_bounds=(-.1, .1))
        integral = (3/(16*math.pi**2)*math.expm1(20*common)/(2*common)
                    if common else 30/(16*math.pi**2))
        actual = charged_lepton_finite_transfer(initial, common_log_factor=10*common,
                                                 self_integral=integral)
        assert bounded["charged_lepton_log_correction_interval"][0] <= actual["charged_lepton_log_correction"]
        assert actual["charged_lepton_log_correction"] <= bounded["charged_lepton_log_correction_interval"][1]
    with pytest.raises(ValueError, match="denominator"):
        charged_lepton_transfer_enclosure([.1, .5, 2.], log_scale_span=100.,
                                          common_coefficient_bounds=(0., 0.))


def test_lepton_matching_spread_is_a_sharp_necessary_bound():
    required, known = (.020, .022), (.006, .008)
    bound = lepton_matching_spread_bound(required, known_correction_interval=known)
    assert bound["minimum_log_matching_spread"] == pytest.approx(.006)
    # A source-independent common offset does not change the constraint.
    logs = np.array([-.1, -.094, -.1])
    residual = float(np.array([-1., 2., -1.])@logs)
    assert residual == pytest.approx(.012)
    assert np.ptp(logs) == pytest.approx(bound["minimum_log_matching_spread"])
    overlapping = lepton_matching_spread_bound((.006, .010), known_correction_interval=known)
    assert overlapping["minimum_log_matching_spread"] == 0.


@pytest.mark.parametrize("bad", [np.ones((3, 3)), np.diag([1., 1., .9]), [[1, 0], [0, 1]]])
def test_sum_rule_beta_rejects_nonunitary_or_wrong_shape_ckm(bad):
    with pytest.raises(ValueError, match="ckm"):
        mass_sum_rule_beta_one_loop([0, 0, 1], [0, 0, 0], [0, 0, 0], ckm=bad)


def test_running_mass_constraint_rejects_incomplete_or_indefinite_data(published_mass_reference):
    ref = published_mass_reference
    kwargs = dict(scale_GeV=ref["scale_GeV"], mass_definition=ref["mass_definition"], covariance_source="test")
    with pytest.raises(ValueError, match="seven"):
        running_mass_sum_rules({"top": 173.}, np.eye(7), **kwargs)
    with pytest.raises(ValueError, match="semidefinite"):
        running_mass_sum_rules(ref["masses_GeV"], np.diag([-1.]+[1.]*6), **kwargs)


def test_joint_mass_and_cmb_references_use_the_registered_comparison_table(monkeypatch):
    references = {key: comparison_inputs.published_sm_value(key)
                  for key in comparison_inputs.SM_INPUT_KEYS}
    read_keys = []
    def read(key):
        read_keys.append(key)
        return references[key]
    monkeypatch.setattr(comparison_inputs, "sm_value", read)
    baseline = comparison_inputs.published_running_mass_benchmark()
    remainder = baseline['remaining_lepton_matching']
    target = baseline['weighted_finite_matching_constraints']['charged_lepton']
    qed = baseline['charged_lepton_QED_check']['matching_log_correction']
    assert remainder['central_constraint']['minimum_log_matching_spread'] == pytest.approx(abs(target-qed)/2)
    assert not remainder['production_parameters_updated']
    references["running_mass_reference"]["masses_GeV"][0] *= math.exp(.001)
    changed = comparison_inputs.published_running_mass_benchmark()
    assert changed["residuals"][0]-baseline["residuals"][0] == pytest.approx(.008, abs=2e-14)
    assert set(read_keys) == {"running_mass_reference", "charged_lepton_pole_reference"}
    cmb = references["CMB_MONOPOLE"]
    assert cmb["temperature_K"] == references["T_CMB_K"]
    assert cmb["standard_deviation_K"] == .00057
    assert "10.1088/0004-637X/707/2/916" in cmb["citation"]
