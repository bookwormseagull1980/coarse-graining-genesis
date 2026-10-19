"""Joint connection/radius variation of the actual Gaussian fermion window.

The radius coordinate is eta=log(L); the regulator scale k is held fixed.
The reference spectral domain is z0=omega^2+D0(L)^2<R*k^2: fixed with
respect to torsion, but radius dependent. Its frequency endpoints must
therefore be differentiated. A shell crossing has a square-root edge and
is reported explicitly rather than differentiated through.

Unlike a torsion-only variation, radius variation requires retaining the
reference determinant. Here log(N/k^2) fixes the dimensionless determinant
normalization, with N=omega^2+D_tau^2+R_k(z0). The full, reference and
relative actions and their two-variable jets are all calculated on the
same support. Volume integration is performed before a geometry force is
reported. No parameter store is changed.
"""
import math
from fractions import Fraction as Q

import numpy as np
from scipy.integrate import quad_vec

from cg_core.sm_content import N_GENERATIONS
from cg_core.window_weights import DEFAULT_RESPONSE_DOMAIN
from cg_core.rational_interval import Interval as I, GRID, exp_negative, log_positive, pi_interval
from cg_frg.ewsb.torsion_response import _reference_modes


def _reference_jet(z, scale_squared):
    """A=z/(1-exp(-z/k^2)), A_z and A_zz, stable near z=0."""
    r = z/scale_squared
    if r < .05:
        g = 1+r/2+r*r/12-r**4/720+r**6/30240-r**8/1209600
        first = .5+r/6-r**3/180+r**5/5040-r**7/151200
        second = 1/6-r*r/60+r**4/1008-r**6/21600
        return scale_squared*g, first, second/scale_squared
    e, den = math.exp(-r), -math.expm1(-r)
    return (z/den, (den-r*e)/den**2,
            e*((r-2)+(r+2)*e)/(den**3*scale_squared))


def _volume_jet(jet, volume):
    """Apply d_eta V=3V to the complete density jet, including mixed terms."""
    value, jt, je, htt, hte, hee, bulk, boundary = map(float, jet)
    return {
        "density": value,
        "density_gradient": [jt, je],
        "density_hessian": [[htt, hte], [hte, hee]],
        "integrated_action": volume*value,
        "integrated_gradient": [volume*jt, volume*(je+3*value)],
        "integrated_hessian": [
            [volume*htt, volume*(hte+3*jt)],
            [volume*(hte+3*jt), volume*(hee+6*je+9*value)]],
        "density_radius_bulk": bulk,
        "density_radius_boundary": boundary,
        "integrated_radius_bulk": volume*(bulk+3*value),
        "integrated_radius_boundary": volume*boundary,
    }


def fermion_geometry_response(tau, *, radius, scale,
                              domain=DEFAULT_RESPONSE_DOMAIN,
                              generations=N_GENERATIONS):
    """Full, reference and relative determinant jets in (tau,log radius).

    Derivatives are analytic derivatives of one integral, not finite
    differences of fitted responses. In u=omega/Omega coordinates,
    Omega^2=R*k^2-lambda, z=lambda+Omega^2*u^2 and
    d_eta z=-2lambda(1-u^2). The density measure has logarithmic
    derivative lambda/Omega^2-3. An independent bulk/Leibniz split is
    returned to expose the moving-boundary term.

    The normalization N/k^2, fixed k, finite domain and round geometry
    define this Gaussian block. Gauge/Higgs interactions and metric
    backreaction require their actual additional action terms.
    """
    if not math.isfinite(tau) or not -.5 < tau < .25:
        raise ValueError("finite tau in the positive-metric interval required")
    modes = _reference_modes(radius, scale, domain, generations)
    length, k2 = float(radius), float(scale)**2
    edge = domain.edge(k2)
    # Check the next excluded shell as well: equality is not included in
    # _reference_modes but its one-sided geometry derivative is singular.
    candidates = [float(mode["reference_squared"]) for mode in modes]
    candidates.append(((len(modes)+1.5)/length)**2)
    if any(abs(lam-edge) <= 32*np.finfo(float).eps*max(lam, edge)
           for lam in candidates):
        raise ValueError("radius lies on a spectral-domain shell crossing")
    volume = math.pi**2*length**3
    v, result, error_sum, sectors = 3/(4*length), np.zeros((3, 8)), 0., []
    for mode in modes:
        d, lam = float(mode["native"]), float(mode["reference_squared"])
        h = edge-lam
        omega = math.sqrt(h)
        shifted = d-v*tau
        delta = (shifted-d)*(shifted+d)
        dt, dtt = -2*v*shifted, 2*v*v
        q = lam/h-3
        dq = -2*edge*lam/h**2

        def integrand(u):
            z = lam+h*u*u
            a, az, azz = _reference_jet(z, k2)
            ze = -2*lam*(1-u*u)
            ae = az*ze
            aee = azz*ze*ze-2*az*ze
            den = a+delta
            ne, nee = ae-2*delta, aee+4*delta
            if den <= 0:
                raise ArithmeticError("nonpositive regulated squared-operator denominator")

            def jet(f, n, nt, ntt, n_eta, n_etaeta, insertion):
                jt, je = -nt/n, -n_eta/n
                htt = nt*nt/n**2-ntt/n
                # delta_tau scales as L^-2; the reference has nt=0.
                hte = 2*nt/n+nt*n_eta/n**2
                hee = n_eta*n_eta/n**2-n_etaeta/n
                return np.array((f, jt, q*f+je, htt,
                                 q*jt+hte,
                                 (q*q+dq)*f+2*q*je+hee,
                                 -3*f+2*(lam*az+insertion)/n,
                                 0.))

            full = jet(-math.log(den/k2), den, dt, dtt, ne, nee, delta)
            reference = jet(-math.log(a/k2), a, 0., 0., ae, aee, 0.)
            relative = full-reference
            # log1p avoids cancellation in the small torsion action.
            relative[0] = -math.log1p(delta/a)
            return np.array((full, reference, relative))

        integral, error = quad_vec(integrand, 0., 1., epsabs=2e-12, epsrel=2e-11)
        coefficient = mode["degeneracy"]*omega/(math.pi*volume)
        contribution = coefficient*integral
        a_edge = _reference_jet(edge, k2)[0]
        edge_values = np.array((-math.log((a_edge+delta)/k2),
                                -math.log(a_edge/k2), -math.log1p(delta/a_edge)))
        contribution[:, 7] = coefficient*lam/h*edge_values
        result += contribution
        error_sum += coefficient*error
        sectors.append({"shell": mode["shell"],
                        "degeneracy": mode["degeneracy"],
                        "neutral_degeneracy": mode["neutral_degeneracy"],
                        "frequency_edge": omega,
                        "relative_integrated_radius_boundary": volume*contribution[2, 7]})
    reports = {name: _volume_jet(jet, volume)
               for name, jet in zip(("full", "reference", "relative"), result)}
    return {**reports, "coordinates": ["tau", "log_radius"],
            "radius": length, "scale": float(scale), "volume": volume,
            "domain_level": domain.radius, "generations": generations,
            "modes": sectors, "quadrature_error_estimate": error_sum,
            "determinant_normalization": "log(N/k^2), with k fixed in the radius variation",
            "scope": "full sixteen-coordinate Gaussian fermion block on a round radius-dependent reference window"}


def torsion_geometry_response(tau, *, radius, scale,
                              domain=DEFAULT_RESPONSE_DOMAIN,
                              generations=N_GENERATIONS):
    """Joint jet of the retained torsion density plus the full fermion block.

    Adds exactly the isotropic production torsion action -9tau^2/(2L^2).
    Its volume-integrated geometry force differs from its density force.
    The reference fermion action is retained for the geometry equation.
    """
    from cg_frg.ewsb.squash_level_transfer import ec_action
    from cg_core.ec_variation import quadratic_torsion_coefficients
    report = fermion_geometry_response(tau, radius=radius, scale=scale,
                                        domain=domain, generations=generations)
    action = ec_action(1.)
    c0 = quadratic_torsion_coefficients(*(action[key] for key in ("a", "b", "c")))[0]
    bare = 3*c0*tau*tau/radius**2
    jt, htt = 6*c0*tau/radius**2, 6*c0/radius**2
    jet = _volume_jet((bare, jt, -2*bare, htt, -2*jt, 4*bare, -2*bare, 0.),
                      report["volume"])
    full = report["full"]
    combined = {key: (np.asarray(full[key])+np.asarray(jet[key])).tolist()
                for key in full}
    return {**report, "bare_torsion": jet, "common": combined,
            "scope": "volume-integrated production torsion plus full Gaussian fermion block; the LC geometry action and other fields are separate terms"}


def trace_matched_curvature_response(tau, *, radius, scale,
                                     domain=DEFAULT_RESPONSE_DOMAIN,
                                     generations=N_GENERATIONS):
    """Test the unique scalar-curvature completion matching the retained trace.

    production_curvature_matching fixes gamma=3 in M_G=1 units. Adding
    gamma*R_LC completes precisely that curvature contribution, leaving
    the two previously identified transverse production terms unchanged.
    This is an explicit candidate action with no fitted gamma; trace
    matching does not derive the normalization from the minimal source.
    Both the common block and this completion are reported separately.
    """
    from cg_core.connection_action import production_curvature_matching
    report = torsion_geometry_response(tau, radius=radius, scale=scale,
                                        domain=domain, generations=generations)
    gamma = float(production_curvature_matching()["trace_matched_curvature_normalization"])
    density = 6*gamma/radius**2
    lc = _volume_jet((density, 0., -2*density, 0., 0., 4*density, -2*density, 0.),
                    report["volume"])
    completed = {key: (np.asarray(report["common"][key])+np.asarray(lc[key])).tolist()
                 for key in lc}
    required = -report["common"]["integrated_gradient"][1]/(6*math.pi**2*radius)
    return {**report, "lc_geometry": lc, "curvature_completed": completed,
            "trace_matched_curvature_coefficient": gamma,
            "curvature_coefficient_required_by_radius_equation": required,
            "scope": "trace-matched scalar-curvature completion of the displayed common block; coefficient matching is stated explicitly"}


def content_fixed_geometry_response(*, radius, scale,
                                    domain=DEFAULT_RESPONSE_DOMAIN,
                                    generations=N_GENERATIONS):
    """Pull the displayed action back along the V5 fixed-content lift.

    For eta=log(L), iota(eta)=(tau_content,eta) has tangent (0,1).
    Consequently d(iota*S)=S_eta and d2(iota*S)=S_eta,eta.  No torsion
    equation is solved and no Schur complement is taken.  The ambient
    normal derivative S_tau is reported, not discarded or replaced by
    an assumed matter current.  This calculation uses the existing
    production identification of content with connection amplitude.
    """
    from cg_core.ec_variation import torsion_capacity_balance
    balance = torsion_capacity_balance()
    report = trace_matched_curvature_response(
        float(balance["tau_content"]), radius=radius, scale=scale,
        domain=domain, generations=generations)
    jet = report["curvature_completed"]
    hessian = jet["integrated_hessian"]
    return {
        **report, "content_balance": balance,
        "tau_content_exact": str(balance["tau_content"]),
        "tau_content": float(balance["tau_content"]),
        "content_fixed": {
            "coordinate": "log_radius",
            "integrated_action": jet["integrated_action"],
            "integrated_gradient": jet["integrated_gradient"][1],
            "integrated_hessian": hessian[1][1],
            "tangent": [0, 1],
            "ambient_connection_derivative": jet["integrated_gradient"][0],
            "connection_elimination_correction": (None if hessian[0][0] == 0 else
                -hessian[1][0]*hessian[0][1]/hessian[0][0]),
        },
        "construction": "pullback along the existing V5 isotropic content lift",
    }


def solve_content_fixed_radius(*, radius_bracket, scale,
                               domain=DEFAULT_RESPONSE_DOMAIN,
                               generations=N_GENERATIONS):
    """Solve the radius variation while preserving exact content capacity.

    This is a one-dimensional restriction of the same displayed test
    action used by solve_joint_window_saddle, not a different fitted
    functional.  The two-variable saddle remains a separate comparison.
    """
    from scipy.optimize import brentq
    if (len(radius_bracket) != 2 or
            not all(math.isfinite(x) for x in radius_bracket) or
            not 0 < radius_bracket[0] < radius_bracket[1]):
        raise ValueError("two ordered positive finite radius endpoints required")
    low, high = radius_bracket
    if len(_reference_modes(low, scale, domain, generations)) != len(
            _reference_modes(high, scale, domain, generations)):
        raise ValueError("radius search crosses a spectral-domain shell edge")

    def response(length):
        return content_fixed_geometry_response(radius=length, scale=scale,
                                                domain=domain, generations=generations)

    length = brentq(lambda l: response(l)["content_fixed"]["integrated_gradient"],
                    low, high, xtol=1e-12)
    data = response(length)
    return {
        "status": "numerical radius stationary point on the fixed-content lift",
        "tau_content_exact": data["tau_content_exact"],
        "tau_content": data["tau_content"], "radius_estimate": length,
        "radius_bracket": list(radius_bracket),
        "content_fixed": data["content_fixed"],
        "reference_radius_force": data["reference"]["integrated_gradient"][1],
        "frequency_boundary_radius_force": data["full"]["integrated_radius_boundary"],
        "scope": data["scope"], "construction": data["construction"],
        "interval_existence_or_uniqueness_certificate": False,
    }


def solve_joint_window_saddle(*, radius_bracket, scale,
                              domain=DEFAULT_RESPONSE_DOMAIN,
                              generations=N_GENERATIONS,
                              tau_bracket=(-.49, .24)):
    """Numerical solution of both variations in one open spectral chamber.

    The action is the trace-matched curvature completion above. The
    brackets delimit a computation; they are not parameters in the action.
    A bracket crossing a spectral edge is rejected, since the corresponding
    radius force has no continuous extension through that edge. This solver
    reports a numerical stationary point, its full two-variable Hessian and
    the radius force with/without the reference contribution. No global
    uniqueness or interval certificate is inferred from a small residual.
    """
    from scipy.optimize import brentq
    if (len(radius_bracket) != 2 or len(tau_bracket) != 2
            or not all(math.isfinite(x) for x in (*radius_bracket, *tau_bracket))):
        raise ValueError("two finite radius and tau bracket endpoints required")
    low, high = radius_bracket
    tl, th = tau_bracket
    if not 0 < low < high or not -.5 < tl < th < .25:
        raise ValueError("ordered positive radius and interior tau brackets required")
    modes_low = _reference_modes(low, scale, domain, generations)
    modes_high = _reference_modes(high, scale, domain, generations)
    if len(modes_low) != len(modes_high):
        raise ValueError("radius search crosses a spectral-domain shell edge")

    def response(length):
        def trace_equation(tau):
            data = trace_matched_curvature_response(
                tau, radius=length, scale=scale, domain=domain, generations=generations)
            return data["curvature_completed"]["integrated_gradient"][0]
        tau = brentq(trace_equation, tl, th, xtol=1e-13)
        return tau, trace_matched_curvature_response(
            tau, radius=length, scale=scale, domain=domain, generations=generations)

    def radius_equation(length):
        return response(length)[1]["curvature_completed"]["integrated_gradient"][1]

    radius = brentq(radius_equation, low, high, xtol=1e-12)
    tau, report = response(radius)
    completed = report["curvature_completed"]
    hessian = np.asarray(completed["integrated_hessian"])
    if hessian[0, 0] == 0:
        raise ArithmeticError("singular torsion Hessian at joint stationary point")
    return {"status": "numerical stationary point of the specified common action",
            "radius_bracket": list(radius_bracket), "tau_bracket": list(tau_bracket),
            "radius_estimate": radius, "tau_estimate": tau,
            "integrated_gradient": completed["integrated_gradient"],
            "integrated_hessian": completed["integrated_hessian"],
            "hessian_eigenvalues": np.linalg.eigvalsh(hessian).tolist(),
            "radius_curvature_after_torsion_elimination": float(
                hessian[1, 1]-hessian[1, 0]*hessian[0, 1]/hessian[0, 0]),
            "reference_radius_force": report["reference"]["integrated_gradient"][1],
            "relative_only_radius_force": (completed["integrated_gradient"][1]
                                           -report["reference"]["integrated_gradient"][1]),
            "frequency_boundary_radius_force": report["full"]["integrated_radius_boundary"],
            "neutral_reference_multiplicity": sum(row["neutral_degeneracy"] for row in report["modes"]),
            "trace_matched_curvature_coefficient": report["trace_matched_curvature_coefficient"],
            "determinant_normalization": report["determinant_normalization"],
            "scope": report["scope"],
            "interval_existence_or_uniqueness_certificate": False}


def _interval_joint_variation(tau_interval, radius_interval, *, scale, domain,
                              generations, cells):
    """Outward derivatives of the integrated completion in (tau,L)."""
    tau, length = I.bounds(*tau_interval), I.bounds(*radius_interval)
    k2, edge = Q(str(scale))**2, Q(str(domain.radius))*Q(str(scale))**2
    modes = _reference_modes(Q(str(radius_interval[0])), scale, domain, generations)
    other = _reference_modes(Q(str(radius_interval[1])), scale, domain, generations)
    if len(modes) != len(other):
        raise ValueError("certificate box crosses a spectral-domain shell edge")
    next_squared = (Q(2*len(modes)+3, 2)/length)**2
    if next_squared.lo <= edge*GRID:
        raise ValueError("certificate box meets the next spectral-domain shell edge")
    pi = pi_interval()
    gradient, hessian = [I.point(0) for _ in range(2)], [I.point(0) for _ in range(3)]
    v = Q(3, 4)/length
    for mode in modes:
        n = mode["shell"]
        d = (1 if n % 2 == 0 else -1)*Q(2*n+3, 2)/length
        lam = d**2
        h = edge-lam
        if h.lo <= 0:
            raise ValueError("certificate box meets a spectral-domain shell edge")
        shifted = d-v*tau
        delta = -2*d*v*tau+(v*tau)**2
        dt, dtt = -2*v*shifted, 2*v*v
        q, dq = lam/h, -2*edge*lam/(h**2)
        measure = mode["degeneracy"]*h.sqrt()/(pi*cells)
        for j in range(cells):
            u = I.bounds(Q(j, cells), Q(j+1, cells))
            z = lam+h*(u**2)
            r = z/k2
            e = exp_negative(r)
            den = 1-e
            a = z/den
            az = (den-r*e)/(den**2)
            azz = e*((r-2)+(r+2)*e)/(den**3*k2)
            ze = -2*lam*(1-u**2)
            ne = az*ze-2*delta
            nee = azz*ze**2-2*az*ze+4*delta
            prop = a+delta
            if prop.lo <= 0:
                raise ArithmeticError("certificate crosses a regulated-propagator pole")
            f = -log_positive(prop/k2)
            jt, je = -dt/prop, -ne/prop
            htt = dt**2/prop**2-dtt/prop
            hte = 2*dt/prop+dt*ne/prop**2
            hee = ne**2/prop**2-nee/prop
            gradient[0] += measure*jt
            gradient[1] += measure*(q*f+je)/length
            hessian[0] += measure*htt
            hessian[1] += measure*(q*jt+hte)/length
            hessian[2] += measure*((q*q+dq-q)*f+(2*q-1)*je+hee)/length**2
    # The same exact production/curvature coefficients as the numerical
    # action, with the volume included: pi^2 L (3c0 tau^2+6gamma).
    from cg_core.ec_variation import production_torsion_variation
    from cg_core.connection_action import production_curvature_matching
    c0 = production_torsion_variation()["irreducible_weights"][0]
    gamma = production_curvature_matching()["trace_matched_curvature_normalization"]
    gradient[0] += 6*c0*pi**2*length*tau
    gradient[1] += pi**2*(3*c0*tau**2+6*gamma)
    hessian[0] += 6*c0*pi**2*length
    hessian[1] += 6*c0*pi**2*tau
    return gradient, ((hessian[0], hessian[1]), (hessian[1], hessian[2]))


def certify_joint_window_saddle(*, tau_interval, radius_interval, scale,
                                domain=DEFAULT_RESPONSE_DOMAIN,
                                generations=N_GENERATIONS, cells=512,
                                center=None):
    """Prove a joint stationary point by an outward Newton-map inclusion.

    A rational preconditioner P is taken from the numerical Hessian only
    to propose a Newton map. Exact interval arithmetic independently checks
    det(P)!=0, T(X) inside the box and ||I-P Hess S(X)||_infinity<1.
    Banach's theorem then proves existence and uniqueness in that box.
    The reported sign of the Schur complement certifies auxiliary inertia.
    No numerical residual is used as the existence proof.
    """
    if (not isinstance(cells, int) or isinstance(cells, bool) or cells < 1
            or len(tau_interval) != 2 or len(radius_interval) != 2):
        raise ValueError("two nonempty intervals and positive cell count required")
    intervals = [tuple(Q(str(x)) for x in values)
                 for values in (tau_interval, radius_interval)]
    if (not -Q(1, 2) < intervals[0][0] < intervals[0][1] < Q(1, 4)
            or not 0 < intervals[1][0] < intervals[1][1]):
        raise ValueError("interior tau and positive radius boxes required")
    point = ([sum(pair)/2 for pair in intervals] if center is None
             else [Q(str(x)) for x in center])
    if len(point) != 2 or any(not lo <= x <= hi for x, (lo, hi) in zip(point, intervals)):
        raise ValueError("center must belong to the certificate box")
    data = trace_matched_curvature_response(float(point[0]), radius=float(point[1]),
                                            scale=scale, domain=domain, generations=generations)
    jet = data["curvature_completed"]
    l = float(point[1])
    he = np.asarray(jet["integrated_hessian"])
    gl = jet["integrated_gradient"][1]
    # The certificate variables are (tau,L), not (tau,eta).
    hl = np.array([[he[0, 0], he[0, 1]/l], [he[1, 0]/l, (he[1, 1]-gl)/l**2]])
    inverse = np.linalg.inv(hl)
    preconditioner = [[Q(str(x)) for x in row] for row in inverse]
    determinant = preconditioner[0][0]*preconditioner[1][1]-preconditioner[0][1]*preconditioner[1][0]
    if determinant == 0:
        raise ArithmeticError("singular rational Newton preconditioner")
    options = dict(scale=scale, domain=domain, generations=generations, cells=cells)
    gp, _ = _interval_joint_variation((point[0], point[0]), (point[1], point[1]), **options)
    _, hx = _interval_joint_variation(*intervals, **options)
    remainder = [[I.point(int(i == j))-sum(preconditioner[i][k]*hx[k][j] for k in range(2))
                  for j in range(2)] for i in range(2)]
    norm = max(sum(Q(max(abs(item.lo), abs(item.hi)), GRID) for item in row) for row in remainder)
    box = [I.bounds(*pair) for pair in intervals]
    image = [I.point(point[i])-sum(preconditioner[i][k]*gp[k] for k in range(2))
             +sum(remainder[i][j]*(box[j]-point[j]) for j in range(2)) for i in range(2)]
    interior = all(x.lo < y.lo <= y.hi < x.hi for x, y in zip(box, image))
    schur = None if hx[0][0].lo <= 0 <= hx[0][0].hi else hx[1][1]-hx[1][0]*hx[0][1]/hx[0][0]
    inertia = hx[0][0].hi < 0 and schur is not None and schur.lo > 0
    return {"proof": "strict invariant Newton box and contraction in (tau,L)",
            "center": [str(x) for x in point], "cells": cells,
            "tau_box": box[0].decimal_bounds(), "radius_box": box[1].decimal_bounds(),
            "point_gradient": [x.decimal_bounds() for x in gp],
            "hessian_box": [[x.decimal_bounds() for x in row] for row in hx],
            "rational_preconditioner": [[str(x) for x in row] for row in preconditioner],
            "newton_image": [x.decimal_bounds() for x in image],
            "newton_image_strictly_inside": interior,
            "contraction_norm_bound": I.point(norm).decimal_bounds(),
            "strict_contraction": norm < 1,
            "unique_joint_stationary_point_certified": bool(interior and norm < 1),
            "reduced_radius_curvature_box": None if schur is None else schur.decimal_bounds(),
            "one_negative_one_positive_direction_certified": bool(inertia),
            "scope": data["scope"]}


def certify_content_fixed_radius(*, radius_interval, scale,
                                 domain=DEFAULT_RESPONSE_DOMAIN,
                                 generations=N_GENERATIONS, cells=512):
    """Certify a restricted radius minimum by signs and positive curvature.

    Exact interval derivatives refer to (tau,L).  Restricting tau to the
    rational capacity value leaves the second gradient and (L,L) Hessian
    entries.  Opposite endpoint signs prove existence; a strictly positive
    Hessian throughout the box proves uniqueness and a strict minimum.
    Neither a vanishing ambient torsion derivative nor its Schur
    complement is asserted by this certificate.
    """
    from cg_core.ec_variation import torsion_capacity_balance
    if (not isinstance(cells, int) or isinstance(cells, bool) or cells < 1 or
            len(radius_interval) != 2):
        raise ValueError("two radius endpoints and a positive cell count required")
    low, high = (Q(str(x)) for x in radius_interval)
    if not 0 < low < high:
        raise ValueError("ordered positive radius endpoints required")
    tau = torsion_capacity_balance()["tau_content"]
    options = dict(scale=scale, domain=domain, generations=generations, cells=cells)
    left, _ = _interval_joint_variation((tau, tau), (low, low), **options)
    right, _ = _interval_joint_variation((tau, tau), (high, high), **options)
    gradient, hessian = _interval_joint_variation((tau, tau), (low, high), **options)
    signs = left[1].hi < 0 < right[1].lo
    positive = hessian[1][1].lo > 0
    return {
        "proof": "opposite radius derivative signs and positive restricted curvature",
        "tau_content_exact": str(tau), "cells": cells,
        "radius_interval": I.bounds(low, high).decimal_bounds(),
        "left_radius_derivative": left[1].decimal_bounds(),
        "right_radius_derivative": right[1].decimal_bounds(),
        "restricted_radius_hessian": hessian[1][1].decimal_bounds(),
        "ambient_connection_derivative": gradient[0].decimal_bounds(),
        "opposite_endpoint_signs": bool(signs),
        "positive_restricted_curvature": bool(positive),
        "unique_restricted_radius_minimum_certified": bool(signs and positive),
        "construction": "existing V5 isotropic content lift of the displayed action",
    }
