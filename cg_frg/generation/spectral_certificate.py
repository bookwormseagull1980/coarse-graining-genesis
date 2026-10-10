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

"""Read-only R=5 endpoint and joint-generation certificate.

Implements Guo (2026g) Appendix C's eight branch integrals and Appendix D's
midpoint bound |f''|<=726, U<9/2, with outward rational arithmetic.
The response domain R=5 is part of the input definition. This certificate
does not replace it by the distinct complete-Gaussian response.
"""
from fractions import Fraction as Q

from cg_core.content_response import finite_source_response, screening_compatibility
from cg_core.rational_interval import Interval as I, pi_interval, exp_negative, GRID


def _integral(a, b, steps, pi):
    a, b = I.point(a), I.point(b)
    upper = (5*pi-a).sqrt()
    width = upper/steps
    value = I.point(0)
    for j in range(steps):
        u = width*Q(2*j+1, 2)
        q = u*u+a
        value += (q/(q+b))**2 * exp_negative(q/pi)
    midpoint = width*value
    error = I.point(Q(726, 24*steps**2)*Q(9, 2)**3)
    return I(max(0, midpoint.lo-error.hi), midpoint.hi+error.hi)


def certify_endpoint(steps=4096):
    """Compute a mathematical enclosure; never reads or writes parameter stores."""
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ValueError("steps must be a positive integer")
    pi = pi_interval()
    tau = finite_source_response()["tau"]
    b_v, b_f = tau**2/6, 3*tau**2/8
    bosons = [(0, Q(3,4), 4), (8, Q(3,4), 36),
              (4, Q(3,2)+b_v, 192), (4, 1+b_v, 72), (4, b_v, 24)]
    fermions = [(Q(9,4), b_f, 56), (Q(25,4), b_f, 192),
                (Q(49,4), b_f, 336)]
    prefactor = 27/(128*pi**3)
    def coefficient(rows):
        return prefactor*sum((_integral(a,b,steps,pi)*d for a,b,d in rows), I.point(0))
    a5, b5 = coefficient(bosons), coefficient(fermions)
    selection = screening_compatibility()
    g = selection["generations"]
    c = a5+g*b5
    if c.lo <= 0:
        raise ArithmeticError("quadrature enclosure too coarse to certify a positive root")
    capacity = c*c
    lower, upper = Q(4*g-1, 2), Q(4*g+3, 2)
    platform = capacity.lo > I.point(lower).hi and capacity.hi <= I.point(upper).lo
    # F(c)=A/c-4/27 is strictly decreasing on c>0 for positive A.
    # Its sole positive zero is c=(27/4)A=a5+g*b5.
    return {"response_domain": "R=5", "tau_exact": str(tau),
            "steps_per_integral": steps, "rational_grid": "1e-40",
            "pi": pi.decimal_bounds(39),
            "a5": a5.decimal_bounds(), "b5": b5.decimal_bounds(),
            "endpoint": c.decimal_bounds(), "capacity": capacity.decimal_bounds(),
            "unique_positive_root": True, "generations": g,
            "joint_screening_residual": str(selection["colour_residual"]),
            "three_position_platform_certified": platform,
            "retained_positions": ["3/2", "7/2", "11/2"] if platform else None,
            "excluded_next_position": "15/2" if platform else None,
            "proof_inputs": {"second_derivative_bound": 726,
                             "interval_length_bound": "9/2",
                             "pi_series_terms": 40, "exponential_degree": 60},
            "source": "Guo (2026g) Appendix C branch coefficients and Appendix D enclosure"}


def certify_bandwidth_platform(steps=128):
    """Enclose every c_R, R>=5, using monotonicity and positive Gaussian tails.

    On each interval the kernel (q/(q+b))² increases and exp(-q/pi)
    decreases. Products of opposite endpoint bounds therefore enclose its
    integral without a derivative estimate. Only the precision needed to
    separate 11/2 and 15/2 is requested. Common Gaussian nodes are reused.
    The full-domain degree and frequency tails are those of Guo (2026g),
    Appendix D. No bandwidth scan enters the all-domain conclusion.
    """
    if not isinstance(steps, int) or isinstance(steps, bool) or steps < 1:
        raise ValueError("steps must be a positive integer")
    pi = pi_interval()
    tau = finite_source_response()["tau"]
    generations = screening_compatibility()["generations"]
    if tau != Q(1,50) or generations != 3:
        raise ValueError("bandwidth certificate requires the stated three-copy source")
    rows = []
    for n in range(9):
        if n%2 == 0:
            rows.append((Q(n*(n+2)), Q(3,4), 4*(n+1)**2))
        else:
            for b, weight in ((Q(3,2)+tau**2/6,64),
                              (1+tau**2/6,24),(tau**2/6,8)):
                rows.append((Q((n+1)**2), b, weight*n*(n+2)))
        rows.append(((Q(n)+Q(3,2))**2, 3*tau**2/8,
                     generations*(28 if n%2 == 0 else 32)*(n+1)*(n+2)))
    prefactor = 27/(128*pi**3)
    nodes = {}
    exponential_cache = {}
    def exponential(x):
        key = (x.lo,x.hi)
        if key not in exponential_cache:
            exponential_cache[key] = exp_negative(x)
        return exponential_cache[key]

    def integral(a,b,upper):
        key = (a,upper.lo,upper.hi)
        if key not in nodes:
            width = upper/steps
            q = [(width*j)**2+a for j in range(steps+1)]
            nodes[key] = (width,q,[exponential(x/pi) for x in q])
        width,q,e = nodes[key]
        kernel = [(x/(x+b))**2 for x in q]
        lower = width*sum((kernel[j]*e[j+1] for j in range(steps)),I.point(0))
        upper_bound = width*sum((kernel[j+1]*e[j] for j in range(steps)),I.point(0))
        return I(lower.lo,upper_bound.hi)

    finite = I.point(0)
    complete = I.point(0)
    retained_tail = I.point(0)
    finite_rows = 0
    for a,b,weight in rows:
        if I.point(a).hi < (5*pi).lo:
            finite += weight*integral(a,b,(5*pi-a).sqrt())
            finite_rows += 1
        complete += weight*integral(a,b,I.point(8))
        retained_tail += weight*exponential(I.point(a)/pi)
    # Integral_8^infinity exp(-u²/pi) du <= pi/16 exp(-64/pi).
    frequency_tail = prefactor*retained_tail*pi/16*exponential(64/pi)
    # For n>=9, total weight <= (100+3*32)(n+2)², a_n>=n².
    ratio = Q(144,121)*exponential(19/pi)
    spectral_tail = (27*(100+32*generations)/(256*pi**2)
                     *121*exponential(81/pi)/(1-ratio))
    finite = prefactor*finite
    complete = prefactor*complete
    full = I(complete.lo, (complete+frequency_tail+spectral_tail).hi)
    all_domains = I(finite.lo,full.hi)
    capacity = all_domains**2
    certified = capacity.lo > I.point(Q(11,2)).hi and capacity.hi < I.point(Q(15,2)).lo
    return {"scope": "fixed three-copy source, tau=1/50, every R>=5",
            "response_radius_lower": 5, "tau_exact": str(tau), "generations": generations,
            "endpoint_at_R5": finite.decimal_bounds(),
            "complete_gaussian_endpoint": full.decimal_bounds(),
            "all_bandwidth_endpoint": all_domains.decimal_bounds(),
            "all_bandwidth_capacity": capacity.decimal_bounds(),
            "frequency_tail_upper": frequency_tail.decimal_bounds()[1],
            "spectral_tail_upper": spectral_tail.decimal_bounds()[1],
            "three_position_platform_certified": certified,
            "retained_positions": ["3/2","7/2","11/2"] if certified else None,
            "excluded_next_position": "15/2" if certified else None,
            "proof_method": "monotone bandwidth, outward kernel-Gaussian endpoint envelopes, positive infinite tails",
            "reference": "Guo (2026g), Appendices C and D",
            "work": {"subintervals_per_row": steps, "R5_rows": finite_rows,
                     "complete_rows": len(rows), "row_subintervals": (finite_rows+len(rows))*steps,
                     "distinct_gaussian_meshes": len(nodes),
                     "exponential_enclosure_evaluations": len(exponential_cache),
                     "bandwidth_scan_points": 0}}
