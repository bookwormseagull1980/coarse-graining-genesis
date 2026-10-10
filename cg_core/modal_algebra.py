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

"""Finite exact-support mode operations on round RP3, in normalized Haar units.

Scalar labels are (j,m,n), integer j>=0, with e=sqrt(2j+1) D^j_mn.
Coefficients can be scalars, matrices or matter vectors. Products retain
all output shells. Heat acts on scalar coefficients at fixed round radius
and fixed frame; the residual cocycle is resolution, not a physical-time
or Wetterich evolution. Spinor multiplication is evaluated on explicit
coupled scalar x spin-1/2 modes of one specified spin lift.
"""
from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
import math

import numpy as np
from scipy.linalg import block_diag


def _twice(x):
    if not math.isfinite(x) or 2 * x != round(2 * x):
        raise ValueError("spin and weight labels must be integer or half-integer")
    return int(round(2 * x))


@lru_cache(maxsize=32768)
def clebsch_gordan(j1, m1, j2, m2, J, M):
    """Condon--Shortley coefficient; Racah sum evaluated in exact rationals.

    Only the final square root is rounded. Integer factorial arguments
    avoid a symbolic runtime dependency and large floating cancellations.
    """
    twice = tuple(_twice(x) for x in (j1, m1, j2, m2, J, M))
    a, ma, b, mb, c, mc = twice
    if min(a, b, c) < 0:
        raise ValueError("spins must be nonnegative")
    if (ma + mb != mc or any(abs(m) > j or (j - m) % 2 for j, m in
                             ((a, ma), (b, mb), (c, mc))) or
            c < abs(a - b) or c > a + b or (a + b - c) % 2):
        return 0.0
    fact = math.factorial
    p, q, r = (c + a - b) // 2, (c - a + b) // 2, (a + b - c) // 2
    prefactor = Fraction((c + 1) * fact(p) * fact(q) * fact(r), fact((a + b + c) // 2 + 1))
    for label, weight in ((c, mc), (a, ma), (b, mb)):
        prefactor *= fact((label + weight) // 2) * fact((label - weight) // 2)
    u, v = (a - ma) // 2, (b + mb) // 2
    w, x = (c - b + ma) // 2, (c - a - mb) // 2
    total = Fraction(0)
    for k in range(max(0, -w, -x), min(r, u, v) + 1):
        total += Fraction((-1) ** k, fact(k) * fact(r - k) * fact(u - k) *
                          fact(v - k) * fact(w + k) * fact(x + k))
    if not total:
        return 0.0
    return math.copysign(math.sqrt(float(prefactor * total * total)), total)


@lru_cache(maxsize=128)
def spin_matrices(j):
    """Hermitian Jx,Jy,Jz, in increasing weight order; returned read-only."""
    twice = _twice(j)
    if twice < 0:
        raise ValueError("spin must be nonnegative")
    weights = np.arange(twice + 1) - j
    raising = np.zeros((twice + 1, twice + 1), complex)
    for i, m in enumerate(weights[:-1]):
        raising[i + 1, i] = math.sqrt((j - m) * (j + m + 1))
    matrices = ((raising + raising.conj().T) / 2,
                (raising - raising.conj().T) / (2j), np.diag(weights).astype(complex))
    for matrix in matrices:
        matrix.setflags(write=False)
    return matrices


def _mode(label):
    if len(label) != 3 or any(not isinstance(x, (int, np.integer)) for x in label):
        raise ValueError("scalar mode requires three integer labels (j,m,n)")
    j, m, n = map(int, label)
    if j < 0 or max(abs(m), abs(n)) > j:
        raise ValueError("invalid scalar mode")
    return j, m, n


@lru_cache(maxsize=32768)
def mode_product(alpha, beta):
    """All nonzero coefficients of e_alpha e_beta, with no output cutoff."""
    j, m, n = _mode(alpha)
    k, a, b = _mode(beta)
    result = []
    for J in range(abs(j - k), j + k + 1):
        coefficient = (math.sqrt((2 * j + 1) * (2 * k + 1) / (2 * J + 1)) *
                       clebsch_gordan(j, m, k, a, J, m + a) *
                       clebsch_gordan(j, n, k, b, J, n + b))
        if coefficient:
            result.append(((J, m + a, n + b), coefficient))
    return tuple(result)


def _accumulate(out, label, value):
    value = np.asarray(value, dtype=complex)
    if not np.all(np.isfinite(value)):
        raise ValueError("non-finite mode coefficient")
    out[label] = out.get(label, 0) + value


def _clean(field):
    return {label: value for label, value in field.items() if np.any(value != 0)}


def add(*fields):
    result = {}
    for field in fields:
        for label, value in field.items():
            _accumulate(result, label, value)
    return _clean(result)


def scale(field, factor):
    return _clean({label: np.asarray(value) * factor for label, value in field.items()})


def multiply(left, right):
    """Scalar, matrix--matrix or matrix--vector product with complete support."""
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            x, y = np.asarray(x), np.asarray(y)
            value = x * y if x.ndim == 0 or y.ndim == 0 else x @ y
            for label, coefficient in mode_product(a, b):
                _accumulate(result, label, coefficient * value)
    return _clean(result)


def adjoint(field):
    """Pointwise Hermitian adjoint, including conjugation of harmonic modes."""
    result = {}
    for label, value in field.items():
        j, m, n = _mode(label)
        _accumulate(result, (j, -m, -n), (-1.0) ** (m - n) * np.asarray(value).conj().T)
    return _clean(result)


def mode_norm(field):
    """Haar L2/Hilbert--Schmidt norm of a finite coefficient field."""
    return math.sqrt(sum(float(np.vdot(value, value).real) for value in field.values()))


def eigenvalue(label, L=1.0):
    j, _, _ = _mode(label)
    if not math.isfinite(L) or L <= 0:
        raise ValueError("a positive finite fixed radius is required")
    return 4 * j * (j + 1) / L**2


def heat(field, t, *, L=1.0):
    if not math.isfinite(t) or t < 0:
        raise ValueError("nonnegative finite heat parameter required")
    return _clean({label: np.asarray(value) * math.exp(-t * eigenvalue(label, L))
                   for label, value in field.items()})


def derivative(field, axis, *, L=1.0):
    """E_a on the right matrix index, [E_a,E_b]=(2/L) epsilon_abc E_c."""
    if axis not in (0, 1, 2) or not math.isfinite(L) or L <= 0:
        raise ValueError("axis 0,1,2 and positive finite radius required")
    result = {}
    for label, value in field.items():
        j, m, n = _mode(label)
        generator = (-2j / L) * spin_matrices(j)[axis]
        for index, coefficient in enumerate(generator[:, n + j]):
            if coefficient:
                _accumulate(result, (j, m, index - j), coefficient * np.asarray(value))
    return _clean(result)


def represent_connection(coordinates, generators):
    """Apply the same Lie-algebra coordinates to an explicit representation."""
    generators = np.asarray(generators, dtype=complex)
    if generators.ndim != 3 or generators.shape[1] != generators.shape[2]:
        raise ValueError("an array of square representation matrices is required")
    if not np.allclose(generators + generators.conj().transpose(0, 2, 1), 0, atol=1e-13):
        raise ValueError("connection generators must be skew-adjoint")
    result = []
    for component in coordinates:
        field = {}
        for label, value in component.items():
            value = np.asarray(value)
            if value.shape != (len(generators),):
                raise ValueError("Lie-algebra coordinate dimension mismatch")
            _accumulate(field, label, np.einsum("a,aij->ij", value, generators))
        result.append(_clean(field))
    if len(result) != 3:
        raise ValueError("three connection components required")
    return tuple(result)


def curvature(connection, *, L=1.0):
    """F_ab in cyclic order (01,12,20), in the same fixed round coframe."""
    if len(connection) != 3:
        raise ValueError("three connection components required")
    answer = []
    for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        answer.append(add(derivative(connection[b], a, L=L),
                          scale(derivative(connection[a], b, L=L), -1),
                          scale(connection[c], -2 / L),
                          multiply(connection[a], connection[b]),
                          scale(multiply(connection[b], connection[a]), -1)))
    return tuple(answer)


def matter_derivative(connection, matter, *, L=1.0):
    if len(connection) != 3:
        raise ValueError("three connection components required")
    return tuple(add(derivative(matter, a, L=L), multiply(connection[a], matter))
                 for a in range(3))


def joint_response(connection, matter, *, L=1.0):
    """Connection matrices must already be in the actual matter representation."""
    return curvature(connection, L=L) + matter_derivative(connection, matter, L=L)


def joint_defect(connection, matter, t, *, L=1.0):
    original = joint_response(connection, matter, L=L)
    resolved = joint_response(tuple(heat(a, t, L=L) for a in connection), heat(matter, t, L=L), L=L)
    return tuple(add(heat(before, t, L=L), scale(after, -1)) for before, after in zip(original, resolved))


def joint_resolution(connection, matter, residual, t, *, L=1.0):
    """Triangular Gaussian resolution and its six complete residual fields."""
    if len(residual) != 6:
        raise ValueError("three curvature and three matter residuals required")
    defect = joint_defect(connection, matter, t, L=L)
    updated = tuple(add(heat(r, t, L=L), c) for r, c in zip(residual, defect))
    return tuple(heat(a, t, L=L) for a in connection), heat(matter, t, L=L), updated


def joint_defect_integral(connection, matter, t, *, L=1.0, quadrature_order=24):
    """Independent Duhamel evaluation using frame derivatives and Gauss nodes."""
    if not math.isfinite(t) or t < 0 or quadrature_order < 1:
        raise ValueError("nonnegative t and positive quadrature order required")
    nodes, weights = np.polynomial.legendre.leggauss(quadrature_order)
    result = ({}, {}, {}, {}, {}, {})
    for node, weight in zip(nodes, weights):
        u = t * (node + 1) / 2
        A = tuple(heat(a, u, L=L) for a in connection)
        psi = heat(matter, u, L=L)
        dA = [[derivative(A[a], c, L=L) for c in range(3)] for a in range(3)]
        dpsi = [derivative(psi, c, L=L) for c in range(3)]
        integrand = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            integrand.append(add(*(add(multiply(dA[a][c], dA[b][c]),
                                      scale(multiply(dA[b][c], dA[a][c]), -1)) for c in range(3))))
        integrand.extend(add(*(multiply(dA[a][c], dpsi[c]) for c in range(3))) for a in range(3))
        result = tuple(add(old, scale(heat(value, t - u, L=L), t * weight))
                       for old, value in zip(result, integrand))
    return result


def spinor_basis(max_j):
    """Selected spin lift in a left-trivialized spin frame.

    Labels (j,m,J,M) couple the right scalar index n with spin 1/2.
    J=j+1/2 gives +(2j+3/2)/L; J=j-1/2 gives -(2j+1/2)/L.
    Every n parity of one complete signed Dirac tower is retained.
    """
    if not isinstance(max_j, int) or max_j < 0:
        raise ValueError("nonnegative integer maximum scalar spin required")
    return tuple((j, m, J, M / 2) for j in range(max_j + 1)
                 for m in range(-j, j + 1) for J in (j - .5, j + .5) if J >= 0
                 for M in range(-int(2 * J), int(2 * J) + 1, 2))


def spinor_dirac_value(label, *, L=1.0):
    j, m, J, M = label
    if label not in spinor_basis(j) or not math.isfinite(L) or L <= 0:
        raise ValueError("valid coupled spinor label and positive radius required")
    return ((2 * j + 1.5) if J == j + .5 else -(2 * j + .5)) / L


def spinor_multiplication(scalar_field, inputs, outputs):
    """Actual spinor Gaunt matrix for a finite scalar multiplication operator.

    The output basis is caller supplied; choose max_j_out >= max_j_in+
    max_j_scalar to avoid discarding multiplication support. Matrix element
    sums use the two spin components, not merely allowed representations.
    """
    result = np.zeros((len(outputs), len(inputs)), complex)
    for col, incoming in enumerate(inputs):
        j, m, J, M = incoming
        spinor_dirac_value(incoming)
        for row, outgoing in enumerate(outputs):
            k, a, K, A = outgoing
            spinor_dirac_value(outgoing)
            for scalar, value in scalar_field.items():
                if np.ndim(value) != 0:
                    raise ValueError("spinor multiplication requires scalar coefficients")
                for s in (-.5, .5):
                    n, b = M - s, A - s
                    if n != int(n) or b != int(b) or abs(n) > j or abs(b) > k:
                        continue
                    cin = clebsch_gordan(j, n, .5, s, J, M)
                    cout = clebsch_gordan(k, b, .5, s, K, A)
                    coefficients = dict(mode_product(scalar, (j, m, int(n))))
                    result[row, col] += value * cin * cout * coefficients.get((k, a, int(b)), 0)
    return result


def signed_cross_blocks(matrix, input_labels, output_labels):
    """Return actual sign-projected matrix blocks; no assumption of invariance."""
    matrix = np.asarray(matrix, dtype=complex)
    if matrix.shape != (len(output_labels), len(input_labels)):
        raise ValueError("matrix and signed basis dimensions disagree")
    signs_in = np.array([spinor_dirac_value(x) > 0 for x in input_labels])
    signs_out = np.array([spinor_dirac_value(x) > 0 for x in output_labels])
    return {(out, inc): matrix[np.ix_(signs_out == (out == "+"), signs_in == (inc == "+"))]
            for out in ("+", "-") for inc in ("+", "-")}


def symmetric_square_basis(dimension):
    """Isometry Sym2(C^d) -> C^d tensor C^d in lexicographic i<=j order."""
    if not isinstance(dimension, int) or dimension < 1:
        raise ValueError("positive integer dimension required")
    basis = np.zeros((dimension**2, dimension * (dimension + 1) // 2), complex)
    for column, (i, j) in enumerate((i, j) for i in range(dimension) for j in range(i, dimension)):
        if i == j:
            basis[i * dimension + j, column] = 1
        else:
            basis[i * dimension + j, column] = basis[j * dimension + i, column] = 1 / math.sqrt(2)
    return basis


def killing_two_body():
    """Actual 6 -> 21 Killing representation, Casimirs and parity exchange.

    The additive levels 8+C2 are a specified candidate response, not a
    calculation of bound-state energies or external J^PC identifications.
    """
    basis = symmetric_square_basis(6)
    identity = np.eye(6)
    zero = np.zeros((3, 3))
    JL = tuple(block_diag(j, zero) for j in spin_matrices(1))
    JR = tuple(block_diag(zero, j) for j in spin_matrices(1))
    lifted = [tuple(basis.conj().T @ (np.kron(j, identity) + np.kron(identity, j)) @ basis
                    for j in factor) for factor in (JL, JR)]
    CL, CR = (sum(j @ j for j in factor) for factor in lifted)
    projectors = {}
    eye = np.eye(21)
    for jl, jr in ((0, 0), (1, 1), (2, 0), (0, 2)):
        projection = eye.astype(complex)
        for operator, target in ((CL, jl * (jl + 1)), (CR, jr * (jr + 1))):
            for other in (0, 2, 6):
                if other != target:
                    projection = projection @ ((operator - other * eye) / (target - other))
        projectors[(jl, jr)] = (projection + projection.conj().T) / 2
    exchange = np.block([[zero, np.eye(3)], [np.eye(3), zero]])
    parity = basis.conj().T @ np.kron(exchange, exchange) @ basis
    return {"basis": basis, "left_generators": lifted[0], "right_generators": lifted[1],
            "casimir": 2 * (CL + CR), "projectors": projectors,
            "parity": parity, "candidate_operator": 8 * eye + 2 * (CL + CR)}


def killing_source_weights(source):
    source = np.asarray(source, dtype=complex)
    if source.shape != (21,) or not np.all(np.isfinite(source)):
        raise ValueError("finite source in the 21-dimensional symmetric carrier required")
    data = killing_two_body()
    return {label: float(np.vdot(projector @ source, projector @ source).real)
            for label, projector in data["projectors"].items()}


def colour_singlet_lift(source, *, colours=8):
    """Symmetric Killing source lifted with normalized delta_AB/sqrt(8)."""
    source = np.asarray(source, dtype=complex)
    if source.shape != (21,) or not np.all(np.isfinite(source)) or colours != 8:
        raise ValueError("finite Sym2(K) source and SU(3) adjoint colour dimension 8 required")
    orbital = (symmetric_square_basis(6) @ source).reshape(6, 6)
    return np.einsum("ij,ab->iajb", orbital, np.eye(colours) / math.sqrt(colours))


def colour_singlet_projection(two_leg_source):
    """Contract the actual colour singlet, then report symmetric projection loss."""
    source = np.asarray(two_leg_source, dtype=complex)
    if source.shape != (6, 8, 6, 8) or not np.all(np.isfinite(source)):
        raise ValueError("finite K-adjoint x K-adjoint source required")
    orbital = np.einsum("iaja->ij", source) / math.sqrt(8)
    coefficients = symmetric_square_basis(6).conj().T @ orbital.reshape(36)
    return {"coefficients": coefficients,
            "antisymmetric_norm": float(np.linalg.norm((orbital - orbital.T) / 2)),
            "retained_norm_squared": float(np.vdot(coefficients, coefficients).real)}
