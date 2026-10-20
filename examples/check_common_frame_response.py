"""Finite local check of the complete response in a moving colour frame.

Run from the repository root with:
    python -B examples/check_common_frame_response.py

The probes include a nonzero derivative of the frame transformation.  The
connection, frame, finite source law and observable are transported together.
The restoring coefficient is read from the generated Yang--Mills response.
This check uses local matrix jets; the transport of the allowed field
domain is proved in the companion manuscript.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cg_frg.qcd.generated_yang_mills import generated_yang_mills_gap


def skew_traceless(rng):
    matrix = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    matrix = (matrix - matrix.conj().T) / 2
    return matrix - np.trace(matrix) * np.eye(3) / 3


def curvature(connection, gradient):
    return np.array([gradient[a, b] - gradient[b, a]
                     + connection[a] @ connection[b] - connection[b] @ connection[a]
                     for a, b in ((0, 1), (1, 2), (2, 0))])


def frame_derivative(connection, frame, gradient):
    return gradient + np.array([component @ frame for component in connection])


def density(connection, gradient, frame, frame_gradient, restoring):
    field = curvature(connection, gradient)
    relative = frame_derivative(connection, frame, frame_gradient)
    return float((np.vdot(field, field).real + restoring * np.vdot(relative, relative).real) / 2)


def transport(connection, gradient, frame, frame_gradient, g, dg, ddg):
    inverse = g.conj().T
    derivative_inverse = np.array([-inverse @ component @ inverse for component in dg])
    transformed = np.array([inverse @ connection[b] @ g + inverse @ dg[b] for b in range(3)])
    differentiated = np.array([
        [derivative_inverse[a] @ connection[b] @ g
         + inverse @ gradient[a, b] @ g + inverse @ connection[b] @ dg[a]
         + derivative_inverse[a] @ dg[b] + inverse @ ddg[a, b]
         for b in range(3)] for a in range(3)])
    return (transformed, differentiated, inverse @ frame,
            np.array([derivative_inverse[a] @ frame + inverse @ frame_gradient[a]
                      for a in range(3)]))


def evaluate(seed=794):
    rng = np.random.default_rng(seed)
    generated = generated_yang_mills_gap(math.sqrt(2 * math.pi), certify=False)
    restoring = generated['transverse_shift']
    g, frame = expm(skew_traceless(rng)), expm(skew_traceless(rng))
    K = np.array([skew_traceless(rng) for _ in range(3)])
    dg = np.array([g @ k for k in K])
    ddg = np.array([[g @ (K[a] @ K[b] + K[b] @ K[a]) / 2
                     for b in range(3)] for a in range(3)])
    connection = np.array([skew_traceless(rng) for _ in range(3)])
    gradient = np.array([[skew_traceless(rng) for _ in range(3)] for _ in range(3)])
    frame_gradient = np.array([frame @ skew_traceless(rng) for _ in range(3)])
    moved = transport(connection, gradient, frame, frame_gradient, g, dg, ddg)
    expected_curvature = np.array([g.conj().T @ f @ g for f in curvature(connection, gradient)])
    expected_relative = np.array([g.conj().T @ f
                                  for f in frame_derivative(connection, frame, frame_gradient)])
    errors = {
        'curvature_covariance': float(np.max(np.abs(curvature(*moved[:2]) - expected_curvature))),
        'relative_frame_covariance': float(np.max(np.abs(frame_derivative(moved[0], moved[2], moved[3])
                                                         - expected_relative))),
    }
    original = density(connection, gradient, frame, frame_gradient, restoring)
    errors['complete_response_relative'] = abs(density(*moved, restoring) - original) / max(1., original)

    # Push forward a finite Gaussian probe law using the same samples and
    # weights.  The observable is transported with each sample, not refitted.
    samples = rng.normal(size=9)
    weights = np.exp(-samples**2 / 2)
    weights /= weights.sum()
    before, after = [], []
    for sample in samples:
        shifted = connection + sample * K
        before.append(density(shifted, gradient, frame, frame_gradient, restoring))
        after.append(density(*transport(shifted, gradient, frame, frame_gradient, g, dg, ddg), restoring))
    expected = float(weights @ np.asarray(before))
    errors['transported_source_expectation_relative'] = abs(float(weights @ np.asarray(after)) - expected) / max(1., expected)

    zero, zero_gradient = np.zeros_like(connection), np.zeros_like(gradient)
    identity = np.eye(3, dtype=complex)
    pure = transport(zero, zero_gradient, identity, zero, g, dg, ddg)
    errors['pure_frame_response'] = abs(density(*pure, restoring))
    fixed_frame = density(pure[0], pure[1], identity, zero, restoring)
    witnesses = {'inhomogeneous_term_norm': float(np.linalg.norm(K)),
                 'fixed_frame_response': fixed_frame, 'restoring_coefficient': restoring}
    tolerance = 2e-11
    passed = (all(value < tolerance for value in errors.values())
              and witnesses['inhomogeneous_term_norm'] > 1
              and fixed_frame > 0 and restoring > 0)
    return {'mechanism': 'common frame covariance and response invariance',
            'scope': 'local colour jets and a transported finite source probe law',
            'seed': seed, 'errors': errors, 'witnesses': witnesses,
            'absolute_error_tolerance': tolerance, 'passed': bool(passed)}


if __name__ == '__main__':
    results = [evaluate(seed) for seed in (794, 1267, 20261020)]
    print(json.dumps({'checks': results, 'passed': all(row['passed'] for row in results)}, indent=2))
    raise SystemExit(0 if all(row['passed'] for row in results) else 1)
