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

"""Independent identities and invariance checks for explicit matter extensions.

All boundary data below are declared mathematical test inputs. No production
parameter store, experimental coupling or observed neutron lifetime is read.
"""
import math

import numpy as np
import pytest

from cg_core.content_response import (
    chiral_center_power_law_screening, chiral_center_response,
    closed_chiral_center_certificate, closed_generated_world_contract,
    finite_source_response, interacting_content_response,
    log_partition_response, weighted_content_response,
)
from cg_core.matter_matching import (
    spatial_vertex, kinetic_gram, canonical_vertex, axial_squash_grams,
    qcd_mass_matching_one_loop, electroweak_matching_one_loop,
    electroweak_matching_from_fermi_readout,
    top_higgs_pole_matching_one_loop, generated_on_shell_matter_matching,
    charged_lepton_pole_matching_one_loop,
)
from cg_core.gauge_running import (
    CoupledBoundary, RGThreshold, coupled_run, coupled_boundary_residual,
)
from cg_core.beta_functions import derivatives5
from cg_frg.ewsb.native_condensate import (
    canonical_radial_curvature, source_visible_resolvent,
)
from cg_frg.qcd.mass_gap_scale import apply_finite_content_matching, run_qcd_thresholds
from cg_frg.qcd.qcd_sector import (constituent_proton_readout, matched_isovector_split,
    matched_nucleon_masses, native_nucleon_readout, three_quark_source_certificate)
from cg_frg.cosmology.bbn_helium import (
    helium_yield, matched_neutron_proton_split, beta_phase_space, bbn_joint_response,
    weak_mass_difference_ranges,
)
from cg_frg.cosmology.thermal_weak import (
    WeakInputs, weak_rates, zero_temperature_lifetime, photon_electron_eos,
    evolve_neutron_fraction, thermal_history_bath, HBAR_GEV_S,
)
from cg_frg.cosmology.reaction_network import Nuclide, NuclearReaction, ReactionNetwork, WeakConversion
from cg_frg.ewsb.pseudo_dilaton import canonical_potential_vertices


def test_lepton_matching_analytic_intervals_against_independent_integrals():
    import mpmath as mp
    masses = {'electron': .0004, 'muon': .12, 'tau': 1.6}
    g1, g, v, mh, scale = .47, .63, 241., 127., 89.
    result = charged_lepton_pole_matching_one_loop(masses, (g1, g), v,
        higgs_mass_GeV=mh, scale_GeV=scale,
        input_definition='generated_on_shell_conditions', action_source='test action')
    with mp.workdps(70):
        gp2, g2 = 3*mp.mpf(g1)**2/5, mp.mpf(g)**2
        total, v2, q2 = gp2+g2, mp.mpf(v)**2, mp.mpf(scale)**2
        W, Z, h = g2*v2/4, total*v2/4, mp.mpf(mh)**2
        A = lambda x: x*(mp.log(x/q2)-1)
        def B(x, y, t):
            return -mp.quad(lambda u: mp.log((u*x+(1-u)*y-u*(1-u)*t)/q2),
                            [0, mp.mpf('.5'), mp.mpf('.99'), 1])
        for name, mass in masses.items():
            t = mp.mpf(mass)**2
            bw, bz, bh = B(0, W, t), B(t, Z, t), B(t, h, t)
            squared = {
                'photon': g2*gp2/total*t*(8-6*mp.log(t/q2)),
                'W': g2/4*((2*W-t-t*t/W)*bw+(2*W-t)*A(W)/W+2*t),
                'Z_chiral': (total/4-gp2+2*gp2**2/total)*((Z-t)*bz+A(Z)-A(t)+t),
                'Z_mass': -2*gp2*(mp.mpf('.5')-gp2/total)*t*(3*bz-2),
                'Higgs': t/v2*((h-4*t)*bh+A(h)-2*A(t)),
            }
            for component, value in squared.items():
                expected = -value/(32*mp.pi**2*t)
                low, high = result['log_matching_component_intervals'][name][component]
                assert mp.mpf(low) <= expected <= mp.mpf(high)
    assert result['evaluation_work']['quadrature_integrand_evaluations'] == 0


def test_lepton_matching_weighted_qed_and_light_threshold_limits():
    from cg_core.joint_response import charged_lepton_qed_log_matching
    masses = {'electron': .0003, 'muon': .0006, 'tau': .0012}
    g1, g, v, mh, scale = .46, .65, 247., 124., 93.
    result = charged_lepton_pole_matching_one_loop(masses, (g1, g), v,
        higgs_mass_GeV=mh, scale_GeV=scale,
        input_definition='generated_on_shell_conditions', action_source='test action')
    qed = charged_lepton_qed_log_matching(masses, scale_GeV=scale,
                                        alpha=result['alpha_same_action'])
    assert result['weighted_log_components']['photon'] == pytest.approx(
        qed['matching_log_correction'], abs=2e-17)
    # Martin (2019), Sec. II.C (arXiv HTML Eq. (2.23)): the light-lepton threshold
    # is universal, theta=(9g²+3g'²)/16+g'²(W/Z-1/2)(3ln(Z/Q²)-5/2).
    gp2, g2 = 3*g1*g1/5, g*g
    W, Z = g2*v*v/4, (g2+gp2)*v*v/4
    theta = (9*g2+3*gp2)/16+gp2*(W/Z-.5)*(3*math.log(Z/scale**2)-2.5)
    for name in masses:
        terms = result['log_matching_components'][name]
        weak = sum(value for key, value in terms.items() if key != 'photon')
        assert weak == pytest.approx(-theta/(16*math.pi**2), abs=5e-12)
    assert abs(result['finite_weak_log_correction']) < 5e-12
    assert result['common_vev_log_weight'] == 0


def test_lepton_matching_scale_derivative_and_common_units():
    masses = {'electron': .002, 'muon': .2, 'tau': 2.}
    args = dict(gauge_couplings=(.45, .66), vev_GeV=245.,
                higgs_mass_GeV=126., input_definition='generated_on_shell_conditions',
                action_source='test action')
    result = charged_lepton_pole_matching_one_loop(masses, scale_GeV=90., **args)
    step = .02
    up = charged_lepton_pole_matching_one_loop(masses, scale_GeV=90*math.exp(step), **args)
    down = charged_lepton_pole_matching_one_loop(masses, scale_GeV=90*math.exp(-step), **args)
    derivative = (up['charged_lepton_log_correction']-down['charged_lepton_log_correction'])/(2*step)
    weighted_y2 = 2*(2*masses['muon']**2-masses['electron']**2-masses['tau']**2)/245**2
    assert derivative == pytest.approx(1.5*weighted_y2/(16*math.pi**2), rel=2e-11)
    ratio = 1e4
    scaled = charged_lepton_pole_matching_one_loop(
        {k: ratio*m for k, m in masses.items()}, args['gauge_couplings'], ratio*245.,
        higgs_mass_GeV=ratio*126., scale_GeV=ratio*90.,
        input_definition='generated_on_shell_conditions', action_source='scaled test action')
    assert scaled['charged_lepton_log_correction'] == pytest.approx(result['charged_lepton_log_correction'], rel=2e-15)
    with pytest.raises(ValueError, match='generated_on_shell_conditions'):
        charged_lepton_pole_matching_one_loop(masses, (.45, .66), 245.,
            higgs_mass_GeV=126., scale_GeV=90., input_definition='geometric', action_source='test')


def test_noncommuting_response_against_closed_two_level_partition():
    # log Tr exp(k sigma_z+j sigma_x)/2 = log cosh(sqrt(k²+j²)).
    k=2.3
    K=np.diag([k,-k]); X=np.array([[0,1],[1,0]])
    result=log_partition_response(K,[X])
    assert result['hessian'][0,0]==pytest.approx(math.tanh(k)/k,rel=2e-14)
    assert abs(result['hessian'][0,0]-1)>0.5  # naive covariance is not Duhamel
    j=.31
    value=log_partition_response(K,[X],[j])
    radius=math.hypot(k,j)
    assert value['log_partition']==pytest.approx(math.log(math.cosh(radius)))
    assert value['gradient'][0]==pytest.approx(math.tanh(radius)*j/radius)


def test_content_hessian_zero_common_and_unequal_weights():
    exact=finite_source_response()
    actual=interacting_content_response()
    assert np.allclose(actual['hessian'],np.array(exact['hessian'],dtype=float),rtol=1e-13,atol=1e-14)
    assert actual['tau_response']==pytest.approx(1/50,rel=1e-14)
    common=weighted_content_response(1e150,1e150)
    assert np.allclose(common['hessian'],actual['hessian'],atol=1e-14)
    assert common['tau_response']==pytest.approx(1/50,rel=1e-14)
    r=1.17
    changed=weighted_content_response(r,1)
    assert changed['tau_response']==pytest.approx((8*r-7)/(10*r+40),rel=2e-14)
    assert np.linalg.eigvalsh(changed['hessian']).min()>-1e-13


def test_complete_and_quotient_chiral_center_responses():
    complete = chiral_center_response()
    assert complete['left_capacity'] == 8
    assert complete['right_capacity'] == 8
    assert complete['bias'] == 0
    assert complete['susceptibility'] == 1
    assert complete['restoring_hessian'] == 1
    assert not complete['elimination_feedback_required']
    assert not complete['external_source_required']

    quotient = chiral_center_response(neutral_right_weight=0)
    exact = finite_source_response()
    assert quotient['right_capacity'] == 7
    assert quotient['bias'] == pytest.approx(1/15, abs=2e-16)
    assert quotient['susceptibility'] == pytest.approx(224/225, abs=2e-16)
    assert quotient['restoring_hessian'] == pytest.approx(225/224, abs=2e-16)
    assert quotient['bias'] == pytest.approx(float(exact['gradient'][0]))
    assert quotient['susceptibility'] == pytest.approx(float(exact['hessian'][0][0]))
    assert quotient['removed_coordinate'] == 'nu_R'
    assert quotient['elimination_feedback_required']

    closed = closed_chiral_center_certificate()
    assert closed['complete_dimension'] == 16
    assert closed['partition_even']
    assert closed['closed_center_bias'] == 0
    assert closed['closed_center_susceptibility'] == 1
    assert closed['closed_restoring_hessian'] == 1
    assert not closed['external_source_required']
    assert closed['quotient_dimension'] == 15
    assert closed['quotient_bias'] == pytest.approx(1/15, abs=2e-16)
    assert closed['quotient_is_projection_defect']
    assert closed['removed_coordinate'] == 'nu_R'

    world = closed_generated_world_contract()
    assert world['sole_root'] == 'minimal_unbiased_compositional_change'
    assert world['root_argument_count'] == 0
    assert world['complete_matter_capacity'] == 16
    assert world['complete_capacity_balanced']
    assert world['charged_quotient_is_internal_projection']
    assert world['applied_probes_are_response_coordinates']
    assert world['subsystem_boundaries_are_internal_complements']
    assert not world['comparison_data_are_dynamical_sources']
    assert not world['external_dynamical_source_required']


def test_center_drive_derivative_and_scale_screening():
    drive = 0.37
    step = 1e-6
    middle = chiral_center_response(drive)
    derivative = (
        chiral_center_response(drive + step)['bias']
        - chiral_center_response(drive - step)['bias']
    ) / (2 * step)
    # The source argument is log(wL/wR)=2h, hence dm/dlog(r)=chi/2.
    assert derivative == pytest.approx(middle['susceptibility']/2, rel=2e-10)

    full = chiral_center_power_law_screening(.4, .3)
    assert full['infinite_scale_restoration']
    assert full['energy_upper_bound'] == pytest.approx(.4**2/(2*.3))
    assert not full['closure_input']

    quotient = chiral_center_power_law_screening(
        0, .3, neutral_right_weight=0
    )
    assert math.isinf(quotient['energy_upper_bound'])
    assert quotient['persistent_projection_defect']

    finite = chiral_center_power_law_screening(
        0, .3, scale_ratio=32, neutral_right_weight=0
    )
    assert finite['zero_drive_exact_energy'] == pytest.approx(math.log(32)/225)
    assert finite['energy_upper_bound'] == pytest.approx(math.log(32)/225)


def test_actual_overlap_and_general_basis_covariance():
    x,w=np.polynomial.legendre.leggauss(16)
    modes=np.stack((np.ones_like(x),math.sqrt(3)*x),axis=1)[:,:,None]
    G=kinetic_gram(modes,w/2)
    Y=spatial_vertex(modes,modes,x[:,None,None],w/2)
    assert np.allclose(G,np.eye(2),atol=1e-14)
    assert np.allclose(Y,[[0,1/math.sqrt(3)],[1/math.sqrt(3),0]],atol=1e-14)
    S=np.array([[2,1j],[.3,1.1]],dtype=complex)
    T=np.array([[.8,.2],[-.1j,1.7]],dtype=complex)
    L=np.einsum('qia,ij->qja',modes,S)
    R=np.einsum('qia,ij->qja',modes,T)
    transformed=canonical_vertex(spatial_vertex(L,R,x[:,None,None],w/2),
                                 kinetic_gram(L,w/2),kinetic_gram(R,w/2),1)
    assert np.allclose(np.linalg.svd(transformed,compute_uv=False),
                       np.linalg.svd(Y,compute_uv=False),rtol=2e-13)
    assert not np.allclose(transformed,Y)
    with pytest.raises(ValueError,match='positive definite'):
        canonical_vertex(Y,[[1,1],[1,1]],G,1)


def test_internal_curvature_and_external_kinetic_gram_are_distinct():
    s=.08; A,B=1+s,1-2*s
    grams=axial_squash_grams(s)
    assert grams['curvature_gram_ratio']==pytest.approx(B**2.5/A,rel=2e-14)
    assert grams['oneform_gram_ratio']==pytest.approx(A*B**1.5,rel=2e-14)
    assert grams['curvature_gram_ratio']!=pytest.approx(grams['oneform_gram_ratio'])


def test_coupled_actual_beta_semigroup_and_boundary_residual():
    boundary=CoupledBoundary((.48,.53,.61,.7,.12),1e8,'MSbar','explicit test action boundary')
    direct=coupled_run(boundary,1e6)
    half=coupled_run(boundary,1e7)
    twice=coupled_run(CoupledBoundary(half['couplings'],1e7,'MSbar',boundary.source),1e6)
    assert np.allclose(direct['couplings'],twice['couplings'],rtol=3e-10)
    tiny=coupled_run(boundary,boundary.scale*math.exp(1e-5))
    derivative=(np.array(tiny['couplings'])-boundary.values)/1e-5
    assert np.allclose(derivative,derivatives5(boundary.values),rtol=2e-6,atol=1e-9)
    assert direct['couplings'][3]!=pytest.approx(boundary.values[3],rel=1e-4)
    residual=coupled_boundary_residual(boundary,1e6,lambda y,mu,scheme:y[0]-y[1])
    assert residual['residual']==pytest.approx(direct['couplings'][0]-direct['couplings'][1])


def test_directional_threshold_and_negative_quartic_are_not_silently_erased():
    boundary=CoupledBoundary((.4,.5,.6,.7,.1),100,'test-scheme','test equation')
    rhs=lambda y:[0,0,0,0,.1]
    threshold=RGThreshold(10,lambda y:(*y[:4],y[4]+.02),rhs,'test-scheme','explicit finite threshold','down')
    result=coupled_run(boundary,1,initial_beta=rhs,thresholds=(threshold,))
    assert result['couplings'][4]==pytest.approx(.1+.1*math.log(.01)+.02)
    assert result['negative_quartic_encountered']
    with pytest.raises(ValueError,match='scheme'):
        coupled_run(boundary,1)
    with pytest.raises(ValueError,match='direction'):
        coupled_run(boundary,1000,initial_beta=rhs,thresholds=(threshold,))
    with pytest.raises(ValueError,match='coupled flow'):
        apply_finite_content_matching(.1,.04,flow_convention='coupled-top-sector')


def test_qcd_threshold_is_real_content_change():
    result=run_qcd_thresholds(.08,1000,10,n_flavours=6,heavy_thresholds=(100,))
    assert [s['n_flavours'] for s in result['segments']]==[6,5]
    assert result['alpha_s']>.08
    assert result['matching_order']==1
    assert not result['finite_fixed_y0_compensation_applied']


def test_qcd_finite_mass_matching_from_self_energy_integral():
    from scipy.integrate import quad
    mass, scale, alpha = 150., 210., .1
    coefficient = quad(lambda x: (2+2*x)*math.log(scale**2/(mass*x)**2)-2*x,
                       0, 1, epsabs=1e-12, epsrel=1e-12)[0]
    result = qcd_mass_matching_one_loop(mass, alpha, scale_GeV=scale,
        input_definition='MSbar', boundary_source='declared test QCD action mass')
    assert result['self_energy_finite_coefficient'] == pytest.approx(coefficient, rel=2e-14)
    assert result['matched_mass_GeV'] == pytest.approx(
        mass*(1+(4/3)*alpha/(4*math.pi)*coefficient), rel=2e-14)
    selfscale = qcd_mass_matching_one_loop(mass, alpha, scale_GeV=mass,
        input_definition='MSbar', boundary_source='declared test QCD action mass')
    assert selfscale['relative_one_loop_term'] == pytest.approx(4*alpha/(3*math.pi))
    assert not selfscale['finite_vev_and_electroweak_matching_included']


def test_qcd_mass_matching_order_and_renormalization_group_cancellation():
    mass, scale, alpha = 150., 150., 1e-5
    def convert(m, mu, definition='MSbar'):
        return qcd_mass_matching_one_loop(m, alpha, scale_GeV=mu,
            input_definition=definition, boundary_source='declared perturbative test')
    pole = convert(mass, scale)['matched_mass_GeV']
    back = convert(pole, scale, 'pole')['matched_mass_GeV']
    assert abs(back/mass-1) < alpha**2
    # d log m / d log mu = -6 CF alpha_s/(4 pi) cancels the finite log.
    step = 1e-4
    running_mass = mass*math.exp(-2*alpha/math.pi*step)
    shifted = convert(running_mass, scale*math.exp(step))['matched_mass_GeV']
    assert abs((shifted-pole)/(mass*step)) < alpha**2
    with pytest.raises(ValueError, match='input_definition'):
        convert(mass, scale, 'geometric')
    with pytest.raises(ValueError, match='identification'):
        qcd_mass_matching_one_loop(mass, alpha, scale_GeV=scale,
                                  input_definition='MSbar', boundary_source='')


def test_condensate_hessian_and_source_coordinate_invariance():
    E=.7; h=1e-5
    settings=dict(g=.8,Z=1.3,L=2.5)
    middle=canonical_radial_curvature(amplitude=E,**settings)
    plus=canonical_radial_curvature(amplitude=E+h,**settings)
    minus=canonical_radial_curvature(amplitude=E-h,**settings)
    derivative=(plus['potential_gradient']-minus['potential_gradient'])/(2*h)
    assert middle['potential_second_derivative']==pytest.approx(derivative,rel=2e-9)
    source={0:[0],2:[1,2j,0,0,0,0,0,0,0]}
    args=dict(mass_squared=.4,L=2.5,length_unit=.2)
    response=source_visible_resolvent(.6,shell_coefficients=source,source_Z=2,**args)
    a=3.4
    transformed={l:np.array(c)/a for l,c in source.items()}
    same=source_visible_resolvent(.6,shell_coefficients=transformed,source_Z=2/a**2,**args)
    assert same['response']==pytest.approx(response['response'],rel=2e-14)
    assert response['lowest_visible_mass_squared']==pytest.approx((8/2.5**2+.4)/.2**2)
    with pytest.raises(ValueError,match='degeneracy'):
        source_visible_resolvent(.6,shell_coefficients={2:[1]},**args)


@pytest.fixture
def weak_inputs():
    return WeakInputs(1e-5,.97,1.2,.0005,.00125,.007,1.03,'specified mathematical test inputs')


def test_thermal_detailed_balance_and_zero_temperature_decay(weak_inputs):
    inputs=weak_inputs
    for T in (.0002,.0007,.002):
        mue,munu=1e-5,-2e-5
        rates=weak_rates(inputs,T,electron_chemical_potential=mue,neutrino_chemical_potential=munu)
        assert rates['p_to_n']/rates['n_to_p']==pytest.approx(
            math.exp(-(inputs.neutron_proton_split-mue+munu)/T),rel=2e-7)
    rates=weak_rates(inputs,0)
    assert rates['p_to_n']==0
    assert rates['n_to_p']==pytest.approx(1/zero_temperature_lifetime(inputs),rel=1e-14)
    assert rates['channels']['capture_n_to_p']==0


def test_born_decay_against_analytic_phase_space(weak_inputs):
    original=weak_inputs
    inputs=WeakInputs(original.G_F,original.V_ud,original.g_A,original.electron_mass,
                      original.neutron_proton_split,0,1,original.source)
    d=inputs.neutron_proton_split/inputs.electron_mass
    phase=math.sqrt(d*d-1)*(2*d**4-9*d*d-8)/60+d/4*math.acosh(d)
    rate=inputs.G_F**2*inputs.V_ud**2*(1+3*inputs.g_A**2)*inputs.electron_mass**5*phase/(2*math.pi**3*HBAR_GEV_S)
    assert weak_rates(inputs,0)['n_to_p']==pytest.approx(rate,rel=3e-10)


def test_decay_phase_space_regular_quadrature_and_threshold():
    from cg_frg.cosmology.bbn_helium import beta_phase_space
    import mpmath as mp
    # Direct high-precision Coulomb integral in electron energy, independent
    # of the normalized Gauss-Kronrod production variable and endpoint limit.
    for splitting_ratio, alpha in ((2.5, .0073), (1.0001, .02), (4., 0.)):
        actual = beta_phase_space(splitting_ratio, 1., alpha)
        with mp.workdps(55):
            end, charge = mp.mpf(splitting_ratio), mp.mpf(alpha)
            def kernel(w):
                if w == 1:
                    return 2*mp.pi*charge*(end-1)**2
                momentum = mp.sqrt(w*w-1)
                phase = w*momentum
                if charge:
                    eta = 2*mp.pi*charge*w/momentum
                    phase *= eta/(-mp.expm1(-eta))
                return phase*(end-w)**2
            reference = float(mp.quad(kernel, [1, (1+end)/2, end]))
        assert actual['value'] == pytest.approx(reference, rel=3e-12, abs=1e-28)
        assert actual['estimated_abs_error'] >= 0
        assert actual['integrand_evaluations'] < 3000
    assert beta_phase_space(.5, 1., .007)['value'] == 0
    assert beta_phase_space(1., 1., .007)['integrand_evaluations'] == 0
    with pytest.raises(ValueError):
        beta_phase_space(2., 1., -.007)


def test_beta_phase_space_derivatives_against_analytic_born_integral():
    import mpmath as mp
    q = 2.4
    result = beta_phase_space(q, 1., 0., include_derivatives=True)
    with mp.workdps(50):
        def born(x):
            return mp.sqrt(x*x-1)*(2*x**4-9*x*x-8)/60+x*mp.acosh(x)/4
        expected_derivative = float(mp.diff(born, mp.mpf(str(q))))
    alpha_derivative = math.pi*(q**5/30-q*q/3+q/2-1/5)
    assert result['derivative_splitting_ratio'] == pytest.approx(expected_derivative, rel=2e-12)
    assert result['derivative_alpha_em'] == pytest.approx(alpha_derivative, rel=2e-12)
    assert result['integrand_evaluations'] > 0


def _bbn_independent_inputs():
    return dict(m_down=.0047, m_up=.0022, scalar_isovector_matrix_element=1.02,
                electromagnetic_split=.0012, G_F=1.17e-5, V_ud=.976, g_A=1.27,
                rate_multiplier=1.04, electron_mass=.000511, alpha_em=.0073,
                reduced_planck_mass=2.43e18, freeze_rate_multiplier=1.)


@pytest.fixture(scope="module")
def joint_bbn_response():
    """Share the production centre and derivatives; comparisons stay independent."""
    return bbn_joint_response(**_bbn_independent_inputs())


def _independent_instantaneous_bbn(values):
    from scipy.integrate import quad
    from scipy.optimize import brentq
    d = values['scalar_isovector_matrix_element']*(values['m_down']-values['m_up'])-values['electromagnetic_split']
    me, alpha = values['electron_mass'], values['alpha_em']
    end = d/me
    def phase_integrand(w):
        momentum = math.sqrt(w*w-1)
        coulomb = 2*math.pi*alpha*w/momentum
        return w*momentum*coulomb/(-math.expm1(-coulomb))*(end-w)**2
    phase = quad(phase_integrand, 1., end, epsabs=2e-12, epsrel=2e-12)[0]
    strength = values['G_F']**2*(1+3*values['g_A']**2)
    lifetime = 2*math.pi**3*HBAR_GEV_S/(strength*values['V_ud']**2*
                   values['rate_multiplier']*me**5*phase)
    full_planck = math.sqrt(8*math.pi)*values['reduced_planck_mass']
    coefficient = math.sqrt(4*math.pi**3*10.75/45)/full_planck
    temperature = brentq(lambda t: 7*math.pi/60*strength*values['freeze_rate_multiplier']*
                        (t**3+1.5*d*t*t)-coefficient, 1e-5, .01, xtol=1e-17)
    interval = .301*full_planck*HBAR_GEV_S*(1/(math.sqrt(3.36)*.00008**2)-
                                           1/(math.sqrt(10.75)*temperature**2))
    helium = 2/(math.exp(d/temperature)+1)*math.exp(-interval/lifetime)
    return np.array([d, lifetime, temperature, interval, helium])


def test_joint_bbn_jacobian_matches_independent_full_chain_differences(joint_bbn_response):
    values = _bbn_independent_inputs()
    response = joint_bbn_response
    central = np.array([response['values'][key] for key in response['output_order']])
    np.testing.assert_allclose(central, _independent_instantaneous_bbn(values), rtol=3e-12)
    jacobian = np.array(response['jacobian'])
    # Each difference recomputes the original integral, implicit freeze
    # equation and conserved capture formula, not the derivative routines.
    for column, name in enumerate(response['input_order']):
        step = values[name]*1e-5
        plus = _independent_instantaneous_bbn({**values, name: values[name]+step})
        minus = _independent_instantaneous_bbn({**values, name: values[name]-step})
        measured = (plus-minus)/(2*step)
        scale = np.maximum(np.abs(jacobian[:, column]), np.abs(central/values[name]))
        np.testing.assert_allclose(measured/scale, jacobian[:, column]/scale,
                                   rtol=3e-7, atol=3e-9)
    assert not response['uncertainty_model_supplied']
    np.testing.assert_allclose(np.array(response['logarithmic_derivatives']),
        jacobian*np.array(list(response['inputs'].values()))[None, :]/central[:, None], rtol=2e-15)


def test_joint_bbn_shared_mass_matching_and_rate_directions(joint_bbn_response):
    response = joint_bbn_response
    J = np.array(response['jacobian'])
    names = response['input_order']
    g_column, em_column = names.index('scalar_isovector_matrix_element'), names.index('electromagnetic_split')
    difference = response['inputs']['m_down']-response['inputs']['m_up']
    # These changes preserve the common nucleon splitting exactly. Every
    # downstream first derivative must vanish in their joint direction.
    np.testing.assert_allclose(J[:, g_column]+difference*J[:, em_column], 0., atol=2e-12)
    elasticities = np.array(response['logarithmic_derivatives'])
    rate_column = names.index('rate_multiplier')
    freeze_column = names.index('freeze_rate_multiplier')
    assert elasticities[1, rate_column] == pytest.approx(-1., abs=2e-15)
    assert elasticities[2, rate_column] == 0
    assert elasticities[1, freeze_column] == 0
    assert elasticities[4, rate_column] == pytest.approx(
        -response['values']['t_decay']/response['values']['tau_n'], rel=2e-14)
    with pytest.raises(ValueError, match='Delta_np'):
        bbn_joint_response(**{**_bbn_independent_inputs(), 'electromagnetic_split': .0024})


def test_finite_mass_gap_ranges_contain_independent_weak_chain():
    inputs = _bbn_independent_inputs()
    weak = {key: value for key, value in inputs.items() if key not in {
        'm_down', 'm_up', 'scalar_isovector_matrix_element', 'electromagnetic_split'}}
    central, stat, systematic = .0016, .00013, .00021
    result = weak_mass_difference_ranges(central_split=central,
        statistical_error=stat, systematic_error=systematic, **weak)
    for interval in result['ranges'].values():
        # Recompute in the independent original-energy phase variable and
        # with a separate root solver; no derivative routine supplies values.
        for splitting in np.linspace(*interval['input_split_GeV'], 9):
            displaced = dict(inputs, m_down=inputs['m_up']+
                (splitting+inputs['electromagnetic_split'])/
                inputs['scalar_isovector_matrix_element'])
            expected = _independent_instantaneous_bbn(displaced)
            for key, value in zip(('dm_np', 'tau_n', 'T_f', 't_decay', 'Y_p'), expected):
                lower, upper = interval['output_ranges'][key]
                assert lower-abs(value)*2e-11 <= value <= upper+abs(value)*2e-11
    assert not result['production_parameters_updated']
    assert not result['physical_approximation_error_quantified']
    assert result['operation_counts']['unique_weak_chains'] == 7
    assert result['operation_counts']['derivative_quadratures'] == 0


def test_finite_mass_gap_range_reuses_duplicate_endpoints(monkeypatch):
    import cg_frg.cosmology.bbn_helium as module
    inputs = _bbn_independent_inputs()
    weak = {key: value for key, value in inputs.items() if key not in {
        'm_down', 'm_up', 'scalar_isovector_matrix_element', 'electromagnetic_split'}}
    original = module.instantaneous_weak_chain
    evaluated = []
    def count_chain(**kwargs):
        evaluated.append(kwargs['neutron_proton_split'])
        return original(**kwargs)
    monkeypatch.setattr(module, 'instantaneous_weak_chain', count_chain)
    result = weak_mass_difference_ranges(central_split=.0016,
        statistical_error=.0001, systematic_error=.0001, **weak)
    assert len(evaluated) == len(set(evaluated)) == 5
    assert result['operation_counts']['phase_space_quadratures'] == 5
    assert result['ranges']['statistical'] == result['ranges']['systematic']
    point = weak_mass_difference_ranges(central_split=.0016,
        statistical_error=0., systematic_error=0., **weak)
    assert point['operation_counts']['phase_space_quadratures'] == 1
    for key, value in point['central_chain']['values'].items():
        assert point['ranges']['additive_envelope']['output_ranges'][key] == pytest.approx([value, value])
    for stat, systematic in ((-.0001, .0001), (.0008, .0003)):
        with pytest.raises(ValueError):
            weak_mass_difference_ranges(central_split=.0016,
                statistical_error=stat, systematic_error=systematic, **weak)


def test_joint_bbn_retains_scalar_centre_and_reuses_its_partition(joint_bbn_response):
    values = _bbn_independent_inputs()
    response = joint_bbn_response
    dm = values['scalar_isovector_matrix_element']*(values['m_down']-values['m_up'])-values['electromagnetic_split']
    scalar = beta_phase_space(dm, values['electron_mass'], values['alpha_em'])
    assert response['phase_space']['value'] == scalar['value']
    assert response['phase_space']['estimated_abs_error'] == scalar['estimated_abs_error']
    lifetime = 2.0*math.pi**3/(values['G_F']**2*values['V_ud']**2*
        (1.0+3.0*values['g_A']**2)*values['electron_mass']**5*scalar['value']*values['rate_multiplier'])
    lifetime *= HBAR_GEV_S
    assert response['values']['tau_n'] == lifetime
    full_planck = math.sqrt(8.0*math.pi)*values['reduced_planck_mass']
    temperature = response['values']['T_f']
    interval = (.301*full_planck/math.sqrt(3.36)/.00008**2-
                .301*full_planck/math.sqrt(10.75)/temperature**2)*HBAR_GEV_S
    assert response['values']['t_decay'] == interval
    assert response['values']['Y_p'] == helium_yield(temperature, dm, interval, lifetime)['Y_p']
    work = response['operation_counts']
    assert work['phase_space_quadratures'] == 1
    assert work['center_integrand_evaluations'] == scalar['integrand_evaluations']
    assert work['reused_center_subintervals'] > 0
    assert work['derivative_integrand_evaluations'] == 36*work['derivative_interval_evaluations']
    assert work['phase_space_integrand_evaluations'] == (
        work['center_integrand_evaluations']+work['derivative_integrand_evaluations'])


@pytest.mark.numerical
def test_observed_gap_diagnostic_propagates_one_gap_without_changing_inputs(
        joint_bbn_response, monkeypatch):
    from copy import deepcopy
    from comparison.sm_rge import inputs as references
    baseline = joint_bbn_response
    saved = deepcopy(baseline)
    dm = baseline['values']['dm_np']*1.0064
    sigma = 4e-10
    targets = dict(dm_np_obs_GeV=dm, dm_np_obs_sigma_GeV=sigma,
                   tau_n_obs=880., tau_n_obs_sigma=.5, Y_p_obs=.245)
    targets['nucleon_qcd_qed_lattice'] = {
        'total': {'central': dm*1.03, 'statistical': 4e-6, 'systematic': 8e-6},
        'scope': 'independent mathematical comparison inputs'}
    accessed = []
    def reference_value(key):
        accessed.append(key)
        return targets[key]
    monkeypatch.setattr(references, 'sm_value', reference_value)
    comparison = references.neutron_helium_benchmark(
        {'bbn_'+key: baseline['values'][key] for key in ('dm_np', 'tau_n')}
        | {'bbn_Yp': baseline['values']['Y_p']}, generated_joint_response=baseline)
    diagnostic = comparison['mass_gap_substitution']
    independent = dict(baseline['inputs'])
    # The independent reference uses an equivalent algebraic parameterization
    # of the imposed gap, retaining every weak and thermal coefficient.
    independent['m_down'] += (dm-baseline['values']['dm_np'])/independent['scalar_isovector_matrix_element']
    expected = _independent_instantaneous_bbn(independent)
    actual = np.array([diagnostic['conditional_values'][key] for key in baseline['output_order']])
    np.testing.assert_allclose(actual, expected, rtol=3e-12)
    assert baseline == saved
    assert set(accessed) == set(targets)
    lattice = comparison['independent_lattice_matching']
    assert lattice['generated_values'] == baseline['values']
    assert not lattice['production_parameters_updated']
    assert lattice['weak_chain']['central_split_GeV'] == targets['nucleon_qcd_qed_lattice']['total']['central']
    assert not diagnostic['production_parameters_updated']
    assert not diagnostic['strong_and_electromagnetic_terms_fitted']
    assert diagnostic['operation_counts']['additional_phase_space_quadratures'] == 1
    assert not diagnostic['numerical_error_estimates']['rigorous_interval_bound']
    assert not diagnostic['physical_approximation_uncertainty']['quantified']
    assert diagnostic['conditional_values']['T_f'] != baseline['values']['T_f']
    assert diagnostic['conditional_values']['t_decay'] != baseline['values']['t_decay']
    step = dm*1e-5
    plus, minus = dict(independent), dict(independent)
    plus['m_down'] += step/independent['scalar_isovector_matrix_element']
    minus['m_down'] -= step/independent['scalar_isovector_matrix_element']
    measured = (_independent_instantaneous_bbn(plus)-
                _independent_instantaneous_bbn(minus))/(2*step)
    uncertainties = diagnostic['reference_mass_gap_uncertainty']['propagated_standard_uncertainties']
    np.testing.assert_allclose([uncertainties[key] for key in baseline['output_order']],
                               np.abs(measured)*sigma, rtol=2e-7)


def test_observed_gap_diagnostic_obeys_prediction_input_guard(joint_bbn_response):
    from cg_core.params import prediction_inputs_only
    from comparison.sm_rge.inputs import neutron_helium_benchmark
    values = joint_bbn_response['values']
    with prediction_inputs_only(), pytest.raises(ValueError, match='reference-data access'):
        neutron_helium_benchmark({'bbn_dm_np': values['dm_np'],
            'bbn_tau_n': values['tau_n'], 'bbn_Yp': values['Y_p']},
            generated_joint_response=joint_bbn_response)


def test_complete_capture_from_independent_conserved_neutron_proton_evolution():
    from scipy.integrate import solve_ivp
    temperature, splitting, interval, lifetime = .00076, .00127, 210., 920.
    ratio = math.exp(-splitting/temperature)
    # The two populations share a conserved total. This independent ODE
    # does not integrate the production X_n formula itself.
    initial = np.array([3*ratio, 3.])
    solution = solve_ivp(lambda t, populations:
        [-populations[0]/lifetime, populations[0]/lifetime],
        (0., interval), initial, method='DOP853', rtol=1e-12, atol=1e-14)
    assert solution.success
    total = initial.sum()
    np.testing.assert_allclose(solution.y.sum(axis=0), total, atol=2e-14)
    actual = helium_yield(temperature, splitting, interval, lifetime)
    assert actual['Y_p'] == pytest.approx(2*solution.y[0, -1]/total, abs=2e-13)
    assert actual['np_bbn'] == pytest.approx(solution.y[0, -1]/solution.y[1, -1], abs=2e-13)
    assert actual['neutron_fraction_capture']+actual['proton_fraction_capture'] == 1.
    assert actual['Y_p'] == pytest.approx(2*actual['np_bbn']/(1+actual['np_bbn']), abs=2e-16)
    first = helium_yield(temperature, splitting, interval/2, lifetime)
    assert actual['neutron_fraction_capture'] == pytest.approx(
        first['neutron_fraction_capture']*math.exp(-interval/(2*lifetime)), abs=2e-16)


def test_conserved_capture_limits_and_input_validation():
    temperature, splitting, lifetime = .0008, .0013, 900.
    initial = helium_yield(temperature, splitting, 0., lifetime)
    expected = 1/(1+math.exp(splitting/temperature))
    assert initial['neutron_fraction_capture'] == pytest.approx(expected, abs=1e-16)
    assert initial['np_bbn'] == pytest.approx(initial['np_freeze'], abs=1e-16)
    late = helium_yield(temperature, splitting, 1e9, lifetime)
    assert late['Y_p'] == 0 and late['np_bbn'] == 0
    assert late['proton_fraction_capture'] == 1
    equal = helium_yield(temperature, 0., 90., lifetime)
    assert equal['Y_p'] == pytest.approx(math.exp(-.1), abs=2e-16)
    for args in ((0., splitting, 1., lifetime), (temperature, -1., 1., lifetime),
                 (temperature, splitting, -1., lifetime), (temperature, splitting, 1., 0.)):
        with pytest.raises(ValueError, match='positive freeze'):
            helium_yield(*args)


def test_three_quark_source_channels_obey_colour_and_spinor_selection():
    result = three_quark_source_certificate()
    # 3 tensor 3 tensor 3 = 1 + 8 + 8 + 10.  The two octets couple to
    # an adjoint source to form two independent global colour singlets.
    assert result['colour_casimir_multiplicities'] == {'0': 1, '3': 16, '6': 10}
    gram = np.asarray(result['adjoint_source_gram'])
    assert np.linalg.eigvalsh(gram) == pytest.approx([0., 2., 2.], abs=2e-14)
    assert result['independent_adjoint_source_channels'] == 2
    assert max(result['residuals'].values()) < 2e-14
    source = result['spatial_source']
    assert source['positive_dirac_weight_per_column'] == pytest.approx([2/3]*2)
    assert source['negative_dirac_weight_per_column'] == pytest.approx([1/3]*2)
    assert source['norm_outside_incoming_shell_per_column'] == pytest.approx([1.]*2)
    # Charge normalization follows Q^2=sum_i q_i^2+2 sum_(i<j) q_i q_j.
    from fractions import Fraction
    for row in result['electric_charge_moments'].values():
        assert Fraction(row['total_charge'])**2 == (
            Fraction(row['sum_squared_charges'])+2*Fraction(row['sum_pair_charge_products']))
    assert result['evaluation_work']['binding_kernel_solves'] == 0
    assert result['physical_scalar_charge_computed'] is False


def test_isovector_matching_preserves_mass_scalar_renormalization_and_em_sign():
    inputs = dict(m_down=.005, m_up=.0024, scalar_isovector_matrix_element=1.1,
        electromagnetic_split=.0011, scale=2., scheme='MSbar',
        source='specified scalar density matrix element at the declared scale',
        matrix_element_scale=2., matrix_element_scheme='MSbar',
        electromagnetic_convention='specified fixed QCD/QED separation',
        electromagnetic_source='specified current response', mass_source='specified running masses')
    original = matched_neutron_proton_split(**inputs)
    assert original['strong_split_GeV'] == pytest.approx(1.1*(.005-.0024), abs=1e-18)
    assert original['neutron_proton_split'] == pytest.approx(1.1*(.005-.0024)-.0011, abs=1e-18)
    for factor in (.3, 4.):
        transformed = matched_isovector_split(**{**inputs,
            'm_down': factor*inputs['m_down'], 'm_up': factor*inputs['m_up'],
            'scalar_isovector_matrix_element': inputs['scalar_isovector_matrix_element']/factor})
        assert transformed['strong_split_GeV'] == pytest.approx(original['strong_split_GeV'], abs=1e-18)
        assert transformed['neutron_proton_split'] == pytest.approx(original['neutron_proton_split'], abs=1e-18)
    for changes in ({'matrix_element_scheme': 'RI-MOM'}, {'matrix_element_scale': 3.}):
        with pytest.raises(ValueError, match='share scheme and scale'):
            matched_isovector_split(**{**inputs, **changes})
    with pytest.raises(ValueError, match='nonempty'):
        matched_isovector_split(**{**inputs, 'electromagnetic_convention': ''})
    for key, derivative in (('m_down', original['derivatives']['m_down']),
                            ('m_up', original['derivatives']['m_up']),
                            ('electromagnetic_split', -1.)):
        h = 1e-6
        upper = matched_isovector_split(**{**inputs, key: inputs[key]+h})['neutron_proton_split']
        lower = matched_isovector_split(**{**inputs, key: inputs[key]-h})['neutron_proton_split']
        assert (upper-lower)/(2*h) == pytest.approx(derivative, abs=3e-12)


def test_nucleon_mass_pair_and_common_native_scale():
    split = matched_isovector_split(m_down=.005, m_up=.0024,
        scalar_isovector_matrix_element=1.1, electromagnetic_split=.0011,
        scale=2., scheme='MSbar', source='specified mathematical scalar data',
        electromagnetic_convention='fixed mathematical QCD/EM separation')
    pair = matched_nucleon_masses(isoscalar_qcd_mass=.94, electromagnetic_mean_shift=.0002,
        isovector=split, isoscalar_source='specified mathematical common QCD mass',
        electromagnetic_convention=split['electromagnetic_convention'])
    assert (pair['proton_mass_GeV']+pair['neutron_mass_GeV'])/2 == pytest.approx(.9402, abs=2e-16)
    assert pair['neutron_mass_GeV']-pair['proton_mass_GeV'] == pytest.approx(
        split['neutron_proton_split'], abs=2e-16)
    assert pair['electromagnetic_proton_shift_GeV']-pair['electromagnetic_neutron_shift_GeV'] == pytest.approx(.0011, abs=1e-18)
    with pytest.raises(ValueError, match='QCD/EM convention'):
        matched_nucleon_masses(isoscalar_qcd_mass=.94, electromagnetic_mean_shift=.0002,
            isovector=split, isoscalar_source='specified source', electromagnetic_convention='another split')
    native = native_nucleon_readout(Lambda_QCD=.2, tau=.02, m_down=.0048, m_up=.0022,
                                    alpha_em=.0073, generation_scale=1e18)
    expected = constituent_proton_readout(.2, .02)
    assert native['proton'] == expected
    assert native['isovector']['scheme'] == 'native spectral mass readout'
    assert native['isovector']['scalar_isovector_matrix_element'] == 1.
    assert native['neutron_mass_GeV'] == expected['proton_mass_GeV']+native['isovector']['neutron_proton_split']
    for scale in (.01, 100.):
        changed = native_nucleon_readout(Lambda_QCD=.2*scale, tau=.02,
            m_down=.0048*scale, m_up=.0022*scale, alpha_em=.0073, generation_scale=1e18*scale)
        assert changed['proton']['proton_mass_GeV'] == pytest.approx(
            scale*native['proton']['proton_mass_GeV'], rel=2e-15)
        assert changed['isovector']['neutron_proton_split'] == pytest.approx(
            scale*native['isovector']['neutron_proton_split'], rel=2e-15)


def test_thermal_equation_of_state_limits_and_evolution(weak_inputs,monkeypatch):
    hot=photon_electron_eos(.5,weak_inputs.electron_mass)
    assert hot['rho']/.5**4==pytest.approx(5.5*math.pi**2/30,rel=2e-6)
    cold=photon_electron_eos(1e-5,weak_inputs.electron_mass)
    assert cold['rho']/1e-20==pytest.approx(math.pi**2/15,rel=1e-10)
    # Observe the actual quadrature dispatches, including all EOS moments
    # and six weak channels; reporting may not add a second calculation.
    import cg_frg.cosmology.thermal_weak as thermal
    original_quad=thermal.quad
    quadrature_counts=[]
    def observed_quad(*args,**kwargs):
        result=original_quad(*args,**kwargs)
        quadrature_counts.append(result[2]['neval'])
        return result
    monkeypatch.setattr(thermal,'quad',observed_quad)
    result=evolve_neutron_fraction(weak_inputs,.002,.00015,reduced_planck_mass=2.4e18,
                                   neutrino_species=3.02,decoupling_temperature=.0012,
                                   rtol=2e-5)
    assert 0<result['neutron_fraction']<.5
    assert result['elapsed_seconds']>0
    assert 0<result['neutrino_temperature']<result['photon_temperature']
    assert not result['nuclear_capture_included']
    work=result['evaluation_work']
    assert work['quadrature_calls']==len(quadrature_counts)
    assert work['integrand_evaluations']==sum(quadrature_counts)
    assert work['eos_reuses']>0 and work['weak_rates_reuses']>0
    assert work['eos_requests']==work['eos_evaluations']+work['eos_reuses']
    assert work['weak_rates_requests']==work['weak_rates_evaluations']+work['weak_rates_reuses']
    bath=thermal_history_bath(result,1e25)
    T,Tnu,density=bath(result['elapsed_seconds'])
    assert T==pytest.approx(result['photon_temperature'])
    assert Tnu==pytest.approx(result['neutrino_temperature'])
    assert density==pytest.approx(1e25*math.exp(-3*result['log_scale_factor_growth']))


def test_sourced_reaction_network_against_exact_capture_solution():
    nuclei=(Nuclide('n',1,0),Nuclide('p',1,1),Nuclide('D',2,1))
    rate=NuclearReaction((1,1,0),(0,0,1),lambda T:1e-20,
                         'test model: constant two-body coefficient, not nuclear data',
                         (1e-5,1e-3),'test n+p capture')
    network=ReactionNetwork(nuclei,[rate])
    result=network.evolve([.5,.5,0],(0,2),lambda t:(.0001,1e20))
    assert result['abundances'][0,-1]==pytest.approx(.25,rel=2e-7)
    assert result['abundances'][2,-1]==pytest.approx(.25,rel=2e-7)
    assert result['baryon_conservation_residual']<1e-12
    with pytest.raises(ValueError,match='outside'):
        network.derivative([.5,.5,0],.1,1e20)


def test_thermal_quadrature_convergence_is_required(weak_inputs,monkeypatch):
    import cg_frg.cosmology.thermal_weak as thermal
    monkeypatch.setattr(thermal,'quad',lambda *args,**kwargs:
        (1.,.1,{'neval':21},'roundoff prevents requested tolerance'))
    with pytest.raises(ArithmeticError,match='did not converge'):
        thermal.weak_rates(weak_inputs,.001)
    with pytest.raises(ArithmeticError,match='did not converge'):
        thermal.photon_electron_eos(.001,weak_inputs.electron_mass)


def test_nuclear_evolution_keeps_free_weak_conversion_active():
    network=ReactionNetwork([Nuclide('n',1,0),Nuclide('p',1,1)],[])
    weak=WeakConversion(lambda t:(1.0,.2),'explicit constant-rate mathematical example')
    result=network.evolve([.5,.5],(0,2),lambda t:(.0001,1e20),weak_conversion=weak)
    expected=1/6+(.5-1/6)*math.exp(-1.2*2)
    assert result['abundances'][0,-1]==pytest.approx(expected,rel=2e-7)
    assert result['baryon_conservation_residual']<1e-12


def test_scalar_potential_vertices_transform_with_kinetic_normalization():
    values=dict(second_derivative=2.3,third_derivative=.7,fourth_derivative=1.8,kinetic_coefficient=.6)
    result=canonical_potential_vertices(**values)
    a=2.7
    rescaled=canonical_potential_vertices(second_derivative=2.3/a**2,
        third_derivative=.7/a**3,fourth_derivative=1.8/a**4,kinetic_coefficient=.6/a**2)
    for key in ('mass_squared','cubic_vertex','quartic_radial'):
        assert result[key]==pytest.approx(rescaled[key],rel=2e-14)


def _independent_electroweak_reference(couplings, vev, scale, bottom=0., tau=0.):
    import mpmath as mp
    with mp.workdps(85):
        g1,g,g3,yt,lam=map(lambda x:mp.mpf(str(x)),couplings)
        v,q,yb,yl=map(lambda x:mp.mpf(str(x)),(vev,scale,bottom,tau))
        gp2=3*g1*g1/5
        W,Z,h=g*g*v*v/4,(g*g+gp2)*v*v/4,2*lam*v*v
        t,b,tau_mass=yt*yt*v*v/2,yb*yb*v*v/2,yl*yl*v*v/2
        A=lambda x:x*(mp.log(x/(q*q))-1) if x else mp.mpf(0)
        # Original published expression, independent of the stable divided
        # differences used by the implementation; exact coincidences use
        # derivatives of the original numerators.
        zw=(A(Z)-A(W))/(Z-W) if Z!=W else mp.diff(A,W)
        numerator=lambda x:(4*g*g-12*x/(v*v))*A(W)-g*g*A(x)
        hw=numerator(h)/(h-W) if h!=W else mp.diff(numerator,W)
        fermion=lambda x:2*x*A(x)/(v*v)
        tb=(yt*yt*A(t)-yb*yb*A(b))/(t-b) if t!=b else mp.diff(fermion,t)
        dr=(mp.mpf(3)/4*(g*g-gp2)*zw+mp.mpf(3)/4*hw+3*tb
            +2*A(tau_mass)/(v*v)-(3*g*g+gp2)/8+(3*yt*yt+3*yb*yb+yl*yl)/2-lam)/(16*mp.pi**2)
        m2=-lam*v*v
        f=lambda x:x*x/4*(mp.log(x/(q*q))-mp.mpf(3)/2)
        def potential(phi):
            H=m2+3*lam*phi*phi
            w,z=g*g*phi*phi/4,(g*g+gp2)*phi*phi/4
            value=f(H)-12*f(yt*yt*phi*phi/2)+6*f(w)+w*w+3*f(z)+z*z/2
            if yb:value-=12*f(yb*yb*phi*phi/2)
            if yl:value-=4*f(yl*yl*phi*phi/2)
            return value
        # The Goldstone first derivative vanishes at the tree minimum.
        return float(dr),float(mp.diff(potential,v)/v)


@pytest.mark.parametrize('bottom,tau',[(0.,0.),(.024,.01)])
def test_electroweak_finite_matching_against_original_formula_and_potential(bottom,tau):
    couplings=(.47,.65,1.2,.94,.14)
    result=electroweak_matching_one_loop(couplings,243.,scale_GeV=153.,
        vev_definition='tree_minimum',action_source='specified canonical test action',
        bottom_yukawa=bottom,tau_yukawa=tau)
    dr,tadpole=_independent_electroweak_reference(couplings,243.,153.,bottom,tau)
    assert result['delta_r_one_loop']==pytest.approx(dr,rel=2e-13,abs=2e-16)
    assert result['tadpole_delta1_GeV2']==pytest.approx(tadpole,rel=2e-13,abs=2e-10)
    loop_vev=electroweak_matching_one_loop(couplings,243.,scale_GeV=153.,
        vev_definition='tadpole_free_landau',action_source='specified loop-minimum test action',
        bottom_yukawa=bottom,tau_yukawa=tau)
    assert loop_vev['G_F_one_loop_GeVminus2']==pytest.approx((1+dr)/(math.sqrt(2)*243**2))
    assert result['G_F_finite_relative_term']-dr==pytest.approx(tadpole/(16*math.pi**2*.14*243**2))


@pytest.mark.parametrize('relative_gap',[0.,1e-12,-1e-12])
def test_electroweak_matching_removable_mass_coincidences(relative_gap):
    # h=W, Z=W and t=b are all regular in the matched coefficient.
    couplings=(0.,.5,1.,.75,.5**2/8*(1+relative_gap))
    result=electroweak_matching_one_loop(couplings,240.,scale_GeV=160.,
        vev_definition='tadpole_free_landau',action_source='coincident-mass test action',
        bottom_yukawa=.75)
    reference=_independent_electroweak_reference(couplings,240.,160.,.75)[0]
    assert result['delta_r_one_loop']==pytest.approx(reference,rel=3e-13,abs=3e-15)


def test_electroweak_matching_dimension_and_one_loop_scale_cancellation():
    couplings=(.47,.65,1.2,.94,.14)
    settings=dict(vev_definition='tadpole_free_landau',action_source='specified canonical test action')
    result=electroweak_matching_one_loop(couplings,243.,scale_GeV=153.,**settings)
    scaled=electroweak_matching_one_loop(couplings,7*243.,scale_GeV=7*153.,**settings)
    assert scaled['G_F_one_loop_GeVminus2']*49==pytest.approx(result['G_F_one_loop_GeVminus2'],rel=3e-15)
    assert scaled['tadpole_delta1_GeV2']/49==pytest.approx(result['tadpole_delta1_GeV2'],rel=3e-14)
    step=1e-5
    upper=electroweak_matching_one_loop(couplings,243.,scale_GeV=153*math.exp(step),**settings)
    lower=electroweak_matching_one_loop(couplings,243.,scale_GeV=153*math.exp(-step),**settings)
    derivative=(upper['delta_r_one_loop']-lower['delta_r_one_loop'])/(2*step)
    # This cancels d log(v^-2)/d log Q at first loop order. Running the
    # couplings inside the one-loop coefficient contributes at two loops.
    assert derivative==pytest.approx(2*result['vev_logarithmic_beta_one_loop'],abs=3e-12)


@pytest.mark.parametrize('definition,source',[
    ('window','specified'),('', 'specified'),(None,'specified'),
    ('tree_minimum',''),('tree_minimum','   '),('tree_minimum',None),('tree_minimum',7)])
def test_electroweak_matching_requires_explicit_input_identity(definition,source):
    with pytest.raises(ValueError):
        electroweak_matching_one_loop((.47,.65,1.2,.94,.14),243.,scale_GeV=153.,
            vev_definition=definition,action_source=source)


@pytest.mark.parametrize('bottom,tau',[(0.,0.),(.024,.01)])
def test_fermi_readout_matching_preserves_weak_amplitude_series(monkeypatch,bottom,tau):
    import mpmath as mp
    import cg_core.matter_matching as matching
    couplings=(.47,.65,1.2,.94,.14)
    vf,scale=243.,153.
    calls=[]
    original=matching.electroweak_matching_one_loop
    def counted_kernel(*args,**kwargs):
        calls.append((args,kwargs))
        return original(*args,**kwargs)
    monkeypatch.setattr(matching,'electroweak_matching_one_loop',counted_kernel)
    result=electroweak_matching_from_fermi_readout(couplings,vf,scale_GeV=scale,
        input_definition='fermi_constant_readout',action_source='declared same-action Fermi input',
        bottom_yukawa=bottom,tau_yukawa=tau)
    assert len(calls)==1
    dr,tadpole=_independent_electroweak_reference(couplings,vf,scale,bottom,tau)
    assert result['delta_r_one_loop']==pytest.approx(dr,rel=2e-13)
    assert result['tadpole_one_loop_GeV2']==pytest.approx(tadpole/(16*math.pi**2),rel=2e-13)
    # Insert the reported VEV series into the independently evaluated
    # weak amplitude. Its zeroth and first loop coefficients preserve G_F.
    with mp.workdps(60):
        v=mp.mpf(str(vf))
        shift=mp.mpf(str(result['running_vev_GeV_first_order']))-v
        shift_sq=mp.mpf(str(result['running_vev_squared_GeV2_first_order']))-v*v
        r=mp.mpf(str(dr))
        amplitude=lambda order:(1+order*r)/(mp.sqrt(2)*(v+order*shift)**2)
        assert float(amplitude(0))==pytest.approx(result['G_F_preserved_GeVminus2'],rel=2e-15)
        assert abs(float(mp.diff(amplitude,0)/amplitude(0)))<1e-14
        square_difference=lambda order:(v+order*shift)**2-(v*v+order*shift_sq)
        assert abs(float(mp.diff(square_difference,0)))<3e-11
        # The nonzero second coefficient is deliberately absent from v_L².
        assert float(mp.diff(square_difference,0,2))==pytest.approx(2*float(shift)**2,rel=2e-14)
    assert result['input_definition']=='fermi_constant_readout'
    assert result['output_vev_definition']=='tadpole_free_landau'
    assert result['finite_mass_readout_matching']['top_correction_GeV'] is None
    assert result['finite_mass_readout_matching']['higgs_squared_correction_GeV2'] is None


def test_fermi_readout_matching_scale_derivative_and_units():
    couplings=(.47,.65,1.2,.94,.14)
    settings=dict(input_definition='fermi_constant_readout',action_source='declared same-action Fermi input')
    base=electroweak_matching_from_fermi_readout(couplings,243.,scale_GeV=153.,**settings)
    step=1e-5
    upper=electroweak_matching_from_fermi_readout(couplings,243.,scale_GeV=153*math.exp(step),**settings)
    lower=electroweak_matching_from_fermi_readout(couplings,243.,scale_GeV=153*math.exp(-step),**settings)
    # A fixed physical G_F induces the known Landau-gauge VEV running.
    # Coupling evolution inside the finite coefficient starts at two loops.
    g1,g,_,yt,_=couplings
    gamma=(2.25*g*g+.45*g1*g1-3*yt*yt)/(16*math.pi**2)
    derivative=(upper['running_vev_GeV_first_order']-lower['running_vev_GeV_first_order'])/(2*step*243.)
    assert derivative==pytest.approx(gamma,abs=1e-11)
    assert upper['G_F_preserved_GeVminus2']==lower['G_F_preserved_GeVminus2']
    scaled=electroweak_matching_from_fermi_readout(couplings,7*243.,scale_GeV=7*153.,**settings)
    assert scaled['running_vev_GeV_first_order']/7==pytest.approx(base['running_vev_GeV_first_order'],rel=2e-15)
    assert scaled['G_F_preserved_GeVminus2']*49==pytest.approx(base['G_F_preserved_GeVminus2'],rel=2e-15)
    assert scaled['tadpole_one_loop_GeV2']/49==pytest.approx(base['tadpole_one_loop_GeV2'],rel=3e-14)


@pytest.mark.parametrize('definition,source',[
    ('tree_minimum','specified'),('tadpole_free_landau','specified'),
    ('', 'specified'),(None,'specified'),(1,'specified'),
    ('fermi_constant_readout',''),('fermi_constant_readout','   '),
    ('fermi_constant_readout',None),('fermi_constant_readout',7)])
def test_fermi_readout_matching_requires_explicit_input_identity(definition,source):
    with pytest.raises(ValueError):
        electroweak_matching_from_fermi_readout((.47,.65,1.2,.94,.14),243.,scale_GeV=153.,
            input_definition=definition,action_source=source)


@pytest.mark.parametrize('x,y,s',[
    (3.,3.,1e-5),(3.,3.,7.),(3.,3.,12.),(3.,3.,20.),
    (0.,2.,1e-6),(0.,2.,2.),(0.,2.,3.),(0.,0.,2.),
    (1.,4.,1.),(1.,4.,12.),(1.,4.,0.),
])
def test_pole_two_point_integral_against_complex_parameter_integral(x,y,s):
    import mpmath as mp
    from cg_core.matter_matching import _ew_two_point_finite
    actual,count,method=_ew_two_point_finite(x,y,s,5.)
    with mp.workdps(65):
        X,Y,S=map(mp.mpf,(x,y,s))
        points=[mp.mpf(0),mp.mpf(1)]
        disc=(S-X-Y)**2-4*X*Y
        if S and disc>=0:
            for root in ((S+Y-X-mp.sqrt(disc))/(2*S),(S+Y-X+mp.sqrt(disc))/(2*S)):
                if 0<root<1:points.append(root)
        def integrand(u):
            denominator=u*X+(1-u)*Y-u*(1-u)*S
            if not denominator:return mp.mpf(0)  # an integrable isolated endpoint
            return -mp.log(abs(denominator)/5)+(1j*mp.pi if denominator<0 else 0)
        expected=complex(mp.quad(integrand,sorted(set(points))))
    assert actual==pytest.approx(expected,rel=2e-11,abs=2e-11)
    assert count>=0 and method


def test_top_pole_imaginary_part_is_born_decay_width():
    couplings=(.47,.65,1.2,.94,.14)
    v=243.
    result=top_higgs_pole_matching_one_loop(couplings,v,scale_GeV=153.,
        vev_definition='tadpole_free_landau',action_source='declared generated leading action')
    mt=couplings[3]*v/math.sqrt(2)
    mw=couplings[1]*v/2
    born=couplings[1]**2*mt**3/(64*math.pi*mw**2)*(1-mw**2/mt**2)**2*(1+2*mw**2/mt**2)
    assert result['top_width_GeV_first_order']==pytest.approx(born,rel=3e-14)
    assert result['higgs_width_GeV_first_order']==0
    work=result['evaluation_work']
    assert work['distinct_A_values']==4
    assert work['distinct_B_values']==7  # B(t,Z) appears in two source terms
    assert work['quadrature_integrand_evaluations']>0
    assert work['B_methods']['split Feynman-parameter integral']==2


def test_pole_matching_qcd_limit_and_dimensional_scaling():
    couplings=np.array((.47,.65,1.2,.94,.14))
    settings=dict(vev_definition='tadpole_free_landau',action_source='declared generated leading action')
    base=top_higgs_pole_matching_one_loop(couplings,243.,scale_GeV=153.,**settings)
    mt=couplings[3]*243/math.sqrt(2)
    qcd=qcd_mass_matching_one_loop(mt,couplings[2]**2/(4*math.pi),
        scale_GeV=153.,input_definition='MSbar',boundary_source=settings['action_source'])
    expected=2*mt*(qcd['matched_mass_GeV']-mt)
    assert base['top_squared_terms_GeV2']['QCD']['real']==pytest.approx(expected,rel=3e-14)
    # Sending all electroweak couplings to zero at fixed tree masses
    # removes their corrections while retaining precisely the QCD kernel.
    epsilon=1e-3
    small=couplings*np.array((epsilon,epsilon,1,epsilon,epsilon**2))
    limit=top_higgs_pole_matching_one_loop(small,243/epsilon,scale_GeV=153.,**settings)
    assert limit['top_squared_terms_GeV2']['QCD']['real']==pytest.approx(expected,rel=3e-14)
    ew=base['top_squared_correction_GeV2']['real']-expected
    assert (limit['top_squared_correction_GeV2']['real']-expected)/epsilon**2==pytest.approx(ew,rel=2e-8)
    scaled=top_higgs_pole_matching_one_loop(couplings,7*243.,scale_GeV=7*153.,**settings)
    for sector in ('top','higgs'):
        for component in ('real','imag'):
            assert scaled[f'{sector}_squared_correction_GeV2'][component]/49==pytest.approx(
                base[f'{sector}_squared_correction_GeV2'][component],rel=3e-14,abs=1e-12)
    assert scaled['top_width_GeV_first_order']/7==pytest.approx(base['top_width_GeV_first_order'],rel=3e-14)


def test_pole_matching_one_loop_logarithms_cancel_tree_running():
    g1,g,g3,yt,lam=couplings=(.47,.65,1.2,.94,.14)
    v,scale,step=243.,153.,1e-5
    settings=dict(vev_definition='tadpole_free_landau',action_source='declared generated leading action')
    plus=top_higgs_pole_matching_one_loop(couplings,v,scale_GeV=scale*math.exp(step),**settings)
    minus=top_higgs_pole_matching_one_loop(couplings,v,scale_GeV=scale*math.exp(-step),**settings)
    gp2=3*g1*g1/5
    bv=9*g*g/4+3*gp2/4-3*yt*yt
    by=9*yt*yt/2-8*g3*g3-9*g*g/4-17*gp2/12
    bl=24*lam*lam+12*lam*yt*yt-6*yt**4-9*lam*g*g-3*lam*gp2+9*g**4/8+3*g*g*gp2/4+3*gp2**2/8
    t,h=yt*yt*v*v/2,2*lam*v*v
    tree={'top':2*t*(by+bv)/(16*math.pi**2),
          'higgs':2*v*v*(bl+2*lam*bv)/(16*math.pi**2)}
    for sector in tree:
        derivative=(plus[f'{sector}_squared_correction_GeV2']['real']-
                    minus[f'{sector}_squared_correction_GeV2']['real'])/(2*step)
        assert derivative==pytest.approx(-tree[sector],rel=2e-9,abs=2e-7)


def test_generated_on_shell_inverse_conditions_and_reused_weak_kernel(monkeypatch):
    import mpmath as mp
    import cg_core.matter_matching as matching
    couplings=(.47,.65,1.2,.94,.14)
    v,scale=243.,153.
    mt,mh=couplings[3]*v/math.sqrt(2),math.sqrt(2*couplings[4])*v
    source='generated values as common-action on-shell conditions'
    weak=electroweak_matching_from_fermi_readout(couplings,v,scale_GeV=scale,
        input_definition='fermi_constant_readout',action_source=source)
    def forbidden(*args,**kwargs):
        raise AssertionError('existing finite weak coefficient must be reused')
    monkeypatch.setattr(matching,'electroweak_matching_one_loop',forbidden)
    result=generated_on_shell_matter_matching(couplings[:3],v,top_mass_GeV=mt,
        higgs_mass_GeV=mh,scale_GeV=scale,input_definition='generated_on_shell_conditions',
        action_source=source,fermi_matching=weak)
    with mp.workdps(60):
        V,Y,L=map(lambda x:mp.mpf(str(x)),(v,couplings[3],couplings[4]))
        dv2=mp.mpf(str(result['running_vev_squared_GeV2_first_order']))-V*V
        dy,dl=map(lambda k:mp.mpf(str(result[k])),('yukawa_finite_shift','quartic_finite_shift'))
        dt2=mp.mpf(str(result['pole_kernel']['top_squared_correction_GeV2']['real']))
        dh2=mp.mpf(str(result['pole_kernel']['higgs_squared_correction_GeV2']['real']))
        dm2=mp.mpf(str(result['matched_quadratic_GeV2_first_order']))+L*V*V
        tad=mp.mpf(str(weak['tadpole_one_loop_GeV2']))
        top=lambda order:(Y+order*dy)**2*(V*V+order*dv2)/2+order*dt2
        higgs=lambda order:2*(L+order*dl)*(V*V+order*dv2)+order*dh2
        stationary=lambda order:-L*V*V+order*dm2+(L+order*dl)*(V*V+order*dv2)+order*tad
        for relation in (top,higgs,stationary):
            assert abs(float(mp.diff(relation,0)))<3e-11
    assert result['evaluation_work']['fermi_kernel_calls']==0
    assert result['evaluation_work']['pole_kernel_calls']==1
    assert result['conditions']['top_pole_mass_GeV']==mt
    assert not result['native_source_readout_identification_derived']
    assert weak['finite_mass_readout_matching']['top_correction_GeV'] is None


@pytest.mark.parametrize('definition,source',[
    ('tree_minimum','specified'),(None,'specified'),
    ('tadpole_free_landau',''),('tadpole_free_landau',None),
])
def test_pole_matching_requires_action_and_vev_identity(definition,source):
    with pytest.raises(ValueError):
        top_higgs_pole_matching_one_loop((.47,.65,1.2,.94,.14),243.,scale_GeV=153.,
            vev_definition=definition,action_source=source)


@pytest.mark.parametrize('key,value',[
    ('action_source','different action'),('scale_GeV',151.),
    ('input_fermi_vev_GeV',242.),('leading_couplings',[.47,.65,1.2,1.,.14]),
    ('bottom_yukawa',.02),
])
def test_generated_on_shell_matching_rejects_incompatible_reused_action(key,value):
    c=(.47,.65,1.2,.94,.14)
    weak=electroweak_matching_from_fermi_readout(c,243.,scale_GeV=153.,
        input_definition='fermi_constant_readout',action_source='same source')
    weak[key]=value
    with pytest.raises(ValueError,match='same source'):
        generated_on_shell_matter_matching(c[:3],243.,top_mass_GeV=c[3]*243/math.sqrt(2),
            higgs_mass_GeV=math.sqrt(2*c[4])*243,scale_GeV=153.,
            input_definition='generated_on_shell_conditions',action_source='same source',fermi_matching=weak)
