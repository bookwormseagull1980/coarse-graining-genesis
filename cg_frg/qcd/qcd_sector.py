# -*- coding: utf-8 -*-
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

"""QCD scales, actual internal two-leg carrier, and specified mass readouts.

The Killing carrier is K=(1,0)+(0,1), dimension six. Its colour-singlet
bosonic square is Sym2(K), dimension 21. The actual representation
matrices and source projections are evaluated by cg_core.modal_algebra.
The candidate rule 8+C2 is an assigned internal operator. It does not
by itself supply an external J^PC map or a two-body bound-state kernel.

The four-channel mass catalogue uses coefficients 8,16,17,18. Its first
two entries agree with candidates of that operator; 17,18 are additional
excitation assignments. The lowest native complete scalar mode includes
the constant shell and is a different observable from this catalogue.

Lambda_QCD is supplied by the production running/extraction prescription.
Condensate energy and generator mass are parallel readouts, not implicit
threshold steps in the Lambda equation. The constituent-proton,
deconfinement, and string-tension maps retain their specified
normalizations; the latter is not a Wilson-loop area-law computation.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.modal_algebra import killing_two_body  # noqa: E402


def constituent_proton_readout(Lambda_QCD: float, tau: float) -> dict:
    """Evaluate the native proton map with explicit common-scale inputs.

    The Lambda input is the production five-flavour MSbar scale parameter.
    Its use in a constituent mass is defined by the dimensionless native
    coefficient, including the same torsion normalization as the other
    hadronic readouts. The output carries that mass definition explicitly.
    """
    if (not all(math.isfinite(v) for v in (Lambda_QCD, tau))
            or Lambda_QCD <= 0 or not 0 <= tau < .25):
        raise ValueError("positive finite Lambda and 0<=tau<1/4 required")
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    mass = ((9.0 / 2.0) * (1.0 - (1.0 / 8.0) / 4.0) * Lambda_QCD
            * (1.0 + tau * kappa * (10.0 / 3.0) * .5))
    return {"proton_mass_GeV": mass, "Lambda_GeV": Lambda_QCD,
            "Lambda_definition": "five-flavour MSbar production scale parameter",
            "tau": tau, "kappa": kappa, "dimensionless_coefficient": mass/Lambda_QCD,
            "mass_definition": "native constituent proton mass readout",
            "formula": "(279/64)*Lambda*(1+5*tau*kappa/3)"}


def proton_mass(Lambda_QCD: float) -> float:
    """The constituent proton readout on the current common torsion input."""
    return constituent_proton_readout(Lambda_QCD, float(get("tau")))["proton_mass_GeV"]


def matched_isovector_split(*, m_down, m_up, scalar_isovector_matrix_element,
                            electromagnetic_split, scale, scheme, source,
                            matrix_element_scale=None, matrix_element_scheme=None,
                            electromagnetic_convention=None,
                            electromagnetic_source=None, mass_source=None):
    """Evaluate C_ud(mu)[m_d(mu)-m_u(mu)]-Delta_EM in one stated convention.

    Delta_EM is the proton-minus-neutron electromagnetic contribution.
    Masses and the scalar density matrix element must share the same
    scale and mass-renormalization scheme; their product is invariant
    under reciprocal finite mass/scalar-density renormalizations. The
    strong/electromagnetic separation uses an explicitly supplied
    convention. Omitted scalar metadata inherits the common declaration
    for compatibility with the single-convention interface.

    Numerical evaluation does not supply a nucleon state or scalar
    matrix element. They enter through the stated source. Native mass
    readouts can use this algebra with their own mass definition, which
    remains distinct from a renormalized QCD mass convention.
    """
    values = (m_down, m_up, scalar_isovector_matrix_element, electromagnetic_split, scale)
    if not all(math.isfinite(x) for x in values) or min(m_down, m_up, scale) <= 0:
        raise ValueError("finite matching data and positive quark masses/scale required")
    if not isinstance(scheme, str) or not scheme.strip() or not isinstance(source, str) or not source.strip():
        raise ValueError("explicit mass scheme and scalar-matrix-element source required")
    matrix_element_scale = scale if matrix_element_scale is None else matrix_element_scale
    matrix_element_scheme = scheme if matrix_element_scheme is None else matrix_element_scheme
    if (not math.isfinite(matrix_element_scale) or matrix_element_scale != scale
            or matrix_element_scheme != scheme):
        raise ValueError("quark masses and scalar matrix element must share scheme and scale")
    em_convention = ("QCD/EM separation declared by the input source"
                     if electromagnetic_convention is None else electromagnetic_convention)
    em_source = source if electromagnetic_source is None else electromagnetic_source
    quark_source = source if mass_source is None else mass_source
    if not all(isinstance(text, str) and text.strip() for text in (em_convention, em_source, quark_source)):
        raise ValueError("nonempty mass and electromagnetic source declarations required")
    difference = m_down-m_up
    strong = scalar_isovector_matrix_element*difference
    total = strong-electromagnetic_split
    return {"neutron_proton_split": total, "strong_split_GeV": strong,
            "electromagnetic_proton_minus_neutron_GeV": electromagnetic_split,
            "quark_mass_difference_GeV": difference,
            "quark_masses_GeV": {"up": m_up, "down": m_down},
            "scalar_isovector_matrix_element": scalar_isovector_matrix_element,
            "scale": scale, "scheme": scheme, "mass_source": quark_source,
            "matrix_element_scale_GeV": matrix_element_scale,
            "matrix_element_scheme": matrix_element_scheme,
            "matrix_element_source": source, "electromagnetic_convention": em_convention,
            "electromagnetic_source": em_source,
            "formula": "C_ud*(m_down-m_up)-Delta_EM",
            "derivatives": {"m_down": scalar_isovector_matrix_element,
                            "m_up": -scalar_isovector_matrix_element,
                            "C_ud": difference, "Delta_EM": -1.}}


def matched_nucleon_masses(*, isoscalar_qcd_mass, electromagnetic_mean_shift,
                          isovector, isoscalar_source, electromagnetic_convention):
    """First-order isospin mass pair in the supplied QCD/EM separation.

    The QCD isoscalar mass is (M_p^QCD+M_n^QCD)/2. The electromagnetic
    mean is (delta M_p^EM+delta M_n^EM)/2. The same electromagnetic
    convention as the isovector record is required by definition. These
    inputs provide both mass channels; the splitting alone does not set
    their common scale.
    """
    if (not all(math.isfinite(x) for x in (isoscalar_qcd_mass, electromagnetic_mean_shift))
            or isoscalar_qcd_mass <= 0 or not isinstance(isoscalar_source, str)
            or not isoscalar_source.strip()):
        raise ValueError("positive QCD isoscalar mass and explicit source required")
    strong, em = isovector["strong_split_GeV"], isovector["electromagnetic_proton_minus_neutron_GeV"]
    total = isovector["neutron_proton_split"]
    if (electromagnetic_convention != isovector["electromagnetic_convention"]
            or not all(math.isfinite(v) for v in (strong, em, total))
            or not math.isclose(total, strong-em, rel_tol=1e-13, abs_tol=1e-16)):
        raise ValueError("one consistent isovector record and QCD/EM convention required")
    qcd_proton, qcd_neutron = isoscalar_qcd_mass-strong/2, isoscalar_qcd_mass+strong/2
    em_proton, em_neutron = electromagnetic_mean_shift+em/2, electromagnetic_mean_shift-em/2
    proton, neutron = qcd_proton+em_proton, qcd_neutron+em_neutron
    if not all(math.isfinite(x) and x > 0 for x in (qcd_proton, qcd_neutron, proton, neutron)):
        raise ValueError("the matched strong and total nucleon masses must be positive")
    return {"proton_mass_GeV": proton, "neutron_mass_GeV": neutron,
            "qcd_proton_mass_GeV": qcd_proton, "qcd_neutron_mass_GeV": qcd_neutron,
            "electromagnetic_proton_shift_GeV": em_proton,
            "electromagnetic_neutron_shift_GeV": em_neutron,
            "neutron_proton_split_GeV": isovector["neutron_proton_split"],
            "isoscalar_qcd_mass_GeV": isoscalar_qcd_mass,
            "electromagnetic_mean_shift_GeV": electromagnetic_mean_shift,
            "isoscalar_source": isoscalar_source,
            "electromagnetic_convention": isovector["electromagnetic_convention"],
            "mass_identity_residual_GeV": abs(neutron-proton-isovector["neutron_proton_split"]),
            "order": "linear strong isospin splitting plus supplied electromagnetic shifts"}


def native_nucleon_readout(*, Lambda_QCD, tau, m_down, m_up, alpha_em,
                          generation_scale):
    """The production proton anchor and isovector source in one mass record.

    C_ud=1 and Delta_EM=(1-1/(2*pi))*alpha*Lambda are the native source
    coefficients. The generation scale labels their spectral readout; it
    is not a QCD renormalization scale. A physical QCD matching instead
    supplies renormalized quark masses, their scalar matrix element, and
    a QCD/EM separation to matched_isovector_split and matched_nucleon_masses.
    """
    if not math.isfinite(alpha_em) or alpha_em < 0:
        raise ValueError("finite nonnegative electromagnetic coupling required")
    proton = constituent_proton_readout(Lambda_QCD, tau)
    electromagnetic = (1-1/(2*math.pi))*alpha_em*Lambda_QCD
    split = matched_isovector_split(m_down=m_down, m_up=m_up,
        scalar_isovector_matrix_element=1., electromagnetic_split=electromagnetic,
        scale=generation_scale, scheme="native spectral mass readout",
        source="unit scalar coefficient in the native isovector source",
        mass_source="generated up and down spectral mass readouts",
        electromagnetic_convention="native proton-minus-neutron electromagnetic readout",
        electromagnetic_source="(1-1/(2*pi))*alpha_em(0)*Lambda_QCD")
    neutron = proton["proton_mass_GeV"]+split["neutron_proton_split"]
    if neutron <= 0:
        raise ValueError("positive native neutron mass required")
    return {"scope": "common native constituent and isovector mass readouts",
            "proton": proton, "isovector": split, "neutron_mass_GeV": neutron,
            "alpha_em_0": alpha_em,
            "scale_role": "generation reference for the spectral mass source",
            "physical_matching_inputs": "renormalized quark masses, sourced scalar density and QCD/EM separation"}


def three_quark_source_certificate():
    """Generated colour singlet and its first adjoint source channels.

    The three-quark colour tensor and the fundamental matter vertex fix
    these finite factors independently of a radial or binding Hamiltonian.
    The adjoint-source vectors obey the global colour constraint in the
    product representation. Spatial Gauss constraints and the baryon pole
    use the common dynamical kernel and are not evaluated by colour algebra.
    """
    from itertools import permutations
    from cg_core.content_response import CHARGED_GENERATION
    from cg_core.modal_algebra import spinor_basis, spinor_multiplication

    content = {name: (rep, charge) for name, rep, charge, _, _ in CHARGED_GENERATION}
    dimension = content['Q_L'][0][0]
    if dimension != 3:
        raise ValueError("the retained three-quark colour carrier requires SU(3)")
    eye = np.eye(dimension, dtype=complex)
    generators = []
    for i in range(dimension):
        for j in range(i+1, dimension):
            unit = np.outer(eye[i], eye[j])
            generators.extend(((unit+unit.T)/2, (unit-unit.T)/(2j)))
    for k in range(1, dimension):
        diagonal = np.zeros(dimension)
        diagonal[:k], diagonal[k] = 1., -k
        generators.append(np.diag(diagonal)/math.sqrt(2*k*(k+1)))
    generators = np.asarray(generators)
    count, tensor_dimension = len(generators), dimension**3
    singlet = np.zeros(tensor_dimension, complex)
    for entries in permutations(range(dimension)):
        inversions = sum(entries[i] > entries[j] for i in range(3) for j in range(i+1, 3))
        singlet[np.ravel_multi_index(entries, (dimension,)*3)] = (-1)**inversions/math.sqrt(6)
    legs = np.array([[np.kron(np.kron(
        generator if leg == 0 else eye, generator if leg == 1 else eye),
        generator if leg == 2 else eye) for generator in generators]
        for leg in range(3)])
    total = np.sum(legs, axis=0)
    colour_casimir = sum(matrix@matrix for matrix in total)
    casimir_levels = np.linalg.eigvalsh(colour_casimir)
    vertices = np.array([np.column_stack([matrix@singlet for matrix in leg]) for leg in legs])
    gram = np.array([[np.vdot(first, second).real for second in vertices] for first in vertices])
    constants = np.empty((count, count, count))
    for a in range(count):
        for b in range(count):
            commutator = generators[a]@generators[b]-generators[b]@generators[a]
            constants[a, b] = [(-2j*np.trace(commutator@generator)).real
                               for generator in generators]
    adjoint = -1j*constants
    constraint_residual = max(float(np.linalg.norm(
        total[a]@vertex+vertex@adjoint[a].T))
        for a in range(count) for vertex in vertices)
    expected_gram = 2*np.eye(3)-2*np.ones((3, 3))/3

    # The actual scalar-coefficient matter vertex e^1_00 Psi_(j=0)
    # retains both signed spinor product branches in j=1.
    incoming, outgoing = spinor_basis(0), spinor_basis(1)
    spatial = spinor_multiplication({(1, 0, 0): 1.}, incoming, outgoing)
    positive_rows = [i for i, label in enumerate(outgoing) if label[0] == 1 and label[2] == 1.5]
    negative_rows = [i for i, label in enumerate(outgoing) if label[0] == 1 and label[2] == .5]
    retained_rows = [i for i, label in enumerate(outgoing) if label[0] == 0]
    positive_weight = np.sum(abs(spatial[positive_rows])**2, axis=0)
    negative_weight = np.sum(abs(spatial[negative_rows])**2, axis=0)
    norm_residual = float(np.linalg.norm(spatial.conj().T@spatial-np.eye(len(incoming))))
    up, down = content['u_R'][1], content['d_R'][1]
    charges = {}
    for name, entries in (('uud', (up, up, down)), ('udd', (up, down, down))):
        charges[name] = {
            'total_charge': str(sum(entries)),
            'sum_squared_charges': str(sum(q*q for q in entries)),
            'sum_pair_charge_products': str(sum(entries[i]*entries[j]
                for i in range(3) for j in range(i+1, 3)))}
    residuals = {
        'generator_trace_normalization': float(np.linalg.norm(
            np.einsum('aij,bji->ab', generators, generators)-np.eye(count)/2)),
        'singlet_global_colour_constraint': max(float(np.linalg.norm(matrix@singlet)) for matrix in total),
        'adjoint_source_global_colour_constraint': constraint_residual,
        'source_gram': float(np.linalg.norm(gram-expected_gram)),
        'summed_leg_source': float(np.linalg.norm(np.sum(vertices, axis=0))),
        'spatial_source_isometry': norm_residual,
        'spatial_retained_projection': float(np.linalg.norm(spatial[retained_rows]))}
    if max(residuals.values()) > 2e-12:
        raise ArithmeticError("three-quark colour or generated matter-source identity failed")
    return {
        'scope': 'colour factors and actual internal matter-vertex support for the retained three-quark carrier',
        'colour_tensor_dimension': tensor_dimension,
        'colour_singlet_multiplicity': int(np.count_nonzero(abs(casimir_levels) < 1e-12)),
        'colour_casimir_multiplicities': {
            str(level): int(np.count_nonzero(abs(casimir_levels-level) < 1e-12)) for level in (0, 3, 6)},
        'adjoint_source_gram': gram.tolist(),
        'adjoint_source_gram_exact': [['4/3', '-2/3', '-2/3'],
                                      ['-2/3', '4/3', '-2/3'],
                                      ['-2/3', '-2/3', '4/3']],
        'independent_adjoint_source_channels': int(np.linalg.matrix_rank(gram, tol=1e-12)),
        'pair_colour_factor': '-2/3',
        'electric_charge_moments': charges,
        'spatial_source': {'coefficient_mode': [1, 0, 0],
            'incoming_spinor_shell': 0, 'outgoing_spinor_shell': 1,
            'positive_dirac_weight_per_column': positive_weight.tolist(),
            'negative_dirac_weight_per_column': negative_weight.tolist(),
            'norm_outside_incoming_shell_per_column': np.sum(abs(spatial)**2, axis=0).tolist()},
        'evaluation_work': {'colour_tensor_dimension': tensor_dimension,
            'colour_generators': count, 'casimir_diagonalizations': 1,
            'source_vectors': len(vertices),
            'adjoint_constraint_matrix_actions': count*len(vertices),
            'spinor_vertex_shape': list(spatial.shape),
            'spectral_tail_evaluations': 0,
            'binding_kernel_solves': 0},
        'residuals': residuals,
        'mass_operator_computed': False,
        'physical_scalar_charge_computed': False,
        'passed': True}


def killing_candidate_certificate() -> dict:
    """Finite matrix decomposition and candidate levels, without J^PC claims."""
    data = killing_two_body()
    sectors = []
    for (jl, jr), projector in data["projectors"].items():
        dimension = round(float(np.trace(projector).real))
        level = float(np.trace(projector @ data["candidate_operator"]).real) / dimension
        level_integer = round(level)
        defect = np.linalg.norm((data["candidate_operator"] - level_integer * np.eye(21)) @ projector)
        if defect > 1e-10:
            raise ArithmeticError("candidate representation is not an eigenspace")
        sectors.append({"spin4": [jl, jr], "dimension": dimension,
                        "copies": dimension // ((2 * jl + 1) * (2 * jr + 1)),
                        "candidate_lambda_L2": level_integer,
                        "operator_residual": float(defect)})
    return {"carrier_dimension": 6, "symmetric_dimension": 21, "sectors": sectors,
            "decomposition_residual": float(np.linalg.norm(sum(data["projectors"].values()) - np.eye(21))),
            "source_projection_available": True,
            "external_JPC_identification": "requires an observable and dynamical matching",
            "candidate_rule": "8 I + 2(C_left + C_right)"}


def glueball_two_gluon_spectrum() -> dict:
    """Actual Sym2(K) candidate levels, keyed by internal Spin(4) representation.

    The two singlets both have candidate level 8; their source weights can
    differ. There is no (1,0)+(0,1) sector in this bosonic colour-singlet square.
    """
    certificate = killing_candidate_certificate()
    return {f"({row['spin4'][0]},{row['spin4'][1]})": float(row["candidate_lambda_L2"])
            for row in certificate["sectors"]}


def compute() -> dict:
    """Publish specified QCD results and the checked finite candidate carrier."""
    tau = float(get("tau"))
    # c = kL is the V5 TT endpoint; the Gaussian IR edge sqrt(2*pi) is not used.
    c = float(get("kL"))
    dE = float(get("mass_gap_dE"))
    mgen = float(get("mass_gap_m_gen"))
    mgl = float(get("m_glueball"))
    Lam = float(get("qcd_Lambda_QCD"))
    certificate = killing_candidate_certificate()
    candidates = {f"({row['spin4'][0]},{row['spin4'][1]})": float(row["candidate_lambda_L2"])
                  for row in certificate["sectors"]}
    base, tensor = candidates["(0,0)"], candidates["(1,1)"]
    lam_l2 = 8.0 / (c * c)
    # External JPC labels are assigned by the specified mass catalogue.
    ratios = {"0++": 1.0, "2++": math.sqrt(tensor / base),
              "0++*": math.sqrt((tensor + 2.0) / base),
              "0-+": math.sqrt((tensor + 1.0) / base)}
    descriptions = {
        "0++": "assigned scalar readout, internal singlet candidate lambda=8",
        "2++": "assigned tensor readout, internal (1,1) candidate lambda=16",
        "0++*": "additional excitation assignment lambda=18",
        "0-+": "additional excitation assignment lambda=17",
    }
    tower = {label: {"mass_GeV": mgl * ratio, "ratio": ratio, "mode": descriptions[label]}
             for label, ratio in ratios.items()}
    pset("qcd_Lambda_QCD", Lam, provenance="DERIVED", role="internal",
         note=f"Lambda_QCD = {Lam:.8g} GeV from the specified two-loop production "
              "running and nf=5 extraction with its declared finite factor.")
    pset("qcd_gap_lambda_l2", lam_l2, provenance="DERIVED", role="internal",
         note=f"lambda_l2 = 8/c^2 = {lam_l2:.8g}, the first nonconstant scalar "
              "level in the stated radius units, separate from the constant-inclusive native scalar gap.")
    pset("qcd_killing_candidates", certificate, provenance="DERIVED", role="internal",
         note="Actual normalized symmetric-square matrices, source projections and Casimir sectors "
              "of the six-dimensional Killing carrier; external JPC and bound-state matching are separate.")
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    T_d = (4.0 / 3.0) * Lam * 1000.0 * (1.0 - tau * kappa)
    sigma = (14.0 / math.pi) * Lam * Lam
    proton = constituent_proton_readout(Lam, tau)
    m_p = proton["proton_mass_GeV"]
    pset("qcd_deconfinement_T", T_d, provenance="DERIVED", role="internal",
         note="Constitutive deconfinement-scale readout T_d=(4/3) Lambda_QCD "
              "(1-tau*kappa), in MeV.")
    pset("qcd_string_tension", sigma, provenance="DERIVED", role="internal",
         note="Specified sigma=(14/pi) Lambda_QCD^2, in GeV^2; 14 is the "
              "effective three-branch tensor-catalogue coefficient. This constitutive "
              "tension readout uses the catalogue normalisation stated in Guo (2026g).")
    pset("m_p", m_p, provenance="DERIVED", role="internal",
         note="Native constituent map m_p=(279/64) Lambda_QCD (1+5 tau*kappa/3), in GeV; "
              "the same proton anchor enters the common nucleon/isovector source record.",
         dependencies=("qcd_Lambda_QCD", "tau"))
    pset("qcd_glueball_tower", tower, provenance="DERIVED", role="internal",
         note="Specified mass catalogue with coefficients 8,16,18,17 and common m_glueball scale. "
              "The actual internal candidates support levels 8 and 16; 18 and 17 retain "
              "their additional excitation assignments. Source and bound-state matching are separate.")
    valid = certificate["decomposition_residual"] < 1e-10 and all(
        row["operator_residual"] < 1e-10 for row in certificate["sectors"])
    pset("qcd_sector_status",
         {"candidate_carrier_verified": valid,
          "specified_catalogue_evaluated": all(row["mass_GeV"] > 0 for row in tower.values()),
          "two_body_kernel_solved": False, "external_JPC_matched": False,
          "condensate_and_generator_readouts": "parallel quantities"},
         provenance="DERIVED", role="informational",
         note="Status follows actual finite-matrix residuals and the specified positive mass readouts.")
    return {"Lambda_QCD": Lam, "m_glueball": mgl, "lambda_l2": lam_l2,
            "dE": dE, "m_gen": mgen, "tower": tower, "string_tension": sigma,
            "m_p": m_p, "internal_candidates": certificate}


if __name__ == "__main__":
    result = compute()
    print(f"Lambda_QCD = {result['Lambda_QCD']:.8g} GeV")
    print("Sym2(K): " + ", ".join(f"{r['spin4']} dimension {r['dimension']} "
          f"level {r['candidate_lambda_L2']}" for r in result["internal_candidates"]["sectors"]))
    print("Specified catalogue: " + ", ".join(f"{k} {v['mass_GeV']:.8g} GeV"
                                               for k, v in result["tower"].items()))
