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

"""Independent limits, residuals and numerical convergence; no parameter writes."""
from pathlib import Path
import json
import math
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cg_core.electroweak import (
    bottom_vertex_width_shift, heavy_top_x, leading_rho_bar,
    leading_universal_parameters, neutral_current_widths, veltman_delta_rho,
)
from cg_core.gauge_running import common_origin, geometric_run, run_geometric
from cg_core.rk4 import rk4_integrate
from cg_core.beta_functions import beta_gauge, _B_GAUGE, _BM_GAUGE, _A_GAUGE
from cg_frg.ewsb import ew_precision, ew_one_loop
from cg_core.quantities import readout_definition


@pytest.fixture(scope="module")
def baseline():
    with (ROOT / "cg_params.json").open(encoding="utf-8") as handle:
        data = json.load(handle)["parameters"]
    from cg_core.params import resolved_records
    return {k: record["value"] for k, record in resolved_records(data).items()}


@pytest.mark.parametrize("masses", [(0., 0.), (2., 2.), (100., 100.)])
def test_custodial_zero(masses):
    assert ew_precision.delta_rho(1., *masses) == 0.
    assert ew_one_loop.delta_rho(1., *masses) == 0.


def test_single_massless_and_swap():
    exact = 3.0 * 4.0 / (8.0 * math.pi**2 * math.sqrt(2.0))
    assert veltman_delta_rho(1., 2., 0.) == pytest.approx(exact, rel=2e-15)
    assert veltman_delta_rho(1., 0., 2.) == pytest.approx(exact, rel=2e-15)


@pytest.mark.parametrize("a,b", [(173., 4.2), (100., 99.),
                                 (100., 100. + 1e-6), (100., 100. + 1e-10)])
def test_near_degeneracy_against_high_precision(a, b):
    mp = pytest.importorskip("mpmath")
    with mp.workdps(80):
        x, y = mp.mpf(a)**2, mp.mpf(b)**2
        expected = float(3 * (x + y - 2*x*y/(x-y)*mp.log(x/y)) /
                         (8 * mp.pi**2 * mp.sqrt(2)))
    actual = veltman_delta_rho(1., a, b)
    assert actual > 0
    assert actual == pytest.approx(expected, rel=5e-14, abs=0.)
    assert actual == veltman_delta_rho(1., b, a)


def test_weak_root_and_rejected_no_root():
    mz, a0, az, gf, drho = 91.1, 1/137., 1/128., 1.166e-5, .0094
    x, mw = ew_precision.solve_MW(mz, a0, az, gf, drho)
    rhs = math.pi*a0/(math.sqrt(2)*gf*mz*mz) / (a0/az+(1-x)/x*drho)
    assert x*(1-x) == pytest.approx(rhs, rel=2e-14)
    assert mw == pytest.approx(mz*math.sqrt(1-x), rel=2e-15)
    with pytest.raises(ValueError):
        ew_precision.solve_MW(1., a0, az, gf, drho)


def test_failed_iterations_are_not_results(baseline):
    p = baseline
    with pytest.raises(RuntimeError, match="did not converge"):
        ew_precision.mz_fixed_point(p["v_HIGGS"], p["g1_MG_geo"],
            p["g2_MG"], p["g3_MG_geo"], p["M_G"], max_iterations=0)
    with pytest.raises(RuntimeError, match="did not converge"):
        common_origin(p["g1_MG_geo"], p["g2_MG"], p["M_G"],
                      p["M_P"]*math.sqrt(math.pi)*p["tau"]/math.sqrt(3.),
                      max_iterations=0)
    with pytest.raises(RuntimeError, match="did not converge"):
        ew_one_loop.solve_MW(1/137., 1.166e-5, 91.1, 125., 173., 4., max_iter=0)


def test_observed_fourth_order_for_actual_gauge_flow(baseline):
    p = baseline
    initial = [p["g1_MG_geo"], p["g2_MG"], p["g3_MG_geo"]]
    dt = math.log(p["v_HIGGS"]/p["M_G"])
    rhs = lambda g: beta_gauge(*g, 1.)
    states = [rk4_integrate(rhs, initial, dt, n) for n in (100, 200, 400)]
    differences = [abs(states[i][2]-states[i+1][2]) for i in (0, 1)]
    assert 13 < differences[0]/differences[1] < 19


def test_reciprocal_variable_independent_solver(baseline):
    scipy = pytest.importorskip("scipy.integrate")
    p = baseline
    initial = [p["g1_MG_geo"], p["g2_MG"], p["g3_MG_geo"]]
    pi2 = 16*math.pi**2
    def rhs(_t, u):
        return [-2/pi2*(_B_GAUGE[i] +
                (sum(_BM_GAUGE[i][j]/u[j] for j in range(3))-_A_GAUGE[i])/pi2)
                for i in range(3)]
    independent = scipy.solve_ivp(rhs, (0., math.log(p["v_HIGGS"]/p["M_G"])),
            [1/g**2 for g in initial], method="DOP853", rtol=3e-13, atol=1e-14)
    assert independent.success
    expected = [1/math.sqrt(u) for u in independent.y[:, -1]]
    checked = geometric_run(initial, p["M_G"], p["v_HIGGS"])
    assert checked.couplings == pytest.approx(expected, rel=6e-11)
    finer = geometric_run(initial, p["M_G"], p["v_HIGGS"], rtol=2e-13, atol=2e-15)
    assert finer.couplings == pytest.approx(expected, rel=1e-12)


def test_common_origin_forward_boundary_and_scale_identity(baseline):
    p = baseline
    scale = p["M_P"]*math.sqrt(math.pi)*p["tau"]/math.sqrt(3.)
    result = common_origin(p["g1_MG_geo"], p["g2_MG"], p["M_G"], scale)
    initial = (p["g1_MG_geo"], p["g2_MG"], result["g3_initial"])
    actual = run_geometric(initial, p["M_G"], scale, rtol=2e-13, atol=2e-15)
    expected = actual[1]*(1+(actual[1]**2/(4*math.pi))**2/(8/3))
    assert actual[2] == pytest.approx(expected, rel=8e-12)
    assert run_geometric(initial, p["M_G"], p["M_G"]) == initial


def test_effective_lineshape_uses_one_neutral_current_amplitude(baseline, monkeypatch):
    """Angles, partial widths, sums and ratios share the same amplitude."""
    values = dict(baseline)
    published = {}

    def record(key, value, *reference, **metadata):
        published[key] = {"value": value, **metadata}
        values[key] = value

    monkeypatch.setattr(ew_one_loop, "get", values.__getitem__)
    monkeypatch.setattr(ew_one_loop, "pset", record)
    monkeypatch.setattr(ew_one_loop, "compare_and_set", record)
    monkeypatch.setattr(ew_one_loop, "sm_value", lambda _key: 1.0)
    result = ew_one_loop.compute()

    partial = result["partial_widths"]
    assert result["Gamma_had_corr"] == pytest.approx(
        sum(partial[name] for name in ("u", "c", "d", "s", "b")), rel=2e-15)
    assert (result["Gamma_Z_corr"] - result["Gamma_had_corr"]
            == pytest.approx(result["Gamma_l_corr"] + result["Gamma_inv_corr"],
                             rel=2e-15))
    assert result["R_b_corr"] * result["Gamma_had_corr"] == pytest.approx(
        result["Gamma_b_corr"], rel=2e-15)
    assert result["R_l_corr"] * result["Gamma_l_corr"] / 3 == pytest.approx(
        result["Gamma_had_corr"], rel=2e-15)
    assert result["sigma_had_corr_nb"] / 3.89379e5 * baseline["M_Z_pred"]**2 / (
        12 * math.pi) == pytest.approx(
            (result["Gamma_l_corr"] / 3 / result["Gamma_Z_corr"])
            * (result["Gamma_had_corr"] / result["Gamma_Z_corr"]), rel=2e-15)

    for suffix, unit in (("Gamma_had", "GeV"), ("Gamma_Z", "GeV"),
                         ("R_b", "1"), ("R_l", "1"), ("sigma_had", "nb")):
        key = suffix + "_pred_lead1loop"
        assert key in published
        assert published[key]["dependencies"]
        definition = readout_definition(key)
        assert definition.unit == unit
        assert values[suffix + "_pred"] == baseline[suffix + "_pred"]

    # A separately stored Born angle or width cannot alter this amplitude.
    values["Gamma_b_pred"] *= 7.0
    values["Gamma_Z_pred"] *= 3.0
    values["s2_thetaW_MZ"] = 0.27
    repeated = ew_one_loop.compute()
    assert repeated == result
    assert published["z_pole_partial_widths"]["value"] == partial
    assert set(published["Gamma_inv_pred_lead1loop"]["dependencies"]) == {
        "M_Z_pred", "v_HIGGS", "m_t_pred"}
    assert "alpha_s_MZ_pred" not in published["Gamma_l_pred_lead1loop"]["dependencies"]
    assert "Gamma_l_pred_lead1loop" in published["R_l_pred_lead1loop"]["dependencies"]


def test_effective_neutral_current_normalization_and_zero_top_limit():
    mz, alpha, gf, mt = 91.1, 1 / 128.2, 1.166e-5, 174.0
    drho = leading_rho_bar(gf, mt)
    effective = leading_universal_parameters(mz, alpha, gf, drho)
    sbar = effective["s2_eff"]
    # Denner's neutral-current coupling normalization, Eq. (8.25).
    left = math.pi * alpha / (sbar * (1.0 - sbar))
    right = math.sqrt(2.0) * gf * mz**2 * effective["rho_nc"]
    assert left == pytest.approx(right, rel=3e-15)
    assert math.pi * alpha / sbar == pytest.approx(
        math.sqrt(2.0) * gf * effective["M_W"]**2, rel=3e-15)
    assert sbar == pytest.approx(
        effective["s2_os"] + (1.0-effective["s2_os"]) * drho, rel=3e-15)
    tree = leading_universal_parameters(mz, alpha, gf, leading_rho_bar(gf, 0.0))
    assert tree["rho_nc"] == 1.0
    assert tree["s2_eff"] == pytest.approx(tree["s2_os"], rel=3e-15)
    widths = neutral_current_widths(mz, tree["s2_eff"], gf, 0.0, 0.0)
    # Independent massless chiral trace, with only the left neutrino current.
    neutrino = gf * mz**3 / (12.0 * math.sqrt(2.0) * math.pi)
    assert widths["nu_e"] == pytest.approx(neutrino, rel=2e-15)
    gl, gr = -.5 + tree["s2_eff"], tree["s2_eff"]
    assert widths["e"] / neutrino == pytest.approx(4*(gl*gl+gr*gr), rel=2e-15)
    assert widths["b"] == widths["d"]


@pytest.mark.parametrize("angle", [0.20, 0.231, 0.27])
def test_bottom_interference_from_independent_rho_kappa_amplitudes(angle):
    # PDG rho_b=1-4x and kappa_b=1+2x, expanded at x=0.
    def exact_quadratic(x):
        rho, kappa = 1-4*x, 1+2*x
        gv = math.sqrt(rho) * (-.5 + 2*kappa*angle/3)
        ga = -.5 * math.sqrt(rho)
        return gv*gv + ga*ga

    h = 1e-5
    derivative = (exact_quadratic(h)-exact_quadratic(-h))/(2*h)
    xt = heavy_top_x(1.166e-5, 174.0)
    expected = xt * derivative / exact_quadratic(0.0)
    retained = bottom_vertex_width_shift(angle, xt)
    assert retained == pytest.approx(expected, rel=2e-10)
    baseline = neutral_current_widths(91., angle, 1.166e-5, 1/128., .118)
    corrected = neutral_current_widths(91., angle, 1.166e-5, 1/128., .118,
                                       x_t=xt)
    assert corrected["b"]/baseline["b"]-1 == pytest.approx(retained, rel=2e-14)
    assert corrected["d"] == baseline["d"]
    assert corrected["Z"]-baseline["Z"] == pytest.approx(
        corrected["b"]-baseline["b"], rel=1e-12)
    # The relative width is not the left-amplitude factor -2x.
    assert abs(retained / (-2*xt) - 1) > 1.0


def test_neutral_current_energy_units_and_common_ratio_cancellation():
    mz, gf, mt, alpha, alphas = 91., 1.166e-5, 174., 1/128., .118
    drho = leading_rho_bar(gf, mt)
    effective = leading_universal_parameters(mz, alpha, gf, drho)
    xt = heavy_top_x(gf, mt)
    def readout(scale, rho_factor=1.0):
        return neutral_current_widths(mz*scale, effective["s2_eff"],
            gf/scale**2, alpha, alphas,
            rho_nc=effective["rho_nc"]*rho_factor, x_t=xt)
    original, converted, normalized = readout(1.), readout(1000.), readout(1., 1.7)
    for name, width in original.items():
        assert converted[name] == pytest.approx(1000*width, rel=3e-15)
        assert normalized[name] == pytest.approx(1.7*width, rel=3e-15)
    assert normalized["b"]/normalized["had"] == pytest.approx(
        original["b"]/original["had"], rel=3e-15)
    assert heavy_top_x(gf/1e6, mt*1000) == pytest.approx(xt, rel=2e-15)


@pytest.mark.parametrize("changes", [dict(M_Z=-1.), dict(alpha_Z=float("nan")),
    dict(G_F=0.), dict(delta_rho_bar=1.), dict(delta_rho_bar=-.1), dict(M_Z=1.)])
def test_invalid_effective_neutral_current_inputs(changes):
    inputs = dict(M_Z=91., alpha_Z=1/128., G_F=1.166e-5, delta_rho_bar=.0094)
    inputs.update(changes)
    with pytest.raises(ValueError):
        leading_universal_parameters(**inputs)


@pytest.mark.parametrize("angle,xt", [(0., 0.), (.5, 0.), (.23, -.001),
                                      (.23, 1.), (.23, float("nan"))])
def test_invalid_bottom_amplitude_inputs(angle, xt):
    with pytest.raises(ValueError):
        bottom_vertex_width_shift(angle, xt)
