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

"""Independent oscillation, basis, free-phase and static-response checks."""
import numpy as np
import pytest
from cg_frg.neutrino.complex_mixing import mixing_matrix, pmns_texture
from cg_frg.neutrino.propagation import (vacuum_hamiltonian, hamiltonian,
    propagate_layers, propagate_profile, beta_mass_observables,
    dirac_yukawa, flavour_invariants, mass_squared_source)
from cg_frg.gravity.local_response import (background_response, flux,
    solve_dirichlet, local_source_decomposition, gaussian_disk_source,
    plane_source_state, evolve_plane_source, primitive)
from cg_frg.cosmology.cold_source import (
    plane_dust_solution, transported_density, evaluate_cold_transport, evolve_plane_dust)


def test_cosmology_readers_reject_file_records_before_file_access(monkeypatch):
    from pathlib import Path
    from cg_frg.cosmology.camb_interface import current_camb_record, current_bao_record
    def forbidden(*args, **kwargs):
        raise AssertionError('a comparison record must not read a side file')
    monkeypatch.setattr(Path, 'read_text', forbidden)
    for candidate in ('comparison.json', Path('comparison.json')):
        for reader in (current_camb_record, current_bao_record):
            result = reader({}, candidate)
            assert result['status'] == 'PENDING'
            assert 'in-memory mappings' in result['reason']


@pytest.mark.parametrize('module,flag', [
    ('scripts.run_explicit_camb','--configuration'),
    ('scripts.run_explicit_camb','--output'),
    ('scripts.run_explicit_camb','--tau-reio'),
    ('scripts.run_bao_comparison','--output'),
    ('scripts.validate_endpoint_cosmology','--output'),
])
def test_cosmology_commands_reject_unregistered_file_and_physical_inputs(monkeypatch,module,flag):
    import importlib
    import sys
    command = importlib.import_module(module)
    def forbidden(*args, **kwargs):
        raise AssertionError('invalid arguments must be rejected before store access or calculation')
    monkeypatch.setattr(command, 'get', forbidden)
    monkeypatch.setattr(sys, 'argv', [module, flag, 'unregistered'])
    with pytest.raises(SystemExit) as error:
        command.main()
    assert error.value.code == 2


def test_camb_execution_uses_registered_reionization_without_completed_center(monkeypatch,tmp_path):
    import copy
    import json
    import sys
    from cg_core import params
    from cg_frg.cosmology.camb_interface import INPUT_KEYS
    from comparison.sm_rge.inputs import init_sm_table
    from scripts import run_explicit_camb as command
    inputs = {key:params.get(key) for key in INPUT_KEYS}
    reference_store = tmp_path/'reference_inputs.json'
    reference_store.write_text(json.dumps({'parameters':{}}),encoding='utf8')
    monkeypatch.setattr(params, '_SM_FILE', reference_store)
    init_sm_table()
    registered = copy.deepcopy(params.sm_value('CAMB_PROPAGATION_SETTINGS'))
    assert registered['reionization_optical_depth'] == .054
    assert registered['kind'] == 'declared propagation convention'
    # A non-default value detects any independent constant in the command.
    registered['reionization_optical_depth'] = .061
    params.sm_set('CAMB_PROPAGATION_SETTINGS',registered,
                  note='independent test of a registered propagation convention',
                  comparison_kind='declared_convention')
    configs, published = [], []
    def controlled_get(key):
        if key == 'endpoint_camb_record':
            raise KeyError('no completed centre exists')
        return inputs[key]
    def no_solver(config):
        configs.append(config)
        return {'status':'current_inputs_match','camb_version':'test model',
                'configuration_sha256':'test configuration', 'density_dictionary':{},'outputs':{}}
    monkeypatch.setattr(command, 'get', controlled_get)
    monkeypatch.setattr(command, 'run', no_solver)
    monkeypatch.setattr(command, 'current_camb_record', lambda inputs,record:record)
    monkeypatch.setattr(command, 'register_completed_record',
                        lambda record,**kwargs:published.append(record) or record)
    monkeypatch.setattr(sys, 'argv', ['run_explicit_camb','--mode','background','--accuracy','2'])
    command.main()
    assert len(configs) == len(published) == 1
    assert configs[0]['cosmology']['tau'] == .061
    assert configs[0]['endpoint_inputs'] == inputs
    assert configs[0]['accuracy']['AccuracyBoost'] == 2.


def test_background_record_has_only_current_background_observables():
    import copy
    import re
    from cg_core.params import published_record
    from cg_frg.cosmology.camb_interface import current_camb_record, fingerprint
    original = published_record('endpoint_camb_record')
    record = copy.deepcopy(original)
    record.pop('execution_sha256',None)
    record.pop('background_response',None)
    record['configuration']['calculation_mode'] = 'background'
    record['calculation_mode'] = 'background'
    record['configuration_sha256'] = fingerprint(record['configuration'])
    for flag in ('WantCls','WantTransfer','WantTensors'):
        record['resolved_parameters'] = re.sub(r'(?m)^(\s*'+flag+r' = ).+$',
            r'\g<1>False',record['resolved_parameters'])
    for key in ('sigma8','S8_total_matter'):
        record['outputs'].pop(key,None)
    inputs = record['configuration']['endpoint_inputs']
    assert current_camb_record(inputs,record)['status'] == 'current_inputs_match'
    record['outputs']['sigma8'] = .8
    assert current_camb_record(inputs,record)['status'] == 'PENDING'


def test_background_response_reuses_center_and_only_refines_selected_stencils():
    import copy
    import math
    from cg_core.params import published_record
    from cg_frg.cosmology.camb_interface import (BACKGROUND_COORDINATES,
        background_physical_coordinates, evaluate_background_response,
        compose_background_directions, fingerprint)
    center = published_record('endpoint_camb_record')
    baseline = background_physical_coordinates(center)
    powers = {'YHe':.03,'omega_b':-.12,'omega_m':-.25,'TCMB':-.8,'N_eff':-.1}
    calls = []
    def independent_power_law(config):
        calls.append(config)
        factor = math.prod((config['physical_coordinates'][key]/baseline[key])**power
                           for key,power in powers.items())
        outputs = copy.deepcopy(center['outputs'])
        for key in ('sigma8','S8_total_matter'):
            outputs.pop(key,None)
        outputs['r_drag_Mpc'] *= factor
        return {'configuration':config,'configuration_sha256':fingerprint(config),
                'calculation_mode':'background','camb_version':'analytic test function',
                'outputs':outputs,'work':{'explicit_background_solver_calls':1,
                                         'full_perturbation_solver_calls':0}}
    result = evaluate_background_response(center,solver=independent_power_law)
    assert len(calls) == 2*len(BACKGROUND_COORDINATES)
    assert result['work']['center_solver_calls'] == 0
    assert result['work']['full_perturbation_solver_calls'] == 0
    for key,power in powers.items():
        assert result['responses'][key]['log_derivative']['r_drag_Mpc'] == pytest.approx(power,abs=2e-12)
        assert result['responses'][key]['log_derivative']['DM_over_rd@0.51'] == pytest.approx(-power,abs=2e-12)
    refined = evaluate_background_response(center,refine=('TCMB',),previous=result,
                                           solver=independent_power_law)
    assert len(calls) == 12
    assert refined['work']['reused_stencil_evaluations'] == 10
    assert refined['work']['new_stencil_evaluations'] == 2
    assert refined['responses']['TCMB']['half_step_abs_difference']['r_drag_Mpc'] < 3e-12
    incomplete = compose_background_directions(refined,{'shared':{'H0':2.,'TCMB':1.}},
        source='test source map')
    assert incomplete['directions']['shared']['missing_response_coordinates'] == ['H0']
    complete = compose_background_directions(refined,{'test':{'TCMB':2.,'omega_b':1.}},
        source='specified two-coordinate test direction',held_fixed=('omega_m','N_eff','YHe'))
    assert complete['directions']['test']['log_readout_derivative']['r_drag_Mpc'] == pytest.approx(-1.72,abs=3e-12)
    corrupted = copy.deepcopy(result)
    corrupted['stencil'][0]['readouts']['r_drag_Mpc'] *= 1.01
    with pytest.raises(ValueError,match='fingerprint'):
        evaluate_background_response(center,previous=corrupted,solver=independent_power_law)


def test_background_execution_never_calls_power_solver(monkeypatch):
    import copy
    import sys
    import types
    from cg_core.params import published_record
    from cg_frg.cosmology import camb_interface as interface
    center = published_record('endpoint_camb_record')
    config = interface.background_probe_configuration(center,'YHe',.001)
    calls = []
    class Parameters:
        def __init__(self):
            self.Recomb = object()
        def set_cosmology(self,**kwargs):
            self.__dict__.update(kwargs)
            self.omnuh2 = kwargs['mnu']/94
        def set_dark_energy(self,**kwargs): pass
        def set_accuracy(self,**kwargs): pass
        @property
        def InitPower(self): return types.SimpleNamespace(set_params=lambda **kwargs:None)
        def set_for_lmax(self,*args,**kwargs): raise AssertionError('power setup called')
        def set_matter_power(self,*args,**kwargs): raise AssertionError('power setup called')
    class Results:
        nu_masses = [1.,2.,3.]
        def get_derived_params(self): return {'zeq':3400.,'rdrag':147.,'thetastar':1.04}
        def get_sigma8_0(self): raise AssertionError('power-spectrum output requested during background-only calculation')
    def background(parameters,**kwargs):
        assert not parameters.WantCls and not parameters.WantTransfer and not parameters.WantTensors
        calls.append(kwargs)
        return Results()
    def forbidden(*args,**kwargs): raise AssertionError('full perturbation solver called')
    module = types.SimpleNamespace(CAMBparams=Parameters,get_background=background,get_results=forbidden,
        model=types.SimpleNamespace(NonLinear_none=0),__version__='test',
        constants=types.SimpleNamespace(m_e=9e-31,sigma_thomson=6e-29))
    monkeypatch.setitem(sys.modules,'camb',module)
    monkeypatch.setattr(interface,'validate_neutrino_resolution',lambda *args:None)
    monkeypatch.setattr(interface,'density_dictionary',lambda *args,**kwargs:copy.deepcopy(center['density_dictionary']))
    monkeypatch.setattr(interface,'background_distances',lambda *args:copy.deepcopy(center['outputs']['background_distances']))
    result = interface.run(config)
    assert len(calls) == 1
    assert result['work']['explicit_background_solver_calls'] == 1
    assert result['work']['full_perturbation_solver_calls'] == 0
    assert not {'sigma8','S8_total_matter'} & result['outputs'].keys()


def test_two_flavour_formula_profile_and_units():
    theta, energy, length, dm2 = .38, 2e6, 2e9, 7.1e-5
    u = mixing_matrix(np.sin(theta), 0., 0., 0.)
    h = vacuum_hamiltonian([0, np.sqrt(dm2), .05], u, energy)
    exact = np.sin(2*theta)**2*np.sin(dm2*length/(4*energy))**2
    layers = propagate_layers([(length/2, h), (length/2, h)])
    profile = propagate_profile(lambda x: h, length)
    assert layers["probabilities"][1, 0] == pytest.approx(exact, abs=1e-13)
    assert profile["probabilities"] == pytest.approx(layers["probabilities"], abs=2e-10)
    assert layers["probabilities"].sum(axis=0) == pytest.approx(np.ones(3), abs=2e-13)
    constant = np.diag([1., 2., 4.]).astype(complex)*1e-12
    original = constant.copy()
    propagate_profile(lambda x: constant, 1e9)
    assert np.array_equal(constant, original)


def test_environment_and_antineutrino_are_explicit():
    u, m, energy = pmns_texture(), [.003, .009, .05], 3e6
    v = np.diag([2e-12, 0., 0.])
    hv = vacuum_hamiltonian(m, u, energy)
    assert hamiltonian(m, u, energy, antineutrino=True) == pytest.approx(hv.conj())
    assert hamiltonian(m, u, energy, matter_eV=v, antineutrino=True) == pytest.approx(hv.conj()-v)
    with pytest.raises(ValueError, match="explicit antineutrino"):
        hamiltonian(m, u, energy, extra_eV=v, antineutrino=True)
    with pytest.raises(ValueError, match="Hermitian"):
        propagate_layers([(1., np.array([[0, 1, 0], [0, 0, 0], [0, 0, 0]]))])


def test_natural_units_preserve_full_source_propagation():
    masses, u, energy, distance = np.array([.003, .009, .05]), pmns_texture(), 3e6, 4e10
    potential = 1e-12*np.array([[2., .3j, .1], [-.3j, 0., .2j], [.1, -.2j, -.4]])
    h = hamiltonian(masses, u, energy, matter_eV=potential)
    original = propagate_layers([(distance, h)])
    for scale in (1e-9, 1e9):
        scaled = hamiltonian(scale*masses, u, scale*energy, matter_eV=scale*potential)
        np.testing.assert_allclose(scaled/scale, h, rtol=2e-13, atol=1e-28)
        result = propagate_layers([(distance/scale, scaled)])
        np.testing.assert_allclose(result['probabilities'], original['probabilities'], atol=3e-13)
        profile = propagate_profile(lambda x: scaled, distance/scale)
        np.testing.assert_allclose(profile['probabilities'], original['probabilities'], atol=2e-9)


def test_noncommuting_layers_follow_traversal_order_and_profile():
    first = np.array([[.6, .2+.1j, 0.], [.2-.1j, -.3, .15], [0., .15, .1]])
    second = np.array([[-.4, .3j, .2], [-.3j, .2, .1j], [.2, -.1j, .5]])
    ordered = propagate_layers([(.7, first), (1.3, second)])
    reversed_order = propagate_layers([(1.3, second), (.7, first)])
    assert np.linalg.norm(ordered['probabilities']-reversed_order['probabilities']) > .05
    profile = propagate_profile(lambda x: first if x < .7 else second, 2.)
    np.testing.assert_allclose(profile['evolution'], ordered['evolution'], atol=2e-9)


def test_complex_vector_potential_and_vacuum_cp_conventions():
    masses, u, energy = [.003, .009, .05], pmns_texture(), 3e6
    potential = 1e-12*np.array([[2., .3j, .1], [-.3j, 0., .2j], [.1, -.2j, -.4]])
    vacuum = vacuum_hamiltonian(masses, u, energy)
    anti = hamiltonian(masses, u, energy, matter_eV=potential, antineutrino=True)
    np.testing.assert_allclose(anti, vacuum.conj()-potential.conj(), rtol=2e-13, atol=1e-28)
    assert np.linalg.norm(anti-(vacuum.conj()-potential)) > 1e-13
    particle = propagate_layers([(4e10, vacuum)])
    antiparticle = propagate_layers([(4e10, vacuum.conj())])
    np.testing.assert_allclose(antiparticle['probabilities'], particle['probabilities'].T, atol=2e-13)
    phased = vacuum_hamiltonian(masses, pmns_texture(majorana=(.8, 1.7)), energy)
    np.testing.assert_allclose(phased, vacuum, rtol=2e-13, atol=1e-28)


def test_nonhermitian_rejection_is_independent_of_energy_unit():
    bad = np.array([[0., 1j, 0.], [0., 1., 0.], [0., 0., 2.]])
    for scale in (1e-32, 1., 1e32):
        with pytest.raises(ValueError, match='Hermitian'):
            propagate_layers([(1/scale, scale*bad)])


def test_nonfinite_tolerances_and_yukawa_normalization_are_rejected():
    for invalid in (np.nan, np.inf, -1., 0.):
        with pytest.raises(ValueError):
            propagate_profile(lambda x: np.eye(3), 1., rtol=invalid)
        with pytest.raises(ValueError):
            dirac_yukawa([.01, 1., 170.], np.eye(3), np.eye(3), invalid,
                         scale_GeV=200., scheme='specified')
        with pytest.raises(ValueError):
            solve_dirichlet(lambda x: np.ones(len(x)), lambda x: np.zeros(len(x)),
                            n=2, tolerance=invalid)
    for invalid_lengths in ((1., 1.), (1., np.inf, 1.), (1., -1., 1.)):
        with pytest.raises(ValueError):
            solve_dirichlet(lambda x: np.ones(len(x)), lambda x: np.zeros(len(x)),
                            n=2, lengths=invalid_lengths)
    for invalid_iterations in (-1, True, 1.5):
        with pytest.raises(ValueError):
            solve_dirichlet(lambda x: np.ones(len(x)), lambda x: np.zeros(len(x)),
                            n=2, max_iterations=invalid_iterations)


def test_free_majorana_range_and_flavour_basis():
    m, u = [.004, .009, .05], pmns_texture()
    masses = beta_mass_observables(m, u)
    for a in np.linspace(0, 2*np.pi, 19):
        for b in np.linspace(0, 2*np.pi, 17):
            value = beta_mass_observables(m, pmns_texture(majorana=(a, b)))
            assert value["m_beta_eV"] == pytest.approx(masses["m_beta_eV"])
            assert masses["m_beta_beta_min_eV"]-1e-14 <= value["m_beta_beta_at_supplied_phases_eV"] <= masses["m_beta_beta_max_eV"]+1e-14
    yu = dirac_yukawa([.01, 1., 170.], u, np.eye(3), 246., scale_GeV=200., scheme="specified")['Y']
    yd = np.diag([1e-4, .003, .02])
    q, _ = np.linalg.qr(np.random.default_rng(2).normal(size=(3, 3))+1j*np.eye(3))
    first, second = flavour_invariants(yu, yd), flavour_invariants(q@yu, q@yd)
    for key in first:
        assert second[key] == pytest.approx(first[key], abs=2e-13)


def test_static_zero_background_and_external_field_derivative():
    assert np.all(background_response([0., 0., 0.])["principal_tensor"] == 0)
    g, direction = np.array([.4, -.2, .7]), np.array([1., 2., -.3])
    result = background_response(g)
    eps = 1e-6
    numeric = (flux(g+eps*direction)-flux(g-eps*direction))/(2*eps)
    assert result["principal_tensor"]@direction == pytest.approx(numeric, abs=2e-10)
    assert result["longitudinal_eigenvalue"] > result["transverse_eigenvalue"] > 0


def test_actual_disk_source_weak_identity():
    source = gaussian_disk_source(mass=.015, radial_width=.22, vertical_width=.12)
    solution = solve_dirichlet(source, lambda x: .1*x[:, 0], n=4,
                               a0=.3, epsilon=.07, tolerance=2e-10)
    result = local_source_decomposition(solution)
    assert result["interior_source_residual"] < 2e-10
    assert solution["source_integral"] > 0
    assert abs(solution["flux_balance_residual"]) < 2e-9
    assert result["average_requires_boundary_flux"]
    with pytest.raises(ValueError, match="solved response"):
        local_source_decomposition(solution, a0=1.)
    with pytest.raises(ValueError, match="solved response"):
        local_source_decomposition(solution, epsilon=0.)


def test_weak_source_decomposition_scales_with_the_solved_model():
    def solve(scale):
        return solve_dirichlet(lambda x: np.full(len(x), .01*scale),
                               lambda x: .1*scale*x[:, 0], n=3,
                               a0=.3*scale, epsilon=.07*scale, tolerance=1e-11*scale)
    reference = solve(1.)
    reference_loads = local_source_decomposition(reference)
    for scale in (1e-3, 1e3):
        solution = solve(scale)
        loads = local_source_decomposition(solution)
        np.testing.assert_allclose(solution['phi']/scale, reference['phi'], atol=1e-9)
        for key in ('linear_divergence_load', 'source_divergence_load',
                    'polarization_divergence_load'):
            np.testing.assert_allclose(loads[key]/scale, reference_loads[key], atol=1e-10)
        assert loads['interior_source_residual'] < 1e-11*scale
        # These are integrated nodal loads. No pointwise or cosmological
        # density is manufactured by the algebraic source identity.
        assert 'mass-matrix' in loads['density_normalization']


def test_exact_dust_slice_satisfies_continuity_and_poisson_before_crossing():
    assert evaluate_cold_transport()['checks_passed']
    q=np.linspace(0,2*np.pi,63,endpoint=False)
    options=dict(amplitude=.4,growth=.8,growth_velocity=.7,
                 scale_factor=.6,mean_density=1.3,four_pi_G=.9,wave_number=1.)
    result=plane_dust_solution(q,**options)
    # Material continuity: drho/dt+3 H rho+rho div(v)/a=0.
    h=.5
    jdot=-options['amplitude']*options['growth_velocity']*np.cos(q)
    material=-3*h*result['density']-result['density']*jdot/result['jacobian']
    divergence=jdot/result['jacobian']
    np.testing.assert_allclose(material+3*h*result['density']
                               +result['density']*divergence,0.,atol=5e-16)
    with pytest.raises(ValueError,match='single-stream'):
        plane_dust_solution(q,**{**options,'growth':2.5})
    with pytest.raises(ValueError,match='positive Jacobian'):
        transported_density(1.,np.diag([-1.,1.,1.]),scale_factor=1.)


def test_scalar_mass_self_energy_preserves_labels_and_rest_limit():
    u=pmns_texture()
    masses=np.array([.003,.009,.05])
    tilt=.035
    shift=masses[1]**2*((1+tilt)**2-1)
    correction=mass_squared_source([0.,shift,0.],u,3e6,amplitude=1.)
    raised=masses.copy()
    raised[1]*=1+tilt
    actual=vacuum_hamiltonian(masses,u,3e6)+correction
    np.testing.assert_allclose(actual,vacuum_hamiltonian(raised,u,3e6),atol=2e-25)
    anti=mass_squared_source([0.,shift,0.],u,3e6,amplitude=1.,antineutrino=True)
    np.testing.assert_allclose(anti,correction.conj(),atol=1e-28)
    assert np.count_nonzero(mass_squared_source([0.,shift,0.],u,3e6,amplitude=0.))==0
    twice_energy=mass_squared_source([0.,shift,0.],u,6e6,amplitude=1.)
    np.testing.assert_allclose(2*twice_energy,correction,atol=1e-28)


def test_characteristic_evolution_matches_growing_solution_and_stops_at_crossing():
    for cold_fraction in (1.,.4):
        result=evolve_plane_dust(a_initial=.03,a_final=.9,amplitude=.2,
            omega_m0=1.,omega_cold0=cold_fraction)
        power=(np.sqrt(1+24*cold_fraction)-1)/4
        assert result['growth']==pytest.approx(.9**power,rel=3e-12)
        assert result['growth_log_derivative']==pytest.approx(power*.9**power,rel=3e-12)
        assert result['physical_volume_mean_residual']<1e-14
    options=dict(a_initial=.03,a_final=1.,amplitude=.2,omega_m0=.3,omega_cold0=.25)
    first=evolve_plane_dust(**options)
    refined=evolve_plane_dust(**options,rtol=2e-13,atol=2e-15)
    assert first['growth']==pytest.approx(refined['growth'],rel=2e-11)
    with pytest.raises(ValueError,match='crossing'):
        evolve_plane_dust(a_initial=.03,a_final=1.,amplitude=2.,
                          omega_m0=1.,omega_cold0=1.)


def _plane_initial_data():
    positions = np.linspace(0., 1., 9)
    middle = (positions[:-1]+positions[1:])/2
    masses = .1*np.diff(positions)*(1+.2*np.cos(2*np.pi*middle)
                                    +.1*np.sin(2*np.pi*middle))
    velocity = .02*np.sin(np.pi*positions)
    velocity[[0, -1]] = 0.
    return positions, masses, velocity


def test_nonlinear_plane_field_energy_and_actual_variational_force():
    from scipy.integrate import quad
    positions, masses, _ = _plane_initial_data()
    a0, coupling, boundary = .3, .7, (.03, .01)
    result = plane_source_state(positions, masses, a0=a0, four_pi_G=coupling,
                                boundary_values=boundary)
    np.testing.assert_allclose(flux(result['gradient_nodes'][:, None], a0)[:, 0],
                               result['flux_nodes'], atol=2e-16)
    assert result['boundary_residual'] < 2e-13
    assert result['energy_identity_residual'] < 2e-14
    # Independent physical-position quadrature of F and rho*Phi. Fubini's
    # identity integral rho*Phi=M*Phi_left+integral g*(M-M_left) avoids
    # reusing the code's Legendre-energy formula for the source energy.
    source_energy, field_energy = masses.sum()*boundary[0], 0.
    before = 0.
    for index, mass in enumerate(masses):
        left, right = positions[index:index+2]
        width = right-left
        current0 = result['flux_nodes'][index]
        def gradient(z):
            current = current0+coupling*mass*(z-left)/width
            return np.sign(current)*np.sqrt((current*current
                    +abs(current)*np.hypot(current, 2*a0))/2)
        zero = left-current0*width/(coupling*mass)
        points = [zero] if left < zero < right else None
        field_energy += quad(lambda z: float(primitive(np.array([gradient(z)]), a0)),
            left, right, points=points, epsabs=1e-13, epsrel=1e-11)[0]/coupling
        source_energy += quad(lambda z: gradient(z)*(masses.sum()-before
            -mass*(z-left)/width), left, right, points=points,
            epsabs=1e-13, epsrel=1e-11)[0]
        before += mass
    assert result['source_energy'] == pytest.approx(source_energy, abs=2e-13)
    assert result['field_energy'] == pytest.approx(field_energy, abs=2e-13)
    # A perturbation of actual node positions differentiates the complete
    # relaxed potential energy, including the re-solved boundary flux.
    for index in range(1, len(positions)-1):
        positive, negative = positions.copy(), positions.copy()
        positive[index] += 1e-6; negative[index] -= 1e-6
        settings = dict(a0=a0, four_pi_G=coupling, boundary_values=boundary)
        derivative = (plane_source_state(positive, masses, **settings)['potential_energy']
            -plane_source_state(negative, masses, **settings)['potential_energy'])/2e-6
        assert -derivative == pytest.approx(result['generalized_force'][index-1], abs=5e-11)


def test_plane_feedback_mass_energy_and_time_step_convergence():
    positions, masses, velocity = _plane_initial_data()
    results = [evolve_plane_source(positions, masses, velocity,
        duration=.4, steps=steps, a0=.3) for steps in (20, 40, 80)]
    errors = [np.max(np.abs(results[i]['positions'][-1]-results[i+1]['positions'][-1]))
              for i in (0, 1)]
    assert 3.8 < errors[0]/errors[1] < 4.2
    balances = [result['maximum_energy_balance_residual'] for result in results]
    assert 3.8 < balances[0]/balances[1] < 4.2
    assert balances[-1] < 3e-12
    assert np.max(np.abs(results[-1]['velocities'][-1]-velocity)) > .01
    for result, steps in zip(results, (20, 40, 80)):
        assert result['mass_conservation_residual'] < 1e-15
        assert result['minimum_cell_length'] > .11
        assert result['boundary_residual'] < 2e-13
        assert result['energy_identity_residual'] < 2e-14
        assert result['operation_counts']['field_solves'] == steps+1
        assert result['operation_counts']['force_evaluations'] == steps+1
        assert result['operation_counts']['mass_matrix_factorizations'] == 1
        assert result['positions'][:, [0, -1]] == pytest.approx(
            np.broadcast_to([0., 1.], (steps+1, 2)))
    refined_quadrature = evolve_plane_source(positions, masses, velocity,
        duration=.4, steps=40, a0=.3, quadrature_order=40)
    np.testing.assert_allclose(refined_quadrature['positions'], results[1]['positions'], atol=2e-12)


def test_plane_feedback_time_dependent_boundary_work():
    positions, masses, velocity = _plane_initial_data()
    boundary = lambda time: (.01*time, .03*time)
    rate = lambda time: (.01, .03)
    results = [evolve_plane_source(positions, masses, velocity, duration=.4,
        steps=steps, a0=.3, boundary=boundary, boundary_rate=rate) for steps in (20, 40)]
    first, second = results
    assert 3.8 < first['maximum_energy_balance_residual']/second['maximum_energy_balance_residual'] < 4.2
    assert second['boundary_work'][-1] > 7e-4
    assert abs(second['total_energy'][-1]-second['total_energy'][0]
               -second['boundary_work'][-1]) < 1.1e-10
    # A uniform time-dependent potential changes the source energy by
    # M*b(t), and the two boundary fluxes give exactly this work.
    constant = evolve_plane_source(positions, masses, velocity, duration=.2, steps=20, a0=.3)
    shifted = evolve_plane_source(positions, masses, velocity, duration=.2, steps=20, a0=.3,
        boundary=lambda time: (.07*time, .07*time), boundary_rate=lambda time: (.07, .07))
    np.testing.assert_allclose(shifted['positions'], constant['positions'], atol=1e-14)
    np.testing.assert_allclose(shifted['total_energy']-constant['total_energy'],
                              masses.sum()*.07*shifted['time'], atol=2e-14)
    assert shifted['boundary_work'][-1] == pytest.approx(masses.sum()*.07*.2, abs=2e-15)


def test_plane_feedback_zero_gradient_and_crossing_guard():
    positions = np.linspace(0., 1., 5)
    masses = np.full(4, .025)
    state = plane_source_state(positions, masses, a0=.3)
    assert state['gradient_nodes'][2] == pytest.approx(0., abs=1e-15)
    np.testing.assert_allclose(state['generalized_force'], -state['generalized_force'][::-1], atol=1e-15)
    velocity = np.array([0., 0., -10., 0., 0.])
    with pytest.raises(ValueError, match='crossing'):
        evolve_plane_source(positions, masses, velocity, duration=.1, steps=1, a0=.3)
    with pytest.raises(ValueError, match='both boundary'):
        evolve_plane_source(positions, masses, velocity, duration=.1, steps=1,
                            boundary=lambda time: (0., time))


def test_covariant_clock_primitive_variation_and_geodesic_branch():
    from cg_frg.gravity.local_response import covariant_clock_response, flux_jacobian
    a0 = .7
    for g in (np.array([.06, -.08, .03]), np.array([.8, .4, -.3]), np.array([3., -4., 2.])):
        record = covariant_clock_response(g, a0=a0)
        h = 1e-5
        derivative = np.array([(covariant_clock_response(g+h*axis, a0=a0)['J']
                               -covariant_clock_response(g-h*axis, a0=a0)['J'])/(2*h)
                              for axis in np.eye(3)])
        np.testing.assert_allclose(derivative, record['gradient_J'], atol=3e-10, rtol=1e-8)
        np.testing.assert_allclose(g+derivative/2, flux(g, a0), atol=2e-10, rtol=1e-8)
        hessian = np.column_stack([(covariant_clock_response(g+h*axis, a0=a0)['gradient_J']
                                 -covariant_clock_response(g-h*axis, a0=a0)['gradient_J'])/(2*h)
                                for axis in np.eye(3)])
        np.testing.assert_allclose(np.eye(3)+hessian/2, flux_jacobian(g, a0), atol=3e-9)
    zero = covariant_clock_response(np.zeros(3), a0=a0)
    assert zero['J'] == 0 and zero['J_Y'] == -1
    np.testing.assert_array_equal(zero['gradient_J'], np.zeros(3))
    np.testing.assert_array_equal(zero['hessian_J'], -2*np.eye(3))


def test_covariant_clock_canonical_reduction_and_positive_physical_kinetics():
    from cg_frg.gravity.local_response import clock_dust_coefficients
    for H, rho, k in ((1., .3, 2.), (1., 3., 10.)):
        record = clock_dust_coefficients(H, rho, k)
        B, C, D = (record[key] for key in ('B','C','D'))
        a, P, pi, pidot, sigmadot = 1.7, .21, -.037, -.12, .46
        Q = a**3*C*(sigmadot-B*pi)
        original = P*(pidot-B*pi)-a**3*D*pi*pi/2+a**3*C*(sigmadot-B*pi)**2/2
        legendre = P*pidot+Q*sigmadot-original
        R, etadot = P+Q, sigmadot-pidot
        assert P*pidot+Q*sigmadot == pytest.approx(R*pidot+Q*etadot, abs=1e-12)
        split_hamiltonian = B*R*pi+a**3*D*pi*pi/2+Q*Q/(2*a**3*C)
        assert legendre == pytest.approx(split_hamiltonian, rel=2e-15)
        # Independent ADM constraint evaluation before lapse, shift and
        # the dust density multiplier have been removed.
        p, q = P/a**3, Q/a**3
        n, density_multiplier = B*pi, p
        shift = -(6*H*H*n+p+q)/(2*H)
        unreduced = (3*H*H*n*n+2*H*n*shift+(p+q)*n
                     +(p-density_multiplier)**2/(2*rho)+rho*k*k*pi*pi/2
                     -rho*shift*pi+q*q/(2*C))
        assert a**3*unreduced == pytest.approx(split_hamiltonian, rel=3e-15)
        assert 2*H*n-rho*pi == pytest.approx(0., abs=1e-16)
        assert 6*H*H*n+2*H*shift+p+q == pytest.approx(0., abs=1e-13)
        r, rdot = -.21, .37
        A = rdot+(3*H+B)*r
        stationary_pi = -A/D
        action = lambda potential: -A*potential-D*potential**2/2
        # The action is quadratic in pi, so this central difference is
        # exact in real arithmetic at any step and avoids cancellation.
        h = 1e-3
        assert (action(stationary_pi+h)-action(stationary_pi-h))/(2*h) == pytest.approx(0., abs=2e-10)
        assert action(stationary_pi) == pytest.approx(A*A/(2*D), rel=2e-15)
        assert np.all(record['physical_scalar_kinetic_eigenvalues'] > 0)
        assert record['clock_spatial_restoring_coefficient'] == 0.


def test_covariant_clock_conserved_charge_against_eds_exact_solution():
    from cg_frg.gravity.local_response import evolve_clock_dust_mode
    background = lambda t: (t**(2/3), 2/(3*t), 4/(3*t*t), -2/(3*t*t), -8/(3*t**3))
    times = np.linspace(1., 3., 25)
    p0, pi0, sigma0, k = -.01, .003, -.002, 4.
    for charge in (0., .007):
        actual = evolve_clock_dust_mode((p0, pi0, sigma0), times,
            background=background, comoving_wavenumber=k, charge=charge)
        coefficient = p0+4*pi0*k*k/5+8*pi0/3+charge
        p = coefficient*times**-3-4*pi0*k*k/5*times**(-4/3)-(8*pi0/3+charge)*times**-2
        sigma = sigma0+pi0*(times-1)+3*charge/(2*k*k)*(times**(1/3)-1)
        np.testing.assert_allclose(actual['p'], p, atol=4e-11)
        np.testing.assert_allclose(actual['dust_clock'], pi0*times, atol=3e-13)
        np.testing.assert_allclose(actual['foliation_clock'], sigma, atol=3e-13)
        np.testing.assert_allclose(actual['foliation_density']*actual['scale_factor']**3,
                                   charge, atol=2e-18)
        # The source seen by the metric is p+q/a^3. It equals an ordinary
        # Einstein dust mode with initial density momentum p0+q at a=1.
        effective_coefficient = p0+charge+4*pi0*k*k/5+8*pi0/3
        effective = effective_coefficient*times**-3-4*pi0*k*k/5*times**(-4/3)-8*pi0/3*times**-2
        np.testing.assert_allclose(actual['effective_cold_density_perturbation'], effective, atol=4e-11)
        assert np.all(actual['physical_kinetic_coefficients'] > 0)
        assert actual['zero_charge_branch'] == (charge == 0)
        assert max(actual['background_constraints'].values()) < 2e-15
        assert actual['operation_counts']['rhs_evaluations'] < 400
    with pytest.raises(ValueError, match='Einstein dust/vacuum'):
        evolve_clock_dust_mode((p0, pi0, sigma0), times,
            background=lambda t: (1., 1., 1., -.5, 0.), comoving_wavenumber=k)


def test_covariant_clock_dust_vacuum_background_and_effective_density():
    from cg_frg.gravity.local_response import evolve_clock_dust_mode, clock_dust_coefficients
    # Exact flat dust+Lambda solution: M_P^2=H_Lambda=1, rho_Lambda=3.
    def background(t):
        s = 1.5*t
        a, H, rho = np.sinh(s)**(2/3), 1/np.tanh(s), 3/np.sinh(s)**2
        return a, H, rho, -.5*rho, -3*H*rho
    times = np.linspace(.2, 1.6, 17)
    results = [evolve_clock_dust_mode((-.01, .003, -.002), times, background=background,
                comoving_wavenumber=4., charge=.007, rtol=rtol, atol=rtol*.01)
               for rtol in (1e-8, 1e-10)]
    np.testing.assert_allclose(results[0]['p'], results[1]['p'], atol=2e-9)
    np.testing.assert_allclose(results[0]['foliation_clock'], results[1]['foliation_clock'], atol=2e-10)
    assert np.all(results[1]['physical_kinetic_coefficients'] > 0)
    for t in times:
        a, H, rho, Hdot, rhodot = background(t)
        assert 3*H*H-rho == pytest.approx(3., abs=3e-14)
        for k in (.01, 1., 100.):
            coefficients = clock_dust_coefficients(H, rho, k/a)
            assert np.all(coefficients['physical_scalar_kinetic_eigenvalues'] > 0)
    # Equal effective initial density and velocity give equal metric
    # sources, independently of their conserved clock-charge partition.
    a_initial = background(times[0])[0]
    neutral = evolve_clock_dust_mode((-.01+.007/a_initial**3, .003, -.002), times,
        background=background, comoving_wavenumber=4., charge=0.)
    np.testing.assert_allclose(neutral['effective_cold_density_perturbation'],
        results[1]['effective_cold_density_perturbation'], atol=8e-11)
    np.testing.assert_allclose(neutral['lapse'], results[1]['lapse'], atol=4e-13)


def test_accelerated_clock_schur_complement_with_noncommuting_stiffnesses():
    from cg_frg.gravity.local_response import constrained_clock_kinetic
    D = np.array([[3., -1., 0.], [-1., 4., -1.], [0., -1., 2.]])
    L = np.array([[2., -.2, 0.], [-.2, 5., -.4], [0., -.4, 1.]])
    B = np.array([[1., .2], [.3, 1.], [-.4, .5]])
    M2 = 2.3
    result = constrained_clock_kinetic(D, L, B, planck_mass_squared=M2)
    # Compare the original two-field action after solving its constraint,
    # independently of the simplified D L^-1 D identity.
    for velocity in (np.array([.4, -.7]), np.array([-.2, .8])):
        v = B@velocity
        phi = np.linalg.solve(L, (L-D)@v)
        original = -M2*(phi@D@phi+(phi-v)@(L-D)@(phi-v))
        reduced = .5*velocity@result['kinetic_matrix']@velocity
        assert reduced == pytest.approx(original, rel=3e-14, abs=3e-14)
        np.testing.assert_allclose(result['potential_velocity_map']@velocity, phi, atol=2e-15)
    assert result['relative_constraint_residual'] < 1e-14


def test_clock_generated_coordinates_and_heat_preserve_finite_inertia():
    from cg_frg.gravity.local_response import constrained_clock_kinetic
    D = np.diag([1., 4., 9.])
    L = np.diag([.8, 1.1, .9])@D
    B = np.eye(3)
    base = constrained_clock_kinetic(D, L, B, planck_mass_squared=1.)
    for transform in (np.diag(np.exp(-.1*np.diag(D))),
                      np.array([[1., .3, .1], [0., 2., -.4], [.1, 0., 1.]])):
        result = constrained_clock_kinetic(D, L, B@transform, planck_mass_squared=1.)
        np.testing.assert_allclose(result['gradient_normalized_eigenvalues'],
            base['gradient_normalized_eigenvalues'], atol=2e-15)
        assert sum(np.linalg.eigvalsh(result['kinetic_matrix']) < 0) == 1


def test_accelerated_clock_threshold_and_generated_product_direction():
    from cg_frg.gravity.local_response import accelerated_clock_diagnostic, background_response
    result = accelerated_clock_diagnostic()
    y = result['parallel_threshold']
    assert y*y*(y*y+2)**2 == pytest.approx((1+y*y)**3, abs=2e-15)
    assert result['maximum_identity_residual'] < 2e-14
    sampled_minimum = min(row['normalized_kinetic_coefficient']/2 for row in result['samples'])
    assert sampled_minimum == pytest.approx(
        result['minimum_kinetic_over_twice_planck_gradient_metric'], abs=2e-15)
    assert not result['physical_kinetic_positive_all_accelerations']
    assert result['generation_mapping']['source_to_foliation_map'] is None
    H = background_response([1., 0., 0.])['principal_tensor']
    first, second = np.array([1., 1., 0.]), np.array([1., -1., 0.])
    assert first@H@first/(first@first) < 1
    assert second@H@second/(second@second) < 1
    longitudinal = first+second
    assert longitudinal@H@longitudinal/(longitudinal@longitudinal) > 1
    # A finite product retains the sum and difference frequencies.
    point = np.array([.31, -.7, 0.])
    assert np.cos(first@point)*np.cos(second@point) == pytest.approx(
        .5*(np.cos(longitudinal@point)+np.cos((first-second)@point)), abs=2e-16)


@pytest.mark.parametrize('D,L,B', [
    ([[1., 1.], [0., 1.]], np.eye(2), np.eye(2)),
    (np.eye(2), np.diag([1., 0.]), np.eye(2)),
    (np.eye(2), np.eye(2), [[1., 1.], [0., 0.]]),
    (np.eye(2), np.eye(2), [[np.nan], [0.]]),
])
def test_clock_kinetic_rejects_incompatible_constraints(D, L, B):
    from cg_frg.gravity.local_response import constrained_clock_kinetic
    with pytest.raises(ValueError):
        constrained_clock_kinetic(D, L, B, planck_mass_squared=1.)
