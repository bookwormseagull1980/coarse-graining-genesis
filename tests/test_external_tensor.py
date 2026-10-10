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

"""Action, gauge identities and physical residues of the external extension."""
from fractions import Fraction
from itertools import product
import numpy as np
import pytest
from cg_frg.gravity.external_tensor import (fp_operator, conserved_exchange,
    physical_polarizations, helicity_reflection_gram, exact_helicity_certificate,
    matched_ladder_branch, flrw_tensor_coefficients, flrw_background_constraints)
from cg_frg.gravity.nonlinear_tensor import (
    palatini_ward_residual, scalar_ward_residual, homogeneous_ward_coefficients,
    verify_classical_completion)


def test_gauge_identity_transversality_and_self_adjoint_operator():
    q = np.array([1., 2., 3., 4.])
    xi = np.array([3., -2., 1., 5.])
    assert np.array_equal(fp_operator(q, np.outer(q, xi)+np.outer(xi, q)), np.zeros((4, 4)))
    a = np.arange(16.).reshape(4, 4)
    a = a+a.T
    b = np.diag([2., -1., 3., 7.])
    assert np.array_equal(fp_operator(q, a)@q, np.zeros(4))
    assert np.sum(a*fp_operator(q, b)) == np.sum(b*fp_operator(q, a))


@pytest.mark.parametrize('direction', [[0., 0., 1.], [1., 2., 3.], [-1., 0., 0.]])
def test_two_helicities_and_reduced_operator(direction):
    pol = physical_polarizations(direction)
    assert np.einsum('aij,bij->ab', pol, pol) == pytest.approx(np.eye(2), abs=1e-14)
    for e in pol:
        assert e@direction == pytest.approx(np.zeros(3), abs=1e-14)
        assert np.trace(e) == pytest.approx(0., abs=1e-14)
        h = np.zeros((4, 4))
        h[1:, 1:] = e
        q = np.r_[2., direction]
        assert fp_operator(q, h) == pytest.approx((q@q)*h, abs=1e-13)


def test_exact_external_massless_residue_and_dark_vertex():
    certificate = exact_helicity_certificate(Fraction(3, 2), Fraction(2))
    assert certificate['residue'] == [['8/3', '0'], ['0', '8/3']]
    assert certificate['free_external_pole_established']
    assert certificate['visible_rank'] == 2
    assert exact_helicity_certificate(2, 0)['visible_rank'] == 0
    assert 'macroscopic collective tensor' in certificate['physical_description']
    assert certificate['certificate_order'].startswith('quadratic action')
    with pytest.raises(ValueError):
        exact_helicity_certificate(-1)
    with pytest.raises(TypeError):
        exact_helicity_certificate(1.5)


def test_static_conserved_exchange_trace_factor_and_normalization():
    t = np.diag([3., 0., 0., 0.])
    u = np.diag([5., 0., 0., 0.])
    assert conserved_exchange([0., 0., 0., 2.], t, u, kinetic=2., coupling=3.) == pytest.approx(135/16)
    assert conserved_exchange([0., 0., 0., 2.], t, u, kinetic=8., coupling=6.) == pytest.approx(135/16)
    with pytest.raises(ValueError):
        conserved_exchange([1., 0., 0., 0.], t, u, kinetic=2.)


def test_physical_reflection_positivity():
    sources = np.array([[1., 1j], [2., 0.], [0., 3j]])
    gram = helicity_reflection_gram([0., .4, .9], sources, 2., kinetic=3.)
    assert gram == pytest.approx(gram.conj().T, abs=1e-15)
    assert np.linalg.eigvalsh(gram).min() > -1e-14
    with pytest.raises(ValueError):
        helicity_reflection_gram([0.], [[1., 0.]], 0., kinetic=3.)


def test_matching_solves_same_inverse_response_with_reused_quadrature(monkeypatch):
    from cg_frg.gravity import chi_pole_condition as chi
    calls = []
    def pi(value, *args):
        calls.append(value)
        return 2.
    monkeypatch.setattr(chi, 'pi2_chi', pi)
    monkeypatch.setattr(chi, 'v_tt', lambda value, *args: (1-2*(.3-value))/2)
    result = matched_ladder_branch(.01, {}, .02, .3)
    assert result['chi'] == pytest.approx(.29, abs=1e-14)
    assert result['momentum_times_response'] == pytest.approx(1., abs=1e-12)
    assert len(calls) == result['spectral_evaluations']
    assert len(calls) == len(set(calls))
    assert matched_ladder_branch(0., {}, .02, .3)['chi'] == .3
    with pytest.raises(ValueError):
        matched_ladder_branch(.4, {}, .02, .3)
    with pytest.raises(ValueError):
        matched_ladder_branch(.01, {}, .02, .2)


def test_publication_reuses_stored_inputs_and_records_direct_dependencies(monkeypatch):
    from cg_core import params
    from cg_frg.gravity import external_tensor as tensor
    records = {'M_P': 3., 'chi_detuning_response': {'slope': 4., 'residue': .125},
               'chi_pole_crossing': .7}
    published = {}
    def publish(key, value, **metadata):
        records[key] = value
        published[key] = metadata
    monkeypatch.setattr(params, 'get', records.__getitem__)
    monkeypatch.setattr(params, 'set', publish)
    monkeypatch.setattr(tensor, 'matched_ladder_branch', lambda *a, **k: pytest.fail('production must reuse stored inputs'))
    status = tensor.compute()
    assert len(published) == 6
    assert records['external_tensor_Z'] == 9.
    assert records['external_tensor_residue'] == 1/9
    assert records['external_tensor_Pi_critical'] == .5
    assert records['external_tensor_chi_slope'] == .125
    assert status['external_massless_pole_established']
    assert status['scope'] == 'macroscopic Einstein--matter response; flat-background tensor coefficients'
    assert status['interacting_completion_established']
    assert status['completion_scope'].startswith('classical Einstein--scalar')
    assert status['tensor_background_operator'] == 'd_t^2+3*H*d_t-a^-2*Delta'
    assert status['approximation_order'].startswith('classical effective action')
    assert published['external_tensor_residue']['dependencies'] == ('external_tensor_Z',)
    for key, metadata in published.items():
        assert metadata['provenance'] == 'DERIVED'
        assert metadata['evidence_kind']
        if key != 'external_tensor_status':
            assert metadata['definition'].unit


def test_flrw_operator_returns_same_flat_action_source_and_static_exchange():
    data = flrw_tensor_coefficients(1., 0., 0., 2., kinetic=8., coupling=2.)
    assert data['phi_action_kinetic_weight'] == 8.
    assert data['phi_action_gradient_weight'] == 8.
    assert data['physical_momentum_squared'] == 4.
    assert data['canonical_frequency_squared'] == 4.
    assert data['metric_kinetic_coefficient'] == 2.
    assert data['phi_source_coefficient'] == .25
    assert data['metric_source_coefficient'] == 1.
    assert data['static_poisson_coefficient'] == .25
    assert data['newton_constant'] == pytest.approx(1/(16*np.pi))
    monopole = np.diag([1., 0., 0., 0.])
    static_fourier = conserved_exchange([0., 0., 0., 2.], monopole,
                                       monopole, kinetic=8., coupling=2.)
    assert static_fourier == pytest.approx(data['static_poisson_coefficient']/4)


@pytest.mark.parametrize('power', [Fraction(2, 3), Fraction(1, 2)])
def test_flrw_dust_and_radiation_satisfy_background_constraint_and_conservation(power):
    t, m_squared = 2., 3.
    n = float(power)
    h, dh = n/t, -n/t**2
    rho = 3*m_squared*h*h
    pressure = -2*m_squared*dh-rho
    data = flrw_background_constraints(h, dh, rho, pressure, -2*rho/t,
                                       kinetic=m_squared)
    for residual in data.values():
        assert residual == pytest.approx(0., abs=2e-15)
    tensor = flrw_tensor_coefficients(t**n, h, dh, 5., kinetic=m_squared)
    assert tensor['canonical_pump'] == pytest.approx(t**(2*n-2)*n*(2*n-1))
    assert tensor['tensor_wave_speed_squared'] == 1.


def test_de_sitter_background_and_tensor_canonical_pump():
    h, a, m_squared = 2., 3., 5.
    data = flrw_background_constraints(h, 0., 0., 0., 0., kinetic=m_squared,
                                       vacuum_density=3*m_squared*h*h)
    assert all(value == 0. for value in data.values())
    tensor = flrw_tensor_coefficients(a, h, 0., 0., kinetic=m_squared)
    assert tensor['canonical_pump'] == 2*a*a*h*h
    assert tensor['cosmic_friction'] == 3*h
    assert tensor['physical_momentum_squared'] == 0.


def test_constraint_propagation_identity_also_holds_off_shell_at_a_turning_point():
    for h in [0., 2.]:
        data = flrw_background_constraints(h, -3., 7., 11., 13.,
                                           kinetic=5., coupling=2., vacuum_density=17.)
        assert data['constraint_propagation_identity_residual'] == 0.
        assert data['hamiltonian_constraint'] != 0.
    with pytest.raises(ValueError):
        flrw_tensor_coefficients(0., 1., 0., 2., kinetic=3.)
    with pytest.raises(ValueError):
        flrw_tensor_coefficients(1., 1., 0., -2., kinetic=3.)
    with pytest.raises(ValueError):
        flrw_background_constraints(1., 0., 0., 0., 0., kinetic=3., coupling=0.)


def _jets(seed):
    n = 4
    def entry(indices, denominator):
        return Fraction((sum((k+seed+1)*(i+1)**2 for k, i in enumerate(indices))
                         +seed*3) % 17-8, denominator)
    def tensor(rank, canonical, denominator):
        out = np.empty((n,)*rank, dtype=object)
        for index in np.ndindex(out.shape):
            out[index] = entry(canonical(index), denominator)
        return out
    h = tensor(2, lambda t: tuple(sorted(t)), 13)
    dh = tensor(3, lambda t: t[:1]+tuple(sorted(t[1:])), 17)
    a = tensor(3, lambda t: t[:1]+tuple(sorted(t[1:])), 19)
    da = tensor(4, lambda t: t[:2]+tuple(sorted(t[2:])), 23)
    dda = tensor(5, lambda t: tuple(sorted(t[:2]))+t[2:3]+tuple(sorted(t[3:])), 29)
    xi = tensor(1, lambda t: t, 7)
    dx = tensor(2, lambda t: t, 11)
    ddx = tensor(3, lambda t: tuple(sorted(t[:2]))+t[2:], 31)
    dddx = tensor(4, lambda t: tuple(sorted(t[:3]))+t[3:], 37)
    return h, dh, a, da, dda, xi, dx, ddx, dddx


@pytest.mark.parametrize("seed", [1, 3])
def test_complete_palatini_density_has_exact_off_shell_ward_identity(seed):
    h, *jets = _jets(seed)
    eta = np.diag([1, -1, -1, -1]).astype(object)
    result = palatini_ward_residual(eta+h, *jets)
    assert result["gauge_variation"] != 0
    assert result["total_divergence"] != 0
    assert result["ward_residual"] == 0


def test_cubic_vertex_cancels_nonlinear_variation_of_quadratic_action():
    data = _jets(2)
    full = homogeneous_ward_coefficients(*data)
    without_cubic = homogeneous_ward_coefficients(*data, cubic_weight=0)
    assert full == [Fraction(0)]*5
    assert without_cubic[:3] == [Fraction(0)]*3
    assert without_cubic[3] != 0
    assert without_cubic[4] == 0


def test_scalar_matter_uses_same_density_and_satisfies_off_shell_identity():
    h, dh, _, _, _, xi, dx, _, _ = _jets(4)
    q = np.diag([1, -1, -1, -1]).astype(object)+h
    gradient = np.array([Fraction(2, 3), Fraction(-1, 7), Fraction(5, 11), Fraction(3, 2)])
    hessian = np.array([[Fraction((i+1)*(j+1), 13) for j in range(4)] for i in range(4)])
    result = scalar_ward_residual(q, dh, gradient, hessian, xi, dx)
    assert result["ward_residual"] == 0
    assert result["gauge_variation"] != 0
    # The scalar jet is off shell: the local identity requires no wave equation.
    assert sum(q[i, j]*hessian[i, j] for i, j in product(range(4), repeat=2)) != 0


def test_exact_jet_and_torsion_requirements_are_enforced():
    data = list(_jets(5))
    floating = [v.copy() for v in data]
    floating[0][0, 0] = .5
    with pytest.raises(TypeError):
        palatini_ward_residual(*floating)
    data[2][0, 1, 2] += Fraction(1)
    with pytest.raises(ValueError):
        palatini_ward_residual(*data)


def test_verification_record_distinguishes_classical_identity_and_instances():
    result = verify_classical_completion()
    assert result['passed']
    assert result['gravitational_ward_coefficients'] == ['0']*5
    assert Fraction(result['cubic_omission_residual']) != 0
    assert result['scalar_ward_residual'] == '0'
    assert result['jet_evaluations'] == 11
