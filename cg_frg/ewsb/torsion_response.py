"""Action-consistent torsion response of the finite V5 fermion window.

The reference operator is the signed RP3 Dirac operator.  All sixteen
content coordinates are retained, with the existing chiral source rule:
left components use odd shells and right components use even shells.
The neutral right line therefore contributes to the spin response.

At a fixed reference projection q0^2+D0^2<R*k^2 the Gaussian-regulated
relative fermion action, in the trace convention of trace_kernels, is

  F(tau) = -sum deg/V3 int dq0/(2*pi)
             log(1 + (D_tau^2-D0^2)/(q0^2+D0^2+R_k(q0^2+D0^2))).

R_k(z)=z/(exp(z/k^2)-1), D_tau=D0-3*tau/(4*L).  The window and regulator
are held fixed in tau; only the actual operator is differentiated.  Thus
the action, first derivative and Hessian use precisely the same support
and denominator.  No current is adjusted to a target torsion.

This is the regulated Gaussian fermion block at fixed round geometry,
not the interacting gauge/Higgs/geometry effective action.  The relative
determinant is exact for this quadratic block; stationarity of this block
does not perform the remaining field variations.  Units are M_G=1, with
the V5 trace-density convention V3=pi^2*L^3 and the production EC action.
Numerical quadrature and outward rational certificates are kept separate.
"""
from functools import lru_cache
from fractions import Fraction as Q
import math

import numpy as np
from scipy.integrate import quad_vec
from scipy.optimize import brentq

from cg_core.content_response import FULL_GENERATION
from cg_core.ec_variation import quadratic_torsion_coefficients
from cg_core.rational_interval import Interval as I, exp_negative, pi_interval
from cg_core.sm_content import N_GENERATIONS
from cg_core.window_weights import DEFAULT_RESPONSE_DOMAIN, ResponseDomain


def _rational(value):
    return Q(str(value)) if isinstance(value, (float, np.floating)) else Q(value)


def _reference_modes(radius, scale, domain, generations):
    """Enumerate the whole declared reference domain, without a mode cap."""
    if (not math.isfinite(float(radius)) or radius <= 0
            or not math.isfinite(float(scale)) or scale <= 0
            or not isinstance(domain, ResponseDomain) or domain.projection != "fixed"
            or not isinstance(generations, int) or isinstance(generations, bool)
            or generations <= 0):
        raise ValueError("positive radius/scale, a fixed reference domain and positive generation count required")
    length, cutoff = _rational(radius), _rational(scale)
    edge = _rational(domain.radius)*cutoff*cutoff
    n, result = 0, []
    while (Q(2*n+3, 2)/length)**2 < edge:
        native = (-1 if n % 2 else 1)*Q(2*n+3, 2)/length
        # This is the existing source projection, not a hypercharge weight.
        rows = tuple(row for row in FULL_GENERATION if (row[4] == 1) == bool(n % 2))
        components = sum(row[3] for row in rows)
        spatial = (n+1)*(n+2)
        result.append({"shell": n, "native": native, "reference_squared": native*native,
                       "degeneracy": spatial*components*generations,
                       "neutral_degeneracy": spatial*generations if n % 2 == 0 else 0,
                       "content_labels": tuple(row[0] for row in rows)})
        n += 1
    return tuple(result)


def fermion_window_response(tau, *, radius, scale, domain=DEFAULT_RESPONSE_DOMAIN,
                            generations=N_GENERATIONS):
    """Relative action and two actual tau derivatives of one fermion block.

    The finite-domain edge and regulator are the tau=0 reference data, so
    there is no omitted moving-boundary term.  Binary quadrature errors
    are estimates.  certify_fermion_window_response provides an independent
    enclosure of the first and second derivatives using rational arithmetic.
    """
    if not math.isfinite(tau) or not -.5 < tau < .25:
        raise ValueError("finite tau in the downstream positive-metric interval required")
    modes = _reference_modes(radius, scale, domain, generations)
    length, cutoff = float(radius), float(scale)
    volume = math.pi**2*length**3
    v = 3/(4*length)
    result, errors = np.zeros(3), 0.
    neutral_current, sectors = 0., []
    for mode in modes:
        native, lam = float(mode["native"]), float(mode["reference_squared"])
        omega = math.sqrt(domain.edge(cutoff*cutoff)-lam)
        coupled = native-v*tau
        delta, first, second = (coupled-native)*(coupled+native), -2*v*coupled, 2*v*v

        def integrand(u):
            z = lam+omega*omega*u*u
            reference = z/(-math.expm1(-z/(cutoff*cutoff)))
            den = reference+delta
            return np.array((-math.log1p(delta/reference), -first/den,
                             first*first/(den*den)-second/den))

        integral, error = quad_vec(integrand, 0., 1., epsabs=1e-12, epsrel=1e-11)
        coefficient = mode["degeneracy"]*omega/(math.pi*volume)
        contribution = coefficient*integral
        result += contribution
        errors += coefficient*error
        if mode["neutral_degeneracy"]:
            neutral_current += contribution[1]*mode["neutral_degeneracy"]/mode["degeneracy"]
        sectors.append({"shell": mode["shell"], "native_dirac": native,
                        "degeneracy": mode["degeneracy"], "content_labels": mode["content_labels"],
                        "neutral_degeneracy": mode["neutral_degeneracy"],
                        "action": float(contribution[0]), "current": float(contribution[1]),
                        "curvature": float(contribution[2])})
    return {"relative_action": float(result[0]), "tau_current": float(result[1]),
            "tau_curvature": float(result[2]),
            "matter_bilinear": float(-result[1]/v),
            "neutral_tau_current": float(neutral_current),
            "quadrature_error_estimate": errors, "modes": sectors,
            "generations": generations, "content_dimension_per_generation": 16,
            "reference_projection": "fixed at D0; no source-dependent boundary shift",
            "scope": "regulated Gaussian fermion determinant at fixed round geometry"}


@lru_cache(maxsize=12)
def _reference_rectangles(length, cutoff, level, generations, cells):
    """Outward reference propagators on a normalized frequency partition."""
    domain = ResponseDomain(float(level), "fixed")
    modes = _reference_modes(length, cutoff, domain, generations)
    pi = pi_interval()
    volume = pi**2*length**3
    edge = level*cutoff**2
    prepared = []
    for mode in modes:
        lam = mode["reference_squared"]
        width_squared = edge-lam
        # F(z)=z/(1-exp(-z/k²)) is increasing for z>0.  End-point
        # evaluation avoids introducing an artificial inverse correlation.
        edges = []
        for j in range(cells+1):
            z = I.point(lam+width_squared*Q(j, cells)**2)
            edges.append(z/(1-exp_negative(z/cutoff**2)))
        rectangles = tuple(I(edges[j].lo, edges[j+1].hi) for j in range(cells))
        coefficient = mode["degeneracy"]*I.point(width_squared).sqrt()/(pi*volume*cells)
        prepared.append((mode["native"], rectangles, coefficient))
    return tuple(prepared)


def certify_fermion_window_response(tau_interval, *, radius, scale,
                                    domain=DEFAULT_RESPONSE_DOMAIN,
                                    generations=N_GENERATIONS, cells=512):
    """Outward current/Hessian enclosures, including every reference shell.

    Rectangular interval integration encloses the continuous frequency
    integral; it is not a comparison of two quadrature resolutions.  The
    only truncation is the declared finite measurement domain itself.
    No claim is made that an infinite Gaussian tail vanishes outside it.
    """
    if (not isinstance(cells, int) or isinstance(cells, bool) or cells < 1
            or len(tau_interval) != 2):
        raise ValueError("a two-endpoint tau interval and positive cell count required")
    _reference_modes(radius, scale, domain, generations)
    length, cutoff, level = map(_rational, (radius, scale, domain.radius))
    low, high = map(_rational, tau_interval)
    if low > high or low <= -Q(1, 2) or high >= Q(1, 4):
        raise ValueError("ordered tau interval inside the positive-metric domain required")
    tau = I.bounds(low, high)
    v = Q(3, 4)/length
    current, curvature = I.point(0), I.point(0)
    for native, rectangles, coefficient in _reference_rectangles(
            length, cutoff, level, generations, cells):
        coupled = native-v*tau
        # Interval.__pow__ is a repeated-product enclosure.  It remains
        # valid even when overestimation occurs; positive denominators
        # below are checked explicitly.
        delta = (coupled-native)*(coupled+native)
        first, second = -2*v*coupled, 2*v*v
        j, h = I.point(0), I.point(0)
        for reference in rectangles:
            den = reference+delta
            if den.lo <= 0:
                raise ArithmeticError("interval crosses a regulated-propagator pole; subdivide tau")
            j += -first/den
            h += first**2/den**2-second/den
        current += coefficient*j
        curvature += coefficient*h
    return current, curvature


def torsion_window_action(tau, *, radius, scale, domain=DEFAULT_RESPONSE_DOMAIN,
                          generations=N_GENERATIONS):
    """Common EC plus Gaussian-fermion action and its tau variations.

    All values are in M_G=1 action units.  The production trace coefficient
    is read from ec_action; no coupling is determined by demanding a
    prescribed nonzero stationary tau.  In particular order_parameter's
    quartic reconstructed from phi0=2*tau is not used here.
    """
    from cg_frg.ewsb.squash_level_transfer import ec_action
    coefficients = ec_action(1.)
    c0 = quadratic_torsion_coefficients(*(coefficients[key] for key in ("a", "b", "c")))[0]
    fermion = fermion_window_response(tau, radius=radius, scale=scale,
                                      domain=domain, generations=generations)
    bare = 3*c0* tau*tau/radius**2
    bare_first, bare_second = 6*c0*tau/radius**2, 6*c0/radius**2
    return {**fermion, "relative_action": bare+fermion["relative_action"],
            "stationarity_residual": bare_first+fermion["tau_current"],
            "tau_hessian": bare_second+fermion["tau_curvature"],
            "bare_tau_current": bare_first, "bare_tau_hessian": bare_second,
            "scope": "EC plus Gaussian fermion block in unit-M_G action convention; fixed round geometry"}


def solve_torsion_window(*, radius, scale, domain=DEFAULT_RESPONSE_DOMAIN,
                         generations=N_GENERATIONS, bracket=(-.49, .24), cells=512):
    """Compute a saddle and certify existence/uniqueness when signs permit.

    A certified nonzero derivative of constant sign on the whole supplied
    bracket establishes uniqueness there.  A point enclosure divided by
    that derivative bound then encloses the computed root.  Failure of
    these checks is reported, never turned into a root certificate.
    This does not assert stability of the auxiliary tau direction.
    """
    from cg_core.ec_variation import production_torsion_variation, full_carrier_response
    if len(bracket) != 2:
        raise ValueError("a two-endpoint stationary bracket required")
    low, high = map(_rational, bracket)
    if low >= high or low <= -Q(1, 2) or high >= Q(1, 4):
        raise ValueError("nonempty bracket inside the positive-metric interval required")
    bare_hessian = production_torsion_variation()["isotropic_hessian"]/_rational(radius)**2
    options = dict(radius=radius, scale=scale, domain=domain, generations=generations)
    def numerical(tau):
        return torsion_window_action(tau, **options)["stationarity_residual"]
    point_low, _ = certify_fermion_window_response((low, low), cells=cells, **options)
    point_high, _ = certify_fermion_window_response((high, high), cells=cells, **options)
    gl, gh = point_low+bare_hessian*low, point_high+bare_hessian*high
    _, hh = certify_fermion_window_response((low, high), cells=cells, **options)
    derivative = hh+bare_hessian
    monotone = derivative.hi < 0 or derivative.lo > 0
    crossed = gl.lo > 0 and gh.hi < 0 or gl.hi < 0 and gh.lo > 0
    result = {"scope": "EC plus regulated Gaussian fermion block, fixed geometry and fixed reference window",
              "radius": float(radius), "scale": float(scale), "domain_level": domain.radius,
              "generations": generations, "cells": cells,
              "bracket": [str(low), str(high)],
              "left_residual": gl.decimal_bounds(), "right_residual": gh.decimal_bounds(),
              "hessian_on_bracket": derivative.decimal_bounds(),
              "strict_monotonicity_certified": monotone,
              "existence_certified": crossed,
              "unique_root_certified": crossed and monotone}
    tau_gauge = full_carrier_response()["gauge_conditioned_tau"]
    gauge_j, _ = certify_fermion_window_response((tau_gauge, tau_gauge), cells=cells, **options)
    gauge_residual = gauge_j+bare_hessian*tau_gauge
    result["gauge_tau_residual"] = gauge_residual.decimal_bounds()
    result["gauge_tau_stationarity_excluded"] = gauge_residual.lo > 0 or gauge_residual.hi < 0
    if crossed:
        root = brentq(numerical, float(low), float(high), xtol=1e-13)
        result["root_estimate"] = root
        result["at_root"] = torsion_window_action(root, **options)
        if monotone:
            point, _ = certify_fermion_window_response((root, root), cells=cells, **options)
            residual = point+bare_hessian*_rational(root)
            slope = -derivative.hi if derivative.hi < 0 else derivative.lo
            error = Q(max(abs(residual.lo), abs(residual.hi)), slope)
            enclosed = I.bounds(max(low, _rational(root)-error),
                                min(high, _rational(root)+error))
            result["root_enclosure"] = enclosed.decimal_bounds()
    return result
