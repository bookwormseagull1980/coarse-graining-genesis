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

"""Assigned diagnostics: geometry, source derivative and integration conventions."""
import math
import numpy as np
import pytest
from scipy.integrate import quad
from cg_frg.gravity.zk_gravitational_rg import (eta_N, geometric_Z, z_dim,
                                              logarithmic_correction)
from cg_frg.gravity.chi_pole_condition import (_geometry, find_crossing, x_chi,
                                             crossing_derivative, pi2_chi)
from cg_frg.frg.discrete_flow import resolution_width, beta_sigma, free_carrier_checks
from scripts.analyze_gravity_ir import (
    p_laplacian_scan, scan_scale_law, scan_internal_trajectory)


def test_logarithmic_correction_on_the_declared_running_background():
    mg, mp, c = 2., 3., 2.49
    dof = {"scalar": 4, "fermion": 45, "vector": 24}
    z0 = z_dim(mg, mp)
    numerical = quad(lambda t: eta_N(math.exp(t), c/math.exp(t),
                                     geometric_Z(math.exp(t), z0), dof),
                     0, math.log(mp/mg), epsabs=1e-13, epsrel=1e-13)[0]
    assert logarithmic_correction(mg, mp, c, dof) == pytest.approx(numerical, rel=1e-13)
    assert logarithmic_correction(2000, 3000, c, dof) == pytest.approx(numerical, rel=1e-13)
    assert logarithmic_correction(mp, mp, c, dof) == 0


def test_chi_derivative_and_internal_detuning_residue():
    c = 2.4935343325226915
    geo = _geometry(c, math.sqrt(math.pi)/c, 1.)
    root = find_crossing(2., geo, 0.02)
    slope = crossing_derivative(root, 2., geo, 0.02)
    fd = (x_chi(root+1e-5, 2., geo, 0.02)-x_chi(root-1e-5, 2., geo, 0.02))/2e-5
    assert slope > 0 and slope == pytest.approx(fd, rel=2e-9)
    residue = pi2_chi(root, 2., geo, 0.02)/slope
    delta = 1e-6
    measured = delta*pi2_chi(root-delta, 2., geo, 0.02)/(1-x_chi(root-delta, 2., geo, 0.02))
    assert measured == pytest.approx(residue, rel=5e-6)
    for alpha in (1., 3.):
        assert alpha*find_crossing(alpha, geo, 0.02) == pytest.approx(2*root, rel=1e-12)


def test_radius_changes_do_not_select_the_detuning_crossing():
    products = []
    for c in (1.5, 2.4935343325226915, 3.5):
        geo = _geometry(c, math.sqrt(math.pi)/c, 1.)
        products.append(x_chi(0., 2., geo, 0.02))
    assert max(products)-min(products) < 1e-13
    assert 0 < products[1] < 20/189
    assert 1-products[1] > 169/189


def test_crossing_stops_at_machine_resolution_with_bounded_evaluations(monkeypatch):
    from cg_frg.gravity import chi_pole_condition as chi
    calls = []
    def product(value, alpha, geo, tau):
        calls.append(value)
        return 1+(value-0.75)
    monkeypatch.setattr(chi, 'x_chi', product)
    assert chi.find_crossing(2., {}, .02) == pytest.approx(.75, abs=2e-16)
    assert len(calls) <= 62


def test_coordinate_table_uses_one_critical_solve(monkeypatch):
    from cg_frg.gravity import chi_pole_condition as chi
    calls = []
    monkeypatch.setattr(chi, 'get', {'M_P': 1., 'M_G': math.sqrt(math.pi)/2.49,
                                    'kL': 2.49, 'tau': .02}.__getitem__)
    monkeypatch.setattr(chi, 'pset', lambda *args, **kwargs: None)
    def crossing(alpha, geo, tau):
        calls.append(alpha)
        return .65722485
    monkeypatch.setattr(chi, 'find_crossing', crossing)
    monkeypatch.setattr(chi, 'x_chi', lambda value, alpha, geo, tau: math.exp(alpha*value-1))
    monkeypatch.setattr(chi, 'v_tt', lambda *args: 1.)
    monkeypatch.setattr(chi, 'pi2_chi', lambda *args: 1.)
    monkeypatch.setattr(chi, 'crossing_derivative', lambda *args: 3.)
    result = chi.compute()
    assert calls == [2.]
    for alpha in (1., 1.5, 2., 2.5, 3.):
        assert result['coordinate_check'][str(alpha)] == round(2*.65722485/alpha, 4)


def test_exact_extension_certificates_and_production_branch_margin():
    import json
    from pathlib import Path
    from scripts.evaluate_joint_extensions import exact_affine_examples, undeformed_branch_check
    affine = exact_affine_examples()
    assert affine['passed']
    assert affine['examples']['visible_kernel']['residue'] == [['1/2']]
    assert affine['examples']['positive_mass']['kernel_dimension'] == 0
    assert affine['examples']['positive_mass']['residue'] == [['0']]
    records = json.loads((Path(__file__).resolve().parents[1]/'cg_params.json').read_text(encoding='utf-8'))['parameters']
    branch = undeformed_branch_check(records)
    assert branch['passed'] and not branch['radius_closure_selects_detuning']
    assert not branch['full_tensor_kernel_computed']
    assert branch['rational_denominator_margin_lower_bound'] == '10043/172543'
    json.dumps({'affine': affine, 'branch': branch}, allow_nan=False)


def test_resolution_speed_is_a_declared_ode_with_an_exact_solution():
    C, sigma0, t = -0.7, 1.2, 0.4
    h = 1e-5
    derivative = (resolution_width(C, sigma0, t+h)-resolution_width(C, sigma0, t-h))/(2*h)
    assert derivative == pytest.approx(beta_sigma(C, resolution_width(C, sigma0, t)), rel=1e-9)
    report = free_carrier_checks()
    assert report['free_reflection_gram_min'] >= 0
    assert report['phase_trace_error'] < 1e-14
    assert not report['interacting_reflection_positivity_established']


def test_present_tt_kernel_is_newtonian():
    r = scan_internal_trajectory(points=120)
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
