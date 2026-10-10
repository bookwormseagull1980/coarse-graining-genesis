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

"""Quadrature and canonical normalization for explicitly supplied matter data.

These APIs do not infer spatial modes, an action, or physical matching scales
from target couplings. The caller supplies modes, quadrature, kinetic metric
and vertex from the same action. Arrays retain all bundle components; scalar
harmonics are not silently substituted for spinor modes. No parameter store or
comparison database is read. Integration convergence remains a property of
the supplied quadrature and must be checked by refinement.
"""
from __future__ import annotations

import math
import numpy as np


def _weights(weights, count):
    w = np.asarray(weights,dtype=float)
    if w.shape != (count,) or not np.isfinite(w).all() or np.any(w <= 0):
        raise ValueError("one strictly positive finite quadrature weight per point required")
    return w


def _modes(modes):
    a = np.asarray(modes,dtype=complex)
    if a.ndim != 3 or min(a.shape)==0 or not np.isfinite(a).all():
        raise ValueError("modes must have shape (points, modes, bundle components)")
    return a


def _hermitian(matrix, name):
    a = np.asarray(matrix,dtype=complex)
    if a.ndim != 2 or a.shape[0] != a.shape[1] or not a.shape[0]:
        raise ValueError(f"{name} must be a nonempty square matrix")
    if not np.isfinite(a).all() or not np.allclose(a,a.conj().T,rtol=1e-11,atol=1e-13):
        raise ValueError(f"{name} must be finite Hermitian")
    return a


def inverse_sqrt_gram(gram, *, relative_floor=1e-13):
    """Principal G^(-1/2), rejecting null/ill-conditioned retained modes."""
    G = _hermitian(gram,"kinetic Gram")
    if not 0 < relative_floor < 1:
        raise ValueError("relative_floor must lie strictly between zero and one")
    eigenvalues,U = np.linalg.eigh(G)
    if eigenvalues[0] <= max(0.0,eigenvalues[-1]*relative_floor):
        raise ValueError("retained kinetic Gram must be positive definite and resolved")
    return (U/eigenvalues**.5)@U.conj().T


def kinetic_gram(modes, weights, bundle_metric=None):
    """Integral psi_i^dagger B psi_j with explicit measure weights."""
    psi = _modes(modes)
    q,_,d = psi.shape
    w = _weights(weights,q)
    B = np.broadcast_to(np.eye(d) if bundle_metric is None else bundle_metric,(q,d,d))
    if not np.isfinite(B).all() or not np.allclose(B,B.conj().transpose(0,2,1)):
        raise ValueError("bundle kinetic metric must be Hermitian at every point")
    if np.min(np.linalg.eigvalsh(B)) <= 0:
        raise ValueError("bundle kinetic metric must be positive definite")
    return np.einsum('q,qia,qab,qjb->ij',w,psi.conj(),B,psi)


def spatial_vertex(left_modes, right_modes, operator, weights):
    """Compute integral psi_L^dagger O_H psi_R, including bundle indices.

    operator has shape (points, left_components, right_components), or a
    constant matrix of the corresponding component dimensions.
    """
    left,right = _modes(left_modes),_modes(right_modes)
    if left.shape[0] != right.shape[0]:
        raise ValueError("left/right modes must use the same quadrature points")
    w = _weights(weights,left.shape[0])
    O = np.broadcast_to(np.asarray(operator,dtype=complex),
                        (len(w),left.shape[2],right.shape[2]))
    if not np.isfinite(O).all():
        raise ValueError("vertex operator must be finite")
    return np.einsum('q,qia,qab,qjb->ij',w,left.conj(),O,right)


def canonical_vertex(vertex, left_gram, right_gram, scalar_kinetic):
    """Z_L^(-1/2) Y Z_R^(-1/2)/sqrt(Z_H), in principal canonical bases.

    Under arbitrary invertible mode changes the resulting vertices transform
    by induced unitary matrices. Singular values and physical amplitudes,
    not individual entries, are invariant. Z_H is the same action's positive
    scalar kinetic coefficient, not a finite-source susceptibility.
    """
    L,R = inverse_sqrt_gram(left_gram),inverse_sqrt_gram(right_gram)
    Y = np.asarray(vertex,dtype=complex)
    if Y.shape != (len(L),len(R)) or not np.isfinite(Y).all():
        raise ValueError("vertex dimensions must match the retained modes")
    if not np.isfinite(scalar_kinetic) or scalar_kinetic <= 0:
        raise ValueError("positive scalar kinetic coefficient required")
    return L@Y@R/np.sqrt(scalar_kinetic)


def canonical_flavour_pair(up_vertex, down_vertex, left_gram, up_right_gram,
                          down_right_gram, scalar_kinetic, *, gap_rtol=1e-10):
    """Forward mass and mixing extraction from one common left kinetic form.

    Both raw vertices and all kinetic forms are inputs from the same action.
    Eigenvalues are ordered by increasing Yukawa magnitude. For a degenerate
    left spectrum the matrix of mixing angles is not an observable; only the
    spectral projectors and invariant traces are returned in that case.
    A common nonunitary change of left coordinates induces the same unitary
    transformation after canonical normalization in both sectors.
    """
    if not np.isfinite(gap_rtol) or gap_rtol <= 0:
        raise ValueError("positive finite spectral gap tolerance required")
    up = canonical_vertex(up_vertex, left_gram, up_right_gram, scalar_kinetic)
    down = canonical_vertex(down_vertex, left_gram, down_right_gram, scalar_kinetic)
    if up.shape != (3, 3) or down.shape != (3, 3):
        raise ValueError("three retained left and right family coordinates required")
    # Direct SVD avoids squaring the condition number of a mass hierarchy.
    # Forming Y Y* before extracting its lightest eigenvalue loses relative
    # precision even when the singular value itself remains well resolved.
    lu, su, _ = np.linalg.svd(up, full_matrices=False)
    ld, sd, _ = np.linalg.svd(down, full_matrices=False)
    su, lu = su[::-1], lu[:, ::-1]
    sd, ld = sd[::-1], ld[:, ::-1]
    def spectral_groups(values, vectors):
        scale = max(float(values[-1]), np.finfo(float).tiny)
        numerical_floor = 16*np.finfo(float).eps*scale
        groups = [[0]]
        for i in range(1, len(values)):
            tolerance = max(numerical_floor, gap_rtol*values[i])
            if values[i]-values[i-1] <= tolerance:
                groups[-1].append(i)
            else:
                groups.append([i])
        return [{"indices": tuple(group),
                 "projector": vectors[:, group]@vectors[:, group].conj().T}
                for group in groups]
    up_groups, down_groups = spectral_groups(su, lu), spectral_groups(sd, ld)
    resolved = len(up_groups) == len(down_groups) == 3
    hu, hd = up@up.conj().T, down@down.conj().T
    commutator = hu@hd-hd@hu
    mixing = lu.conj().T@ld if resolved else None
    return {"up_yukawa": su, "down_yukawa": sd,
            "up_canonical_vertex": up, "down_canonical_vertex": down,
            "mass_labels": "increasing singular value in each sector",
            "simple_left_spectra": resolved,
            "up_spectral_groups": up_groups, "down_spectral_groups": down_groups,
            "mixing": mixing,
            "commutator_norm": float(np.linalg.norm(commutator, ord=2)),
            "imag_trace_commutator_cubed": float(np.imag(np.trace(
                commutator@commutator@commutator))),
            "J": None if mixing is None else float(np.imag(
                mixing[0, 0]*mixing[1, 1]*mixing[0, 1].conjugate()
                *mixing[1, 0].conjugate()))}


def tree_mass_parameters(couplings, vev_GeV, *, scale_GeV, coupling_scheme,
                         vev_definition):
    """Tree coefficients of the canonically normalized broken-phase action.

    g1 is GUT-normalized. The caller declares the renormalized or fixed VEV
    definition at the same scale; no electroweak finite conversion is assumed.
    Negative lambda is retained as a negative curvature mass-squared and does
    not acquire a real Higgs mass by absolute-value replacement.
    """
    state = np.asarray(couplings, float)
    if (state.shape != (5,) or not np.isfinite(state).all()
            or np.any(state[:3] <= 0) or state[3] < 0):
        raise ValueError("finite five-coupling state with positive gauge couplings required")
    if not all(np.isfinite(x) and x > 0 for x in (vev_GeV, scale_GeV)):
        raise ValueError("positive finite scale and VEV required")
    if not coupling_scheme.strip() or not vev_definition.strip():
        raise ValueError("coupling scheme and VEV definition must be stated")
    g1, g2, _, yt, quartic = state
    mh2 = float(2*quartic*vev_GeV**2)
    return {"scale_GeV": float(scale_GeV), "coupling_scheme": coupling_scheme,
            "vev_definition": vev_definition, "vev_GeV": float(vev_GeV),
            "m_top_tree_GeV": float(yt*vev_GeV/np.sqrt(2)),
            "m_H_curvature_squared_GeV2": mh2,
            "m_H_tree_GeV": float(np.sqrt(mh2)) if mh2 >= 0 else None,
            "m_W_tree_GeV": float(g2*vev_GeV/2),
            "m_Z_tree_GeV": float(np.sqrt(g2*g2+3*g1*g1/5)*vev_GeV/2),
            "pole_mass_matching_performed": False,
            "order": "tree conversion of the supplied canonical couplings and VEV"}


def qcd_mass_matching_one_loop(mass_GeV, alpha_s, *, scale_GeV,
                               input_definition, boundary_source):
    """Finite heavy-quark self-energy matching in fundamental SU(3) QCD.

    The action uses Tr(Ta Tb)=delta_ab/2 and CF=4/3. In dimensional
    regularization its on-shell finite coefficient is
    integral_0^1 [(2+2x) log(mu^2/(m^2*x^2))-2x] dx
    = 4+3 log(mu^2/m^2). This gives the MSbar-to-pole conversion through
    O(alpha_s); the inverse is expanded to the same order, not resummed.
    See PDG 2024, Quark Masses, Eq. (60.25), for mu=m and the pole-mass
    convention. Electroweak, finite-VEV and higher-order terms are separate.

    input_definition is explicitly 'MSbar' or 'pole'. A geometric readout
    can enter only after a caller supplies a physical boundary identification;
    its name or numerical proximity to a pole mass supplies no such map.
    alpha_s is MSbar at scale_GeV. Perturbative use requires a heavy quark,
    small alpha_s and controlled logarithms; no nonperturbative pole is assumed.
    """
    if not all(np.isfinite(x) and x > 0 for x in (mass_GeV, scale_GeV)):
        raise ValueError("positive finite mass and matching scale required")
    if not np.isfinite(alpha_s) or alpha_s < 0:
        raise ValueError("finite nonnegative MSbar alpha_s required")
    if input_definition not in ("MSbar", "pole"):
        raise ValueError("input_definition must be MSbar or pole")
    if not isinstance(boundary_source, str) or not boundary_source.strip():
        raise ValueError("physical boundary identification must be stated")
    cf = 4/3
    logarithm = 2*(np.log(scale_GeV)-np.log(mass_GeV))
    finite_coefficient = float(4+3*logarithm)
    relative = float(cf*alpha_s/(4*np.pi)*finite_coefficient)
    sign = 1 if input_definition == "MSbar" else -1
    matched = float(mass_GeV*(1+sign*relative))
    if not np.isfinite(matched) or matched <= 0:
        raise ValueError("one-loop expansion gives no positive matched mass")
    return {"input_mass_GeV": float(mass_GeV),
            "input_definition": input_definition,
            "output_definition": "pole" if input_definition == "MSbar" else "MSbar",
            "matched_mass_GeV": matched, "scale_GeV": float(scale_GeV),
            "alpha_s_MSbar": float(alpha_s), "colour_C_F": cf,
            "self_energy_finite_coefficient": finite_coefficient,
            "relative_one_loop_term": sign*relative,
            "boundary_source": boundary_source,
            "order": "one-loop pure-QCD finite matching; O(alpha_s^2) omitted",
            "finite_vev_and_electroweak_matching_included": False}


def _ew_tadpole_integral(x, scale_squared):
    return 0. if x == 0 else x*(math.log(x/scale_squared)-1)


def _ew_tadpole_divided_difference(x, y, scale_squared):
    """A[x,y] for A(x)=x(log(x/Q²)-1), including coincident masses."""
    if x < y:
        x, y = y, x
    if y == 0:
        if x == 0:
            raise ValueError("unweighted divided difference at two zero masses is singular")
        return math.log(x/scale_squared)-1
    ratio = (x-y)/y
    if ratio < 1e-4:
        remainder = ratio*(.5+ratio*(-1/6+ratio*(1/12+ratio*(-1/20+ratio/30))))
    else:
        remainder = (1+ratio)*math.log1p(ratio)/ratio-1
    return math.log(y/scale_squared)+remainder


def electroweak_matching_one_loop(couplings, vev_GeV, *, scale_GeV,
                                 vev_definition, action_source,
                                 bottom_yukawa=0., tau_yukawa=0.):
    """Finite VEV and muon-decay matching of one canonical MSbar action.

    Landau gauge and V=m² H*H+lambda(H*H)². The input g1 is GUT-normalized.
    vev_definition is tree_minimum (v_tree²=-m²/lambda) or
    tadpole_free_landau (the loop effective-potential minimum). Optional
    bottom/tau Yukawas use the same scale and scheme; zero selects the
    five-coupling top-sector truncation. Every result is expanded to one loop.

    The finite coefficients are Martin--Robertson, arXiv:1907.02500v5,
    equations (1.3), (4.1)--(4.7), and Martin, arXiv:1406.2355,
    equations (1.6)--(1.12), (2.3). No measured Fermi constant is an input.
    """
    state = np.asarray(couplings, dtype=float)
    if state.shape != (5,) or not np.isfinite(state).all():
        raise ValueError("five finite canonical MSbar couplings required")
    g1, g, g3, yt, quartic = map(float, state)
    if not all(np.isfinite(x) for x in (bottom_yukawa, tau_yukawa)):
        raise ValueError("finite bottom and tau Yukawas required")
    if min(g1, g3, yt, bottom_yukawa, tau_yukawa) < 0 or g <= 0 or quartic <= 0:
        raise ValueError("nonnegative gauge/Yukawa and positive weak/quartic couplings required")
    if not all(np.isfinite(x) and x > 0 for x in (vev_GeV, scale_GeV)):
        raise ValueError("positive finite VEV and scale required")
    if (not isinstance(vev_definition, str)
            or vev_definition not in ("tree_minimum", "tadpole_free_landau")):
        raise ValueError("explicit supported VEV definition required")
    if not isinstance(action_source, str) or not action_source.strip():
        raise ValueError("a nonempty action source string is required")
    v2, q2 = vev_GeV**2, scale_GeV**2
    gp2 = 3*g1*g1/5
    W, Z, h = g*g*v2/4, (g*g+gp2)*v2/4, 2*quartic*v2
    t, b, tau_mass = yt*yt*v2/2, bottom_yukawa**2*v2/2, tau_yukawa**2*v2/2
    A = lambda x: _ew_tadpole_integral(x, q2)
    dd = lambda x, y: _ew_tadpole_divided_difference(x, y, q2)
    # Eliminate the removable h=W singularity before evaluation:
    # [(4g²-24lambda)A(W)-g²A(h)]/(h-W) = -g² A[h,W]-12 A(W)/v².
    fermion_ratio = 0. if t == b == 0 else t*dd(t, b)+A(b)
    delta_r_terms = {
        "weak_hypercharge": .75*(g*g-gp2)*dd(Z, W),
        "higgs_weak": -.75*g*g*dd(h, W)-9*A(W)/v2,
        "quark_doublet": 6*fermion_ratio/v2,
        "tau": 2*A(tau_mass)/v2,
        "local": -(3*g*g+gp2)/8+(3*yt*yt+3*bottom_yukawa**2+tau_yukawa**2)/2-quartic,
    }
    tadpole_terms = {
        "higgs": 3*quartic*A(h),
        "W": g*g/2*(3*A(W)+2*W),
        "Z": (g*g+gp2)/4*(3*A(Z)+2*Z),
        "top": -6*yt*yt*A(t),
        "bottom": -6*bottom_yukawa**2*A(b),
        "tau": -2*tau_yukawa**2*A(tau_mass),
    }
    loop = 16*math.pi**2
    delta_r = sum(delta_r_terms.values())/loop
    delta1 = sum(tadpole_terms.values())
    tadpole_fraction = delta1/(loop*quartic*v2)
    if vev_definition == "tree_minimum":
        relative = delta_r+tadpole_fraction
        loop_vev_shift = -tadpole_fraction/2
        quadratic = -quartic*v2
        loop_vev_sq = v2*(1-tadpole_fraction)
    else:
        relative = delta_r
        loop_vev_shift = 0.
        quadratic = -quartic*v2-delta1/loop
        loop_vev_sq = v2
    gf_tree = 1/(math.sqrt(2)*v2)
    return {"scheme": "MSbar", "gauge": "Landau",
            "order": "one loop; terms of two-loop order omitted",
            "action_source": action_source, "vev_definition": vev_definition,
            "scale_GeV": float(scale_GeV), "input_vev_GeV": float(vev_GeV),
            "couplings": state.tolist(), "bottom_yukawa": float(bottom_yukawa),
            "tau_yukawa": float(tau_yukawa),
            "running_mass_squares_GeV2": {"W": W, "Z": Z, "h": h, "top": t, "bottom": b, "tau": tau_mass},
            "delta_r_one_loop_coefficient_terms": delta_r_terms,
            "delta_r_one_loop": delta_r,
            "tadpole_delta1_terms_GeV2": tadpole_terms, "tadpole_delta1_GeV2": delta1,
            "tree_to_loop_vev_squared_fraction": -tadpole_fraction,
            "loop_vev_GeV_first_order": vev_GeV*(1+loop_vev_shift),
            "loop_vev_squared_GeV2_first_order": loop_vev_sq,
            "potential_quadratic_GeV2": quadratic,
            "G_F_tree_GeVminus2": gf_tree,
            "G_F_finite_relative_term": relative,
            "G_F_one_loop_GeVminus2": gf_tree*(1+relative),
            "fermi_vev_GeV_first_order": vev_GeV*(1-relative/2),
            "vev_logarithmic_beta_one_loop": (2.25*g*g+.75*gp2-3*yt*yt-3*bottom_yukawa**2-tau_yukawa**2)/loop}


def electroweak_matching_from_fermi_readout(couplings, fermi_vev_GeV, *,
                                          scale_GeV, input_definition,
                                          action_source, bottom_yukawa=0.,
                                          tau_yukawa=0.):
    """Represent a fixed G_F=1/(sqrt(2)*v_F^2) in tadpole-free MSbar.

    The leading canonical couplings and v_F belong to the same declared
    effective action. The finite kernel is evaluated once at v=v_F: a
    one-loop displacement of its arguments contributes only at two loops.
    Martin--Robertson, arXiv:1907.02500v5, (4.1)--(4.3), then gives
    v_L^2=v_F^2*(1+delta_r) and v_L=v_F*(1+delta_r/2) through one loop.
    These two truncated series are returned separately; their difference
    after squaring is of two-loop order.

    The tadpole term enters m2_MSbar=-lambda_MSbar*v_L^2-tadpole_one_loop.
    Finite top and Higgs mass-readout corrections are separate source
    calculations. No value for either correction or matched matter
    coupling is assigned by this weak-input conversion.
    """
    if (not isinstance(input_definition, str)
            or input_definition != "fermi_constant_readout"):
        raise ValueError("input_definition must be fermi_constant_readout")
    coefficient = electroweak_matching_one_loop(
        couplings, fermi_vev_GeV, scale_GeV=scale_GeV,
        vev_definition="tadpole_free_landau", action_source=action_source,
        bottom_yukawa=bottom_yukawa, tau_yukawa=tau_yukawa)
    v2 = float(fermi_vev_GeV)**2
    delta_r = coefficient["delta_r_one_loop"]
    return {
        "input_definition": input_definition,
        "input_fermi_vev_GeV": float(fermi_vev_GeV),
        "action_source": action_source,
        "scale_GeV": float(scale_GeV),
        "leading_couplings": coefficient["couplings"],
        "leading_coupling_definition": "canonical leading-order coefficients of the same action",
        "bottom_yukawa": coefficient["bottom_yukawa"],
        "tau_yukawa": coefficient["tau_yukawa"],
        "output_vev_definition": "tadpole_free_landau",
        "scheme": "MSbar", "gauge": "Landau",
        "order": "one loop; terms of two-loop order omitted",
        "coefficient_evaluation_vev_GeV": float(fermi_vev_GeV),
        "G_F_preserved_GeVminus2": 1/(math.sqrt(2)*v2),
        "running_vev_GeV_first_order": float(fermi_vev_GeV)*(1+delta_r/2),
        "running_vev_squared_GeV2_first_order": v2*(1+delta_r),
        "delta_r_one_loop": delta_r,
        "delta_r_one_loop_coefficient_terms": coefficient["delta_r_one_loop_coefficient_terms"],
        "tadpole_delta1_GeV2": coefficient["tadpole_delta1_GeV2"],
        "tadpole_one_loop_GeV2": coefficient["tadpole_delta1_GeV2"]/(16*math.pi**2),
        "vev_logarithmic_beta_one_loop": coefficient["vev_logarithmic_beta_one_loop"],
        "stationarity_relation": "m2_MSbar = -lambda_MSbar*v_L^2 - tadpole_one_loop_GeV2 + O(two-loop)",
        "finite_mass_readout_matching": {
            "top_correction_GeV": None,
            "higgs_squared_correction_GeV2": None,
            "correction_definition": "finite corrections to the same generated mass readouts",
            "top_relation": "m_top_generated = y_top_MSbar*v_L/sqrt(2) + Delta_top + O(two-loop)",
            "higgs_relation": "m_H_generated^2 = 2*lambda_MSbar*v_L^2 + Delta_H_squared + O(two-loop)",
        },
    }


def _ew_two_point_finite(x, y, s, q2):
    """B(x,y;s)=-integral_0^1 log((ux+(1-u)y-u(1-u)s-i0)/Q²) du.

    Squared masses and s are nonnegative. Equal-mass and massless limits
    have analytic expressions. The remaining real integral is split at
    its threshold roots; the -i0 prescription gives +i*pi times the
    length of the negative-denominator interval. The returned count is
    the actual number of quadrature integrand evaluations.
    """
    if s == 0:
        return complex(-_ew_tadpole_divided_difference(x, y, q2)), 0, "zero momentum"
    if x == y and x > 0:
        ratio = s/x
        if ratio < 1e-3:
            term, total, n = ratio/6, 0., 1
            while True:
                total += term
                term *= ratio*n/(2*(2*n+3))
                n += 1
                if abs(term) <= np.finfo(float).eps*abs(total):
                    break
            return complex(-math.log(x/q2)+total), 0, "equal masses: convergent series"
        if ratio < 4:
            beta = math.sqrt(4/ratio-1)
            value = 2-math.log(x/q2)-2*beta*math.atan(1/beta)
            return complex(value), 0, "equal masses: below threshold"
        beta = math.sqrt(max(0., 1-4/ratio))
        value = 2-math.log(x/q2)-beta*(2*math.log1p(beta)+math.log(ratio/4))
        return complex(value, math.pi*beta), 0, "equal masses: physical branch"
    if min(x, y) == 0:
        mass = max(x, y)
        if mass == 0:
            return complex(2-math.log(s/q2), math.pi), 0, "two massless lines"
        ratio = s/mass
        if ratio < 1e-3:
            term, total, n = ratio/2, 0., 1
            while True:
                total += term
                term *= ratio*n/(n+2)
                n += 1
                if abs(term) <= np.finfo(float).eps*abs(total):
                    break
            return complex(1-math.log(mass/q2)+total), 0, "one massless line: convergent series"
        product = 0. if ratio == 1 else (1/ratio-1)*math.log(abs(1-ratio))
        return complex(2-math.log(mass/q2)+product,
                       math.pi*max(0., 1-1/ratio)), 0, "one massless line: physical branch"
    from scipy.integrate import quad
    discriminant = (s-x-y)**2-4*x*y
    roots = []
    negative_length = 0.
    if discriminant >= 0:
        middle = (s+y-x)/(2*s)
        half = math.sqrt(discriminant)/(2*s)
        lower, upper = middle-half, middle+half
        roots = sorted(set(r for r in (lower, upper) if 0 < r < 1))
        negative_length = max(0., min(1., upper)-max(0., lower))
    def integrand(u):
        denominator = u*x+(1-u)*y-u*(1-u)*s
        return -math.log(abs(denominator)/q2)
    points = [0., *roots, 1.]
    value, count = 0., 0
    for lower, upper in zip(points[:-1], points[1:]):
        result = quad(integrand, lower, upper, epsabs=2e-11,
                      epsrel=3e-12, full_output=1)
        if len(result) != 3:
            raise ArithmeticError("finite two-point integral did not converge")
        value += result[0]
        count += result[2]["neval"]
    return complex(value, math.pi*negative_length), count, "split Feynman-parameter integral"


def top_higgs_pole_matching_one_loop(couplings, vev_GeV, *, scale_GeV,
                                    vev_definition, action_source):
    """Complex top and Higgs poles of the same canonical leading action.

    V=m² H†H+lambda(H†H)², g'²=3*g1²/5, with the Landau-gauge,
    tadpole-free MSbar VEV. Bottom and lighter Yukawas vanish and the
    charged-current top vertex has V_tb=1, matching the five-coupling
    truncation. A(x)=x[log(x/Q²)-1] and B has the -i0 prescription stated
    in _ew_two_point_finite. The finite parts include the tadpole-free
    stationarity relation; a second tadpole correction is not added.

    The Higgs squared-mass coefficient is Martin--Robertson,
    arXiv:1407.4336v3, (2.43),(2.46), at s=h=2*lambda*v². The top
    coefficient is Martin, arXiv:1604.01134v2, (2.1),(2.2),(2.20), at
    s=t=yt²*v²/2. At one loop all integral arguments are leading-order
    masses; shifting them by the matched finite terms is two-loop order.
    Each distinct A or B is evaluated once and reused in every sector.
    """
    state = np.asarray(couplings, dtype=float)
    if state.shape != (5,) or not np.isfinite(state).all():
        raise ValueError("five finite canonical leading couplings required")
    g1, g, g3, yt, quartic = map(float, state)
    if min(g1, g3) < 0 or min(g, yt, quartic) <= 0:
        raise ValueError("nonnegative Abelian/strong and positive weak/Yukawa/quartic couplings required")
    if not all(np.isfinite(x) and x > 0 for x in (vev_GeV, scale_GeV)):
        raise ValueError("positive finite VEV and scale required")
    if not isinstance(vev_definition, str) or vev_definition != "tadpole_free_landau":
        raise ValueError("vev_definition must be tadpole_free_landau")
    if not isinstance(action_source, str) or not action_source.strip():
        raise ValueError("a nonempty action source string is required")
    v2, q2 = float(vev_GeV)**2, float(scale_GeV)**2
    gp2, g2 = 3*g1*g1/5, g*g
    combined = g2+gp2
    t, h, W, Z = yt*yt*v2/2, 2*quartic*v2, g2*v2/4, combined*v2/4
    a_cache, b_cache, methods = {}, {}, {}
    integral_count = 0
    def A(x):
        if x not in a_cache:
            a_cache[x] = _ew_tadpole_integral(x, q2)
        return a_cache[x]
    def B(x, y, s):
        nonlocal integral_count
        key = (min(x, y), max(x, y), s)
        if key not in b_cache:
            value, count, method = _ew_two_point_finite(*key, q2)
            b_cache[key] = value
            integral_count += count
            methods[method] = methods.get(method, 0)+1
        return b_cache[key]
    higgs_terms = {
        "top": 3*yt*yt*(4*t-h)*B(t, t, h),
        "scalar": -18*quartic**2*v2*B(h, h, h),
        "Z": combined/2*((h-3*Z-h*h/(4*Z))*B(Z, Z, h)-h*A(Z)/(2*Z)+2*Z),
        "W": g2*((h-3*W-h*h/(4*W))*B(W, W, h)-h*A(W)/(2*W)+2*W),
    }
    charge, isospin = 2/3, .5
    e2 = g2*gp2/combined
    top_terms = {
        "QCD": g3*g3*(4/3)*t*(8-6*math.log(t/q2)),
        "photon": charge*charge*e2*t*(8-6*math.log(t/q2)),
        "W": g2/4*((2*W-t-t*t/W)*B(0., W, t)+(2*W-t)*A(W)/W+2*t),
        "Z_chiral": (isospin**2*combined-2*isospin*charge*gp2
            +2*charge**2*gp2**2/combined)*((Z-t)*B(t, Z, t)+A(Z)-A(t)+t),
        "Z_mass": 2*charge*gp2*(-isospin+charge*gp2/combined)*t*(3*B(t, Z, t)-2),
        "Higgs": yt*yt/2*((h-4*t)*B(h, t, t)+A(h)-2*A(t)),
    }
    loop = 16*math.pi**2
    top_shift, higgs_shift = sum(top_terms.values())/loop, sum(higgs_terms.values())/loop
    def components(value):
        return {"real": float(np.real(value)), "imag": float(np.imag(value))}
    return {
        "scheme": "MSbar", "gauge": "Landau", "vev_definition": vev_definition,
        "action_source": action_source, "scale_GeV": float(scale_GeV),
        "leading_vev_GeV": float(vev_GeV), "leading_couplings": state.tolist(),
        "order": "one loop; masses and squared masses expanded separately",
        "content": "five-coupling SM action; y_b and lighter Yukawas zero; V_tb=1",
        "references": ["arXiv:1407.4336v3 Eqs. (2.43),(2.46)",
                       "arXiv:1604.01134v2 Eqs. (2.1),(2.2),(2.20)"],
        "running_mass_squares_GeV2": {"top": t, "Higgs": h, "W": W, "Z": Z},
        "top_squared_correction_GeV2": components(top_shift),
        "higgs_squared_correction_GeV2": components(higgs_shift),
        "top_squared_terms_GeV2": {k: components(x/loop) for k, x in top_terms.items()},
        "higgs_squared_terms_GeV2": {k: components(x/loop) for k, x in higgs_terms.items()},
        "top_mass_correction_GeV": float(np.real(top_shift))/(2*math.sqrt(t)),
        "higgs_mass_correction_GeV": float(np.real(higgs_shift))/(2*math.sqrt(h)),
        "top_width_GeV_first_order": -float(np.imag(top_shift))/math.sqrt(t),
        "higgs_width_GeV_first_order": -float(np.imag(higgs_shift))/math.sqrt(h),
        "evaluation_work": {"distinct_A_values": len(a_cache), "distinct_B_values": len(b_cache),
                            "B_methods": methods, "quadrature_integrand_evaluations": integral_count},
    }


def charged_lepton_pole_matching_one_loop(pole_masses_GeV, gauge_couplings,
        vev_GeV, *, higgs_mass_GeV, scale_GeV, input_definition, action_source):
    """Finite charged-lepton matching in the common Landau MSbar action.

    The supplied generated masses define pole conditions of this effective
    realization. Martin, Phys. Rev. D 93, 094017 (2016), Eq. (2.20), with
    Q=-1, I3=-1/2 and a massless neutrino partner, gives the full one-loop
    photon, W, Z and Higgs self-energy. Charged-lepton masses are retained
    in the loop functions and y_l^2=2*M_l^2/v^2. GUT-normalized g1 and g2
    fix e^2 in the same action. The common VEV conversion cancels from
    (-1,2,-1) weighted log Yukawa/mass matching.

    All A and B functions are analytic below the weak thresholds. Their
    50-digit interval evaluation encloses roundoff, including cancellations
    of heavy squared masses for the electron. It is not an enclosure of
    uncomputed two-loop terms. No geometric-to-pole counterterm is inferred.
    """
    from mpmath.ctx_iv import MPIntervalContext
    species = ("electron", "muon", "tau")
    weights = (-1, 2, -1)
    if set(pole_masses_GeV) != set(species):
        raise ValueError("electron, muon and tau pole conditions required")
    masses = {name: float(pole_masses_GeV[name]) for name in species}
    gauge = np.asarray(gauge_couplings, dtype=float)
    if gauge.shape != (2,) or not np.isfinite(gauge).all() or min(gauge) <= 0:
        raise ValueError("positive finite GUT-normalized g1 and weak g2 required")
    if not all(math.isfinite(x) and x > 0 for x in
               (*masses.values(), vev_GeV, higgs_mass_GeV, scale_GeV)):
        raise ValueError("positive finite masses, VEV and scale required")
    if input_definition != "generated_on_shell_conditions":
        raise ValueError("input_definition must be generated_on_shell_conditions")
    if not isinstance(action_source, str) or not action_source.strip():
        raise ValueError("a nonempty action source string is required")
    iv = MPIntervalContext()
    iv.dps = 50
    g1, g = map(iv.mpf, gauge)
    v2, q2, h = iv.mpf(vev_GeV)**2, iv.mpf(scale_GeV)**2, iv.mpf(higgs_mass_GeV)**2
    gp2, g2 = 3*g1*g1/5, g*g
    combined = g2+gp2
    e2 = g2*gp2/combined
    W, Z = g2*v2/4, combined*v2/4
    A = lambda x: x*(iv.log(x/q2)-1)
    aw, az, ah = A(W), A(Z), A(h)
    loop = 32*iv.pi**2
    charge, isospin = -1, -iv.mpf(1)/2

    def endpoints(x):
        return [math.nextafter(float(x.a), -math.inf),
                math.nextafter(float(x.b), math.inf)]

    def center(x):
        return float(x.mid)

    def B_light_heavy(t, heavy):
        # B(t,X;t)=-log(X/Q^2)-integral log(1-u+(t/X)u^2)du.
        # Factoring the quadratic gives an exact real expression for t/X<1/4.
        r = t/heavy
        if r.b >= iv.mpf(1)/4:
            raise ValueError("charged-lepton mass must be below half each neutral heavy mass")
        s = iv.sqrt(1-4*r)
        small = 2*r/(1+s)
        integral = (-2-4*r/(1+s)**2*iv.log(small)
                    -((1+s)/(2*r)-1)*iv.log1p(-small))
        return -iv.log(heavy/q2)-integral

    terms_by_species, intervals_by_species, shifts = {}, {}, {}
    weighted_terms = {name: iv.mpf(0) for name in ("photon", "W", "Z_chiral", "Z_mass", "Higgs")}
    running = {}
    for name, weight in zip(species, weights):
        mass = iv.mpf(masses[name])
        t, yl2 = mass**2, 2*mass**2/v2
        r = t/W
        if r.b >= 1:
            raise ValueError("charged-lepton mass must be below the W mass")
        bw = 2-iv.log(W/q2)+(1/r-1)*iv.log1p(-r)
        bz, bh = B_light_heavy(t, Z), B_light_heavy(t, h)
        at = A(t)
        squared_terms = {
            "photon": e2*t*(8-6*iv.log(t/q2)),
            "W": g2/4*((2*W-t-t*t/W)*bw+(2*W-t)*aw/W+2*t),
            "Z_chiral": (isospin**2*combined-2*isospin*charge*gp2
                +2*charge**2*gp2**2/combined)*((Z-t)*bz+az-at+t),
            "Z_mass": 2*charge*gp2*(-isospin+charge*gp2/combined)*t*(3*bz-2),
            "Higgs": yl2/2*((h-4*t)*bh+ah-2*at),
        }
        # Pole inversion: log(mbar/M)=-delta M^2/(2*M^2) at one loop.
        log_terms = {key: -value/(loop*t) for key, value in squared_terms.items()}
        shift = sum(log_terms.values(), iv.mpf(0))
        shifts[name] = shift
        terms_by_species[name] = {key: center(value) for key, value in log_terms.items()}
        intervals_by_species[name] = {key: endpoints(value) for key, value in log_terms.items()}
        running[name] = center(mass*(1+shift))
        for key, value in log_terms.items():
            weighted_terms[key] += weight*value
    weighted = sum(weighted_terms.values(), iv.mpf(0))
    weak_weighted = sum((v for k, v in weighted_terms.items() if k != "photon"), iv.mpf(0))
    pole_combination = sum((weight*iv.log(iv.mpf(masses[name]))
        for name, weight in zip(species, weights)), iv.mpf(0))
    scale_derivative = 3*sum((weight*iv.mpf(masses[name])**2
        for name, weight in zip(species, weights)), iv.mpf(0))/(16*iv.pi**2*v2)
    return {
        "input_definition": input_definition, "action_source": action_source,
        "scheme": "MSbar", "gauge": "Landau", "vev_definition": "tadpole_free_landau",
        "scale_GeV": float(scale_GeV), "leading_vev_GeV": float(vev_GeV),
        "gauge_couplings_GUT_g1_g2": gauge.tolist(), "alpha_same_action": center(e2/(4*iv.pi)),
        "pole_mass_conditions_GeV": masses, "higgs_mass_GeV": float(higgs_mass_GeV),
        "content": "three charged leptons with massless neutrino partners; complete one-loop electroweak mass kernels",
        "order": "one loop; inverse masses and logarithms expanded to first order",
        "log_matching_factors": {k: center(v) for k, v in shifts.items()},
        "log_matching_factor_intervals": {k: endpoints(v) for k, v in shifts.items()},
        "log_matching_components": terms_by_species,
        "log_matching_component_intervals": intervals_by_species,
        "running_masses_GeV_first_order": running,
        "charged_lepton_log_correction": center(weighted),
        "charged_lepton_log_correction_interval": endpoints(weighted),
        "pole_log_combination": center(pole_combination),
        "running_log_combination_first_order": center(pole_combination+weighted),
        "weighted_one_loop_log_scale_derivative": center(scale_derivative),
        "weighted_log_components": {k: center(v) for k, v in weighted_terms.items()},
        "weighted_log_component_intervals": {k: endpoints(v) for k, v in weighted_terms.items()},
        "finite_weak_log_correction": center(weak_weighted),
        "finite_weak_log_correction_interval": endpoints(weak_weighted),
        "common_vev_log_weight": sum(weights),
        "numerical_enclosure": "50-digit interval arithmetic; outward binary64 endpoints; fixed input floats",
        "uncomputed_orders": "two-loop electroweak and QED corrections; neutrino-mass contributions",
        "native_source_readout_identification_derived": False, "production_replacement": False,
        "references": ["S. P. Martin, Phys. Rev. D 93, 094017 (2016), Eq. (2.20); doi:10.1103/PhysRevD.93.094017",
                       "S. P. Martin, Phys. Rev. D 99, 033007 (2019), Sec. II.C, arXiv HTML Eq. (2.23); doi:10.1103/PhysRevD.99.033007"],
        "evaluation_work": {"distinct_A_values": 6, "distinct_B_values": 9,
                            "analytic_interval_B_evaluations": 9, "quadrature_integrand_evaluations": 0},
    }


def generated_on_shell_matter_matching(gauge_couplings, fermi_vev_GeV, *,
                                      top_mass_GeV, higgs_mass_GeV, scale_GeV,
                                      input_definition, action_source,
                                      fermi_matching=None):
    """One-loop EFT parameters from generated G_F, M_t and M_H conditions.

    The three supplied values define physical renormalization conditions
    of this realization: G_F=1/(sqrt(2)*v_F²) and real pole masses M_t,M_H.
    Their leading coefficients are yt0=sqrt(2)*M_t/v_F and
    lambda0=M_H²/(2*v_F²). No experimental value enters this map.
    The gauge couplings are the declared leading common-scale gauge
    boundary. Their finite input conversion enters these mass kernels
    at two loops; the finite matching here determines yt, lambda and m².

    The Fermi conversion determines v_L; the complex-pole kernels give
    the finite mass corrections. Linear inversion preserves all three
    conditions through one loop, including m²=-lambda*v_L²-Delta1/(16pi²).
    This specifies an on-shell effective realization of the generated
    readouts. Identification with the native dynamical source is a
    separate map, retained explicitly in the returned record.

    A supplied fermi_matching record is reused after checking its source,
    input identity, scale and leading coefficients. No RG solve is used.
    """
    if not isinstance(input_definition, str) or input_definition != "generated_on_shell_conditions":
        raise ValueError("input_definition must be generated_on_shell_conditions")
    gauge = np.asarray(gauge_couplings, dtype=float)
    if gauge.shape != (3,) or not np.isfinite(gauge).all() or min(gauge) < 0 or gauge[1] <= 0:
        raise ValueError("three finite gauge couplings with positive weak coupling required")
    if not all(np.isfinite(x) and x > 0 for x in (fermi_vev_GeV, top_mass_GeV, higgs_mass_GeV, scale_GeV)):
        raise ValueError("positive finite generated masses, Fermi VEV and scale required")
    if not isinstance(action_source, str) or not action_source.strip():
        raise ValueError("a nonempty action source string is required")
    v2 = float(fermi_vev_GeV)**2
    y0, lam0 = math.sqrt(2)*top_mass_GeV/fermi_vev_GeV, higgs_mass_GeV**2/(2*v2)
    leading = (*map(float, gauge), y0, lam0)
    if fermi_matching is None:
        weak = electroweak_matching_from_fermi_readout(leading, fermi_vev_GeV,
            scale_GeV=scale_GeV, input_definition="fermi_constant_readout", action_source=action_source)
    else:
        weak = fermi_matching
        if (not isinstance(weak, dict) or weak.get("input_definition") != "fermi_constant_readout"
                or weak.get("action_source") != action_source
                or weak.get("input_fermi_vev_GeV") != fermi_vev_GeV
                or weak.get("scale_GeV") != scale_GeV
                or np.shape(weak.get("leading_couplings")) != (5,)
                or not np.allclose(weak["leading_couplings"], leading, rtol=3e-14, atol=0)
                or weak.get("bottom_yukawa") != 0 or weak.get("tau_yukawa") != 0):
            raise ValueError("reused Fermi matching must have the same source, scale and leading action")
    pole = top_higgs_pole_matching_one_loop(leading, fermi_vev_GeV,
        scale_GeV=scale_GeV, vev_definition="tadpole_free_landau", action_source=action_source)
    dr = weak["delta_r_one_loop"]
    dt = pole["top_mass_correction_GeV"]
    dh2 = pole["higgs_squared_correction_GeV2"]["real"]
    dy, dl = -y0*dr/2-math.sqrt(2)*dt/fermi_vev_GeV, -lam0*dr-dh2/(2*v2)
    quadratic = -higgs_mass_GeV**2/2+dh2/2-weak["tadpole_one_loop_GeV2"]
    return {
        "input_definition": input_definition, "action_source": action_source,
        "conditions": {"fermi_vev_GeV": float(fermi_vev_GeV),
            "G_F_GeVminus2": weak["G_F_preserved_GeVminus2"],
            "top_pole_mass_GeV": float(top_mass_GeV), "higgs_pole_mass_GeV": float(higgs_mass_GeV)},
        "scale_GeV": float(scale_GeV), "scheme": "MSbar", "gauge": "Landau",
        "gauge_boundary_order": "declared leading common-scale gauge coefficients; "
                                "finite gauge-input conversion enters the mass kernels at two loops",
        "finite_matched_parameters": ["y_top", "lambda_H", "m_squared"],
        "leading_couplings": list(leading),
        "matched_couplings_first_order": [*map(float, gauge), y0+dy, lam0+dl],
        "matched_quadratic_GeV2_first_order": quadratic,
        "running_vev_GeV_first_order": weak["running_vev_GeV_first_order"],
        "running_vev_squared_GeV2_first_order": weak["running_vev_squared_GeV2_first_order"],
        "yukawa_finite_shift": dy, "quartic_finite_shift": dl,
        "fermi_conversion": weak, "pole_kernel": pole,
        "condition_residuals_GeV2_first_order": {
            "top": 2*top_mass_GeV**2*dy/y0+top_mass_GeV**2*dr+2*top_mass_GeV*dt,
            "Higgs": 2*v2*dl+higgs_mass_GeV**2*dr+dh2,
            "stationarity": quadratic+lam0*v2+v2*dl+lam0*v2*dr+weak["tadpole_one_loop_GeV2"],
        },
        "order": "one loop; all inverse matching products expanded to first order",
        "native_source_readout_identification_derived": False,
        "physical_readout_conditions": "the generated masses define real pole conditions in this effective realization",
        "production_replacement": False,
        "evaluation_work": {"fermi_kernel_calls": int(fermi_matching is None), "pole_kernel_calls": 1,
                            **pole["evaluation_work"]},
    }


def form_gram(forms, metric, coordinate_weights, *, degree):
    """L2 Gram of explicit one-forms or antisymmetric two-form components.

    metric is the covariant internal metric, possibly point dependent.
    coordinate_weights exclude sqrt(det(metric)), which is included here.
    For two-forms F_ij, the contraction is (1/2)g^ik g^jl F*_ij F_kl.
    Lie-algebra trace normalization must already be in the supplied data.
    """
    a = np.asarray(forms,dtype=complex)
    if degree not in (1,2) or a.ndim != degree+2 or not np.isfinite(a).all():
        raise ValueError("forms must have shape (points,modes,d[,d]); degree 1 or 2")
    q,_,d = a.shape[:3]
    if degree==2 and (a.shape[-1]!=d or not np.allclose(a,-a.swapaxes(-1,-2))):
        raise ValueError("two-form components must be antisymmetric")
    g = np.broadcast_to(np.asarray(metric,dtype=float),(q,d,d))
    if not np.isfinite(g).all() or not np.allclose(g,g.swapaxes(-1,-2)):
        raise ValueError("metric must be finite symmetric")
    if np.min(np.linalg.eigvalsh(g)) <= 0:
        raise ValueError("internal metric must be positive definite")
    w = _weights(coordinate_weights,q)*np.sqrt(np.linalg.det(g))
    inv = np.linalg.inv(g)
    if degree==1:
        return np.einsum('q,qia,qab,qjb->ij',w,a.conj(),inv,a)
    return np.einsum('q,qnab,qac,qbd,qmcd->nm',w,a.conj(),inv,inv,a)/2


def axial_squash_grams(s):
    """Evaluate Gram integrals for the fixed Killing vector's dual B sigma3.

    A=1+s, B=1-2s. Its internal curvature d(alpha_s)=B d(sigma3)
    and external-amplitude kinetic form alpha_s have different norms.
    Constant Maurer--Cartan, covering and generator-trace factors cancel
    against the round metric. This is a geometric computation, not an EFT
    coupling inferred by imposing a desired final normalization.
    """
    if not np.isfinite(s) or not -1 < s < .5:
        raise ValueError("positive squash metric requires -1 < s < 1/2")
    A,B = 1+s,1-2*s
    metric = np.diag([A,A,B])
    alpha = np.array([[[0,0,B]]],dtype=float)
    curvature = np.zeros((1,1,3,3))
    curvature[0,0,0,1],curvature[0,0,1,0] = B,-B
    one = float(form_gram(alpha,metric,[1],degree=1)[0,0].real)
    two = float(form_gram(curvature,metric,[1],degree=2)[0,0].real)
    return {"oneform_gram_ratio":one,"curvature_gram_ratio":two,
            "curvature_preserving_amplitude":1/np.sqrt(two),
            "fixed_axis_matter_profile":B/np.sqrt(two),
            "unit_axis_matter_profile":np.sqrt(B/two)}


def evaluate_matter_extensions(records):
    """JSON-ready, store-free evaluation of explicit matter extension cases.

    records maps parameter names to current records with a 'value' field,
    or directly to numerical values. Record metadata is not a substitute for
    a physical matching proof. Conditional examples are returned separately
    from production readouts; this function writes no prediction or file.
    Every reported verification is evaluated, and failure raises an error.
    """
    import math
    from cg_core.content_response import (
        interacting_content_response, weighted_content_response,log_partition_response,
    )
    from cg_core.gauge_running import CoupledBoundary,coupled_run,coupled_common_origin
    from cg_core.native_matter_matching import evaluate_native_matching
    from cg_frg.cosmology.thermal_weak import (
        WeakInputs,weak_rates,zero_temperature_lifetime,evolve_neutron_fraction,
    )
    from cg_frg.cosmology.bbn_helium import beta_phase_space
    from cg_frg.cosmology.reaction_network import Nuclide,NuclearReaction,ReactionNetwork
    from cg_frg.cosmology.cold_source import evaluate_cold_transport
    def value(name):
        record=records[name]
        result=float(record['value'] if isinstance(record,dict) else record)
        if not math.isfinite(result):
            raise ValueError(f"nonfinite current record {name}")
        return result
    def require(condition,label):
        if not condition:
            raise ArithmeticError("matter extension verification failed: "+label)
    finite=interacting_content_response()
    weighted=weighted_content_response(1.17,1)
    noncommuting=log_partition_response(np.diag([2.3,-2.3]),[np.array([[0,1],[1,0]])])
    km_residual=float(noncommuting['hessian'][0,0]-math.tanh(2.3)/2.3)
    require(abs(km_residual)<1e-13,'noncommuting two-level Hessian')
    require(abs(finite['tau_response']-.02)<1e-13,'zero-background tau')
    require(abs(weighted['tau_response']-(8*1.17-7)/(10*1.17+40))<1e-13,'unequal-weight tau')
    up_index, down_index, cmb_window = value('alpha_up'), value('alpha_down'), value('kL_CMB')
    transfers = {'up': [1., math.exp(-2*up_index), .25*math.exp(-2*up_index-2*cmb_window)],
                 'down': [1., math.exp(-2*down_index),
                          math.exp(-2*down_index-2*(down_index-cmb_window/6))]}
    torsion=value('tau')
    squash=math.sqrt((1+2*torsion)/(1-4*torsion)**2.5)
    vus=math.sqrt(value('md_over_ms_geo'))
    vcb=.5*math.exp(-up_index)*(1-2*torsion*squash)
    vub=.5*math.exp(-2*up_index)*(1+torsion*squash)
    cosine13=math.sqrt(1-vub*vub)
    native=evaluate_native_matching(quartic_coefficient=value('lambda_H_pseudo'),
        family_transfers=transfers,
        family_angular_data={'angular_sines': [vus/cosine13, vcb/cosine13, vub],
                             'phase':value('ckm_delta_direction'),
                             'down_coefficient':value('y_b_over_y_t')})
    native['squash_grams']={k:float(v) for k,v in axial_squash_grams(2*value('tau')).items()}
    # Reconstruct the same leading gauge readouts algebraically at M_Z.
    # This Fermi-input conversion uses no additional RG evolution.
    fermi_inputs={name:value(name) for name in (
        'M_Z_pred','s2_thetaW_MZ','v_HIGGS','y_top_base',
        'lambda_H_pseudo','alpha_s_MZ_pred')}
    require(fermi_inputs['M_Z_pred']>0 and fermi_inputs['v_HIGGS']>0
            and 0<fermi_inputs['s2_thetaW_MZ']<1
            and fermi_inputs['alpha_s_MZ_pred']>=0,
            'positive generated weak scales and gauge readouts')
    gauge_sum=4*fermi_inputs['M_Z_pred']**2/fermi_inputs['v_HIGGS']**2
    weak_fraction=fermi_inputs['s2_thetaW_MZ']
    leading_couplings=(math.sqrt(5*weak_fraction*gauge_sum/3),
        math.sqrt((1-weak_fraction)*gauge_sum),
        math.sqrt(4*math.pi*fermi_inputs['alpha_s_MZ_pred']),
        fermi_inputs['y_top_base'],fermi_inputs['lambda_H_pseudo'])
    fermi_match=electroweak_matching_from_fermi_readout(
        leading_couplings, fermi_inputs['v_HIGGS'],
        scale_GeV=fermi_inputs['M_Z_pred'],
        input_definition='fermi_constant_readout',
        action_source='same generated weak-input and leading gauge, unit-connector '
                      'and Higgs-quartic readouts in the five-coupling effective action')
    require(abs((1+fermi_match['delta_r_one_loop'])/
        (math.sqrt(2)*fermi_match['running_vev_squared_GeV2_first_order'])/
        fermi_match['G_F_preserved_GeVminus2']-1)<1e-13,
        'generated Fermi-input preservation')
    on_shell_match=generated_on_shell_matter_matching(leading_couplings[:3],
        fermi_inputs['v_HIGGS'], top_mass_GeV=value('m_t_pred'),
        higgs_mass_GeV=value('m_H_pred'), scale_GeV=fermi_inputs['M_Z_pred'],
        input_definition='generated_on_shell_conditions',
        action_source=fermi_match['action_source'], fermi_matching=fermi_match)
    on_shell_match['strong_input_definition']=(
        'generated five-flavour MSbar alpha_s at M_Z, used as the leading strong coefficient; '
        'five-to-six-flavour threshold matching enters the mass kernels at two loops')
    require(max(abs(x) for x in on_shell_match['condition_residuals_GeV2_first_order'].values())<1e-8,
            'same-action generated on-shell conditions through one loop')
    lepton_match = charged_lepton_pole_matching_one_loop(
        {'electron': value('m_e_pred')/1000, 'muon': value('m_mu_pred'),
         'tau': value('m_tau_pred')}, leading_couplings[:2], fermi_inputs['v_HIGGS'],
        higgs_mass_GeV=value('m_H_pred'), scale_GeV=fermi_inputs['M_Z_pred'],
        input_definition='generated_on_shell_conditions',
        action_source=fermi_match['action_source'])
    require(lepton_match['charged_lepton_log_correction_interval'][0]
            <= lepton_match['charged_lepton_log_correction']
            <= lepton_match['charged_lepton_log_correction_interval'][1],
            'generated lepton matching numerical enclosure')
    # These assignments define a conditional numerical EFT boundary only.
    # The finite seed and constitutive quartic are not promoted to matched
    # physical MSbar inputs by this calculation.
    boundary_values=(value('g1_MG_geo'),value('g2_MG'),value('g3_MG_geo'),
                     native['constant_connector']['canonical_yukawa_singular_value'],
                     native['constant_connector']['canonical_quartic'])
    scale=value('M_G')
    source=('conditional constant-profile RP3 action: unit finite connector and unit kinetic '
            'coefficients, current gauge readouts and declared constitutive quartic assigned in MSbar')
    boundary=CoupledBoundary(boundary_values,scale,'MSbar',source)
    low=value('k_GUT')
    shooting=coupled_common_origin(boundary,low)
    boundary=CoupledBoundary(shooting['initial_couplings'],scale,'MSbar',source)
    run=coupled_run(boundary,low)
    half=coupled_run(boundary,math.sqrt(scale*low))
    two=coupled_run(CoupledBoundary(half['couplings'],half['scale'],'MSbar',source),low)
    rg_residual=float(np.max(np.abs(np.array(run['couplings'])-two['couplings'])))
    require(rg_residual<1e-9,'joint-flow semigroup check')
    require(abs(shooting['relative_residual'])<2e-11,'joint common-origin boundary')
    infrared=coupled_run(boundary,value('M_Z_pred'))
    infrared_refined=coupled_run(boundary,value('M_Z_pred'),rtol=2e-12,atol=2e-14,max_step=.075)
    infrared_error=float(np.max(np.abs(np.array(infrared['couplings'])-infrared_refined['couplings'])))
    require(infrared_error<1e-9,'low-scale joint-flow refinement')
    infrared_masses=tree_mass_parameters(infrared_refined['couplings'],value('v_HIGGS'),
        scale_GeV=infrared_refined['scale'],coupling_scheme=infrared_refined['scheme'],
        vev_definition='fixed window VEV used in a tree-level broken-phase conversion')
    electroweak_match=electroweak_matching_one_loop(infrared_refined['couplings'],
        value('v_HIGGS'), scale_GeV=infrared_refined['scale'],
        vev_definition='tree_minimum',
        action_source='same conditional canonical five-coupling action at the low scale; '
                      'window VEV assigned as the tree minimum m2=-lambda*v_window^2')
    qcd_action_match=qcd_mass_matching_one_loop(infrared_masses['m_top_tree_GeV'],
        infrared_refined['couplings'][2]**2/(4*math.pi),
        scale_GeV=infrared_refined['scale'], input_definition='MSbar',
        boundary_source='QCD running mass of the specified conditional broken-phase action; '
                        'fixed window VEV, independently supplied canonical boundary')
    # The current heavy readouts set reference scales for the finite kernel.
    # Their relation m_MSbar(mu_Q)=z_Q*m_geo still requires action matching.
    # A fixed nf=5 mass-independent QCD coupling is used here; no threshold
    # identification or replacement of a geometric production mass is made.
    from scipy.integrate import solve_ivp
    heavy_references={'top': value('m_t_pred'), 'bottom': value('m_b_pred'),
                      'charm': value('m_t_pred')/value('m_t_over_m_c')}
    heavy_kernels={}
    for flavour, reference in heavy_references.items():
        alpha_start=value('alpha_s_MZ_pred')
        def qcd_rhs(t, y):
            return [-(23/3)*y[0]**2/(2*math.pi)-(116/3)*y[0]**3/(8*math.pi**2)]
        evolved=solve_ivp(qcd_rhs, (math.log(value('M_Z_pred')), math.log(reference)),
                         [alpha_start], method='DOP853', rtol=2e-11, atol=2e-13)
        require(evolved.success and evolved.y[0,-1]>0, 'QCD reference-scale evolution')
        coupling=float(evolved.y[0,-1])
        kernel=qcd_mass_matching_one_loop(reference, coupling, scale_GeV=reference,
            input_definition='MSbar', boundary_source='auxiliary mass equal to the reference scale; '
            'used to evaluate the universal self-energy coefficient, not identify the production mass')
        heavy_kernels[flavour]={'geometric_readout_GeV': reference,
            'reference_scale_GeV': reference, 'alpha_s_MSbar_nf5': coupling,
            'coefficient_a': kernel['colour_C_F']*coupling/(4*math.pi),
            'finite_term_at_z1': kernel['relative_one_loop_term'],
            'native_bridge_z': None, 'physical_matched_mass_GeV': None}
    tau=value('tau')
    inputs=WeakInputs(1/(math.sqrt(2)*value('v_HIGGS')**2),
        math.sqrt(1-value('V_us_geo')**2),4/math.pi,value('m_e_pred')*1e-3,
        value('bbn_dm_np'),value('alpha_em_0_pred'),1+(1-tau)/(8*math.pi),
        'current V5 EW, mass-splitting and specified hadronic readouts')
    Tcheck=.0007
    rates=weak_rates(inputs,Tcheck)
    equilibrium=math.exp(-inputs.neutron_proton_split/Tcheck)
    balance_residual=rates['p_to_n']/rates['n_to_p']/equilibrium-1
    require(abs(balance_residual)<2e-7,'weak detailed balance')
    phase_space = beta_phase_space(inputs.neutron_proton_split,
                                  inputs.electron_mass, inputs.alpha_em)
    lifetime = zero_temperature_lifetime(inputs)
    require(abs(lifetime/value('bbn_tau_n')-1)<2e-10,
            'same-input free decay and production lifetime')
    thermal=evolve_neutron_fraction(inputs,.002,.0005,
        reduced_planck_mass=value('M_P'),neutrino_species=value('bbn_Neff'),
        decoupling_temperature=.0012,rtol=2e-5)
    require(0<thermal['neutron_fraction']<.5 and thermal['elapsed_seconds']>0,
            'continuous neutron evolution bounds')
    nuclei=(Nuclide('n',1,0),Nuclide('p',1,1),Nuclide('D',2,1))
    reaction=NuclearReaction((1,1,0),(0,0,1),lambda T:1e-20,
        'specified constant-rate mathematical example, not nuclear cross-section data',
        (1e-5,1e-3),'conditional n+p capture')
    network=ReactionNetwork(nuclei,[reaction])
    evolution=network.evolve([.5,.5,0],(0,2),lambda t:(.0001,1e20))
    network_error=float(np.max(np.abs(evolution['abundances'][:,-1]-.25)))
    require(network_error<1e-7 and evolution['baryon_conservation_residual']<1e-10,
            'conditional nuclear capture and baryon conservation')
    return {
        'finite_source':{'scope':'same finite carrier; explicit backgrounds, not kinetic coefficients',
            'inputs':{'left_weight':1.17,'right_weight':1.0,'two_level_background':2.3},
            'tau_zero':finite['tau_response'],'tau_weighted':weighted['tau_response'],
            'noncommuting_hessian':float(noncommuting['hessian'][0,0]),
            'analytic_hessian_residual':km_residual},
        'spatial_matching':native,
        'electroweak_finite_matching':{
            'scope':'one-loop VEV and weak matching with explicit Fermi-input and tree-minimum conventions',
            'generated_fermi_readout':fermi_match,
            'generated_on_shell_realization':on_shell_match,
            'generated_charged_lepton_realization':lepton_match,
            'generated_readout_inputs':fermi_inputs,
            'fermi_input_reuse':'stored weak, gauge and matter readouts; no additional RG evolution',
            'conditional_action':electroweak_match,
            'input_reuse':'already computed infrared_refined state and fixed window VEV',
            'physical_native_boundary_identified':False,
            'production_replacement':False},
        'qcd_finite_mass_matching':{
            'scope':'one-loop fundamental-SU(3) self-energy with explicit mass and VEV conventions',
            'conditional_action_top':qcd_action_match,
            'production_heavy_kernel':heavy_kernels,
            'kernel_coupling_convention':'fixed nf=5 MSbar QCD, two-loop scale evolution from the declared production alpha_s boundary',
            'native_bridge_definition':'m_MSbar(mu_Q)=z_Q*m_geometric, mu_Q=m_geometric',
            'forward_equation':'M_Q/m_geometric=z_Q*[1+a_Q*(4-6*log(z_Q))]+O(alpha_s^2)',
            'physical_native_boundary_identified':False,
            'production_replacement':False},
        'cold_source_transport':evaluate_cold_transport(),
        'coupled_rg':{'scope':'actual jointly solved conditional MSbar boundary and full five-variable propagation',
            'inputs':{'couplings':list(boundary.values),'scale_GeV':scale,'scheme':'MSbar',
                      'thresholds':[],'physical_matter_matching_established':False},
            'couplings_at_scale_to':list(run['couplings']),'scale_to_GeV':low,
            'semigroup_residual':rg_residual,
            'shooting':shooting,
            'common_origin_boundary_residual':float(shooting['residual']),
            'boundary_equation':'g3(k_GUT)-g2(k_GUT)*(1+alpha2(k_GUT)^2/(8/3))',
            'boundary_residual_required_to_vanish':True,
            'low_scale_propagation':{'scale_GeV':infrared_refined['scale'],
                'couplings':list(infrared_refined['couplings']),
                'scheme':'MSbar','content':'full SM top-sector truncation without threshold decoupling',
                'max_refinement_difference':infrared_error,
                'tree_mass_parameters':infrared_masses,
                'finite_fixed_y0_compensation_applied':False,
                'production_replacement':False}},
        'thermal_weak':{'scope':'same specified weak inputs; static-nucleon rates and instantaneous neutrino decoupling',
            'inputs':{**inputs.__dict__,'Ti_GeV':.002,'Tf_GeV':.0005,'Tdec_GeV':.0012,
                      'neutrino_species':value('bbn_Neff'),'reduced_planck_mass_GeV':value('M_P')},
            'zero_temperature_lifetime_s':lifetime,
            'beta_phase_space':phase_space,
            'detailed_balance_relative_residual':balance_residual,
            'detailed_balance_temperature_GeV':Tcheck,
            'neutron_fraction_final':thermal['neutron_fraction'],
            'elapsed_seconds':thermal['elapsed_seconds'],
            'Tnu_final_GeV':thermal['neutrino_temperature'],'helium_yield_computed':False,
            'evaluation_work':thermal['evaluation_work']},
        'nuclear_network':{'scope':'sourced conditional mass-action example; no physical nuclear rate table supplied',
            'inputs':{'coefficient_cm3_per_s':1e-20,'baryon_density_cm3':1e20,
                      'temperature_GeV':.0001,'initial_abundances':[.5,.5,0],'time_seconds':[0,2]},
            'final_abundances':evolution['abundances'][:,-1].tolist(),
            'analytic_solution_residual':network_error,
            'baryon_conservation_residual':evolution['baryon_conservation_residual']},
        'checks_passed':True}
