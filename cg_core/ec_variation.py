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


def torsion_capacity_balance():
    """The finite content equation, with no connection or state argument.

    The two counts are evaluated on support(Y), retaining the neutral
    coordinate in the complete carrier.  Positive capacity makes
    capacity*tau=index a uniquely solvable rational equation.  This is
    the SourceTorsionContent identity; it is not an equation obtained by
    varying an independently supplied connection.
    """
    content = full_carrier_response()
    rank, index = content["gauge_support_rank"], content["projected_center_trace"]
    capacity = rank*content["hypercharge_second_moment"]
    if capacity <= 0:
        raise ArithmeticError("the generated charged capacity must be positive")
    return {
        "full_dimension": content["dimension"],
        "left_count": (rank+index)/2,
        "charged_right_count": (rank-index)/2,
        "charged_weyl_count": rank,
        "hypercharge_capacity": content["hypercharge_second_moment"],
        "charged_index": index, "balance_capacity": capacity,
        "tau_content": index/capacity,
        "balance_residual": capacity*content["gauge_conditioned_tau"]-index,
        "capacity_positive": capacity > 0,
        "equation": "balance_capacity * tau_content = charged_index",
        "scope": "finite generated content with its fixed charge normalization",
    }


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
    This is the retained K table. Cartan's T=de+omega wedge e uses
    C=-K; connection_action computes the opposite signed vertex from C.
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


def minimal_torsion_spectral_terms(n, tau, radius):
    """Differentiate the minimally coupled internal Dirac square, shell by shell.

    This uses the signed native RP3 Dirac spectrum and the Clifford vertex
    above, with T_abc=(tau/radius)*epsilon_abc.  The vertex acts as I_16 on
    matter content.  In particular a neutral hypercharge does not remove it.

    The production mass insertion is also reported for comparison.  It is
    not substituted for the Dirac square: squaring D0-3*tau/(4*radius)
    retains both the term linear in D0 and the scalar quadratic term.
    """
    from cg_core.rp3_spectrum import spinor_dirac_eigenvalue, spinor_multiplicity
    from cg_core.spectrum_loop import m2_fermion
    if (not isinstance(n, int) or isinstance(n, bool) or n < 0
            or not np.isfinite(tau) or not np.isfinite(radius) or radius <= 0):
        raise ValueError("a nonnegative integer shell, finite torsion and positive radius required")
    native = spinor_dirac_eigenvalue(n, radius)
    shift = -3*tau/(4*radius)
    shifted = native+shift
    production = native*native+m2_fermion(radius, tau)
    return {
        "shell": n, "spatial_multiplicity": spinor_multiplicity(n),
        "content_dimension": full_carrier_response()["dimension"],
        "native_dirac": native, "torsion_dirac_shift": shift,
        "coupled_dirac": shifted, "coupled_dirac_square": shifted*shifted,
        "linear_square_term": 2*native*shift,
        "quadratic_square_term": shift*shift,
        "d_dirac_square_d_tau": -3*shifted/(2*radius),
        "d2_dirac_square_d_tau2": 9/(8*radius*radius),
        "production_squared_response": production,
        "production_minus_coupled_square": production-shifted*shifted,
        "neutral_dirac_shift": shift,
    }


def minimal_coupled_action_variation(dual, psi, psi_bar, native_dirac, coefficients):
    """The complete first variation of the finite minimal algebraic action.

    S=sum c_i*||B_i||^2 + psi_bar*(D0-tr(B)/4)*psi.  The two matter
    arguments are independent column and row variables, as in a Dirac
    action; no positivity assumption on their bilinear is used.  D0 may
    be a finite native spectral block tensored with the full matter fibre.
    B has units of inverse length.  This function evaluates a field
    configuration; it does not introduce another source or fix its state.
    """
    b = np.asarray(dual, float)
    ket = np.asarray(psi, complex)
    bra = np.asarray(psi_bar, complex)
    d0 = np.asarray(native_dirac, complex)
    coefficients = np.asarray(coefficients, float)
    if b.shape != (3, 3) or ket.ndim != 1 or ket.size == 0 or bra.shape != ket.shape:
        raise ValueError("a real 3 by 3 torsion matrix and equally sized matter row and column required")
    if d0.shape != (ket.size, ket.size) or len(coefficients) != 3:
        raise ValueError("a compatible native Dirac matrix and three action coefficients required")
    if not all(np.all(np.isfinite(x)) for x in (b, ket, bra, d0, coefficients)):
        raise ValueError("finite field and action data required")
    weights = quadratic_torsion_coefficients(*coefficients)
    b0 = np.eye(3)*np.trace(b)/3
    ba = (b-b.T)/2
    bs = (b+b.T)/2-b0
    parts = (b0, ba, bs)
    torsion_action = sum(w*np.sum(part*part) for w, part in zip(weights, parts))
    coupled = d0-np.trace(b)/4*np.eye(ket.size)
    bilinear = bra @ ket
    current = -bilinear/4*np.eye(3)
    gradient = sum(2*w*part for w, part in zip(weights, parts))+current
    return {
        "action": torsion_action+bra @ coupled @ ket,
        "torsion_action": torsion_action, "matter_bilinear": bilinear,
        "coupled_dirac": coupled, "torsion_gradient": gradient,
        "matter_row_equation": coupled @ ket,
        "matter_column_equation": bra @ coupled,
        "matter_current": current,
    }


def minimal_classical_stationarity():
    """Exact all-shell result at fixed round RP3 geometry for the minimal action.

    For the production coefficients the two transverse Hessians are
    invertible.  The computed spin vertex has only a trace component, so
    their equations imply B=(tau/L)I.  In the downstream metric domain
    -1/2<tau<1/4 every native Dirac eigenvalue has modulus >=3/(2L),
    while the isotropic shift has modulus <3/(8L).  Thus D_tau is
    invertible on the entire tower, not just a finite cutoff.  The two
    classical matter equations then set both matter variables to zero;
    the trace equation sets tau to zero.

    This is a classical result for precisely the action evaluated by
    minimal_coupled_action_variation.  A fermionic effective determinant,
    condensate or other interacting sector has its own action derivative
    and is not replaced by the gauge-content trace.
    """
    production = production_torsion_variation()
    tau_g = production["gauge_conditioned_tau"]
    a = production["action_coefficients"][0]
    trace_residual = production["isotropic_hessian"]*tau_g
    native_gap = Q(3, 2)
    dirac_shift_coefficient = Q(3, 4)
    uniform_gap = native_gap-dirac_shift_coefficient*Q(1, 2)
    return {
        "scope": "minimal classical algebraic Dirac--torsion action on the full 16D fibre at fixed round RP3 geometry",
        "metric_tau_interval": (Q(-1, 2), Q(1, 4)),
        "native_dirac_gap_times_radius": native_gap,
        "uniform_coupled_gap_times_radius_lower_bound": uniform_gap,
        "stationary_tau": Q(0),
        "stationary_matter_field": "zero",
        "gauge_conditioned_tau": tau_g,
        "trace_action_derivative_at_gauge_tau": trace_residual,
        "required_matter_bilinear_times_radius_at_gauge_tau": -48*a*tau_g,
        "gauge_tau_is_a_minimal_classical_stationary_point": trace_residual == 0,
        "dirac_square_quadratic_coefficient": Q(9, 16),
        "production_mass_quadratic_coefficient": Q(3, 8),
        "sign_averaged_quadratic_difference": Q(3, 16),
    }


def eliminate_minimal_trace_torsion(bilinear, *, radius, coefficients):
    """Exact stationary elimination of the minimally coupled trace sector.

    Write c0=2(a-b), B=(tau/L)I and rho=bar(psi)psi.  The part of the
    action depending on tau is 3*c0*tau^2/L^2-3*tau*rho/(4*L).
    Completing its square gives tau_*=L*rho/(8*c0) and the induced
    interaction -3*rho^2/(64*c0).  This is an algebraic stationary
    elimination, including when c0<0; it is not a Gaussian integral over
    a negative Euclidean quadratic form.  The fermion bilinear remains
    an observable of the same matter action, never an imposed drive.

    Rational inputs remain exact.  The normalization of rho includes
    the complete matter fibre, including its neutral right coordinate.
    Only the trace coefficient is used: transverse fluctuations must be
    retained separately when computing a full fluctuation determinant.
    """
    def rational(value):
        return Q(str(value)) if isinstance(value, (float, np.floating)) else Q(value)

    if len(coefficients) != 3:
        raise ValueError("three quadratic torsion coefficients required")
    rho, length = rational(bilinear), rational(radius)
    a, b, c = map(rational, coefficients)
    if length <= 0:
        raise ValueError("positive radius required")
    c0 = quadratic_torsion_coefficients(a, b, c)[0]
    if not c0:
        raise ValueError("the trace auxiliary Hessian must be invertible")
    tau = length*rho/(8*c0)
    induced = -Q(3, 64)/c0
    return {
        "trace_coefficient": c0,
        "trace_hessian": 6*c0/length**2,
        "stationary_tau": tau,
        "stationary_dual_trace": tau/length,
        "induced_four_fermion_coefficient": induced,
        "induced_interaction": induced*rho*rho,
        "completed_square_coefficient": 3*c0/length**2,
        "trace_equation_residual": 6*c0*tau/length**2-3*rho/(4*length),
        "content_dimension": full_carrier_response()["dimension"],
    }


def eliminate_auxiliary_hessian(hessian, auxiliary_indices):
    """Hessian of an action after stationary auxiliary-field elimination.

    The physical Hessian is Hxx-Hxa*Haa^{-1}*Hax.  Invertibility of Haa
    is required, while positivity of Haa is not.  No mixed block is
    dropped.  The inertia of the reduced physical form is returned so
    a caller can check stability on its actual physical/gauge quotient.
    """
    matrix = np.asarray(hessian, float)
    indices = tuple(auxiliary_indices)
    if (matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]
            or not np.all(np.isfinite(matrix))
            or not np.allclose(matrix, matrix.T, rtol=1e-12, atol=1e-14)):
        raise ValueError("a finite real symmetric Hessian required")
    if (not indices or len(set(indices)) != len(indices)
            or any(not isinstance(i, (int, np.integer)) or isinstance(i, bool)
                   or i < 0 or i >= len(matrix) for i in indices)):
        raise ValueError("distinct valid auxiliary indices required")
    physical = tuple(i for i in range(len(matrix)) if i not in indices)
    if not physical:
        raise ValueError("at least one retained physical coordinate required")
    haa = matrix[np.ix_(indices, indices)]
    hax = matrix[np.ix_(indices, physical)]
    feedback = hax.T @ np.linalg.solve(haa, hax)
    reduced = matrix[np.ix_(physical, physical)]-feedback
    return {"physical_indices": physical, "auxiliary_indices": indices,
            "auxiliary_response": -np.linalg.solve(haa, hax),
            "schur_feedback": feedback, "reduced_hessian": reduced,
            "reduced_eigenvalues": np.linalg.eigvalsh(reduced)}


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
    from cg_core.connection_action import production_curvature_matching
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
    matching = production_curvature_matching()
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
        "curvature_action_matching": {
            "same_action_up_to_overall_normalization": matching["same_action_up_to_overall_normalization"],
            "trace_matched_curvature_normalization_MG3": float(matching["trace_matched_curvature_normalization"]),
            "extra_irreducible_weights_MG3": [float(w) for w in matching["extra_irreducible_weights"]],
            "cartan_tau_from_existing_spin_tau": float(matching["cartan_dual_from_existing_spin_dual"]),
        },
        "tau_observation": "full-carrier gauge-conditioned response",
        "tau_matter_current_matching": "minimal classical joint equations give tau=0; gauge response is a different observable",
        "minimal_classical_stationary_tau": 0.,
        "minimal_classical_trace_residual_at_input_tau": -36*action["a"]*tau/radius**2,
        "minimal_dirac_square_matching": "signed cross term retained; quadratic coefficient 9/16 differs from production 3/8",
        "induced_four_fermion_coefficient_unit_MG": float(
            eliminate_minimal_trace_torsion(0, radius=radius, coefficients=coefficients)
            ["induced_four_fermion_coefficient"]),
        "quantum_response_calculation": "cg_frg.ewsb.torsion_response: common EC plus regulated Gaussian fermion action; fixed geometry/window",
        "quartic_reconstruction_used_to_determine_tau": False,
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
