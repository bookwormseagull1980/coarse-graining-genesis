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

"""Refresh the current DESI comparison from the completed CAMB propagation.

The separate observation store supplies the vector, covariance and source
identities. The result is registered with the other framework comparisons.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from cg_core.params import get, record, sm_value, sm_set
from cg_frg.cosmology.camb_interface import (
    BAO_DATA_KEY, INPUT_KEYS, current_camb_record, current_bao_record)


def register_dataset(data):
    """Register an observed BAO vector and covariance independently of predictions."""
    import math
    import re
    import numpy as np
    covariance = np.asarray(data['covariance'], dtype=float)
    rows = data['rows']
    if not rows or covariance.shape != (len(rows), len(rows)) or not np.all(np.isfinite(covariance)):
        raise ValueError('Invalid BAO dataset dimensions or covariance')
    if not np.allclose(covariance, covariance.T, rtol=0, atol=1e-14):
        raise ValueError('BAO covariance must be symmetric')
    np.linalg.cholesky(covariance)
    for row in rows:
        if set(row) != {'z', 'quantity', 'observed'} or not math.isfinite(row['z']) or row['z'] <= 0 \
                or not math.isfinite(row['observed']) or row['quantity'] not in \
                {'DM_over_rs', 'DH_over_rs', 'DV_over_rs'}:
            raise ValueError('Invalid BAO observation row')
    sources = data['sources']
    for prefix in ('mean', 'covariance'):
        if not sources[prefix+'_url'].startswith('https://') or not re.fullmatch(
                '[0-9a-f]{64}', sources[prefix+'_sha256']):
            raise ValueError('BAO source identity is incomplete')
    sm_set(BAO_DATA_KEY, data, note='DESI DR2 observed vector and covariance with exact source fingerprints.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    camb = current_camb_record({k: float(get(k)) for k in INPUT_KEYS}, get('endpoint_camb_record'))
    if camb['status'] != 'current_inputs_match':
        raise RuntimeError('CAMB input validation failed: ' + camb['reason'])
    result = current_bao_record(camb, data=sm_value(BAO_DATA_KEY))
    if result['status'] != 'current_inputs_match':
        raise RuntimeError('BAO comparison failed: ' + result['reason'])
    record('endpoint_bao_record', result, role='comparison', dependencies=('endpoint_camb_record',),
           note='Fixed-parameter DESI DR2 comparison using registered observations.')
    print(json.dumps({k: result[k] for k in ('n_data', 'chi2', 'pte')}, indent=2))


if __name__ == '__main__':
    main()
