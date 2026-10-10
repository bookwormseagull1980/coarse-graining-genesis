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

"""Run and register a declared CAMB propagation in the unified comparison records."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cg_core.release import publication_metadata
from cg_core.params import get, record, sm_value
from cg_frg.cosmology.camb_interface import (INPUT_KEYS, BACKGROUND_COORDINATES,
    new_configuration, run, current_camb_record, evaluate_background_response)


def register_completed_record(completed, *, freshly_executed=False):
    """Validate and register a completed propagation with its execution identity."""
    inputs = {key: float(get(key)) for key in INPUT_KEYS}
    result = current_camb_record(inputs, completed)
    if result['status'] != 'current_inputs_match':
        raise ValueError('Completed propagation validation failed: ' + result['reason'])
    result['fresh_run'] = bool(freshly_executed)
    record('endpoint_camb_record', result, role='comparison', dependencies=INPUT_KEYS,
           note='Completed explicit CAMB propagation with full configuration and solver identity.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accuracy', type=float, default=1.)
    parser.add_argument('--mode', choices=('full','background'), default='full',
                        help='background computes thermal history and distances without power spectra')
    parser.add_argument('--reuse-center', action='store_true',
                        help='reuse a current input-bound propagation for a response calculation')
    parser.add_argument('--background-response', action='store_true',
                        help='register physical-coordinate thermal-background derivatives with the centre')
    parser.add_argument('--response-coordinates', default=','.join(BACKGROUND_COORDINATES))
    parser.add_argument('--response-refine', default='', help='comma-separated coordinates for half-step checks')
    parser.add_argument('--response-log-step', type=float, default=1e-3)
    args = parser.parse_args()
    inputs = {k: float(get(k)) for k in INPUT_KEYS}
    if args.reuse_center:
        if not args.background_response:
            raise ValueError('--reuse-center requires --background-response')
        result = current_camb_record(inputs)
        if result['status'] != 'current_inputs_match':
            raise ValueError('Requested centre is unavailable: '+result['reason'])
    else:
        registered = sm_value('CAMB_PROPAGATION_SETTINGS')
        if registered['reionization_model'] != 'TanhReionization':
            raise ValueError('The registered reionization convention requires an implemented propagation model')
        config = new_configuration(inputs, YHe=inputs['bbn_Yp'], N_eff=inputs['bbn_Neff'],
            tau_reio=registered['reionization_optical_depth'],
            accuracy=args.accuracy, mode=args.mode)
        result = {'publication': publication_metadata(), **run(config)}
        result['source_sha256'] = {rel: hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
                                  for rel in ('scripts/run_explicit_camb.py',
                                              'cg_frg/cosmology/camb_interface.py')}
        result = current_camb_record(inputs,result)
        if result['status'] != 'current_inputs_match':
            raise ValueError('New propagation failed validation: '+result['reason'])
    if args.background_response:
        result['background_response'] = evaluate_background_response(result,
            coordinates=tuple(x for x in args.response_coordinates.split(',') if x),
            log_step=args.response_log_step,
            refine=tuple(x for x in args.response_refine.split(',') if x),
            previous=result.get('background_response'))
    result = register_completed_record(result, freshly_executed=not args.reuse_center)
    print(json.dumps({k: result[k] for k in ('camb_version', 'configuration_sha256',
                                           'density_dictionary', 'outputs')}, indent=2))


if __name__ == '__main__':
    main()
