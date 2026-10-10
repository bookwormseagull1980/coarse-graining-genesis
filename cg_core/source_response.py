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

"""Finite same-source responses, exact elimination and critical residues.

The caller supplies a residual E(X,h,z)=0 and observation O(X,h,z), or
their derivatives. Physical interpretation specifies the generating action,
external momentum, spectral representation and physical source space.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from numbers import Integral
import numpy as np
from scipy.linalg import null_space


def _matrix(value, name):
    value = np.asarray(value, dtype=complex)
    if value.ndim != 2 or not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be a finite matrix")
    return value


def _hermitian(value, name):
    value = _matrix(value, name)
    if value.shape[0] != value.shape[1]:
        raise ValueError(f"{name} must be Hermitian")
    scale = float(np.max(np.abs(value), initial=0.))
    if np.max(np.abs(value-value.conj().T), initial=0.) > 1e-12*scale:
        raise ValueError(f"{name} must be Hermitian")
    return value


@dataclass(frozen=True)
class SourceResponse:
    """L=E_X, S=-E_h, R=O_X, D=O_h in one declared source convention.

    R is the analytic row map of the stated observation. Reciprocity gives
    R=S* when the source and observation use the corresponding Hilbert pairing.
    Source-dependent direct and eliminated-sector terms enter the full response.
    """
    L: np.ndarray
    S: np.ndarray
    R: np.ndarray
    D: np.ndarray

    def __post_init__(self):
        for key in ("L", "S", "R", "D"):
            object.__setattr__(self, key, _matrix(getattr(self, key), key).copy())
        n = self.L.shape[0]
        if (self.L.shape != (n, n) or self.S.shape[0] != n
                or self.R.shape[1] != n
                or self.D.shape != (self.R.shape[0], self.S.shape[1])):
            raise ValueError("incompatible state, source and readout dimensions")

    def evaluate(self):
        """Evaluate D+R L^-1 S on the domain where L is invertible."""
        solution = np.linalg.solve(self.L, self.S)
        return self.D + self.R @ solution


def differentiate_response(residual, observation, state, source, z=0., *,
                           step=1e-5, residual_tolerance=1e-10):
    """Central differences at a supplied solved branch.

    State and source coordinates are real. Outputs may be complex. The caller
    compares step sizes to assess the derivative approximation. Interval
    certification uses separate enclosures. z is the supplied response variable.
    """
    x, h = np.asarray(state, dtype=float), np.asarray(source, dtype=float)
    if (x.ndim != 1 or h.ndim != 1 or not np.all(np.isfinite(x))
            or not np.all(np.isfinite(h)) or not np.isfinite(step) or step <= 0
            or not np.isfinite(residual_tolerance) or residual_tolerance < 0):
        raise ValueError("finite vectors, positive step and nonnegative tolerance required")
    def vector(fn, a, b):
        value = np.atleast_1d(np.asarray(fn(a, b, z), dtype=complex))
        if value.ndim != 1 or not np.all(np.isfinite(value)):
            raise ValueError("residual and observation must return finite vectors")
        return value
    e = vector(residual, x, h)
    if e.shape != x.shape or np.linalg.norm(e, ord=np.inf) > residual_tolerance:
        raise ValueError("state is not a solved residual branch")
    def derivative(fn, coordinate):
        v = x if coordinate == 0 else h
        cols = []
        for i in range(len(v)):
            delta = step * max(1., abs(v[i]))
            plus, minus = v.copy(), v.copy()
            plus[i] += delta
            minus[i] -= delta
            a = vector(fn, plus, h) if coordinate == 0 else vector(fn, x, plus)
            b = vector(fn, minus, h) if coordinate == 0 else vector(fn, x, minus)
            cols.append((a-b)/(2*delta))
        return np.column_stack(cols) if cols else np.empty((len(vector(fn, x, h)), 0))
    return SourceResponse(derivative(residual, 0), -derivative(residual, 1),
                          derivative(observation, 0), derivative(observation, 1))


def schur_reduce(data: SourceResponse, retained):
    """Eliminate an invertible complementary block, transforming all four maps."""
    ids = np.asarray(retained)
    n = data.L.shape[0]
    if (ids.ndim != 1 or not np.issubdtype(ids.dtype, np.integer)
            or len(np.unique(ids)) != len(ids) or np.any(ids < 0) or np.any(ids >= n)
            or len(ids) == 0):
        raise ValueError("retained must be distinct nonempty state indices")
    other = np.setdiff1d(np.arange(n), ids)
    rr = data.L[np.ix_(ids, ids)]
    if len(other) == 0:
        return SourceResponse(rr, data.S[ids], data.R[:, ids], data.D)
    re, er, ee = (data.L[np.ix_(ids, other)], data.L[np.ix_(other, ids)],
                  data.L[np.ix_(other, other)])
    feedback, forcing = np.linalg.solve(ee, er), np.linalg.solve(ee, data.S[other])
    return SourceResponse(rr-re@feedback, data.S[ids]-re@forcing,
                          data.R[:, ids]-data.R[:, other]@feedback,
                          data.D+data.R[:, other]@forcing)


def restrict_variational_constraints(data: SourceResponse, constraint):
    """Restrict a variational system to a source-independent constraint C X=0.

    Returns (reduced tuple, orthonormal null-space basis). This is equivalent
    to eliminating Lagrange multipliers in [L,C*;C,0], with source (S,0).
    Inhomogeneous/source-dependent constraints need their own affine source
    and direct terms and are deliberately not represented by this interface.
    """
    c = _matrix(constraint, "constraint")
    if c.shape[1] != data.L.shape[0]:
        raise ValueError("constraint has wrong state dimension")
    basis = null_space(c)
    if basis.shape[1] == 0:
        raise ValueError("constraint removes every state direction")
    return SourceResponse(basis.conj().T@data.L@basis, basis.conj().T@data.S,
                          data.R@basis, data.D), basis


def critical_residue(H, K, source, *, zero_tolerance=1e-11):
    """Finite Hermitian affine response S* (H+zK)^-1 S near z=0.

    The relative eigenvalue threshold defines a candidate critical subspace,
    on which K has positive compression. Exact kernel certification uses
    certify_affine_residue. A positive Stieltjes representation additionally
    requires K > 0 on the full space; this numerical condition is reported.
    Physical atom identification uses the corresponding spectral realisation.
    """
    H, K, s = _hermitian(H, "H"), _hermitian(K, "K"), _matrix(source, "source")
    if H.shape != K.shape or s.shape[0] != H.shape[0] or H.shape[0] == 0 or s.shape[1] == 0:
        raise ValueError("incompatible matrix dimensions")
    if not np.isfinite(zero_tolerance) or zero_tolerance <= 0:
        raise ValueError("positive finite zero tolerance required")
    eigenvalues, modes = np.linalg.eigh(H)
    # Relative thresholds respect changes of state/source units. An exactly
    # zero H has threshold zero and its entire space is the declared kernel.
    threshold = zero_tolerance * np.linalg.norm(H, ord=2)
    slope_threshold = zero_tolerance * np.linalg.norm(K, ord=2)
    if np.min(eigenvalues) < -threshold:
        raise ValueError("H is not nonnegative within the declared tolerance")
    kernel = modes[:, np.abs(eigenvalues) <= threshold]
    overlap = kernel.conj().T @ s
    if kernel.shape[1]:
        slope = kernel.conj().T @ K @ kernel
        slope_eigenvalues = np.linalg.eigvalsh(slope)
        if np.min(slope_eigenvalues) <= slope_threshold:
            raise ValueError("critical slope must be strictly positive")
        residue = overlap.conj().T @ np.linalg.solve(slope, overlap)
    else:
        slope = np.empty((0, 0), complex)
        residue = np.zeros((s.shape[1], s.shape[1]), complex)
    positive = eigenvalues[eigenvalues > threshold]
    return {"residue": residue, "kernel_basis": kernel, "critical_slope": slope,
            "classification": "floating_point_candidate",
            "exact_zero_certified": False,
            "algebraic_pole_established": False,
            "kernel_dimension": kernel.shape[1],
            "visible_rank": int(np.linalg.matrix_rank(
                overlap, tol=zero_tolerance*np.linalg.norm(s, ord=2))),
            "complement_gap": float(positive.min()) if len(positive) else None,
            "kernel_tolerance": float(threshold),
            "kernel_residual_norm": float(np.linalg.norm(H@kernel)),
            # The finite affine measure requires H >= 0 and K > 0.
            "positive_affine_measure": bool(np.min(eigenvalues) >= 0 and
                np.min(np.linalg.eigvalsh(K)) > slope_threshold),
            "physical_atom_established": False}


def _rational_matrix(value, name):
    a = np.asarray(value, dtype=object)
    if a.ndim != 2:
        raise ValueError(f"{name} must be a rational matrix")
    result = np.empty(a.shape, dtype=object)
    for index, item in np.ndenumerate(a):
        if isinstance(item, bool):
            raise TypeError("booleans are not rational coefficients")
        if isinstance(item, Fraction):
            result[index] = item
        elif isinstance(item, Integral):
            result[index] = Fraction(int(item))
        elif isinstance(item, str):
            result[index] = Fraction(item)
        else:
            raise TypeError("exact coefficients require integers, Fraction or rational strings; floats are rejected")
    return result


def _rational_rref(a):
    """Exact elimination; pivot decisions never use a numerical tolerance."""
    a = a.copy()
    row, pivots = 0, []
    for col in range(a.shape[1]):
        pivot = next((i for i in range(row, a.shape[0]) if a[i, col] != 0), None)
        if pivot is None:
            continue
        a[[row, pivot]] = a[[pivot, row]]
        a[row] = a[row] / a[row, col]
        for i in range(a.shape[0]):
            if i != row and a[i, col] != 0:
                a[i] = a[i] - a[i, col] * a[row]
        pivots.append(col)
        row += 1
        if row == a.shape[0]:
            break
    return a, pivots


def _rational_positive_pivots(a):
    """Positive Schur pivots certify a symmetric matrix is positive definite."""
    a = a.copy()
    pivots = []
    for i in range(len(a)):
        pivot = a[i, i]
        if pivot <= 0:
            return None
        pivots.append(pivot)
        if i + 1 < len(a):
            v = a[i+1:, i].copy()
            a[i+1:, i+1:] -= np.outer(v, v) / pivot
    return tuple(pivots)


def _rational_solve(a, b):
    n = len(a)
    reduced, pivots = _rational_rref(np.concatenate((a, b), axis=1))
    if pivots[:n] != list(range(n)):
        raise ValueError("exact complementary operator is singular")
    return reduced[:, n:]


def certify_affine_residue(H, K, source):
    """Certify the zero-pole coefficient of supplied real rational matrices.

    The response is S.T (H+z K)^-1 S. Exact elimination checks H >= 0,
    the full kernel, and positivity of K on that kernel. With a rational
    kernel basis N (no orthogonalization), the coefficient is
    S.T N (N.T K N)^-1 N.T S. A finite complementary gap is certified too.
    Coefficients are supplied as integers, Fraction or rational strings.
    The certificate concerns those exact finite matrices. A physical tensor
    realisation supplies the generating action, external momentum, physical
    polarizations, spectral measure and source identification.
    """
    H, K, s = (_rational_matrix(H, "H"), _rational_matrix(K, "K"),
               _rational_matrix(source, "source"))
    n = H.shape[0]
    if n == 0 or H.shape != (n, n) or K.shape != H.shape or s.shape[0] != n or s.shape[1] == 0:
        raise ValueError("incompatible matrix dimensions")
    if not np.array_equal(H, H.T) or not np.array_equal(K, K.T):
        raise ValueError("H and K must be exactly symmetric")
    reduced, pivots = _rational_rref(H)
    free = [i for i in range(n) if i not in pivots]
    N = np.full((n, len(free)), Fraction(0), dtype=object)
    for j, col in enumerate(free):
        N[col, j] = Fraction(1)
        for i, pivot in enumerate(pivots):
            N[pivot, j] = -reduced[i, col]
    # Pivot coordinate vectors complement the kernel. Congruence gives
    # diag(0,H[pivots,pivots]); positive Schur pivots therefore certify H >= 0.
    positive_pivots = _rational_positive_pivots(H[np.ix_(pivots, pivots)])
    if positive_pivots is None:
        raise ValueError("H is not exactly nonnegative")
    slope = N.T @ K @ N
    slope_pivots = _rational_positive_pivots(slope)
    if slope_pivots is None:
        raise ValueError("critical slope must be exactly strictly positive")
    overlap = N.T @ s
    if free:
        residue = overlap.T @ _rational_solve(slope, overlap)
        visible_rank = len(_rational_rref(overlap)[1])
    else:
        residue = np.full((s.shape[1], s.shape[1]), Fraction(0), dtype=object)
        visible_rank = 0
    gap = None
    if pivots:
        C = H[:, pivots]
        inverse_moment = _rational_solve(C.T @ H @ C, C.T @ C)
        gap = Fraction(1) / sum(inverse_moment[i, i] for i in range(len(pivots)))
    return {"classification": "exact_rational_affine_certificate",
            "kernel_basis": N, "kernel_dimension": len(free),
            "kernel_identity_verified": bool(np.all(H @ N == 0)),
            "exact_zero_certified": bool(free), "visible_rank": visible_rank,
            "critical_slope": slope, "positive_H_pivots": positive_pivots,
            "positive_slope_pivots": slope_pivots,
            "complement_gap_lower_bound": gap, "residue": residue,
            "algebraic_pole_established": visible_rank > 0,
            "finite_positive_measure_certified": _rational_positive_pivots(K) is not None,
            "physical_atom_established": False}


def evaluate_endpoint_response(tau, response_radius):
    """Actual endpoint feedback into the hierarchy, without writing records.

    The additive source h changes the existing torsion coordinate tau+h.
    Matter content and the reference projection stay fixed, with the stated
    finite Gaussian response domain. The state is c=kL; the observation is
    ln(v/M_P) from the existing hierarchy readout. Neither this source nor
    the state derivative is identified with external TT momentum.

    A_R is computed from the production spectral sum. Independent nearby
    endpoints are solved using the full scaled spectral response. Step
    agreement checks numerical consistency; certified uncertainties use
    the independent spectral and derivative enclosures.
    """
    import math
    from functools import lru_cache
    from scipy.optimize import brentq
    from cg_core.joint_response import evaluate as hierarchy
    from cg_core.window_weights import ResponseDomain
    from cg_frg.frg.spectral_sum import channel_tmunu_spin2
    from cg_frg.frg.endpoint_constraint import CRIT

    if not np.isfinite(tau) or not 0 < tau < 0.25:
        raise ValueError("torsion probe requires 0 < tau < 1/4")
    domain = ResponseDomain(response_radius, "fixed")

    @lru_cache(maxsize=None)
    def coefficient(t):
        return channel_tmunu_spin2(1., math.pi, t, domain=domain)["rp3_pi0"]/32

    coefficient_centre = coefficient(float(tau))
    c = coefficient_centre/CRIT
    hierarchy(c, tau, 1.)  # Check the same positive hierarchy branch.

    def residual(state, source, z):
        return np.array([coefficient(float(tau+source[0]))/state[0]-CRIT])

    def observation(state, source, z):
        return np.array([math.log(hierarchy(state[0], tau+source[0], 1.)["v_HIGGS"])])

    def scaled_residual(state, t):
        value = channel_tmunu_spin2(state, math.pi/state**2, t, domain=domain)
        return state**3*value["rp3_pi0"]/32-CRIT

    checks = []
    step_scale = min(1., tau/0.002)
    for step in (1e-4*step_scale, 1e-5*step_scale, 1e-6*step_scale):
        data = differentiate_response(residual, observation, [c], [0.], step=step)
        nearby = [brentq(lambda state: scaled_residual(state, tau+h),
                         c/2, 2*c, xtol=1e-13, rtol=2e-14) for h in (step, -step)]
        measured = float((observation([nearby[0]], [step], 0.)[0]
                          -observation([nearby[1]], [-step], 0.)[0])/(2*step))
        response = float(data.evaluate()[0, 0].real)
        error = abs(response-measured)/max(1., abs(measured))
        root_error = max(abs(scaled_residual(state, tau+h))
                         for state, h in zip(nearby, (step, -step)))
        checks.append({"step": step, "L": float(data.L[0, 0].real),
                       "S": float(data.S[0, 0].real), "R": float(data.R[0, 0].real),
                       "D": float(data.D[0, 0].real), "response": response,
                       "resolved_branch_derivative": measured,
                       "relative_derivative_residual": error,
                       "endpoint_residual": root_error,
                       "passed": bool(error < 1e-6 and root_error < 1e-11)})
    step_spread = max(abs(row["response"]-checks[1]["response"])
                      for row in checks)/max(1., abs(checks[1]["response"]))
    return {"scope": "native fixed-domain endpoint feedback into the hierarchy",
            "source": "additive dimensionless torsion probe h: tau -> tau+h",
            "state": "c=kL", "observation": "ln(v/M_P)",
            "response_domain": {"radius": domain.radius, "projection": domain.projection},
            "tau": float(tau), "endpoint": float(c), "coefficient_A": coefficient_centre,
            "residual_definition": "E(c,h)=A_R(tau+h)/c-4/27",
            "response_definition": "d ln(v/M_P)/dh=D+R L^-1 S",
            "checks": checks, "step_relative_spread": float(step_spread),
            "physical_atom_established": False,
            "passed": bool(all(row["passed"] for row in checks) and step_spread < 1e-5)}


def evaluate_bandwidth_response(radii=(5.,6.,20.), tau=0.02, *, certify_platform=True):
    """Joint mass response to a finite Gaussian measurement bandwidth.

    The source, three-copy content, Planck anchor and transfer coefficients
    remain fixed. Each distinct radius uses one production spectral sum;
    c_R=27 A_R/4 eliminates an iterative endpoint solve. The derivative is
    the analytic boundary term, evaluated away from shell thresholds.
    """
    import math
    from cg_core.joint_response import evaluate as hierarchy
    from cg_core.spectrum_loop import iter_sm_spectrum
    from cg_core.window_weights import ResponseDomain
    from cg_frg.frg.spectral_sum import channel_tmunu_spin2, _w_tmunu_spin2
    from cg_frg.generation.spectral_certificate import certify_bandwidth_platform

    radii = tuple(float(radius) for radius in radii)
    if not radii or not math.isfinite(tau) or not 0 < tau < .25:
        raise ValueError("nonempty positive finite bandwidths and 0<tau<1/4 required")
    for radius in radii:
        ResponseDomain(radius)
    cache = {}
    boundary_terms = 0
    quadrature_integrals = 0
    for radius in dict.fromkeys((5.,*radii)):
        domain = ResponseDomain(radius)
        coefficient = channel_tmunu_spin2(1.,math.pi,tau,domain=domain)["rp3_pi0"]/32
        endpoint = 27*coefficient/4
        edge = radius*math.pi
        # Inspect the edge shell too, even though its integral is zero.
        inspection = ResponseDomain(radius+32*np.finfo(float).eps*max(1.,radius))
        terms = []
        threshold = False
        for kind,name,_,a,b,deg in iter_sm_spectrum(1.,math.sqrt(math.pi),tau,domain=inspection):
            weight = deg*_w_tmunu_spin2(kind,name)
            if weight == 0:
                continue
            gap = edge-a
            if abs(gap) <= 16*np.finfo(float).eps*max(1.,edge):
                threshold = True
            elif gap > 0:
                terms.append(weight/math.sqrt(gap)*(edge/(edge+b))**2)
            if gap > 0:
                quadrature_integrals += 1
        boundary_terms += len(terms)
        derivative = None if threshold else math.exp(-radius)/(64*math.pi**2)*math.fsum(terms)
        cache[radius] = {"radius": radius, "coefficient_A": coefficient,
                         "endpoint": endpoint, "capacity": endpoint**2,
                         "coefficient_radius_derivative": derivative,
                         "endpoint_radius_derivative": None if derivative is None else 27*derivative/4,
                         "derivative_status": "shell threshold" if threshold else "regular",
                         "hierarchy": hierarchy(endpoint,tau,1.)}
    base = cache[5.]
    result_rows = []
    for radius in radii:
        row = cache[radius]
        values = row["hierarchy"]
        v_ratio = values["v_HIGGS"]/base["hierarchy"]["v_HIGGS"]
        electron_ratio = values["m_e_pred"]/base["hierarchy"]["m_e_pred"]
        eliminated = base["endpoint"]/row["endpoint"]*electron_ratio**(math.pi/5)
        result_rows.append({k:v for k,v in row.items() if k != "hierarchy"} | {
            "v_over_reference": v_ratio, "electron_over_reference": electron_ratio,
            "mass_elimination_relative_residual": v_ratio/eliminated-1})
    certificate = certify_bandwidth_platform() if certify_platform and tau == .02 else None
    passed = all(abs(row["mass_elimination_relative_residual"]) < 1e-12 and
                 (row["coefficient_radius_derivative"] is None or
                  row["coefficient_radius_derivative"] > 0) for row in result_rows)
    if certificate is not None:
        lower,upper = map(float,certificate["all_bandwidth_endpoint"])
        passed = passed and certificate["three_position_platform_certified"] and all(
            lower <= row["endpoint"] <= upper for row in result_rows if row["radius"] >= 5)
    return {"scope": "joint bandwidth sensitivity at fixed content, source and transfer coefficients",
            "tau": float(tau), "reference_radius": 5., "reference_endpoint": base["endpoint"],
            "rows": result_rows, "all_bandwidth_certificate": certificate,
            "production_parameters_updated": False,
            "work": {"spectral_response_evaluations": len(cache),
                     "frequency_quadrature_integrals": quadrature_integrals,
                     "analytic_boundary_terms": boundary_terms,
                     "iterative_endpoint_solves": 0},
            "passed": bool(passed)}


def hierarchy_scale_ratio(endpoint):
    """Return v/m_e in common mass units after eliminating M_P and squash.

    The ratio is 3 exp[(20-4*pi)c]/(16*pi**(5/2)*c). Its logarithm
    increases for c>1/(20-4*pi), including the complete three-position
    branch. Physical use supplies matching to these geometric readouts.
    """
    import math
    c = float(endpoint)
    beta = 20-4*math.pi
    if not math.isfinite(c) or c <= 1/beta:
        raise ValueError("endpoint must lie on the increasing scale-ratio branch")
    logarithm = math.log(3/(16*math.pi**2.5))+beta*c-math.log(c)
    return {"log_v_over_electron": logarithm,
            "log_ratio_endpoint_derivative": beta-1/c,
            "endpoint_log_ratio_derivative": 1/(beta-1/c),
            "endpoint_log_elasticity": 1/(beta*c-1)}


def invert_hierarchy_scale_ratio(ratio, *, endpoint_bounds=None):
    """Invert a matched v/m_e ratio on the increasing three-position branch.

    This is a scalar logarithmic equation and requires no spectral integral.
    The caller supplies a dimensionless ratio with v and m_e in common
    mass units. Interval endpoints may include the boundary of the branch.
    """
    import math
    from scipy.optimize import brentq
    ratio = float(ratio)
    if not math.isfinite(ratio) or ratio <= 0:
        raise ValueError("positive finite matched scale ratio required")
    bounds = (math.sqrt(11/2),math.sqrt(15/2)) if endpoint_bounds is None else tuple(endpoint_bounds)
    if len(bounds) != 2 or not bounds[0] < bounds[1]:
        raise ValueError("two increasing endpoint bounds required")
    lower,upper = (hierarchy_scale_ratio(x)["log_v_over_electron"] for x in bounds)
    target = math.log(ratio)
    if not lower <= target <= upper:
        raise ValueError("matched scale ratio is outside the declared endpoint branch")
    return float(brentq(lambda c: hierarchy_scale_ratio(c)["log_v_over_electron"]-target,
                        *bounds,xtol=1e-13,rtol=2e-14))


def _certify_same_shell_edges(steps=32):
    """Outward bounds at the two exact edges q=49/4 and q=16.

    Kernel monotonicity and opposite Gaussian endpoint bounds enclose each
    cell. This coarse certificate establishes only the position of the
    generation threshold, without computing precision mass intervals.
    """
    from cg_core.rational_interval import Interval as I, pi_interval, exp_negative
    Q = Fraction
    pi = pi_interval()
    tau = Q(1,50)
    rows = ((Q(0),Q(3,4),4),(Q(8),Q(3,4),36),
            (Q(4),Q(3,2)+tau*tau/6,192),(Q(4),1+tau*tau/6,72),
            (Q(4),tau*tau/6,24),
            (Q(9,4),3*tau*tau/8,168),(Q(25,4),3*tau*tau/8,576),
            (Q(49,4),3*tau*tau/8,1008))
    nodes, edges, row_cells = {}, [], 0
    for edge in (Q(49,4),Q(16)):
        total = I.point(0)
        for a,b,weight in rows:
            if a >= edge:
                continue
            key = (edge,a)
            if key not in nodes:
                width = I.point(edge-a).sqrt()/steps
                q = [(width*j)**2+a for j in range(steps+1)]
                nodes[key] = (width,q,[exp_negative(x/pi) for x in q])
            width,q,exponential = nodes[key]
            kernel = [(x/(x+b))**2 for x in q]
            lo = width*sum((kernel[j]*exponential[j+1] for j in range(steps)),I.point(0))
            hi = width*sum((kernel[j+1]*exponential[j] for j in range(steps)),I.point(0))
            total += weight*I(lo.lo,hi.hi)
            row_cells += steps
        edges.append(total*27/(128*pi**3))
    left,right = edges
    certified = ((left**2).hi < I.point(Q(11,2)).lo
                 and I.point(Q(11,2)).hi < (right**2).lo
                 and (right**2).hi < I.point(Q(15,2)).lo)
    return {"tau_exact": "1/50", "squared_frequency_edges": ["49/4","16"],
            "endpoint_enclosures": [x.decimal_bounds() for x in edges],
            "generation_edge_inside_support_certified": bool(certified),
            "method": "outward rational monotone kernel-Gaussian cell envelopes",
            "work": {"subintervals_per_row": steps,"row_subintervals": row_cells,
                     "exponential_enclosure_evaluations": len(nodes)*(steps+1)}}


def evaluate_hierarchy_selection(tau=.02):
    """Evaluate source support, the generation edge and transfer invariants.

    The R=5 response uses precisely the shells with 49/4 as the largest
    active a_j and 16 as the first excluded a_j. Hence this same nonzero
    shell support occurs for 49/(4*pi)<R<=16/pi. Strict monotonicity of
    c_R determines one lower generation edge c_R=sqrt(11/2). Reported
    inverse radii use floating quadrature; the support inequalities and
    monotonicity are analytic. No measured quantities enter this evaluation.
    """
    import math
    from scipy.optimize import brentq
    from cg_core.joint_response import evaluate as hierarchy
    from cg_core.spectrum_loop import iter_sm_spectrum
    from cg_core.window_weights import ResponseDomain
    from cg_frg.frg.spectral_sum import channel_tmunu_spin2, _w_tmunu_spin2
    if not math.isfinite(tau) or not 0 < tau < .25:
        raise ValueError("0<tau<1/4 required")
    cache = {}
    def endpoint(radius):
        if radius not in cache:
            cache[radius] = 27*channel_tmunu_spin2(1.,math.pi,tau,
                domain=ResponseDomain(radius))["rp3_pi0"]/128
        return cache[radius]
    thresholds = sorted({float(a) for kind,name,_,a,_,degree in
        iter_sm_spectrum(1.,math.sqrt(math.pi),tau,domain=ResponseDomain(6.))
        if degree*_w_tmunu_spin2(kind,name)>0})
    largest = max(a for a in thresholds if a < 5*math.pi)
    first_excluded = min(a for a in thresholds if a >= 5*math.pi)
    support = (largest/math.pi,first_excluded/math.pi)
    lower,upper = (endpoint(radius) for radius in support)
    edge = math.sqrt(11/2)
    if not lower < edge < endpoint(5.) < upper < math.sqrt(15/2):
        raise ValueError("the stated source support does not contain this three-position branch")
    radius_edge = float(brentq(lambda radius: endpoint(radius)-edge,*support,
                              xtol=2e-12,rtol=2e-14))
    c = endpoint(5.)
    readouts = hierarchy(c,tau,1.)
    ratio = readouts["v_HIGGS"]/(readouts["m_e_pred"]/1e3)
    invariant = hierarchy_scale_ratio(c)
    recovered = invert_hierarchy_scale_ratio(ratio)
    lepton_step = 2*readouts["alpha_lepton"]
    # Log masses retain the same scalar factor and their complete transfers.
    log_e = math.log(readouts["m_e_pred"]/1e3)
    log_mu = log_e+lepton_step+math.sqrt(2*math.pi)
    log_tau = log_mu+lepton_step
    lepton_residual = math.fsum((2*log_mu,-log_e,-log_tau,-math.sqrt(2*math.pi)))
    scale_residual = math.log(ratio)-invariant["log_v_over_electron"]
    certificate = _certify_same_shell_edges() if tau == .02 else None
    return {"scope": "fixed source support and geometric transfer identities",
            "tau": float(tau), "reference_radius": 5., "reference_endpoint": c,
            "support_interval": {"lower": support[0],"upper": support[1],
                "lower_closed": False,"upper_closed": True,
                "largest_active_spectral_value": largest,
                "first_excluded_spectral_value": first_excluded},
            "three_position_radius_interval": {"lower": radius_edge,"upper": support[1],
                "lower_closed": False,"upper_closed": True,
                "lower_definition": "c_R=sqrt(11/2)",
                "numeric_method": "floating quadrature and monotone inversion"},
            "support_endpoint_values": [lower,upper],
            "support_certificate": certificate,
            "scale_ratio": {**invariant,"v_over_electron": ratio,
                "eliminated_inputs": ["Planck scale","common squash factor"],
                "recovered_endpoint": recovered,"log_identity_residual": scale_residual},
            "charged_lepton_relation": {
                "definition": "2 ln(m_mu)-ln(m_e)-ln(m_tau)=sqrt(2*pi)",
                "species_order": ["electron","muon","tau"],
                "log_mass_weights": [-1,2,-1],
                "squared_muon_over_electron_tau": math.exp(math.sqrt(2*math.pi)),
                "log_identity_residual": lepton_residual,
                "matching_correction": "2 ln(C_mu)-ln(C_e)-ln(C_tau)"},
            "empirical_test_performed": False,"production_parameters_updated": False,
            "work": {"spectral_response_evaluations": len(cache),
                     "scale_ratio_spectral_evaluations": 0,
                     "bandwidth_inverse_solves": 1,"iterative_endpoint_solves": 0},
            "passed": bool(abs(scale_residual)<1e-12 and abs(lepton_residual)<1e-12
                           and abs(recovered-c)<1e-12 and
                           (certificate is None or
                            certificate["generation_edge_inside_support_certified"]))}


def infer_response_bandwidth(ratio_bounds, *, matching_source, mass_definition, tau=.02):
    """Map independently matched v/m_e bounds to the same-shell bandwidth.

    This comparison leaves all production parameters fixed. The supplied
    bounds include the physical-to-geometric matching in a stated mass
    definition. They are intersected with the source support and the
    three-position branch. Numerical inversion is not an interval certificate.
    """
    import math
    from scipy.optimize import brentq
    from cg_core.window_weights import ResponseDomain
    from cg_frg.frg.spectral_sum import channel_tmunu_spin2
    bounds = tuple(float(x) for x in ratio_bounds)
    if len(bounds) != 2 or not all(math.isfinite(x) and x>0 for x in bounds) or bounds[0]>bounds[1]:
        raise ValueError("two ordered positive matched ratio bounds required")
    if not all(isinstance(x,str) and x.strip() for x in (matching_source,mass_definition)):
        raise ValueError("matching source and common mass definition are required")
    if not math.isfinite(tau) or not 0 < tau < .25:
        raise ValueError("0<tau<1/4 required")
    support = (49/(4*math.pi),16/math.pi)
    cache = {}
    def endpoint(radius):
        if radius not in cache:
            cache[radius] = 27*channel_tmunu_spin2(1.,math.pi,tau,
                domain=ResponseDomain(radius))["rp3_pi0"]/128
        return cache[radius]
    c_lower = max(endpoint(support[0]),math.sqrt(11/2))
    c_upper = min(endpoint(support[1]),math.sqrt(15/2))
    base = {"matched_ratio_bounds": list(bounds),"matching_source": matching_source,
            "mass_definition": mass_definition,"tau": float(tau),
            "production_parameters_updated": False,
            "numerical_method": "monotone image of supplied bounds, floating quadrature and inversion"}
    if c_lower >= c_upper:
        return {**base,"status": "empty source branch","endpoint_interval": None,
                "radius_interval": None,"spectral_response_evaluations": len(cache)}
    logs = (max(math.log(bounds[0]),hierarchy_scale_ratio(c_lower)["log_v_over_electron"]),
            min(math.log(bounds[1]),hierarchy_scale_ratio(c_upper)["log_v_over_electron"]))
    if logs[0] > logs[1] or (logs[0] == logs[1] and
            logs[1] == hierarchy_scale_ratio(c_lower)["log_v_over_electron"]):
        return {**base,"status": "incompatible matched ratio","endpoint_interval": None,
                "radius_interval": None,"spectral_response_evaluations": len(cache)}
    targets = [float(brentq(lambda c: hierarchy_scale_ratio(c)["log_v_over_electron"]-target,
                    c_lower,c_upper,xtol=1e-13,rtol=2e-14)) for target in logs]
    radii = [float(brentq(lambda radius: endpoint(radius)-target,*support,
                        xtol=2e-12,rtol=2e-14)) for target in targets]
    return {**base,"status": "compatible matched ratio","endpoint_interval": targets,
            "radius_interval": radii,
            "lower_closed": targets[0] > math.sqrt(11/2) and radii[0] > support[0],
            "upper_closed": True,"spectral_response_evaluations": len(cache)}
