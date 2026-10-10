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

"""The prescribed three-gauge-coupling flow with fixed geometric y0=1.

This is not the comparison branch with running Yukawa/quartic couplings.
Step doubling supplies an estimated integration error, not a rigorous interval.
The common-origin boundary is tested by a fresh forward integration.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from cg_core.beta_functions import beta_gauge
from cg_core.rk4 import rk4_integrate


@dataclass(frozen=True)
class CoupledBoundary:
    """Explicit dimensionless (g1_GUT,g2,g3,y_t,lambda_H) at scale in GeV.

    The quartic convention is V=lambda_H (H^dagger H)^2. A source names
    the supplied matching calculation; its text is provenance, not proof.
    No values are loaded from a comparison branch or parameter database.
    """
    values: tuple[float, float, float, float, float]
    scale: float
    scheme: str
    source: str


@dataclass(frozen=True)
class RGThreshold:
    """Directional EFT matching at a supplied scale on the requested path.

    match(values) gives the five couplings just beyond this threshold;
    beta_after(values) is the specified EFT beta function beyond it.
    The map applies only in the declared run direction; inverse matching
    must be supplied separately. It is never inferred from continuity.
    """
    scale: float
    match: object
    beta_after: object
    scheme_after: str
    source: str
    direction: str


@dataclass(frozen=True)
class GaugeRun:
    couplings: tuple[float, float, float]
    estimated_abs_error: tuple[float, float, float]
    steps: int
    refinements: int


def _positive(values, name):
    if not all(math.isfinite(float(x)) and x > 0 for x in values):
        raise ValueError(f"{name} must contain finite positive values")


def geometric_run(initial, scale_from, scale_to, *, rtol=2e-11,
                  atol=2e-13, steps_per_efold=8, max_refinements=10):
    """Return a converged RK4 solution and the step-doubling error estimate.

    The fine solution is retained without Richardson extrapolation. Success
    requires each |fine-coarse|/15 to be within atol+rtol*|fine|. The estimate
    assumes the fourth-order asymptotic regime; independent-variable checks
    and observed order tests are provided in the numeric contract tests.
    """
    initial = tuple(float(x) for x in initial)
    if len(initial) != 3:
        raise ValueError("geometric running requires exactly (g1,g2,g3)")
    _positive(initial, "couplings")
    _positive((scale_from, scale_to, steps_per_efold), "scales and step density")
    if rtol <= 0 or atol < 0 or max_refinements < 1:
        raise ValueError("invalid error-control settings")
    duration = math.log(scale_to) - math.log(scale_from)
    if duration == 0:
        return GaugeRun(initial, (0.0, 0.0, 0.0), 0, 0)
    steps = max(1, math.ceil(abs(duration) * steps_per_efold))

    def rhs(g):
        _positive(g, "intermediate couplings")
        return beta_gauge(*g, 1.0)

    coarse = rk4_integrate(rhs, initial, duration, steps)
    for refinement in range(1, max_refinements + 1):
        steps *= 2
        fine = tuple(rk4_integrate(rhs, initial, duration, steps))
        _positive(fine, "final couplings")
        errors = tuple(abs(a - b) / 15.0 for a, b in zip(fine, coarse))
        if all(e <= atol + rtol * abs(v) for e, v in zip(errors, fine)):
            return GaugeRun(fine, errors, steps, refinement)
        coarse = fine
    raise RuntimeError("geometric RK4 integration failed its error tolerance")


def run_geometric(initial, scale_from, scale_to, **settings):
    """Tuple-only convenience API for the same checked geometric flow."""
    return geometric_run(initial, scale_from, scale_to, **settings).couplings


def common_origin(g1, g2, scale_from, scale_breaking, *, K_long=8.0 / 3.0,
                  boundary_rtol=2e-12, max_iterations=80, **settings):
    """Shoot g3(scale_from) to g3=g2*(1+alpha2**2/K_long) at breaking.

    g1 and g2 at scale_from remain fixed. Bisection checks the actual forward
    residual; a reversible round-trip alone is not a boundary certificate.
    """
    _positive((g1, g2, K_long, boundary_rtol), "boundary inputs")
    def evaluate(g3):
        run = geometric_run((g1, g2, g3), scale_from, scale_breaking, **settings)
        _, weak, colour = run.couplings
        target = weak * (1.0 + (weak * weak / (4.0 * math.pi)) ** 2 / K_long)
        return colour - target, target, run

    lo, hi = 0.25 * g2, 1.5 * g2
    flo, _, _ = evaluate(lo)
    fhi, _, _ = evaluate(hi)
    if flo * fhi > 0:
        raise RuntimeError("common-origin root not bracketed in the prescribed positive branch")
    for iteration in range(1, max_iterations + 1):
        mid = (lo + hi) / 2.0
        residual, target, run = evaluate(mid)
        if abs(residual) <= boundary_rtol * target:
            # Re-evaluate with tighter integration tolerance, so acceptance
            # is not based solely on the trial integrator's own discretization.
            verify_settings = dict(settings)
            verify_settings["rtol"] = min(settings.get("rtol", 2e-11), 2e-13)
            verify_settings["atol"] = min(settings.get("atol", 2e-13), 2e-15)
            verified = geometric_run((g1, g2, mid), scale_from, scale_breaking,
                                     **verify_settings)
            weak, colour = verified.couplings[1:]
            target = weak * (1.0 + (weak * weak / (4.0 * math.pi)) ** 2 / K_long)
            residual = colour - target
            if abs(residual) > 4.0 * boundary_rtol * target:
                raise RuntimeError("common-origin forward residual failed finer integration")
            return {"g3_initial": mid, "at_breaking": verified.couplings,
                    "relative_residual": residual / target,
                    "iterations": iteration, "integration": verified}
        if flo * residual <= 0:
            hi = mid
        else:
            lo, flo = mid, residual
    raise RuntimeError("common-origin boundary solve did not converge")


def coupled_run(boundary, scale_to, *, thresholds=(), rtol=2e-10,
                atol=2e-12, max_step=.15, initial_beta=None):
    """Joint gauge/Yukawa/quartic evolution with explicit directional matching.

    The default beta is the repository's two-loop top-sector MSbar system;
    light-Yukawa feedback is omitted by that truncation. The quartic may
    cross zero; such a crossing is reported rather than numerically clipped.
    A changed particle content below a threshold requires both its matching
    map and its beta function. This API does not upgrade the production
    fixed-y0 flow without an independently established canonical boundary.
    DOP853 errors are numerical estimates, not rigorous interval bounds.
    """
    import numpy as np
    from scipy.integrate import solve_ivp
    from cg_core.beta_functions import derivatives5
    if not isinstance(boundary,CoupledBoundary):
        raise TypeError("an explicit CoupledBoundary is required")
    if not boundary.source.strip() or not boundary.scheme.strip():
        raise ValueError("matching source and scheme must be stated")
    if initial_beta is None and boundary.scheme != "MSbar":
        raise ValueError("the default top-sector beta uses scheme='MSbar'")
    _positive((boundary.scale,scale_to,rtol,max_step),"scales and tolerances")
    if not math.isfinite(atol) or atol <= 0:
        raise ValueError("positive finite absolute tolerance required")
    def validate(values):
        a = np.asarray(values,dtype=float)
        if a.shape!=(5,) or not np.isfinite(a).all() or np.any(a[:3]<=0) or a[3]<0:
            raise ValueError("finite five-coupling state, positive gauge couplings and y_t>=0 required")
        return a
    y = validate(boundary.values)
    direction = "down" if scale_to<boundary.scale else "up"
    path = list(thresholds)
    previous = boundary.scale
    for threshold in path:
        if not isinstance(threshold,RGThreshold):
            raise TypeError("thresholds must be RGThreshold records")
        if threshold.direction != direction or not threshold.source.strip() or not threshold.scheme_after.strip():
            raise ValueError("threshold direction, scheme and matching source required")
        if not callable(threshold.match) or not callable(threshold.beta_after):
            raise ValueError("each threshold requires a matching map and EFT beta")
        inside = (scale_to<threshold.scale<previous if direction=="down"
                  else previous<threshold.scale<scale_to)
        if not inside:
            raise ValueError("thresholds must be strictly ordered inside the run interval")
        previous = threshold.scale
    rhs = derivatives5 if initial_beta is None else initial_beta
    mu,scheme = boundary.scale,boundary.scheme
    segments,matching = [],[]
    negative_quartic = bool(y[4]<0)
    for threshold in [*path,None]:
        end = scale_to if threshold is None else threshold.scale
        def derivative(t,state):
            value = np.asarray(rhs(validate(state)),dtype=float)
            if value.shape!=(5,) or not np.isfinite(value).all():
                raise ArithmeticError("EFT beta returned a nonfinite or wrong-shaped derivative")
            return value
        if end != mu:
            solution = solve_ivp(derivative,(math.log(mu),math.log(end)),y,
                                 method="DOP853",rtol=rtol,atol=atol,max_step=max_step)
            if not solution.success:
                raise RuntimeError(solution.message)
            y = validate(solution.y[:,-1])
            negative_quartic |= bool(np.any(solution.y[4]<0))
            segments.append({"from":mu,"to":end,"scheme":scheme,
                             "steps":len(solution.t)-1,"nfev":solution.nfev})
        if threshold is not None:
            before = y.copy()
            y = validate(threshold.match(tuple(y)))
            matching.append({"scale":end,"before":tuple(before),"after":tuple(y),
                             "source":threshold.source,"scheme_after":threshold.scheme_after})
            negative_quartic |= bool(y[4]<0)
            rhs,scheme = threshold.beta_after,threshold.scheme_after
        mu = end
    return {"couplings":tuple(float(v) for v in y),"scale":float(scale_to),
            "scheme":scheme,"boundary_source":boundary.source,"segments":segments,
            "thresholds":matching,"negative_quartic_encountered":negative_quartic,
            "flow_convention":"coupled-top-sector","rtol":rtol,"atol":atol}


def coupled_boundary_residual(boundary, scale_to, residual, **settings):
    """Evaluate a supplied physical boundary equation after a fresh joint run.

    residual(couplings, scale, scheme) must encode the independent boundary
    relation. This evaluation performs no parameter fitting and imports no
    observed low-energy boundary values.
    """
    import numpy as np
    result = coupled_run(boundary,scale_to,**settings)
    value = np.asarray(residual(result["couplings"],result["scale"],result["scheme"]),dtype=float)
    if not np.isfinite(value).all():
        raise ValueError("boundary residual must be finite")
    return {"run":result,"residual":value,"max_abs_residual":float(np.max(np.abs(value)))}


def coupled_common_origin(boundary, scale_breaking, *, K_long=8./3.,
                          bracket=None, boundary_rtol=2e-11, **settings):
    """Solve the common colour condition with all five couplings evolving.

    Only the initial g3 is solved. All other action boundary inputs retain
    their declared values, scale and scheme. A bracket plus independently
    refined forward residual certifies this conditional boundary solution;
    it neither identifies those inputs physically nor changes production.
    """
    from scipy.optimize import brentq
    if not isinstance(boundary, CoupledBoundary):
        raise TypeError("an explicit CoupledBoundary is required")
    _positive((K_long, boundary_rtol), "boundary settings")
    initial = tuple(boundary.values)
    if len(initial) != 5:
        raise ValueError("five initial couplings required")
    lower, upper = (.25*initial[1], 1.5*initial[1]) if bracket is None else bracket
    _positive((lower, upper), "colour bracket")
    if lower >= upper:
        raise ValueError("ordered initial colour bracket required")
    def trial(g3, options):
        current = CoupledBoundary((initial[0], initial[1], g3, initial[3], initial[4]),
                                  boundary.scale, boundary.scheme, boundary.source)
        run = coupled_run(current, scale_breaking, **options)
        weak, colour = run["couplings"][1:3]
        target = weak*(1+(weak**2/(4*math.pi))**2/K_long)
        return colour-target, target, run
    options = dict(settings)
    options["rtol"] = min(settings.get("rtol", 2e-10), 2e-12)
    options["atol"] = min(settings.get("atol", 2e-12), 2e-14)
    f_lower, _, _ = trial(lower, options)
    f_upper, _, _ = trial(upper, options)
    if f_lower*f_upper >= 0:
        raise ValueError("common colour residual must have opposite signs at bracket endpoints")
    root = brentq(lambda x: trial(x, options)[0], lower, upper,
                  xtol=boundary_rtol*min(1., initial[1])*.1, rtol=1e-14)
    refined = dict(options)
    refined["rtol"] = min(options["rtol"], 2e-13)
    refined["atol"] = min(options["atol"], 2e-15)
    refined["max_step"] = min(options.get("max_step", .15), .075)
    residual, target, run = trial(root, refined)
    if abs(residual) > boundary_rtol*abs(target):
        raise ArithmeticError("coupled common colour residual failed independent refinement")
    solved = (initial[0], initial[1], root, initial[3], initial[4])
    return {"initial_couplings": solved, "scale_from_GeV": boundary.scale,
            "scheme": boundary.scheme, "source": boundary.source,
            "g3_initial": root, "bracket": [lower, upper],
            "bracket_residuals": [f_lower, f_upper], "at_breaking": run,
            "residual": residual, "relative_residual": residual/target,
            "boundary_rtol": boundary_rtol, "K_long": K_long,
            "physical_matching_inferred": False}
