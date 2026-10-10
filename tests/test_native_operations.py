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

"""Independent finite-operator and mode identities, including failed descents."""
import math

import numpy as np
import pytest
from scipy.linalg import expm

from cg_core.finite_connector import (elementary_connector, chiral_operator,
                                      canonical_transfer, source_response,
                                      split_carrier, matter_generators)
from cg_core import modal_algebra as modes


def _random(shape, rng):
    return rng.normal(size=shape) + 1j * rng.normal(size=shape)


def test_elementary_square_feedback_heat_trace_and_full_neutral_charges():
    data = elementary_connector([.3 + .2j, .8 - .1j])
    D, N, r2 = data["operator"], data["neutral_basis"], data["amplitude_squared"]
    split = split_carrier(D, N)
    assert np.allclose(D @ D, r2 * np.eye(16))
    assert np.allclose(split["square_defect"], split["coupling"] @ split["coupling"].conj().T)
    assert np.linalg.matrix_rank(split["square_defect"], tol=1e-12) == 1
    ev = np.linalg.eigvalsh(split["charged_operator"])
    assert np.allclose(ev, [-math.sqrt(r2)] * 7 + [0] + [math.sqrt(r2)] * 7)
    t = .7
    full_trace = np.trace(expm(-t * D @ D)).real
    Dc = split["charged_operator"]
    compressed_trace = np.trace(expm(-t * Dc @ Dc)).real
    assert full_trace == pytest.approx(16 * math.exp(-t * r2))
    assert compressed_trace == pytest.approx(14 * math.exp(-t * r2) + 1)
    for generator in matter_generators().values():
        assert np.allclose(generator + generator.conj().T, 0)
        assert np.linalg.norm(generator @ N) == 0
    weak = [matter_generators()[f"weak_{i}"] for i in (1, 2, 3)]
    assert np.allclose(weak[0] @ weak[1] - weak[1] @ weak[0], weak[2])


@pytest.mark.parametrize("z", [.23 + .7j, .1 + .3j, 1e-6j, 0])
def test_arbitrary_complex_source_readout_and_stable_near_zero(z):
    rng = np.random.default_rng(513)
    data = elementary_connector([.3 + .2j, .8 - .1j])
    D, N = data["operator"], data["neutral_basis"]
    source, readout = _random((16,), rng), _random((16,), rng)
    result = source_response(D, z, source, readout=readout, neutral_basis=N)
    exact = readout @ np.linalg.solve(D - z * np.eye(16), source)
    assert result["value"] == pytest.approx(exact, rel=2e-12, abs=2e-12)
    assert result["relative_residual"] < 1e-14
    if abs(z) < 1e-5:
        assert result["method"] == "full"
    else:
        assert result["method"] == "schur"
        assert abs(result["direct_neutral_term"]) > .1
    U, _ = np.linalg.qr(_random((16, 16), rng))
    transformed = source_response(U.conj().T @ D @ U, z, U.conj().T @ source,
                                  readout=readout @ U, neutral_basis=U.conj().T @ N)
    assert transformed["value"] == pytest.approx(exact, rel=3e-12, abs=3e-12)


def test_general_weighted_kinetic_multigeneration_and_singular_case():
    rng = np.random.default_rng(1616)
    data = elementary_connector([0, 1], generations=3)
    assert data["operator"].shape == (48, 48)
    assert split_carrier(data["operator"], data["neutral_basis"])["charged_operator"].shape == (45, 45)
    T = _random((8, 8), rng)
    D = chiral_operator(T, right_block=np.diag(np.arange(8) / 10))
    N = elementary_connector([0, 1])["neutral_basis"]
    K0 = _random((16, 16), rng)
    K = np.eye(16) + K0.conj().T @ K0
    j, ell = _random((16,), rng), _random((16,), rng)
    z = .6 + .8j
    result = source_response(D, z, j, readout=ell, neutral_basis=N, kinetic=K)
    assert result["value"] == pytest.approx(ell @ np.linalg.solve(D - z * K, j), rel=1e-11)
    assert not np.allclose(D @ D, np.eye(16) * np.trace(D @ D) / 16)
    transfer = canonical_transfer(T, 4 * np.eye(8), 9 * np.eye(8), kinetic_scalar=25)
    assert np.allclose(transfer, T / 30)
    with pytest.raises(np.linalg.LinAlgError):
        source_response(np.zeros((16, 16)), 0, j, neutral_basis=N)
    with pytest.raises(ValueError):
        canonical_transfer(T, np.zeros((8, 8)), np.eye(8))


def test_clebsch_unitarity_and_matrix_product_at_an_independent_group_element():
    # Spin-one tensor product -> dimensions 1+3+5; actual unitary change of basis.
    product_labels = [(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)]
    coupled_labels = [(J, M) for J in (0, 1, 2) for M in range(-J, J + 1)]
    C = np.array([[modes.clebsch_gordan(1, a, 1, b, J, M)
                   for J, M in coupled_labels] for a, b in product_labels])
    assert np.allclose(C.T @ C, np.eye(9), atol=1e-14)
    theta = np.array([.37, -.22, .41])
    D = {j: expm(-1j * sum(t * J for t, J in zip(theta, modes.spin_matrices(j))))
         for j in (0, 1, 2)}
    def evaluate(mode):
        j, m, n = mode
        return math.sqrt(2 * j + 1) * D[j][m + j, n + j]
    for a in ((1, -1, 0), (1, 1, 1), (1, 0, -1)):
        for b in ((1, 0, 1), (1, -1, -1)):
            assert sum(c * evaluate(x) for x, c in modes.mode_product(a, b)) == pytest.approx(
                evaluate(a) * evaluate(b), abs=1e-14)
    highest = dict(modes.mode_product((1, 1, 1), (1, 1, 1)))
    assert highest == {(2, 2, 2): pytest.approx(3 / math.sqrt(5))}


def test_frame_derivatives_product_rule_commutator_and_heat_identity():
    f = {(1, 1, 0): .3 + .2j, (0, 0, 0): -.2}
    g = {(1, -1, 1): .7, (1, 0, 0): .2j}
    L = 1.7
    for a in range(3):
        lhs = modes.derivative(modes.multiply(f, g), a, L=L)
        rhs = modes.add(modes.multiply(modes.derivative(f, a, L=L), g),
                        modes.multiply(f, modes.derivative(g, a, L=L)))
        assert modes.mode_norm(modes.add(lhs, modes.scale(rhs, -1))) < 1e-14
    bracket = modes.add(modes.derivative(modes.derivative(f, 1, L=L), 0, L=L),
                        modes.scale(modes.derivative(modes.derivative(f, 0, L=L), 1, L=L), -1))
    assert modes.mode_norm(modes.add(bracket, modes.scale(modes.derivative(f, 2, L=L), -2 / L))) < 1e-14


def test_actual_nonlinear_joint_residual_cocycle_and_duhamel():
    # Real spatial function and noncommuting, skew-adjoint matrices.
    f = {(1, 1, 1): 1., (1, -1, -1): 1.}
    T = [-1j * j for j in modes.spin_matrices(.5)]
    A = (modes.scale(f, T[0]), modes.scale(f, T[1]), {})
    psi = {(1, 1, 0): np.array([.2j, .4]), (0, 0, 0): np.array([1., -.3j])}
    t, s, L = .11, .07, 1.3
    F = modes.curvature(A, L=L)
    assert any(label[0] == 2 and np.linalg.norm(value) > .1 for label, value in F[0].items())
    direct = modes.joint_defect(A, psi, t, L=L)
    integral = modes.joint_defect_integral(A, psi, t, L=L)
    assert sum(modes.mode_norm(x) for x in direct) > .1
    for x, y in zip(direct, integral):
        assert modes.mode_norm(modes.add(x, modes.scale(y, -1))) < 2e-13
    once = modes.joint_resolution(A, psi, ({},) * 6, s + t, L=L)
    At, pt, rt = modes.joint_resolution(A, psi, ({},) * 6, t, L=L)
    twice = modes.joint_resolution(At, pt, rt, s, L=L)
    for x, y in zip(once[2], twice[2]):
        assert modes.mode_norm(modes.add(x, modes.scale(y, -1))) < 2e-13
    reconstructed = tuple(modes.add(b, r) for b, r in zip(modes.joint_response(At, pt, L=L), rt))
    original = modes.joint_response(A, psi, L=L)
    for actual, value in zip(reconstructed, original):
        assert modes.mode_norm(modes.add(actual, modes.scale(modes.heat(value, t, L=L), -1))) < 2e-13
    generators = list(matter_generators().values())
    coords = ({(1, 1, 1): np.arange(12) / 100}, {}, {})
    represented = modes.represent_connection(coords, generators)
    assert represented[0][(1, 1, 1)].shape == (16, 16)


def test_actual_spinor_cross_block_and_complete_signed_degeneracies():
    incoming, outgoing = modes.spinor_basis(0), modes.spinor_basis(1)
    matrix = modes.spinor_multiplication({(1, 1, 0): 1.}, incoming, outgoing)
    assert np.allclose(matrix.conj().T @ matrix, np.eye(2))
    blocks = modes.signed_cross_blocks(matrix, incoming, outgoing)
    # Actual coupled mode sum gives 1/3 negative-sign norm per lowest spinor.
    assert np.allclose(blocks[("-", "+")].conj().T @ blocks[("-", "+")], np.eye(2) / 3)
    assert len([x for x in outgoing if modes.spinor_dirac_value(x) == -2.5]) == 6
    assert len([x for x in outgoing if modes.spinor_dirac_value(x) == 3.5]) == 12
    identity = modes.spinor_multiplication({(0, 0, 0): 1.}, outgoing, outgoing)
    assert np.allclose(identity, np.eye(len(outgoing)))


def test_true_killing_symmetric_square_colour_projection_and_source_visibility():
    data = modes.killing_two_body()
    assert data["basis"].shape == (36, 21)
    assert np.allclose(data["basis"].conj().T @ data["basis"], np.eye(21))
    assert np.allclose(np.linalg.eigvalsh(data["casimir"]), [0] * 2 + [8] * 9 + [12] * 10, atol=2e-13)
    assert np.allclose(sum(data["projectors"].values()), np.eye(21), atol=3e-14)
    for label, dimension in (((0, 0), 2), ((1, 1), 9), ((2, 0), 5), ((0, 2), 5)):
        P = data["projectors"][label]
        assert np.trace(P).real == pytest.approx(dimension)
        assert np.allclose(P @ P, P, atol=3e-14)
    parity = data["parity"]
    assert np.allclose(parity @ parity, np.eye(21))
    assert np.allclose(parity @ data["projectors"][(2, 0)] @ parity, data["projectors"][(0, 2)])
    rng = np.random.default_rng(21)
    source = _random((21,), rng)
    lift = modes.colour_singlet_lift(source)
    assert np.linalg.norm(lift) == pytest.approx(np.linalg.norm(source))
    assert np.allclose(lift, lift.transpose(2, 3, 0, 1))
    projection = modes.colour_singlet_projection(lift)
    assert np.allclose(projection["coefficients"], source)
    assert projection["antisymmetric_norm"] < 1e-14
    weights = modes.killing_source_weights(source)
    assert sum(weights.values()) == pytest.approx(np.vdot(source, source).real)
    singlet = data["projectors"][(0, 0)] @ source
    assert modes.killing_source_weights(singlet)[(1, 1)] < 1e-25


def test_finite_seed_is_an_actual_pairing_not_a_spatial_vertex():
    from cg_frg.fermion.mass_operator_overlap import (
        Y_0, finite_connector_pairing, mass_operator_matrix_element)
    left, right = np.eye(16)[0], np.eye(16)[8]
    assert Y_0 == 1.0
    assert mass_operator_matrix_element(.5, 0) == 1.0
    assert finite_connector_pairing([0, 2], left, right) == 2.0
    assert finite_connector_pairing([0, 1], left, 3j * right) == 3j
    with pytest.raises(ValueError):
        mass_operator_matrix_element(.2, 0)


def test_qcd_candidate_carrier_and_prescribed_catalogue_are_separate(monkeypatch):
    from cg_frg.qcd import qcd_sector as qcd
    candidates = qcd.glueball_two_gluon_spectrum()
    assert candidates == {"(0,0)": 8., "(1,1)": 16., "(2,0)": 20., "(0,2)": 20.}
    inputs = {"tau": .02, "kL": 2.4935343325226915, "mass_gap_dE": 2e17,
              "mass_gap_m_gen": 2e16, "m_glueball": 1.664, "qcd_Lambda_QCD": .208}
    published = {}
    monkeypatch.setattr(qcd, "get", inputs.__getitem__)
    monkeypatch.setattr(qcd, "pset", lambda key, value, **kw: published.update({key: value}))
    result = qcd.compute()
    assert result["tower"]["0++"]["mass_GeV"] == 1.664
    for label, coefficient in (("2++", 16), ("0++*", 18), ("0-+", 17)):
        assert result["tower"][label]["ratio"] == math.sqrt(coefficient / 8)
    assert published["qcd_killing_candidates"]["symmetric_dimension"] == 21
    assert published["qcd_sector_status"]["candidate_carrier_verified"]
    assert not published["qcd_sector_status"]["two_body_kernel_solved"]


def test_current_finite_examples_are_finite_json_with_actual_checks():
    import json
    from cg_core.finite_connector import evaluate_native_operations
    result = evaluate_native_operations()
    assert result["all_checks_passed"]
    assert result["joint_resolution"]["defect_norm"] > .1
    assert len(result["checks"]) == 9
    assert json.loads(json.dumps(result, allow_nan=False))["all_checks_passed"]
