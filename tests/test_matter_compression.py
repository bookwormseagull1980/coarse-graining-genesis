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
from cg_core.matter_compression import covariant_matter_pullback, compressed_matter_response
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
