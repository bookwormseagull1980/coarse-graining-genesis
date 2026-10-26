"""Complete connection pullback and finite matter resolvent response.

The embedding, its derivative and the original connection describe one
field configuration in orthonormal source coordinates. Both the retained
connection and its orthogonal complement are evaluated. The resolvent
uses one complete Hermitian operator for the ordinary force correlation,
irreducible return and energy derivative. No mass-dependent source rate,
state, matching constant or parameter-store value is supplied here.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import null_space


def _matrix(value, name):
    result = np.asarray(value, dtype=complex)
    if result.ndim != 2 or not min(result.shape) or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a finite nonempty matrix")
    return result


def _embedding(value):
    result = _matrix(value, "embedding")
    if result.shape[1] > result.shape[0] or not np.allclose(
            result.conj().T @ result, np.eye(result.shape[1]), rtol=0, atol=2e-12):
        raise ValueError("embedding must have orthonormal columns")
    return result


def covariant_matter_pullback(embedding, embedding_derivative, connection):
    """Compress dR+A R together and retain its complete normal block.

    One direction may be passed as two matrices; several directions use
    arrays of shape (directions, ambient, retained) and
    (directions, ambient, ambient). The derivative is that of the same
    orthonormal embedding. Its tangency condition is checked explicitly.

    The returned Gram identity includes interference between dR and A R.
    A separate dR-only norm is not substituted for that complete response.
    """
    R = _embedding(embedding)
    dR, A = np.asarray(embedding_derivative, complex), np.asarray(connection, complex)
    if dR.ndim == 2 and A.ndim == 2:
        dR, A = dR[None], A[None]
    n, r = R.shape
    if (dR.ndim != 3 or not len(dR) or dR.shape[1:] != (n, r)
            or A.shape != (len(dR), n, n)
            or not np.isfinite(dR).all() or not np.isfinite(A).all()):
        raise ValueError("connection and readout jets must have matching finite dimensions")
    Rstar = R.conj().T
    tangent = Rstar @ dR + dR.conj().transpose(0, 2, 1) @ R
    if np.linalg.norm(tangent) > 2e-11 * max(1., np.linalg.norm(dR)):
        raise ValueError("readout derivative must be tangent to the orthonormal embeddings")
    if np.linalg.norm(A + A.conj().transpose(0, 2, 1)) > 2e-11 * max(1., np.linalg.norm(A)):
        raise ValueError("original connection must be skew-adjoint")
    original = A @ R
    covariant = dR + original
    retained = Rstar @ covariant
    complement = covariant - R @ retained
    adjoint = lambda x: x.conj().transpose(0, 2, 1)
    full_gram = adjoint(covariant) @ covariant
    retained_gram = adjoint(retained) @ retained
    complement_gram = adjoint(complement) @ complement
    moving_gram = adjoint(dR) @ dR
    original_gram = adjoint(original) @ original
    cross_gram = adjoint(dR) @ original + adjoint(original) @ dR
    return {
        "retained_connection": retained,
        "original_retained_connection": Rstar @ original,
        "moving_retained_connection": Rstar @ dR,
        "complement_connection": complement,
        "covariant_readout_jet": covariant,
        "full_gram": full_gram,
        "retained_gram": retained_gram,
        "complement_gram": complement_gram,
        "moving_gram": moving_gram,
        "original_gram": original_gram,
        "cross_gram": cross_gram,
        "residuals": {
            "orthogonal_complement": float(np.linalg.norm(Rstar @ complement)),
            "reconstruction": float(np.linalg.norm(covariant - R @ retained - complement)),
            "retained_skew_adjoint": float(np.linalg.norm(retained + adjoint(retained))),
            "gram_split": float(np.linalg.norm(full_gram - retained_gram - complement_gram)),
            "gram_interference": float(np.linalg.norm(full_gram-moving_gram-original_gram-cross_gram)),
        },
    }


def compressed_matter_response(operator, embedding, energy):
    """Full finite operator, complement return and its analytic derivative.

    The retarded parameter has Im(energy)>0. The complement is constructed
    from the supplied orthonormal embedding. Its propagation is the actual
    compression of the same operator. G and Sigma use the convention
    G(z)=R*(z-H)^(-1)R, Sigma=F*(z-Q H Q)^(-1)F.

    The ordinary full-force correlation T is evaluated independently of
    the complement formula. Sigma=T (I+G0 T)^(-1) removes reducible returns.
    The reported residuals are floating-point diagnostics, not enclosures.
    """
    H, R = _matrix(operator, "operator"), _embedding(embedding)
    n, r = R.shape
    if H.shape != (n, n) or not np.allclose(H, H.conj().T, rtol=1e-12, atol=1e-13):
        raise ValueError("operator must be Hermitian on the complete ambient space")
    z = complex(energy)
    if not np.isfinite(z) or z.imag <= 0:
        raise ValueError("retarded energy must be finite with positive imaginary part")
    retained = R.conj().T @ H @ R
    force = H @ R - R @ retained
    Q = null_space(R.conj().T)
    if Q.shape[1] != n-r:
        raise ArithmeticError("the orthogonal complement has the wrong dimension")
    if n > r:
        complement_operator = Q.conj().T @ H @ Q
        coupling = Q.conj().T @ force
        returned = np.linalg.solve(z*np.eye(n-r)-complement_operator, coupling)
        self_energy = coupling.conj().T @ returned
        self_energy_derivative = -coupling.conj().T @ np.linalg.solve(
            z*np.eye(n-r)-complement_operator, returned)
    else:
        complement_operator = np.zeros((0, 0), complex)
        coupling = np.zeros((0, r), complex)
        self_energy = np.zeros((r, r), complex)
        self_energy_derivative = self_energy.copy()
    pencil = z*np.eye(n)-H
    full_readout = np.linalg.solve(pencil, R)
    response = R.conj().T @ full_readout
    response_derivative = -R.conj().T @ np.linalg.solve(pencil, full_readout)
    force_propagation = np.linalg.solve(pencil, force)
    ordinary_force = force.conj().T @ force_propagation
    ordinary_force_derivative = -force.conj().T @ np.linalg.solve(pencil, force_propagation)
    G0 = np.linalg.solve(z*np.eye(r)-retained, np.eye(r))
    denominator = np.eye(r)+G0 @ ordinary_force
    self_energy_from_force = np.linalg.solve(denominator.T, ordinary_force.T).T
    from_complement = np.linalg.solve(z*np.eye(r)-retained-self_energy, np.eye(r))
    from_force = G0+G0 @ ordinary_force @ G0
    # The derivative of the same inverse pencil determines the kinetic response.
    derivative_from_complement = -from_complement @ (
        np.eye(r)-self_energy_derivative) @ from_complement
    C0 = force.conj().T @ force
    C1 = force.conj().T @ H @ force
    second_moment = R.conj().T @ H @ H @ R
    third_moment = R.conj().T @ H @ H @ H @ R
    difference = lambda a, b: float(np.linalg.norm(a-b)/max(1., np.linalg.norm(a), np.linalg.norm(b)))
    return {
        "retained_operator": retained, "complement_operator": complement_operator,
        "complement_coupling": coupling, "force": force,
        "response": response, "response_derivative": response_derivative,
        "self_energy": self_energy, "self_energy_derivative": self_energy_derivative,
        "ordinary_force_response": ordinary_force,
        "ordinary_force_response_derivative": ordinary_force_derivative,
        "force_moment_0": C0, "force_moment_1": C1,
        "ambient_dimension": n, "retained_dimension": r, "complement_dimension": n-r,
        "residuals": {
            "full_equation": difference(pencil @ full_readout, R),
            "force_orthogonal": float(np.linalg.norm(R.conj().T @ force)),
            "complement_response": difference(response, from_complement),
            "ordinary_force_response": difference(response, from_force),
            "irreducible_force_return": difference(self_energy, self_energy_from_force),
            "same_response_derivative": difference(response_derivative, derivative_from_complement),
            "force_moment_0": difference(C0, second_moment-retained @ retained),
            "force_moment_1": difference(C1, third_moment-retained @ second_moment
                                        -second_moment @ retained+retained @ retained @ retained),
        },
    }
