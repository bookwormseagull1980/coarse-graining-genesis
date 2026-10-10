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

"""Finite-domain completeness and source-boundary derivatives."""
import math
import numpy as np
import pytest
from cg_core.window_weights import ResponseDomain
from cg_core.spectrum_loop import iter_sm_spectrum
from cg_frg.frg.spectral_sum import _freq_integral_gaussian, channel_tmunu_spin2
from cg_frg.framework.sigma_language import physical_radius, eff_temperature


def test_complete_high_tensor_domain_and_bound():
    L, k, R = 2.0, 4.0, 9.0
    modes = list(iter_sm_spectrum(L, k, .02, domain=ResponseDomain(R)))
    actual = {name for kind, name, *_ in modes if kind == "tensor_TT"}
    expected = {f"TT_{a}{b}" for a in range(40) for b in range(40)
                if a+b >= 2 and abs(a-b) <= 2 and (a+b) % 2 == 0
                and (2*a*(a+1)+2*b*(b+1)+6)/L**2 < R*k*k}
    assert actual == expected
    assert "TT_88" in actual
    assert all(lam < R*k*k for _, _, _, lam, *_ in modes)
    with pytest.raises(ValueError, match="safety cap"):
        list(iter_sm_spectrum(L, k, .02, l_max=5, domain=ResponseDomain(R)))


def test_domain_integral_and_moving_source_boundary():
    domain = ResponseDomain(3.0, "moving")
    lam, cutoff, h = .7, 1.2, 1e-6
    analytic = domain.boundary_derivative(lam, cutoff, dlam=.4, dcutoff=.2, dradius=.1)
    plus = ResponseDomain(3+.1*h).frequency_edge(lam+.4*h, cutoff+.2*h)
    minus = ResponseDomain(3-.1*h).frequency_edge(lam-.4*h, cutoff-.2*h)
    assert analytic == pytest.approx((plus-minus)/(2*h), rel=2e-8)
    assert ResponseDomain(3).boundary_derivative(lam, cutoff, dlam=1) == 0
    with pytest.raises(ValueError, match="boundary"):
        domain.boundary_derivative(3*cutoff, cutoff, dlam=1)
    value = _freq_integral_gaussian(lambda q, m: 1., lam, 0, cutoff, domain)
    expected = math.exp(-lam/cutoff)*math.sqrt(cutoff)/(2*math.sqrt(math.pi))*math.erf(
        math.sqrt(3-lam/cutoff))
    assert value == pytest.approx(expected, rel=2e-13)


def test_endpoint_response_scaling_with_explicit_domain():
    # On the prescribed branch cutoff*pi relation makes L sqrt(cutoff)=sqrt(pi).
    values = []
    for c in (2.1, 2.5, 2.9):
        pi0 = channel_tmunu_spin2(c, math.pi/c**2, .02, domain=ResponseDomain(5))["rp3_pi0"]
        values.append(c*math.pi**2*c**3*pi0/(32*math.pi**2))
    assert np.ptp(values) < 2e-14
    assert physical_radius(4., 2.5)*4 == 2.5
    with pytest.raises(ValueError, match="thermal state"):
        eff_temperature(4.)
    assert eff_temperature(4., assume_kms_period=True) == pytest.approx(2/math.pi)


def test_bandwidth_derivative_and_shared_mass_response():
    from cg_core.source_response import evaluate_bandwidth_response
    result = evaluate_bandwidth_response((5.,6.,20.,5.),certify_platform=False)
    assert result['passed'] and not result['production_parameters_updated']
    assert result['work']['spectral_response_evaluations'] == 3
    assert result['work']['iterative_endpoint_solves'] == 0
    c5 = result['reference_endpoint']
    for row in result['rows'][:2]:
        radius, step = row['radius'],1e-5
        coefficient = lambda R: channel_tmunu_spin2(1.,math.pi,.02,
            domain=ResponseDomain(R))['rp3_pi0']/32
        numerical = (coefficient(radius+step)-coefficient(radius-step))/(2*step)
        assert row['coefficient_radius_derivative'] == pytest.approx(numerical,rel=2e-8)
        delta = row['endpoint']-c5
        assert row['v_over_reference'] == pytest.approx(c5/row['endpoint']*math.exp(-4*math.pi*delta),rel=1e-13)
        assert row['electron_over_reference'] == pytest.approx(math.exp(-20*delta),rel=1e-13)
    threshold = evaluate_bandwidth_response((8/math.pi,),certify_platform=False)['rows'][0]
    assert threshold['derivative_status'] == 'shell threshold'
    assert threshold['coefficient_radius_derivative'] is None
    for invalid in ([],[0],[float('nan')],[float('inf')]):
        with pytest.raises(ValueError):
            evaluate_bandwidth_response(invalid,certify_platform=False)


def test_bandwidth_platform_certifies_infinite_tails_without_a_radius_scan():
    from scipy.integrate import quad
    from cg_frg.generation.spectral_certificate import certify_bandwidth_platform
    certificate = certify_bandwidth_platform()
    assert certificate['three_position_platform_certified']
    lo,hi = map(float,certificate['all_bandwidth_capacity'])
    assert 11/2 < lo < hi < 15/2
    assert certificate['work']['bandwidth_scan_points'] == 0
    assert certificate['work']['row_subintervals'] == 34*128
    # Independent adaptive integrals through degree 20 approximate the
    # complete Gaussian coefficient well inside its coarse certified box.
    value = 0.
    for n in range(21):
        rows = []
        if n%2 == 0:
            rows.append((n*(n+2),.75,4*(n+1)**2))
        else:
            rows.extend(((n+1)**2,b,w*n*(n+2)) for b,w in
                        ((1.5+1/15000,64),(1+1/15000,24),(1/15000,8)))
        rows.append(((n+1.5)**2,.00015,(84 if n%2 == 0 else 96)*(n+1)*(n+2)))
        for a,b,weight in rows:
            value += weight*quad(lambda u: ((u*u+a)/(u*u+a+b))**2*
                math.exp(-(u*u+a)/math.pi),0,np.inf,epsabs=1e-12)[0]
    value *= 27/(128*math.pi**3)
    lower,upper = map(float,certificate['complete_gaussian_endpoint'])
    assert lower < value < upper
    # Insufficient precision is reported as uncertified, not silently accepted.
    assert not certify_bandwidth_platform(16)['three_position_platform_certified']


def test_scale_ratio_eliminates_common_inputs_and_has_unique_physical_inverse():
    from cg_core.joint_response import evaluate
    from cg_core.source_response import hierarchy_scale_ratio, invert_hierarchy_scale_ratio
    for c in (2.36,2.4935343325,2.7):
        for tau,anchor in ((.01,1.),(.02,2.435e18),(.035,10.)):
            values = evaluate(c,tau,anchor)
            ratio = values['v_HIGGS']/(values['m_e_pred']/1e3)
            analytic = hierarchy_scale_ratio(c)
            assert math.log(ratio) == pytest.approx(analytic['log_v_over_electron'],abs=2e-14)
            assert invert_hierarchy_scale_ratio(ratio) == pytest.approx(c,abs=2e-13)
            epsilon = 1e-5
            numerical = (invert_hierarchy_scale_ratio(ratio*math.exp(epsilon))-
                         invert_hierarchy_scale_ratio(ratio*math.exp(-epsilon)))/(2*epsilon)
            assert numerical == pytest.approx(analytic['endpoint_log_ratio_derivative'],rel=2e-8)
    with pytest.raises(ValueError,match='outside'):
        invert_hierarchy_scale_ratio(1.)
    with pytest.raises(ValueError,match='increasing'):
        hierarchy_scale_ratio(.1)


def test_same_shell_support_and_joint_generation_edge():
    from cg_core.source_response import evaluate_hierarchy_selection
    result = evaluate_hierarchy_selection()
    assert result['passed'] and not result['empirical_test_performed']
    assert result['support_interval']['largest_active_spectral_value'] == 49/4
    assert result['support_interval']['first_excluded_spectral_value'] == 16
    assert 4 < result['three_position_radius_interval']['lower'] < 4.1
    radius = result['three_position_radius_interval']['lower']
    coefficient = channel_tmunu_spin2(1.,math.pi,.02,domain=ResponseDomain(radius))['rp3_pi0']
    assert (27*coefficient/128)**2 == pytest.approx(11/2,abs=1e-11)
    assert not result['three_position_radius_interval']['lower_closed']
    assert result['three_position_radius_interval']['upper_closed']
    certificate = result['support_certificate']
    assert certificate['generation_edge_inside_support_certified']
    for value,bounds in zip(result['support_endpoint_values'],certificate['endpoint_enclosures']):
        assert float(bounds[0]) < value < float(bounds[1])
    assert certificate['work']['row_subintervals'] == 15*32
    assert abs(result['charged_lepton_relation']['log_identity_residual']) < 1e-12
    assert result['work']['scale_ratio_spectral_evaluations'] == 0


def test_independently_supplied_matched_ratio_interval_maps_to_bandwidth():
    from cg_core.joint_response import evaluate
    from cg_core.source_response import infer_response_bandwidth
    bounds = (4.5,5.05)
    ratios = []
    for radius in bounds:
        c = 27*channel_tmunu_spin2(1.,math.pi,.02,domain=ResponseDomain(radius))['rp3_pi0']/128
        values = evaluate(c,.02,1.)
        ratios.append(values['v_HIGGS']/(values['m_e_pred']/1e3))
    metadata = dict(matching_source='Synthetic inverse-problem fixture',
                    mass_definition='geometric masses, common GeV units')
    result = infer_response_bandwidth(ratios,**metadata)
    assert result['status'] == 'compatible matched ratio'
    assert result['radius_interval'] == pytest.approx(bounds,abs=1e-10)
    assert not result['production_parameters_updated']
    assert result['lower_closed'] and result['upper_closed']
    excluded = infer_response_bandwidth((1.,2.),**metadata)
    assert excluded['status'] == 'incompatible matched ratio'
    assert excluded['radius_interval'] is None
    for invalid in ((0.,1.),(2.,1.),(1.,float('nan'))):
        with pytest.raises(ValueError):
            infer_response_bandwidth(invalid,**metadata)
    with pytest.raises(ValueError,match='matching source'):
        infer_response_bandwidth(ratios,matching_source='',mass_definition='GeV')


def test_correlated_cosmological_scale_uses_monopole_bound_without_fitting(monkeypatch):
    from scripts import validate_endpoint_cosmology as comparison
    theory = np.array([2., 3.])
    observed = np.array([1.9, 2.8])
    covariance = np.array([[.01, .002], [.002, .02]])
    residual = theory-observed
    fixed = float(residual@np.linalg.solve(covariance, residual))
    monkeypatch.setattr(comparison, 'current_bao_record', lambda camb, data: {
        'status': 'current_inputs_match', 'chi2': fixed, 'pte': .3,
        'rows': [{'predicted': t, 'residual': r} for t,r in zip(theory,residual)]})
    names = ['DM_over_rd@0.5', 'DH_over_rd@1']
    derivatives = {'H0': [-.5, -.6], 'TCMB': [.2, .3],
                   'omega_b': [.1, .2], 'omega_m': [.03, -.01],
                   'neutrino_mass_scale': [0., .001]}
    camb = {'configuration': {'cosmology': {'TCMB': 2.7}},
            'background_response': {'responses': {key: {'log_derivative': dict(zip(names, values))}
                                    for key,values in derivatives.items()}}}
    data = {'rows': [{'z': .5, 'quantity': 'DM_over_rs'},
                     {'z': 1., 'quantity': 'DH_over_rs'}], 'covariance': covariance}
    result = comparison.shared_mass_scale_diagnostic(camb,data,
        {'temperature_K': 2.7, 'standard_deviation_K': .0005})
    expected = np.array([-.38, -.339])
    assert result['log_distance_elasticities'] == pytest.approx(expected)
    assert result['fixed_joint_chi2'] == pytest.approx(fixed)
    assert result['fixed_joint_degrees_of_freedom'] == 3
    assert abs(result['three_sigma_constrained_displacement']) <= 3*.0005/2.7
    assert not result['production_parameters_updated']
    assert result['operation_counts']['additional_background_solutions'] == 0


def test_finite_scale_constraint_uses_exact_temperature_and_covariance_images():
    from scipy.stats import chi2
    from scripts.validate_endpoint_cosmology import common_mass_scale_constraints
    theory = np.array([2.,3.])
    observed = np.array([1.9,2.8])
    covariance = np.array([[.01,.002],[.002,.02]])
    inverse = np.linalg.inv(covariance)
    alpha = float(theory@inverse@observed/(theory@inverse@theory))
    sigma = 1/math.sqrt(float(theory@inverse@theory))
    orthogonal = alpha*theory-observed
    shape = float(orthogonal@inverse@orthogonal)
    result = common_mass_scale_constraints(
        {'alpha':alpha,'alpha_standard_error':sigma,'chi2_orthogonal':shape},
        2.7,{'temperature_K':2.701,'standard_deviation_K':.01},
        degrees_of_freedom=2,log_scale_tangent=-.7)
    lo,hi = result['cmb_three_sigma_log_interval']
    assert [2.7*math.exp(lo),2.7*math.exp(hi)] == pytest.approx([2.671,2.731],abs=1e-14)
    for value in result['positive_alpha_interval_below_threshold']:
        residual = value*theory-observed
        assert float(residual@inverse@residual) == pytest.approx(chi2.ppf(.95,2),rel=1e-13)
    enclosure = result['fixed_drag_epoch']['alpha_enclosure']
    # Independent positive sound-horizon integral with constant geometric kernel.
    def horizon(s,loading,drag):
        return 2*drag/(math.sqrt(1+loading*math.exp(-s)*drag)+1)
    for loading in (0.,1.,1e4,1e8):
        baseline = horizon(0.,loading,.001)
        for s in np.linspace(lo,hi,9):
            ratio = baseline/horizon(s,loading,.001)
            assert enclosure[0]-1e-14 <= ratio <= enclosure[1]+1e-14
    assert result['operation_counts']['additional_covariance_solves'] == 0
    assert not result['fixed_drag_epoch']['actual_drag_epoch_constrained']


def test_finite_scale_constraints_separate_drag_response_and_nonlinear_remainder():
    from scripts.validate_endpoint_cosmology import common_mass_scale_constraints
    result = common_mass_scale_constraints(
        {'alpha':.98,'alpha_standard_error':.002,'chi2_orthogonal':10.},
        2.7,{'temperature_K':2.7,'standard_deviation_K':.0005},
        degrees_of_freedom=13,log_scale_tangent=-.75)
    necessary = result['required_response_to_reach_threshold']
    assert necessary['target_alpha'] < 1
    assert necessary['minimum_sup_abs_log_scale_derivative'] > 20
    assert necessary['minimum_abs_log_drag_integral_ratio'] > .01
    assert necessary['minimum_abs_log_remainder_from_reference_tangent'] > .01
    # An orthogonal residual above the stated threshold excludes every common scale.
    incompatible = common_mass_scale_constraints(
        {'alpha':.98,'alpha_standard_error':.002,'chi2_orthogonal':100.},
        2.7,{'temperature_K':2.7,'standard_deviation_K':.0005},degrees_of_freedom=13)
    assert incompatible['positive_alpha_interval_below_threshold'] is None
    assert incompatible['required_response_to_reach_threshold'] is None
    with pytest.raises(ValueError,match='three-sigma'):
        common_mass_scale_constraints(
            {'alpha':.98,'alpha_standard_error':.002,'chi2_orthogonal':10.},
            2.7,{'temperature_K':2.7,'standard_deviation_K':1.},degrees_of_freedom=13)
