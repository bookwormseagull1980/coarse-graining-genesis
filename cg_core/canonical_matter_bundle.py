"""Concrete source matter fibres over the generated Hermitian four-carrier.

The root entry takes no bundle, local chart, width or coupling. The sixteen
source coordinates and their operators are obtained from the existing
elementary connector. Gauge matrices accepted by the frame routines are
configuration coordinates on this fixed carrier, not additional roots.
"""

from __future__ import annotations

import numpy as np

from cg_core.finite_connector import matter_generators


def _unitary(matrix):
    value = np.asarray(matrix, dtype=complex)
    if value.shape != (16, 16) or not np.isfinite(value).all():
        raise ValueError("a finite matrix on the complete source fibre is required")
    if not np.allclose(value.conj().T @ value, np.eye(16), rtol=1e-12, atol=1e-12):
        raise ValueError("a source-fibre frame change must be unitary")
    return value


def relative_transition(first, second):
    """Passive transition: components in the second frame to the first."""
    return _unitary(first).conj().T @ _unitary(second)


def components(frame, section):
    """Components of one complete matter vector in a local unitary frame."""
    vector = np.asarray(section, dtype=complex)
    if vector.shape != (16,) or not np.isfinite(vector).all():
        raise ValueError("a finite complete source vector is required")
    return _unitary(frame).conj().T @ vector


def generated_matter_bundle():
    """Construct the fixed fibre, its canonical frame and actual source action.

    The four Hermitian matrices give the source determinant form. The neutral
    line is located by the simultaneous kernel of the twelve existing colour,
    weak and hypercharge matrices; its index is not supplied to this entry.
    """
    generators = matter_generators()
    operators = np.asarray(list(generators.values()))
    dimension = operators.shape[1]
    identity = np.eye(dimension, dtype=complex)
    hermitian_basis = np.asarray([
        np.eye(2), [[0, 1], [1, 0]], [[0, 1j], [-1j, 0]], np.diag([1, -1]),
    ], dtype=complex)
    neutral = [i for i in range(dimension)
               if not np.any(operators[:, :, i]) and not np.any(operators[:, i, :])]
    if len(neutral) != 1:
        raise ArithmeticError("the complete source action must have one neutral line")
    neutral_projector = np.zeros_like(identity)
    neutral_projector[neutral[0], neutral[0]] = 1
    return {
        "base_dimension": len(hermitian_basis),
        "hermitian_basis": hermitian_basis,
        "fibre_dimension": dimension,
        "canonical_frame": identity,
        "source_generators": generators,
        "neutral_projector": neutral_projector,
        "charged_projector": identity - neutral_projector,
        "source_skew_adjoint_residual": float(np.max(np.abs(
            operators + operators.conj().transpose(0, 2, 1)))),
        "root_argument_count": 0,
    }


__all__ = ["generated_matter_bundle", "relative_transition", "components"]
