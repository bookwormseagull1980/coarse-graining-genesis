"""Full-carrier content responses and algebraic contorsion variation.

The neutral right line is retained throughout.  A gauge response can restrict
to the support of Y without choosing fifteen coordinates: that support is a
spectral projection of the generated charge operator.  A spin-connection
vertex is a different operator and must be evaluated separately.

The torsion calculation uses the index convention of ec_structure and
squash_level_transfer: T[a,b,c] is antisymmetric in b,c and I2=T[b,a,c]T[a,b,c].
It classifies derivative-free, SO(3)-invariant quadratic forms, then varies
the coefficients actually used by the production chain.
"""
from fractions import Fraction as Q

import numpy as np

from cg_core.content_response import FULL_GENERATION


def full_carrier_response():
    """Compute all content traces on the complete generated carrier exactly.

    P=1-product_(q!=0)(1-Y^2/q^2) is the unique support projection of Y.
    Repeated charge squares are removed before forming this polynomial.
    The conditional gauge response is Tr(P chi)/(Tr(P) Tr(Y^2)).
    This is a response on the full carrier, not an EC field equation.
    """
    entries = tuple((name, y, sign) for name, _, y, n, sign in FULL_GENERATION
                    for _ in range(n))
    squares = sorted({y*y for _, y, _ in entries if y})
    projectors = []
    for _, y, _ in entries:
        complement = Q(1)
        for square in squares:
            complement *= 1-y*y/square
        projectors.append(1-complement)
    n = len(entries)
    rank = sum(projectors)
    chi = sum(sign for _, _, sign in entries)
    projected_chi = sum(p*sign for p, (_, _, sign) in zip(projectors, entries))
    y2 = sum(y*y for _, y, _ in entries)
    return {
        "dimension": n, "charge_square_spectrum": tuple(squares),
        "gauge_support_diagonal": tuple(projectors), "gauge_support_rank": rank,
        "neutral_labels": tuple(name for p, (name, _, _) in zip(projectors, entries) if not p),
        "center_trace": chi, "center_mean": Q(chi, n),
        "hypercharge_trace": sum(y for _, y, _ in entries),
        "hypercharge_second_moment": y2,
        "full_center_hessian": 1-Q(chi, n)**2,
        "full_hypercharge_hessian": y2/n,
        "projected_center_trace": projected_chi,
        "gauge_conditioned_tau": projected_chi/(rank*y2),
        "unconditioned_center_response": Q(chi, n)/y2,
        "projected_current_full_state_response": projected_chi/(n*y2),
        "neutral_hypercharge_vertex": Q(0),
    }


def full_source_matrices():
    """The existing charged generators extended to the generated neutral line.

    This order is FULL_GENERATION, not the different finite_connector basis.
    Gauge matrices vanish on nu_R.  The center has eigenvalue -1 there.
    """
    from cg_core.content_response import charged_source_matrices
    charged = charged_source_matrices()
    full = np.zeros((charged.shape[0], 16, 16), complex)
    full[:, :15, :15] = charged
    full[0, 15, 15] = -1
    return full


def publish_content_modulus():
    """Publish the complete-carrier gauge response with its operator identity."""
    from cg_core.params import set as pset
    result = full_carrier_response()
    tau = float(result["gauge_conditioned_tau"])
    pset("tau", tau, provenance="DERIVED", dependencies=(),
         evidence_kind="exact rational full-carrier spectral-projection response",
         note="Tr(P chi)/(Tr(P) Tr(Y^2))=1/50 on the full 16D carrier; "
              "P=support(Y) has rank 15, Tr(P chi)=1, Tr(Y^2)=10/3; "
              "the complete center trace is zero. EC stationarity is a "
              "separate action derivative, not this trace identity")
    return tau


def minimal_spin_connection_vertex():
    """Evaluate a nonzero minimally coupled Hermitian Dirac torsion vertex.

    Euclidean gamma matrices obey {gamma_a,gamma_b}=2 delta_ab.  Variation
    of i/2*(bar(psi) gamma D psi-D bar(psi) gamma psi) with respect to
    K[0,1,2] gives i/8*{gamma_2,gamma_0 gamma_1}.  On matter content this
    vertex tensors with I_16, not Y.  Both antisymmetric K entries must be
    included when assembling an independent connection variation.
    The three-form Clifford product is dual to the axial current in 4D.
    No expectation value of that current is inferred from a dimension count.
    """
    identity = np.eye(2, dtype=complex)
    pauli = (np.array([[0, 1], [1, 0]], complex),
             np.array([[0, -1j], [1j, 0]], complex),
             np.diag([1., -1.]).astype(complex))
    zero = np.zeros((2, 2), complex)
    gammas = tuple(np.block([[zero, -1j*s], [1j*s, zero]]) for s in pauli)
    gammas += (np.block([[zero, identity], [identity, zero]]),)
    vertex = 1j/8*(gammas[2] @ gammas[0] @ gammas[1]
                  + gammas[0] @ gammas[1] @ gammas[2])
    return {"gammas": gammas, "spin_vertex": vertex,
            "content_vertex": np.eye(len(full_carrier_response()["gauge_support_diagonal"])),
            "neutral_vertex": vertex.copy()}


def neutral_connector_schur():
    """Retain the neutral feedback of the existing unit Higgs connector.

    H=(0,1) fixes a unit representative for this algebraic comparison; it
    is not a new dimensional VEV.  This function uses finite_connector's
    basis, where nu_R has index 14.  At z=i the full and eliminated blocks
    are invertible.  The Schur correction is evaluated, not set to zero.
    """
    from cg_core.finite_connector import elementary_connector, split_carrier
    data = elementary_connector((0., 1.))
    split = split_carrier(data["operator"], data["neutral_basis"])
    z = 1j
    diagonal = split["neutral_operator"]-z*np.eye(1)
    coupling = split["coupling"]
    feedback = coupling @ np.linalg.solve(diagonal, coupling.conj().T)
    schur = split["charged_operator"]-z*np.eye(15)-feedback
    full_resolvent = np.linalg.inv(data["operator"]-z*np.eye(16))
    charged_resolvent = split["charged_basis"].conj().T @ full_resolvent @ split["charged_basis"]
    return {"neutral_coupling_norm": split["descent_defect_norm"],
            "schur_feedback": feedback, "schur_feedback_norm": float(np.linalg.norm(feedback)),
            "resolvent_difference": charged_resolvent-np.linalg.inv(schur)}


def _epsilon(a, b, c):
    if len({a, b, c}) < 3:
        return 0
    return 1 if (a, b, c) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)) else -1


def minimal_internal_torsion_vertices():
    """Differentiate the internal Hermitian spin action in all nine directions.

    T_abc=epsilon_dbc B_ad and
    K_abc=(T_abc+T_bca-T_cab)/2 give K_abc-K_acb=T_abc.
    Direct Pauli multiplication evaluates i/8 K_bc,a {gamma_a,gamma_b gamma_c}.
    The result is -(tr B)/4 I_2: the minimal source has no antisymmetric
    or symmetric traceless dual-torsion component. Both ordered connection
    entries are summed, so this includes their antisymmetry factor.
    """
    gamma = (np.array([[0, 1], [1, 0]], complex),
             np.array([[0, -1j], [1j, 0]], complex),
             np.diag([1., -1.]).astype(complex))
    vertices = np.zeros((3, 3, 2, 2), complex)
    for i in range(3):
        for j in range(3):
            b = np.zeros((3, 3))
            b[i, j] = 1
            t = np.einsum('ad,dbc->abc', b, np.array(
                [[[_epsilon(d, u, v) for v in range(3)] for u in range(3)] for d in range(3)]))
            for a in range(3):
                for u in range(3):
                    for v in range(3):
                        k = (t[u, v, a]+t[v, a, u]-t[a, u, v])/2
                        vertices[i, j] += 1j/8*k*(gamma[a]@gamma[u]@gamma[v]
                                                  + gamma[u]@gamma[v]@gamma[a])
    return vertices


def solve_algebraic_torsion(current, coefficients):
    """Stationary point of sum c_i ||B_i||^2+<J,B> in all nine directions.

    This is algebraic elimination, not a claim of a minimum in the trace
    direction.  Nonzero coefficients ensure a unique stationary point.
    The independent tensor contractions in torsion_invariants provide
    another way to evaluate its action.
    """
    j = np.asarray(current, float)
    if j.shape != (3, 3) or not np.all(np.isfinite(j)):
        raise ValueError("a finite real 3 by 3 matter-current matrix is required")
    if len(coefficients) != 3:
        raise ValueError("three quadratic torsion coefficients required")
    weights = np.asarray(quadratic_torsion_coefficients(*coefficients), float)
    if not np.all(np.isfinite(weights)) or np.any(weights == 0):
        raise ValueError("each irreducible algebraic Hessian must be invertible")
    j0 = np.eye(3)*np.trace(j)/3
    ja = (j-j.T)/2
    js = (j+j.T)/2-j0
    source_parts = (j0, ja, js)
    parts = tuple(-part/(2*weight) for part, weight in zip(source_parts, weights))
    stationary = sum(parts)
    gradient = sum(2*weight*part for part, weight in zip(parts, weights))+j
    return {"stationary_dual_torsion": stationary,
            "trace_free_stationary_part": parts[1]+parts[2],
            "gradient_residual": gradient, "irreducible_hessians": 2*weights}


def production_torsion_sector_contract(tau, radius):
    """Connect the algebraic sector elimination to the retained V5 spectrum.

    The unit-M_G action ratios are those used by ec_action.  The minimal
    internal spin vertex is purely trace.  The positive transverse Hessians
    therefore eliminate the two trace-free sectors uniquely.  This fixes
    their classical response, while the amplitude of the trace current
    must still be obtained from the same generated matter action.
    """
    from cg_core.spectrum_loop import m2_gauge, m2_fermion
    from cg_frg.ewsb.squash_level_transfer import ec_action, killing_normalisation
    if not np.isfinite(tau) or not -.5 < tau < .25 or not np.isfinite(radius) or radius <= 0:
        raise ValueError("-.5 < tau < .25 and positive finite radius required by the squash metric")
    action = ec_action(1.)
    coefficients = tuple(action[key] for key in ("a", "b", "c"))
    hessians = 2*np.array(quadratic_torsion_coefficients(*coefficients))
    vertices = minimal_internal_torsion_vertices()
    trace = sum(vertices[i, i] for i in range(3))
    deviator = vertices.copy()
    for i in range(3):
        deviator[i, i] -= trace/3
    # The source amplitude is deliberately not inferred from its channel.
    # These derivatives transfer any computed amplitude correction downstream.
    return {
        "carrier_dimension": 16,
        "spin_source_trace_free_vertex_norm": float(np.linalg.norm(deviator)),
        "trace_free_hessian_eigenvalues": hessians[1:].tolist(),
        "trace_hessian_eigenvalue": float(hessians[0]),
        "trace_free_hessian_multiplicities": [3, 5],
        "classical_trace_free_elimination": "unique zero for the minimal algebraic spin source",
        "stationary_equation_scope": "production algebraic torsion; no extra torsion kinetic term",
        "tau_observation": "full-carrier gauge-conditioned response",
        "tau_matter_current_matching": "requires the trace-current expectation of the common matter action",
        "matter_action_derivative_required": 36*action["a"]*tau/radius**2,
        "gauge_torsion_mass_squared": m2_gauge(0., radius, tau),
        "fermion_torsion_mass_squared": m2_fermion(radius, tau),
        "squash_amplitude": 2*tau,
        "squash_kappa": killing_normalisation(tau)["kappa"],
        "lambda_ec": 14+8*tau+2*tau*tau,
        "d_lambda_ec_d_tau": 8+4*tau,
        "d_gauge_mass_squared_d_tau": tau/(3*radius*radius),
        "d_fermion_mass_squared_d_tau": 3*tau/(4*radius*radius),
        "d_inverse_alpha_torsion_term_d_tau": -np.pi*tau,
        "d_log_kappa_d_tau": 1/(1+2*tau)+5/(1-4*tau),
        "background_unchanged_at_fixed_trace_coefficient_and_current": True,
        "trace_free_fluctuation_hessian_depends_on_action_coefficients": True,
    }


def torsion_invariants(dual):
    """Exact I1,I2,I3 for T[a,b,c]=epsilon[d,b,c]*dual[a,d]."""
    if len(dual) != 3 or any(len(row) != 3 for row in dual):
        raise ValueError("a real 3 by 3 dual torsion matrix is required")
    t = [[[sum(_epsilon(d, b, c)*dual[a][d] for d in range(3))
           for c in range(3)] for b in range(3)] for a in range(3)]
    i1 = sum(t[a][b][c]**2 for a in range(3) for b in range(3) for c in range(3))
    i2 = sum(t[b][a][c]*t[a][b][c] for a in range(3) for b in range(3) for c in range(3))
    i3 = sum(sum(t[b][b][a] for b in range(3))**2 for a in range(3))
    return i1, i2, i3


def quadratic_torsion_coefficients(a, b, c):
    """Weights of trace, antisymmetric and symmetric traceless dual torsion.

    These three inequivalent SO(3) irreducibles have dimensions 1,3,5.
    Schur's lemma leaves one quadratic coefficient on each.  Rotational
    invariance singles out the isotropic ansatz; it does not fix all three
    coefficients of the action.
    """
    return (2*a-2*b, 2*a+b+2*c, 2*a+b)


def production_torsion_variation():
    """Exact homogeneous variation in units M_G=L=1.

    The production coefficients are a=1/4,b=4a,c=-7a/3.  Restricting to
    T=tau*epsilon gives S_torsion=-9*tau^2/2.  A retained matter action
    adds its actual first derivative J; stationarity is -9*tau+J=0.
    The calculation reports the current required by the claimed value;
    it does not insert that current as an additional source.
    """
    a = Q(1, 4)
    b, c = 4*a, -7*a/3
    i1, i2, i3 = torsion_invariants(((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    coefficient = a*i1+b*i2+c*i3
    tau = full_carrier_response()["gauge_conditioned_tau"]
    return {
        "action_coefficients": (a, b, c),
        "irreducible_weights": quadratic_torsion_coefficients(a, b, c),
        "isotropic_quadratic_coefficient": coefficient,
        "isotropic_hessian": 2*coefficient,
        "torsion_only_stationary_point": Q(0),
        "gauge_conditioned_tau": tau,
        "matter_action_derivative_required_at_tau": -2*coefficient*tau,
        "same_order_quadratic_invariants": 3,
        "rotation_invariant_torsion_directions": 1,
    }
