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

"""Parameterized complete conformal condensate of Guo (2026d), Section 8.

The input g, Z and radius units are explicit. This evaluates the native
unweighted relative logarithmic potential, including j=0, and does not
replace Guo's (2026g) distinct window VEV or assigned QCD catalogue.
Exact finite sums plus Guo's (2026d) positive tail give certified root/mass
enclosures; a closed-form H(z) supplies an independent numerical readout.
"""
from fractions import Fraction as Q
import math

from cg_core.rational_interval import Interval as I, GRID, pi_interval


def _shell(j):
    d = (2*j+1)**2
    return Q(4*d-1, 4), d


def restoring_response(z):
    """Full H(z)=J'(z), in binary floating point (not a certificate)."""
    if z < 0 or not math.isfinite(z):
        raise ValueError("z must be finite and nonnegative")
    if z == 0:
        return 0.0
    if z < 1e-8:
        # Avoid subtracting pi/8 from a nearly equal number.
        # The first derivative is exact; the quadratic term follows from
        # the convergent resolvent derivative at zero.
        q3 = math.pi**3/16+math.pi**2/8-math.pi/4
        return math.pi*(math.pi+2)/8*z-q3*z*z
    if z < .25:
        b = math.sqrt(.25-z)
        return math.pi/8-math.pi*b/4*math.tan(math.pi*b/2)
    if z == .25:
        return math.pi/8
    s = math.sqrt(z-.25)
    return math.pi/8+math.pi*s/4*math.tanh(math.pi*s/2)


def restoring_derivative(z):
    """Full H'(z), continuously evaluated across z=1/4."""
    if z < 0 or not math.isfinite(z):
        raise ValueError("z must be finite and nonnegative")
    if abs(z-.25) < 1e-8:
        return math.pi**2/8-math.pi**4/48*(z-.25)
    if z < .25:
        b = math.sqrt(.25-z)
        angle = math.pi*b/2
        return math.pi/(8*b)*(math.tan(angle)+angle/math.cos(angle)**2)
    s = math.sqrt(z-.25)
    angle = math.pi*s/2
    tanh = math.tanh(angle)
    return math.pi/(8*s)*(tanh+angle*(1-tanh*tanh))


def finite_response(z, shells):
    """Outward H_N and H_N' for the constant shell through j=N."""
    z = z if isinstance(z, I) else I.point(z)
    if z.lo < 0 or not isinstance(shells, int) or shells < 0:
        raise ValueError("nonnegative z and integer maximum shell required")
    h, hp = I.point(0), I.point(0)
    for j in range(shells+1):
        c, d = _shell(j)
        h += d*z/(I.point(c)*(c+z))
        hp += d/(c+z)**2
    return h, hp


def _bisect_finite(nu, shells, high, tail_slope, iterations):
    low, high = 0, I.point(high).hi
    for _ in range(iterations):
        mid = (low+high)//2
        if mid in (low, high):
            break
        z = I(mid,mid)
        h, _ = finite_response(z, shells)
        residual = h+tail_slope*z-nu
        if residual.hi < 0:
            low = mid
        elif residual.lo > 0:
            high = mid
        else:
            # Derivative >= contribution of j=0 on this current bracket.
            derivative_lower = (1/(I.point(Q(3,4))+I(high,high))**2).lo
            radius = ((max(abs(residual.lo),abs(residual.hi))*GRID
                       + derivative_lower-1)//derivative_lower)
            low, high = max(low,mid-radius), min(high,mid+radius)
            break
    return I(low,high)


def solve_native_condensate(*, g, Z, L, shells=512, iterations=80):
    """Certify the full stationary root and radial mass for explicit inputs.

    Decimal input strings are interpreted exactly. Radius reference is
    Lc²=pi, mu=16(1/L²-1/pi), kappa=gL². The positive omitted tail obeys
    0<=H-H_N<=z*r_N and 0<=H'-H_N'<=r_N,
    r_N=8/[9(2N+1)]. Returned decimal interval endpoints round outward.
    """
    g, Z, L = (value if isinstance(value, I) else I.point(value) for value in (g, Z, L))
    if min(g.lo,Z.lo,L.lo) <= 0:
        raise ValueError("g, Z and L must be strictly positive")
    if not isinstance(shells,int) or shells < 0 or iterations < 1:
        raise ValueError("nonnegative shells and positive iterations required")
    kappa = g*L**2
    mu = 16*(1/L**2-1/pi_interval())
    if mu.lo >= 0:
        return {"phase":"uncondensed", "amplitude_squared":["0","0"],
                "mass_squared":(mu/Z).decimal_bounds(),
                "mu":mu.decimal_bounds(), "constant_shell_included":True}
    if mu.hi >= 0:
        raise ArithmeticError("input interval overlaps the critical radius")
    nu = -mu/(2*kappa)
    minimum_shell = (2*nu.hi)//GRID
    if shells < minimum_shell:
        raise ValueError(f"finite restoring slope requires shells >= {minimum_shell}")
    high, _ = _shell(minimum_shell)
    tail = I.point(Q(8,9*(2*shells+1)))
    lower = _bisect_finite(nu,shells,high,tail,iterations)
    upper = _bisect_finite(nu,shells,high,I.point(0),iterations)
    z = I(lower.lo,upper.hi)
    _, hp_lower = finite_response(I(z.hi,z.hi),shells)
    _, hp_upper = finite_response(I(z.lo,z.lo),shells)
    hp = I(hp_lower.lo,hp_upper.hi+tail.hi)
    mass = 4*kappa*z*hp/Z
    # Closed-form estimate is reported separately, never used to shrink
    # the certificate or hide its finite spectral-tail error.
    lo, hi = 0.0,float(high)
    target = (nu.lo+nu.hi)/(2*GRID)
    for _ in range(100):
        mid = (lo+hi)/2
        if restoring_response(mid) < target:
            lo = mid
        else:
            hi = mid
    estimate = (lo+hi)/2
    kappa_mid = (kappa.lo+kappa.hi)/(2*GRID)
    Z_mid = (Z.lo+Z.hi)/(2*GRID)
    return {"phase":"condensed", "mu":mu.decimal_bounds(),
            "kappa":kappa.decimal_bounds(), "drive_nu":nu.decimal_bounds(),
            "z":z.decimal_bounds(), "amplitude_squared":(z/kappa).decimal_bounds(),
            "mass_squared":mass.decimal_bounds(),
            "strict_positive_gap_certified":mass.lo>0,
            "spectral_tail_slope":tail.decimal_bounds(),
            "finite_root":upper.decimal_bounds(),
            "finite_max_shell":shells, "constant_shell_included":True,
            "full_response_estimate":{"z":estimate,
                "mass_squared":4*kappa_mid*estimate*restoring_derivative(estimate)/Z_mid},
            "units":"declared response units; Lc²=pi; explicit g and kinetic Z",
            "source":"Guo (2026d) complete conformal response and stationary-tail propositions"}


def finite_joint_relative_potential(*, amplitude_squared, L, g, shells):
    """Finite native potential and its joint radius--amplitude square completion.

    The coupling and reference radius Lc^2=pi are held fixed.  This is a
    floating-point identity check of the explicitly retained shell sum;
    infinite-tail certification belongs to solve_joint_native_condensate.
    """
    if (not all(math.isfinite(value) for value in (amplitude_squared, L, g))
            or amplitude_squared < 0 or min(L, g) <= 0
            or isinstance(shells, bool) or not isinstance(shells, int) or shells < 0):
        raise ValueError("nonnegative amplitude, positive radius/coupling and integer shells required")
    u, z = g*L*L*amplitude_squared, 1/(L*L)
    def log_remainder(x):
        if x < 1e-3:
            return math.fsum((-1)**k*x**k/k for k in range(2, 13))
        return x-math.log1p(x)
    terms = []
    for j in range(shells+1):
        alpha, multiplicity = _shell(j)
        terms.append(multiplicity*log_remainder(u/float(alpha)))
    spectral = math.fsum(terms)
    direct = 8*(z-1/math.pi)*amplitude_squared+spectral
    square = 8*u/g*(z-1/(2*math.pi))**2
    completed = spectral+square-2*u/(g*math.pi**2)
    return {"direct_potential": direct, "completed_square_potential": completed,
            "identity_residual": direct-completed, "u": u, "z": z,
            "spectral_potential": spectral, "radius_square_term": square,
            "finite_max_shell": shells}


def complete_relative_potential(*, amplitude_squared, L, g):
    """Full relative potential from the analytic restoring function.

    Integrating H=I' avoids a second spectral truncation.  The reported
    quadrature error is a floating-point integration estimate, distinct
    from the outward stationary-root certificates supplied by this module.
    """
    from scipy.integrate import quad
    if (not all(math.isfinite(value) for value in (amplitude_squared, L, g))
            or amplitude_squared < 0 or min(L, g) <= 0):
        raise ValueError("nonnegative amplitude squared and positive finite g,L required")
    u = g*L*L*amplitude_squared
    value, error, information = quad(restoring_response, 0., u,
        epsabs=2e-13, epsrel=2e-13, full_output=1)[:3]
    return {"value": 8*(1/(L*L)-1/math.pi)*amplitude_squared+value,
            "spectral_potential": value, "quadrature_error_estimate": error,
            "restoring_function_evaluations": int(information['neval'])}


def joint_native_source_response(*, amplitude_squared, L, g):
    """Full static source derivatives at fixed g and reference radius Lc^2=pi.

    Set u=g L^2 y, z=L^(-2) and eta=-log(L/L_reference).  Derivatives in
    eta hold y fixed.  The returned source equation from a potential action
    -F is -Feta.  The Schur curvature relaxes y at quadratic order; away
    from a joint equilibrium it is a Hessian Schur complement only.
    """
    if (not all(math.isfinite(value) for value in (amplitude_squared, L, g))
            or amplitude_squared < 0 or min(L, g) <= 0):
        raise ValueError("nonnegative amplitude squared and positive finite g,L required")
    kappa, z = g*L*L, 1/(L*L)
    u = kappa*amplitude_squared
    response, slope = restoring_response(u), restoring_derivative(u)
    Fy = 8*(z-1/math.pi)+kappa*response
    Feta = 16*z*amplitude_squared-2*u*response
    Fyy = kappa*kappa*slope
    Feta_y = 16*z-2*kappa*(response+u*slope)
    Feta_eta = 32*z*amplitude_squared+4*u*response+4*u*u*slope
    return {"u": u, "z": z, "Fy": Fy, "Feta": Feta,
            "source_equation_from_potential": -Feta,
            "hessian_eta_y": [[Feta_eta, Feta_y], [Feta_y, Fyy]],
            "relaxed_eta_curvature": Feta_eta-Feta_y*Feta_y/Fyy,
            "source_coordinate": "eta=-log(L/L_reference), with y and g fixed in the eta derivative",
            "scope": "static joint response of the native unweighted relative potential"}


def solve_joint_native_condensate(*, g, Z, shells=128, iterations=55):
    """Certify the unique positive joint minimum of the same relative potential.

    For u=gL^2 y and z=L^(-2),
    F=I(u)+(8u/g)(z-1/(2pi))^2-2u/(g pi^2).
    The unweighted tower has I'(0)=0, I''>0 and I'(u)->infinity.
    Consequently L_*^2=2pi and I'(u_*)=2/(g pi^2) select its unique
    positive joint minimum.  A single existing radial-root certificate
    at the outward interval sqrt(2pi) supplies all remaining enclosures.
    No source kinetic term or production mass assignment is introduced.
    """
    coupling = g if isinstance(g, I) else I.point(g)
    kinetic = Z if isinstance(Z, I) else I.point(Z)
    if min(coupling.lo, kinetic.lo) <= 0:
        raise ValueError("g and Z must be strictly positive")
    radius_squared = 2*pi_interval()
    radius = radius_squared.sqrt()
    stationary = solve_native_condensate(g=coupling, Z=kinetic, L=radius,
                                         shells=shells, iterations=iterations)
    if stationary["phase"] != "condensed":
        raise ArithmeticError("joint native minimum must lie on the positive branch")
    u = I.bounds(*stationary["z"])
    y = u/(coupling*radius_squared)
    mass = I.bounds(*stationary["mass_squared"])
    # Reuse the mass certificate, m^2=4*kappa*u*I''/Z.  All factors have
    # positive lower bounds, so interval division retains the full tail.
    slope = mass*kinetic/(4*coupling*radius_squared*u)
    radius_curvature = 16*u/coupling
    relaxed = 64*y/radius_squared
    kappa = coupling*radius_squared
    Fyy = kappa**2*slope
    mixed = -2*kappa*u*slope
    Fetaeta = relaxed+4*u**2*slope
    g_mid = (coupling.lo+coupling.hi)/(2*GRID)
    u_estimate = stationary["full_response_estimate"]["z"]
    radius_estimate = math.sqrt(2*math.pi)
    estimate = joint_native_source_response(amplitude_squared=u_estimate/(2*g_mid*math.pi),
                                             L=radius_estimate, g=g_mid)
    checks = {"positive_joint_minimum_certified": u.lo > 0,
              "positive_joint_hessian_certified": min(slope.lo, radius_curvature.lo) > 0,
              "positive_relaxed_compression_curvature_certified": relaxed.lo > 0,
              "radial_gap_certified": stationary["strict_positive_gap_certified"]}
    return {"scope": "joint static minimum of the native unweighted relative potential at fixed g",
            "inputs": {"g": coupling.decimal_bounds(32), "Z": kinetic.decimal_bounds(32),
                       "finite_max_shell": shells, "root_iterations_per_bound": iterations},
            "potential_normalization": "the same relative F_L at every radius, with fixed g and Lc^2=pi",
            "reference_radius_squared": pi_interval().decimal_bounds(32),
            "selected_radius": radius.decimal_bounds(32),
            "radius_squared": radius_squared.decimal_bounds(32),
            "radius_ratio_squared": ["2", "2"],
            "restoring_target": (2/(coupling*pi_interval()**2)).decimal_bounds(32),
            "scaled_amplitude_u": u.decimal_bounds(32), "amplitude_squared": y.decimal_bounds(32),
            "joint_hessian_u_z_diagonal": [slope.decimal_bounds(32), radius_curvature.decimal_bounds(32)],
            "joint_hessian_eta_y": [[Fetaeta.decimal_bounds(32), mixed.decimal_bounds(32)],
                                    [mixed.decimal_bounds(32), Fyy.decimal_bounds(32)]],
            "relaxed_eta_curvature": relaxed.decimal_bounds(32),
            "stationary": stationary,
            "full_response_estimate": {"u": u_estimate, "L": radius_estimate,
                                       "amplitude_squared": u_estimate/(2*g_mid*math.pi),
                                       "Fy": estimate["Fy"], "Feta": estimate["Feta"],
                                       "relaxed_eta_curvature": estimate["relaxed_eta_curvature"]},
            "stationary_certificate_evaluations": 1,
            "spectral_tail_reused": True,
            "source_kinetic_term_supplied": False,
            "assigned_production_mass": False,
            "checks": {name: bool(value) for name, value in checks.items()},
            "passed": bool(all(checks.values()))}


def scalar_mass_tower(mass_squared, L, l_max=10):
    """Assigned full even scalar tower, including its constant l=0 shell."""
    if mass_squared < 0 or L <= 0 or l_max < 0:
        raise ValueError("nonnegative mass squared and positive L required")
    return [(l,l*(l+2)/L**2+mass_squared,(l+1)**2)
            for l in range(0,l_max+1,2)]


def uniform_gap_budget(*, nu_bounds, kappa_bounds, Z_bounds, shells):
    """Guo (2026d) finite-scale certificate for a supplied verified parameter box.

    The caller must verify that its entire scale path lies in this box.
    This routine evaluates the theorem; it does not invent g(k) or Z(k).
    """
    nu, kappa, Z = (I.bounds(*bounds) for bounds in
                    (nu_bounds,kappa_bounds,Z_bounds))
    if min(nu.lo,kappa.lo,Z.lo) <= 0:
        raise ValueError("strictly positive two-sided parameter bounds required")
    M = (2*nu.hi)//GRID
    if shells < M:
        raise ValueError(f"shells must be at least {M}")
    Y,_ = _shell(M)
    u = I(nu.lo,nu.lo)/(2*Q(8,3))
    _,m = finite_response(I.point(Y),M)
    gamma = 4*I(kappa.lo,kappa.lo)*u*m/I(Z.hi,Z.hi)
    K = 4*I(kappa.hi,kappa.hi)*Y/I(Z.lo,Z.lo)*(1+(Q(8,3)+2*Y*Q(32,9))/m)
    error = K*Q(8,9*(2*shells+1))
    return {"verified_input_box_required":True,"low_mode_max":M,
            "common_z_bracket":[u.decimal_bounds()[0],I.point(Y).decimal_bounds()[1]],
            "uniform_positive_gap_lower":gamma.decimal_bounds()[0],
            "uniform_mass_squared_error_upper":error.decimal_bounds()[1],
            "error_below_half_gap":2*error.hi < gamma.lo}


def canonical_radial_curvature(*, amplitude, g, Z, L):
    """Compute V''(E)/Z without assuming that E is a stationary solution.

    V'(E)=E[mu+2*kappa*H(kappa E²)], kappa=gL². At a nonzero
    stationary root this reduces to 4*kappa*z*H'(z)/Z. At a general
    amplitude the Hessian also includes the stationary residual term.
    """
    if not all(math.isfinite(x) for x in (amplitude,g,Z,L)) or min(g,Z,L)<=0:
        raise ValueError("finite amplitude and positive g, Z, L required")
    kappa = g*L*L
    mu = 16*(1/(L*L)-1/math.pi)
    z = kappa*amplitude*amplitude
    radial_residual = mu+2*kappa*restoring_response(z)
    curvature = radial_residual+4*kappa*z*restoring_derivative(z)
    return {"potential_gradient":amplitude*radial_residual,
            "potential_second_derivative":curvature,
            "canonical_mass_squared":curvature/Z,"z":z}


def source_visible_resolvent(Q_squared, *, shell_coefficients, mass_squared,
                             L, length_unit, source_Z=1.0,
                             external_kinetic="canonical-laplacian"):
    """Finite even-shell response to an explicitly normalized scalar source.

    shell_coefficients[l] contains all (l+1)^2 coefficients of the source
    on that shell. They are dimensionful source coefficients in the same
    spacetime units as Q. They couple to the amplitude E, so f_can=f/sqrt(Z).
    length_unit converts the dimensionless internal masses to physical
    masses. The condition external_kinetic='canonical-laplacian' specifies
    the external quadratic action Q²+M²; it is not inferred from the internal
    positive-gap theorem. No omitted source tail is silently assigned zero:
    the returned response is for the supplied finite source projection.
    """
    import numpy as np
    if external_kinetic != "canonical-laplacian":
        raise ValueError("an explicit supported external kinetic operator is required")
    if not all(math.isfinite(x) for x in (Q_squared,mass_squared,L,length_unit,source_Z)):
        raise ValueError("finite response inputs required")
    if min(Q_squared,mass_squared)<0 or min(L,length_unit,source_Z)<=0:
        raise ValueError("nonnegative squared scales and positive radius, units and Z required")
    if not shell_coefficients:
        raise ValueError("at least one explicit even-shell source projection required")
    response,visible,shells = 0.0,[],[]
    for l,coefficients in sorted(shell_coefficients.items()):
        if not isinstance(l,int) or isinstance(l,bool) or l<0 or l%2:
            raise ValueError("RP3 scalar shells must be nonnegative even integers")
        c = np.asarray(coefficients,dtype=complex)
        if c.shape!=((l+1)**2,) or not np.isfinite(c).all():
            raise ValueError("supply every degeneracy coefficient on each retained shell")
        weight = float(np.vdot(c,c).real/source_Z)
        m2 = (l*(l+2)/L**2+mass_squared)/length_unit**2
        denominator = Q_squared+m2
        if weight>0 and denominator==0:
            raise ValueError("evaluate the pole away from Q_squared=0")
        response += weight/denominator if weight>0 else 0
        if weight>0:
            visible.append(m2)
        shells.append({"l":l,"degeneracy":(l+1)**2,"canonical_weight":weight,
                       "physical_mass_squared":m2})
    return {"response":response,"shells":shells,
            "lowest_visible_mass_squared":min(visible) if visible else None,
            "source_is_finite_projection":True,"external_kinetic":external_kinetic}


def _intensity_bubble_interval(ratio, terms):
    """Enclose integral_0^1 [r*u*(1-u)-log(1+r*u*(1-u))] du.

    For 0<=r<=4 the integrated alternating terms decrease. Their exact
    recurrence is t_2=r²/60, t_(n+1)=-t_n*r*n/[2*(2*n+3)]. Monotonicity
    in r and adjacent even/odd partial sums enclose the entire interval.
    """
    if ratio.lo < 0 or ratio.hi > 4*GRID:
        raise ValueError("bubble certificate requires 0 <= Q²/M² <= 4")
    if isinstance(terms, bool) or not isinstance(terms, int) or terms < 2 or terms % 2:
        raise ValueError("an even number of series terms >= 2 is required")

    def partial(r, last):
        term = r*r/60
        total = term
        for n in range(2, last):
            term *= -r*Q(n, 2*(2*n+3))
            total += term
        return total

    low = partial(Q(ratio.lo, GRID), terms+1)
    high = partial(Q(ratio.hi, GRID), terms)
    return I.bounds(low, high)


def intensity_response_certificate(Q_squared, *, amplitude_squared,
        mass_squared, Z, L, shells=16, terms=24,
        external_kinetic="canonical-laplacian"):
    """Infinite-tower Wick intensity in the specified quadratic realization.

    E=E_*+Z^(-1/2)*sum(phi_la*e_la), with normalized internal Haar measure
    and independent canonical four-dimensional free fields. The observable
    integral :(E²-E_*²): has a pole of weight 4*E_*²/Z at mass_squared and
    a positive two-particle continuum starting at 4*mass_squared. The
    continuum's value and first Q² derivative at zero are subtracted.

    Inputs use one declared system of response units. Interval inputs reuse
    a stationary-root certificate without rerunning its spectral sums.
    The finite bubbles use exact rational alternating-series bounds, and
    all omitted internal shells are enclosed by the analytic positive tail.
    This certifies the quadratic scalar realization, not an interacting
    colour-observable spectral function.
    """
    values = (Q_squared, amplitude_squared, mass_squared, Z, L)
    z, y, m2, kinetic, radius = tuple(v if isinstance(v, I) else I.point(v)
                                     for v in values)
    if external_kinetic != "canonical-laplacian":
        raise ValueError("the canonical external quadratic action is required")
    if min(z.lo,y.lo)<0 or min(m2.lo,kinetic.lo,radius.lo)<=0:
        raise ValueError("nonnegative Q²,y and strictly positive m²,Z,L required")
    if isinstance(shells,bool) or not isinstance(shells,int) or shells<0:
        raise ValueError("a nonnegative integer maximum internal shell is required")
    bubbles = I.point(0)
    for j in range(shells+1):
        a = m2+4*j*(j+1)/radius**2
        bubbles += (2*j+1)**2*_intensity_bubble_interval(z/a, terms)
    continuum = bubbles/(8*pi_interval()**2*kinetic**2)
    residue = 4*y/kinetic
    pole = residue/(z+m2)
    tail = 81*z**2*radius**4/(61440*pi_interval()**2*kinetic**2*(2*shells+1))
    full = pole+continuum+I(0,tail.hi)
    return {
        "scope":"centred Wick intensity of the canonically realized native quadratic scalar tower",
        "external_kinetic":external_kinetic,
        "inputs":{name:v.decimal_bounds(32) for name,v in zip(
            ("Q_squared","amplitude_squared","mass_squared","Z","L"),
            (z,y,m2,kinetic,radius))},
        "pole_mass_squared":m2.decimal_bounds(32),
        "pole_residue":residue.decimal_bounds(32),
        "continuum_threshold_squared":(4*m2).decimal_bounds(32),
        "finite_continuum_response":continuum.decimal_bounds(32),
        "continuum_tail_upper":tail.decimal_bounds(32)[1],
        "subtracted_response":full.decimal_bounds(32),
        "subtraction":"continuum C(0)=C'(0)=0; derivative with respect to Q²",
        "internal_shells_retained":shells+1,
        "bubble_max_orders_per_endpoint":[terms,terms+1],
        "bubble_recurrence_updates":(shells+1)*(2*terms-3),
        "arithmetic":"exact rational partial sums and outward integer-grid interval operations",
        "strict_positive_atom_certified":residue.lo>0,
        "infinite_internal_tail_included":True,
        "interacting_colour_spectrum_established":False,
    }


def certify_common_source_interval(*, planck_ratio, vacuum_density):
    """Certify a continuous occupied background interval by an exit-time bound.

    The realization has g=1, Z=2, Lref²=2*pi, m0²=3/(8*pi), and
    initial L²=3*pi. All variables use the declared common energy unit.
    Inputs require MP/unit >= 1 and 0 <= rho_v/unit**4 <= 1/1000.
    The proof uses a rational phase-space box, a uniformly bracketed
    algebraic source, and bounds on the canonical vector field. It does
    not infer continuous stability from sampled trajectories, and does
    not run an interval ODE solver or a potential quadrature.
    """
    mp = planck_ratio if isinstance(planck_ratio, I) else I.point(planck_ratio)
    vacuum = vacuum_density if isinstance(vacuum_density, I) else I.point(vacuum_density)
    if mp.lo < GRID or vacuum.lo < 0 or vacuum.hi > I.point(Q(1, 1000)).hi:
        raise ValueError("certificate requires MP/unit >= 1 and 0 <= vacuum density <= 1/1000")
    pi = pi_interval()
    maximum_shell = 64
    tail = I.point(Q(8, 9*(2*maximum_shell+1)))
    endpoint_cache = {}

    def endpoint_response(endpoint):
        if endpoint not in endpoint_cache:
            endpoint_cache[endpoint] = finite_response(I(endpoint, endpoint), maximum_shell)
        return endpoint_cache[endpoint]

    def response(interval):
        lower, derivative_upper = endpoint_response(interval.lo)
        upper, derivative_lower = endpoint_response(interval.hi)
        return (I(lower.lo, upper.hi+(tail*I(interval.hi, interval.hi)).hi),
                I(derivative_lower.lo, derivative_upper.hi+tail.hi))

    def positive_square(interval):
        if interval.lo <= 0 <= interval.hi:
            return I(0, (I.point(Q(max(-interval.lo, interval.hi), GRID))**2).hi)
        endpoints = [I.point(Q(value, GRID))**2 for value in (interval.lo, interval.hi)]
        return I(min(value.lo for value in endpoints), max(value.hi for value in endpoints))

    def absolute_upper(interval):
        value = max(abs(interval.lo), abs(interval.hi))
        return I(value, value)

    box = {
        "a": I.bounds(".99", "1.01"), "E": I.bounds(".101", ".105"),
        "p_E": I.bounds("-.004", ".004"),
        "phi_1": I.bounds(".347", ".354"), "phi_2": I.bounds("-.004", ".004"),
        "p_1": I.bounds("-.003", ".003"), "p_2": I.bounds(".178", ".185"),
        "H": I(I.point(".06").lo, I.point(".12").hi)/mp,
    }
    alpha = I.bounds(".79", ".85")
    radius_squared = positive_square(box["phi_1"])+positive_square(box["phi_2"])
    momentum_squared = positive_square(box["p_1"])+positive_square(box["p_2"])
    m0_squared = 3/(8*pi)

    def source_bounds(source_alpha):
        z = source_alpha**2/(2*pi)
        u = 2*pi*box["E"]**2/source_alpha**2
        restoring, derivative = response(u)
        kinetic = momentum_squared*source_alpha**3/(2*box["a"]**6)
        mass = m0_squared*radius_squared/(2*source_alpha)
        source = 16*box["E"]**2*z-2*u*restoring+3*kinetic-mass
        curvature = 32*box["E"]**2*z+4*u*restoring+4*u**2*derivative
        amplitude_force = 16*box["E"]*(z-1/pi)+2*u*restoring/box["E"]
        return {"F": source, "h": curvature-9*kinetic+mass,
                "h_H": curvature+9*kinetic+mass,
                "T": kinetic, "U_E": amplitude_force}

    left = source_bounds(I(alpha.lo, alpha.lo))
    right = source_bounds(I(alpha.hi, alpha.hi))
    whole = source_bounds(alpha)
    if left["F"].hi >= 0 or right["F"].lo <= 0 or whole["h"].lo <= 0:
        raise ArithmeticError("uniform source bracket or kinetic margin failed")

    # Each initial spectral root is enclosed by two sign evaluations.
    u_initial, u_vacuum = I.bounds(".099", ".101"), I.bounds(".10", ".12")
    root_residuals = {}
    for name, interval, target in (
            ("occupied", u_initial, 16/(9*pi**2)),
            ("vacuum", u_vacuum, 2/pi**2)):
        lower_residual = response(I(interval.lo, interval.lo))[0]-target
        upper_residual = response(I(interval.hi, interval.hi))[0]-target
        if lower_residual.hi >= 0 or upper_residual.lo <= 0:
            raise ArithmeticError("initial spectral-root enclosure failed")
        root_residuals[name] = {"root": interval.decimal_bounds(18),
                               "lower_residual": lower_residual.decimal_bounds(18),
                               "upper_residual": upper_residual.decimal_bounds(18)}
    E_initial = (u_initial/(3*pi)).sqrt()
    alpha_initial = (I.point(2)/3).sqrt()
    occupied_energy = 16*E_initial**2/(3*pi)
    # U0=-A+I(u0), Uvac=I(uv)-2uv/pi². The joint-minimum theorem
    # gives rho0 >= A. Also I(u0) <= H'(0) u0²/2 and I(uv) >= 0.
    rho_upper = pi*(pi+2)*u_initial**2/16+2*I(u_vacuum.hi, u_vacuum.hi)/pi**2+vacuum
    rho_initial = I(occupied_energy.lo, rho_upper.hi)
    initial = {
        "a": I.point(1), "E": E_initial, "p_E": I.point(0),
        "phi_1": (occupied_energy*alpha_initial/m0_squared).sqrt(),
        "phi_2": I.point(0), "p_1": I.point(0),
        "p_2": (occupied_energy/alpha_initial**3).sqrt(),
        "H": (rho_initial/3).sqrt()/mp,
    }
    a_low, a_high = I(box["a"].lo, box["a"].lo), I(box["a"].hi, box["a"].hi)
    alpha_low, alpha_high = I(alpha.lo, alpha.lo), I(alpha.hi, alpha.hi)
    derivatives = {
        "a": a_high*I(box["H"].hi, box["H"].hi),
        "E": absolute_upper(box["p_E"])/(2*a_low**3),
        "p_E": a_high**3*absolute_upper(whole["U_E"]),
        "phi_1": absolute_upper(box["p_1"])*alpha_high**3/a_low**3,
        "phi_2": absolute_upper(box["p_2"])*alpha_high**3/a_low**3,
        "p_1": a_high**3*m0_squared*absolute_upper(box["phi_1"])/alpha_low,
        "p_2": a_high**3*m0_squared*absolute_upper(box["phi_2"])/alpha_low,
        "H": (absolute_upper(box["p_E"])**2/(4*a_low**6)
              +I(whole["T"].hi, whole["T"].hi))/mp**2,
    }
    duration = I.point(Q(1, 100))
    margins, displacements, remaining = {}, {}, {}
    for name, interval in box.items():
        distance = min(initial[name].lo-interval.lo, interval.hi-initial[name].hi)
        displacement = (duration*derivatives[name]).hi
        if distance <= 0 or 2*displacement >= distance:
            raise ArithmeticError("continuous exit-time margin failed for "+name)
        margins[name] = I(distance, distance).decimal_bounds(18)[0]
        displacements[name] = I(displacement, displacement).decimal_bounds(18)[1]
        remaining[name] = I(distance-displacement, distance-displacement).decimal_bounds(18)[0]

    minimum_h = I(whole["h"].lo, whole["h"].lo)
    maximum_kinetic = I(whole["T"].hi, whole["T"].hi)
    sound_lower = minimum_h/(minimum_h+18*maximum_kinetic)
    phase_charge = box["phi_1"]*box["p_2"]-box["phi_2"]*box["p_1"]
    phase_rate = alpha**3*phase_charge/(box["a"]**3*radius_squared)
    if sound_lower.lo <= I.point(".19").hi or phase_rate.lo <= 0:
        raise ArithmeticError("propagation or monotone-clock certificate failed")
    return {
        "status": "certified", "duration_in_inverse_energy_unit": duration.decimal_bounds(18),
        "scope": "continuous homogeneous solution and constrained scalar/tensor principal forms on the stated interval",
        "normalization": "g=1; Z=2; Lref²=2*pi; m0²=3/(8*pi); initial L²=3*pi; common energy unit",
        "inputs": {"planck_ratio": mp.decimal_bounds(18), "vacuum_density": vacuum.decimal_bounds(40)},
        "phase_space_box": {name: value.decimal_bounds(18) for name, value in box.items()},
        "initial_state_enclosures": {name: value.decimal_bounds(18) for name, value in initial.items()},
        "initial_spectral_root_enclosures": root_residuals,
        "source_alpha_interval": alpha.decimal_bounds(18),
        "source_left_residual": left["F"].decimal_bounds(18),
        "source_right_residual": right["F"].decimal_bounds(18),
        "constrained_curvature_h": whole["h"].decimal_bounds(18),
        "canonical_source_curvature_h_H": whole["h_H"].decimal_bounds(18),
        "sound_speed_squared_lower_bound": sound_lower.decimal_bounds(18)[0],
        "phase_clock_rate": phase_rate.decimal_bounds(18),
        "absolute_vector_field_upper_bounds": {name: value.decimal_bounds(18)[1] for name, value in derivatives.items()},
        "initial_boundary_distances": margins, "maximum_displacements": displacements,
        "remaining_boundary_margins": remaining,
        "exit_time_test": "twice each duration times vector-field bound is smaller than its initial boundary distance",
        "infinite_spectral_tail_included": True,
        "work_counts": {"finite_max_shell": maximum_shell,
                        "distinct_spectral_endpoint_evaluations": len(endpoint_cache),
                        "spectral_shell_pair_evaluations": len(endpoint_cache)*(maximum_shell+1),
                        "interval_ode_steps": 0, "potential_quadratures": 0},
        "arithmetic": "outward integer-grid rational intervals; analytic positive spectral-tail bound",
    }
