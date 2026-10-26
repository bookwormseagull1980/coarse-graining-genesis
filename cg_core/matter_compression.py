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


def compressed_matter_poles(operator, embedding, *, resolution=1e-11):
    """Resolve all energies and residues of one finite matter response.

    Energies and amplitudes come from the complete Hermitian operator.
    Close energies are reported as an unresolved cluster with their full
    interval and total residue; no mean energy replaces them. The complete
    eigensystem remains available for exact finite spectral evaluation.

    At each visible eigenvalue outside the complementary spectrum, the
    same complement gives Sigma and I-Sigma'. The latter is the Gram form
    of the lifted eigenvector and fixes its residue. A complementary pole
    only disables this Schur diagnostic: the full spectral answer survives.

    These are the spectrum and weights of the supplied operator, in its
    energy units. The function assigns neither a source state nor a clock
    conversion and does not identify a positive Dirac energy with a lepton
    mass. Residuals and clustering are floating-point diagnostics.
    """
    H, R = _matrix(operator, "operator"), _embedding(embedding)
    n, r = R.shape
    if H.shape != (n, n) or not np.allclose(H, H.conj().T, rtol=1e-12, atol=1e-13):
        raise ValueError("operator must be Hermitian on the complete ambient space")
    resolution = float(resolution)
    if not np.isfinite(resolution) or resolution <= 0:
        raise ValueError("resolution must be finite and positive")
    energies, states = np.linalg.eigh(H)
    amplitudes = R.conj().T @ states
    A = R.conj().T @ H @ R
    Q = null_space(R.conj().T)
    if Q.shape[1] != n-r:
        raise ArithmeticError("the orthogonal complement has the wrong dimension")
    C = Q.conj().T @ H @ Q
    B = Q.conj().T @ H @ R
    complement_energies, complement_states = np.linalg.eigh(C)
    coupling = complement_states.conj().T @ B
    energy_scale = max(1., float(np.max(np.abs(energies))))
    gap_tolerance = resolution*energy_scale
    # Compare to the start of a cluster, avoiding transitive chaining of
    # distinct levels across an arbitrarily large total energy interval.
    clusters = []
    start = 0
    for stop in range(1, n+1):
        if stop == n or energies[stop]-energies[start] > gap_tolerance:
            cluster_amplitudes = amplitudes[:, start:stop]
            residue = cluster_amplitudes @ cluster_amplitudes.conj().T
            clusters.append({
                "energy_interval": (float(energies[start]), float(energies[stop-1])),
                "energy_eigenvalues": energies[start:stop].copy(),
                "multiplicity": stop-start,
                "residue": residue,
                "visible_weight": float(np.trace(residue).real),
                "visible": bool(np.trace(residue).real > resolution**2),
                "unresolved_cluster": bool(stop-start > 1),
            })
            start = stop
    diagnostics = []
    for index, E in enumerate(energies):
        u = amplitudes[:, index]
        weight = float(np.vdot(u, u).real)
        if weight <= resolution**2:
            continue
        distance = (float(np.min(np.abs(E-complement_energies)))
                    if len(complement_energies) else float("inf"))
        if distance <= gap_tolerance:
            diagnostics.append({"eigenvalue_index": index, "energy": float(E),
                                "complement_distance": distance,
                                "schur_available": False})
            continue
        if len(complement_energies):
            W = complement_states @ (coupling/(E-complement_energies[:, None]))
        else:
            W = np.zeros((0, r), complex)
        Sigma = B.conj().T @ W
        metric = np.eye(r)+W.conj().T @ W
        kernel = E*np.eye(r)-A-Sigma
        direction = u/np.sqrt(weight)
        slope = float(np.vdot(direction, metric @ direction).real)
        predicted_residue = np.outer(direction, direction.conj())/slope
        residue = np.outer(u, u.conj())
        lifted = R @ u+Q @ (W @ u)
        diagnostics.append({
            "eigenvalue_index": index, "energy": float(E),
            "complement_distance": distance, "schur_available": True,
            "self_energy": Sigma, "inverse_response": kernel,
            "inverse_response_derivative": metric,
            "retained_weight": weight, "normalized_slope": slope,
            "residuals": {
                "reduced_equation": float(np.linalg.norm(kernel @ u)/energy_scale),
                "full_eigenvector_lift": float(np.linalg.norm(lifted-states[:, index])),
                "full_eigenvector_norm": abs(float(np.vdot(u, metric @ u).real)-1.),
                "residue_from_same_derivative": float(np.linalg.norm(predicted_residue-residue)),
            },
        })
    total_residue = amplitudes @ amplitudes.conj().T
    first_moment = (amplitudes*energies) @ amplitudes.conj().T
    return {
        "energy_eigenvalues": energies, "readout_amplitudes": amplitudes,
        "pole_blocks": clusters, "pole_diagnostics": diagnostics,
        "retained_operator": A, "complement_eigenvalues": complement_energies,
        "ambient_dimension": n, "retained_dimension": r,
        "resolution": resolution, "energy_resolution": gap_tolerance,
        "residuals": {
            "total_spectral_weight": float(np.linalg.norm(total_residue-np.eye(r))),
            "first_spectral_moment": float(np.linalg.norm(first_moment-A)/energy_scale),
        },
    }


def joint_matter_response(hamiltonian, state, annihilators, energy):
    """Retarded CAR response in one finite stationary interacting state.

    The Hamiltonian acts on the complete source-and-matter Hilbert space.
    The density matrix is its stationary joint state, not a product of
    separately normalized source and matter states. Annihilation operators
    act on that same space and obey the complete CAR. No occupation law,
    source frequency, temperature or interaction is assigned by this API.

    Two Hilbert-Schmidt copies implement
        <X,Y> = Tr rho (X Y^dagger + Y^dagger X).
    Their embedding uses c_i^dagger sqrt(rho) and sqrt(rho) c_i^dagger.
    The common Liouvillian is [H, .]. This construction also covers
    noncommuting joint states within degenerate energy spaces without
    discarding coherences or needing simultaneous numerical eigenvectors.

    The returned transition amplitudes and real frequencies can be used
    for full finite spectral evaluation. G, G', the mean, force moments,
    ordinary force response and irreducible return use these same data.
    Residuals are floating-point diagnostics, not certified enclosures.
    """
    H, rho = _matrix(hamiltonian, "hamiltonian"), _matrix(state, "state")
    n = H.shape[0]
    if H.shape != (n, n) or not np.allclose(H, H.conj().T, rtol=1e-12, atol=1e-13):
        raise ValueError("hamiltonian must be Hermitian on the complete joint space")
    if rho.shape != (n, n) or not np.allclose(rho, rho.conj().T, rtol=1e-12, atol=1e-13):
        raise ValueError("state must be Hermitian on the complete joint space")
    probabilities, state_vectors = np.linalg.eigh(rho)
    if probabilities[0] < -1e-12 or abs(np.trace(rho)-1) > 1e-12:
        raise ValueError("state must be positive with unit trace")
    scale = max(1., float(np.linalg.norm(H)))
    stationarity = float(np.linalg.norm(H @ rho-rho @ H)/scale)
    if stationarity > 1e-11:
        raise ValueError("joint state must be stationary under the same Hamiltonian")
    operators = np.asarray(annihilators, complex)
    if (operators.ndim != 3 or not len(operators) or operators.shape[1:] != (n, n)
            or not np.isfinite(operators).all()):
        raise ValueError("annihilators must be finite operators on the complete joint space")
    r = len(operators)
    car_error = 0.
    for i, ci in enumerate(operators):
        for j, cj in enumerate(operators):
            car_error = max(car_error,
                float(np.linalg.norm(ci @ cj+cj @ ci)),
                float(np.linalg.norm(ci @ cj.conj().T+cj.conj().T @ ci
                                     -(np.eye(n) if i == j else 0))))
    if car_error > 1e-11*max(1., np.sqrt(n)):
        raise ValueError("annihilators must satisfy CAR on the complete joint space")
    z = complex(energy)
    if not np.isfinite(z) or z.imag <= 0:
        raise ValueError("retarded energy must be finite with positive imaginary part")
    sqrt_state = (state_vectors*np.sqrt(np.maximum(probabilities, 0.))) @ state_vectors.conj().T
    levels, basis = np.linalg.eigh(H)
    sqrt_state = basis.conj().T @ sqrt_state @ basis
    frequencies = levels[:, None]-levels[None, :]
    frequencies = np.tile(frequencies.ravel(), 2)
    columns = []
    for c in operators:
        creator = basis.conj().T @ c.conj().T @ basis
        columns.append(np.concatenate(((creator @ sqrt_state).ravel(),
                                       (sqrt_state @ creator).ravel())))
    R = np.column_stack(columns)
    gram = R.conj().T @ R
    if not np.allclose(gram, np.eye(r), rtol=0, atol=2e-11):
        raise ArithmeticError("joint CAR response has lost its unit equal-time normalization")
    response = R.conj().T @ (R/(z-frequencies[:, None]))
    response_derivative = -R.conj().T @ (R/(z-frequencies[:, None])**2)
    mean = R.conj().T @ (frequencies[:, None]*R)
    force = frequencies[:, None]*R-R @ mean
    ordinary_force = force.conj().T @ (force/(z-frequencies[:, None]))
    ordinary_force_derivative = -force.conj().T @ (force/(z-frequencies[:, None])**2)
    inverse = np.linalg.solve(response, np.eye(r))
    self_energy = z*np.eye(r)-mean-inverse
    self_energy_derivative = np.eye(r)+inverse @ response_derivative @ inverse
    G0 = np.linalg.solve(z*np.eye(r)-mean, np.eye(r))
    from_force = G0+G0 @ ordinary_force @ G0
    force_denominator = np.eye(r)+G0 @ ordinary_force
    irreducible_from_force = np.linalg.solve(force_denominator.T, ordinary_force.T).T
    # Direct equal-time CAR commutators independently check the first two
    # moments of the joint transition representation.
    currents = [c @ H-H @ c for c in operators]
    first = np.array([[np.trace(rho @ (current @ c.conj().T+c.conj().T @ current))
                       for c in operators] for current in currents])
    second = np.array([[np.trace(rho @ (left @ right.conj().T+right.conj().T @ left))
                        for right in currents] for left in currents])
    force_moment_0 = force.conj().T @ force
    force_moment_1 = force.conj().T @ (frequencies[:, None]*force)
    return {
        "response": response, "response_derivative": response_derivative,
        "retained_operator": mean, "self_energy": self_energy,
        "self_energy_derivative": self_energy_derivative,
        "ordinary_force_response": ordinary_force,
        "ordinary_force_response_derivative": ordinary_force_derivative,
        "force_moment_0": force_moment_0, "force_moment_1": force_moment_1,
        "transition_energies": frequencies, "transition_embedding": R,
        "joint_dimension": n, "retained_dimension": r,
        "residuals": {
            "joint_state_stationarity": stationarity, "complete_car": car_error,
            "equal_time_normalization": float(np.linalg.norm(gram-np.eye(r))),
            "first_commutator_moment": float(np.linalg.norm(mean-first)/scale),
            "second_commutator_moment": float(np.linalg.norm(
                force_moment_0+mean @ mean-second)/scale**2),
            "force_orthogonal": float(np.linalg.norm(R.conj().T @ force)/scale),
            "ordinary_force_reconstruction": float(np.linalg.norm(response-from_force)),
            "irreducible_return": float(np.linalg.norm(self_energy-irreducible_from_force)/scale),
        },
    }


def precise_matter_response(operator, embedding, energy, *, digits=80, guard_digits=20):
    """Arbitrary-precision full response, checked at two working precisions.

    Decimal strings and (real, imaginary) pairs retain their supplied
    precision. Python/numpy floating inputs retain only the information
    present in those inputs. No array is converted through numpy here.

    The full linear systems are first solved at digits+guard_digits and
    digits+2*guard_digits. Working precision is increased if their results
    do not agree to the requested accuracy. A nonorthogonal readout uses its
    actual Gram S: G0^-1=z S^-1-S^-1(R^dagger H R)S^-1. This avoids
    silently reorthogonalizing rounded readouts. The same G' determines
    the inverse-response derivative and irreducible-return derivative.

    Matrices are returned as decimal (real, imaginary) pairs. Refinement
    changes and residuals measure arithmetic consistency. They are not
    interval enclosures, spectral truncation bounds or uncertainties in H.
    """
    import mpmath

    if (isinstance(digits, bool) or not isinstance(digits, int) or digits < 30
            or isinstance(guard_digits, bool) or not isinstance(guard_digits, int)
            or guard_digits < 10):
        raise ValueError("at least 30 output digits and 10 guard digits are required")

    def evaluate(precision):
        ctx = mpmath.mp.clone()
        ctx.dps = precision

        def scalar(value):
            if isinstance(value, (tuple, list)) and len(value) == 2:
                result = ctx.mpc(ctx.mpf(value[0]), ctx.mpf(value[1]))
            elif isinstance(value, (complex, np.complexfloating)):
                result = ctx.mpc(repr(float(value.real)), repr(float(value.imag)))
            else:
                result = ctx.mpc(value)
            if not ctx.isfinite(result):
                raise ValueError("all response inputs must be finite")
            return result

        def matrix(value, name):
            rows = value.tolist() if isinstance(value, np.ndarray) else value
            try:
                lengths = [len(row) for row in rows]
                if not lengths or not min(lengths) or len(set(lengths)) != 1:
                    raise ValueError
                return ctx.matrix([[scalar(x) for x in row] for row in rows])
            except (TypeError, ValueError, IndexError) as exc:
                raise ValueError(f"{name} must be a finite nonempty rectangular matrix") from exc

        H, R, z = matrix(operator, "operator"), matrix(embedding, "embedding"), scalar(energy)
        if H.rows != H.cols or R.rows != H.rows or R.cols > R.rows:
            raise ValueError("complete operator and readout dimensions must agree")
        if z.imag <= 0:
            raise ValueError("retarded energy must have positive imaginary part")
        tolerance = ctx.power(10, -precision+5)
        if ctx.norm(H-H.H) > tolerance*max(1, ctx.norm(H)):
            raise ValueError("operator must be Hermitian at the supplied precision")
        A = z*ctx.eye(H.rows)-H

        def solve(columns):
            result = ctx.matrix(H.rows, columns.cols)
            for j in range(columns.cols):
                result[:, j] = ctx.lu_solve(A, columns[:, j])
            return result

        X = solve(R)
        Y = solve(X)
        G, dG = R.H*X, -R.H*Y
        S = R.H*R
        try:
            S_inv, G_inv = ctx.inverse(S), ctx.inverse(G)
        except ZeroDivisionError as exc:
            raise ValueError("readout must have independent columns") from exc
        mean = R.H*H*R
        inverse_derivative = -G_inv*dG*G_inv
        result = {
            "response": G, "response_derivative": dG,
            "readout_gram": S, "first_spectral_moment": mean,
            "inverse_response_derivative": inverse_derivative,
            "self_energy": z*S_inv-S_inv*mean*S_inv-G_inv,
            "self_energy_derivative": S_inv-inverse_derivative,
        }
        residual_X, residual_Y = ctx.norm(A*X-R), ctx.norm(A*Y-X)
        # Hermiticity gives ||(z-H)^-1|| <= 1/Im z. These are
        # a posteriori formulas evaluated numerically, not outward-rounded
        # error certificates. No truncation error is hidden inside them.
        result["residuals"] = {
            "full_linear_system": residual_X,
            "derivative_linear_system": residual_Y,
            "response_residual_error_estimate": ctx.norm(R)*residual_X/z.imag,
            "derivative_residual_error_estimate": ctx.norm(R)*(
                residual_Y/z.imag+residual_X/z.imag**2),
        }
        return ctx, result

    precision = digits+guard_digits
    tried_precisions = []
    for _ in range(8):
        _, lower = evaluate(precision)
        ctx, higher = evaluate(precision+guard_digits)
        tried_precisions.extend((precision, precision+guard_digits))
        changes = {name: ctx.norm(higher[name]-ctx.matrix(lower[name].tolist()))
                   for name in higher if name != "residuals"}
        tolerance = ctx.power(10, -digits-3)
        if all(change <= tolerance*max(1, ctx.norm(higher[name]))
               for name, change in changes.items()):
            break
        precision += max(2*guard_digits, precision//2)
    else:
        raise ArithmeticError("response did not stabilize to the requested precision")
    encode = lambda matrix: [[(ctx.nstr(matrix[i, j].real, digits),
                               ctx.nstr(matrix[i, j].imag, digits))
                              for j in range(matrix.cols)] for i in range(matrix.rows)]
    return {
        **{name: encode(value) for name, value in higher.items() if name != "residuals"},
        "digits": digits, "working_precisions": [precision, precision+guard_digits],
        "tried_precisions": tried_precisions,
        "arithmetic_refinement_changes": {name: ctx.nstr(value, digits)
                                           for name, value in changes.items()},
        "residuals": {name: ctx.nstr(value, digits)
                      for name, value in higher["residuals"].items()},
        "interval_certificate": False,
    }
