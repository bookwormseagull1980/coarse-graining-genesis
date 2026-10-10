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

"""Native RP3 integrals and a separately solved joint coupling boundary."""
import math
import numpy as np
import pytest

from cg_core import modal_algebra as modes
from cg_core.native_matter_matching import (
    spinor_fields, spinor_gram, spinor_vertex, native_vertex,
    scalar_profile_integrals, canonical_quartic, evaluate_native_matching,
    positive_shell_labels, shell_vertex_resolution, native_shell_action_pair,
    radial_spinor_family, native_family_action, lowest_signed_spatial_kernel,
)
from cg_core.gauge_running import CoupledBoundary, coupled_run, coupled_common_origin
from cg_core.matter_matching import canonical_flavour_pair, tree_mass_parameters


def test_complete_rp3_spinor_gram_and_constant_connector():
    labels=modes.spinor_basis(2)
    assert np.allclose(spinor_gram(labels),np.eye(len(labels)),rtol=0,atol=2e-15)
    actual=spinor_vertex({(0,0,0):1.},labels,labels)
    assert np.allclose(actual,np.eye(len(labels)),rtol=0,atol=2e-15)
    with pytest.raises(ValueError,match='distinct'):
        spinor_fields([labels[0],labels[0]])


def test_real_rp3_profile_quartic_by_independent_haar_integration():
    eta=.43
    profile={(0,0,0):1/math.sqrt(1+eta**2),(1,0,0):eta/math.sqrt(1+eta**2)}
    # D^1_00=cos(beta), and x=cos(beta) is uniform in the Haar integral.
    x,w=np.polynomial.legendre.leggauss(8)
    f=(1+eta*math.sqrt(3)*x)/math.sqrt(1+eta**2)
    result=scalar_profile_integrals(profile)
    assert result['quadratic']==pytest.approx(w@f**2/2,rel=2e-14)
    assert result['quartic']==pytest.approx(w@f**4/2,rel=2e-14)
    incoming=modes.spinor_basis(0)
    outgoing=modes.spinor_basis(1)
    complete=spinor_vertex(profile,outgoing,incoming)
    assert np.allclose(complete.conj().T@complete,np.eye(2),atol=2e-15)
    retained=spinor_vertex(profile,incoming,incoming)
    assert np.allclose(retained,np.eye(2)/math.sqrt(1+eta**2),atol=2e-15)
    sign_blocks=modes.signed_cross_blocks(complete,incoming,outgoing)
    negative=sign_blocks[('-', '+')]
    assert np.allclose(negative.conj().T@negative,
                       eta**2/(3*(1+eta**2))*np.eye(2),atol=2e-15)


def test_complex_spinor_integral_matches_independent_gaunt_path():
    left,right=modes.spinor_basis(2),modes.spinor_basis(1)
    profile={(1,1,0):.3+.2j,(1,-1,1):.7j,(0,0,0):.6}
    actual=spinor_vertex(profile,left,right)
    gaunt=modes.spinor_multiplication(profile,right,left)
    assert np.allclose(actual,gaunt,rtol=2e-14,atol=2e-15)
    reverse=spinor_vertex(modes.adjoint(profile),right,left)
    assert np.allclose(reverse,actual.conj().T,rtol=2e-14,atol=2e-15)


def test_specified_action_coefficient_sensitivity_at_fixed_spatial_modes():
    labels=modes.spinor_basis(0)
    profile={(0,0,0):1.}
    inputs=dict(yukawa_coefficient=.7,left_kinetic=2.,right_kinetic=3.,
                scalar_kinetic=5.,measure_volume=7.)
    result=native_vertex(profile,labels,labels,**inputs)
    assert np.allclose(result['vertex'],np.eye(2)*.7/math.sqrt(210),atol=2e-15)
    larger=native_vertex(profile,labels,labels,**{**inputs,'scalar_kinetic':20.})
    assert np.allclose(larger['vertex'],result['vertex']/2,atol=2e-15)
    quartic=canonical_quartic(profile,quartic_coefficient=.3,scalar_kinetic=5.,measure_volume=7.)
    assert quartic==pytest.approx(.3/(7*25),rel=2e-14)
    with pytest.raises(ValueError,match='positive'):
        native_vertex(profile,labels,labels,**{**inputs,'left_kinetic':0})


def test_joint_common_origin_is_solved_not_just_a_round_trip():
    initial=CoupledBoundary((.59,.51,.50,.91,.13),1e18,'MSbar','specified action example')
    solved=coupled_common_origin(initial,5e16)
    assert solved['bracket_residuals'][0]<0<solved['bracket_residuals'][1]
    assert abs(solved['relative_residual'])<2e-11
    assert solved['initial_couplings'][3:]==initial.values[3:]
    fresh=CoupledBoundary(solved['initial_couplings'],initial.scale,initial.scheme,initial.source)
    independent=coupled_run(fresh,5e16,rtol=5e-13,atol=5e-15,max_step=.05)
    weak,colour=independent['couplings'][1:3]
    assert colour==pytest.approx(weak*(1+(weak**2/(4*math.pi))**2/(8/3)),rel=2e-11)
    # A deliberately displaced initial colour coupling fails that same equation.
    displaced=CoupledBoundary((*fresh.values[:2],fresh.values[2]*1.001,*fresh.values[3:]),
                              fresh.scale,fresh.scheme,fresh.source)
    other=coupled_run(displaced,5e16)
    w,c=other['couplings'][1:3]
    assert abs(c-w*(1+(w**2/(4*math.pi))**2/(8/3)))>1e-4
    with pytest.raises(ValueError,match='opposite signs'):
        coupled_common_origin(initial,5e16,bracket=(.1,.2))


def test_zero_duration_colour_boundary_has_closed_root():
    initial=CoupledBoundary((.4,.6,.7,.8,.11),100,'MSbar','exact boundary test')
    result=coupled_common_origin(initial,100)
    expected=.6*(1+(.6**2/(4*math.pi))**2/(8/3))
    assert result['g3_initial']==pytest.approx(expected,rel=2e-14)


def test_native_report_includes_actual_inputs_and_unidentified_matching():
    report=evaluate_native_matching(quartic_coefficient=.13,
        family_transfers={'up': [1., .03, .00001], 'down': [1., .02, .001]},
        family_angular_data={'angular_sines': [.22, .04, .0038],
                             'phase': 1.2, 'down_coefficient': .024})
    assert report['checks_passed']
    assert not report['matching']['physical_msbar_boundary_determined']
    assert report['nonconstant_source']['full_matter_vertex_shape']==[160,16]
    assert len(report['matching']['unidentified_inputs'])>=5
    symmetric=report['generation_symmetric_action']
    assert not symmetric['simple_left_spectra']
    assert not symmetric['mixing_fixed_by_action']
    assert symmetric['commutator_norm']==0.
    shells=report['complete_shell_vertices']
    assert shells['shell_dimensions']==[2, 12, 30]
    assert shells['source_basis']['e100']['gram_traces']['negative']==pytest.approx(10/3)
    assert shells['source_basis']['e200']['shell_hilbert_schmidt_squared'][0][2]==pytest.approx(6/5)
    assert max(shells['production_transfer_action']['singular_value_residuals'].values())<2e-15
    assert not shells['production_transfer_action']['physical_family_projection_supplied']
    assert report['joint_family_action']['inherited_angular_prescription_realized']
    assert report['joint_family_action']['J'] != 0
    assert not report['joint_family_action']['source_sequence_uniqueness_proved']
    signed=report['signed_spatial_connector']
    assert signed['gaunt_coefficient']==pytest.approx(1/math.sqrt(3))
    assert signed['normalization']==pytest.approx(math.sqrt(3))
    assert (signed['left_ambient_dimension'],signed['right_ambient_dimension'])==(6,2)
    assert signed['source_dimension']==2 and signed['left_complement_dimension']==4
    assert (signed['left_dirac_position'],signed['right_dirac_position'])==(-2.5,1.5)
    assert max(signed['residuals'].values())<3e-14
    import json
    json.dumps(report, allow_nan=False)


def test_forward_common_action_flavour_invariants_under_nonunitary_coordinates():
    # Supplied vertices are fixed independently, without inverse mass construction.
    up=np.array([[.4,.12j,.03],[.1,.9,.2j],[.07,.11,1.2]],complex)
    down=np.array([[.2,.04,.1j],[.01,.6,.02],[.15j,.03,.8]],complex)
    left=np.diag([1.2,.8,1.7])
    ru,rd=np.diag([.7,1.5,1.1]),np.diag([1.3,.6,.9])
    first=canonical_flavour_pair(up,down,left,ru,rd,1.4)
    a=np.array([[1.,.2j,0.],[.1,1.1,.05],[0.,.1j,.9]],complex)
    b=np.array([[.8,.03,0.],[.1j,1.2,.07],[0.,.02j,1.]],complex)
    c=np.array([[1.1,0.,.06j],[.03,.9,0.],[.04,0.,1.2]],complex)
    second=canonical_flavour_pair(a.conj().T@up@b,a.conj().T@down@c,
        a.conj().T@left@a,b.conj().T@ru@b,c.conj().T@rd@c,1.4)
    assert first['simple_left_spectra'] and second['simple_left_spectra']
    for key in ('up_yukawa','down_yukawa','J','imag_trace_commutator_cubed'):
        np.testing.assert_allclose(second[key],first[key],rtol=2e-12,atol=3e-14)
    np.testing.assert_allclose(abs(second['mixing']),abs(first['mixing']),atol=3e-14)
    # Independent spectral-projector identity for squared mixing magnitudes.
    for i in range(3):
        assert np.sum(abs(first['mixing'][i])**2)==pytest.approx(1.,abs=3e-14)


def test_tree_mass_conversion_preserves_negative_curvature_and_scheme_data():
    result=tree_mass_parameters((.4,.6,1.1,.9,.12),250.,scale_GeV=200.,
        coupling_scheme='MSbar',vev_definition='explicit canonical VEV at this scale')
    assert result['m_top_tree_GeV']==pytest.approx(.9*250/math.sqrt(2))
    assert result['m_H_tree_GeV']==pytest.approx(math.sqrt(.24)*250)
    assert result['m_Z_tree_GeV']==pytest.approx(math.sqrt(.36+.6*.16)*125)
    assert not result['pole_mass_matching_performed']
    unstable=tree_mass_parameters((.4,.6,1.1,.9,-.12),250.,scale_GeV=200.,
        coupling_scheme='MSbar',vev_definition='explicit canonical VEV at this scale')
    assert unstable['m_H_curvature_squared_GeV2']<0 and unstable['m_H_tree_GeV'] is None
    with pytest.raises(ValueError,match='definition'):
        tree_mass_parameters((.4,.6,1.1,.9,.12),250.,scale_GeV=200.,
                             coupling_scheme='MSbar',vev_definition='')


def test_direct_svd_preserves_small_mass_in_rotated_hierarchy():
    from cg_frg.neutrino.complex_mixing import mixing_matrix
    left = mixing_matrix(.23, .04, .003, .9)
    right = mixing_matrix(.31, .17, .09, 1.3)
    expected = np.array([1e-9, .003, .8])
    up = left@np.diag(expected)@right.conj().T
    result = canonical_flavour_pair(up, np.diag([.001, .02, .3]),
        np.eye(3), np.eye(3), np.eye(3), 1.)
    np.testing.assert_allclose(result['up_yukawa'], expected, rtol=2e-7, atol=0)
    assert result['simple_left_spectra']
    np.testing.assert_allclose(abs(result['mixing']), abs(left.conj().T), atol=2e-13)


def test_degenerate_flavour_groups_return_only_invariant_projectors():
    result = canonical_flavour_pair(np.diag([.2, .2, .8]), np.diag([.1, .3, .7]),
        np.eye(3), np.eye(3), np.eye(3), 1.)
    assert not result['simple_left_spectra'] and result['mixing'] is None
    assert result['up_spectral_groups'][0]['indices'] == (0, 1)
    np.testing.assert_allclose(result['up_spectral_groups'][0]['projector'],
                               np.diag([1., 1., 0.]), atol=2e-15)


def test_complete_three_shell_vertex_keeps_multiplicities_and_transfer():
    labels = positive_shell_labels()
    assert len(labels) == 44
    transfer = [1., math.exp(-4.9), math.exp(-9.8)/4]
    data = shell_vertex_resolution({(0, 0, 0): 1.}, transfer=transfer)
    assert data['shell_dimensions'] == (2, 12, 30)
    expected = np.array([transfer[label[0]] for label in labels])
    np.testing.assert_allclose(data['retained_vertex'], np.diag(expected), atol=2e-15)
    assert data['omitted_operator_norm'] == pytest.approx(0., abs=2e-15)
    np.testing.assert_allclose(data['shell_hilbert_schmidt_squared'],
                               np.diag(np.array([2, 12, 30])*np.array(transfer)**2), atol=2e-15)
    with pytest.raises(ValueError, match='increasing'):
        positive_shell_labels((1, 0))


@pytest.mark.parametrize('degree', [1, 2])
def test_native_source_selection_and_complete_clebsch_gordan_budget(degree):
    profile = {(degree, 0, 0): 1.}
    data = shell_vertex_resolution(profile)
    # The j=0 incoming spinor is constant. Coupling degree k to spin 1/2
    # splits its norm in fractions (k+1)/(2k+1), k/(2k+1), independently
    # of an omitted-shell or sign truncation.
    first = [i for i, label in enumerate(data['input_labels']) if label[0] == 0]
    np.testing.assert_allclose(data['grams']['retained'][np.ix_(first, first)],
        np.eye(2)*(degree+1)/(2*degree+1), atol=3e-15)
    np.testing.assert_allclose(data['grams']['negative'][np.ix_(first, first)],
        np.eye(2)*degree/(2*degree+1), atol=3e-15)
    np.testing.assert_allclose(data['full_gram'][np.ix_(first, first)], np.eye(2), atol=3e-15)
    assert data['closure_residual'] < 3e-14
    blocks = data['shell_hilbert_schmidt_squared']
    assert blocks[degree, 0] == pytest.approx(2*(degree+1)/(2*degree+1), abs=3e-15)
    assert blocks[2 if degree == 1 else 1, 0] == pytest.approx(0., abs=3e-15)
    for gram in data['grams'].values():
        assert np.linalg.eigvalsh(gram)[0] > -2e-14
    independent = modes.spinor_multiplication(profile, data['input_labels'], data['output_labels'])
    np.testing.assert_allclose(data['full_vertex'], independent, atol=3e-15)


def test_joint_native_action_uses_one_left_form_and_complete_source_products():
    common = {(0, 0, 0): 1.}
    down_source = {(0, 0, 0): 1., (1, 0, 0): .2, (2, 1, 0): .1j}
    settings = dict(up_transfer=[1., .3, .02], down_transfer=[1., .2, .03],
        up_coefficient=.7, down_coefficient=.4, left_kinetic=2.,
        up_right_kinetic=3., down_right_kinetic=5., scalar_kinetic=7., measure_volume=11.)
    pair = native_shell_action_pair(common, down_source, common, **settings)
    assert pair['shell_dimensions'] == (2, 12, 30)
    assert pair['left_commutator_norm'] > 0
    assert not pair['physical_family_projection_supplied']
    expected = np.sort(np.repeat(np.array(settings['up_transfer'])*.7/math.sqrt(11*2*3*7),
                                 [2, 12, 30]))
    np.testing.assert_allclose(pair['up_singular_values'], expected, rtol=2e-14)
    scaled = native_shell_action_pair(common, down_source, common,
        **{**settings, 'measure_volume': 44.})
    for sector in ('up', 'down'):
        np.testing.assert_allclose(2*scaled[sector+'_canonical_vertex'],
                                   pair[sector+'_canonical_vertex'], atol=2e-15)
    assert pair['down']['omitted_operator_norm'] > 0


def test_radial_evaluation_and_character_vertices_are_basepoint_covariant():
    native = radial_spinor_family()
    shifted = radial_spinor_family(basepoint=(.23, -.31, .19))
    transport = shifted['translation']
    np.testing.assert_allclose(shifted['embedding'], transport@native['embedding'], atol=3e-15)
    for k in (1, 2):
        # The shifted multiplier was independently recomputed from its modal
        # coefficients, not manufactured by this unitary conjugation.
        np.testing.assert_allclose(shifted['character_vertices'][k],
            transport@native['character_vertices'][k]@transport.conj().T, atol=3e-15)
    for i in range(3):
        for j in range(3):
            for k in range(3):
                np.testing.assert_allclose(native['matrix_units'][i, j]@native['matrix_units'][j, k],
                                            native['matrix_units'][i, k], atol=3e-15)
    assert np.trace(native['source_projector']).real == pytest.approx(6)
    dirac = np.diag([modes.spinor_dirac_value(label) for label in native['labels']])
    np.testing.assert_allclose(dirac@native['source_projector'],
                               native['source_projector']@dirac, atol=3e-15)


def test_native_ordered_source_recovers_mass_mixing_and_cp_on_complete_domain():
    from cg_frg.neutrino.complex_mixing import mixing_matrix, jarlskog
    settings = dict(angular_sines=(.22, .04, .0038), phase=1.2,
        up_coefficient=.8, down_coefficient=.024, left_kinetic=1.3,
        up_right_kinetic=.7, down_right_kinetic=1.1, scalar_kinetic=1.2, measure_volume=2.)
    up, down = [1e-5, .007, 1.], [.001, .02, 1.]
    result = native_family_action(up, down, **settings)
    flavour = result['flavour']
    expected = mixing_matrix(*settings['angular_sines'], settings['phase'])
    np.testing.assert_allclose(abs(flavour['mixing']), abs(expected), atol=3e-14)
    np.testing.assert_allclose(flavour['up_yukawa'],
        np.array(up)*.8/math.sqrt(2*1.3*.7*1.2), rtol=3e-14)
    np.testing.assert_allclose(flavour['down_yukawa'],
        np.array(down)*.024/math.sqrt(2*1.3*1.1*1.2), rtol=3e-14)
    assert flavour['J'] == pytest.approx(jarlskog(expected), rel=3e-13)
    assert flavour['imag_trace_commutator_cubed'] != 0
    assert result['ambient_dimension'] == 44 and result['complement_dimension'] == 38
    assert max(result['residuals'].values()) < 3e-14
    conjugate = native_family_action(up, down, **{**settings, 'phase': -settings['phase']})
    assert conjugate['flavour']['J'] == pytest.approx(-flavour['J'], rel=3e-13)
    assert conjugate['flavour']['imag_trace_commutator_cubed'] == pytest.approx(
        -flavour['imag_trace_commutator_cubed'], rel=3e-13, abs=1e-35)


def test_native_family_action_common_nonunitary_coordinates():
    result = native_family_action([1e-5, .007, 1.], [.001, .02, 1.],
        angular_sines=(.22, .04, .0038), phase=1.2, up_coefficient=1.,
        down_coefficient=.024, left_kinetic=1., up_right_kinetic=1.,
        down_right_kinetic=1., scalar_kinetic=1., measure_volume=1.)
    left = np.array([[1., .2j, 0.], [.1, 1.1, .05], [0., .1j, .9]])
    ru, rd = np.diag([1.2, .7, 1.3]), np.diag([.8, 1.1, 1.5])
    changed = canonical_flavour_pair(left.conj().T@result['family_up_raw_vertex']@ru,
        left.conj().T@result['family_down_raw_vertex']@rd,
        left.conj().T@result['left_gram']@left, ru.conj().T@result['up_right_gram']@ru,
        rd.conj().T@result['down_right_gram']@rd, result['scalar_gram'])
    for key in ('up_yukawa', 'down_yukawa'):
        np.testing.assert_allclose(changed[key], result['flavour'][key], rtol=4e-11)
    np.testing.assert_allclose(abs(changed['mixing']), abs(result['flavour']['mixing']), atol=4e-13)
    assert changed['J'] == pytest.approx(result['flavour']['J'], rel=4e-11)


def test_lowest_signed_spatial_kernel_against_complete_gaunt_support():
    data=lowest_signed_spatial_kernel()
    complete=modes.spinor_basis(1)
    gaunt=modes.spinor_multiplication(data['source_profile'],data['right_labels'],complete)
    negative=[i for i,label in enumerate(complete) if modes.spinor_dirac_value(label)<0]
    np.testing.assert_allclose(data['raw_gaunt'],gaunt[negative],atol=2e-15)
    np.testing.assert_allclose(data['raw_gaunt'].conj().T@data['raw_gaunt'],np.eye(2)/3,atol=2e-15)
    left,kernel=data['left_embedding'],data['kernel']
    np.testing.assert_allclose(kernel.conj().T@kernel,np.eye(2),atol=2e-15)
    np.testing.assert_allclose(kernel@kernel.conj().T,data['left_projector'],atol=2e-15)
    np.testing.assert_allclose(left.conj().T@kernel,np.eye(2),atol=2e-15)
    complement=np.eye(6)-data['left_projector']
    assert np.trace(complement).real==pytest.approx(4)
    np.testing.assert_allclose(complement@kernel,np.zeros((6,2)),atol=2e-15)
    assert all(modes.spinor_dirac_value(x)==-2.5 for x in data['left_labels'])
    assert all(modes.spinor_dirac_value(x)==1.5 for x in data['right_labels'])


def test_lowest_signed_spatial_kernel_basepoint_covariance():
    origin=lowest_signed_spatial_kernel()
    shifted=lowest_signed_spatial_kernel(basepoint=(.23,-.31,.19))
    translation=shifted['left_translation']
    independent=modes.spinor_multiplication(shifted['source_profile'],
        shifted['right_labels'],shifted['left_labels'])
    np.testing.assert_allclose(shifted['raw_gaunt'],independent,atol=2e-15)
    for key in ('left_embedding','raw_gaunt','kernel'):
        np.testing.assert_allclose(shifted[key],translation@origin[key],atol=2e-15)
    np.testing.assert_allclose(shifted['left_projector'],
        translation@origin['left_projector']@translation.conj().T,atol=2e-15)
    assert max(shifted['residuals'].values())<3e-14
    for point in ((0.,0.),(0.,float('nan'),0.)):
        with pytest.raises(ValueError,match='three finite'):
            lowest_signed_spatial_kernel(basepoint=point)
