"""Covariant compression checked on the actual Haar and matter carriers.

Field amplitudes and complex probe energies below are finite test
configurations. No comparison mass, production parameter or source
covariance is used to construct the operators.
"""
import numpy as np
import pytest
from scipy.linalg import expm, null_space

from cg_core import modal_algebra as modes
from cg_core.finite_connector import matter_generators, source_response
from cg_core.matter_compression import (
    covariant_matter_pullback, compressed_matter_response, compressed_matter_poles,
    joint_matter_response,
    precise_matter_response,
)
from cg_core.native_matter_matching import (
    covariant_spinor_matrix, radial_spinor_family, spinor_vertex,
)


@pytest.fixture(scope="module")
def radial():
    return radial_spinor_family()


def translation_generator(labels):
    """Derivative of the original source's left magnetic translation."""
    result = np.zeros((len(labels), len(labels)), complex)
    for i, (j, m, J, M) in enumerate(labels):
        for k, (ell, n, K, N) in enumerate(labels):
            if (j, J, M) == (ell, K, N):
                result[i, k] = 1j*modes.spin_matrices(j)[0].conj()[m+j, n+j]
    return result


def test_full_connection_cancels_a_pure_moving_frame(radial):
    R = radial["embedding"]
    K = translation_generator(radial["labels"])
    result = covariant_matter_pullback(R, -K @ R, K)
    assert np.linalg.norm(result["moving_gram"]) > 1
    assert np.linalg.norm(result["original_gram"]) > 1
    np.testing.assert_allclose(result["cross_gram"], -2*result["moving_gram"], atol=5e-15)
    np.testing.assert_allclose(result["full_gram"], 0, atol=1e-28)
    assert max(result["residuals"].values()) < 2e-14


def test_complete_pullback_is_covariant_with_the_inhomogeneous_term(radial):
    R = radial["embedding"]
    K = translation_generator(radial["labels"])
    A = 2*K
    dR = -K @ R
    initial = covariant_matter_pullback(R, dR, A)
    U = expm(.37*K)
    dU = U @ K
    transformed_R = U.conj().T @ R
    transformed_dR = U.conj().T @ dR-U.conj().T @ dU @ transformed_R
    transformed_A = U.conj().T @ A @ U+U.conj().T @ dU
    result = covariant_matter_pullback(transformed_R, transformed_dR, transformed_A)
    np.testing.assert_allclose(result["retained_connection"], initial["retained_connection"], atol=2e-14)
    np.testing.assert_allclose(result["complement_connection"][0],
                               U.conj().T @ initial["complement_connection"][0], atol=2e-14)
    np.testing.assert_allclose(result["full_gram"], initial["full_gram"], atol=3e-14)
    assert np.linalg.norm(initial["complement_gram"]) > 1
    assert max(result["residuals"].values()) < 4e-14


def test_connection_requires_the_same_orthonormal_readout_derivative():
    R = np.eye(4, 2, dtype=complex)
    with pytest.raises(ValueError, match="orthonormal"):
        covariant_matter_pullback(2*R, np.zeros_like(R), np.zeros((4, 4)))
    with pytest.raises(ValueError, match="tangent"):
        covariant_matter_pullback(R, R, np.zeros((4, 4)))
    with pytest.raises(ValueError, match="skew"):
        covariant_matter_pullback(R, np.zeros_like(R), np.eye(4))
    with pytest.raises(ValueError, match="matching"):
        covariant_matter_pullback(R, np.zeros((2, 4, 2)), np.zeros((3, 4, 4)))


def test_actual_source_complement_and_ordinary_force_give_the_same_return(radial):
    labels, R = radial["labels"], radial["embedding"]
    multiplier = spinor_vertex({(1, 0, 0): 1.}, labels, labels)
    H = np.diag([modes.spinor_dirac_value(label) for label in labels])+.23*multiplier
    z = 1.4+.7j
    result = compressed_matter_response(H, R, z)
    assert result["complement_dimension"] == 38
    assert np.linalg.norm(result["complement_coupling"]) > .1
    assert np.linalg.norm(result["self_energy"]) > .001
    assert max(result["residuals"].values()) < 8e-14
    # Independent existing full-pencil solver uses (H-z), the opposite sign.
    complement = null_space(R.conj().T)
    for i, j in ((0, 0), (0, 2), (2, 4)):
        old = source_response(H, z, R[:, j], readout=R[:, i].conj(), neutral_basis=complement)
        assert old["value"] == pytest.approx(-result["response"][i, j], abs=3e-14)
    step = 2e-5
    positive = compressed_matter_response(H, R, z+step)
    negative = compressed_matter_response(H, R, z-step)
    np.testing.assert_allclose((positive["response"]-negative["response"])/(2*step),
                               result["response_derivative"], rtol=3e-9, atol=3e-10)
    np.testing.assert_allclose((positive["self_energy"]-negative["self_energy"])/(2*step),
                               result["self_energy_derivative"], rtol=3e-9, atol=3e-11)


def test_response_preserves_ambient_and_retained_unitary_coordinates(radial):
    R, labels = radial["embedding"], radial["labels"]
    H = np.diag([modes.spinor_dirac_value(label) for label in labels])
    H = H+.31*spinor_vertex({(1, 0, 0): 1.}, labels, labels)
    U = expm(.29*translation_generator(labels))
    V = expm(.21j*np.diag(np.arange(6)))
    initial = compressed_matter_response(H, R, 2+.6j)
    result = compressed_matter_response(U.conj().T @ H @ U, U.conj().T @ R @ V, 2+.6j)
    for key in ("response", "self_energy", "response_derivative", "self_energy_derivative",
                "ordinary_force_response", "force_moment_0", "force_moment_1"):
        np.testing.assert_allclose(result[key], V.conj().T @ initial[key] @ V, atol=2e-13)


def test_full_readout_has_zero_complement_return():
    H = np.array([[1, .2j], [-.2j, 3.]])
    result = compressed_matter_response(H, np.eye(2), .2+.7j)
    assert result["complement_dimension"] == 0
    np.testing.assert_array_equal(result["self_energy"], np.zeros((2, 2)))
    assert max(result["residuals"].values()) < 3e-15
    with pytest.raises(ValueError, match="positive imaginary"):
        compressed_matter_response(H, np.eye(2), 1.)
    with pytest.raises(ValueError, match="Hermitian"):
        compressed_matter_response(H+np.eye(2)*1j, np.eye(2), 1+.4j)


def test_original_dirac_free_part_and_complete_nonconstant_support():
    labels = modes.spinor_basis(0)
    free = covariant_spinor_matrix(({}, {}, {}), labels, L=1.7)
    np.testing.assert_allclose(free["matrix"], np.eye(32)*1.5/1.7, atol=2e-15)
    generator = matter_generators()["weak_1"]
    connection = ({(1, 0, 0): .27*generator}, {}, {})
    full = covariant_spinor_matrix(connection, labels)
    retained = covariant_spinor_matrix(connection, labels, labels)
    assert full["product_support_complete"]
    assert not retained["product_support_complete"]
    negative = [i for i, label in enumerate(full["output_labels"])
                if modes.spinor_dirac_value(label) < 0]
    negative_rows = [16*i+a for i in negative for a in range(16)]
    assert np.linalg.norm(full["connection_matrix"][negative_rows]) > .01
    np.testing.assert_allclose(full["matrix"].conj().T @ full["matrix"],
        retained["matrix"].conj().T @ retained["matrix"]+retained["omitted_gram"], atol=2e-15)
    assert np.linalg.norm(retained["omitted_gram"]) > .01


def test_original_dirac_connection_on_all_sixteen_matter_coordinates():
    labels = modes.spinor_basis(1)
    generators = matter_generators()
    connection = ({(0, 0, 0): .23*generators["weak_1"]},
                  {(1, 0, 0): .17*generators["hypercharge"]}, {})
    result = covariant_spinor_matrix(connection, labels, labels)
    H = result["matrix"]
    np.testing.assert_allclose(H, H.conj().T, atol=2e-15)
    # Compare a constant connection independently in the lowest spin frame.
    lowest = modes.spinor_basis(0)
    constant = covariant_spinor_matrix((connection[0], {}, {}), lowest)
    sigma = 2*modes.spin_matrices(.5)[0]
    expected = 1.5*np.eye(32)+1j*np.kron(sigma, .23*generators["weak_1"])
    np.testing.assert_allclose(constant["matrix"], expected, atol=2e-15)
    g = expm(.39*generators["weak_2"])
    changed = tuple({label: g.conj().T @ a @ g for label, a in component.items()}
                    for component in connection)
    changed_H = covariant_spinor_matrix(changed, labels, labels)["matrix"]
    full_g = np.kron(np.eye(len(labels)), g)
    np.testing.assert_allclose(changed_H, full_g.conj().T @ H @ full_g, atol=3e-15)


def test_direct_colour_annihilates_the_complete_lepton_source():
    labels = modes.spinor_basis(0)
    generators = matter_generators()
    casimir = -sum(a @ a for name, a in generators.items() if name.startswith("colour_"))
    eigenvalues, basis = np.linalg.eigh(casimir)
    leptons = np.kron(np.eye(2), basis[:, np.abs(eigenvalues) < 1e-12])
    full = covariant_spinor_matrix(({(1, 0, 0): generators["colour_1"]}, {}, {}), labels)
    np.testing.assert_allclose(full["connection_matrix"] @ leptons, 0, atol=1e-15)
    weak = covariant_spinor_matrix(({(0, 0, 0): generators["weak_1"]}, {}, {}), labels)
    assert np.linalg.norm(weak["connection_matrix"] @ leptons) > .1


def test_covariant_dirac_operator_feeds_the_same_complete_matter_response():
    labels = modes.spinor_basis(1)
    generators = matter_generators()
    connection = ({(1, 0, 0): .19*generators["weak_1"]}, {}, {})
    H = covariant_spinor_matrix(connection, labels, labels)["matrix"]
    casimir = -sum(a @ a for name, a in generators.items() if name.startswith("colour_"))
    values, vectors = np.linalg.eigh(casimir)
    leptons = vectors[:, np.abs(values) < 1e-12]
    lowest = modes.spinor_basis(0)
    R = np.zeros((16*len(labels), len(lowest)*leptons.shape[1]), complex)
    for j, label in enumerate(lowest):
        i = labels.index(label)
        R[16*i:16*(i+1), 4*j:4*(j+1)] = leptons
    z = 1.2+.8j
    result = compressed_matter_response(H, R, z)
    assert result["retained_dimension"] == 8
    assert np.linalg.norm(result["self_energy"]) > .001
    assert max(result["residuals"].values()) < 8e-14
    # An independent spectral sum checks the resolvent and its derivative
    # on the same operator, without a separate complement propagation law.
    energies, states = np.linalg.eigh(H)
    amplitudes = states.conj().T @ R
    spectral = amplitudes.conj().T @ (amplitudes/(z-energies[:, None]))
    derivative = -amplitudes.conj().T @ (amplitudes/(z-energies[:, None])**2)
    np.testing.assert_allclose(spectral, result["response"], atol=4e-14)
    np.testing.assert_allclose(derivative, result["response_derivative"], atol=4e-14)
    np.testing.assert_allclose(amplitudes.conj().T @ amplitudes, np.eye(8), atol=4e-14)


def test_original_connection_rejects_inconsistent_matrix_and_adjoint_conventions():
    labels = modes.spinor_basis(0)
    with pytest.raises(ValueError, match="sixteen"):
        covariant_spinor_matrix(({(0, 0, 0): np.eye(3)}, {}, {}), labels)
    with pytest.raises(ValueError, match="skew-adjoint"):
        covariant_spinor_matrix(({(0, 0, 0): np.eye(16)}, {}, {}), labels)
    with pytest.raises(ValueError, match="radius"):
        covariant_spinor_matrix(({}, {}, {}), labels, L=0.)


def test_same_operator_fixes_poles_and_kinetic_residues():
    # Three different tree energies couple to the same two complementary
    # states. All shifts, mixing and normalization follow from this H.
    A = np.diag([.4, 1.3, 2.7])
    C = np.array([[4.1, .2j], [-.2j, 5.4]])
    B = np.array([[.12, .08j, .25], [.04j, .17, -.11j]])
    H = np.block([[A, B.conj().T], [B, C]])
    R = np.eye(5, dtype=complex)[:, :3]
    result = compressed_matter_poles(H, R)
    assert max(result["residuals"].values()) < 4e-15
    assert len(result["pole_diagnostics"]) == 5
    for diagnostic in result["pole_diagnostics"]:
        assert diagnostic["schur_available"]
        assert max(diagnostic["residuals"].values()) < 2e-12
        metric = diagnostic["inverse_response_derivative"]
        assert np.min(np.linalg.eigvalsh(metric)) >= 1-2e-14
        assert diagnostic["normalized_slope"] >= 1-2e-14
    E = result["energy_eigenvalues"]
    shifts = E[:3]/np.diag(A)
    assert np.ptp(shifts) > 1e-3
    z = 1.4+.6j
    amplitudes = result["readout_amplitudes"]
    spectral = (amplitudes/(z-E)) @ amplitudes.conj().T
    direct = compressed_matter_response(H, R, z)
    np.testing.assert_allclose(spectral, direct["response"], atol=2e-15)


def test_degenerate_and_dark_poles_preserve_the_complete_spectral_response():
    H = np.diag([1., 1., 3., 4.]).astype(complex)
    R = np.eye(4, dtype=complex)[:, :2]
    result = compressed_matter_poles(H, R)
    block = result["pole_blocks"][0]
    assert block["multiplicity"] == 2
    assert block["unresolved_cluster"]
    np.testing.assert_allclose(block["residue"], np.eye(2), atol=1e-15)
    assert not any(b["visible"] for b in result["pole_blocks"][1:])
    # A readout may share an eigenvalue with its complement. The full
    # response is regular to calculate even where Schur elimination fails.
    overlap = compressed_matter_poles(H, np.eye(4, dtype=complex)[:, :1])
    assert any(not d["schur_available"] for d in overlap["pole_diagnostics"])
    assert max(overlap["residuals"].values()) == 0
    full = compressed_matter_poles(H, np.eye(4))
    assert full["complement_eigenvalues"].size == 0
    assert all(d["schur_available"] for d in full["pole_diagnostics"])


def test_pole_cluster_keeps_close_distinct_energies_and_unitary_covariance():
    H = np.diag([1., 1.+2e-6, 1.+4e-6, 3.]).astype(complex)
    R = np.eye(4, dtype=complex)[:, :3]
    result = compressed_matter_poles(H, R, resolution=1e-6)
    assert result["pole_blocks"][0]["multiplicity"] == 2
    assert result["pole_blocks"][1]["multiplicity"] == 1
    assert np.ptp(result["pole_blocks"][0]["energy_eigenvalues"]) > 0
    K = np.array([[0, .2, 0, .3j], [-.2, 0, .1j, 0],
                  [0, .1j, 0, .4], [.3j, 0, -.4, 0]], complex)
    U = expm(K)
    transformed = compressed_matter_poles(U @ H @ U.conj().T, U @ R, resolution=1e-6)
    np.testing.assert_allclose(transformed["energy_eigenvalues"], result["energy_eigenvalues"], atol=2e-15)
    for before, after in zip(result["pole_blocks"], transformed["pole_blocks"]):
        np.testing.assert_allclose(before["residue"], after["residue"], atol=1e-8)
    # Within a nearly degenerate cluster, only its full projector is stable.
    assert max(transformed["residuals"].values()) < 3e-15


def test_poles_reject_invalid_resolution_and_nonhermitian_operator():
    R = np.eye(2, dtype=complex)[:, :1]
    for resolution in (0, -1, float("nan")):
        with pytest.raises(ValueError, match="resolution"):
            compressed_matter_poles(np.eye(2), R, resolution=resolution)
    with pytest.raises(ValueError, match="Hermitian"):
        compressed_matter_poles([[1, 1], [0, 2]], R)


def car_annihilators(count):
    result = []
    for mode in range(count):
        c = np.zeros((2**count, 2**count), complex)
        for occupation in range(2**count):
            if occupation & (1 << mode):
                sign = (-1)**(occupation & ((1 << mode)-1)).bit_count()
                c[occupation ^ (1 << mode), occupation] = sign
        result.append(c)
    return result


def test_joint_response_preserves_correlated_occupations_and_both_addition_energies():
    c1, c2 = car_annihilators(2)
    n1, n2 = c1.conj().T @ c1, c2.conj().T @ c2
    H = .7*n1+1.8*n2+.4*n1 @ n2
    # A correlated stationary state, with no factorization assumption.
    rho = np.diag([.31, .17, .13, .39])
    z = .9+.35j
    result = joint_matter_response(H, rho, [c1, c2], z)
    occupation2, occupation1 = np.trace(rho @ n2), np.trace(rho @ n1)
    expected = np.diag([(1-occupation2)/(z-.7)+occupation2/(z-1.1),
                        (1-occupation1)/(z-1.8)+occupation1/(z-2.2)])
    derivative = -np.diag([(1-occupation2)/(z-.7)**2+occupation2/(z-1.1)**2,
                           (1-occupation1)/(z-1.8)**2+occupation1/(z-2.2)**2])
    np.testing.assert_allclose(result["response"], expected, atol=2e-15)
    np.testing.assert_allclose(result["response_derivative"], derivative, atol=5e-15)
    assert max(result["residuals"].values()) < 5e-15
    assert np.linalg.norm(result["self_energy"]) > .03


def test_joint_source_matter_state_and_common_force_response():
    c1, c2 = car_annihilators(2)
    n1, n2 = c1.conj().T @ c1, c2.conj().T @ c2
    sx = np.array([[0, 1], [1, 0]], complex)
    sz = np.diag([1., -1.])
    H = np.kron(.9*sz, np.eye(4))+np.kron(np.eye(2), .6*n1+1.7*n2)
    H += np.kron(.23*sx, n1-.4*n2)
    values, states = np.linalg.eigh(H)
    probabilities = np.exp(-.7*(values-values.min()))
    rho = (states*(probabilities/probabilities.sum())) @ states.conj().T
    operators = [np.kron(np.eye(2), c) for c in (c1, c2)]
    z = .8+.4j
    result = joint_matter_response(H, rho, operators, z)
    assert max(result["residuals"].values()) < 8e-15
    # Independent Lehmann sum: here the actual stationary state happens
    # to be a spectral function of H, so no degenerate coherence is lost.
    amplitudes = [states.conj().T @ c @ states for c in operators]
    expected = np.zeros((2, 2), complex)
    probabilities /= probabilities.sum()
    for a in range(8):
        for b in range(8):
            v = np.array([c[a, b] for c in amplitudes])
            expected += ((probabilities[a]+probabilities[b])/(z-(values[b]-values[a]))
                         * np.outer(v, v.conj()))
    np.testing.assert_allclose(result["response"], expected, atol=3e-15)
    # The exact transition representation enters the existing complement
    # engine unchanged, including source/matter correlations.
    compressed = compressed_matter_response(
        np.diag(result["transition_energies"]), result["transition_embedding"], z)
    np.testing.assert_allclose(compressed["response"], result["response"], atol=3e-15)
    np.testing.assert_allclose(compressed["self_energy"], result["self_energy"], atol=3e-14)


def test_joint_response_keeps_stationary_degenerate_coherence():
    c1, c2 = car_annihilators(2)
    H = c1.conj().T @ c1+c2.conj().T @ c2
    rho = np.diag([.2, .3, .3, .2]).astype(complex)
    rho[1, 2] = .08j
    rho[2, 1] = -.08j
    z = 1.2+.3j
    result = joint_matter_response(H, rho, [c1, c2], z)
    np.testing.assert_allclose(result["response"], np.eye(2)/(z-1), atol=3e-15)
    assert max(result["residuals"].values()) < 5e-15
    # Simultaneous Hilbert-space transport preserves the full answer.
    K = np.array([[0, .2, 0, .3j], [-.2, 0, .1j, 0],
                  [0, .1j, 0, .4], [.3j, 0, -.4, 0]], complex)
    U = expm(K)
    transformed = joint_matter_response(U @ H @ U.conj().T, U @ rho @ U.conj().T,
                                      [U @ c @ U.conj().T for c in (c1, c2)], z)
    np.testing.assert_allclose(transformed["response"], result["response"], atol=1e-14)


def test_joint_response_rejects_invalid_joint_state_and_car():
    c = car_annihilators(1)[0]
    H, rho = np.diag([0., 1.]), np.eye(2)/2
    with pytest.raises(ValueError, match="CAR"):
        joint_matter_response(H, rho, [2*c], 1j)
    with pytest.raises(ValueError, match="stationary"):
        joint_matter_response(H, [[.5, .2], [.2, .5]], [c], 1j)
    with pytest.raises(ValueError, match="positive"):
        joint_matter_response(H, np.diag([-1., 2.]), [c], 1j)


def test_arbitrary_precision_response_retains_finite_return_and_same_derivative():
    import mpmath

    ctx = mpmath.mp.clone()
    ctx.dps = 110
    H = [["1", "0.1"], ["0.1", "2"]]
    result = precise_matter_response(H, [["1"], ["0"]], ("1.3", "0.7"))
    value = lambda name: ctx.mpc(*result[name][0][0])
    z = ctx.mpc("1.3", "0.7")
    sigma = ctx.mpf("0.01")/(z-2)
    dsigma = -ctx.mpf("0.01")/(z-2)**2
    G = 1/(z-1-sigma)
    assert abs(value("response")-G) < ctx.mpf("1e-79")
    assert abs(value("response_derivative")+G**2*(1-dsigma)) < ctx.mpf("1e-79")
    assert abs(value("self_energy")-sigma) < ctx.mpf("1e-80")
    assert abs(value("self_energy_derivative")-dsigma) < ctx.mpf("1e-80")
    assert max(ctx.mpf(v) for v in result["arithmetic_refinement_changes"].values()) < ctx.mpf("1e-98")
    assert result["working_precisions"] == [100, 120]
    assert not result["interval_certificate"]
    # Actual nonunit readout Gram is kept, rather than rounded to identity.
    scaled = precise_matter_response(H, [["2"], ["0"]], ("1.3", "0.7"))
    assert abs(ctx.mpc(*scaled["response"][0][0])-4*G) < ctx.mpf("1e-78")
    assert abs(ctx.mpc(*scaled["self_energy"][0][0])-sigma/4) < ctx.mpf("1e-80")


def test_arbitrary_precision_inputs_are_not_rounded_through_float64():
    import mpmath

    ctx = mpmath.mp.clone()
    ctx.dps = 200
    levels = ["1.000000000000000000000000000000000000000000001",
              "1.000000000000000000000000000000000000000000002"]
    result = precise_matter_response([[levels[0], "0"], ["0", levels[1]]],
                                    [["1", "0"], ["0", "1"]], ("1", "1e-46"))
    actual = [ctx.mpc(*result["response"][i][i]) for i in range(2)]
    for i in range(2):
        expected = 1/(ctx.mpc(1, "1e-46")-ctx.mpf(levels[i]))
        assert abs(actual[i]/expected-1) < ctx.mpf("1e-79")
    assert abs(actual[0]-actual[1]) > ctx.mpf("1e44")
    assert result["response"][0][1] == ("0.0", "0.0")
    assert result["working_precisions"][0] > 100
