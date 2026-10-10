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

"""Actual RP3 spinor integrals for an explicitly specified action realization.

The spin lift, normalized Haar modes and finite Higgs connector are those
used by the native construction. Intrinsic Dirac sign is never identified
with four-dimensional chirality. External kinetic coefficients, the action
Yukawa/quartic, volume convention and quantum matching conditions remain
explicit data; exact internal integrals do not determine them.
"""
from __future__ import annotations

import math
import numpy as np

from cg_core import modal_algebra as modes
from cg_core.finite_connector import elementary_connector
from cg_core.matter_matching import canonical_vertex, canonical_flavour_pair


def spinor_fields(labels):
    """Expand genuine coupled spinor modes in scalar Haar modes x C^2."""
    fields = []
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("nonempty distinct valid spinor labels required")
    for label in labels:
        modes.spinor_dirac_value(label)
        j, m, J, M = label
        field = {}
        for component, s in enumerate((-.5, .5)):
            n = M - s
            if n == int(n) and abs(n) <= j:
                coefficient = modes.clebsch_gordan(j, n, .5, s, J, M)
                if coefficient:
                    vector = np.zeros(2, complex)
                    vector[component] = coefficient
                    field[(j, m, int(n))] = vector
        fields.append(field)
    return tuple(fields)


def modal_inner(left, right):
    """Exact Haar integral by orthogonality, retaining all bundle indices."""
    return sum((np.vdot(value, right[label]) for label, value in left.items()
                if label in right), 0j)


def spinor_gram(labels):
    fields = spinor_fields(labels)
    return np.array([[modal_inner(a, b) for b in fields] for a in fields])


def spinor_vertex(profile, left_labels, right_labels):
    """Integral Psi_L^dagger h Psi_R by actual finite mode multiplication.

    L/R label independent external matter factors, not intrinsic Dirac sign.
    Projection onto the supplied left modes is explicit. To keep all output
    support take j_left_max >= j_right_max + j_profile_max, with both signs.
    """
    for label, coefficient in profile.items():
        modes.eigenvalue(label)
        if np.ndim(coefficient) or not np.isfinite(coefficient):
            raise ValueError("finite scalar profile coefficients required")
    left, right = spinor_fields(left_labels), spinor_fields(right_labels)
    outputs = tuple(modes.multiply(profile, psi) for psi in right)
    return np.array([[modal_inner(a, b) for b in outputs] for a in left])


def lowest_signed_spatial_kernel(*, basepoint=(0., 0., 0.)):
    """Generated finite source kernel between the lowest opposite Dirac signs.

    Normalized adjoint evaluation selects the radial spin-1/2 subspace in
    the complete negative j=1 shell. Actual multiplication by the centred
    character chi_1 has radial coefficient 1/sqrt(3). Its projected block,
    multiplied by sqrt(3), is an isometry from the complete positive j=0
    doublet onto that negative radial doublet. The remaining four negative
    magnetic modes are retained as the orthogonal source complement.

    For B denoting this kernel, R_L^* B R_R=I_2 fixes the spatial factor
    of a specified mass vertex. Action coefficients and canonical kinetic
    forms are applied separately to that finite source readout.
    """
    from scipy.linalg import expm
    point = np.asarray(basepoint, float)
    if point.shape != (3,) or not np.isfinite(point).all():
        raise ValueError("three finite basepoint rotation coordinates required")
    right_labels = modes.spinor_basis(0)
    left_labels = tuple(label for label in modes.spinor_basis(1)
                        if label[0] == 1 and label[2] == .5)
    representation = expm(-1j*sum(point[a]*modes.spin_matrices(1)[a]
                                  for a in range(3)))
    left = np.zeros((len(left_labels), 2), complex)
    translation = np.zeros((len(left_labels), len(left_labels)), complex)
    for a, (j, m, J, M) in enumerate(left_labels):
        for column, s in enumerate((-.5, .5)):
            n = M-s
            if n == int(n) and abs(n) <= j:
                left[a, column] = (representation[m+1, int(n)+1].conjugate()
                    *modes.clebsch_gordan(j, n, .5, s, J, M))
        for b, (_, p, K, N) in enumerate(left_labels):
            if J == K and M == N:
                translation[a, b] = representation[m+1, p+1].conjugate()
    right = np.eye(2, dtype=complex)
    profile = {(1, m, n): representation[m+1, n+1].conjugate()/math.sqrt(3)
               for m in range(-1, 2) for n in range(-1, 2)}
    raw = spinor_vertex(profile, left_labels, right_labels)
    left_projector = left@left.conj().T
    kernel = math.sqrt(3)*left_projector@raw
    residuals = {
        "left_gram": float(np.linalg.norm(left.conj().T@left-np.eye(2))),
        "gaunt_readout": float(np.linalg.norm(left.conj().T@raw-np.eye(2)/math.sqrt(3))),
        "partial_isometry": float(np.linalg.norm(kernel.conj().T@kernel-np.eye(2))),
        "range_projector": float(np.linalg.norm(kernel@kernel.conj().T-left_projector)),
        "source_readout": float(np.linalg.norm(left.conj().T@kernel-np.eye(2))),
        "source_complement": float(np.linalg.norm((np.eye(6)-left_projector)@kernel)),
    }
    if max(residuals.values()) > 2e-12:
        raise ArithmeticError("lowest signed spatial kernel failed its Gaunt identities")
    return {"left_labels": left_labels, "right_labels": right_labels,
            "left_embedding": left, "right_embedding": right,
            "left_translation": translation, "right_translation": right,
            "left_projector": left_projector, "right_projector": right,
            "source_profile": profile, "raw_gaunt": raw, "kernel": kernel,
            "gaunt_coefficient": 1/math.sqrt(3), "normalization": math.sqrt(3),
            "left_dirac_position": -2.5, "right_dirac_position": 1.5,
            "left_ambient_dimension": 6, "right_ambient_dimension": 2,
            "source_dimension": 2, "left_complement_dimension": 4,
            "residuals": residuals}


def positive_shell_labels(shells=(0, 1, 2)):
    """Complete positive Dirac shells, with every magnetic multiplicity.

    The three retained positive positions n=0,2,4 have j=0,1,2 and
    dimensions 2,12,30. A shell index is not a selected single spinor.
    """
    shells = tuple(shells)
    if (not shells or any(not isinstance(j, (int, np.integer)) or j < 0 for j in shells)
            or tuple(sorted(set(shells))) != shells):
        raise ValueError("distinct increasing nonnegative integer shells required")
    return tuple(label for label in modes.spinor_basis(int(shells[-1]))
                 if label[0] in shells and label[2] == label[0]+.5)


def shell_vertex_resolution(profile, *, shells=(0, 1, 2), transfer=None):
    """Complete Gaunt vertex and positive Gram budget for retained shells.

    This evaluates M_profile T, with T constant on each incoming shell.
    Its outputs include both intrinsic Dirac signs and all product support.
    The exact identity B*B=P T* M_|profile|² T P is checked independently
    by multiplying the scalar source before forming its spinor matrix.
    The retained, higher-positive and negative-sign contributions are kept
    separately. They are kinematic vertex norms, not integrated self-energies.
    """
    scalar_profile_integrals(profile)
    shells = tuple(shells)
    inputs = positive_shell_labels(shells)
    transfer = np.ones(len(shells)) if transfer is None else np.asarray(transfer, complex)
    if transfer.shape != (len(shells),) or not np.isfinite(transfer).all():
        raise ValueError("one finite transfer coefficient for each retained shell required")
    factors = np.array([transfer[shells.index(label[0])] for label in inputs])
    max_output = int(shells[-1])+max(label[0] for label in profile)
    outputs = modes.spinor_basis(max_output)
    full = spinor_vertex(profile, outputs, inputs)*factors
    retained_rows = [i for i, label in enumerate(outputs) if label in inputs]
    negative_rows = [i for i, label in enumerate(outputs) if label[2] < label[0]]
    positive_rows = [i for i, label in enumerate(outputs)
                     if label[2] > label[0] and label not in inputs]
    retained, negative, higher = full[retained_rows], full[negative_rows], full[positive_rows]
    grams = {"retained": retained.conj().T@retained,
             "negative": negative.conj().T@negative,
             "higher_positive": higher.conj().T@higher}
    squared_profile = modes.multiply(modes.adjoint(profile), profile)
    independent = spinor_vertex(squared_profile, inputs, inputs)
    independent = factors.conj()[:, None]*independent*factors[None, :]
    closure = float(np.linalg.norm(sum(grams.values())-independent, ord=2))
    tolerance = 2e-12*max(1., float(np.linalg.norm(independent, ord=2)))
    if closure > tolerance:
        raise ArithmeticError("complete spinor product failed its positive Gram budget")
    blocks = np.empty((len(shells), len(shells)))
    for i, left_j in enumerate(shells):
        rows = [a for a, label in enumerate(inputs) if label[0] == left_j]
        for k, right_j in enumerate(shells):
            columns = [a for a, label in enumerate(inputs) if label[0] == right_j]
            blocks[i, k] = np.linalg.norm(retained[np.ix_(rows, columns)])**2
    return {"input_labels": inputs, "output_labels": outputs,
            "shells": shells,
            "shell_dimensions": tuple(sum(label[0] == j for label in inputs) for j in shells),
            "transfer": transfer, "retained_vertex": retained,
            "full_vertex": full, "negative_vertex": negative,
            "higher_positive_vertex": higher, "grams": grams,
            "full_gram": independent, "closure_residual": closure,
            "shell_hilbert_schmidt_squared": blocks,
            "omitted_operator_norm": float(np.sqrt(max(0., np.linalg.eigvalsh(
                grams["negative"]+grams["higher_positive"])[-1])))}


def native_shell_action_pair(up_source, down_source, scalar_profile, *,
                             up_transfer, down_transfer, up_coefficient,
                             down_coefficient, left_kinetic, up_right_kinetic,
                             down_right_kinetic, scalar_kinetic, measure_volume,
                             shells=(0, 1, 2)):
    """Two forward vertices of one separated action on complete Dirac shells.

    The elementary Higgs profile, left kinetic form and volume are shared.
    The raw operators are V*y_f*M_(source_f*h)*T_f; all modal integrals
    precede the retained projection. Both sectors use the same left frame.
    Sources and transfer coefficients are supplied action data, not inferred
    from target masses or mixing. The output remains the complete internal
    shell space; a three-family physical projection must be supplied by its
    own source/retention rule before identifying a CKM matrix.
    """
    coefficients = (left_kinetic, up_right_kinetic, down_right_kinetic,
                    scalar_kinetic, measure_volume)
    if not all(np.isfinite(x) and x > 0 for x in coefficients):
        raise ValueError("positive finite kinetic coefficients and volume required")
    if not all(np.ndim(x) == 0 and np.isfinite(x) for x in (up_coefficient, down_coefficient)):
        raise ValueError("finite scalar action coefficients required")
    scalar_profile_integrals(up_source)
    scalar_profile_integrals(down_source)
    integrals = scalar_profile_integrals(scalar_profile)
    up = shell_vertex_resolution(modes.multiply(up_source, scalar_profile),
                                 shells=shells, transfer=up_transfer)
    down = shell_vertex_resolution(modes.multiply(down_source, scalar_profile),
                                   shells=shells, transfer=down_transfer)
    gram = spinor_gram(up["input_labels"])
    left = measure_volume*left_kinetic*gram
    scalar = measure_volume*scalar_kinetic*integrals["quadratic"]
    yu = canonical_vertex(measure_volume*up_coefficient*up["retained_vertex"],
                          left, measure_volume*up_right_kinetic*gram, scalar)
    yd = canonical_vertex(measure_volume*down_coefficient*down["retained_vertex"],
                          left, measure_volume*down_right_kinetic*gram, scalar)
    hu, hd = yu@yu.conj().T, yd@yd.conj().T
    return {"labels": up["input_labels"], "shell_dimensions": up["shell_dimensions"],
            "up": up, "down": down, "left_gram": left, "scalar_gram": scalar,
            "up_canonical_vertex": yu, "down_canonical_vertex": yd,
            "up_singular_values": np.linalg.svd(yu, compute_uv=False)[::-1],
            "down_singular_values": np.linalg.svd(yd, compute_uv=False)[::-1],
            "left_commutator_norm": float(np.linalg.norm(hu@hd-hd@hu, ord=2)),
            "physical_family_projection_supplied": False}


def radial_spinor_family(*, basepoint=(0., 0., 0.)):
    """Covariant lowest-spin readout of the three complete positive shells.

    In the left-trivialized spin bundle, evaluation at g in SU(2) is
    Ev_g:F_j^+ -> C^2. Its adjoint, divided by sqrt(d_j/2), is an isometry
    R_j. Under the isotropy group at g this is the unique spin-1/2 copy in
    V_j tensor V_(j+1/2). Thus three shells give three radial spinors without
    choosing one magnetic state from each shell. Family order is j=2,1,0.

    basepoint is a Lie-algebra rotation vector: D^j(g)=exp(-i b.J).
    The centred character chi_k(g^-1 x) is multiplied in the full Gaunt
    algebra before projection. Its j=2<->1, 1<->0 and 2<->0 radial blocks
    have coefficients 3/sqrt(10), sqrt(2/3), sqrt(3/5), respectively.
    Sandwiching by the radial projectors and dividing by those computed
    coefficients supplies native matrix units. This is a finite-rank
    internal source kernel, not a pointwise scalar multiplication ansatz.
    """
    from scipy.linalg import expm
    point = np.asarray(basepoint, float)
    if point.shape != (3,) or not np.isfinite(point).all():
        raise ValueError("three finite basepoint rotation coordinates required")
    labels = positive_shell_labels()
    representations = {j: expm(-1j*sum(point[a]*modes.spin_matrices(j)[a]
                                      for a in range(3))) for j in range(3)}
    embedding = np.zeros((len(labels), 6), complex)
    translation = np.zeros((len(labels), len(labels)), complex)
    for a, (j, m, J, M) in enumerate(labels):
        for spin, s in enumerate((-.5, .5)):
            n = M-s
            if n == int(n) and abs(n) <= j:
                embedding[a, 2*(2-j)+spin] = (
                    representations[j][m+j, int(n)+j].conjugate()
                    *modes.clebsch_gordan(j, n, .5, s, J, M)/math.sqrt(j+1))
        for b, (ell, p, K, N) in enumerate(labels):
            if j == ell and J == K and M == N:
                translation[a, b] = representations[j][m+j, p+j].conjugate()
    projectors = tuple(embedding[:, 2*i:2*i+2]@embedding[:, 2*i:2*i+2].conj().T
                       for i in range(3))
    character_vertices = {}
    for k in (1, 2):
        profile = {(k, m, n): representations[k][m+k, n+k].conjugate()/math.sqrt(2*k+1)
                   for m in range(-k, k+1) for n in range(-k, k+1)
                   if representations[k][m+k, n+k] != 0}
        character_vertices[k] = spinor_vertex(profile, labels, labels)
    units = {(i, i): p for i, p in enumerate(projectors)}
    coefficients = {(0, 1): 3/math.sqrt(10), (1, 2): math.sqrt(2/3),
                    (0, 2): math.sqrt(3/5)}
    for (i, j), coefficient in coefficients.items():
        k = 2 if (i, j) == (0, 2) else 1
        units[i, j] = projectors[i]@character_vertices[k]@projectors[j]/coefficient
        units[j, i] = units[i, j].conj().T
    gram_error = float(np.linalg.norm(embedding.conj().T@embedding-np.eye(6), ord=2))
    unit_error = max(float(np.linalg.norm(units[i, j]-
        embedding[:, 2*i:2*i+2]@embedding[:, 2*j:2*j+2].conj().T, ord=2))
        for i in range(3) for j in range(3))
    if max(gram_error, unit_error) > 2e-12:
        raise ArithmeticError("radial evaluation or native matrix-unit normalization failed")
    return {"labels": labels, "embedding": embedding, "projectors": projectors,
            "source_projector": sum(projectors), "translation": translation,
            "character_vertices": character_vertices, "matrix_units": units,
            "gaunt_coefficients": coefficients, "family_shell_order": (2, 1, 0),
            "basepoint": point, "gram_residual": gram_error, "matrix_unit_residual": unit_error}


def native_family_action(up_transfer, down_transfer, *, angular_sines, phase,
                         up_coefficient, down_coefficient, left_kinetic,
                         up_right_kinetic, down_right_kinetic, scalar_kinetic,
                         measure_volume, basepoint=(0., 0., 0.)):
    """Forward common-action realization of the specified native readouts.

    Input transfer factors use light-to-heavy order. The three angle sines
    and phase prescribe the ordered 23,13,12 source operations. The actual
    generators are obtained from radial spectral projectors and character
    multiplication, without diagonalizing a target matrix. Their exponential
    acts on all 44 retained spinors and is the identity on the orthogonal
    complement; the weighted vertex is supported on the six radial spinors.
    That complement retains its original Dirac spectral identity and is not
    included in the selected three-family source action.

    The Higgs radial profile is constant and has unit normalized-Haar norm.
    Both sectors share its kinetic term and the left kinetic form. A scalar
    block is extracted only after checking the exact spin-1/2 factorization.
    This realizes the inherited transfer/angle prescriptions as one action;
    selection of the ordered source sequence is a separate physical rule.
    """
    from scipy.linalg import expm
    transfers = tuple(np.asarray(t, float) for t in (up_transfer, down_transfer))
    if any(t.shape != (3,) or not np.isfinite(t).all() or np.any(t < 0) for t in transfers):
        raise ValueError("three finite nonnegative transfer factors per sector required")
    sines = np.asarray(angular_sines, float)
    if (sines.shape != (3,) or not np.isfinite(sines).all() or np.any(abs(sines) > 1)
            or not np.isfinite(phase)):
        raise ValueError("finite phase and three angle sines in [-1,1] required")
    if not all(np.isfinite(x) and x > 0 for x in
               (left_kinetic, up_right_kinetic, down_right_kinetic,
                scalar_kinetic, measure_volume)):
        raise ValueError("positive finite kinetic coefficients and volume required")
    if not all(np.ndim(x) == 0 and np.isfinite(x) for x in (up_coefficient, down_coefficient)):
        raise ValueError("finite scalar action coefficients required")
    radial = radial_spinor_family(basepoint=basepoint)
    units, embedding = radial["matrix_units"], radial["embedding"]
    angles = np.arcsin(sines)
    generators = (units[0, 1]-units[1, 0],
                  units[1, 2]-units[2, 1],
                  np.exp(-1j*phase)*units[0, 2]-np.exp(1j*phase)*units[2, 0])
    rotation = expm(angles[1]*generators[1])@expm(angles[2]*generators[2])@expm(angles[0]*generators[0])
    up_operator = up_coefficient*sum(t*units[i, i] for i, t in enumerate(transfers[0]))
    down_operator = down_coefficient*rotation@sum(t*units[i, i] for i, t in enumerate(transfers[1]))
    family_vertices, spin_errors = [], []
    for operator in (up_operator, down_operator):
        small = embedding.conj().T@operator@embedding
        vertex = np.array([[np.trace(small[2*i:2*i+2, 2*j:2*j+2])/2
                            for j in range(3)] for i in range(3)])
        family_vertices.append(measure_volume*vertex)
        spin_errors.append(float(np.linalg.norm(small-np.kron(vertex, np.eye(2)), ord=2)))
    left = measure_volume*left_kinetic*np.eye(3)
    right_u, right_d = (measure_volume*x*np.eye(3) for x in (up_right_kinetic, down_right_kinetic))
    scalar = measure_volume*scalar_kinetic
    flavour = canonical_flavour_pair(*family_vertices, left, right_u, right_d, scalar)
    complement = np.eye(len(embedding))-radial["source_projector"]
    residuals = {"radial_gram": radial["gram_residual"],
        "matrix_units": radial["matrix_unit_residual"], "spin_factorization": max(spin_errors),
        "rotation_unitarity": float(np.linalg.norm(rotation.conj().T@rotation-np.eye(len(embedding)), ord=2)),
        "complement_rotation_identity": float(np.linalg.norm((rotation-np.eye(len(embedding)))@complement, ord=2)),
        "complement_source_vertex": max(float(np.linalg.norm(operator@complement, ord=2))
                                         for operator in (up_operator, down_operator))}
    if max(residuals.values()) > 2e-12:
        raise ArithmeticError("native family source action failed its structural identities")
    return {"radial": radial, "ambient_up_vertex": up_operator,
            "ambient_down_vertex": down_operator, "ambient_rotation": rotation,
            "family_up_raw_vertex": family_vertices[0], "family_down_raw_vertex": family_vertices[1],
            "left_gram": left, "up_right_gram": right_u, "down_right_gram": right_d,
            "scalar_gram": scalar, "flavour": flavour, "residuals": residuals,
            "ambient_dimension": len(embedding), "source_dimension": 6, "complement_dimension": len(embedding)-6,
            "source_sequence_uniqueness_proved": False}


def scalar_profile_integrals(profile):
    """Actual quadratic and quartic Haar integrals of a complex scalar mode."""
    if not profile:
        raise ValueError("nonzero scalar profile required")
    for label, coefficient in profile.items():
        modes.eigenvalue(label)
        if np.ndim(coefficient) or not np.isfinite(coefficient):
            raise ValueError("finite scalar profile coefficients required")
    second = float(modal_inner(profile, profile).real)
    norm_square = modes.multiply(modes.adjoint(profile), profile)
    fourth = float(modal_inner(norm_square, norm_square).real)
    if second <= 0 or fourth <= 0:
        raise ValueError("nonzero scalar profile required")
    return {"quadratic": second, "quartic": fourth}


def native_vertex(profile, left_labels, right_labels, *, yukawa_coefficient,
                  left_kinetic, right_kinetic, scalar_kinetic, measure_volume):
    """Canonical spatial vertex of one declared separated action.

    Raw fields are Haar-normalized; the action measure is V*dmu_Haar.
    Its quadratic forms are V*Z_L/R times the actual spinor Grams and
    V*Z_H*integral|h|^2. Its raw vertex is V*y_action*integral Psi_L^dag h Psi_R.
    Thus the vertex scales as y_action/sqrt(V Z_L Z_R Z_H). Dimensionful
    conversion to a four-dimensional coupling requires the supplied action
    convention; V=1 states normalized Haar units, not a measured compact volume.
    """
    if not all(math.isfinite(x) and x > 0 for x in
               (left_kinetic, right_kinetic, scalar_kinetic, measure_volume)):
        raise ValueError("positive finite kinetic coefficients and volume required")
    if not np.isfinite(yukawa_coefficient):
        raise ValueError("finite action Yukawa coefficient required")
    overlaps = spinor_vertex(profile, left_labels, right_labels)
    left_gram = measure_volume * left_kinetic * spinor_gram(left_labels)
    right_gram = measure_volume * right_kinetic * spinor_gram(right_labels)
    integrals = scalar_profile_integrals(profile)
    scalar_gram = measure_volume * scalar_kinetic * integrals["quadratic"]
    raw = measure_volume * yukawa_coefficient * overlaps
    return {"vertex": canonical_vertex(raw, left_gram, right_gram, scalar_gram),
            "raw_vertex": raw, "left_gram": left_gram, "right_gram": right_gram,
            "scalar_gram": scalar_gram, "profile_integrals": integrals}


def canonical_quartic(profile, *, quartic_coefficient, scalar_kinetic, measure_volume):
    """Coefficient of (H^dagger H)^2 for the same separated scalar action."""
    if not math.isfinite(quartic_coefficient) or not all(
            math.isfinite(x) and x > 0 for x in (scalar_kinetic, measure_volume)):
        raise ValueError("finite quartic and positive kinetic coefficient/volume required")
    integrals = scalar_profile_integrals(profile)
    return (quartic_coefficient * integrals["quartic"] /
            (measure_volume * scalar_kinetic**2 * integrals["quadratic"]**2))


def evaluate_native_matching(*, quartic_coefficient, profile_amplitude=.4,
                             family_transfers=None, family_angular_data=None):
    """JSON-ready RP3 integrals and specified-action coefficient sensitivity.

    The constant profile is the spatial realization of the finite unit seed.
    The additional real shell-one profile is a declared source perturbation,
    not a replacement for the production top Yukawa. Action coefficients
    below define a conditional realization and are not inferred by fitting.
    """
    if not math.isfinite(profile_amplitude):
        raise ValueError("finite profile amplitude required")
    right, complete = modes.spinor_basis(0), modes.spinor_basis(1)
    settings = dict(yukawa_coefficient=1., left_kinetic=1., right_kinetic=1.,
                    scalar_kinetic=1., measure_volume=1.)
    constant = {(0, 0, 0): 1.}
    uniform = native_vertex(constant, right, right, **settings)
    seed_yukawa = float(np.linalg.svd(uniform["vertex"], compute_uv=False)[0])
    seed_quartic = canonical_quartic(constant,
        quartic_coefficient=quartic_coefficient, scalar_kinetic=1., measure_volume=1.)
    family_pair = canonical_flavour_pair(seed_yukawa*np.eye(3), seed_yukawa*np.eye(3),
        np.eye(3), np.eye(3), np.eye(3), 1.)
    eta = profile_amplitude
    normalization = math.sqrt(1 + eta**2)
    profile = {(0, 0, 0): 1/normalization, (1, 0, 0): eta/normalization}
    spatial = native_vertex(profile, complete, right, **settings)
    vertex = spatial["vertex"]
    # Independent Gaunt implementation checks the Haar-integral evaluation.
    gaunt = modes.spinor_multiplication(profile, right, complete)
    all_gram = vertex.conj().T @ vertex
    signs = modes.signed_cross_blocks(vertex, right, complete)
    negative_gram = signs[("-", "+")].conj().T @ signs[("-", "+")]
    expected_negative = eta**2/(3*(1+eta**2))
    exact_fourth = (1+6*eta**2+9*eta**4/5)/(1+eta**2)**2
    # The generated elementary doublet H=(0,1) has transfer I_8. Tensoring
    # keeps all finite matter coordinates, including the neutral right line.
    finite = elementary_connector([0., 1.])["transfer"]
    full_vertex = np.kron(vertex, finite)
    full_gram = full_vertex.conj().T @ full_vertex
    changed = native_vertex(profile, complete, right,
        **{**settings, "scalar_kinetic": 4.})
    quartic = canonical_quartic(profile, quartic_coefficient=quartic_coefficient,
                               scalar_kinetic=1., measure_volume=1.)
    quartic_changed = canonical_quartic(profile, quartic_coefficient=quartic_coefficient,
                                       scalar_kinetic=4., measure_volume=1.)
    residuals = {
        "spinor_gram": float(np.linalg.norm(spinor_gram(complete)-np.eye(len(complete)))),
        "constant_seed": float(np.linalg.norm(uniform["vertex"]-np.eye(2))),
        "gaunt_integral": float(np.linalg.norm(vertex-gaunt)),
        "complete_support": float(np.linalg.norm(all_gram-np.eye(2))),
        "negative_projection": float(np.linalg.norm(negative_gram-expected_negative*np.eye(2))),
        "scalar_quartic": abs(spatial["profile_integrals"]["quartic"]-exact_fourth),
        "full_matter_vertex": float(np.linalg.norm(full_gram-np.eye(16))),
        "kinetic_rescaling_yukawa": float(np.linalg.norm(2*changed["vertex"]-vertex)),
        "kinetic_rescaling_quartic": abs(16*quartic_changed-quartic),
    }
    if any(value > 2e-12 for value in residuals.values()):
        raise ArithmeticError("native RP3 matching integral failed its independent identity")
    signed = lowest_signed_spatial_kernel()
    shifted_signed = lowest_signed_spatial_kernel(basepoint=(.23, -.31, .19))
    independent_signed = modes.spinor_multiplication(signed["source_profile"],
        signed["right_labels"], signed["left_labels"])
    signed_residuals = {**signed["residuals"],
        "independent_gaunt": float(np.linalg.norm(signed["raw_gaunt"]-independent_signed)),
        "basepoint_gaunt_covariance": float(np.linalg.norm(shifted_signed["raw_gaunt"]-
            shifted_signed["left_translation"]@signed["raw_gaunt"])),
        "basepoint_kernel_covariance": float(np.linalg.norm(shifted_signed["kernel"]-
            shifted_signed["left_translation"]@signed["kernel"])),
    }
    if max(signed_residuals.values()) > 2e-12:
        raise ArithmeticError("signed spatial connector failed its independent checks")
    shell_sources = {}
    for k in (1, 2):
        resolved = shell_vertex_resolution({(k, 0, 0): 1.})
        shell_sources[f"e{k}00"] = {
            "shell_hilbert_schmidt_squared": resolved["shell_hilbert_schmidt_squared"].tolist(),
            "gram_traces": {name: float(np.trace(g).real)
                            for name, g in resolved["grams"].items()},
            "omitted_operator_norm": resolved["omitted_operator_norm"],
            "closure_residual": resolved["closure_residual"]}
    shell_action = None
    joint_family = None
    if family_transfers is not None:
        up_transfer, down_transfer = family_transfers["up"], family_transfers["down"]
        pair = native_shell_action_pair(constant, constant, constant,
            up_transfer=up_transfer, down_transfer=down_transfer,
            up_coefficient=1., down_coefficient=1., left_kinetic=1.,
            up_right_kinetic=1., down_right_kinetic=1., scalar_kinetic=1., measure_volume=1.)
        errors = {sector: float(np.max(np.abs(pair[f"{sector}_singular_values"]-
            np.sort(np.repeat(np.abs(transfer), pair["shell_dimensions"])))))
            for sector, transfer in (("up", up_transfer), ("down", down_transfer))}
        if max(errors.values()) > 2e-12 or pair["left_commutator_norm"] > 2e-12:
            raise ArithmeticError("constant-source shell transfer action failed its spectral identity")
        shell_action = {"scope": "production transfer factors in the common constant-source shell action",
            "shell_order": [0, 1, 2], "shell_dimensions": list(pair["shell_dimensions"]),
            "up_transfer": list(up_transfer), "down_transfer": list(down_transfer),
            "singular_value_residuals": errors,
            "left_commutator_norm": pair["left_commutator_norm"],
            "action_normalization": "normalized Haar, unit common scalar and kinetic coefficients; sector bases factored out",
            "physical_family_projection_supplied": False,
            "angular_source_realization_supplied": False,
            "production_replacement": False}
        if family_angular_data is not None:
            arguments = dict(angular_sines=family_angular_data["angular_sines"],
                phase=family_angular_data["phase"], up_coefficient=1.,
                down_coefficient=family_angular_data["down_coefficient"],
                left_kinetic=1., up_right_kinetic=1., down_right_kinetic=1.,
                scalar_kinetic=1., measure_volume=1.)
            action = native_family_action(up_transfer[::-1], down_transfer[::-1], **arguments)
            translated = native_family_action(up_transfer[::-1], down_transfer[::-1],
                **arguments, basepoint=(.23, -.31, .19))
            transport = translated["radial"]["translation"]
            covariant_errors = {sector: float(np.linalg.norm(translated[f"ambient_{sector}_vertex"]-
                transport@action[f"ambient_{sector}_vertex"]@transport.conj().T, ord=2))
                for sector in ("up", "down")}
            flavour = action["flavour"]
            s12, s23, s13 = arguments["angular_sines"]
            expected_J = s12*s23*s13*math.sqrt((1-s12*s12)*(1-s23*s23))*(1-s13*s13)*math.sin(arguments["phase"])
            expected_up = np.sort(np.abs(up_transfer))
            expected_down = arguments["down_coefficient"]*np.sort(np.abs(down_transfer))
            recovery = {"up_singular_values": float(np.max(abs(flavour["up_yukawa"]-expected_up))),
                "down_singular_values": float(np.max(abs(flavour["down_yukawa"]-expected_down))),
                "J": abs(flavour["J"]-expected_J),
                "basepoint_mixing_moduli": float(np.max(abs(abs(flavour["mixing"])-abs(translated["flavour"]["mixing"]))))}
            if max((*covariant_errors.values(), *recovery.values())) > 2e-12:
                raise ArithmeticError("native family action failed its covariant readout recovery")
            joint_family = {
                "scope": "forward native spectral-kernel realization of inherited mass transfers and ordered angular source",
                "family_shell_order": [2, 1, 0], "ambient_dimension": 44,
                "source_dimension": 6, "complement_dimension": 38,
                "radial_projection": "R_j=Ev_g^*/sqrt(d_j/2), the unique isotropy spin-1/2 copy",
                "native_matrix_units": "radial spectral projectors times centred-character multiplication, with Clebsch-Gordan normalization",
                "gaunt_coefficients": {"j2_j1": 3/math.sqrt(10), "j1_j0": math.sqrt(2/3),
                                       "j2_j0": math.sqrt(3/5)},
                "source_sequence": "exp(theta23 A23) exp(theta13 A13(delta)) exp(theta12 A12)",
                "inputs": arguments, "up_transfer": list(up_transfer[::-1]),
                "down_transfer": list(down_transfer[::-1]),
                "up_yukawa": flavour["up_yukawa"].tolist(), "down_yukawa": flavour["down_yukawa"].tolist(),
                "mixing_moduli": abs(flavour["mixing"]).tolist(), "J": flavour["J"],
                "commutator_norm": flavour["commutator_norm"],
                "imag_trace_commutator_cubed": flavour["imag_trace_commutator_cubed"],
                "shared_left_gram": action["left_gram"].real.tolist(),
                "up_vertex_real": flavour["up_canonical_vertex"].real.tolist(),
                "up_vertex_imag": flavour["up_canonical_vertex"].imag.tolist(),
                "down_vertex_real": flavour["down_canonical_vertex"].real.tolist(),
                "down_vertex_imag": flavour["down_canonical_vertex"].imag.tolist(),
                "complement": "original Dirac spectral complement; source vertices vanish and source rotations act as identity",
                "structural_residuals": action["residuals"], "readout_recovery_residuals": recovery,
                "basepoint_covariance_residuals": covariant_errors,
                "inherited_angular_prescription_realized": True,
                "source_sequence_uniqueness_proved": False,
                "finite_MSbar_matching_established": False}
    return {"scope": "actual selected RP3 spinors and full elementary connector in an explicit action realization",
        "inputs": {"action_coefficients": settings, "quartic_coefficient": quartic_coefficient,
                   "H_finite": [0., 1.], "spin_lift": "left-trivialized selected lift, integer j",
                   "incoming_labels": [list(x) for x in right],
                   "outgoing_labels": [list(x) for x in complete],
                   "measure": "normalized RP3 Haar; action volume multiplier V=1",
                   "source_profile": "(1+eta*e100)/sqrt(1+eta^2)", "eta": eta},
        "constant_connector": {"spatial_yukawa_factor": 1., "scalar_quartic_factor": 1.,
                               "canonical_yukawa_singular_value": seed_yukawa,
                               "canonical_quartic": seed_quartic,
                               "four_dimensional_chirality": "finite matter L/R; independent of intrinsic Dirac sign"},
        "signed_spatial_connector": {
            "scope": "finite mass-vertex source between the lowest positive and negative Dirac radial doublets",
            "construction": "sqrt(3) Pi_rad,- M_chi1 Pi_low,+ in normalized Haar measure",
            "gaunt_coefficient": signed["gaunt_coefficient"],
            "normalization": signed["normalization"],
            "left_dirac_position": signed["left_dirac_position"],
            "right_dirac_position": signed["right_dirac_position"],
            "left_ambient_dimension": signed["left_ambient_dimension"],
            "right_ambient_dimension": signed["right_ambient_dimension"],
            "source_dimension": signed["source_dimension"],
            "left_complement_dimension": signed["left_complement_dimension"],
            "canonical_source_factor": 1.,
            "mass_vertex_readout": "R_L^* B R_R=I_2; a specified action coefficient multiplies this spatial pairing",
            "residuals": signed_residuals},
        "generation_symmetric_action": {
            "up_yukawa_singular_values": family_pair["up_yukawa"].tolist(),
            "down_yukawa_singular_values": family_pair["down_yukawa"].tolist(),
            "commutator_norm": family_pair["commutator_norm"],
            "simple_left_spectra": family_pair["simple_left_spectra"],
            "mixing_fixed_by_action": family_pair["mixing"] is not None,
            "family_action": "identical copies of the computed constant connector"},
        "nonconstant_source": {"profile_quadratic": spatial["profile_integrals"]["quadratic"],
            "profile_quartic": spatial["profile_integrals"]["quartic"],
            "canonical_yukawa_singular_values": np.linalg.svd(vertex,compute_uv=False).tolist(),
            "lowest_to_lowest_factor": 1/normalization,
            "negative_output_norm_squared_per_input": np.diag(negative_gram).real.tolist(),
            "full_matter_vertex_shape": list(full_vertex.shape),
            "canonical_quartic": quartic,
            "physical_yukawa_replacement": False},
        "complete_shell_vertices": {"shell_order": [0, 1, 2], "shell_dimensions": [2, 12, 30],
            "source_basis": shell_sources,
            "gram_identity": "B*B = P T* M_|h|^2 T P; retained + negative + higher-positive outputs",
            "production_transfer_action": shell_action},
        "joint_family_action": joint_family,
        "matching": {"physical_msbar_boundary_determined": False,
            "unidentified_inputs": ["action Yukawa coefficient", "external matter kinetic coefficients",
                                    "external scalar kinetic coefficient", "four-dimensional quartic and finite local terms",
                                    "gauge kinetic coefficient and quantum matching map"],
            "scaling_relations": {"y_can": "y_action / sqrt(V*Z_L*Z_R*Z_H) times the normalized spatial overlap",
                                  "lambda_can": "lambda_action*I4/(V*Z_H^2*I2^2)"},
            "coefficient_sensitivity_scope":
                "partial action-realization diagnostic with fixed spatial modes; "
                "the full minimal-change construction and its transfer rules remain fixed by their own definitions"},
        "residuals": residuals, "checks_passed": True}
