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

"""Read-only shared-input response for the declared Guo (2026g) construction.

Coordinates are ln(c), ln(tau), ln(M_P), with c=kL and M_P in GeV.
Matter content, response domain and all readout definitions stay fixed.
Changing R is model sensitivity, not a random error in this Jacobian.
No uncertainty is assigned unless the caller supplies an input covariance.
"""
from __future__ import annotations
import math
from collections.abc import Mapping

from cg_core.window_weights import scalar_vector_window_ratio
from cg_frg.generation.sector_alpha import (
    alpha_up, sector_step, ladder_down, ladder_lepton,
)

INPUTS = ("c", "tau", "M_P")
GEV_TO_K = 1.160451812e13
R12 = 3.0 / 10.0
R23 = R12 / math.sqrt(3.0)
D = 2.0 * math.pi + R23
RATIO_READOUTS = {"m_tau_over_m_mu": ("m_tau_pred", "m_mu_pred")}
MASS_SPECIES = ("top", "charm", "tau", "muon", "bottom", "strange")
MASS_LOG_WEIGHTS = (8., -8., 9., -9., -17., 17.)
MASS_COMPARISON_LOG_ORDER = tuple(
    f"ln_{quantity}:{name}" for quantity in ("mass", "matching_factor")
    for name in MASS_SPECIES
)
_MASS_RATIO_WEIGHTS = {"m_t_over_m_c": 8., "m_tau_over_m_mu": 9.,
                       "m_b_over_m_s": -17.}
RUNNING_MASS_SPECIES = (*MASS_SPECIES, "electron")
MASS_SUM_RULE_WEIGHTS = (MASS_LOG_WEIGHTS+(0.,), (0., 0., -1., 2., 0., 0., -1.))
MASS_SUM_RULE_NAMES = ("six_mass", "charged_lepton")


def _positive_finite(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be finite and positive")
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be finite and positive") from error
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _validated_log_covariance(value, size, name):
    import numpy as np
    try:
        covariance = np.asarray(value, dtype=float)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{name} must be a finite {size}x{size} matrix") from error
    if covariance.shape != (size, size) or not np.all(np.isfinite(covariance)):
        raise ValueError(f"{name} must be a finite {size}x{size} matrix")
    scale = float(np.max(np.abs(covariance)))
    tolerance = 1e-12*scale
    if np.max(np.abs(covariance-covariance.T)) > tolerance:
        raise ValueError(f"{name} must be symmetric")
    covariance = covariance/2+covariance.T/2
    if float(np.linalg.eigvalsh(covariance)[0]) < -tolerance:
        raise ValueError(f"{name} must be positive semidefinite")
    return covariance


def _geometric_mass_relation(ratios, rows):
    terms = {key: weight*math.log(_positive_finite(ratios[key], key))
             for key, weight in _MASS_RATIO_WEIGHTS.items()}
    derivative = [math.fsum(weight*rows[key][i]
                            for key, weight in _MASS_RATIO_WEIGHTS.items())
                  for i in range(len(INPUTS))]
    return {"definition": "8 ln(m_t/m_c)+9 ln(m_tau/m_mu)-17 ln(m_b/m_s)",
            "mass_definition": "geometric spectral mass readouts",
            "log_ratio_terms": terms, "residual": math.fsum(terms.values()),
            "input_log_order": list(INPUTS), "input_log_derivative": derivative,
            "physical_mass_comparison_performed": False}


def compare_matched_mass_relation(species, joint_log_covariance=None, *,
                                  covariance_order=None, covariance_source=None):
    """Compare six physical masses after independently supplied matching.

    Each species in MASS_SPECIES supplies mass_GeV, mass_definition,
    mass_scheme, scale_GeV, mass_source, matching_factor, matching_source
    and matching_order. The factor C_i maps the geometric mass to exactly
    that physical definition at the recorded scale. For a pole mass, the
    scale is the reference scale of the matching calculation.

    The covariance order is MASS_COMPARISON_LOG_ORDER: six log masses in
    GeV followed by their six log C_i, including all cross correlations.
    The corrected combination is linear in these logarithms, so its
    variance is the exact linear covariance contraction for supplied log
    variables. Converting errors on masses to log errors may itself use
    a local approximation, which belongs to covariance_source.

    Missing data produce an incomplete comparison record. Complete inputs
    return a residual and its standard deviation; a statistical decision
    requires a separately stated probability model and test criterion.
    Matching factors are supplied by the caller and are never fitted here.
    """
    import numpy as np
    if not isinstance(species, Mapping):
        raise ValueError("species must be a mapping of six mass definitions")
    unknown = set(species)-set(MASS_SPECIES)
    if unknown:
        raise ValueError(f"unknown mass species: {sorted(unknown)}")
    numeric = ("mass_GeV", "scale_GeV", "matching_factor")
    textual = ("mass_definition", "mass_scheme", "mass_source",
               "matching_source", "matching_order")
    missing, inputs = [], {}
    for name in MASS_SPECIES:
        record = species.get(name)
        if record is None:
            missing.append(name)
            continue
        if not isinstance(record, Mapping):
            raise ValueError(f"{name} must contain its mass and matching definitions")
        inputs[name] = {}
        for field in (*numeric, *textual):
            value = record.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(f"{name}.{field}")
            elif field in numeric:
                inputs[name][field] = _positive_finite(value, f"{name}.{field}")
            elif not isinstance(value, str):
                raise ValueError(f"{name}.{field} must be a nonempty string")
            else:
                inputs[name][field] = value.strip()
    covariance = None
    if joint_log_covariance is None:
        missing.append("joint_log_covariance")
    else:
        covariance = _validated_log_covariance(joint_log_covariance, 12,
                                                "joint mass/matching log covariance")
    if covariance_order is None:
        missing.append("covariance_order")
    else:
        try:
            actual_order = tuple(covariance_order)
        except TypeError as error:
            raise ValueError("covariance_order must match MASS_COMPARISON_LOG_ORDER") from error
        if actual_order != MASS_COMPARISON_LOG_ORDER:
            raise ValueError("covariance_order must match MASS_COMPARISON_LOG_ORDER")
    if covariance_source is None or (isinstance(covariance_source, str)
                                      and not covariance_source.strip()):
        missing.append("covariance_source")
    elif not isinstance(covariance_source, str):
        raise ValueError("covariance_source must be a nonempty string")
    result = {"status": "incomplete" if missing else "evaluated",
              "comparison_performed": not missing,
              "missing_inputs": missing, "inputs": inputs,
              "species_order": list(MASS_SPECIES),
              "log_mass_weights": list(MASS_LOG_WEIGHTS),
              "covariance_log_order": list(MASS_COMPARISON_LOG_ORDER),
              "covariance_source": covariance_source,
              "corrected_residual": None, "standard_deviation": None,
              "standardized_residual": None,
              "definition": "sum_i w_i [ln(m_i^phys/GeV)-ln(C_i)]",
              "matching_factor_definition": "m_i^phys = C_i m_i^geometric"}
    if missing:
        return result
    log_masses = [math.log(inputs[name]["mass_GeV"]) for name in MASS_SPECIES]
    log_factors = [math.log(inputs[name]["matching_factor"]) for name in MASS_SPECIES]
    physical = math.fsum(w*x for w, x in zip(MASS_LOG_WEIGHTS, log_masses))
    correction = math.fsum(w*x for w, x in zip(MASS_LOG_WEIGHTS, log_factors))
    residual = math.fsum(w*(x-y) for w, x, y in
                         zip(MASS_LOG_WEIGHTS, log_masses, log_factors))
    weights = np.asarray((*MASS_LOG_WEIGHTS, *(-w for w in MASS_LOG_WEIGHTS)))
    contraction = covariance*np.outer(weights, weights)
    variance = max(0., math.fsum(float(x) for x in contraction.flat))
    deviation = math.sqrt(variance)
    result.update(physical_log_combination=physical, matching_log_correction=correction,
                  corrected_residual=residual, variance=variance,
                  standard_deviation=deviation,
                  standardized_residual=residual/deviation if deviation else None,
                  joint_log_covariance=covariance.tolist(),
                  covariance_gradient=weights.tolist(),
                  uncertainty_method="joint covariance of log masses and log matching factors")
    return result


def running_mass_sum_rules(masses_GeV, log_covariance, *, scale_GeV,
                           mass_definition, covariance_source):
    """Evaluate both geometric sum rules on a common running-mass record.

    Inputs follow RUNNING_MASS_SPECIES and must use one renormalization
    scheme, scale and VEV convention. The comparison hypothesis is that
    the two weighted finite matching corrections vanish at this scale.
    For m_i^running = C_i m_i^geometric, the returned residuals instead
    constrain W ln(C); they do not determine the individual C_i.

    The covariance of log masses is propagated jointly. A covariance
    obtained from errors on masses by dividing by their central values
    implements the delta method, not an exact log-normal error model.
    """
    import numpy as np
    if not isinstance(masses_GeV, Mapping) or set(masses_GeV) != set(RUNNING_MASS_SPECIES):
        raise ValueError("masses_GeV must specify all seven RUNNING_MASS_SPECIES")
    masses = np.array([_positive_finite(masses_GeV[n], n) for n in RUNNING_MASS_SPECIES])
    scale = _positive_finite(scale_GeV, "scale_GeV")
    for name, value in (("mass_definition", mass_definition),
                        ("covariance_source", covariance_source)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a nonempty string")
    covariance = _validated_log_covariance(log_covariance, 7, "running mass log covariance")
    weights = np.asarray(MASS_SUM_RULE_WEIGHTS)
    offsets = np.array([0., math.sqrt(2*math.pi)])
    residuals = weights@np.log(masses)-offsets
    output_covariance = weights@covariance@weights.T
    output_covariance = (output_covariance+output_covariance.T)/2
    deviations = np.sqrt(np.maximum(0., np.diag(output_covariance)))
    pulls = [float(r/s) if s else None for r, s in zip(residuals, deviations)]
    eigenvalues = np.linalg.eigvalsh(output_covariance)
    statistic = (float(residuals@np.linalg.solve(output_covariance, residuals))
                 if eigenvalues[0] > 1e-12*eigenvalues[-1] else None)
    return {"comparison_performed": True, "production_replacement": False,
            "scale_GeV": scale, "mass_definition": mass_definition.strip(),
            "covariance_source": covariance_source.strip(),
            "species_order": list(RUNNING_MASS_SPECIES),
            "masses_GeV": dict(zip(RUNNING_MASS_SPECIES, masses.tolist())),
            "log_mass_covariance": covariance.tolist(),
            "sum_rule_order": list(MASS_SUM_RULE_NAMES), "weights": weights.tolist(),
            "geometric_offsets": offsets.tolist(), "residuals": residuals.tolist(),
            "residual_covariance": output_covariance.tolist(),
            "standard_deviations": deviations.tolist(), "standardized_residuals": pulls,
            "correlation": (float(output_covariance[0, 1]/math.prod(deviations))
                            if all(deviations) else None),
            "joint_quadratic_statistic": statistic,
            "weighted_finite_matching_constraints": dict(zip(MASS_SUM_RULE_NAMES, residuals.tolist())),
            "zero_matching_test": {"hypothesis": "both weighted finite matching corrections vanish",
                                   "standardized_residuals": pulls,
                                   "joint_quadratic_statistic": statistic},
            "finite_matching_constraint": "W ln(C) equals the two measured residuals",
            "individual_matching_factors_determined": False}


def mass_sum_rule_beta_one_loop(up_yukawa, down_yukawa, lepton_yukawa, *, ckm=None):
    """One-loop SM derivatives d(sum rule)/d ln(mu), with no neutrino Yukawa.

    Yukawa eigenvalues use m=y*v/sqrt(2), ordered (u,c,t), (d,s,b),
    (e,mu,tau). ckm is a unitary 3x3 matrix with up rows and down columns;
    its default is the explicitly diagonal mixing approximation. Gauge
    terms and the common Yukawa trace cancel within each weight vector.
    The remaining eigenvalue beta is 3/2 times the self minus partner
    Yukawa square for quarks, and 3/2 times the self square for leptons,
    in units 1/(16*pi^2). See Machacek and Vaughn, Nucl. Phys. B236 (1984)
    221, and Arason et al., Phys. Rev. D46 (1992) 3945.
    """
    import numpy as np
    vectors = []
    for name, values in (("up_yukawa", up_yukawa), ("down_yukawa", down_yukawa),
                         ("lepton_yukawa", lepton_yukawa)):
        a = np.asarray(values, dtype=float)
        if a.shape != (3,) or not np.all(np.isfinite(a)) or np.any(a < 0):
            raise ValueError(f"{name} must contain three finite nonnegative eigenvalues")
        vectors.append(a)
    mixing = np.eye(3, dtype=complex) if ckm is None else np.asarray(ckm, dtype=complex)
    if (mixing.shape != (3, 3) or not np.all(np.isfinite(mixing))
            or not np.allclose(mixing@mixing.conj().T, np.eye(3), rtol=0., atol=1e-10)):
        raise ValueError("ckm must be a unitary finite 3x3 matrix")
    u2, d2, e2 = (a*a for a in vectors)
    probabilities = np.abs(mixing)**2
    factor = 1.5/(16*math.pi**2)
    up = factor*(u2-probabilities@d2)
    down = factor*(d2-probabilities.T@u2)
    leptons = factor*e2
    beta_ordered = np.array([up[2], up[1], leptons[2], leptons[1],
                             down[2], down[1], leptons[0]])
    beta = np.asarray(MASS_SUM_RULE_WEIGHTS)@beta_ordered
    return {"sum_rule_order": list(MASS_SUM_RULE_NAMES),
            "derivatives_per_log_scale": beta.tolist(),
            "gauge_contributions": [0., 0.], "common_trace_contributions": [0., 0.],
            "mixing_definition": "diagonal CKM" if ckm is None else "supplied unitary CKM",
            "order": "one-loop SM Yukawa beta functions; neutrino Yukawa omitted"}


def charged_lepton_qed_log_matching(pole_masses_GeV, *, scale_GeV, alpha):
    """One-loop QED pole-to-MSbar logarithmic matching for e, mu and tau.

    ln(m_l(mu)/M_l) = -alpha/pi [1+3/2 ln(mu/M_l)] + O(alpha^2).
    The formula is expanded consistently in logarithms; omitted orders
    are not exponentiated into a claimed higher-order mass prediction.
    See Xing, Zhang and Zhou, Phys. Rev. D77 (2008) 113016, Sec. II B.
    """
    names = ("electron", "muon", "tau")
    if not isinstance(pole_masses_GeV, Mapping) or set(pole_masses_GeV) != set(names):
        raise ValueError("pole_masses_GeV must contain electron, muon and tau")
    mu = _positive_finite(scale_GeV, "scale_GeV")
    coupling = float(alpha)
    if isinstance(alpha, bool) or not math.isfinite(coupling) or coupling < 0:
        raise ValueError("alpha must be finite and nonnegative")
    masses = [_positive_finite(pole_masses_GeV[n], n) for n in names]
    logarithms = [math.log(m) for m in masses]
    shifts = [-coupling/math.pi*(1+1.5*(math.log(mu)-x)) for x in logarithms]
    weights = (-1., 2., -1.)
    pole_combination = math.fsum(w*x for w, x in zip(weights, logarithms))
    correction = math.fsum(w*x for w, x in zip(weights, shifts))
    return {"species_order": list(names), "scale_GeV": mu, "alpha": coupling,
            "pole_to_MSbar_log_factors": dict(zip(names, shifts)),
            "pole_log_combination": pole_combination,
            "matching_log_correction": correction,
            "running_log_combination": pole_combination+correction,
            "running_sum_rule_residual": pole_combination+correction-math.sqrt(2*math.pi),
            "order": "one-loop pure QED, expanded in logarithmic masses"}


def charged_lepton_finite_transfer(initial_yukawa, *, common_log_factor, self_integral):
    """Exact finite solution of the one-loop charged-lepton eigenvalue equations.

    For dy_i/dt=y_i[A(t)+3*y_i^2/(32*pi^2)], let
    E=exp(integral A dt), I=3/(16*pi^2)*integral E^2 dt.
    Then y_i=E*y_i0/sqrt(1-I*y_i0^2). A includes the common gauge
    and Yukawa trace of the same path; neutrino Yukawa couplings are absent.
    I is signed for reverse scale evolution. These quantities describe
    running within a stated scheme, separately from finite mass matching.
    """
    import numpy as np
    initial = np.asarray(initial_yukawa, dtype=float)
    if (initial.shape != (3,) or not np.isfinite(initial).all()
            or np.any(initial <= 0) or not math.isfinite(common_log_factor)
            or not math.isfinite(self_integral)):
        raise ValueError("three positive Yukawa values and finite path integrals required")
    arguments = self_integral*initial**2
    if np.any(arguments >= 1):
        raise ValueError("finite transfer must remain before a Yukawa denominator vanishes")
    logs = np.log1p(-arguments)
    log_factors = common_log_factor-.5*logs
    final = initial*np.exp(log_factors)
    if not np.isfinite(final).all() or np.any(final <= 0):
        raise ValueError("finite positive transferred Yukawa values required")
    correction = .5*float(logs[0]-2*logs[1]+logs[2])
    return {"species_order": ["electron", "muon", "tau"],
            "initial_yukawa": initial.tolist(), "final_yukawa": final.tolist(),
            "common_log_factor": float(common_log_factor), "self_integral": float(self_integral),
            "log_transfer_factors": log_factors.tolist(),
            "charged_lepton_log_correction": correction,
            "minimum_denominator": float(np.min(1-arguments)),
            "scope": "exact solution of one-loop running with a common coefficient; finite mass matching separate"}


def charged_lepton_transfer_enclosure(initial_yukawa, *, log_scale_span,
                                      common_coefficient_bounds):
    """Outward interval bound on a finite forward one-loop lepton transfer.

    The caller supplies a proved uniform interval for A(t) over 0<=t<=T.
    Integrating exp(2*A_-*t)<=E(t)^2<=exp(2*A_+*t) encloses I.
    Interval arithmetic then encloses the weighted logarithmic correction.
    The bounds are conditional on this input enclosure, not inferred from
    discrete samples. A denominator interval containing zero is rejected.
    """
    from mpmath.ctx_iv import MPIntervalContext
    initial = [_positive_finite(x, "initial_yukawa") for x in initial_yukawa]
    if len(initial) != 3 or not math.isfinite(log_scale_span) or log_scale_span < 0:
        raise ValueError("three positive Yukawa values and nonnegative log-scale span required")
    bounds = tuple(float(x) for x in common_coefficient_bounds)
    if len(bounds) != 2 or not all(math.isfinite(x) for x in bounds) or bounds[0] > bounds[1]:
        raise ValueError("ordered finite common-coefficient bounds required")
    iv = MPIntervalContext()
    iv.dps = 50
    T = iv.mpf(log_scale_span)
    factor = 3/(16*iv.pi**2)
    def integral_bound(a):
        return factor*T if a == 0 else factor*iv.expm1(2*iv.mpf(a)*T)/(2*iv.mpf(a))
    low, high = integral_bound(bounds[0]), integral_bound(bounds[1])
    integral = iv.mpf([low.a, high.b])
    denominator = [1-integral*iv.mpf(y)**2 for y in initial]
    if any(d.a <= 0 for d in denominator):
        raise ValueError("the supplied bounds do not certify positive Yukawa denominators")
    correction = (iv.log(denominator[0])-2*iv.log(denominator[1])
                  +iv.log(denominator[2]))/2
    def endpoints(value):
        return [math.nextafter(float(value.a), -math.inf),
                math.nextafter(float(value.b), math.inf)]
    return {"initial_yukawa": initial, "log_scale_span": float(log_scale_span),
            "common_coefficient_bounds": list(bounds),
            "self_integral_interval": endpoints(integral),
            "charged_lepton_log_correction_interval": endpoints(correction),
            "minimum_denominator_lower_bound": min(endpoints(d)[0] for d in denominator),
            "enclosure_method": "50-digit interval arithmetic with outward binary-float endpoints",
            "assumption": "supplied uniform bounds enclose the same-path common coefficient throughout the interval",
            "operation_counts": {"endpoint_exponential_integrals": 2,
                                 "interval_logarithms": 3}}


def lepton_matching_spread_bound(required_interval, *, known_correction_interval):
    """Necessary flavour spread after separately computed contributions.

    If epsilon=2*x_mu-x_e-x_tau and x_l=ln(C_l), then
    max(x_l)-min(x_l)>=abs(epsilon)/2, sharply. Intervals on the
    required and independently computed corrections give a conservative
    necessary bound; they neither solve for C_l nor predict a correction.
    """
    intervals = []
    for name, values in (("required_interval", required_interval),
                         ("known_correction_interval", known_correction_interval)):
        pair = tuple(float(x) for x in values)
        if len(pair) != 2 or not all(math.isfinite(x) for x in pair) or pair[0] > pair[1]:
            raise ValueError(f"{name} must be an ordered finite interval")
        intervals.append(pair)
    required, known = intervals
    residual = (math.nextafter(required[0]-known[1], -math.inf),
                math.nextafter(required[1]-known[0], math.inf))
    distance = max(0., residual[0], -residual[1])
    lower = max(0., math.nextafter(distance/2, -math.inf))
    return {"remaining_log_correction_interval": list(residual),
            "minimum_log_matching_spread": lower,
            "minimum_largest_log_deviation_from_common_factor": max(0., math.nextafter(lower/2, -math.inf)),
            "individual_matching_factors_determined": False,
            "interpretation": "necessary bound on the remaining finite flavour-dependent matching"}


def _source(c, tau, M_P):
    if not all(math.isfinite(v) and v > 0 for v in (c, tau, M_P)):
        raise ValueError("c, tau and M_P must be finite and positive")
    if tau >= 0.25:
        raise ValueError("tau must lie below the squash singularity 1/4")
    kappa = math.sqrt((1 + 2*tau) / (1 - 4*tau)**2.5)
    x = 2*tau*kappa
    if x >= 0.25:
        raise ValueError("the declared positive vacuum-density branch requires 1-4x>0")
    return x


def _gauge_and_ladder(c, tau):
    """Algebraic coupling boundaries and ladder, with analytic derivatives.

    The hypercharge boundary uses the specified one-loop transfer between
    k_GUT and M_G. The two-loop colour shooting problem has its own solver.
    All derivatives hold the finite matter content and matching rules fixed.
    """
    inverse_alpha = c**5/2 + 1/3 - tau*tau*math.pi/2
    log_scales = math.log(tau*c/math.sqrt(3))
    b1, b2 = 41/10, -19/6
    kappa = math.sqrt((1+2*tau)/(1-4*tau)**2.5)
    h = R23*5/8
    factor = kappa*(1-h*tau)
    weak_inverse = inverse_alpha/(4*math.pi) - b2/(8*math.pi**2)*log_scales
    hypercharge_inverse = weak_inverse/factor**2 + b1/(8*math.pi**2)*log_scales
    if min(inverse_alpha, weak_inverse, hypercharge_inverse, factor) <= 0:
        raise ValueError("the specified positive gauge-boundary branch is required")
    gauge = {"g2_MG": math.sqrt(4*math.pi/inverse_alpha),
             "g1_MG_geo": 1/math.sqrt(hypercharge_inverse)}
    factor_tau = tau/(1+2*tau)+5*tau/(1-4*tau)-h*tau/(1-h*tau)
    weak_derivatives, hypercharge_derivatives = [], []
    for inverse_derivative, factor_derivative in ((5*c**5/2, 0.),
                                                   (-math.pi*tau*tau, factor_tau)):
        weak_derivatives.append(-inverse_derivative/(2*inverse_alpha))
        boundary_derivative = inverse_derivative/(4*math.pi)-b2/(8*math.pi**2)
        hypercharge_derivative = ((boundary_derivative-2*weak_inverse*factor_derivative)
                                  /factor**2+b1/(8*math.pi**2))
        hypercharge_derivatives.append(-hypercharge_derivative/(2*hypercharge_inverse))
    rows = {"g2_MG": (*weak_derivatives, 0.),
            "g1_MG_geo": (*hypercharge_derivatives, 0.)}
    tilt = tau*scalar_vector_window_ratio()
    cmb = c*(1-tau/4)
    au = alpha_up(c, tau)
    delta = sector_step(tilt, cmb)
    indices = {"alpha_up": au, "alpha_down": ladder_down(au, delta),
               "alpha_lepton": ladder_lepton(au, delta)}
    delta_tau = delta*(1-tau/(4-tau))
    for key, multiplier, ratio in (("alpha_up", 0., "m_t_over_m_c"),
                                  ("alpha_down", 18/17, "m_b_over_m_s"),
                                  ("alpha_lepton", 2., "m_tau_over_m_mu")):
        index = indices[key]
        if index <= 0:
            raise ValueError("positive ladder indices are required for logarithmic sensitivity")
        derivatives = (c-multiplier*delta, -2*tau-multiplier*delta_tau, 0.)
        rows[key] = tuple(value/index for value in derivatives)
        rows[ratio] = tuple(2*value for value in derivatives)
        indices[ratio] = math.exp(2*index)
    return {**gauge, **indices}, rows


def evaluate(c: float, tau: float, M_P: float) -> dict:
    """Return central values in the production store's stated units.

    v,M_G,k_GUT,H0,Traw are GeV; me is MeV; neutrinos are eV;
    rho is GeV^4; Tcorr is K. These are conditional closed forms,
    not new fits, a new response-domain selection or a full dynamical flow.
    """
    x = _source(c, tau, M_P)
    M_G = M_P*math.sqrt(math.pi)/c
    k_GUT = M_P*math.sqrt(math.pi)*tau/math.sqrt(3)
    v = M_G*3/(16*math.pi**3)*math.exp(-4*math.pi*c)*(1-x)
    me = M_P*math.exp(-20*c)*(1-x)*1e3
    m3 = v*v*(2*math.pi)**2/k_GUT*(1+x)  # GeV before output conversion
    m2, m1 = m3*R23, m3*R23*R12
    rho = (2/3)*m1**4*(1-4*x)
    hubble = math.sqrt(math.pi*rho/D)/M_P
    temperature = m1*R12/math.pi*(1-x)*(1-tau/2)
    photon_factor = 1-tau/math.pi**2
    result = {"M_G": M_G, "k_GUT": k_GUT, "v_HIGGS": v,
              "m_t_pred": v/math.sqrt(2),
              "m_e_pred": me, "m_nu1": m1*1e9, "m_nu2": m2*1e9,
              "m_nu3": m3*1e9, "rho_Lambda": rho, "H0_GEV": hubble,
              "T_CMB_GeV": temperature,
              "T_CMB_corrected_K": temperature*photon_factor*GEV_TO_K,
              "Omega_Lambda": D/(3*math.pi),
              "photon_zero_mode_Cgamma": photon_factor}
    result.update(_gauge_and_ladder(c, tau)[0])
    if not all(math.isfinite(v) and v > 0 for v in result.values()):
        raise ValueError("closed-form response is outside representable positive float range")
    return result


def log_jacobian(c: float, tau: float, M_P: float) -> dict:
    """Rows d ln(output) / d (ln c, ln tau, ln M_P), analytically."""
    x = _source(c, tau, M_P)
    dx = x*(1 + tau/(1+2*tau) + 5*tau/(1-4*tau))
    vt = -dx/(1-x)
    nc, nt = -2-8*math.pi*c, 2*vt-1+dx/(1+x)
    rhot = 4*nt-4*dx/(1-4*x)
    tt = nt+vt-tau/(2-tau)
    rows = {"M_G": (-1., 0., 1.), "k_GUT": (0., 1., 1.),
            "v_HIGGS": (-1-4*math.pi*c, vt, 1.),
            "m_t_pred": (-1-4*math.pi*c, vt, 1.),
            "m_e_pred": (-20*c, vt, 1.),
            "m_nu1": (nc, nt, 1.), "m_nu2": (nc, nt, 1.),
            "m_nu3": (nc, nt, 1.),
            "rho_Lambda": (4*nc, rhot, 4.),
            "H0_GEV": (2*nc, rhot/2, 1.),
            "T_CMB_GeV": (nc, tt, 1.),
            "T_CMB_corrected_K": (nc, tt-tau/(math.pi**2-tau), 1.),
            "Omega_Lambda": (0., 0., 0.),
            "photon_zero_mode_Cgamma": (0., -tau/(math.pi**2-tau), 0.)}
    rows.update(_gauge_and_ladder(c, tau)[1])
    return rows


def propagate_log_covariance(c, tau, M_P, input_log_covariance, *, outputs=None):
    """Linearized J Sigma J^T for a caller-supplied log-input covariance.

    This supplies no probability distribution, default error or confidence
    interval. A covariance in dimensional input coordinates must first be
    transformed by the caller to (ln c,ln tau,ln M_P).
    """
    import numpy as np
    covariance = _validated_log_covariance(input_log_covariance, 3, "input log covariance")
    rows = log_jacobian(c, tau, M_P)
    names = list(rows) if outputs is None else list(outputs)
    jacobian = np.asarray([rows[name] for name in names])
    result = jacobian @ covariance @ jacobian.T
    return {"input_order": list(INPUTS), "output_order": names,
            "output_log_covariance": result.tolist(),
            "method": "linearized J Sigma J^T; supplied log-input covariance only"}


def evaluate_records(records, *, relative_tolerance=2e-10):
    """Cross-check a supplied current-run record dictionary without writing it.

    Accepts either records, a top-level {'parameters': records}, or plain
    values. Small residuals verify shared formulas; they are not independent
    experimental or dynamical evidence.
    """
    relative_tolerance = _positive_finite(relative_tolerance, "relative_tolerance")
    if "parameters" in records:
        records = records["parameters"]
    absent = object()

    def read_value(key):
        rec = records.get(key, absent)
        return rec["value"] if isinstance(rec, dict) and "value" in rec else rec

    p = {key: read_value(key) for key in ("kL", "tau", "M_P")}
    expected = evaluate(p["kL"], p["tau"], p["M_P"])
    required = ("eta_b", "m_p", "Omega_b", "Omega_Sigma",
                "eta_B_photon_zero_mode_factor")
    gauge_keys = ("g1_MG_geo", "g2_MG", "g3_MG_geo", "M_G", "v_HIGGS",
                  "cp_jarlskog_magnitude", "eta_b")
    for key in dict.fromkeys((*expected, *required, *gauge_keys)):
        value = read_value(key)
        if value is not absent:
            p[key] = value
        elif key in RATIO_READOUTS:
            numerator, denominator = (read_value(name) for name in RATIO_READOUTS[key])
            if numerator is not absent and denominator is not absent:
                top, bottom = RATIO_READOUTS[key]
                p[key] = _positive_finite(numerator, top)/_positive_finite(denominator, bottom)
    checks, missing = {}, []

    def check(name, actual, reference):
        residual = actual/reference-1 if reference else actual-reference
        checks[name] = {"actual": actual, "expected": reference,
                        "relative_residual": residual,
                        "passed": math.isfinite(residual) and abs(residual) <= relative_tolerance}

    for key, value in expected.items():
        if key in p:
            check(key, p[key], value)
        else:
            missing.append(key)
    for key in required:
        if key not in p and key not in missing:
            missing.append(key)
    if not missing:
        check("neutrino_ratio_12", p["m_nu1"]/p["m_nu2"], R12)
        check("neutrino_ratio_23", p["m_nu2"]/p["m_nu3"], R23)
        raw = p["T_CMB_GeV"]
        corrected = p["T_CMB_corrected_K"]/GEV_TO_K
        photon_density = 2*1.2020569031595942*raw**3/math.pi**2
        critical = 3*p["H0_GEV"]**2*p["M_P"]**2
        check("baryon_budget", p["Omega_b"], p["eta_b"]*photon_density*p["m_p"]/critical)
        check("flat_budget", p["Omega_b"]+p["Omega_Sigma"]+p["Omega_Lambda"], 1.)
        check("eta_photon_invariance", p["eta_B_photon_zero_mode_factor"]*(corrected/raw)**3, 1.)
        x = _source(p["kL"], p["tau"], p["M_P"])
        A = (2/3)*(1-4*x)
        B = R12/math.pi*(1-x)*(1-p["tau"]/2)
        C = 1-p["tau"]/math.pi**2
        check("mass_free_temperature_hubble_ratio", corrected**2/(p["M_P"]*p["H0_GEV"]),
              C*C*B*B*math.sqrt(D/(math.pi*A)))
    rows = log_jacobian(p["kL"], p["tau"], p["M_P"])
    geometric_relation = None
    if all(key in p for key in _MASS_RATIO_WEIGHTS):
        geometric_relation = _geometric_mass_relation(p, rows)
        check("geometric_log_mass_relation", geometric_relation["residual"], 0.)
        for key, derivative in zip(INPUTS, geometric_relation["input_log_derivative"]):
            check(f"geometric_log_mass_relation_derivative_{key}", derivative, 0.)
    if all(key in p for key in gauge_keys):
        from cg_core.gauge_running import run_geometric
        g2 = run_geometric(tuple(p[k] for k in gauge_keys[:3]), p["M_G"], p["v_HIGGS"])[1]
        alpha_w = g2*g2/(4*math.pi)
        check("cp_weak_baryogenesis_readout", p["eta_b"], p["cp_jarlskog_magnitude"]*alpha_w**2/56)
    return {"input_order": list(INPUTS), "log_jacobian": rows,
            "geometric_mass_relation": geometric_relation,
            "checks": checks, "missing": missing,
            "passed": not missing and all(item["passed"] for item in checks.values()),
            "scope": "shared response identities at fixed matter content and response domain"}
