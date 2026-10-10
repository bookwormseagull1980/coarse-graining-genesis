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

"""Independent invariants, manufactured solutions and cache boundaries."""
import math
import copy
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
from cg_frg.gravity.angular_covariance import certificate
from cg_frg.gravity.newton import prescribed_readout, _sigma_response
from cg_frg.frg.trace_density import trace_density, sigma_self_energy
from cg_frg.gravity.pole_analysis import stability
from cg_frg.gravity.local_response import solve_dirichlet, flux_jacobian
from cg_core.params import published_record, published_sm_value
from cg_frg.cosmology.camb_interface import (BAO_DATA_KEY, current_camb_record,
                                           current_bao_record, new_configuration, fingerprint,
                                           evaluate_bao, validate_background, DISTANCE_PRESCRIPTION,
                                           constrained_cold_fraction, bao_inputs,
                                           drag_opacity_enclosure, late_ionization_drag_capacity,
                                           thermal_history_distance_budget)
from cg_frg.cosmology.cold_source import projection_check
from cg_frg.frg.ir_flow import integrate_supplied_profile


class GravityReadoutTests(unittest.TestCase):
    def test_finite_drag_envelope_inverts_both_extreme_histories(self):
        # tau0=z^2 and r_s=1/z give independently known exact endpoints.
        result = drag_opacity_enclosure(lambda z:z*z, lambda z:1/z,
            redshift_bracket=(.1, 3.), relative_bound=.2, absolute_bound=.1)
        expected = [math.sqrt(.9/1.2), math.sqrt(1.1/.8)]
        np.testing.assert_allclose(result['drag_redshift_interval'], expected, rtol=1e-9)
        np.testing.assert_allclose(result['sound_horizon_interval_Mpc'],
                                   [1/expected[1], 1/expected[0]], rtol=1e-9)
        for kwargs in ({'relative_bound':1.}, {'absolute_bound':-1.}):
            with self.assertRaises(ValueError):
                drag_opacity_enclosure(lambda z:z*z, lambda z:1/z,
                    redshift_bracket=(.1,3.), **kwargs)

    def test_electron_capacity_bounds_the_integrated_matter_background(self):
        from scipy.integrate import quad
        # Dimensionless manufactured constants check the integral and its
        # dependence on the fully ionized electron capacity independently.
        atomic = {'speed_of_light_m_s':2., 'Mpc_m':1000., 'G_SI':1.,
            'hydrogen_mass_kg':1., 'helium_hydrogen_mass_ratio':4.,
            'thomson_cross_section_m2':.1}
        cosmo = {'H0':1., 'YHe':.2}
        omega = {'baryon':.1, 'cdm':.2, 'photon':.01}
        result = late_ionization_drag_capacity(redshift_max=2.,
            cosmology=cosmo, components=omega, atomic=atomic)
        nh = 3/(8*math.pi)*.1*.8
        fhe = .2/(4*.8)
        loading = 3*.1/(4*.01)
        integral = quad(lambda z:2*.1*nh*(1+2*fhe)*(1+z)**1.5/
                                  (loading*math.sqrt(.3)),0,2)[0]
        lo,hi = result['capacity_interval']
        self.assertLessEqual(lo, integral)
        self.assertGreaterEqual(hi, integral)

    def test_thermal_distance_set_reuses_original_covariance_and_binds_inputs(self):
        saved = published_record('endpoint_camb_record')
        center = current_camb_record(saved['configuration']['endpoint_inputs'], saved)
        bao = current_bao_record(center)
        data = published_sm_value(BAO_DATA_KEY)
        rd = center['outputs']['r_drag_Mpc']
        thermal = {'center_execution_sha256':center['execution_sha256'],
            'late_ionization':{'sound_horizon_interval_Mpc':[rd*.999,rd*1.001]},
            'relative_opacity_scenario':{'sound_horizon_interval_Mpc':[rd,rd]},
            'recfast_calibration_comparisons':[]}
        thermal['budget_sha256'] = fingerprint(thermal)
        center['thermal_history_budget'] = thermal
        mapped = thermal_history_distance_budget(center,bao)
        predictions = np.array([row['predicted'] for row in bao['rows']])
        observed = np.array([row['observed'] for row in data['rows']])
        covariance = np.array(data['covariance'])
        interval = mapped['late_ionization']['common_ratio_interval']
        chi_values = [(a*predictions-observed)@np.linalg.solve(covariance,a*predictions-observed)
                      for a in interval]
        self.assertAlmostEqual(mapped['late_ionization']['chi2_interval'][1],max(chi_values),places=9)
        self.assertAlmostEqual(mapped['relative_opacity_scenario']['chi2_interval'][0],bao['chi2'],places=9)
        self.assertEqual(len(mapped['late_ionization']['distance_ratio_intervals']),13)
        self.assertEqual(mapped['operation_counts']['power_spectrum_solves'],0)
        altered=copy.deepcopy(center)
        altered['thermal_history_budget']['late_ionization']['sound_horizon_interval_Mpc'][0]*=.99
        with self.assertRaises(ValueError):
            thermal_history_distance_budget(altered,bao)
        thermal.pop('budget_sha256')
        thermal['direct_hyrec_atomic_response']={'generated_atomic_inputs':{'alpha':.01,'electron_mass_GeV':.001},'rows':[]}
        thermal['budget_sha256']=fingerprint(thermal)
        with self.assertRaises(ValueError):
            thermal_history_distance_budget(center,bao,generated_atomic={'alpha':.02,'electron_mass_GeV':.001})

    def test_unit_change_and_sigma_identity(self):
        a = prescribed_readout(.7, 3.5, .02, 1.)
        b = prescribed_readout(700., .0035, .02, 1000.)
        for key in ('r_read', 'Z_read'):
            self.assertAlmostEqual(a[key], b[key], places=11)
        self.assertAlmostEqual(a['sigma_read']*1e6, b['sigma_read'], places=7)
        self.assertAlmostEqual(a['G_read']/1e6, b['G_read'], places=13)
        self.assertAlmostEqual(_sigma_response(.7, 2.45, .02, 1.), sigma_self_energy(.7, 3.5, .02, 1.))
        self.assertAlmostEqual(abs(trace_density(.7, 3.5, .02, 1.)), a['sigma_read'])
        self.assertFalse(a['external_pole_established'])

    def test_domain_not_signed_loophole(self):
        self.assertFalse(stability(-100., 1.)['stable'])
        self.assertFalse(stability(-.001, 1.)['stable'])
        self.assertFalse(stability(0., 1.)['external_pole_established'])
        with self.assertRaises(ValueError):
            stability(0., 0.)

    def test_exact_angular_moment(self):
        c = certificate()
        self.assertTrue(c['exact'])
        self.assertEqual(c['two_block_trace'], '4/3')
        self.assertEqual(c['single_block_eigenvalue'], '2/15')

    def test_supplied_ir_profile_orientation(self):
        zero = integrate_supplied_profile(lambda k: 0., 100., 1., 2.)
        self.assertAlmostEqual(zero['L_end'], 200.)
        one = integrate_supplied_profile(lambda k: 1., 100., 1., 2.)
        self.assertAlmostEqual(one['integral_gamma_dlnk'], -math.log(100.))
        self.assertAlmostEqual(one['L_end'], 20000.)
        self.assertFalse(one['profile_selected_by_endpoint'])

    def test_current_record_input_binding(self):
        inputs = published_record('endpoint_camb_record')['configuration']['endpoint_inputs']
        record = current_camb_record(inputs)
        self.assertEqual(record['status'], 'current_inputs_match', record)
        self.assertFalse(record['fresh_run'])
        self.assertEqual(current_bao_record(record)['status'], 'current_inputs_match')
        changed = dict(inputs, Omega_b=inputs['Omega_b']*1.001)
        self.assertEqual(current_camb_record(changed)['status'], 'PENDING')
        self.assertIsNone(current_camb_record(changed)['outputs'])
        helium_change = dict(inputs, bbn_Yp=inputs['bbn_Yp']+.001)
        self.assertEqual(current_camb_record(helium_change)['status'], 'PENDING')
        cfg = new_configuration(changed, YHe=.25, N_eff=3.044,
                                tau_reio=record['configuration']['cosmology']['tau'])
        self.assertEqual(cfg['neutrino_masses_eV'], [inputs[k] for k in ('m_nu1', 'm_nu2', 'm_nu3')])

    def test_current_record_rejects_configuration_and_output_tampering(self):
        base = published_record('endpoint_camb_record')
        inputs = base['configuration']['endpoint_inputs']
        with self.subTest('in-memory completed records'):
            variants = []
            altered = copy.deepcopy(base)
            altered['configuration']['cosmology']['ombh2'] *= 1.001
            altered['configuration_sha256'] = fingerprint(altered['configuration'])
            variants.append(altered)
            altered = copy.deepcopy(base)
            altered['resolved_parameters'] = altered['resolved_parameters'].replace('YHe = ', 'missing_YHe = ')
            variants.append(altered)
            altered = copy.deepcopy(base)
            altered['outputs']['r_drag_Mpc'] *= 1.001
            variants.append(altered)
            if 'S8_total_matter' in base['outputs']:
                altered = copy.deepcopy(base)
                altered['outputs']['S8_total_matter'] *= 1.001
                variants.append(altered)
            altered = copy.deepcopy(base)
            altered['configuration']['primordial']['nt'] = 0.
            altered['configuration_sha256'] = fingerprint(altered['configuration'])
            variants.append(altered)
            altered = copy.deepcopy(base)
            altered['resolved_parameters'] = altered['resolved_parameters'].replace('ntrun = ', 'missing_ntrun = ')
            variants.append(altered)
            altered = copy.deepcopy(base)
            altered['outputs']['background_distances']['rows'][0]['D_M_Mpc'] *= 1.001
            variants.append(altered)
            altered = copy.deepcopy(base)
            altered['neutrino_resolution']['reconstructed_masses_eV'][0] *= 1.001
            variants.append(altered)
            altered = copy.deepcopy(base)
            masses = altered['configuration']['neutrino_masses_eV']
            altered['neutrino_resolution']['energy_density_fractions'] = [m/sum(masses) for m in masses]
            variants.append(altered)
            for altered in variants:
                result = current_camb_record(inputs, altered)
                self.assertEqual(result['status'], 'PENDING', result)
                self.assertIsNone(result['outputs'])

    def test_bao_record_rejects_mismatched_inputs_and_statistics(self):
        inputs = published_record('endpoint_camb_record')['configuration']['endpoint_inputs']
        camb = current_camb_record(inputs)
        base = current_bao_record(camb)
        with self.subTest('in-memory comparison records'):
            for key in ('camb_execution_sha256', 'dataset_sha256', 'chi2'):
                altered = copy.deepcopy(base)
                altered[key] = 'wrong' if key.endswith('sha256') else altered[key]*1.001
                self.assertEqual(current_bao_record(camb, altered)['status'], 'PENDING')
            for key in ('alpha','chi2_orthogonal'):
                altered = copy.deepcopy(base)
                altered['scale_diagnostic'][key] *= 1.001
                self.assertEqual(current_bao_record(camb,altered)['status'],'PENDING')

    def test_endpoint_pending_cache_aliases_are_unavailable_and_auditable(self):
        from cg_core import params
        from cg_frg.cosmology import camb_interface, endpoint_residual
        from scripts.audit_param_writers import audit_file

        saved = published_record('endpoint_camb_record')
        inputs = saved['configuration']['endpoint_inputs']
        current = json.loads(params._PARAM_FILE.read_text(encoding='utf8'))['parameters']
        aliases = ('Omega_Sigma_cold', 'endpoint_tensor_nt', 'endpoint_tensor_ntrun',
                   'endpoint_z_eq', 'endpoint_r_drag_Mpc',
                   'endpoint_theta100_star', 'endpoint_sigma8', 'endpoint_S8')
        for scenario in ('missing', 'stale'):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory(
                    prefix='v5-endpoint-cache-test-') as work:
                directory = Path(work)
                store = directory/'cg_params.json'
                sm_store = directory/'reference_inputs.json'
                sm_store.write_text(json.dumps({'parameters': {}}), encoding='utf8')
                completed = {}
                seed = {key: copy.deepcopy(current[key]) for key in
                        (*camb_interface.INPUT_KEYS, 'eta_b', 'a0_MOND')}
                for key, value in inputs.items():
                    seed[key]['value'] = value
                if scenario == 'stale':
                    completed = saved
                    seed['bbn_Yp']['value'] = math.nextafter(inputs['bbn_Yp'], math.inf)
                store.write_text(json.dumps({'parameters': seed}), encoding='utf8')
                with patch.object(params, '_PARAM_FILE', store), \
                        patch.object(params, '_SM_FILE', sm_store), \
                        patch.object(params, '_READ_INPUTS', {}), \
                        patch.object(camb_interface, 'current_camb_record',
                                     side_effect=lambda values: current_camb_record(values, completed)):
                    endpoint_residual.compute()
                    records = json.loads(store.read_text(encoding='utf8'))['parameters']
                    self.assertEqual(params.get('endpoint_camb_status'), 'PENDING')
                    self.assertIsNone(records['endpoint_camb_record']['value']['outputs'])
                    for key in aliases:
                        self.assertIsNone(records[key]['value'], key)
                        self.assertEqual(records[key]['provenance'], 'PENDING', key)
                        self.assertEqual(records[key]['role'], 'informational', key)
                        with self.assertRaises(KeyError):
                            params.get(key)
                    self.assertEqual(audit_file(store, 'endpoint cache test', True), [])

    def test_bao_observations_do_not_change_predicted_distances(self):
        base = published_sm_value(BAO_DATA_KEY)
        camb = published_record('endpoint_camb_record')
        background = camb['outputs']['background_distances']
        first = evaluate_bao(bao_inputs(camb), base['rows'], base['covariance'], background)
        altered = copy.deepcopy(base['rows'])
        for row in altered:
            row['observed'] *= 1.1
        second = evaluate_bao(bao_inputs(camb), altered, base['covariance'], background)
        self.assertEqual([r['predicted'] for r in first['rows']],
                         [r['predicted'] for r in second['rows']])
        self.assertNotEqual(first['chi2'], second['chi2'])

    def test_bao_scale_projection_matches_independent_weighted_normal_equation(self):
        data = published_sm_value(BAO_DATA_KEY)
        camb = published_record('endpoint_camb_record')
        result = evaluate_bao(bao_inputs(camb),data['rows'],data['covariance'],
                              camb['outputs']['background_distances'])
        prediction = np.array([row['predicted'] for row in result['rows']])
        observed = np.array([row['observed'] for row in data['rows']])
        covariance = np.asarray(data['covariance'])
        inverse_prediction = np.linalg.solve(covariance,prediction)
        alpha = inverse_prediction@observed/(inverse_prediction@prediction)
        residual = alpha*prediction-observed
        diagnostic = result['scale_diagnostic']
        self.assertAlmostEqual(diagnostic['alpha'],alpha,places=14)
        self.assertAlmostEqual(diagnostic['chi2_orthogonal'],
                               residual@np.linalg.solve(covariance,residual),places=11)
        self.assertLess(diagnostic['chi2_decomposition_abs_residual'],1e-11)
        self.assertLess(abs(diagnostic['covariance_orthogonality_residual']),1e-9)
        self.assertEqual((result['degrees_of_freedom'],result['fitted_parameters']),(13,0))
        self.assertEqual((diagnostic['degrees_of_freedom'],diagnostic['fitted_parameters']),(12,1))
        self.assertFalse(diagnostic['prediction_parameters_updated'])
        # Reordering correlated observations cannot change the projection.
        order = np.arange(len(prediction))[::-1]
        reordered = evaluate_bao(bao_inputs(camb),[data['rows'][i] for i in order],
            covariance[np.ix_(order,order)],camb['outputs']['background_distances'])
        self.assertAlmostEqual(reordered['scale_diagnostic']['alpha'],alpha,places=14)
        self.assertAlmostEqual(reordered['chi2'],result['chi2'],places=11)

    def test_bao_theory_covariance_is_explicit_correlated_and_separate(self):
        data = published_sm_value(BAO_DATA_KEY)
        camb = published_record('endpoint_camb_record')
        arguments = (bao_inputs(camb),data['rows'],data['covariance'],
                     camb['outputs']['background_distances'])
        base = evaluate_bao(*arguments)
        # A synthetic common systematic mode tests the interface, not a
        # physical uncertainty estimate for the published comparison.
        direction = np.linspace(.01,.03,len(data['rows']))
        theory = np.outer(direction,direction)
        assumptions = {'source':'synthetic correlated covariance for interface verification',
                       'approximation_order':'linear response test',
                       'independent_of_observations':True}
        result = evaluate_bao(*arguments,theory_covariance=theory,theory_uncertainty=assumptions)
        extra = result['comparison_with_supplied_theory_covariance']
        residual = np.array([row['residual'] for row in base['rows']])
        expected = residual@np.linalg.solve(np.asarray(data['covariance'])+theory,residual)
        self.assertAlmostEqual(extra['chi2'],expected,places=11)
        self.assertEqual(result['chi2'],base['chi2'])
        self.assertEqual(result['rows'],base['rows'])
        self.assertNotIn('comparison_with_supplied_theory_covariance',base)
        with self.assertRaises(ValueError):
            evaluate_bao(*arguments,theory_covariance=theory)
        with self.assertRaises(ValueError):
            evaluate_bao(*arguments,theory_covariance=-np.eye(13),theory_uncertainty=assumptions)
        with self.assertRaises(ValueError):
            evaluate_bao(*arguments,theory_covariance=theory,
                         theory_uncertainty={**assumptions,'independent_of_observations':False})

    def test_sparc_dataset_and_selection_are_bound_to_actual_evaluation(self):
        from cg_frg.cosmology.endpoint_residual import (current_sparc_record, SPARC_DATA_KEY,
                                                      SPARC_URL, sparc_point)
        dataset = published_sm_value(SPARC_DATA_KEY)
        from cg_core.params import get
        a0 = float(get('a0_MOND'))
        result = current_sparc_record(a0, data=dataset)
        self.assertEqual(result['status'], 'current_inputs_match')
        self.assertEqual(result['dataset_sha256'], fingerprint(dataset))
        self.assertEqual(result['configuration']['Y_disk'], .5)
        self.assertEqual(result['configuration']['Y_bulge'], .7)
        changed = copy.deepcopy(dataset)
        changed['rows'][0]['Vdisk'] *= 2
        self.assertNotEqual(current_sparc_record(a0, data=changed)['dataset_sha256'],
                            result['dataset_sha256'])
        self.assertNotEqual(current_sparc_record(a0*1.1, data=dataset)['curated_points'],
                            result['curated_points'])
        synthetic = {'id': 'test', 'R_kpc': 1., 'Vobs': 25., 'e_Vobs': 2.,
                     'Vgas': 3., 'Vdisk': 5., 'Vbul': 4.}
        self.assertIsNone(sparc_point(dict(synthetic, R_kpc=0), a0))
        sample = {'source': SPARC_URL, 'source_sha256': '0'*64,
                  'rows': [synthetic, dict(synthetic, Vobs=20.),
                           dict(synthetic, e_Vobs=2.5)]}
        filtered = current_sparc_record(a0, data=sample)
        self.assertEqual(filtered['all_points']['n_points'], 3)
        self.assertEqual(filtered['curated_points']['n_points'], 1)

    def test_full_background_distance_units_and_volume_average(self):
        # Analytic Einstein-de Sitter distances test the independent distance
        # contract and BAO algebra without relying on a saved CAMB prediction.
        H0, rd, z = 70., 147., 1.
        dm = 2*299792.458/H0*(1-1/math.sqrt(1+z))
        dh = 299792.458/H0/(1+z)**1.5
        background = {'prescription': DISTANCE_PRESCRIPTION, 'rows': [
            {'z': z, 'H_km_s_Mpc': H0*(1+z)**1.5, 'D_M_Mpc': dm,
             'D_H_Mpc': dh, 'D_M_quad_Mpc': dm, 'D_M_quad_error_estimate_Mpc': 1e-9}]}
        inputs = {'H0_km_s_Mpc': H0, 'r_drag_Mpc': rd,
                  'Omega_m_total_including_massive_neutrinos': .99}
        rows = [{'z': z, 'quantity': q, 'observed': 0.}
                for q in ('DM_over_rs', 'DH_over_rs', 'DV_over_rs')]
        result = evaluate_bao(inputs, rows, np.eye(3), background)
        expected = [dm/rd, dh/rd, (z*dm*dm*dh)**(1/3)/rd]
        np.testing.assert_allclose([row['predicted'] for row in result['rows']], expected,
                                   rtol=1e-14)
        background['rows'][0]['D_H_Mpc'] /= 1000
        with self.assertRaisesRegex(ValueError, 'unit mismatch'):
            validate_background(background, [z])

    def test_common_action_density_and_photon_number_constraints(self):
        visible = {'photon': .00005, 'neutrino': .00001, 'nu': .0015}
        cold = constrained_cold_fraction(.685, .049, visible)
        self.assertAlmostEqual(cold+.685+.049+sum(visible.values()), 1., places=15)
        self.assertAlmostEqual(cold, .26444, places=15)
        with self.assertRaises(ValueError):
            constrained_cold_fraction(.999, .002, visible)
        from cg_frg.cosmology.endpoint_residual import photon_zero_mode_factor
        correction = photon_zero_mode_factor(.02)
        raw_eta, raw_temperature = 6.1e-10, 2.354e-13
        self.assertAlmostEqual((raw_eta/correction**3)*(correction*raw_temperature)**3/
                               (raw_eta*raw_temperature**3), 1., places=14)

    def test_cold_projections(self):
        g = np.diag([-1., 1., 1., 1.])
        u = np.array([1.25, .75, 0., 0.])
        E = 2.*np.outer(g@u, g@u)
        self.assertTrue(projection_check(g, u, E)['cold_projections_satisfied'])
        self.assertFalse(projection_check(g, u, E+g+np.outer(g@u, g@u))['cold_projections_satisfied'])


def manufactured(nodes):
    x, y, z = nodes.T
    wave = np.sin(math.pi*x)*np.sin(math.pi*y)*np.sin(math.pi*z)
    return x+2*y+3*z+.08*wave


def manufactured_source(nodes):
    s = np.sin(math.pi*nodes); c = np.cos(math.pi*nodes)
    g = np.tile([1., 2., 3.], (len(nodes), 1))
    H = np.zeros((len(nodes), 3, 3))
    for i in range(3):
        others = [j for j in range(3) if j != i]
        g[:, i] += .08*math.pi*c[:, i]*s[:, others[0]]*s[:, others[1]]
        H[:, i, i] = -.08*math.pi**2*s.prod(axis=1)
        for j in others:
            k = 3-i-j
            H[:, i, j] = .08*math.pi**2*c[:, i]*c[:, j]*s[:, k]
    return np.einsum('nij,nij->n', flux_jacobian(g), H)


class FoliationRestrictionTests(unittest.TestCase):
    def test_foliation_inertia_on_actual_velocity_image(self):
        from cg_frg.gravity.local_response import constrained_clock_kinetic

        laplacian = np.eye(2)
        response = np.diag([2., .5])
        full = constrained_clock_kinetic(
            laplacian, response, np.eye(2), planck_mass_squared=1.)
        positive_image = constrained_clock_kinetic(
            laplacian, response, np.array([[0.], [1.]]), planck_mass_squared=1.)
        negative_image = constrained_clock_kinetic(
            laplacian, response, np.array([[1.], [0.]]), planck_mass_squared=1.)

        # For the two decoupled modes, potential elimination gives
        # 2*(1/lambda-1), respectively -1 and 2. A proper subspace
        # retains only the coefficient of its actual velocity direction.
        np.testing.assert_allclose(
            full['gradient_normalized_eigenvalues'], [-1., 2.], atol=1e-14)
        self.assertAlmostEqual(positive_image['minimum_normalized_coefficient'], 2.)
        self.assertAlmostEqual(negative_image['minimum_normalized_coefficient'], -1.)
        for result in (full, positive_image, negative_image):
            self.assertFalse(result['generation_map_validated'])
            self.assertEqual(result['model'], 'independent-foliation effective action')


class PhysicalKineticCertificateTests(unittest.TestCase):
    @staticmethod
    def certificate(K, G, error=1e-12):
        from cg_frg.gravity.local_response import certify_reduced_kinetic
        return certify_reduced_kinetic(
            K, G, normalized_operator_error_bound=error,
            action='finite quadratic action used for the analytic test',
            variation_space='two physical velocities after one algebraic constraint',
            source='explicit test coordinate map')

    def test_complete_constraint_reduction_includes_mixed_terms(self):
        # S2=1/2*v^T*A*v+z*C^T*v+z^2; its constraint is
        # z=-C^T*v/2, so K=A-C*C^T/2=diag(2, 5/2).
        A = np.array([[4., 1.], [1., 3.]])
        C = np.array([2., 1.])
        K = A-np.outer(C, C)/2
        v = np.array([.7, -.4])
        z = -C@v/2
        self.assertAlmostEqual(.5*v@A@v+z*(C@v)+z*z, .5*v@K@v)
        result = self.certificate(K, np.eye(2))
        np.testing.assert_allclose(result['normalized_eigenvalues'], [2., 2.5])
        self.assertEqual(result['status'], 'positive')
        self.assertFalse(result['complete_gravitational_action_derived'])

    def test_matter_direction_can_have_zero_foliation_component(self):
        ambient = np.array([[-1., 2.], [2., 5.]])
        source_map = np.array([[0.], [1.]])
        result = self.certificate(source_map.T@ambient@source_map,
                                  source_map.T@source_map)
        self.assertEqual(result['status'], 'positive')
        self.assertAlmostEqual(result['minimum_normalized_coefficient'], 5.)
        self.assertFalse(result['generation_map_validated'])

    def test_physical_basis_congruence_preserves_certificate(self):
        K = np.array([[2., .4], [.4, 3.]])
        G = np.array([[2., .3], [.3, 1.]])
        B = np.array([[1., 2.], [-.5, 1.]])
        original = self.certificate(K, G)
        transformed = self.certificate(B.T@K@B, B.T@G@B)
        np.testing.assert_allclose(transformed['normalized_eigenvalues'],
                                   original['normalized_eigenvalues'], rtol=2e-15)
        self.assertEqual(original['status'], transformed['status'])

    def test_error_budget_separates_unresolved_and_negative_direction(self):
        unresolved = self.certificate(np.diag([.1, 2.]), np.eye(2), error=.2)
        negative = self.certificate(np.diag([-.5, 2.]), np.eye(2), error=.1)
        self.assertEqual(unresolved['status'], 'unresolved')
        self.assertLess(unresolved['minimum_coefficient_interval'][0], 0.)
        self.assertGreater(unresolved['minimum_coefficient_interval'][1], 0.)
        self.assertEqual(negative['status'], 'negative_direction')
        self.assertTrue(negative['conditional_on_supplied_operator_bound'])
        with self.assertRaisesRegex(ValueError, 'positive definite'):
            self.certificate(np.eye(2), np.diag([1., 0.]))


class LocalEquationTests(unittest.TestCase):
    def test_non_spherical_manufactured_grid_convergence(self):
        errors = []
        for n in (4, 8, 12):
            r = solve_dirichlet(manufactured_source, manufactured, n=n)
            errors.append(float(np.sqrt(np.mean((r['phi']-manufactured(r['nodes']))**2))))
            self.assertLess(r['weak_residual_inf'], 1e-9)
            self.assertLess(abs(r['flux_balance_residual']), 2e-8)
            self.assertTrue(r['converged'])
            self.assertFalse(r['cosmological_source_map'])
        self.assertLess(errors[1], errors[0]/2.5)
        self.assertLess(errors[2], errors[1]/1.8)
        self.assertLess(errors[2], .001)

    def test_regularization_limit(self):
        errors = []
        for epsilon in (.1, .03, .01, 0.):
            r = solve_dirichlet(manufactured_source, manufactured, n=4, epsilon=epsilon)
            errors.append(r['phi'])
        self.assertLess(np.linalg.norm(errors[2]-errors[3]), np.linalg.norm(errors[1]-errors[3]))
        self.assertLess(np.linalg.norm(errors[1]-errors[3]), np.linalg.norm(errors[0]-errors[3]))

    def test_zero_and_affine_boundary(self):
        for boundary in (lambda x: np.zeros(len(x)), lambda x: x[:, 0]+2*x[:, 1]):
            r = solve_dirichlet(lambda x: np.zeros(len(x)), boundary, n=3)
            self.assertLess(np.max(np.abs(r['phi']-boundary(r['nodes']))), 1e-12)

    def test_spherical_smooth_source_limit(self):
        def exact(x):
            return np.sum((x-.5)**2, axis=1)/2
        def source(x):
            return np.trace(flux_jacobian(x-.5), axis1=1, axis2=2)
        errors = []
        for n in (8, 16):
            r = solve_dirichlet(source, exact, n=n)
            errors.append(np.sqrt(np.mean((r['phi']-exact(r['nodes']))**2)))
        self.assertLess(errors[1], errors[0]/2.5)


if __name__ == '__main__':
    unittest.main()
