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

"""Finite full-matter operators and source responses of Guo (2026d), Sections 4--5.

Each elementary generation has 8 left and 8 right coordinates, ordered as
(three colours, one lepton) x (up, down). The neutral right coordinate is 14.
Its charged quotient is appropriate for descending charge operators; an odd
Higgs connector requires the full operator or energy-dependent elimination.
All weighted matrices and kinetic forms are explicit inputs, not predictions
of flavour structure. No parameter store or observational input is accessed.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import block_diag, null_space


def _matrix(value, *, hermitian=False):
    value = np.asarray(value, dtype=complex)
    if value.ndim != 2 or not np.all(np.isfinite(value)):
        raise ValueError("a finite matrix is required")
    if hermitian and (value.shape[0] != value.shape[1] or
                      not np.allclose(value, value.conj().T, rtol=1e-13, atol=1e-14)):
        raise ValueError("a Hermitian square matrix is required")
    return value


def chiral_operator(transfer, *, left_block=None, right_block=None):
    """General Hermitian chiral block; no equal-mass identity is presumed."""
    transfer = _matrix(transfer)
    nl, nr = transfer.shape
    left = np.zeros((nl, nl)) if left_block is None else _matrix(left_block, hermitian=True)
    right = np.zeros((nr, nr)) if right_block is None else _matrix(right_block, hermitian=True)
    if left.shape != (nl, nl) or right.shape != (nr, nr):
        raise ValueError("diagonal and transfer block dimensions disagree")
    return np.block([[left, transfer], [transfer.conj().T, right]])


def elementary_connector(H, *, generations=1):
    """Actual quaternionic doublet and full operator, with explicit neutral basis.

    H=(H_up,H_down); h=(i sigma_2 H*, H). Multiple generations are
    independent copies, not a calculation of their Yukawa mixing.
    """
    H = np.asarray(H, dtype=complex)
    if H.shape != (2,) or not np.all(np.isfinite(H)):
        raise ValueError("a finite complex doublet is required")
    if not isinstance(generations, int) or isinstance(generations, bool) or generations < 1:
        raise ValueError("generations must be a positive integer")
    h = np.column_stack(([H[1].conjugate(), -H[0].conjugate()], H))
    transfer = np.kron(np.eye(4), h)
    single = chiral_operator(transfer)
    operator = block_diag(*([single] * generations))
    neutral = np.eye(16 * generations)[:, [16 * i + 14 for i in range(generations)]]
    return {"doublet": H, "reduced_connector": h, "transfer": transfer,
            "operator": operator, "neutral_basis": neutral,
            "amplitude_squared": float(np.vdot(H, H).real),
            "generations": generations}


def canonical_transfer(transfer, kinetic_left, kinetic_right, *, kinetic_scalar=1.0):
    """Z_L^(-1/2) T Z_R^(-1/2)/sqrt(Z_H) for supplied positive kinetic forms."""
    transfer = _matrix(transfer)
    inverses = []
    for kinetic, dimension in zip((kinetic_left, kinetic_right), transfer.shape):
        kinetic = _matrix(kinetic, hermitian=True)
        if kinetic.shape != (dimension, dimension):
            raise ValueError("kinetic and transfer dimensions disagree")
        values, vectors = np.linalg.eigh(kinetic)
        if np.min(values) <= 0:
            raise ValueError("kinetic forms must be positive definite")
        inverses.append((vectors / np.sqrt(values)) @ vectors.conj().T)
    if not np.isfinite(kinetic_scalar) or kinetic_scalar <= 0:
        raise ValueError("positive finite scalar kinetic normalization required")
    return inverses[0] @ transfer @ inverses[1] / np.sqrt(kinetic_scalar)


def split_carrier(operator, neutral_basis):
    """Orthogonal charged/neutral splitting, including the descent defect."""
    operator = _matrix(operator, hermitian=True)
    neutral = _matrix(neutral_basis)
    size, count = neutral.shape
    if size != operator.shape[0] or not 0 < count < size:
        raise ValueError("a proper nonzero neutral subspace is required")
    if not np.allclose(neutral.conj().T @ neutral, np.eye(count), atol=1e-13, rtol=0):
        raise ValueError("neutral basis must be orthonormal")
    charged = null_space(neutral.conj().T)
    basis = np.column_stack((charged, neutral))
    blocks = basis.conj().T @ operator @ basis
    nc = size - count
    dc = blocks[:nc, :nc]
    feedback = blocks[:nc, nc:]
    return {"charged_basis": charged, "neutral_basis": neutral, "basis": basis,
            "charged_operator": dc, "neutral_operator": blocks[nc:, nc:],
            "coupling": feedback,
            "descent_defect_norm": float(np.linalg.norm(feedback)),
            "square_defect": charged.conj().T @ operator @ operator @ charged - dc @ dc}


def source_response(operator, z, source, *, readout=None, neutral_basis,
                    kinetic=None, tolerance=1e-11, force_full=False):
    """Evaluate ell (D-z K)^(-1) j, retaining all neutral source terms.

    ``readout`` is an analytic row covector, not an implicitly conjugated
    column. Its default is j*. The Schur formula is used only when the
    eliminated block is numerically invertible and its amplification,
    cancellation, and full-equation residual pass. Otherwise the full
    matrix is solved. A singular full pencil raises rather than erasing
    its kernel with a pseudoinverse. Error estimates are floating-point
    diagnostics, not rigorous enclosures.
    """
    operator = _matrix(operator, hermitian=True)
    n = operator.shape[0]
    z = complex(z)
    if not np.isfinite(z) or not np.isfinite(tolerance) or tolerance <= 0:
        raise ValueError("finite z and positive tolerance required")
    kinetic = np.eye(n) if kinetic is None else _matrix(kinetic, hermitian=True)
    if kinetic.shape != (n, n) or np.min(np.linalg.eigvalsh(kinetic)) <= 0:
        raise ValueError("kinetic form must be positive definite on the full carrier")
    source = np.asarray(source, dtype=complex)
    readout = source.conj() if readout is None else np.asarray(readout, dtype=complex)
    if source.shape != (n,) or readout.shape != (n,) or not (
            np.all(np.isfinite(source)) and np.all(np.isfinite(readout))):
        raise ValueError("source and analytic row readout must be finite full-carrier vectors")
    split = split_carrier(operator, neutral_basis)
    basis = split["basis"]
    nc = split["charged_operator"].shape[0]
    pencil = operator - z * kinetic
    singular_values = np.linalg.svd(pencil, compute_uv=False)
    eps = np.finfo(float).eps
    if singular_values[-1] <= n * eps * singular_values[0] or singular_values[0] == 0:
        raise np.linalg.LinAlgError("the full pencil is singular at working precision")
    full_condition = float(singular_values[0] / singular_values[-1])
    local = basis.conj().T @ pencil @ basis
    j = basis.conj().T @ source
    ell = readout @ basis
    A, B = local[:nc, :nc], local[:nc, nc:]
    C, E = local[nc:, :nc], local[nc:, nc:]
    result = {"method": "full", "condition_number": full_condition,
              "schur_amplification": None, "schur_condition_number": None,
              "cancellation_factor": None, "direct_neutral_term": None}
    solution = None
    if not force_full:
        try:
            inverse_E = np.linalg.solve(E, np.eye(E.shape[0]))
            amplification = max(1.0, np.linalg.norm(B @ inverse_E), np.linalg.norm(inverse_E @ C))
            S = A - B @ inverse_E @ C
            condition = float(np.linalg.cond(S))
            result.update(schur_amplification=float(amplification), schur_condition_number=condition)
            # Scalar E may have condition number one while its inverse is
            # huge. The coupling amplification detects this near z=0.
            if eps * condition * amplification < tolerance / 32:
                jeff = j[:nc] - B @ inverse_E @ j[nc:]
                leff = ell[:nc] - ell[nc:] @ inverse_E @ C
                direct = ell[nc:] @ inverse_E @ j[nc:]
                xc = np.linalg.solve(S, jeff)
                xn = inverse_E @ (j[nc:] - C @ xc)
                candidate = basis @ np.concatenate((xc, xn))
                value = leff @ xc + direct
                scale = max(np.linalg.norm(readout) * np.linalg.norm(candidate), np.finfo(float).tiny)
                cancellation = (abs(leff @ xc) + abs(direct)) / scale
                residual = np.linalg.norm(pencil @ candidate - source)
                residual /= max(np.linalg.norm(pencil) * np.linalg.norm(candidate) + np.linalg.norm(source),
                                np.finfo(float).tiny)
                result.update(cancellation_factor=float(cancellation), direct_neutral_term=complex(direct))
                if (residual * full_condition < tolerance and eps * cancellation < tolerance / 32
                        and abs(value - readout @ candidate) < tolerance * scale):
                    solution = candidate
                    result["method"] = "schur"
                    result["schur_pairing"] = complex(value)
        except np.linalg.LinAlgError:
            pass
    if solution is None:
        solution = np.linalg.solve(pencil, source)
    residual = np.linalg.norm(pencil @ solution - source)
    residual /= max(np.linalg.norm(pencil) * np.linalg.norm(solution) + np.linalg.norm(source),
                    np.finfo(float).tiny)
    result.update(value=complex(readout @ solution), solution=solution,
                  relative_residual=float(residual),
                  residual_condition_estimate=float(residual * full_condition))
    return result


def matter_generators():
    """Actual skew-adjoint SU(3), SU(2)_W and Y matrices on the full 16.

    The right neutral line has zero charge. Right-handed colour fields
    carry the physical fundamental representation; chirality signs enter
    anomaly traces separately, not by conjugating this representation.
    """
    sigma = (np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]),
             np.diag([1, -1]))
    colour = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        real, imag = np.zeros((3, 3), complex), np.zeros((3, 3), complex)
        real[i, j] = real[j, i] = .5
        imag[i, j], imag[j, i] = -.5j, .5j
        colour.extend((real, imag))
    colour.extend((np.diag([.5, -.5, 0]), np.diag([1, 1, -2]) / np.sqrt(12)))
    answer = {}
    for index, generator in enumerate(colour):
        full_c = block_diag(generator, np.zeros((1, 1)))
        block = np.kron(full_c, np.eye(2))
        answer[f"colour_{index + 1}"] = -1j * block_diag(block, block)
    for index, generator in enumerate(sigma):
        answer[f"weak_{index + 1}"] = -1j * block_diag(np.kron(np.eye(4), generator / 2), np.zeros((8, 8)))
    hypercharge = [1 / 6] * 6 + [-.5] * 2 + [2 / 3, -1 / 3] * 3 + [0, -1]
    answer["hypercharge"] = -1j * np.diag(hypercharge)
    return answer


def evaluate_native_operations():
    """JSON-ready current finite examples for the common verification report.

    All example inputs are declared below. These are floating-point
    checks of specified operators, not new physical parameter estimates.
    The function has no file writes or parameter-store dependency.
    """
    from cg_core import modal_algebra as modes

    data = elementary_connector([.3 + .2j, .8 - .1j])
    D, N, r2 = data["operator"], data["neutral_basis"], data["amplitude_squared"]
    j = np.arange(1, 17) / 16 + 1j * np.arange(16, 0, -1) / 32
    ell = np.arange(16, 0, -1) / 20 + 1j * np.arange(1, 17) / 40
    z = .23 + .7j
    result = source_response(D, z, j, readout=ell, neutral_basis=N)
    direct = ell @ np.linalg.solve(D - z * np.eye(16), j)
    near = source_response(D, 1e-6j, j, readout=ell, neutral_basis=N)
    split = split_carrier(D, N)
    square_error = float(np.linalg.norm(D @ D - r2 * np.eye(16)))
    neutral_error = float(np.linalg.norm(split["square_defect"] - split["coupling"] @ split["coupling"].conj().T))
    eigenvalues = np.linalg.eigvalsh(D)
    heat_error = abs(float(np.sum(np.exp(-.7 * eigenvalues**2))) - 16 * np.exp(-.7 * r2))

    generators = matter_generators()
    f = {(1, 1, 1): 1., (1, -1, -1): 1.}
    A = (modes.scale(f, generators["weak_1"]), modes.scale(f, generators["weak_2"]), {})
    psi = {(1, 1, 0): np.eye(16)[0] + .2j * np.eye(16)[1],
           (0, 0, 0): np.eye(16)[6] + .3 * np.eye(16)[14]}
    L, t, s = 1.3, .11, .07
    defect = modes.joint_defect(A, psi, t, L=L)
    integral = modes.joint_defect_integral(A, psi, t, L=L)
    integral_error = max(modes.mode_norm(modes.add(a, modes.scale(b, -1)))
                         for a, b in zip(defect, integral))
    At, pt, rt = modes.joint_resolution(A, psi, ({},) * 6, t, L=L)
    sequential = modes.joint_resolution(At, pt, rt, s, L=L)[2]
    one_step = modes.joint_resolution(A, psi, ({},) * 6, s + t, L=L)[2]
    cocycle_error = max(modes.mode_norm(modes.add(a, modes.scale(b, -1)))
                        for a, b in zip(sequential, one_step))
    inputs, outputs = modes.spinor_basis(0), modes.spinor_basis(1)
    multiplication = modes.spinor_multiplication({(1, 1, 0): 1.}, inputs, outputs)
    negative = modes.signed_cross_blocks(multiplication, inputs, outputs)[("-", "+")]
    gram = negative.conj().T @ negative
    spinor_error = float(np.linalg.norm(gram - np.eye(2) / 3))
    killing = modes.killing_two_body()
    casimir_values = np.linalg.eigvalsh(killing["casimir"])
    killing_error = float(np.max(np.abs(casimir_values - np.array([0] * 2 + [8] * 9 + [12] * 10))))
    checks = {"elementary_square": square_error < 1e-12,
              "neutral_rank_one_feedback": neutral_error < 1e-12,
              "complete_source_response": abs(result["value"] - direct) < 1e-11,
              "near_zero_full_solve": near["method"] == "full" and near["relative_residual"] < 1e-12,
              "complete_heat_trace": heat_error < 1e-12,
              "joint_duhamel": integral_error < 1e-11,
              "joint_cocycle": cocycle_error < 1e-11,
              "actual_spinor_cross_block": spinor_error < 1e-12,
              "killing_symmetric_square": killing_error < 1e-11}
    checks = {name: bool(value) for name, value in checks.items()}
    return {"scope": "declared finite operators and fixed-frame resolution examples",
            "inputs": {"H_real_imag": [[.3, .2], [.8, -.1]], "z_real_imag": [.23, .7],
                       "source": "j_i=(i+1)/16+i_unit*(16-i)/32, i=0..15",
                       "readout": "ell_i=(16-i)/20+i_unit*(i+1)/40, i=0..15",
                       "L": L, "t": t, "s": s, "Duhamel_order": 24,
                       "connection": "A1=f Tweak1, A2=f Tweak2, A3=0; f=e111+e1,-1,-1",
                       "matter": "e110*(basis0+0.2i*basis1)+e000*(basis6+0.3*basis14)",
                       "spinor_multiplier": "e1,1,0 on the lowest positive doublet"},
            "elementary": {"square_residual": square_error, "neutral_feedback_residual": neutral_error,
                           "response_method": result["method"], "source_pairing_error": float(abs(result["value"] - direct)),
                           "near_zero_method": near["method"], "near_zero_residual": near["relative_residual"],
                           "heat_trace_error": float(heat_error)},
            "joint_resolution": {"Duhamel_error": integral_error, "cocycle_error": cocycle_error,
                                 "defect_norm": sum(modes.mode_norm(x) for x in defect)},
            "spinor": {"negative_block_norm_squared_per_input": [float(x) for x in np.diag(gram).real],
                       "I2_over_3_residual": spinor_error},
            "killing": {"carrier_dimension": 6, "symmetric_dimension": 21,
                        "casimir_levels": [0, 8, 12], "multiplicities": [2, 9, 10],
                        "spectral_residual": killing_error},
            "checks": checks, "all_checks_passed": all(checks.values())}
