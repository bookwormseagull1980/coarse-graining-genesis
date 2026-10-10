# -*- coding: utf-8 -*-
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

"""Fixed-parameter comparison checks for endpoint-residual cosmology.

This optional script performs three checks without fitting V5 parameters:

1. DESI DR2 BAO Gaussian likelihood using registered observations.
2. SPARC rotation-curve residuals with fixed M/L and fixed endpoint mu(y).
3. A bullet-like cluster centroid diagnostic for free endpoint residuals.

Results are registered through the unified parameter interface. Public data
are downloaded only with ``--refresh-data``; ordinary comparison is offline.
Computed comparisons are stored through the unified parameter interface.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_core.params import get, record, sm_set, sm_value  # noqa: E402
from cg_core.release import publication_metadata
from cg_frg.cosmology.camb_interface import (  # noqa: E402
    INPUT_KEYS, BAO_DATA_KEY, current_camb_record, current_bao_record)
from cg_frg.cosmology.endpoint_residual import (
    SPARC_DATA_KEY, SPARC_URL, parse_sparc, current_sparc_record)

DESI_MEAN_URL = (
    "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/"
    "desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt"
)
DESI_COV_URL = (
    "https://raw.githubusercontent.com/CobayaSampler/bao_data/master/"
    "desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt"
)
C_KM_S = 299792.458


def get_float(key: str) -> float:
    """Read a generated parameter from the current store."""
    return float(get(key))


def fetch_bytes(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def register_sparc_dataset():
    """Register public observations and their exact downloaded-byte identity."""
    raw = fetch_bytes(SPARC_URL)
    data = {"identity": "SPARC mass models, Lelli et al. (2016), Zenodo record 16284118",
            "source": SPARC_URL, "source_sha256": hashlib.sha256(raw).hexdigest(),
            "rows": list(parse_sparc(raw.decode("utf8")))}
    if not data["rows"]:
        raise ValueError("SPARC download contains no mass-model observations")
    sm_set(SPARC_DATA_KEY, data, note="Published SPARC mass models; fixed-version source and byte fingerprint.")


def register_bao_dataset():
    mean, covariance = fetch_bytes(DESI_MEAN_URL), fetch_bytes(DESI_COV_URL)
    rows = parse_bao_mean(mean.decode("utf8"))
    data = {"identity": "DESI DR2 Gaussian BAO, ALL_GCcomb",
            "sources": {"mean_url": DESI_MEAN_URL, "covariance_url": DESI_COV_URL,
                        "mean_sha256": hashlib.sha256(mean).hexdigest(),
                        "covariance_sha256": hashlib.sha256(covariance).hexdigest()},
            "rows": [{"z": z, "observed": value, "quantity": quantity}
                     for z, value, quantity in rows],
            "covariance": np.loadtxt(io.StringIO(covariance.decode("utf8"))).tolist()}
    if not rows:
        raise ValueError("BAO download contains no observations")
    from scripts.run_bao_comparison import register_dataset
    return register_dataset(data)


def v5_values() -> dict[str, float]:
    Omega_b = get_float("Omega_b")
    Omega_sigma = get_float("Omega_Sigma")
    camb = current_camb_record({key: float(get(key)) for key in INPUT_KEYS})
    if camb['status'] != 'current_inputs_match':
        raise RuntimeError('CAMB input validation failed: ' + camb['reason'])
    budget = camb['density_dictionary']
    H0 = get_float("H0_GEV") * 1.519267447e24 * 3.0856775814913673e19
    return {
        "H0": H0,
        "Omega_b": Omega_b,
        "Omega_Sigma": Omega_sigma,
        "Omega_Sigma_cold": budget['components']['cdm'],
        "Omega_m": budget['Omega_m_with_massive_neutrinos'],
        "r_drag_Mpc": camb['outputs']['r_drag_Mpc'],
        "a0_m_s2": get_float("a0_MOND"),
    }


def parse_bao_mean(text: str) -> list[tuple[float, float, str]]:
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        z, val, quantity = line.split()
        rows.append((float(z), float(val), quantity))
    return rows


def run_bao() -> dict:
    camb = current_camb_record({key: float(get(key)) for key in INPUT_KEYS})
    if camb['status'] != 'current_inputs_match':
        raise RuntimeError('CAMB input validation failed: ' + camb['reason'])
    result = current_bao_record(camb, data=sm_value(BAO_DATA_KEY))
    if result['status'] != 'current_inputs_match':
        raise RuntimeError('BAO comparison failed: ' + result['reason'])
    record('endpoint_bao_record', result, role='comparison',
           note='Fixed-parameter DESI DR2 likelihood with registered observation identity.')
    return result


def common_mass_scale_constraints(scale_projection, temperature, monopole, *,
                                  degrees_of_freedom, log_scale_tangent=None,
                                  confidence_level=.95):
    """Finite common-scale constraints from a saved covariance projection.

    Thermal photons and fixed-shape Fermi-Dirac neutrinos scale as exp(4s).
    Baryons remain pressureless in the background, and the cold component
    compensates their exp(3s) density to preserve the total dust fraction.
    Thus E(z) is invariant and every distance ratio is multiplied by the
    same alpha(s)=exp(-2s)*r_d(0)/r_d(s). The fixed-drag enclosure follows
    from positivity of the sound-horizon integral at fixed drag scale factor.
    It assigns no bound to the change of the actual drag epoch.
    """
    from scipy.stats import chi2
    measured, error = (float(monopole[key]) for key in
                       ('temperature_K', 'standard_deviation_K'))
    alpha = float(scale_projection['alpha'])
    sigma_alpha = float(scale_projection['alpha_standard_error'])
    shape = float(scale_projection['chi2_orthogonal'])
    if (not all(math.isfinite(x) for x in
                (temperature, measured, error, alpha, sigma_alpha, shape, confidence_level))
            or min(temperature, error, alpha, sigma_alpha) <= 0 or measured <= 3*error
            or shape < 0 or type(degrees_of_freedom) is not int or degrees_of_freedom < 1
            or not 0 < confidence_level < 1
            or (log_scale_tangent is not None and not math.isfinite(log_scale_tangent))):
        raise ValueError('finite positive scale data, a positive three-sigma temperature interval and valid confidence level required')
    bounds = [math.log((measured-3*error)/temperature),
              math.log((measured+3*error)/temperature)]
    maximum_displacement = max(map(abs, bounds))
    fixed_drag = [math.exp(-max(bounds[1], 0.)/2),
                  math.exp(-min(bounds[0], 0.)/2)]
    fixed_drag_optimum = min(max(alpha, fixed_drag[0]), fixed_drag[1])
    threshold = float(chi2.ppf(confidence_level, degrees_of_freedom))
    supported = None
    nearest = None
    if threshold >= shape:
        width = sigma_alpha*math.sqrt(threshold-shape)
        if alpha+width > 0:
            supported = [max(0., alpha-width), alpha+width]
            nearest = min(max(1., supported[0]), supported[1])

    def necessary_response(target):
        log_target = math.log(target)
        magnitude = abs(log_target)
        # I_s(a_d0)/I_0 is between exp(min(s,0)/2) and exp(max(s,0)/2).
        drag_log_interval = [-log_target-max(bounds[1],0.)/2,
                             -log_target-min(bounds[0],0.)/2]
        drag_minimum = max(drag_log_interval[0], -drag_log_interval[1], 0.)
        entry = {'target_alpha':target,
                 'minimum_sup_abs_log_scale_derivative':magnitude/maximum_displacement,
                 'required_log_drag_integral_ratio_interval':drag_log_interval,
                 'minimum_abs_log_drag_integral_ratio':drag_minimum}
        if log_scale_tangent is not None:
            entry['minimum_abs_log_remainder_from_reference_tangent'] = max(
                0., magnitude-abs(log_scale_tangent)*maximum_displacement)
        return entry

    return {
        'background': 'flat FD thermal background with pressureless baryons and compensating cold density',
        'common_scale_identity': 'alpha(s)=exp(-2s)*r_d(0)/r_d(s); E(z,s)=E(z,0)',
        'cmb_three_sigma_log_interval':bounds,
        'cmb_interval_definition':'exact image of [T_observed-3 sigma_T,T_observed+3 sigma_T] under log(T/T_center)',
        'maximum_abs_log_displacement':maximum_displacement,
        'bao_statistic_identity':'chi2(alpha)=chi2_orthogonal+((alpha-alpha_star)/sigma_alpha)^2',
        'statistic_threshold':threshold, 'threshold_probability':confidence_level,
        'threshold_reference_degrees_of_freedom':degrees_of_freedom,
        'threshold_interpretation':'fixed-model Gaussian reference level; no fitted-model p-value assigned',
        'positive_alpha_interval_below_threshold':supported,
        'fixed_drag_epoch':{
            'alpha_enclosure':fixed_drag,
            'minimum_bao_chi2_over_enclosure':shape+((fixed_drag_optimum-alpha)/sigma_alpha)**2,
            'assumption':'drag scale factor held fixed; positive sound-horizon kernel and baryon loading',
            'actual_drag_epoch_constrained':False},
        'required_response_for_scale_optimum':necessary_response(alpha),
        'required_response_to_reach_threshold':None if nearest is None else necessary_response(nearest),
        'reference_log_scale_tangent':log_scale_tangent,
        'remainder_interpretation':'necessary response magnitude, not an assigned theoretical error or an upper bound',
        'operation_counts':{'additional_background_solutions':0,
                            'additional_covariance_factorizations':0,
                            'additional_covariance_solves':0}}


def shared_mass_scale_diagnostic(camb, data, monopole):
    """Covariance-weighted tangent along the common cosmological mass scale.

    A displacement s=ln(m_nu/m_nu,0) preserves the cosmological relations
    H0~exp(2s), T~exp(s), Omega_m=constant and Omega_b~exp(-s).
    The particle/weak inputs, eta_b, torsion, mass ratios and Planck scale
    are held fixed. This is a comparison direction, not a production fit.
    The registered CMB monopole supplies an independent constraint.
    """
    from scipy.stats import chi2
    from scipy.linalg import cho_factor, cho_solve
    result = current_bao_record(camb, data=data)
    if result.get('status') != 'current_inputs_match':
        raise ValueError('a current background and BAO covariance are required')
    response = camb['background_response']
    direction = {'H0': 2., 'TCMB': 1., 'neutrino_mass_scale': 1.,
                 'omega_m': 4., 'omega_b': 3.}
    temperature = float(camb['configuration']['cosmology']['TCMB'])
    observed_T = float(monopole['temperature_K'])
    sigma_T = float(monopole['standard_deviation_K'])
    if min(temperature, observed_T, sigma_T) <= 0:
        raise ValueError('positive temperature and uncertainty are required')
    theory = np.array([row['predicted'] for row in result['rows']])
    residual = np.array([row['residual'] for row in result['rows']])
    covariance = np.asarray(data['covariance'], dtype=float)
    factor = cho_factor(covariance, lower=True)
    elasticities = []
    for row in data['rows']:
        name = row['quantity'].replace('_over_rs', '_over_rd')+'@'+format(row['z'], 'g')
        elasticities.append(math.fsum(weight*response['responses'][coordinate]
            ['log_derivative'][name] for coordinate, weight in direction.items()))
    elasticity = np.asarray(elasticities)
    tangent = theory*elasticity
    weighted_tangent = cho_solve(factor, tangent)
    curvature = float(tangent@weighted_tangent)
    slope = float(residual@weighted_tangent)
    if curvature <= 0:
        raise ValueError('the physical scale direction must be identifiable')
    optimum = -slope/curvature
    cmb_center = math.log(observed_T/temperature)
    cmb_sigma = sigma_T/observed_T
    bounds = (math.log((observed_T-3*sigma_T)/temperature),
              math.log((observed_T+3*sigma_T)/temperature))
    constrained = float(np.clip(optimum, *bounds))
    remaining = residual+constrained*tangent
    fixed_cmb_pull = (temperature-observed_T)/sigma_T
    fixed_joint = result['chi2']+fixed_cmb_pull**2
    finite_scale = None
    if 'scale_diagnostic' in result:
        drag_tangent = math.fsum(weight*response['responses'][coordinate]
            ['log_derivative']['r_drag_Mpc'] for coordinate,weight in direction.items())
        reference_slope = -2-drag_tangent
        finite_scale = common_mass_scale_constraints(result['scale_diagnostic'],temperature,monopole,
            degrees_of_freedom=len(theory), log_scale_tangent=reference_slope)
        finite_scale['maximum_stencil_deviation_from_common_log_slope'] = float(
            max(abs(elasticity-reference_slope)))
    return {'definition': 'common cosmological mass normalization; linear response at the fixed branch',
        'coordinate_log_direction': direction, 'log_distance_elasticities': elasticity.tolist(),
        'held_fixed': ['mass ratios', 'torsion', 'Planck scale', 'eta_b',
                       'proton mass', 'weak freezeout inputs', 'helium fraction', 'N_eff'],
        'cmb_reference': monopole, 'cmb_log_scale_center': cmb_center,
        'cmb_log_scale_sigma': cmb_sigma, 'cmb_three_sigma_log_interval': list(bounds),
        'unconstrained_tangent_displacement': optimum,
        'unconstrained_tangent_sigma': 1/math.sqrt(curvature),
        'unconstrained_tangent_is_nonlinear_fit': False,
        'three_sigma_constrained_displacement': constrained,
        'three_sigma_minimum_linearized_bao_chi2': float(remaining@cho_solve(factor, remaining)),
        'maximum_linearized_relative_distance_change': float(max(abs(elasticity))*max(map(abs, bounds))),
        'fixed_bao_chi2': result['chi2'], 'fixed_bao_pte': result['pte'],
        'fixed_cmb_pull': fixed_cmb_pull, 'fixed_joint_chi2': fixed_joint,
        'fixed_joint_degrees_of_freedom': len(theory)+1,
        'fixed_joint_pte': float(chi2.sf(fixed_joint, len(theory)+1)),
        'finite_scale_constraints':finite_scale,
        'production_parameters_updated': False, 'theory_covariance_assigned': False,
        'operation_counts': {'additional_background_solutions': 0,
                             'covariance_dimension': len(theory), 'cholesky_factorizations': 1,
                             'factored_covariance_solves': 2}}


def registered_scale_diagnostic(camb):
    """Use isolated reference observations in a comparison-only calculation."""
    return shared_mass_scale_diagnostic(camb, sm_value(BAO_DATA_KEY), sm_value('CMB_MONOPOLE'))


def run_sparc() -> dict:
    result = current_sparc_record(get_float('a0_MOND'), data=sm_value(SPARC_DATA_KEY))
    if result['status'] != 'current_inputs_match':
        raise RuntimeError('SPARC comparison failed: ' + result['reason'])
    record('endpoint_sparc_record', result, role='comparison', dependencies=('a0_MOND',),
           note='SPARC comparison at fixed mass-to-light ratios and the stated selection.')
    return result


def run_cluster_diagnostic() -> dict:
    v5 = v5_values()
    dust_budget = v5["Omega_b"]+v5["Omega_Sigma_cold"]
    f_sigma = v5["Omega_Sigma_cold"] / dust_budget
    f_b = v5["Omega_b"] / dust_budget
    x_residual = 720.0
    x_gas = 120.0
    x_lensing = (f_sigma * x_residual + f_b * x_gas) / (f_sigma + f_b)
    return {
        "residual_fraction": f_sigma,
        "baryon_fraction": f_b,
        "x_residual_kpc": x_residual,
        "x_gas_kpc": x_gas,
        "x_lensing_centroid_kpc": x_lensing,
        "distance_to_residual_kpc": abs(x_lensing - x_residual),
        "distance_to_gas_kpc": abs(x_lensing - x_gas),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh-data", action="store_true", help="register newly downloaded public observations")
    args = parser.parse_args()
    if args.refresh_data:
        register_bao_dataset()
        register_sparc_dataset()
    cluster = run_cluster_diagnostic()
    record('endpoint_cluster_diagnostic', cluster, role='comparison',
           note='Specified two-component centroid example with the current cold and baryon fractions.')
    result = {
        "publication": publication_metadata(),
        "v5": v5_values(),
        "bao_desi_dr2": run_bao(),
        "sparc": run_sparc(),
        "cluster_residual_diagnostic": cluster,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
