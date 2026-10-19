"""Connection curvature and action matching in the V5 torsion convention.

The geometric convention is Cartan's T^a=de^a+omega^a_b wedge e^b.
At a Levi-Civita normal frame write omega=omega_LC+C, with C_ab,c
antisymmetric in a,b. For T_abc=epsilon_dbc B_ad this fixes

    C_ab,c=-(T_abc+T_bca-T_cab)/2.

The minus sign matters for spin vertices and derivatives. The table K
used in ec_variation is -C; its quadratic curvature is the same, while
its signed Dirac vertex has the opposite orientation. No action
coefficient or spin-current state is inferred from the content ratio.

All calculations here use exact rational arrays. The curvature contraction
retains the covariant-divergence term; homogeneous examples alone would
not establish that term. Production and geometric actions are compared
without changing the parameter store or replacing either functional.
"""
from fractions import Fraction as Q
from itertools import product

import numpy as np

from cg_core.ec_variation import (
    _epsilon, quadratic_torsion_coefficients, torsion_invariants,
)


def _exact(value, shape, name):
    array = np.asarray(value, dtype=object)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}")
    result = np.empty(shape, dtype=object)
    for index in np.ndindex(shape):
        item = array[index]
        if isinstance(item, (bool, float, complex, np.floating, np.complexfloating)):
            raise TypeError(f"{name} requires rational entries, not floating-point data")
        result[index] = Q(int(item)) if isinstance(item, np.integer) else Q(item)
    return result


def cartan_connection(dual):
    """Metric-compatible connection difference and its actual Cartan torsion.

    C_ab,c acts as a skew matrix on vector indices a,b in direction c.
    The returned torsion satisfies T_abc=C_ac,b-C_ab,c exactly. This
    makes the sign conversion to ec_variation's K explicit.
    """
    b = _exact(dual, (3, 3), "dual torsion")
    torsion = np.empty((3, 3, 3), dtype=object)
    connection = np.empty_like(torsion)
    for a, i, j in product(range(3), repeat=3):
        torsion[a, i, j] = sum(_epsilon(d, i, j)*b[a, d] for d in range(3))
    for a, i, j in product(range(3), repeat=3):
        connection[a, i, j] = -(torsion[a, i, j]+torsion[i, j, a]-torsion[j, a, i])/2
    return {"torsion": torsion, "connection": connection}


def scalar_curvature_difference(dual, derivative=None):
    """Exact R(omega)-R(LC), including the covariant-divergence term.

    derivative[d,a,b] is the LC covariant derivative of B_ab in direction
    d at the point. There is no flat-background assumption: LC-normal
    coordinates remove LC connection coefficients at that point and
    R(LC) is subtracted. The resulting difference is tensorial.

    Directly contract d_LC C+C wedge C. Its quadratic part is
    I1/4+I2/2-I3. The linear part is div J, where J_a=2 sum_b C_ab,b
    =-2 sum_b T_bb,a. On closed RP3 its integral is zero for smooth
    global fields; on a domain it is a boundary flux, not an omitted
    bulk contribution.
    """
    b = _exact(dual, (3, 3), "dual torsion")
    data = cartan_connection(b)
    c = data["connection"]
    db = (np.full((3, 3, 3), Q(0), dtype=object) if derivative is None
          else _exact(derivative, (3, 3, 3), "covariant derivative"))
    dc = np.array([cartan_connection(db[d])["connection"] for d in range(3)], dtype=object)
    curvature = np.empty((3, 3, 3, 3), dtype=object)
    quadratic, divergence = Q(0), Q(0)
    for a, v, i, j in product(range(3), repeat=4):
        commutator = sum(c[a, e, i]*c[e, v, j]-c[a, e, j]*c[e, v, i]
                         for e in range(3))
        linear = dc[i, a, v, j]-dc[j, a, v, i]
        curvature[a, v, i, j] = linear+commutator
        if a == i and v == j:
            quadratic += commutator
            divergence += linear
    flux = tuple(2*sum(c[a, v, v] for v in range(3)) for a in range(3))
    invariants = torsion_invariants(b)
    polynomial = invariants[0]/4+invariants[1]/2-invariants[2]
    return {**data, "curvature_difference": curvature,
            "scalar_difference": quadratic+divergence,
            "quadratic_scalar": quadratic, "covariant_divergence": divergence,
            "divergence_flux": flux, "invariants": invariants,
            "invariant_polynomial": polynomial,
            "quadratic_identity_residual": quadratic-polynomial}


def production_curvature_matching():
    """Compare the actual production action with curvature in M_G=1 units.

    Match the isotropic trace coefficient, which is necessary for any
    common overall normalization. The two remaining coefficients then
    test equality on the complete nine-dimensional torsion space.
    A trace-matched curvature functional has the same isotropic saddle
    but different transverse Hessians. Matching this slice is not a
    derivation of the overall gravitational normalization.
    """
    from cg_core.ec_variation import production_torsion_variation
    production = production_torsion_variation()["action_coefficients"]
    curvature = (Q(1, 4), Q(1, 2), Q(-1))
    pw = quadratic_torsion_coefficients(*production)
    cw = quadratic_torsion_coefficients(*curvature)
    normalization = pw[0]/cw[0]
    difference = tuple(p-normalization*c for p, c in zip(production, curvature))
    weights = quadratic_torsion_coefficients(*difference)
    return {
        "units": "M_G=1; multiply every action coefficient by M_G^3",
        "production_invariant_coefficients": production,
        "curvature_invariant_coefficients": curvature,
        "curvature_irreducible_weights": cw,
        "trace_matched_curvature_normalization": normalization,
        "extra_invariant_coefficients": difference,
        "extra_irreducible_weights": weights,
        "extra_irreducible_hessians": tuple(2*w for w in weights),
        "same_action_up_to_overall_normalization": not any(weights),
        "isotropic_curvature_coefficient": 3*cw[0],
        "production_isotropic_coefficient": 3*pw[0],
        "cartan_dual_from_existing_spin_dual": Q(-1),
        "cartan_dirac_trace_vertex": Q(1, 4),
        "existing_dirac_trace_vertex": Q(-1, 4),
    }


def cartan_spin_connection_vertices():
    """All nine Hermitian Pauli vertices in the stated Cartan convention.

    The same connection used in the curvature is inserted into
    i/8 C_bc,a {gamma_a,gamma_b gamma_c}. Evaluation gives
    +(tr B)/4 I_2. Comparing this table with ec_variation's -K table
    fixes the orientation conversion instead of altering a coefficient
    to obtain a preferred response.
    """
    gamma = (np.array([[0, 1], [1, 0]], complex),
             np.array([[0, -1j], [1j, 0]], complex),
             np.diag([1., -1.]).astype(complex))
    vertices = np.zeros((3, 3, 2, 2), complex)
    for i, j in product(range(3), repeat=2):
        b = np.full((3, 3), Q(0), dtype=object)
        b[i, j] = Q(1)
        c = cartan_connection(b)["connection"]
        for a, u, v in product(range(3), repeat=3):
            vertices[i, j] += 1j/8*float(c[u, v, a])*(
                gamma[a]@gamma[u]@gamma[v]+gamma[u]@gamma[v]@gamma[a])
    return vertices


def minimal_gauge_curvature(dual, gauge, derivative):
    """Compute F=dA+A wedge A using the same torsionful connection.

    gauge[a] is a matrix-valued covector and derivative[a,b] is its LC
    covariant derivative. Cartan's identity gives

        F_ab=nabla_a A_b-nabla_b A_a+T^c_ab A_c+[A_a,A_b].

    The connection term cancels against the torsion term before the
    Yang--Mills norm is formed. Thus minimal F-squared has no explicit
    algebraic contorsion vertex at fixed metric and gauge field. Changes
    of metric, states and nonminimal couplings are distinct variations.
    """
    a = np.asarray(gauge, dtype=object)
    if a.ndim != 3 or a.shape[0] != 3 or a.shape[1] < 1 or a.shape[1] != a.shape[2]:
        raise ValueError("three equally sized square gauge matrices required")
    a = _exact(a, a.shape, "gauge field")
    da = _exact(derivative, (3, 3, a.shape[1], a.shape[2]), "gauge derivative")
    data = cartan_connection(dual)
    c, t = data["connection"], data["torsion"]
    covariant, correction = np.empty_like(da), np.empty_like(da)
    native, complete = np.empty_like(da), np.empty_like(da)
    for i, j in product(range(3), repeat=2):
        native[i, j] = da[i, j]-da[j, i]+a[i]@a[j]-a[j]@a[i]
        covariant[i, j] = native[i, j]-sum((c[e, j, i]-c[e, i, j])*a[e] for e in range(3))
        correction[i, j] = sum(t[e, i, j]*a[e] for e in range(3))
        complete[i, j] = covariant[i, j]+correction[i, j]
    return {"covariant_antisymmetrization_with_commutator": covariant,
            "torsion_correction": correction, "curvature": complete,
            "exterior_curvature": native,
            "connection_cancellation_residual": complete-native}


def paired_dirac_determinants(reference, native, tau, radius):
    """Exact two-sign determinant comparison at one shared reference mode.

    This comparison does not create a missing sign partner in the RP3
    spectrum. It tests the more favourable case where both signs and
    weights really are present. Even then replacing the two squared
    operators by their mean loses a term at order tau squared.
    """
    a, d, t, length = map(Q, (reference, native, tau, radius))
    if a <= 0 or length <= 0:
        raise ValueError("positive reference denominator and radius required")
    shift = -3*t/(4*length)
    mean = a+shift*shift
    plus, minus = mean+2*d*shift, mean-2*d*shift
    if plus <= 0 or minus <= 0:
        raise ValueError("both regulated squared-operator denominators must be positive")
    return {"positive_sign_denominator": plus, "negative_sign_denominator": minus,
            "exact_pair_determinant": plus*minus,
            "mean_square_determinant": mean*mean,
            "lost_determinant_term": -4*d*d*shift*shift,
            "exact_to_mean_determinant_ratio": plus*minus/(mean*mean),
            "same_parameter_quadratic_shift_ratio": Q(3, 8)/Q(9, 16)}
