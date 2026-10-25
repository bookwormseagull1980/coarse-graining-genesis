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


@pytest.mark.parametrize("s,m0,m1,scale", [
    (-1e-16, 1e-9, 2e-9, 1e-8), (-1e-10, 2., 3., 7.),
    (100., 0., 0., 7.), (1., 1e-9, 100., 7.),
    (complex(1., 2.), 2., 3., 7.), (30., 2., 3., 7.),
    (1., 0., 1., 7.), (-1e-10, 0., 2., 7.),
    (25., 2., 3., 7.), (complex(1., -2.), 2., 3., 7.),
])
def test_two_point_scalar_against_independent_parameter_integral(s, m0, m1, scale):
    """The -i0 branch, mass hierarchies and small momenta use the same integral."""
    mp = pytest.importorskip("mpmath")
    with mp.workdps(65):
        momentum, a, b = mp.mpc(s), mp.mpf(m0)**2, mp.mpf(m1)**2
        roots = []
        if momentum.imag == 0 and momentum.real > 0:
            disc = (momentum-a-b)**2-4*a*b
            if disc.real >= 0:
                roots = [r.real for r in (
                    (momentum+b-a-mp.sqrt(disc))/(2*momentum),
                    (momentum+b-a+mp.sqrt(disc))/(2*momentum))
                    if r.imag == 0 and 0 < r.real < 1]

        def integrand(x):
            denominator = x*a+(1-x)*b-x*(1-x)*momentum
            if denominator == 0:
                return mp.mpf(0)  # isolated integrable endpoint/root
            if momentum.imag == 0 and denominator.real < 0:
                return -mp.log(-denominator.real/scale**2)+mp.j*mp.pi
            return -mp.log(denominator/scale**2)

        expected = complex(mp.quad(integrand, [0, *sorted(set(roots)), 1]))
    actual = ew_one_loop._B0(s, m0, m1, scale)
    assert actual == pytest.approx(expected, rel=3e-11, abs=3e-11)
    assert ew_one_loop._B0(s, m1, m0, scale) == pytest.approx(actual, abs=3e-11)
    # A change of energy unit cannot turn nonzero momentum into the zero limit.
    unit = 2**-16  # exact binary rescaling, including the ill-conditioned threshold
    assert ew_one_loop._B0(s*unit**2, m0*unit, m1*unit, scale*unit) == pytest.approx(
        actual, rel=3e-11, abs=3e-11)


@pytest.mark.parametrize("mass,small_mass,scale", [(80.4, 1e-6, 91.2), (1., 1e-16, 1.)])
def test_two_point_on_shell_resolves_the_small_mass_endpoint_layer(mass, small_mass, scale):
    mp = pytest.importorskip("mpmath")
    with mp.workdps(65):
        a, b, s = mp.mpf(mass)**2, mp.mpf(small_mass)**2, mp.mpf(mass*mass)
        width = mp.mpf(small_mass)/mass
        points = [mp.mpf(0), width, 8*width, 64*width, mp.mpf(1)]
        expected = complex(mp.quad(
            lambda x: -mp.log((x*a+(1-x)*b-x*(1-x)*s)/scale**2), points))
    actual = ew_one_loop._B0(mass*mass, mass, small_mass, scale)
    assert actual == pytest.approx(expected, rel=3e-12, abs=3e-12)
    assert ew_one_loop._B0(mass*mass, small_mass, mass, scale) == pytest.approx(
        expected, rel=3e-12, abs=3e-12)


@pytest.mark.parametrize("m0,m1", [(0., 3.), (2., 3.), (2., 2.+1e-10)])
def test_two_point_zero_derivative_against_parameter_integral(m0, m1):
    mp = pytest.importorskip("mpmath")
    with mp.workdps(50):
        a, b = mp.mpf(m0)**2, mp.mpf(m1)**2
        expected = float(mp.quad(lambda x: x*(1-x)/(x*a+(1-x)*b), [0, 1]))
    assert ew_one_loop._dB0dp2_at0(m0, m1) == pytest.approx(expected, rel=2e-12)
    for s in (0., -1e-12, complex(1e-12, 1e-12)):
        assert ew_one_loop._B0_difference_quotient(s, m0, m1, 7.) == pytest.approx(
            expected, rel=2e-12, abs=1e-14)


def test_wz_self_energy_coefficient_uses_inverse_cosine_squared(monkeypatch):
    """B.4 has c_W^-2, while the stored c2 already denotes c_W²."""
    s, mw, mz, mh, s2, alpha = -16., 10., 12., 15., .25, 1/137.
    c2 = 1-s2
    monkeypatch.setattr(ew_one_loop, "_B0", lambda _s, a, b, _mu:
                        1. if {a, b} == {mw, mz} else 0.)
    actual = ew_one_loop._sigma_W(s, [], mw, mz, mh, s2, c2, alpha, 20.)
    # Independently retain the rational terms of the other boson brackets.
    rational = (2/3)*s/3+(4*c2-1)*(2/3)*s/(12*s2)-(2/3)*s/(12*s2)
    coefficient = ((40*c2-1)*s+(16*c2+54-10/c2)*mw**2)/(12*s2)
    assert actual == pytest.approx(-alpha/(4*math.pi)*(coefficient+rational), rel=2e-14)


def test_self_energy_zero_limits_and_massless_neutrinos():
    mw, mz, mh, alpha = 80.4, 91.1876, 125.1, 1/137.035999
    s2 = 1-(mw/mz)**2
    ferm = ew_one_loop._fermion_set(172.5, 4.2)
    args = (ferm, mw, mz, mh, s2, 1-s2, alpha, mz)
    for function in (ew_one_loop._sigma_W, ew_one_loop._sigma_ZZ):
        zero = function(0., *args)
        nearby = function(-1e-8, *args)
        timelike = function(mz*mz, *args)
        assert all(math.isfinite(x) for x in (zero.real, zero.imag, timelike.real, timelike.imag))
        assert nearby == pytest.approx(zero, rel=2e-10, abs=3e-9)
    # A zero mass times the individually IR-divergent B0(0;0,0) is zero.
    assert ew_one_loop._sigma_AA(0., [("massless", 1., .5, 1., 0.)],
                                mw, s2, alpha, mz) == 0j
    with pytest.raises(ValueError, match="IR divergent"):
        ew_one_loop._B0(0., 0., 0., mz)


def test_complete_delta_r_scale_cancellation_and_original_solver_residual():
    """All self energies must cancel their common subtraction scale in Delta r."""
    mw, mz, mh, alpha, gf = 80.4, 91.1876, 125.1, 1/137.035999, 1.1663787e-5
    s2 = 1-(mw/mz)**2
    ferm = ew_one_loop._fermion_set(172.5, 4.2)
    results = [ew_one_loop.delta_r(ferm, mw, mz, mh, s2, alpha, scale)
               for scale in (mz/2, mz, 2*mz)]
    assert results == pytest.approx([results[1]]*3, rel=2e-11, abs=2e-12)
    solved = ew_one_loop.solve_MW(alpha, gf, mz, mh, 172.5, 4.2)
    actual_s2 = 1-(solved["M_W"]/mz)**2
    dr = ew_one_loop.delta_r(ferm, solved["M_W"], mz, mh, actual_s2, alpha, mz)
    lhs = solved["M_W"]**2*actual_s2
    rhs = math.pi*alpha/(math.sqrt(2)*gf)*(1+dr.real)
    assert lhs == pytest.approx(rhs, rel=2e-9)


def test_w_self_energy_does_not_invent_missing_quark_partners():
    with pytest.raises(ValueError, match="both members"):
        ew_one_loop._sigma_W(-1., [("u", 2/3, .5, 3, 1.)],
                             80., 91., 125., .23, .77, 1/137., 91.)


@pytest.mark.parametrize("momentum_squared", [-16., -36.])
def test_w_polarization_lepton_has_unit_colour_weight(momentum_squared):
    """An added colour-singlet doublet must contribute once, not three times."""
    fermions = [(name, 0., 0., 3, mass) for name, mass in
                zip(("u", "d", "c", "s", "t", "b"), (.8, 1.2, 1.7, 1.3, 2.5, 2.1))]
    ml, mu, s2, alpha = .5, 20., .25, 1/137.
    args = (10., 12., 15., s2, 1-s2, alpha, mu)
    baseline = ew_one_loop._sigma_W(momentum_squared, fermions, *args)
    with_lepton = ew_one_loop._sigma_W(
        momentum_squared, fermions + [("e", -1., -.5, 1, ml)], *args)
    b0 = ew_one_loop._B0(momentum_squared, 0., ml, mu)
    doublet = (-(momentum_squared-ml**2/2)*b0 + momentum_squared/3
               + ml**2*ew_one_loop._B0(0., ml, ml, mu)
               + ml**4/(2*momentum_squared)
               * (b0-ew_one_loop._B0(0., 0., ml, mu)))
    expected = -alpha/(4*math.pi)*(2/3)/(2*s2)*doublet
    assert with_lepton-baseline == pytest.approx(expected, rel=2e-8, abs=1e-10)


@pytest.mark.parametrize("momentum_squared", [-16., -36.])
def test_w_polarization_quark_doublet_keeps_three_colours(momentum_squared):
    """Changing a quark doublet retains its factor three after singlet isolation."""
    fermions = [(name, 0., 0., 3, mass) for name, mass in
                zip(("u", "d", "c", "s", "t", "b"), (.8, 1.2, 1.7, 1.3, 2.5, 2.1))]
    fermions.append(("e", -1., -.5, 1, .5))
    mu, s2, alpha = 20., .25, 1/137.
    args = (10., 12., 15., s2, 1-s2, alpha, mu)
    changed = [(name, q, i3, nc, 1.9 if name == "u" else mass)
               for name, q, i3, nc, mass in fermions]

    def doublet(up, down):
        b0 = ew_one_loop._B0(momentum_squared, up, down, mu)
        return (-(momentum_squared-(up**2+down**2)/2)*b0 + momentum_squared/3
                + up**2*ew_one_loop._B0(0., up, up, mu)
                + down**2*ew_one_loop._B0(0., down, down, mu)
                + (up**2-down**2)**2/(2*momentum_squared)
                * (b0-ew_one_loop._B0(0., up, down, mu)))

    actual = (ew_one_loop._sigma_W(momentum_squared, changed, *args)
              - ew_one_loop._sigma_W(momentum_squared, fermions, *args))
    expected = -alpha/(4*math.pi)*(2/3)/(2*s2)*3*(doublet(1.9, 1.2)-doublet(.8, 1.2))
    assert actual == pytest.approx(expected, rel=2e-8, abs=1e-10)


@pytest.mark.parametrize("momentum_squared", [-1., -16.])
def test_photon_polarization_subtraction_against_feynman_parameter(momentum_squared):
    """A Dirac current has the full QED normalization after charge subtraction."""
    mp = pytest.importorskip("mpmath")
    mass, charge, colours = 2., 2/3, 3.
    mw, s2, alpha, scale = 80., .23, 1/137., 7.
    fermion = [("probe", charge, .5, colours, mass)]
    difference = (ew_one_loop._sigma_AA(momentum_squared, fermion, mw, s2, alpha, scale)
                  - ew_one_loop._sigma_AA(momentum_squared, [], mw, s2, alpha, scale))
    derivative = (ew_one_loop._PiAA0(fermion, mw, s2, alpha, scale)
                  - ew_one_loop._PiAA0([], mw, s2, alpha, scale))
    with mp.workdps(50):
        expected = -2*mp.mpf(alpha)/mp.pi*colours*mp.mpf(charge)**2*momentum_squared*mp.quad(
            lambda x: x*(1-x)*mp.log(1-momentum_squared*x*(1-x)/mass**2), [0, 1])
    assert difference-momentum_squared*derivative == pytest.approx(
        complex(expected), rel=2e-10, abs=1e-13)


@pytest.mark.parametrize("channel", ["AA", "AZ", "ZZ"])
def test_neutral_gauge_boson_normalization(channel, monkeypatch):
    """Denner B.1--B.3 place the bosonic braces outside the fermion factor 2/3."""
    s, mw, mz, mh, s2, alpha, scale = -16., 10., 12., 15., .25, 1/137., 20.
    c2 = 1-s2
    if channel == "AA":
        # A constant B0 leaves the pure-W bracket equal to 3s.
        monkeypatch.setattr(ew_one_loop, "_B0", lambda *_args: 1.)
        actual = ew_one_loop._sigma_AA(s, [], mw, s2, alpha, scale)
        expected = -alpha/(4*math.pi)*3*s
    else:
        # Zeroing B0 isolates the independently specified rational numerator terms.
        monkeypatch.setattr(ew_one_loop, "_B0", lambda *_args: 0.)
        if channel == "AZ":
            actual = ew_one_loop._sigma_AZ(s, [], mw, s2, c2, alpha, scale)
            expected = alpha/(4*math.pi)*s/(9*math.sqrt(s2*c2))
        else:
            actual = ew_one_loop._sigma_ZZ(s, [], mw, mz, mh, s2, c2, alpha, scale)
            expected = -alpha/(4*math.pi)*s*(2*c2-1)/(9*s2*c2)
    assert actual == pytest.approx(expected, rel=2e-14, abs=1e-15)


def test_photon_zero_momentum_w_normalization():
    """At Q=M_W the pure-W derivative is the finite constant -alpha/(6pi)."""
    mw, alpha = 80., 1/137.
    assert ew_one_loop._PiAA0([], mw, .23, alpha, mw) == pytest.approx(
        -alpha/(6*math.pi), rel=2e-14, abs=1e-15)


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
