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

"""Actual matter-source derivatives; independent finite-family and support checks."""
import math
import numpy as np
import pytest
from scipy.linalg import block_diag, expm, solve_sylvester

from cg_frg.gravity.matter_source_response import (
    covariant_scalar_operator, compression_matrices, energy_response,
    finite_sourced_energy, scalar_basis, evaluate_matter_source_response, _example,
    canonical_source_matrices, canonical_source_response,
    canonical_source_evolution, covariant_source_jet, canonical_source_adm,
    polar_source_congruence, _polar_congruence_verification,
    uniform_source_dilation)


@pytest.fixture(scope="module")
def native_matter_response():
    """One aggregate calculation, shared by its read-only assertions."""
    from unittest.mock import patch
    with patch('cg_frg.gravity.matter_source_response.finite_sourced_energy',
               wraps=finite_sourced_energy) as energy:
        result = evaluate_matter_source_response()
    assert energy.call_count == result['finite_source_operation_counts']['finite_energy_evaluations']
    return result


def test_connection_gram_retains_complete_product_support():
    # A nonconstant connection sends the constant input beyond max_j=0.
    # The exact B*B contribution is nevertheless present in its Gram form.
    B = ({(1, 0, 0): np.array([[.3j]])}, {}, {})
    data = covariant_scalar_operator(max_j=0, L=2., connection=B, carrier_dimension=1)
    assert (1, 0, 0) in data['derivative_output_labels']
    assert data['operator'][0, 0].real == pytest.approx(3/16+.09, rel=1e-13)
    with pytest.raises(ValueError, match='skew'):
        covariant_scalar_operator(max_j=0, L=2., connection=({(0, 0, 0): np.eye(1)}, {}, {}), carrier_dimension=1)


def test_free_native_operator_has_actual_laplacian_and_curvature():
    data = covariant_scalar_operator(max_j=2, L=1.7, connection=({}, {}, {}), carrier_dimension=1)
    expected = [(4*j*(j+1)+.75)/1.7**2 for j, _, _ in data['labels']]
    np.testing.assert_allclose(data['operator'], np.diag(expected), atol=2e-14)


def test_complete_second_source_derivative_is_needed():
    A = np.diag([1., 4.])
    N = np.diag([1., .5])
    profiles = [np.eye(2), np.array([[0., 1.], [1., 0.]])]
    response = energy_response(A, N, profiles)
    assert response['charges'][0] == pytest.approx(response['energy'])
    assert response['hessian'][0, 0] == pytest.approx(response['energy'])
    assert response['square_root_feedback'][0, 0] < 0
    assert response['second_source_direct_term'][0, 0] == pytest.approx(2*response['energy'])
    # Independent closed coefficient for the mixed-energy off-diagonal probe.
    expected = 2*2*(1+4)/(1+2)**2 + .5*2*1*(4+1)/(2+1)**2
    assert response['hessian'][1, 1] == pytest.approx(expected)


def test_nonstationary_occupation_uses_full_frechet_derivative():
    A = np.diag([1., 9.])
    N = np.array([[1., .3], [.3, 1.]])
    profile = np.array([[0., 1.], [1., 0.]])
    with pytest.raises(ValueError, match='stationary'):
        energy_response(A, N, [profile])
    response = energy_response(A, N, [profile], require_stationary=False)
    step = 1e-5
    actual = (finite_sourced_energy(A, N, [profile], [step])-
              finite_sourced_energy(A, N, [profile], [-step]))/(2*step)
    assert actual == pytest.approx(response['charges'][0], rel=2e-9)
    assert not response['stationary_energy_density_interpretation']
    naive = np.trace(N@np.diag([1., 1/3])@(profile@A+A@profile)/2).real
    assert abs(naive-response['charges'][0]) > .1


def test_global_frame_source_basis_and_energy_unit_covariance():
    carrier, profiles, occupations, _ = _example(max_j=1)
    A, N = carrier['operator'], sum(occupations)
    reference = energy_response(A, N, profiles)
    U, _ = np.linalg.qr(np.array([[1., 2j], [.7j, 1.]]))
    V = np.kron(np.eye(len(carrier['labels'])), U)
    other = energy_response(V.conj().T@A@V, V.conj().T@N@V,
                            [V.conj().T@p@V for p in profiles])
    np.testing.assert_allclose(other['hessian'], reference['hessian'], atol=3e-14)
    J = np.array([[1., .2, 0.], [0., .8, -.3], [.1, 0., 1.]])
    changed = energy_response(A, N, [sum(profiles[a]*J[a, b] for a in range(3)) for b in range(3)])
    np.testing.assert_allclose(changed['hessian'], J.T@reference['hessian']@J, atol=3e-14)
    units, unit_profiles, unit_N, _ = _example(max_j=1, L=1.3/1000)
    scaled = energy_response(units['operator'], sum(unit_N), unit_profiles)
    np.testing.assert_allclose(scaled['hessian']/1000, reference['hessian'], rtol=2e-13, atol=2e-14)


def test_native_example_has_actual_source_and_cutoff_certificates(native_matter_response):
    import json
    result = native_matter_response
    json.dumps(result, allow_nan=False)
    assert result['passed'], result['checks']
    assert result['checks_passed']
    assert result['nonzero_connection_curvature_norm'] > 0
    assert abs(result['cross_source_hessian'][0][1]) > .1
    assert result['minimum_hessian_eigenvalue'] > 0
    assert not result['external_gravitational_kernel_computed']
    assert not result['all_particle_carriers_included']
    work = result['finite_source_operation_counts']
    assert work['finite_energy_requests'] == 30
    assert work['finite_energy_evaluations'] == 18
    assert work['reused_finite_energy_values'] == 12
    assert work['reused_central_energy'] == 1
    support = result['source_support']
    assert support['first_product_omitted_norm'] == 0
    assert support['second_product_outside_retained_space_norm'] > .1
    assert support['low_state_second_derivatives_have_complete_intermediate_support']
    assert not support['finite_nonzero_source_is_full_continuum_compression']
    dynamics = result['canonical_matter_dynamics']
    assert dynamics['passed'], dynamics['checks']
    assert dynamics['contact_relative_cutoff_residual'] < 2e-12
    assert dynamics['response_relative_cutoff_residual'] < 2e-12
    assert dynamics['final_degenerate_position_coherence_norm'] > 1e-8
    assert dynamics['final_covariance_minimum_eigenvalue'] >= -2e-12*dynamics['final_covariance_scale']
    np.testing.assert_allclose(np.diff(dynamics['segment_energies']),
                               dynamics['source_work'], atol=2e-12)
    def decoded(name):
        record = dynamics[name]
        return np.asarray(record['real'])+1j*np.asarray(record['imaginary'])
    np.testing.assert_allclose(
        decoded('canonical_force_response'),
        np.asarray(dynamics['canonical_force_contact'])+
        decoded('difference_frequency_response')+decoded('summed_frequency_response'),
        atol=2e-12)
    assert not dynamics['finite_source_continuum_limit_certified']
    assert not dynamics['external_gravitational_kernel_computed']
    clock = dynamics['clock_reparametrization']
    assert clock['relative_phase_covariance_residual'] < 2e-12
    assert clock['maximum_source_work_residual'] < 2e-12
    assert clock['additional_source_family_evaluations'] == 0
    assert clock['reused_source_families'] == 3
    assert clock['additional_exact_segment_propagators'] == 3


def test_real_profile_and_positive_operator_requirements():
    with pytest.raises(ValueError, match='real'):
        compression_matrices([{(0, 0, 0): 1j}], scalar_basis(0), 1)
    with pytest.raises(ValueError, match='strictly positive'):
        energy_response(np.diag([0., 1.]), np.eye(2), [np.eye(2)])
    with pytest.raises(ValueError, match='nonnegative'):
        energy_response(np.eye(2), np.diag([-1., 1.]), [np.eye(2)])


def test_canonical_oscillator_response_has_contact_and_pair_frequencies():
    omega, occupation, profile = 1.6, .7, .8
    parameters = np.array([.3+.2j, 3.1+.4j, 1e-5j, 1e5j])
    result = canonical_source_response(
        np.array([[omega**2]]), np.array([[occupation]]),
        [np.array([[profile]])], spectral_parameters=parameters)
    # The covariance equations close on q^2, qp and p^2. Their forced
    # oscillator frequency is 2 omega, with the seagull term fixed by M and B.
    contact = 5*occupation*omega*profile**2
    transition = 16*occupation*profile**2*omega**3/(parameters**2-4*omega**2)
    np.testing.assert_allclose(result['charges'], [occupation*omega*profile], rtol=2e-14)
    np.testing.assert_allclose(result['contact'], [[contact]], rtol=2e-14)
    np.testing.assert_allclose(result['response'][:, 0, 0], contact+transition, rtol=2e-13)
    np.testing.assert_allclose(result['difference_frequency_response'], 0., atol=2e-13)
    np.testing.assert_allclose(result['summed_frequency_response'][:, 0, 0], transition, atol=2e-13)
    assert result['response'][2, 0, 0].real == pytest.approx(
        occupation*omega*profile**2, rel=2e-10)


def test_degenerate_coherent_occupation_retains_full_liouville_response():
    A = np.eye(2)
    N = np.array([[.8, .2j], [-.2j, .3]])
    profiles = [np.array([[1., -1j], [1j, 1.]]), np.diag([1., -1.])]
    parameters = np.array([.3+.2j, 1.7+.4j])
    result = canonical_source_response(A, N, profiles, spectral_parameters=parameters,
                                       include_phase_covariances=True)
    W = block_diag(N, N)
    J = np.block([[np.zeros((2, 2)), np.eye(2)], [-np.eye(2), np.zeros((2, 2))]])
    # A=I makes the stationary Hamiltonian degenerate, while N is coherent
    # and unequal within that block. Solve its covariance equation directly.
    vertices = [block_diag(-p, 3*p) for p in profiles]
    expected = np.empty((len(parameters), 2, 2), complex)
    for iz, z in enumerate(parameters):
        for b, vertex in enumerate(vertices):
            perturbation = J@vertex
            forcing = perturbation@W+W@perturbation.conj().T
            covariance = solve_sylvester(-.5j*z*np.eye(4)-J,
                                        -.5j*z*np.eye(4)-J.conj().T, forcing)
            np.testing.assert_allclose(result['response_phase_covariances'][iz, b],
                                       covariance, rtol=2e-13, atol=2e-13)
            for a, left in enumerate(vertices):
                contact = 2.5*np.trace(N@(profiles[a]@profiles[b]+profiles[b]@profiles[a]))
                expected[iz, a, b] = contact+.5*np.trace(left@covariance)
    np.testing.assert_allclose(result['response'], expected, rtol=2e-13, atol=2e-13)
    # Removing the imaginary coherence would give 11 for this contact.
    assert result['contact'][0, 0] == pytest.approx(7., abs=2e-13)


def test_canonical_response_is_covariant_under_complex_basis_rotation():
    A = np.diag([1., 1., 4.])
    N = np.array([[.8, .2j, 0.], [-.2j, .3, 0.], [0., 0., .1]])
    profiles = [np.array([[1., .2j, .3], [-.2j, -.5, .1j], [.3, -.1j, .7]]),
                np.array([[.2, .4, -.3j], [.4, .1, .2], [.3j, .2, -.6]])]
    parameters = np.array([.4+.3j, 2.5+.2j])
    reference = canonical_source_response(A, N, profiles, spectral_parameters=parameters)
    U, _ = np.linalg.qr(np.array([[1., .2j, .4], [.3j, 1., -.2], [.4, .1j, 1.]]))
    transformed = canonical_source_response(
        U.conj().T@A@U, U.conj().T@N@U,
        [U.conj().T@p@U for p in profiles], spectral_parameters=parameters)
    for name in ('charges', 'contact', 'response', 'difference_frequency_response',
                 'summed_frequency_response'):
        np.testing.assert_allclose(transformed[name], reference[name], atol=3e-12, rtol=3e-12)


def test_canonical_constant_source_matches_exact_oscillator_phase_flow():
    omega, occupation, eta, duration = 1.6, .7, .35, .43
    result = canonical_source_evolution(
        np.array([[omega**2]]), np.array([[occupation]]), [np.eye(1)],
        np.array([[eta]]), np.array([duration]))
    frequency = omega*math.exp(eta)
    cosine, sine = math.cos(frequency*duration), math.sin(frequency*duration)
    flow = np.array([[cosine, math.exp(3*eta)*sine/frequency],
                     [-omega**2*math.exp(-eta)*sine/frequency, cosine]])
    initial = np.diag([occupation/omega, occupation*omega])
    final = flow@initial@flow.T
    final_energy = occupation*omega*(math.exp(-eta)+math.exp(3*eta))/2
    np.testing.assert_allclose(result['initial_covariance'], initial, atol=2e-14)
    np.testing.assert_allclose(result['phase_propagators'][0], flow, atol=2e-14)
    np.testing.assert_allclose(result['phase_covariances'][1], final, atol=3e-14)
    np.testing.assert_allclose(result['energies'], [occupation*omega, final_energy], atol=3e-14)
    np.testing.assert_allclose(result['source_work'], [final_energy-occupation*omega], atol=3e-14)
    np.testing.assert_allclose(result['energy_balance_residual'], 0., atol=3e-14)
    assert abs(final[0, 1]) > .1
    assert np.linalg.eigvalsh(final).min() > 0


def test_canonical_source_work_uses_both_metric_and_stiffness_variations():
    A = np.array([[2.1, .2j], [-.2j, 4.3]])
    N = .7*np.eye(2)+.1*A
    profiles = [np.array([[0., 1.], [1., 0.]]), np.diag([1., -.4])]
    source_values = np.array([[.12, -.08], [-.05, .1], [0., 0.]])
    result = canonical_source_evolution(A, N, profiles, source_values, [.13, .21, .17])
    previous = block_diag(A, np.eye(2))
    J = np.block([[np.zeros((2, 2)), np.eye(2)], [-np.eye(2), np.zeros((2, 2))]])
    for i, source in enumerate(source_values):
        eta = sum(value*profile for value, profile in zip(source, profiles))
        conformal = expm(-eta/2)
        current = block_diag(conformal@A@conformal, expm(3*eta))
        before, after = result['phase_covariances'][i:i+2]
        work = .5*np.trace((current-previous)@before).real
        assert result['source_work'][i] == pytest.approx(work, abs=2e-13)
        assert .5*np.trace(current@(after-before)).real == pytest.approx(0., abs=2e-13)
        flow = result['phase_propagators'][i]
        np.testing.assert_allclose(flow.conj().T@J@flow, J, atol=5e-14)
        assert np.linalg.eigvalsh(after).min() > 0
        previous = current
    np.testing.assert_allclose(result['energy_balance_residual'], 0., atol=3e-13)
    response = canonical_source_response(A, N, profiles, spectral_parameters=[.7+.2j])
    step = 1e-6
    for a in range(2):
        direction = np.eye(2)[a]*step
        plus = canonical_source_matrices(A, profiles, direction)
        minus = canonical_source_matrices(A, profiles, -direction)
        derivative = .5*np.trace((plus['phase_hessian']-minus['phase_hessian'])@
                                 result['initial_covariance']).real/(2*step)
        assert derivative == pytest.approx(response['charges'][a], rel=2e-8, abs=2e-9)
    fixed_state = energy_response(A, N, profiles)
    np.testing.assert_allclose(response['charges'], fixed_state['charges'], atol=2e-13)


def test_canonical_dynamics_rejects_invalid_states_and_response_frequencies():
    A = np.diag([1., 4.])
    N = np.array([[1., .2], [.2, 1.]])
    with pytest.raises(ValueError, match='stationary'):
        canonical_source_response(A, N, [np.eye(2)], spectral_parameters=[1.+.2j])
    with pytest.raises(ValueError):
        canonical_source_response(A, np.eye(2), [np.eye(2)], spectral_parameters=[1.-.2j])
    with pytest.raises(ValueError):
        canonical_source_evolution(A, np.eye(2), [np.eye(2)], [[.1]], [-.2])


def test_covariant_source_ward_identity_matches_homogeneous_energy_exchange():
    # A homogeneous scalar in an expanding metric has an independently
    # known friction term and continuity equation, including source work.
    omega, eta, eta_rate = 1.6, .13, .23
    amplitude, velocity, acceleration = .4, .7, -.2
    scale, expansion = 1.4, .19
    mass, stiffness = math.exp(-3*eta), omega**2*math.exp(-eta)
    metric = np.diag([-1., scale**2, scale**2, scale**2])
    metric_gradient = np.zeros((4, 4, 4))
    metric_gradient[0, 1:, 1:] = 2*expansion*scale**2*np.eye(3)
    gradient, hessian = np.zeros((4, 1)), np.zeros((4, 4, 1))
    gradient[0, 0], hessian[0, 0, 0] = velocity, acceleration
    source_gradient = np.zeros((4, 1))
    source_gradient[0, 0] = eta_rate
    result = covariant_source_jet(
        np.array([[omega**2]]), [np.eye(1)], [eta], metric=metric,
        metric_gradient=metric_gradient, field=[amplitude],
        field_gradient=gradient, field_hessian=hessian,
        source_gradient=source_gradient)
    density = (mass*velocity**2+stiffness*amplitude**2)/2
    pressure = (mass*velocity**2-stiffness*amplitude**2)/2
    scalar_equation = (-mass*acceleration-
                       (3*expansion-3*eta_rate)*mass*velocity-
                       stiffness*amplitude)
    source_equation = (-3*mass*velocity**2+stiffness*amplitude**2)/2
    density_rate = (mass*velocity*acceleration-1.5*eta_rate*mass*velocity**2+
                    stiffness*amplitude*velocity-
                    .5*eta_rate*stiffness*amplitude**2)
    expected_divergence = -(density_rate+3*expansion*(density+pressure))
    np.testing.assert_allclose(result['stress_tensor'],
                               np.diag([density]+[scale**2*pressure]*3), atol=2e-14)
    np.testing.assert_allclose(result['field_equation'], [scalar_equation], atol=2e-14)
    np.testing.assert_allclose(result['source_equations'], [source_equation], atol=2e-14)
    np.testing.assert_allclose(result['stress_divergence'],
                               [expected_divergence, 0., 0., 0.], atol=2e-14)
    np.testing.assert_allclose(result['ward_matter_term'],
                               [scalar_equation*velocity, 0., 0., 0.], atol=2e-14)
    np.testing.assert_allclose(result['ward_source_term'],
                               [source_equation*eta_rate, 0., 0., 0.], atol=2e-14)
    np.testing.assert_allclose(result['ward_residual'], 0., atol=3e-14)


def test_covariant_source_noncommuting_variations_and_complex_frame_covariance():
    A = np.array([[2.1, .3j], [-.3j, 3.2]])
    profiles = [np.array([[0., 1.], [1., 0.]]), np.diag([1., -.4])]
    source = np.array([.13, -.2])
    field = np.array([.4+.1j, -.3j])
    gradient = np.array([[.7, .2j], [.3j, -.2], [.1, .4j], [-.3, .2]])
    hessian = np.zeros((4, 4, 2), complex)
    hessian[0, 0] = [.2, -.1j]
    hessian[1, 1] = [.3j, .4]
    hessian[0, 1] = hessian[1, 0] = [-.2, .1j]
    source_gradient = np.array([[.2, -.1], [.3, .2], [-.1, .4], [.1, -.2]])
    metric = np.diag([-1., 1., 1., 1.])
    common = dict(metric=metric, metric_gradient=np.zeros((4, 4, 4)),
                  field=field, field_gradient=gradient, field_hessian=hessian,
                  source_gradient=source_gradient)
    reference = covariant_source_jet(A, profiles, source, **common)
    # Direct finite variations of the scalar Lagrangian check both matrix
    # Frechet derivatives away from zero source, where profiles do not commute.
    def lagrangian(values):
        eta = sum(value*profile for value, profile in zip(values, profiles))
        mass, factor = expm(-3*eta), expm(-eta/2)
        stiffness = factor@A@factor
        contraction = sum(metric[i, i]*np.vdot(gradient[i], mass@gradient[i])
                          for i in range(4))
        return -.5*(contraction+np.vdot(field, stiffness@field)).real
    step = 2e-6
    for a in range(2):
        direction = np.eye(2)[a]*step
        derivative = (lagrangian(source+direction)-lagrangian(source-direction))/(2*step)
        assert reference['source_equations'][a] == pytest.approx(derivative, rel=2e-9, abs=2e-10)
    U, _ = np.linalg.qr(np.array([[1., .3j], [.4j, 1.]]))
    rotated = dict(common, field=U.conj().T@field,
                   field_gradient=gradient@U.conj(), field_hessian=hessian@U.conj())
    transformed = covariant_source_jet(
        U.conj().T@A@U, [U.conj().T@p@U for p in profiles], source, **rotated)
    for name in ('stress_tensor', 'source_equations', 'stress_divergence',
                 'ward_matter_term', 'ward_source_term', 'ward_residual'):
        np.testing.assert_allclose(transformed[name], reference[name], atol=2e-13)
    np.testing.assert_allclose(transformed['field_equation'],
                               U.conj().T@reference['field_equation'], atol=2e-13)
    np.testing.assert_allclose(reference['ward_residual'], 0., atol=2e-13)


def test_covariant_adm_lapse_shift_constraints_and_source_force():
    A = np.array([[2.1, .3j], [-.3j, 3.2]])
    profiles = [np.array([[0., 1.], [1., 0.]]), np.diag([1., -.4])]
    source = np.array([.13, -.2])
    spatial_metric = np.array([[1.4, .2, 0.], [.2, 1.1, .1], [0., .1, .9]])
    lapse, shift = 1.2, np.array([.1, -.2, .15])
    field, momentum = np.array([.4+.1j, -.3j]), np.array([.7, .2j])
    gradient = np.array([[.3j, -.2], [.1, .4j], [-.3, .2]])
    common = dict(spatial_metric=spatial_metric, lapse=lapse, shift=shift,
                  field=field, field_gradient=gradient, momentum=momentum)
    result = canonical_source_adm(A, profiles, source, **common)
    volume = math.sqrt(np.linalg.det(spatial_metric))
    eta = sum(value*profile for value, profile in zip(source, profiles))
    mass, inverse_mass, factor = expm(-3*eta), expm(3*eta), expm(-eta/2)
    stiffness, inverse_metric = factor@A@factor, np.linalg.inv(spatial_metric)
    spatial_energy = sum(inverse_metric[i, j]*np.vdot(gradient[i], mass@gradient[j])
                         for i in range(3) for j in range(3)).real
    expected_normal = (np.vdot(momentum, inverse_mass@momentum).real/volume+
                       volume*(spatial_energy+np.vdot(field, stiffness@field).real))/2
    expected_momentum = np.real(gradient@momentum.conj())
    expected_velocity = lapse*inverse_mass@momentum/volume+shift@gradient
    expected_hamiltonian = lapse*expected_normal+shift@expected_momentum
    assert result['normal_energy'] == pytest.approx(expected_normal/volume, rel=2e-14)
    assert result['normal_hamiltonian_density'] == pytest.approx(expected_normal, rel=2e-14)
    assert result['normal_energy'] > 0
    np.testing.assert_allclose(result['momentum_density'], expected_momentum, atol=2e-14)
    np.testing.assert_allclose(result['field_velocity'], expected_velocity, atol=2e-14)
    assert result['hamiltonian_density'] == pytest.approx(expected_hamiltonian, rel=2e-14)
    assert result['legendre_residual'] == pytest.approx(0., abs=3e-14)
    assert (np.vdot(momentum, expected_velocity).real-result['lagrangian_density']) == pytest.approx(
        expected_hamiltonian, rel=2e-14)
    step = 2e-6
    plus = canonical_source_adm(A, profiles, source, **dict(common, lapse=lapse+step))
    minus = canonical_source_adm(A, profiles, source, **dict(common, lapse=lapse-step))
    assert (plus['hamiltonian_density']-minus['hamiltonian_density'])/(2*step) == pytest.approx(
        expected_normal, rel=2e-9)
    for i in range(3):
        direction = np.eye(3)[i]*step
        plus = canonical_source_adm(A, profiles, source, **dict(common, shift=shift+direction))
        minus = canonical_source_adm(A, profiles, source, **dict(common, shift=shift-direction))
        assert (plus['hamiltonian_density']-minus['hamiltonian_density'])/(2*step) == pytest.approx(
            expected_momentum[i], rel=2e-8, abs=2e-10)
    for a in range(2):
        direction = np.eye(2)[a]*step
        plus = canonical_source_adm(A, profiles, source+direction, **common)
        minus = canonical_source_adm(A, profiles, source-direction, **common)
        derivative = (plus['hamiltonian_density']-minus['hamiltonian_density'])/(2*step)
        assert derivative == pytest.approx(-lapse*volume*result['source_equations'][a],
                                           rel=2e-8, abs=2e-10)


def test_uniform_dilation_preserves_canonical_form_and_actual_time_generator():
    A = np.array([[2.1, .3j], [-.3j, 3.2]])
    field, momentum = np.array([.4+.1j, -.3j]), np.array([.7, .2j])
    eta, rate = .23, -.17
    result = uniform_source_dilation(A, field, momentum, source=eta, source_velocity=rate)
    lapse = math.exp(eta)
    psi, canonical_momentum = field/lapse, lapse*momentum
    np.testing.assert_allclose(result['transformed_field'], psi, atol=2e-14)
    np.testing.assert_allclose(result['transformed_momentum'], canonical_momentum, atol=2e-14)
    native_energy = (math.exp(3*eta)*np.vdot(momentum, momentum).real+
                     math.exp(-eta)*np.vdot(field, A@field).real)/2
    dilation = np.vdot(canonical_momentum, psi).real
    assert result['native_energy'] == pytest.approx(native_energy, rel=2e-14)
    assert result['lapse_energy'] == pytest.approx(native_energy, rel=2e-14)
    assert result['dilation_generator'] == pytest.approx(dilation, abs=2e-14)
    assert result['moving_hamiltonian'] == pytest.approx(native_energy-rate*dilation, rel=2e-14)
    # The transformed Hamiltonian must generate the time derivative of the
    # actual native phase solution, including its moving normalization.
    expected_velocity = math.exp(2*eta)*momentum-rate*psi
    expected_momentum_rate = -A@field+rate*canonical_momentum
    step = 2e-6
    for index in range(2):
        for unit in (1., 1j):
            direction = np.eye(2, dtype=complex)[index]*unit*step
            plus = uniform_source_dilation(A, field, momentum+direction/lapse,
                                           source=eta, source_velocity=rate)
            minus = uniform_source_dilation(A, field, momentum-direction/lapse,
                                            source=eta, source_velocity=rate)
            derivative = (plus['moving_hamiltonian']-minus['moving_hamiltonian'])/(2*step)
            assert derivative == pytest.approx((unit.conjugate()*expected_velocity[index]).real,
                                               rel=2e-8, abs=2e-10)
            plus = uniform_source_dilation(A, field+lapse*direction, momentum,
                                           source=eta, source_velocity=rate)
            minus = uniform_source_dilation(A, field-lapse*direction, momentum,
                                            source=eta, source_velocity=rate)
            derivative = (plus['moving_hamiltonian']-minus['moving_hamiltonian'])/(2*step)
            assert -derivative == pytest.approx((unit.conjugate()*expected_momentum_rate[index]).real,
                                                rel=2e-8, abs=2e-10)


def test_uniform_dilation_kinetic_form_has_exact_source_constraint():
    result = uniform_source_dilation(
        np.diag([1., 4.]), [.4+.1j, -.3j], [.7, .2j],
        source=.23, source_velocity=-.17)
    psi = result['transformed_field']
    real_field = np.concatenate((psi.real, psi.imag))
    hessian = result['velocity_hessian_real']
    null_direction = np.concatenate((-real_field, [1.]))
    np.testing.assert_allclose(hessian@null_direction, 0., atol=2e-14)
    np.testing.assert_allclose(result['null_vector_real'], null_direction, atol=2e-14)
    eigenvalues = np.linalg.eigvalsh(hessian)
    assert abs(eigenvalues[0]) < 2e-14
    assert eigenvalues[1] > .5
    # Directly evaluate the kinetic energy for a velocity that mixes both
    # components with the source; no separately positive source inertia appears.
    velocity = np.array([.2, -.3, .1, .4, -.15])
    expected = math.exp(-.23)*np.dot(velocity[:-1]+velocity[-1]*real_field,
                                   velocity[:-1]+velocity[-1]*real_field)
    assert velocity@hessian@velocity == pytest.approx(expected, rel=2e-14)


def test_native_polar_phase_reproduces_two_real_fields_and_source_force():
    # A static exponential amplitude and constant timelike phase solve the
    # complex wave equation with nonzero, constant quantum pressure.
    r, mass, wave_number, phase = .8, 1.7, .3, .41
    frequency = math.sqrt(mass**2-wave_number**2)
    dr, ddr = np.zeros(4), np.zeros((4, 4))
    dr[1], ddr[1, 1] = wave_number*r, wave_number**2*r
    dt = np.array([frequency, 0., 0., 0.])
    metric = np.diag([-1., 1., 1., 1.])
    result = polar_source_congruence(
        reference_mass_squared=mass**2, source=0., source_gradient=np.zeros(4),
        metric=metric, metric_gradient=np.zeros((4, 4, 4)), amplitude=r,
        amplitude_gradient=dr, amplitude_hessian=ddr, phase_gradient=dt,
        phase_hessian=np.zeros((4, 4)), quantum_pressure_gradient=np.zeros(4))
    unit = np.array([math.cos(phase), math.sin(phase)])
    tangent = np.array([-math.sin(phase), math.cos(phase)])
    field = r*unit
    first = np.outer(dr, unit)+r*np.outer(dt, tangent)
    second = ((ddr-r*np.outer(dt, dt))[:, :, None]*unit+
              (np.outer(dr, dt)+np.outer(dt, dr))[:, :, None]*tangent)
    direct = covariant_source_jet(
        mass**2*np.eye(2), [np.eye(2)], [0.], metric=metric,
        metric_gradient=np.zeros((4, 4, 4)), field=field,
        field_gradient=first, field_hessian=second, source_gradient=np.zeros((4, 1)))
    assert result['quantum_pressure'] == pytest.approx(wave_number**2, rel=2e-14)
    assert result['density'] == pytest.approx(r**2*frequency**2, rel=2e-14)
    np.testing.assert_allclose(result['stress_tensor'], direct['stress_tensor'], atol=2e-14)
    assert result['source_equation'] == pytest.approx(direct['source_equations'][0], rel=2e-14)
    np.testing.assert_allclose(direct['field_equation'], 0., atol=2e-14)
    np.testing.assert_allclose(result['stress_decomposition_residual'], 0., atol=2e-14)
    assert result['source_decomposition_residual'] == pytest.approx(0., abs=2e-14)
    assert result['number_current_divergence'] == pytest.approx(0., abs=2e-14)


def test_polar_static_and_cosmological_congruences_and_pressure_gradient():
    verified = _polar_congruence_verification(1.7**2)
    assert verified['passed']
    assert verified['operation_counts']['time_evolution_steps'] == 0
    cases = verified['cases']
    np.testing.assert_allclose(cases['static_rest_phase']['acceleration_covariant'],
                               [0., 1/8, 0., 0.], atol=2e-14)
    np.testing.assert_allclose(cases['homogeneous_expansion']['acceleration_covariant'],
                               0., atol=2e-14)
    pressure = cases['varying_quantum_pressure']
    assert pressure['relative_quantum_pressure'] == pytest.approx(.1, rel=2e-14)
    assert abs(pressure['acceleration_covariant'][1]) > .01
    assert max(pressure['residuals'].values()) < 2e-13
    # Keeping the same radial equation but dropping its pressure gradient
    # must be detected, rather than reporting the mass-gradient shortcut.
    inputs = dict(pressure['inputs'], quantum_pressure_gradient=np.zeros(4))
    wrong_gradient = polar_source_congruence(**inputs)
    assert abs(wrong_gradient['radial_equation_residual']) < 2e-14
    assert np.linalg.norm(wrong_gradient['radial_gradient_residual']) > .01
    assert np.linalg.norm(wrong_gradient['pressure_acceleration_residual']) > .01


def test_polar_aggregate_uses_existing_degenerate_real_carrier_pair(native_matter_response):
    result = native_matter_response
    polar = result['native_covariant_interface']['polar_source_congruence']
    pair = polar['retained_real_pair']
    carrier, _, _, _ = _example()
    frame = np.eye(len(carrier['operator']))[:, pair['basis_indices']]
    np.testing.assert_allclose(carrier['operator']@frame,
                               pair['reference_mass_squared']*frame, atol=2e-14)
    np.testing.assert_allclose(frame.T@frame, np.eye(2), atol=2e-14)
    assert pair['verified_real_multiplicity_at_least'] == 2
    assert pair['additional_carrier_copies'] == 0
    assert polar['checks']['existing_degenerate_real_pair_is_invariant']


def test_polar_source_rejects_zero_amplitude_and_nontimelike_phase():
    arguments = dict(reference_mass_squared=1., source=0., source_gradient=np.zeros(4),
                     metric=np.diag([-1., 1., 1., 1.]), metric_gradient=np.zeros((4, 4, 4)),
                     amplitude=1., amplitude_gradient=np.zeros(4), amplitude_hessian=np.zeros((4, 4)),
                     phase_gradient=np.array([1., 0., 0., 0.]), phase_hessian=np.zeros((4, 4)),
                     quantum_pressure_gradient=np.zeros(4))
    with pytest.raises(ValueError, match='positive amplitude'):
        polar_source_congruence(**dict(arguments, amplitude=0.))
    with pytest.raises(ValueError, match='timelike'):
        polar_source_congruence(**dict(arguments, phase_gradient=np.array([0., 1., 0., 0.])))


def test_nonconstant_positive_clock_reparametrization_against_phase_exponentials():
    A = np.array([[2.1, .2j], [-.2j, 4.3]])
    N = .7*np.eye(2)+.1*A
    profiles = [np.array([[0., 1.], [1., 0.]]), np.diag([1., -.4])]
    sources = np.array([[.12, -.08], [-.05, .1], [0., 0.]])
    parameter_durations, rates = np.array([.16, .24, .13]), np.array([.5, 1.75, 2.5])
    result = canonical_source_evolution(A, N, profiles, sources, parameter_durations,
                                        clock_rates=rates)
    J = np.block([[np.zeros((2, 2)), np.eye(2)], [-np.eye(2), np.zeros((2, 2))]])
    W = result['initial_covariance'].copy()
    previous = block_diag(A, np.eye(2))
    expected_work = []
    for i, (source, interval, rate) in enumerate(zip(sources, parameter_durations, rates)):
        eta = sum(value*profile for value, profile in zip(source, profiles))
        factor = expm(-eta/2)
        K = block_diag(factor@A@factor, expm(3*eta))
        expected_work.append(np.trace((K-previous)@W).real/2)
        # Independent exponential of the parameter-time generator rate*J*K.
        S = expm(interval*rate*J@K)
        W = S@W@S.conj().T
        np.testing.assert_allclose(result['phase_propagators'][i], S, atol=4e-14)
        np.testing.assert_allclose(result['phase_covariances'][i+1], W, atol=2e-13)
        previous = K
    np.testing.assert_allclose(result['source_work'], expected_work, atol=2e-13)
    np.testing.assert_allclose(result['proper_durations'], rates*parameter_durations, atol=0.)
    # Different parameter partitions with the same integrated clock yield
    # the same physical flow, including repeated source intervals.
    divided = canonical_source_evolution(A, N, profiles, np.repeat(sources, 2, axis=0),
        np.repeat(parameter_durations/2, 2), clock_rates=np.repeat(rates, 2))
    np.testing.assert_allclose(divided['phase_covariances'][::2], result['phase_covariances'], atol=3e-13)
    assert sum(divided['source_work']) == pytest.approx(sum(result['source_work']), abs=3e-13)
    assert divided['evaluation_work']['source_family_cache_hits'] == 3
    with pytest.raises(ValueError, match='clock rate'):
        canonical_source_evolution(A, N, profiles, sources, parameter_durations,
                                   clock_rates=[1., 0., 1.])


def test_phase_clock_matches_exact_static_and_homogeneous_proper_time_forms():
    # In ds²=-N(x)²dt²+dx²+dy²+dz² and theta=omega*t, the clock
    # one-form is N(x)dt: its exterior derivative is N'(x) dx^dt.
    # This checks closure directly, independently of the acceleration formula.
    lapse, spatial_slope, omega = 1.3, .17, 1.8
    metric = np.diag([-lapse**2, 1., 1., 1.])
    dg = np.zeros((4, 4, 4))
    dg[1, 0, 0] = -2*lapse*spatial_slope
    common = dict(reference_mass_squared=omega**2, source=-math.log(lapse),
        source_gradient=np.array([0., -spatial_slope/lapse, 0., 0.]), metric=metric,
        metric_gradient=dg, amplitude=.8, amplitude_gradient=np.zeros(4),
        amplitude_hessian=np.zeros((4, 4)), phase_gradient=np.array([omega, 0., 0., 0.]),
        phase_hessian=np.zeros((4, 4)), quantum_pressure_gradient=np.zeros(4))
    result = polar_source_congruence(**common)
    clock = result['clock']
    assert clock['phase_rate_per_proper_time'] == pytest.approx(omega/lapse)
    assert clock['proper_time_per_phase'] == pytest.approx(lapse/omega)
    np.testing.assert_allclose(clock['proper_time_covector'], [lapse, 0., 0., 0.], atol=2e-14)
    expected_exterior = np.zeros((4, 4))
    expected_exterior[1, 0], expected_exterior[0, 1] = spatial_slope, -spatial_slope
    np.testing.assert_allclose(clock['clock_covector_exterior_derivative'], expected_exterior, atol=2e-14)
    np.testing.assert_allclose(clock['clock_acceleration_identity_residual'], 0., atol=2e-14)
    assert result['acceleration_covariant'][1] == pytest.approx(spatial_slope/lapse)
    # A varying homogeneous lapse N(t) still gives the exact clock T=int N dt.
    # theta'(t)=N(t)*omega then has constant physical phase rate omega.
    lapse_rate = .23
    dg = np.zeros((4, 4, 4))
    dg[0, 0, 0] = -2*lapse*lapse_rate
    ddtheta = np.zeros((4, 4))
    ddtheta[0, 0] = lapse_rate*omega
    homogeneous = polar_source_congruence(**dict(common, source=0., source_gradient=np.zeros(4),
        metric_gradient=dg, phase_gradient=np.array([lapse*omega, 0., 0., 0.]),
        phase_hessian=ddtheta))
    np.testing.assert_allclose(homogeneous['clock']['clock_covector_exterior_derivative'], 0., atol=2e-14)
    np.testing.assert_allclose(homogeneous['acceleration_covariant'], 0., atol=2e-14)
    assert homogeneous['clock']['phase_rate_per_proper_time'] == pytest.approx(omega)
    assert abs(homogeneous['radial_equation_residual']) < 2e-14


def test_phase_clock_covector_is_invariant_under_positive_phase_relabeling():
    verified = _polar_congruence_verification(1.7**2)
    arguments = dict(verified['cases']['varying_quantum_pressure']['inputs'])
    original = polar_source_congruence(**arguments)
    first = np.asarray(arguments['phase_gradient'])
    second = np.asarray(arguments['phase_hessian'])
    slope, curvature = 2.3, -.4
    transformed = polar_source_congruence(**dict(arguments,
        phase_gradient=slope*first,
        phase_hessian=slope*second+curvature*np.outer(first, first)))
    # Only the geometric congruence is relabeled here; the nonlinear phase
    # replacement need not solve the original scalar equation.
    for key in ('proper_time_covector', 'clock_covector_exterior_derivative'):
        np.testing.assert_allclose(transformed['clock'][key], original['clock'][key], atol=3e-14)
    assert transformed['clock']['phase_rate_per_proper_time'] == pytest.approx(
        slope*original['clock']['phase_rate_per_proper_time'], rel=2e-14)
    assert abs(transformed['radial_equation_residual']) > .1


@pytest.fixture(scope='module')
def common_occupied_background():
    from cg_frg.ewsb.native_condensate import solve_joint_native_condensate
    from cg_frg.gravity.matter_source_response import evaluate_common_source_background
    certificate = solve_joint_native_condensate(g='1', Z='2', shells=32, iterations=35)
    arguments = dict(joint_certificate=certificate, planck_ratio=1.5,
                     mass_squared=3/(8*math.pi), vacuum_density=0.)
    return arguments, evaluate_common_source_background(**arguments)


def test_auxiliary_source_reduced_kinetic_matches_velocity_response(common_occupied_background):
    from scipy.optimize import brentq
    from cg_frg.ewsb.native_condensate import joint_native_source_response
    from cg_frg.gravity.matter_source_response import common_source_background_state
    _, result = common_occupied_background
    state = np.array(result['samples'][0]['state'])
    arguments = dict(g=1., Z=2., mass_squared=3/(8*math.pi), reference_radius_squared=2*math.pi)
    actual = common_source_background_state(state, **arguments)
    # Eliminate eta at fixed velocities, independently of the canonical root.
    # Differentiate the resulting momentum to measure the physical Hessian.
    def reduced_momentum(velocity):
        def equation(eta):
            radius = math.sqrt(2*math.pi)*math.exp(-eta)
            force = joint_native_source_response(amplitude_squared=state[1]**2, L=radius, g=1.)['Feta']
            return (force+1.5*math.exp(-3*eta)*float(velocity@velocity)
                    -.5*arguments['mass_squared']*math.exp(-eta)*float(state[3:5]@state[3:5]))
        eta = brentq(equation, actual['eta']-.03, actual['eta']+.03, xtol=1e-14)
        return math.exp(-3*eta)*velocity
    epsilon = 1e-6
    numerical = np.column_stack([(reduced_momentum(actual['matter_velocity']+epsilon*d)
        -reduced_momentum(actual['matter_velocity']-epsilon*d))/(2*epsilon) for d in np.eye(2)])
    np.testing.assert_allclose(numerical, actual['kinetic'][1:, 1:], rtol=2e-8, atol=2e-9)
    assert actual['hamiltonian_source_curvature'] > actual['velocity_source_curvature'] > 0


def test_common_background_source_derivative_and_feedback(common_occupied_background):
    from cg_frg.gravity.matter_source_response import common_source_background_state
    _, result = common_occupied_background
    state = np.array(result['samples'][8]['state'])
    arguments = dict(g=1., Z=2., mass_squared=3/(8*math.pi), reference_radius_squared=2*math.pi)
    data = common_source_background_state(state, **arguments)
    a, H = state[0], state[-1]
    derivative = np.r_[a*H, data['E_velocity'], -a**3*data['U_E'],
        data['matter_velocity'], -a**3*data['B']*state[3:5],
        -(2*data['E_velocity']**2+2*data['T'])/(2*1.5**2)]
    epsilon = 1e-5
    eta_dot = (common_source_background_state(state+epsilon*derivative, **arguments)['eta']
        -common_source_background_state(state-epsilon*derivative, **arguments)['eta'])/(2*epsilon)
    assert eta_dot == pytest.approx(data['eta_velocity'], rel=2e-8, abs=1e-10)
    assert result['initial_feedback']['radius_velocity'] < 0
    assert abs(result['initial_feedback']['identity_residual']) < 1e-13


def test_common_background_constraint_and_integration_refinement(common_occupied_background):
    from cg_frg.gravity.matter_source_response import evaluate_common_source_background
    arguments, result = common_occupied_background
    refined = evaluate_common_source_background(**arguments, rtol=2e-12, atol=2e-14)
    assert result['passed'] and refined['passed']
    np.testing.assert_allclose([r['state'] for r in result['samples']],
                               [r['state'] for r in refined['samples']], rtol=3e-8, atol=3e-10)
    assert refined['maximum_relative_friedmann_residual'] < 1e-10
    assert abs(refined['clock']['phase_reconstruction_residual']) < 1e-10
    assert result['operation_counts']['full_potential_integrals'] == len(result['samples'])+1
    assert result['operation_counts']['reused_vacuum_root_certificates'] == 1
    assert result['samples'][0]['eta'] != result['samples'][-1]['eta']
    certificate = result['finite_time_certificate']
    assert certificate['status'] == 'certified'
    assert float(certificate['duration_in_inverse_energy_unit'][0]) == .01
    assert float(certificate['sound_speed_squared_lower_bound']) > .19
    assert all(float(v) > 0 for v in certificate['remaining_boundary_margins'].values())
    assert certificate['work_counts']['spectral_shell_pair_evaluations'] == 520
    assert certificate['work_counts']['interval_ode_steps'] == 0


def test_common_background_rejects_nonphysical_source_branch(common_occupied_background):
    from cg_frg.gravity.matter_source_response import (
        common_source_background_state, evaluate_common_source_background)
    arguments, result = common_occupied_background
    with pytest.raises(ValueError, match='positive'):
        evaluate_common_source_background(**dict(arguments, planck_ratio=0.))
    state = np.array(result['samples'][0]['state'])
    state[6] = 100.
    with pytest.raises(ArithmeticError, match='positive reduced-kinetic branch'):
        common_source_background_state(state, g=1., Z=2., mass_squared=3/(8*math.pi),
                                       reference_radius_squared=2*math.pi)


@pytest.fixture(scope='module')
def certified_source_reuse(common_occupied_background):
    from cg_frg.gravity.matter_source_response import evaluate_common_source_reuse
    _, background = common_occupied_background
    return background, evaluate_common_source_reuse(background=background)


def test_source_reuse_encloses_independent_adaptive_solution(certified_source_reuse):
    from scipy.integrate import solve_ivp
    from cg_frg.gravity.matter_source_response import common_source_background_state
    background, result = certified_source_reuse
    coefficients = dict(g=1., Z=2., mass_squared=3/(8*math.pi), reference_radius_squared=2*math.pi)
    P = background['inputs']['planck_ratio']
    initial = np.array(background['samples'][0]['state'])
    def rhs(t, state):
        source = common_source_background_state(state, **coefficients)
        a, H = state[0], state[-1]
        return np.r_[a*H, source['E_velocity'], -a**3*source['U_E'],
            source['matter_velocity'], -a**3*source['B']*state[3:5],
            -(source['E_velocity']**2+source['T'])/P**2]
    reference = solve_ivp(rhs, (0., .01), initial, method='DOP853', rtol=2e-12, atol=2e-14)
    assert reference.success and result['passed']
    final = reference.y[:, -1]
    source = common_source_background_state(final, **coefficients)
    phase = math.atan2(final[4], final[3])
    for key in ('full_source', 'reused_source'):
        record = result[key]
        represented = np.array([sum(map(float, pair))/2 for pair in record['final_state']])
        assert np.max(np.abs(represented-final)) < float(record['full_interval_state_error_upper_bound'])
        assert abs(record['final_held_radius']-source['L']) < float(record['full_interval_radius_error_upper_bound'])
        assert abs(record['final_phase']-phase) < float(record['full_interval_phase_error_upper_bound'])
    # Differentiate the implicit field independently of the interval bound.
    epsilon = 1e-7
    for state in (initial, final):
        jacobian = np.column_stack([(rhs(0., state+epsilon*direction)-rhs(0., state-epsilon*direction))/(2*epsilon)
                                    for direction in np.eye(8)])
        assert np.linalg.norm(jacobian, np.inf) < float(result['uniform_bounds']['implicit_vector_field_lipschitz'])


def test_source_reuse_accounts_for_certification_work(certified_source_reuse):
    _, result = certified_source_reuse
    full, reused = result['full_source'], result['reused_source']
    assert 1 < reused['operation_counts']['source_refreshes'] < result['steps']
    assert reused['operation_counts']['accepted_source_reuses']+reused['operation_counts']['source_refreshes'] == result['steps']
    assert reused['operation_counts']['source_budget_tests'] == result['steps']-1
    for key in ('spectral_shell_pair_evaluations', 'interval_additions', 'interval_multiplications', 'interval_divisions'):
        assert 0 < reused['operation_counts'][key] < full['operation_counts'][key]
    assert result['setup_operation_counts']['spectral_tail_moment_terms'] == 65
    assert result['reused_invariant_box_work_counts']['spectral_shell_pair_evaluations'] == 520
    assert float(reused['maximum_node_source_residual']) <= float(result['source_residual_budget'])
    assert result['initial_data_error_bound'] == '0'


def test_source_reuse_rejects_proposal_outside_certified_bracket(common_occupied_background, monkeypatch):
    import cg_frg.gravity.matter_source_response as module
    _, background = common_occupied_background
    original = module.common_source_background_state
    def incorrect_proposal(*args, **kwargs):
        result = original(*args, **kwargs)
        result['eta'] = 0.
        return result
    monkeypatch.setattr(module, 'common_source_background_state', incorrect_proposal)
    with pytest.raises(ArithmeticError, match='certified bracket'):
        module.evaluate_common_source_reuse(background=background)


def test_planar_constraints_and_analytic_initial_metric_response(common_occupied_background):
    from cg_frg.gravity.matter_source_response import evaluate_plane_common_source
    _, background = common_occupied_background
    result = evaluate_plane_common_source(background=background, points=9, steps=4)
    assert result['passed']
    run = result['principal_run']
    psi = np.asarray(run['initial_conformal_factor'])
    x = 2*math.pi*np.arange(9)/9
    first_cosine = 2*np.mean((psi-1)*np.cos(x))
    A0 = background['initial_occupied_energy']
    P = background['inputs']['planck_ratio']
    # Linearize the Einstein Hamiltonian constraint at the occupied FLRW
    # state, holding canonical momentum density fixed. Here T0=V0=A0/2.
    expected = 1e-3*(A0/2)/(2*P**2+3*A0)
    assert first_cosine == pytest.approx(expected, rel=3e-6)
    assert np.max(psi)-np.min(psi) > 1e-6
    assert abs(np.mean(psi)-1) < 1e-13
    assert run['diagnostics'][0]['source_range'][1] > run['diagnostics'][0]['source_range'][0]
    assert run['diagnostics'][-1]['source_range'][0] > run['diagnostics'][0]['source_range'][0]
    assert result['refinement']['spatial_refinement_retained_mode_difference'] < 1e-9
    for row in run['diagnostics']:
        assert row['minimum_spatial_curvature_margin'] > .09
        assert row['minimum_phase_norm'] > .07


def test_planar_zero_amplitude_reduces_to_same_background_ode(common_occupied_background):
    from scipy.integrate import solve_ivp
    from cg_frg.gravity.matter_source_response import (
        evaluate_plane_common_source, common_source_background_state)
    _, background = common_occupied_background
    result = evaluate_plane_common_source(background=background, points=9,
                                         steps=4, amplitude=0., refine=False)
    cfg = background['inputs']
    coefficients = {k: cfg[k] for k in ('g', 'Z', 'mass_squared', 'reference_radius_squared')}
    P, Z = cfg['planck_ratio'], cfg['Z']
    def rhs(t, y):
        data = common_source_background_state(y, **coefficients)
        a, H = y[0], y[-1]
        return np.r_[a*H, data['E_velocity'], -a**3*data['U_E'], data['matter_velocity'],
                     -a**3*data['B']*y[3:5],
                     -(Z*data['E_velocity']**2+2*data['T'])/(2*P**2)]
    reference = solve_ivp(rhs, (0., .01), background['samples'][0]['state'],
                          method='DOP853', rtol=2e-12, atol=2e-14)
    final = reference.y[:, -1]
    expected = np.r_[final[0], final[0], -final[-1], -final[-1], final[1:7]]
    actual = np.asarray(result['principal_run']['final_state'])
    assert result['passed'] and reference.success
    np.testing.assert_allclose(actual, expected[:, None]+np.zeros_like(actual), rtol=2e-10, atol=2e-12)


@pytest.fixture(scope='module')
def expanding_rms_window():
    from cg_frg.gravity.matter_source_response import evaluate_expanding_rms_window
    # Rational synthetic physical inputs exercise the same explicit interface
    # as the production driver; no comparison values enter this test.
    return evaluate_expanding_rms_window(omega_m=1/3, omega_vacuum=2/3,
                                        acceleration_ratio=1/5)


def test_expanding_rms_exact_field_and_uniform_constraint_window(expanding_rms_window):
    import json
    result = expanding_rms_window
    assert result['passed'] and result['uniform_certificate']['passed']
    json.dumps(result, allow_nan=False)
    certificate = result['uniform_certificate']
    assert all(float(bounds[0]) > 0 for bounds in certificate['exit_margins'].values())
    assert certificate['full_poisson_defect_uniform_upper'] == '0'
    for row in result['main']['rows']:
        a, D, pD, pa = row['state']
        assert 1 <= a < 1.06 and .001 <= D < .002
        assert 0 <= pD < 8e-7 and -6.6 < pa < -5.9
        assert row['maximum_flux_reconstruction_residual'] < 1e-19
        assert row['full_poisson_defect_L2'] < 1e-14
        assert row['full_flow_acceleration_defect_L2'] > 0
        assert row['full_flow_acceleration_defect_L2'] < float(certificate['full_flow_acceleration_defect_uniform_upper'])
        assert row['reduced_kinetic_hessian'] >= float(certificate['physical_hamiltonian_hessian_lower'])


def test_expanding_rms_energy_derivatives_from_independent_quadrature(expanding_rms_window):
    from scipy.integrate import quad
    result = expanding_rms_window
    mass = 3*result['inputs']['omega_m']
    a0, k = result['inputs']['acceleration_ratio'], result['inputs']['wavenumber']
    def binding_energy(a, D):
        def integrand(u):
            theta = math.pi*u*u/2
            flux = mass*D*math.sin(theta)/(2*a*a*k)
            g = math.sqrt((flux*flux+flux*math.hypot(flux, 2*a0))/2)
            # Independent convergent small-g expansion avoids cancellation
            # in the primitive used by the production implementation.
            potential = g**3/(3*a0)-g**5/(10*a0**3)+3*g**7/(56*a0**5)-5*g**9/(144*a0**7)
            return 4*a**3*u*(potential-g*flux)
        return quad(integrand, 0., 1., epsabs=1e-23, epsrel=1e-12)[0]
    for row in (result['main']['rows'][0], result['main']['rows'][-1]):
        a, D, _, _ = row['state']
        assert binding_energy(a, D) == pytest.approx(row['potential_energy'], rel=2e-10)
        derivative_D = (binding_energy(a, D+1e-7)-binding_energy(a, D-1e-7))/(2e-7)
        derivative_a = (binding_energy(a+1e-3, D)-binding_energy(a-1e-3, D))/(2e-3)
        assert derivative_D == pytest.approx(row['potential_energy_derivative_D'], rel=2e-8)
        assert derivative_a == pytest.approx(row['potential_energy_derivative_a'], rel=2e-5, abs=1e-19)
    assert result['maximum_state_refinement_difference'] < 1e-10
    assert result['operation_counts']['exact_field_reconstructions'] == result['operation_counts']['potential_quadratures']
    assert result['operation_counts']['rational_exit_certificate_evaluations'] == 1
