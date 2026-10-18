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

"""Actual finite covariant-scalar energy sources on the native RP3 carrier.

The same-source family is A(eta)=exp(eta) A_B exp(eta), where
A_B=D_B*D_B+3/(4 L^2), H=sqrt(A_B), and E_N=Tr(N H).  Occupations,
connection and real compression profiles are explicit inputs. The computed
first and second derivatives give the fixed-state internal energy response.
The noncompact tensor propagator is determined by its sourced action and
constraint reduction.

Products in D_B retain their complete harmonic support before the Gram
matrix is formed.  Compression is a stated finite Galerkin family.  Its
low-state first/second derivatives can be exact without a finite-source
truncation being exact: the executed example checks the required product
support and the next cutoff independently.

The time-dependent conformal source uses the same finite field action:
M(eta)=exp(-3 eta), B(eta)=exp(-eta/2) A_B exp(-eta/2).  Its canonical
Hamiltonian retains both signs of the oscillator frequencies and every
occupied coherence.  Phase covariances in the finite-carrier examples
describe classical occupied ensembles on the prescribed common spacetime background.
The same conformal matrices also determine their covariant Hilbert
stress, exchange with spacetime-dependent compression sources, and the
matter contributions to the lapse and shift constraints.

The common-background calculation below additionally retains the native
radial amplitude, its algebraic radius source and the macroscopic Einstein
action. Its two real matter coordinates are one retained degenerate pair;
the published example uses the existing constant-shell mass and zero
connection. Source balance is solved together with the occupied matter
and metric evolution in this explicitly specified realization.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.linalg import expm

from cg_core import modal_algebra as modes


def scalar_basis(max_j):
    if not isinstance(max_j, int) or isinstance(max_j, bool) or max_j < 0:
        raise ValueError("nonnegative integer maximum scalar spin required")
    return tuple((j, m, n) for j in range(max_j+1)
                 for m in range(-j, j+1) for n in range(-j, j+1))


def common_source_background_state(state, *, g, Z, mass_squared,
                                   reference_radius_squared, work=None):
    """Eliminate the algebraic compression source at fixed canonical data.

    Coordinates are (a,E,p_E,phi_1,phi_2,p_1,p_2,H), in one declared
    reciprocal-energy unit.  The source equation is U_eta+3T-V=0.
    Its Hamiltonian derivative U_etaeta+9T+V is strictly positive.
    The returned velocity curvature instead is U_etaeta-9T+V.
    """
    from scipy.optimize import brentq
    from cg_frg.ewsb.native_condensate import joint_native_source_response
    state = np.asarray(state, float)
    if (state.shape != (8,) or not np.all(np.isfinite(state))
            or not all(math.isfinite(v) for v in (g, Z, mass_squared, reference_radius_squared))
            or min(state[0], state[1], g, Z, mass_squared, reference_radius_squared) <= 0):
        raise ValueError("finite positive background scale, amplitude and action coefficients required")
    a, E, p_E = state[:3]
    phi, momentum = state[3:5], state[5:7]
    if work is not None:
        work['algebraic_source_solves'] += 1
    def evaluate(eta):
        if work is not None:
            work['source_derivative_evaluations'] += 1
        M, B = math.exp(-3*eta), mass_squared*math.exp(-eta)
        L = math.sqrt(reference_radius_squared)*math.exp(-eta)
        response = joint_native_source_response(amplitude_squared=E*E, L=L, g=g)
        T = float(momentum@momentum)/(2*a**6*M)
        V = B*float(phi@phi)/2
        force = response['Feta']+3*T-V
        hamiltonian_curvature = response['hessian_eta_y'][0][0]+9*T+V
        return force, hamiltonian_curvature, response, M, B, T, V, L
    low, high = -1., 1.
    low_value, high_value = evaluate(low)[0], evaluate(high)[0]
    for _ in range(12):
        if low_value < 0 < high_value:
            break
        if low_value >= 0:
            low *= 2
            low_value = evaluate(low)[0]
        if high_value <= 0:
            high *= 2
            high_value = evaluate(high)[0]
    else:
        raise ArithmeticError("algebraic source root could not be bracketed")
    eta = brentq(lambda x: evaluate(x)[0], low, high, xtol=2e-14, rtol=1e-14)
    force, hH, response, M, B, T, V, L = evaluate(eta)
    h = response['hessian_eta_y'][0][0]-9*T+V
    if h <= 0:
        raise ArithmeticError("background leaves the positive reduced-kinetic branch")
    velocity = momentum/(a**3*M)
    E_velocity = p_E/(a**3*Z)
    mixed = 2*E*response['hessian_eta_y'][0][1]
    eta_velocity = (18*state[7]*T+4*B*float(phi@velocity)-mixed*E_velocity)/hH
    gradient = np.diag([Z, M, M])
    coupling = np.concatenate(([0.], -3*M*velocity))
    kinetic = gradient+np.outer(coupling, coupling)/h
    return {'eta': eta, 'L': L, 'M': M, 'B': B, 'T': T, 'V': V,
            'U_E': 2*E*response['Fy'], 'U_eta': response['Feta'],
            'U_eta_E': mixed, 'U_eta_eta': response['hessian_eta_y'][0][0],
            'source_residual': force, 'hamiltonian_source_curvature': hH,
            'velocity_source_curvature': h, 'E_velocity': E_velocity,
            'matter_velocity': velocity, 'eta_velocity': eta_velocity,
            'kinetic': kinetic, 'gradient': gradient}


def evaluate_common_source_background(*, joint_certificate, planck_ratio,
                                     mass_squared, vacuum_density,
                                     duration=None, samples=17,
                                     rtol=2e-10, atol=2e-12):
    """Evolve a nonzero occupied Einstein--matter--auxiliary-source background.

    Energies are measured in a declared mu: planck_ratio=M_P/mu,
    mass_squared=m0^2/mu^2 and vacuum_density=rho_Lambda/mu^4.
    The potential is mu^4(F-F_*), the radial kinetic term is mu^2 Z,
    and eta has no independent derivative term.  The retained initial
    radius is L0^2=3pi; the reference and vacuum radius satisfy Lref^2=2pi.
    This finite classical realization has its own initial data and does
    not change the production finite-response endpoint. The certified
    example uses g=1, Z=2, m0^2/mu^2=3/(8*pi), M_P/mu>=1 and vacuum
    density at most 1/1000 in these units.
    """
    from scipy.integrate import solve_ivp, quad
    from scipy.linalg import eigh
    from scipy.optimize import brentq
    from cg_frg.ewsb.native_condensate import (
        restoring_response, complete_relative_potential, joint_native_source_response,
        certify_common_source_interval)
    if (not all(math.isfinite(v) for v in (planck_ratio, mass_squared, vacuum_density, rtol, atol))
            or min(planck_ratio, mass_squared, rtol, atol) <= 0 or vacuum_density < 0
            or isinstance(samples, bool) or not isinstance(samples, int) or samples < 3):
        raise ValueError("positive action scales, tolerances and at least three samples required")
    if not joint_certificate.get('passed'):
        raise ValueError("a passed joint native stationary certificate is required")
    midpoint = lambda values: sum(float(v) for v in values)/2
    g, Z = (midpoint(joint_certificate['inputs'][key]) for key in ('g', 'Z'))
    if min(g, Z) <= 0:
        raise ValueError("positive certified coupling and radial normalization required")
    if (g != 1. or Z != 2. or abs(mass_squared-3/(8*math.pi)) > 1e-14
            or planck_ratio < 1 or vacuum_density > .001):
        raise ValueError("the certified common background requires g=1, Z=2, the constant-shell mass and its declared density range")
    finite_time_certificate = certify_common_source_interval(
        planck_ratio=planck_ratio, vacuum_density=vacuum_density)
    Lref_squared, L0_squared = 2*math.pi, 3*math.pi
    vacuum_u = float(joint_certificate['full_response_estimate']['u'])
    work = {'algebraic_source_solves': 0, 'source_derivative_evaluations': 0,
            'background_rhs_evaluations': 0, 'full_potential_integrals': 0,
            'potential_restoring_function_evaluations': 0,
            'initial_amplitude_restoring_evaluations': 0,
            'phase_quadrature_evaluations': 0, 'reused_vacuum_root_certificates': 1,
            'ordinary_kinetic_eigensolves': 0, 'generalized_characteristic_eigensolves': 0}
    def potential(E, L):
        value = complete_relative_potential(amplitude_squared=E*E, L=L, g=g)
        work['full_potential_integrals'] += 1
        work['potential_restoring_function_evaluations'] += value['restoring_function_evaluations']
        return value
    E_vacuum = math.sqrt(vacuum_u/(g*Lref_squared))
    vacuum_potential = potential(E_vacuum, math.sqrt(Lref_squared))
    target = 8*(1/math.pi-1/L0_squared)/(g*L0_squared)
    def initial_amplitude_equation(u):
        work['initial_amplitude_restoring_evaluations'] += 1
        return restoring_response(u)-target
    upper = max(1., vacuum_u)
    while initial_amplitude_equation(upper) < 0:
        upper *= 2
    u0 = brentq(initial_amplitude_equation, 0., upper, xtol=2e-14, rtol=1e-14)
    E0 = math.sqrt(u0/(g*L0_squared))
    eta0 = -.5*math.log(L0_squared/Lref_squared)
    response0 = joint_native_source_response(amplitude_squared=E0*E0, L=math.sqrt(L0_squared), g=g)
    occupied_energy = -response0['Feta']
    if occupied_energy <= 0:
        raise ArithmeticError("positive occupied background requires negative static source force")
    M0, B0 = math.exp(-3*eta0), mass_squared*math.exp(-eta0)
    radius0 = math.sqrt(occupied_energy/B0)
    phase_velocity0 = math.sqrt(occupied_energy/M0)
    potential0 = potential(E0, math.sqrt(L0_squared))
    density0 = occupied_energy+potential0['value']-vacuum_potential['value']+vacuum_density
    if density0 <= 0:
        raise ArithmeticError("initial total density must be positive")
    H0 = math.sqrt(density0/(3*planck_ratio**2))
    initial = np.array([1., E0, 0., radius0, 0., 0., M0*phase_velocity0, H0])
    duration = 1/(4*math.sqrt(mass_squared)) if duration is None else float(duration)
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("positive finite evolution duration required")
    common = dict(g=g, Z=Z, mass_squared=mass_squared,
                  reference_radius_squared=Lref_squared)
    def source(state):
        return common_source_background_state(state, **common, work=work)
    def derivative(state, data):
        a, E, p_E, phi1, phi2, p1, p2, H = state
        v, e = data['matter_velocity'], data['E_velocity']
        return np.array([a*H, e, -a**3*data['U_E'], v[0], v[1],
            -a**3*data['B']*phi1, -a**3*data['B']*phi2,
            -(Z*e*e+2*data['T'])/(2*planck_ratio**2)])
    def rhs(t, state):
        work['background_rhs_evaluations'] += 1
        return derivative(state, source(state))
    times = np.linspace(0., duration, samples)
    solution = solve_ivp(rhs, (0., duration), initial, method='DOP853',
                         t_eval=times, dense_output=True, rtol=rtol, atol=atol)
    if not solution.success:
        raise ArithmeticError(solution.message)
    rows = []
    charge0 = initial[3]*initial[6]-initial[4]*initial[5]
    for index, (t, state) in enumerate(zip(times, solution.y.T)):
        data = source(state)
        value = potential0 if index == 0 else potential(state[1], data['L'])
        U = value['value']-vacuum_potential['value']+vacuum_density
        e, v, H = data['E_velocity'], data['matter_velocity'], state[7]
        T, V = data['T'], data['V']
        density, pressure = Z*e*e/2+T+V+U, Z*e*e/2+T-V-U
        density_dot = (-3*H*Z*e*e-6*H*T
                       +data['source_residual']*data['eta_velocity'])
        momentum_dot = -state[0]**3*data['B']*state[3:5]
        force_derivative = (data['U_eta_E']*e-18*H*T
            +3*float(state[5:7]@momentum_dot)/(state[0]**6*data['M'])
            -data['B']*float(state[3:5]@v)
            +data['hamiltonian_source_curvature']*data['eta_velocity'])
        charge = state[3]*state[6]-state[4]*state[5]
        phase_rate = float((state[3]*v[1]-state[4]*v[0])/(state[3:5]@state[3:5]))
        if phase_rate <= 0:
            raise ArithmeticError("occupied phase clock lost positive orientation")
        speeds = eigh(data['gradient'], data['kinetic'], eigvals_only=True)
        work['generalized_characteristic_eigensolves'] += 1
        kinetic_eigenvalues = np.linalg.eigvalsh(data['kinetic'])
        work['ordinary_kinetic_eigensolves'] += 1
        rows.append({'time': float(t), 'state': state.tolist(), 'eta': data['eta'],
            'radius': data['L'], 'source_residual': data['source_residual'],
            'source_derivative_residual': force_derivative,
            'hamiltonian_source_curvature': data['hamiltonian_source_curvature'],
            'velocity_source_curvature': data['velocity_source_curvature'],
            'kinetic_eigenvalues': kinetic_eigenvalues.tolist(),
            'gradient_eigenvalues': sorted([Z, data['M'], data['M']]),
            'characteristic_speeds_squared': speeds.tolist(),
            'density': density, 'pressure': pressure,
            'friedmann_residual': 3*planck_ratio**2*H*H-density,
            'continuity_residual': density_dot+3*H*(density+pressure),
            'charge_relative_residual': (charge-charge0)/charge0,
            'phase_rate': phase_rate, 'clock_rate_residual': phase_rate/math.sqrt(phase_rate**2)-1,
            'potential_quadrature_error_estimate': value['quadrature_error_estimate']})
    def phase_integrand(t):
        work['phase_quadrature_evaluations'] += 1
        state = solution.sol(t)
        data = source(state)
        return float((state[3]*data['matter_velocity'][1]-state[4]*data['matter_velocity'][0])/
                     (state[3:5]@state[3:5]))
    phase_integral, phase_error = quad(phase_integrand, 0., duration,
                                     epsabs=5e-11, epsrel=5e-11)
    phase_readout = np.unwrap(np.arctan2(solution.y[4], solution.y[3]))
    phase_residual = float(phase_readout[-1]-phase_readout[0]-phase_integral)
    maximum = lambda key: max(abs(row[key]) for row in rows)
    initial_source = source(initial)
    initial_feedback = 9*H0*occupied_energy/(initial_source['velocity_source_curvature']+9*occupied_energy)
    initial_feedback_residual = initial_source['eta_velocity']-initial_feedback
    checks = {'continuous_initial_interval': finite_time_certificate['status'] == 'certified',
        'positive_reduced_kinetic': min(min(r['kinetic_eigenvalues']) for r in rows) > 0,
        'positive_source_velocity_curvature': min(r['velocity_source_curvature'] for r in rows) > 0,
        'positive_causal_characteristics': min(min(r['characteristic_speeds_squared']) for r in rows) > 0
            and max(max(r['characteristic_speeds_squared']) for r in rows) < 1+1e-12,
        'source_balance': maximum('source_residual') < 2e-11,
        'differentiated_source_balance': maximum('source_derivative_residual') < 2e-11,
        'friedmann_constraint': maximum('friedmann_residual')/density0 < 2e-8,
        'stress_conservation': maximum('continuity_residual') < 2e-11,
        'phase_charge_conservation': maximum('charge_relative_residual') < 2e-8,
        'phase_clock_reconstruction': abs(phase_residual) < 2e-8,
        'initial_characteristic_bound': min(rows[0]['characteristic_speeds_squared']) > 2/11,
        'nonzero_initial_feedback': initial_feedback > 0 and abs(initial_feedback_residual) < 2e-12}
    return {'scope': 'one occupied classical Einstein--matter background with an algebraic native radius source',
        'action': 'Einstein + positive radial kinetic + conformal matter kinetic and mass + complete relative potential',
        'source_equation': 'U_eta+3T-V=0, solved at each background evaluation',
        'inputs': {'g': g, 'Z': Z, 'planck_ratio': planck_ratio, 'mass_squared': mass_squared,
            'vacuum_density': vacuum_density, 'reference_radius_squared': Lref_squared,
            'initial_radius_squared': L0_squared, 'duration': duration, 'samples': samples,
            'relative_tolerance': rtol, 'absolute_tolerance': atol},
        'units': 'mu*t, e/mu, varphi/mu, H/mu; densities divided by mu^4; M_P/mu supplied',
        'vacuum_potential': vacuum_potential, 'initial_occupied_energy': occupied_energy,
        'initial_density': density0, 'initial_phase_charge': charge0,
        'initial_amplitude_stationarity_residual': response0['Fy'],
        'initial_feedback': {'eta_velocity': initial_source['eta_velocity'],
            'analytic_eta_velocity': initial_feedback, 'identity_residual': initial_feedback_residual,
            'radius_velocity': -math.sqrt(L0_squared)*initial_source['eta_velocity']},
        'source_determined_from_state': True, 'independent_source_kinetic_field': False,
        'assigned_production_endpoint': False, 'samples': rows,
        'clock': {'phase_difference': float(phase_readout[-1]-phase_readout[0]),
            'integrated_phase_rate': phase_integral, 'phase_integral_error_estimate': phase_error,
            'phase_reconstruction_residual': phase_residual,
            'proper_time_duration': duration, 'relation': 'ds=dtheta/sqrt(X), X=phase_rate^2'},
        'maximum_relative_friedmann_residual': maximum('friedmann_residual')/density0,
        'maximum_relative_charge_residual': maximum('charge_relative_residual'),
        'finite_time_certificate': finite_time_certificate,
        'verification_scope': 'certified continuous initial interval; extended floating-point trajectory and sampled margins',
        'operation_counts': work, 'checks': {k: bool(v) for k, v in checks.items()},
        'passed': bool(all(checks.values()))}


def evaluate_common_source_reuse(*, background, steps=64, source_budget='0.000025'):
    """Certify two finite-record evolutions of the same implicit source system.

    Both paths start from the same decimal encoding of the supplied initial
    canonical state.  The reference is the complete spectral vector field
    with its exact algebraic source.  Rational, piecewise-linear Euler
    reconstructions either refresh the source at every node or reuse it
    until its certified residual exceeds a common budget.  Spectral values
    and derivatives are cached at refreshes; Taylor bounds cover reuse.

    The error is relative to that finite initial record.  Uncertainty in
    constructing initial data from an upstream physical state is a separate
    initial-error term in the reconstruction theorem.  All stored error
    bounds round outward; floating roots only propose source values.
    """
    from fractions import Fraction as Q
    from cg_core.rational_interval import Interval as I, GRID, pi_interval
    if (isinstance(steps, bool) or not isinstance(steps, int) or steps < 2
            or not background.get('passed')):
        raise ValueError('a passed common background and at least two steps are required')
    certificate = background['finite_time_certificate']
    if certificate.get('status') != 'certified':
        raise ValueError('the common-source invariant-box certificate is required')
    inputs = background['inputs']
    if inputs['g'] != 1 or inputs['Z'] != 2:
        raise ValueError('the retained common-source example requires g=1 and Z=2')
    names = ('a', 'E', 'p_E', 'phi_1', 'phi_2', 'p_1', 'p_2', 'H')
    work = {'interval_additions': 0, 'interval_multiplications': 0,
            'interval_divisions': 0, 'interval_square_roots': 0,
            'interval_negations': 0, 'rational_point_conversions': 0,
            'interval_absolute_bounds': 0, 'maximum_interval_endpoint_bits': 0,
            'spectral_endpoint_evaluations': 0, 'spectral_shell_pair_evaluations': 0,
            'spectral_tail_moment_terms': 0}

    class Bound:
        """Count the actual outward interval primitives used by this record."""
        def __init__(self, value):
            if not isinstance(value, (Bound, I)):
                work['rational_point_conversions'] += 1
            self.v = value.v if isinstance(value, Bound) else value if isinstance(value, I) else I.point(value)
            work['maximum_interval_endpoint_bits'] = max(
                work['maximum_interval_endpoint_bits'], self.v.lo.bit_length(), self.v.hi.bit_length())
        def __add__(self, other):
            work['interval_additions'] += 1
            return Bound(self.v+Bound(other).v)
        __radd__ = __add__
        def __neg__(self):
            work['interval_negations'] += 1
            return Bound(-self.v)
        def __sub__(self, other):
            return self+-Bound(other)
        def __rsub__(self, other):
            return Bound(other)+-self
        def __mul__(self, other):
            work['interval_multiplications'] += 1
            return Bound(self.v*Bound(other).v)
        __rmul__ = __mul__
        def __truediv__(self, other):
            work['interval_divisions'] += 1
            return Bound(self.v/Bound(other).v)
        def __rtruediv__(self, other):
            return Bound(other)/self
        def __pow__(self, exponent):
            if exponent < 0:
                return Bound(1)/(self**(-exponent))
            answer = Bound(1)
            for _ in range(exponent):
                answer = answer*self
            return answer
        def sqrt(self):
            work['interval_square_roots'] += 1
            return Bound(self.v.sqrt())
        def absolute(self):
            work['interval_absolute_bounds'] += 1
            upper = max(abs(self.v.lo), abs(self.v.hi))
            return Bound(I(upper, upper))
        def upper(self):
            return Bound(I(self.v.hi, self.v.hi))
        def lower(self):
            return Bound(I(self.v.lo, self.v.lo))
        def decimal(self):
            return self.v.decimal_bounds(18)

    maximum = lambda values: Bound(I(max(v.v.hi for v in values), max(v.v.hi for v in values)))
    pi, zero, one = Bound(pi_interval()), Bound(0), Bound(1)
    P = Bound(str(inputs['planck_ratio']))
    m0, duration = 3/(8*pi), Bound(Q(1, 100))
    step = duration/steps
    budget = Bound(source_budget)
    if budget.v.lo <= 0:
        raise ValueError('a positive source residual budget is required')
    box = [Bound(I.bounds(*certificate['phase_space_box'][name])) for name in names]
    alpha_box = Bound(I.bounds(*certificate['source_alpha_interval']))
    kappa = Bound(I.bounds(*certificate['canonical_source_curvature_h_H'])).lower()
    shells = 64
    spectral_terms = [(Q(4*(2*j+1)**2-1, 4), (2*j+1)**2) for j in range(shells+1)]
    tail_slope = pi*(pi+2)/8
    for c, d in spectral_terms:
        tail_slope -= Bound(d)/Bound(c)**2
        work['spectral_tail_moment_terms'] += 1
    if tail_slope.v.lo <= 0:
        raise ArithmeticError('the complete positive spectral tail lost its enclosure')
    next_c = Q(4*(2*shells+3)**2-1, 4)

    def spectral(u):
        # The known complete slope removes the leading 1/N tail.  For c
        # above the next shell, 0 <= u S2-tail(H) <= u² S2/c_next.
        h, hp = Bound(0), Bound(0)
        for c, d in spectral_terms:
            h += d*u/(Bound(c)*(c+u))
            hp += d/(c+u)**2
        htail, hperror = u*tail_slope, 2*u*tail_slope/next_c
        herr = u**2*tail_slope/next_c
        h += Bound(I((htail-herr).v.lo, htail.v.hi))
        hp += Bound(I((tail_slope-hperror).v.lo, tail_slope.v.hi))
        work['spectral_endpoint_evaluations'] += 1
        work['spectral_shell_pair_evaluations'] += shells+1
        return h, hp

    def squared(value):
        if value.v.lo <= 0 <= value.v.hi:
            return Bound(I(0, (value.absolute()**2).v.hi))
        return value**2

    def data(state, alpha, h):
        a, E, pe, p1, p2, q1, q2, hubble = state
        u, z = 2*pi*E**2/alpha**2, alpha**2/(2*pi)
        T = (squared(q1)+squared(q2))*alpha**3/(2*a**6)
        V = m0*(squared(p1)+squared(p2))/(2*alpha)
        ue = 16*E*(z-1/pi)+2*u*h/E
        constraint = 16*E**2*z-2*u*h+3*T-V
        vector = [a*hubble, pe/(2*a**3), -a**3*ue,
                  q1*alpha**3/a**3, q2*alpha**3/a**3,
                  -a**3*m0*p1/alpha, -a**3*m0*p2/alpha,
                  -(squared(pe)/(4*a**6)+T)/P**2]
        return constraint, vector, T, ue, u, z

    # Uniform derivatives are taken at fixed eta=log(alpha), then the
    # implicit source derivative is added using C_eta >= kappa.
    a, E, pe, p1, p2, q1, q2, hubble = box
    ubox = 2*pi*E**2/alpha_box**2
    hbox, hpbox = spectral(ubox)
    _, _, T, ue, _, z = data(box, alpha_box, hbox)
    uee = 16*(z-1/pi)+(2*ubox*hbox+4*ubox**2*hpbox)/E**2
    ueeta = 32*E*z-4*ubox*(hbox+ubox*hpbox)/E
    Cx = [(-18*T/a).absolute(), ueeta.absolute(), zero,
          (m0*p1/alpha_box).absolute(), (m0*p2/alpha_box).absolute(),
          (3*alpha_box**3*q1/a**6).absolute(),
          (3*alpha_box**3*q2/a**6).absolute(), zero]
    source_gradient = sum(Cx, zero)/kappa
    source_lipschitz = maximum([
        (a**3*ueeta).absolute(), (3*q1*alpha_box**3/a**3).absolute(),
        (3*q2*alpha_box**3/a**3).absolute(),
        (a**3*m0*p1/alpha_box).absolute(), (a**3*m0*p2/alpha_box).absolute(),
        (3*T/P**2).absolute()])
    fixed_rows = [a.absolute()+hubble.absolute(),
        (3*pe/(2*a**4)).absolute()+(1/(2*a**3)).absolute(),
        (3*a**2*ue).absolute()+(a**3*uee).absolute(),
        (3*q1*alpha_box**3/a**4).absolute()+(alpha_box**3/a**3).absolute(),
        (3*q2*alpha_box**3/a**4).absolute()+(alpha_box**3/a**3).absolute(),
        (3*a**2*m0*p1/alpha_box).absolute()+(a**3*m0/alpha_box).absolute(),
        (3*a**2*m0*p2/alpha_box).absolute()+(a**3*m0/alpha_box).absolute(),
        (6*(squared(pe)/(4*a**6)+T)/(P**2*a)).absolute()
          +(pe/(2*P**2*a**6)).absolute()
          +(alpha_box**3*q1/(P**2*a**6)).absolute()
          +(alpha_box**3*q2/(P**2*a**6)).absolute()]
    ell = maximum(fixed_rows)+source_lipschitz*source_gradient
    amplification = 1/(1-ell*step)
    if ell.v.lo < 0 or (ell*step).v.hi >= GRID:
        raise ValueError('increase the number of steps for the certified Lipschitz bound')
    second_h = (2*(pi*(pi+2)/8)/(Q(3, 4)+ubox.lower())).upper()
    radius_lipschitz = ((2*pi).sqrt()/alpha_box.lower()).upper()
    phase_lipschitz = ((p1.absolute()+p2.absolute())/(p1.lower()**2)).upper()
    initial = [Bound(str(value)) for value in background['samples'][0]['state']]
    for name, value, domain in zip(names, initial, box):
        enclosure = I.bounds(*certificate['initial_state_enclosures'][name])
        if value.v.lo < enclosure.lo or value.v.hi > enclosure.hi:
            raise ValueError('the finite initial record leaves its certified enclosure: '+name)
        if not domain.v.lo < value.v.lo <= value.v.hi < domain.v.hi:
            raise ValueError('the finite initial record is not interior to its state box')
    setup_counts = dict(work)

    def run(reuse):
        state, error, cached = list(initial), Bound(0), None
        counts = {'algebraic_source_solves': 0, 'source_derivative_evaluations': 0,
                  'accepted_source_reuses': 0, 'source_budget_tests': 0,
                  'reconstructed_segments': steps, 'source_refreshes': 0}
        before = dict(work)
        largest_residual, largest_segment_source_error = Bound(0), Bound(0)
        max_error, radius_error, phase_error = Bound(0), Bound(0), Bound(0)
        source_round = []
        def cached_values():
            u = 2*pi*state[1]**2/cached['alpha']**2
            difference = u-cached['u']
            remainder = second_h*squared(difference)/2
            h = cached['h']+cached['hp']*difference+Bound(I(-remainder.v.hi, remainder.v.hi))
            return data(state, cached['alpha'], h)
        for index in range(steps):
            if cached is not None and reuse:
                current = cached_values()
                counts['source_budget_tests'] += 1
                refresh = current[0].absolute().v.hi > budget.v.lo
            else:
                refresh = True
            if refresh:
                proposed = common_source_background_state(
                    [float(Q((value.v.lo+value.v.hi)//2, GRID)) for value in state],
                    g=1., Z=2., mass_squared=inputs['mass_squared'],
                    reference_radius_squared=inputs['reference_radius_squared'], work=counts)
                alpha = Bound(str(math.exp(proposed['eta'])))
                if not alpha_box.v.lo < alpha.v.lo <= alpha.v.hi < alpha_box.v.hi:
                    raise ArithmeticError('proposed source leaves its certified bracket')
                u = 2*pi*state[1]**2/alpha**2
                h, hp = spectral(u)
                cached = {'alpha': alpha, 'u': u, 'h': h, 'hp': hp}
                current = data(state, alpha, h)
                counts['source_refreshes'] += 1
                source_round.append(index)
            else:
                counts['accepted_source_reuses'] += 1
            constraint, vector = current[:2]
            next_state, slopes = [], []
            for value, component in zip(state, vector):
                chosen = Bound(I((component.v.lo+component.v.hi)//2,
                                 (component.v.lo+component.v.hi)//2))
                tentative = value+step*chosen
                midpoint = (tentative.v.lo+tentative.v.hi)//2
                following = Bound(I(midpoint, midpoint))
                next_state.append(following)
                slopes.append((following-value)/step)
            rounding_defect = maximum([(slope-component).absolute()
                                       for slope, component in zip(slopes, vector)])
            source_error = constraint.absolute()/kappa
            B = maximum([slope.absolute() for slope in slopes])
            defect = rounding_defect+source_lipschitz*source_error+ell*step*B
            error = (error+step*defect)*amplification
            segment_source = (constraint.absolute()+sum(Cx, zero)*step*B)/kappa
            largest_residual = maximum([largest_residual, constraint.absolute()])
            largest_segment_source_error = maximum([largest_segment_source_error, segment_source])
            max_error = maximum([max_error, error])
            radius_error = maximum([radius_error, radius_lipschitz*(source_gradient*error+segment_source)])
            phase_error = maximum([phase_error, phase_lipschitz*error])
            for value, domain in zip(next_state, box):
                if not domain.v.lo < value.v.lo <= value.v.hi < domain.v.hi:
                    raise ArithmeticError('reconstructed common-source trajectory leaves its certified box')
            state = next_state
        counts.update({key: value-before[key] for key, value in work.items()
                       if key != 'maximum_interval_endpoint_bits'})
        final = [float(Q((value.v.lo+value.v.hi)//2, GRID)) for value in state]
        return {'source_refresh_nodes': source_round, 'operation_counts': counts,
            'final_state': [value.decimal() for value in state],
            'final_scale_factor': final[0],
            'final_phase': math.atan2(final[4], final[3]),
            'final_held_radius': math.sqrt(2*math.pi)/float(Q(cached['alpha'].v.lo, GRID)),
            'maximum_node_source_residual': largest_residual.decimal()[1],
            'maximum_within_segment_source_error': largest_segment_source_error.decimal()[1],
            'full_interval_state_error_upper_bound': max_error.decimal()[1],
            'full_interval_scale_factor_error_upper_bound': max_error.decimal()[1],
            'full_interval_radius_error_upper_bound': radius_error.decimal()[1],
            'full_interval_phase_error_upper_bound': phase_error.decimal()[1],
            'reference': 'complete spectral vector field and exact implicit source, with the identical finite initial record'}

    full, reused = run(False), run(True)
    checks = {'source_solves_reduced': reused['operation_counts']['source_refreshes'] < steps,
              'spectral_work_reduced': reused['operation_counts']['spectral_shell_pair_evaluations']
                                      < full['operation_counts']['spectral_shell_pair_evaluations'],
              'continuous_error_bounds': all(float(row['full_interval_state_error_upper_bound']) > 0
                                            for row in (full, reused)),
              'node_source_budget': Q(reused['maximum_node_source_residual']) <= Q(source_budget)}
    return {'scope': 'continuous reconstruction bounds for a homogeneous occupied common-source realization',
            'initial_data_convention': 'shared exact decimal canonical record; upstream construction uncertainty is a separate initial-error term',
            'initial_state': [value.decimal() for value in initial],
            'initial_data_error_bound': '0',
            'initial_friedmann_defect_diagnostic': background['samples'][0]['friedmann_residual'],
            'physical_initial_data_scope': 'the shared canonical record lies in the certified initial enclosure; its floating Friedmann diagnostic is recorded separately from the rigorous trajectory error',
            'duration': duration.decimal(), 'steps': steps, 'source_residual_budget': str(source_budget),
            'uniform_bounds': {'canonical_source_curvature_lower': kappa.decimal()[0],
                'source_map_lipschitz': source_gradient.decimal()[1],
                'fixed_state_source_lipschitz': source_lipschitz.decimal()[1],
                'implicit_vector_field_lipschitz': ell.decimal()[1],
                'radius_lipschitz_in_eta': radius_lipschitz.decimal()[1],
                'phase_lipschitz_in_state': phase_lipschitz.decimal()[1]},
            'certificate': 'r_(j+1) <= (r_j+h*d_j)/(1-h*ell); d_j bounds the complete reconstruction defect on every segment',
            'spectral_tail': 'H_N+u*S2-u^2*S2/c_next <= H <= H_N+u*S2; S2=Hprime(0)-Hprime_N(0)',
            'setup_operation_counts': setup_counts,
            'reused_invariant_box_work_counts': certificate['work_counts'],
            'maximum_interval_endpoint_bits': work['maximum_interval_endpoint_bits'],
            'full_source': full, 'reused_source': reused,
            'invariant_box_certificate_reused': True,
            'infinite_spectral_tail_included': True,
            'arithmetic': 'outward rational grid intervals, complete spectral tail and counted arithmetic; proposed roots are independently enclosed by their residual',
            'checks': checks, 'passed': all(checks.values())}


def evaluate_plane_common_source(*, background, points=17, amplitude=1e-3,
                                duration=.01, steps=8, refine=True):
    """Planar Einstein--matter evolution with the same auxiliary-radius action.

    The nonzero cosine amplitude is initial data, not a physical parameter.
    A conformally flat CMC constraint solve determines the initial metric
    and expansion. Synchronous planar ADM evolution then advances metric,
    matter and the pointwise algebraic source together. Fourier collocation
    and RK4 produce central values; constraint and resolution checks are
    reported independently of the homogeneous interval certificate.
    """
    from scipy.optimize import brentq, root
    from cg_frg.ewsb.native_condensate import (
        joint_native_source_response, complete_relative_potential)
    if (not background.get('passed') or isinstance(points, bool)
            or not isinstance(points, int) or points < 9 or points % 2 == 0
            or isinstance(steps, bool) or not isinstance(steps, int) or steps < 2
            or not all(math.isfinite(v) for v in (amplitude, duration))
            or not 0 <= abs(amplitude) <= .01 or not 0 < duration <= .1):
        raise ValueError('passed background, odd grid, positive steps and small finite initial perturbation required')
    cfg = background['inputs']
    P, Z, g = (float(cfg[k]) for k in ('planck_ratio', 'Z', 'g'))
    m2, Lref2, vacuum = (float(cfg[k]) for k in
                        ('mass_squared', 'reference_radius_squared', 'vacuum_density'))
    flat = np.asarray(background['samples'][0]['state'], float)
    vacuum_potential = float(background['vacuum_potential']['value'])
    work = {'algebraic_source_solves': 0, 'source_response_evaluations': 0,
            'potential_integrals': 0, 'potential_integrand_evaluations': 0,
            'spatial_transforms': 0, 'rhs_evaluations': 0,
            'initial_constraint_evaluations': 0, 'principal_eigensolves': 0}

    def realization(n, nsteps):
        x = 2*math.pi*np.arange(n)/n
        frequencies = np.fft.fftfreq(n, 1/n)
        def derivative(values, order=1):
            work['spatial_transforms'] += 2*np.asarray(values).size//n
            return np.fft.ifft((1j*frequencies)**order*np.fft.fft(values, axis=-1), axis=-1).real

        def source_data(state):
            A, Bmetric, Kx, Ky, E, pE, f1, f2, p1, p2 = state
            volume = A*Bmetric**2
            fields, momenta = np.array([f1, f2]), np.array([p1, p2])
            Ex = derivative(E)
            fx = derivative(fields)
            if np.min(A) <= 0 or np.min(Bmetric) <= 0 or np.min(E) <= 0:
                raise ArithmeticError('planar metric or condensate left its positive domain')
            out = {key: np.empty(n) for key in
                   ('eta', 'M', 'mass_coefficient', 'T', 'G', 'V', 'U', 'U_E',
                    'h', 'hH', 'source_residual')}
            for index in range(n):
                def evaluate(eta):
                    work['source_response_evaluations'] += 1
                    M = math.exp(-3*eta)
                    mass_coefficient = m2*math.exp(-eta)
                    L = math.sqrt(Lref2)*math.exp(-eta)
                    response = joint_native_source_response(
                        amplitude_squared=E[index]**2, L=L, g=g)
                    T = float(momenta[:, index]@momenta[:, index])/(2*volume[index]**2*M)
                    G = M*float(fx[:, index]@fx[:, index])/(2*A[index]**2)
                    V = mass_coefficient*float(fields[:, index]@fields[:, index])/2
                    return response['Feta']+3*(T-G)-V, response, M, mass_coefficient, T, G, V, L
                work['algebraic_source_solves'] += 1
                eta = brentq(lambda z: evaluate(z)[0], -.35, -.05, xtol=8e-15, rtol=4e-15)
                residual, response, M, mass_coefficient, T, G, V, L = evaluate(eta)
                potential = complete_relative_potential(amplitude_squared=E[index]**2, L=L, g=g)
                work['potential_integrals'] += 1
                work['potential_integrand_evaluations'] += potential['restoring_function_evaluations']
                h = response['hessian_eta_y'][0][0]-9*T+9*G+V
                hH = response['hessian_eta_y'][0][0]+9*T+9*G+V
                if h-18*G <= 0:
                    raise ArithmeticError('planar physical spatial principal form lost positivity')
                values = (eta, M, mass_coefficient, T, G, V,
                          potential['value']-vacuum_potential+vacuum,
                          2*E[index]*response['Fy'], h, hH, residual)
                for key, value in zip(out, values):
                    out[key][index] = value
            vE = pE/(volume*Z)
            velocities = momenta/(volume*out['M'])
            radial_T, radial_G = Z*vE**2/2, Z*Ex**2/(2*A**2)
            out.update(volume=volume, Ex=Ex, fx=fx, fields=fields, momenta=momenta,
                       vE=vE, velocities=velocities,
                       total_T=out['T']+radial_T, total_G=out['G']+radial_G)
            out['density'] = out['total_T']+out['total_G']+out['V']+out['U']
            return out

        def geometry(state):
            A, Bmetric = state[:2]
            Ax, Bx, Bxx = derivative(A), derivative(Bmetric), derivative(Bmetric, 2)
            Rx = -2*(Bxx/Bmetric-Ax*Bx/(A*Bmetric))/A**2
            Ry = -(Bxx/Bmetric+(Bx/Bmetric)**2-Ax*Bx/(A*Bmetric))/A**2
            return Rx, Ry, Bx

        fields0 = np.array([flat[3]*(1+amplitude*np.cos(x)), np.zeros(n)])
        def initial_state(unknown):
            psi, H = unknown[:n], unknown[-1]
            return np.array([psi**2, psi**2, np.full(n, -H), np.full(n, -H),
                             np.full(n, flat[1]), np.zeros(n), fields0[0], fields0[1],
                             np.zeros(n), np.full(n, flat[6])])
        def initial_constraint(unknown):
            work['initial_constraint_evaluations'] += 1
            psi, H = unknown[:n], unknown[-1]
            data = source_data(initial_state(unknown))
            constraint = -8*derivative(psi, 2)+(6*H**2-2*data['density']/P**2)*psi**5
            return np.r_[constraint, np.mean(psi)-1]
        solved = root(initial_constraint, np.r_[np.ones(n), flat[-1]], tol=2e-10)
        initial_residual = np.max(np.abs(initial_constraint(solved.x)))
        if not solved.success or initial_residual > 2e-10 or solved.x[-1] <= 0:
            raise ArithmeticError('nonuniform Einstein initial constraints failed')
        state = initial_state(solved.x)

        def rhs(state):
            work['rhs_evaluations'] += 1
            data = source_data(state)
            A, Bmetric, Kx, Ky, E, pE, f1, f2, p1, p2 = state
            Rx, Ry, _ = geometry(state)
            K, W = Kx+2*Ky, data['U']+data['V']
            d_pE = derivative(Bmetric**2/A*Z*data['Ex'])-data['volume']*data['U_E']
            d_p = derivative(Bmetric**2/A*data['M']*data['fx'])-data['volume']*data['mass_coefficient']*data['fields']
            return np.array([-Kx*A, -Ky*Bmetric,
                Rx+K*Kx-(2*data['total_G']+W)/P**2, Ry+K*Ky-W/P**2,
                data['vE'], d_pE, data['velocities'][0], data['velocities'][1], d_p[0], d_p[1]])

        def diagnose(state, t):
            data = source_data(state)
            A, Bmetric, Kx, Ky = state[:4]
            Rx, Ry, Bx = geometry(state)
            hamiltonian = Rx+2*Ry+(Kx+2*Ky)**2-Kx**2-2*Ky**2-2*data['density']/P**2
            current_x = -(Z*data['vE']*data['Ex']+data['M']*np.sum(data['velocities']*data['fx'], axis=0))
            momentum = -2*derivative(Ky)+2*Bx/Bmetric*(Kx-Ky)-current_x/P**2
            f, v = data['fields'], data['velocities']
            r2 = np.sum(f*f, axis=0)
            theta_t = (f[0]*v[1]-f[1]*v[0])/r2
            theta_x = (f[0]*data['fx'][1]-f[1]*data['fx'][0])/r2
            clock_X = theta_t**2-theta_x**2/A**2
            if np.min(clock_X) <= 0 or np.min(theta_t) <= 0:
                raise ArithmeticError('planar matter phase left its future timelike clock domain')
            min_kinetic = min_spatial = math.inf
            max_imaginary = 0.
            min_speed = math.inf
            for index in range(n):
                metric = np.diag([Z, data['M'][index], data['M'][index]])
                velocity = np.r_[0., v[:, index]]
                gradient = np.r_[0., data['fx'][:, index]/A[index]]
                factor = 9*data['M'][index]**2/data['h'][index]
                kinetic = metric+factor*np.outer(velocity, velocity)
                spatial = metric-factor*np.outer(gradient, gradient)
                cross = -factor*(np.outer(velocity, gradient)+np.outer(gradient, velocity))/2
                principal = np.block([[np.zeros((3, 3)), np.eye(3)],
                    [np.linalg.solve(kinetic, spatial), 2*np.linalg.solve(kinetic, cross)]])
                eigen = np.linalg.eigvals(principal)
                work['principal_eigensolves'] += 3
                min_kinetic = min(min_kinetic, float(np.linalg.eigvalsh(kinetic)[0]))
                min_spatial = min(min_spatial, float(np.linalg.eigvalsh(spatial)[0]))
                max_imaginary = max(max_imaginary, float(np.max(np.abs(eigen.imag))))
                min_speed = min(min_speed, float(np.min(np.abs(eigen.real))))
            charge = float(np.mean(f[0]*data['momenta'][1]-f[1]*data['momenta'][0]))
            return {'time': t, 'hamiltonian_residual': float(np.max(np.abs(hamiltonian))),
                    'momentum_residual': float(np.max(np.abs(momentum))),
                    'source_residual': float(np.max(np.abs(data['source_residual']))),
                    'minimum_velocity_curvature': float(np.min(data['h'])),
                    'minimum_spatial_curvature_margin': float(np.min(data['h']-18*data['G'])),
                    'minimum_kinetic_eigenvalue': min_kinetic, 'minimum_spatial_eigenvalue': min_spatial,
                    'maximum_characteristic_imaginary_part': max_imaginary,
                    'minimum_absolute_characteristic_speed': min_speed,
                    'minimum_phase_norm': float(np.min(clock_X)),
                    'minimum_phase_rate': float(np.min(theta_t)),
                    'proper_to_synchronous_clock_rate': [float(np.min(np.sqrt(clock_X)/theta_t)),
                                                       float(np.max(np.sqrt(clock_X)/theta_t))],
                    'charge': charge, 'mean_expansion': float(np.mean(-(Kx+2*Ky)/3)),
                    'mean_volume_scale': float(np.mean(data['volume'])**(1/3)),
                    'source_range': [float(np.min(data['eta'])), float(np.max(data['eta']))],
                    'density_range': [float(np.min(data['density'])), float(np.max(data['density']))]}

        diagnostics = [diagnose(state, 0.)]
        dt = duration/nsteps
        for step in range(nsteps):
            k1 = rhs(state)
            k2 = rhs(state+dt*k1/2)
            k3 = rhs(state+dt*k2/2)
            k4 = rhs(state+dt*k3)
            state = state+dt*(k1+2*k2+2*k3+k4)/6
            diagnostics.append(diagnose(state, (step+1)*dt))
        return {'points': n, 'steps': nsteps, 'initial_conformal_factor': solved.x[:n].tolist(),
                'initial_expansion': float(solved.x[-1]), 'initial_constraint_residual': float(initial_residual),
                'initial_state': initial_state(solved.x).tolist(), 'final_state': state.tolist(),
                'diagnostics': diagnostics}

    principal = realization(points, steps)
    comparisons = {}
    if refine:
        temporal = realization(points, 2*steps)
        spatial = realization(2*points-1, 2*steps)
        coarse = np.asarray(principal['final_state'])
        fine_time = np.asarray(temporal['final_state'])
        fine_space = np.asarray(spatial['final_state'])
        # Compare common Fourier coefficients, not unrelated collocation nodes.
        k = (points-1)//2
        modes_coarse = np.fft.fft(fine_time, axis=1)/points
        modes_fine = np.fft.fft(fine_space, axis=1)/(2*points-1)
        work['spatial_transforms'] += fine_time.shape[0]+fine_space.shape[0]
        selected = np.r_[np.arange(k+1), np.arange(-k, 0)]
        comparisons = {'time_step_halving_maximum_state_difference': float(np.max(np.abs(coarse-fine_time))),
            'spatial_refinement_retained_mode_difference': float(np.max(np.abs(modes_coarse[:, selected]-modes_fine[:, selected]))),
            'time_refinement': temporal, 'spatial_refinement': spatial}
    rows = principal['diagnostics']
    if refine:
        rows = rows+comparisons['time_refinement']['diagnostics']+comparisons['spatial_refinement']['diagnostics']
    checks = {'constraint_compatible_initial_data': principal['initial_constraint_residual'] < 2e-10,
              'einstein_hamiltonian': max(r['hamiltonian_residual'] for r in rows) < 2e-8,
              'einstein_momentum': max(r['momentum_residual'] for r in rows) < 2e-8,
              'algebraic_source': max(r['source_residual'] for r in rows) < 2e-11,
              'positive_principal_forms': min(r['minimum_spatial_eigenvalue'] for r in rows) > 0
                    and min(r['minimum_kinetic_eigenvalue'] for r in rows) > 0,
              'real_characteristics': max(r['maximum_characteristic_imaginary_part'] for r in rows) < 2e-10,
              'timelike_future_phase': min(r['minimum_phase_norm'] for r in rows) > 0
                    and min(r['minimum_phase_rate'] for r in rows) > 0,
              'global_phase_charge': max(abs(r['charge']/rows[0]['charge']-1) for r in rows) < 2e-9}
    if refine:
        checks['time_refinement'] = comparisons['time_step_halving_maximum_state_difference'] < 2e-8
        checks['spatial_refinement'] = comparisons['spatial_refinement_retained_mode_difference'] < 2e-8
    return {'scope': 'finite-amplitude planar Einstein--scalar--auxiliary-radius evolution',
            'action': background['action'], 'inputs': {'amplitude': amplitude, 'period': 2*math.pi,
                'points': points, 'steps': steps, 'duration': duration, 'background_inputs': cfg},
            'initial_data_construction': 'CMC conformally flat Hamiltonian solve with zero momentum source and mean conformal factor one',
            'source_equation': 'U_eta+3(T-G)-V=0',
            'canonical_curvature': 'U_etaeta+9T+9G+V',
            'physical_curvature': 'U_etaeta-9T+9G+V',
            'local_metric_limit': 'Einstein Poisson response with the same positive Planck normalization',
            'verification_scope': 'floating-point constrained initial solve, planar ADM trajectory, sampled principal margins and resolution comparisons',
            'principal_run': principal, 'refinement': comparisons, 'operation_counts': work,
            'checks': checks, 'passed': bool(all(checks.values()))}


def evaluate_expanding_rms_window(*, omega_m, omega_vacuum, acceleration_ratio,
                                  initial_displacement=1e-3, wavenumber=100.,
                                  duration=.05, samples=17, quadrature_order=64):
    """Vary expansion, lapse, cold displacement and RMS potential together.

    The periodic displacement X=q+D sin(kq)/k is inserted in the existing
    nonrelativistic RMS source action. Its complete periodic potential is
    eliminated by the exact one-dimensional flux law. The homogeneous
    Einstein lapse action supplies the expansion constraint.
    Units are H0^-1 and c/H0, with densities divided by M_P^2 H0^2.
    The displacement window is finite: the omitted cold-flow acceleration
    is computed separately from the exactly solved spatial field equation.
    """
    from scipy.integrate import solve_ivp
    from cg_frg.gravity.local_response import primitive
    values = (omega_m, omega_vacuum, acceleration_ratio, initial_displacement,
              wavenumber, duration)
    if (not all(math.isfinite(v) for v in values) or min(values) <= 0
            or abs(omega_m+omega_vacuum-1) > 1e-8 or initial_displacement >= .1
            or isinstance(samples, bool) or not isinstance(samples, int) or samples < 3
            or isinstance(quadrature_order, bool) or not isinstance(quadrature_order, int)
            or quadrature_order < 16):
        raise ValueError('flat positive generated background, positive acceleration and small nonzero displacement required')
    mass, vacuum, k, a0 = 3*omega_m, 3*omega_vacuum, wavenumber, acceleration_ratio
    work = {'exact_field_reconstructions': 0, 'potential_quadratures': 0,
            'quadrature_node_evaluations': 0, 'rhs_evaluations': 0,
            'diagnostic_phase_points': 0}

    def realization(order, rtol, atol):
        nodes, weights = np.polynomial.legendre.leggauss(order)
        u = (nodes+1)/2
        angle, weights = math.pi*u*u/2, weights*u
        sine = np.sin(angle)
        def potential(a, D):
            if a <= 0 or not 0 < D < .9:
                raise ArithmeticError('expanding RMS trajectory left the noncrossing positive source branch')
            work['exact_field_reconstructions'] += 1
            work['potential_quadratures'] += 1
            work['quadrature_node_evaluations'] += order
            flux = mass*D*sine/(2*a*a*k)
            gradient = np.sqrt((flux*flux+flux*np.hypot(flux, 2*a0))/2)
            F = primitive(np.c_[gradient, np.zeros((order, 2))], a0=a0)
            U = 2*a**3*float(weights@F)
            W = 2*a**3*float(weights@(F-gradient*flux))
            Wa = 2*a*a*float(weights@(3*F-gradient*flux))
            mean_force_sine = -float(weights@(gradient*sine))
            WD = mass*a*mean_force_sine/k
            R = vacuum*a**3+mass+W
            if R <= 0:
                raise ArithmeticError('RMS reduced physical Hamiltonian lost positivity')
            return {'U': U, 'Wa': Wa, 'WD': WD, 'W': W, 'R': R,
                    'mean_force_sine': mean_force_sine}

        data0 = potential(1., initial_displacement)
        y0 = np.array([1., initial_displacement, 0., -math.sqrt(12*data0['R'])])
        def rhs(t, y):
            work['rhs_evaluations'] += 1
            a, D, pD, pa = y
            data = potential(a, D)
            kinetic = k*k*pD*pD/(mass*a*a)
            return np.array([-pa/(6*a), 2*k*k*pD/(mass*a*a),
                -data['WD'],
                -pa*pa/(12*a*a)+2*kinetic/a-3*vacuum*a*a-data['Wa']])
        times = np.linspace(0., duration, samples)
        sol = solve_ivp(rhs, (0., duration), y0, method='DOP853',
                        rtol=rtol, atol=atol, t_eval=times)
        if not sol.success:
            raise ArithmeticError(sol.message)
        theta = 2*math.pi*(np.arange(4096)+.5)/4096
        rows = []
        for time, y in zip(times, sol.y.T):
            a, D, pD, pa = y
            data = potential(a, D)
            adot, Ddot, _, _ = rhs(time, y)
            H = adot/a
            kinetic = k*k*pD*pD/(mass*a*a)
            constraint = -pa*pa/(12*a)+kinetic+data['R']
            root_energy = kinetic+data['R']
            # Hessian of H_a=sqrt(12a)*sqrt(K+R) after choosing expanding a.
            reduced_hessian = math.sqrt(12*a)*k*k*data['R']/(mass*a*a*root_energy**1.5)
            jacobian = 1+D*np.cos(theta)
            prescribed_flux = -mass*D*np.sin(theta)/(2*a*a*k)
            abs_flux = np.abs(prescribed_flux)
            gphysical = np.sign(prescribed_flux)*np.sqrt((abs_flux**2+abs_flux*np.hypot(abs_flux, 2*a0))/2)
            abs_g = np.abs(gphysical)
            flux_residual = gphysical*abs_g/np.hypot(abs_g, a0)-prescribed_flux
            divergence = -mass*D*np.cos(theta)/(2*a*a*jacobian)
            poisson_defect = divergence-mass/(2*a*a)*(1/jacobian-1)
            acceleration_defect = (gphysical-2*data['mean_force_sine']*np.sin(theta))/a
            work['diagnostic_phase_points'] += len(theta)
            # Averages of spatial residuals use dx=(1+D cos(theta))dq.
            poisson_l2 = math.sqrt(float(np.mean(poisson_defect**2*jacobian)))
            force_l2 = math.sqrt(float(np.mean(acceleration_defect**2)))
            force_projection = float(np.mean(acceleration_defect*np.sin(theta)))
            energy_rate = -2*H*kinetic+a*H*data['Wa']
            pressure = (2*kinetic-a*data['Wa'])/(3*a**3)
            density_rate = energy_rate/a**3-3*H*(mass+kinetic+data['W'])/a**3
            rows.append({'time': float(time), 'state': y.tolist(),
                'expansion': H, 'displacement_velocity': Ddot,
                'maximum_flux_reconstruction_residual': float(np.max(np.abs(flux_residual))),
                'potential_energy_derivative_a': data['Wa'], 'potential_energy_derivative_D': data['WD'],
                'constraint_residual': constraint, 'reduced_kinetic_hessian': reduced_hessian,
                'potential_plus_rest_margin': data['R'], 'minimum_flow_jacobian': 1-D,
                'maximum_peculiar_speed': a*abs(Ddot)/k,
                'maximum_physical_acceleration': float(np.max(abs_g)),
                'potential_energy': data['W'], 'field_energy': data['U'],
                'background_energy_exchange': energy_rate,
                'background_pressure': pressure,
                'continuity_residual': density_rate+3*H*((mass+kinetic+data['W'])/a**3+pressure),
                'full_poisson_defect_L2': poisson_l2, 'full_flow_acceleration_defect_L2': force_l2,
                'retained_flow_projection_residual': force_projection})
        return {'rows': rows, 'initial_state': y0.tolist(), 'quadrature_order': order,
                'relative_tolerance': rtol, 'absolute_tolerance': atol}

    main = realization(quadrature_order, 2e-10, 2e-12)
    refined = realization(2*quadrature_order, 2e-12, 2e-14)
    state_difference = float(np.max(np.abs(np.array([r['state'] for r in main['rows']])
                                                -np.array([r['state'] for r in refined['rows']]))))
    field_difference = max(abs(a['potential_energy']-b['potential_energy'])
                           for a, b in zip(main['rows'], refined['rows']))
    rows = main['rows']+refined['rows']
    # Exact-decimal input enclosures establish a short-time exit box without
    # subdividing or reintegrating the computed trajectory. The box is a
    # numerical certificate, separate from physical parameters and initial data.
    from cg_core.rational_interval import Interval as I
    im, iv, ik, ia0, id0, it = map(I.point, (str(mass), str(vacuum),
        str(k), str(a0), str(initial_displacement), str(duration)))
    au, du, pu = I.point('1.06'), I.point('.002'), I.point('.0000008')
    pam, pau = I.point('5.9'), I.point('6.6')
    flux_upper = im*du/(2*ik)
    gradient_upper = (flux_upper**2+ia0*flux_upper).sqrt()
    binding_upper = im*au*du*gradient_upper/ik
    initial_R_lower, initial_R_upper = im+iv-binding_upper, im+iv
    initial_pa_lower = (12*initial_R_lower).sqrt()
    initial_pa_upper = (12*initial_R_upper).sqrt()
    ua_upper = 3*au**2*gradient_upper**2
    kinetic_upper = ik**2*pu**2/im
    pa_decrease_upper = pau**2/12+3*iv*au**2+ua_upper
    pa_derivative_upper = -pam**2/(12*au**2)+2*kinetic_upper-3*iv
    exit_margins = {
        'scale_factor': au-(1+it*pau/6),
        'displacement': du-(id0+it*2*ik**2*pu/im),
        'displacement_momentum': pu-it*im*au*gradient_upper/ik,
        'scale_momentum_lower': pau-(initial_pa_upper+it*pa_decrease_upper),
        'scale_momentum_upper': initial_pa_lower-pam,
        'decreasing_scale_momentum': -pa_derivative_upper,
    }
    R_lower, R_upper = im+iv-binding_upper, im+iv*au**3
    hamiltonian_hessian_lower = (I.point(12).sqrt()*ik**2*R_lower
        /(im*au**2*(kinetic_upper+R_upper)*(kinetic_upper+R_upper).sqrt()))
    flow_defect_upper = 3*gradient_upper
    certificate_passed = (id0.lo > 0 and id0.hi < du.lo and du.hi < I.point('.1').lo
        and all(value.lo > 0 for value in exit_margins.values())
        and R_lower.lo > 0 and hamiltonian_hessian_lower.lo > 0)
    certificate = {
        'scope': 'uniform existence, noncrossing and constrained kinetic positivity for the exact decimal inputs on the stated time interval',
        'method': 'outward rational exit inequalities and analytic inverse RMS flux bounds; no trajectory integration',
        'input_interpretation': 'exact decimal encodings of the supplied physical inputs; upstream input uncertainty is separate',
        'box': {'a': ['1', '1.06'], 'D': [str(initial_displacement), '.002'],
                'p_D': ['0', '.0000008'], 'p_a': ['-6.6', '-5.9']},
        'exit_margins': {name: value.decimal_bounds(20) for name, value in exit_margins.items()},
        'physical_acceleration_upper': gradient_upper.decimal_bounds(20)[1],
        'physical_hamiltonian_hessian_lower': hamiltonian_hessian_lower.decimal_bounds(16)[0],
        'potential_plus_rest_lower': R_lower.decimal_bounds(20)[0],
        'full_flow_acceleration_defect_uniform_upper': flow_defect_upper.decimal_bounds(20)[1],
        'full_poisson_defect_uniform_upper': '0',
        'passed': bool(certificate_passed),
    }
    work['rational_exit_certificate_evaluations'] = 1
    checks = {'positive_physical_hamiltonian_hessian': min(r['reduced_kinetic_hessian'] for r in rows) > 0,
        'noncrossing_flow': min(r['minimum_flow_jacobian'] for r in rows) > 0,
        'lapse_constraint': max(abs(r['constraint_residual']) for r in rows) < 2e-9,
        'exact_flux_reconstruction': max(r['maximum_flux_reconstruction_residual'] for r in rows) < 2e-16,
        'full_poisson_equation': max(r['full_poisson_defect_L2'] for r in rows) < 2e-14,
        'retained_force_projection': max(abs(r['retained_flow_projection_residual']) for r in rows) < 2e-10,
        'background_continuity': max(abs(r['continuity_residual']) for r in rows) < 2e-12,
        'numerical_refinement': state_difference < 2e-8 and field_difference < 2e-10,
        'uniform_exit_certificate': certificate_passed}
    return {'scope': 'autonomous finite displacement window of the existing nonrelativistic RMS source action and homogeneous Einstein lapse action, with the complete periodic field solved exactly',
        'inputs': {'omega_m': omega_m, 'omega_vacuum': omega_vacuum,
            'acceleration_ratio': acceleration_ratio, 'initial_displacement': initial_displacement,
            'wavenumber': wavenumber, 'duration': duration, 'samples': samples},
        'units': 'H0*t, H0*x/c, densities/(M_P^2 H0^2), acceleration/(c H0)',
        'flow': 'X(q)=q+D sin(kq)/k; J_RMS(g(X(q)))=-M D sin(kq)/(2a^2 k)',
        'constraint': '-p_a^2/(12a)+k^2 p_D^2/(M a^2)+rho_vac a^3+M+W(a,D)=0',
        'clock': 'the homogeneous lapse is varied before choosing unit proper-time lapse; a is a monotone relational chart',
        'homogeneous_limit': 'D=p_D=0 gives 3H^2=rho_vac+M/a^3',
        'local_limit': 'at fixed a the exact periodic field solves the full RMS Poisson equation for the noncrossing cold displacement',
        'production_background_updated': False, 'full_spatial_pde_solution_claimed': False,
        'main': main, 'refined': refined, 'uniform_certificate': certificate,
        'maximum_state_refinement_difference': state_difference,
        'maximum_potential_refinement_difference': field_difference,
        'operation_counts': work, 'checks': {key: bool(value) for key, value in checks.items()},
        'passed': bool(all(checks.values()))}


def _hermitian(value, name):
    value = np.asarray(value, complex)
    if value.ndim != 2 or value.shape[0] != value.shape[1] or not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be a finite square matrix")
    scale = np.linalg.norm(value, ord=2)
    if np.linalg.norm(value-value.conj().T, ord=2) > 1e-11*max(scale, np.finfo(float).tiny):
        raise ValueError(f"{name} must be Hermitian")
    return (value+value.conj().T)/2


def _field_inner(left, right):
    return sum(np.vdot(value, right[label]) for label, value in left.items() if label in right)


def covariant_scalar_operator(*, max_j, L, connection, carrier_dimension):
    """Construct the native finite quadratic form, including B*B and d-B terms.

    B is an actual skew-adjoint matrix-valued one-form in the orthonormal
    round frame.  Coupling factors belong to B and must be stated by the
    caller.  The output derivative support is never projected away.
    """
    if not math.isfinite(L) or L <= 0:
        raise ValueError("positive finite radius required")
    if (not isinstance(carrier_dimension, int) or isinstance(carrier_dimension, bool)
            or carrier_dimension < 1 or len(connection) != 3):
        raise ValueError("positive carrier dimension and three connection components required")
    for component in connection:
        for value in component.values():
            if np.asarray(value).shape != (carrier_dimension, carrier_dimension):
                raise ValueError("connection matrix dimension mismatch")
        adjoint_sum = modes.add(component, modes.adjoint(component))
        if modes.mode_norm(adjoint_sum) > 1e-11*max(modes.mode_norm(component), np.finfo(float).tiny):
            raise ValueError("connection must be pointwise skew-adjoint")
    labels = scalar_basis(max_j)
    columns = []
    for label in labels:
        for index in range(carrier_dimension):
            vector = np.zeros(carrier_dimension, complex)
            vector[index] = 1.
            columns.append(modes.matter_derivative(connection, {label: vector}, L=L))
    dimension = len(columns)
    operator = np.empty((dimension, dimension), complex)
    for i, left in enumerate(columns):
        for j in range(i, dimension):
            value = sum(_field_inner(a, b) for a, b in zip(left, columns[j]))
            operator[i, j], operator[j, i] = value, np.conjugate(value)
    lower_bound = 3/(4*L*L)
    operator += lower_bound*np.eye(dimension)
    output_labels = sorted(set(label for column in columns for component in column for label in component))
    return {"operator": operator, "labels": labels, "carrier_dimension": carrier_dimension,
            "radius": L, "lower_bound": lower_bound, "derivative_output_labels": output_labels,
            "complete_derivative_support": True}


def compression_matrices(profiles, labels, carrier_dimension):
    """Haar Gaunt matrices P eta P, scalar and identity on the unitary carrier."""
    indices = {label: i for i, label in enumerate(labels)}
    answer = []
    for profile in profiles:
        if any(np.asarray(value).ndim != 0 for value in profile.values()):
            raise ValueError("compression profiles must be scalar fields")
        defect = modes.add(profile, modes.scale(modes.adjoint(profile), -1))
        if modes.mode_norm(defect) > 1e-11*max(modes.mode_norm(profile), np.finfo(float).tiny):
            raise ValueError("compression profiles must be real")
        matrix = np.zeros((len(labels), len(labels)), complex)
        for column, label in enumerate(labels):
            for out, value in modes.multiply(profile, {label: 1.}).items():
                if out in indices:
                    matrix[indices[out], column] = value
        answer.append(np.kron(_hermitian(matrix, "compression"), np.eye(carrier_dimension)))
    if not answer:
        raise ValueError("at least one explicit source profile required")
    return tuple(answer)


def energy_response(operator, occupation, compressions, *, require_stationary=True):
    """Differentiate Tr[N sqrt(exp(eta) A exp(eta))] at eta=0.

    The full square-root Sylvester equation is used, including coherent
    off-diagonal entries.  The stationary density and Gram-Hessian claims
    require [N,H]=0; by default a nonstationary occupation is rejected.
    A nonlinear source produces a second derivative of A itself.  That
    direct term and the two first-variation feedback contributions are retained.
    """
    A, N = _hermitian(operator, "operator"), _hermitian(occupation, "occupation")
    if N.shape != A.shape:
        raise ValueError("occupation and operator dimensions disagree")
    if np.min(np.linalg.eigvalsh(N)) < -1e-12*max(np.linalg.norm(N, 2), np.finfo(float).tiny):
        raise ValueError("occupation must be nonnegative")
    eigenvalues, U = np.linalg.eigh(A)
    if np.min(eigenvalues) <= 0:
        raise ValueError("native matter operator must be strictly positive")
    mass = np.sqrt(eigenvalues)
    Nt = U.conj().T@N@U
    commutator = Nt*mass[None, :]-mass[:, None]*Nt
    stationarity_residual = np.linalg.norm(commutator)/max(
        np.linalg.norm(Nt)*mass.max(), np.finfo(float).tiny)
    stationary = stationarity_residual <= 1e-10
    if require_stationary and not stationary:
        raise ValueError("stationary source density requires [N,H]=0")
    profiles = []
    for profile in compressions:
        profile = _hermitian(profile, "compression")
        if profile.shape != A.shape:
            raise ValueError("source and operator dimensions disagree")
        profiles.append(U.conj().T@profile@U)
    if not profiles:
        raise ValueError("at least one compression source required")
    denominator = mass[:, None]+mass[None, :]
    spectral_sum = eigenvalues[:, None]+eigenvalues[None, :]
    first = [spectral_sum*p/denominator for p in profiles]
    charges = np.array([np.trace(Nt@h).real for h in first])
    direct, feedback = np.empty((len(profiles), len(profiles))), np.empty((len(profiles), len(profiles)))
    for a, p in enumerate(profiles):
        for b, q in enumerate(profiles):
            second_exp = (p@q+q@p)/2
            Aab = spectral_sum*second_exp + (p*eigenvalues[None, :])@q + (q*eigenvalues[None, :])@p
            direct[a, b] = np.trace(Nt@(Aab/denominator)).real
            feedback[a, b] = -np.trace(Nt@((first[a]@first[b]+first[b]@first[a])/denominator)).real
    hessian = (direct+feedback)
    hessian = (hessian+hessian.T)/2
    energy = float(np.dot(np.diag(Nt).real, mass))
    return {"energy": energy, "charges": charges, "hessian": hessian,
            "second_source_direct_term": direct, "square_root_feedback": feedback,
            "minimum_hessian_eigenvalue": float(np.min(np.linalg.eigvalsh(hessian))),
            "stationarity_residual": float(stationarity_residual), "stationary": bool(stationary),
            "lowest_matter_energy": float(mass.min()),
            "occupation_fixed_under_source": True,
            "stationary_energy_density_interpretation": bool(stationary),
            "external_gravitational_kernel_computed": False}


def finite_sourced_energy(operator, occupation, compressions, source):
    """Independent exact finite-family value for derivative verification."""
    A, N = _hermitian(operator, "operator"), _hermitian(occupation, "occupation")
    source = np.asarray(source, float)
    if source.shape != (len(compressions),) or not np.all(np.isfinite(source)) or N.shape != A.shape:
        raise ValueError("finite source with one amplitude per compression required")
    eta = sum((h*_hermitian(p, "compression") for h, p in zip(source, compressions)), np.zeros_like(A))
    congruence = expm(eta)
    eigenvalues, U = np.linalg.eigh(congruence@A@congruence)
    if np.min(eigenvalues) <= 0:
        raise ArithmeticError("sourced positive operator lost numerical positivity")
    return float(np.dot(np.diag(U.conj().T@N@U).real, np.sqrt(eigenvalues)))


def _canonical_reference(operator, occupation, compressions):
    """Positive canonical ensemble on the stated stationary matter source."""
    A, N = _hermitian(operator, "operator"), _hermitian(occupation, "occupation")
    if N.shape != A.shape:
        raise ValueError("occupation and operator dimensions disagree")
    if np.linalg.eigvalsh(N).min() < -1e-12*max(np.linalg.norm(N, 2), np.finfo(float).tiny):
        raise ValueError("occupation must be nonnegative")
    values, U = np.linalg.eigh(A)
    if values.min() <= 0:
        raise ValueError("native matter operator must be strictly positive")
    energies = np.sqrt(values)
    Nt = U.conj().T@N@U
    defect = Nt*energies[None, :]-energies[:, None]*Nt
    residual = np.linalg.norm(defect)/max(np.linalg.norm(Nt)*energies.max(), np.finfo(float).tiny)
    if residual > 1e-10:
        raise ValueError("canonical stationary ensemble requires [N,H]=0")
    profiles = tuple(_hermitian(p, "compression") for p in compressions)
    if not profiles or any(p.shape != A.shape for p in profiles):
        raise ValueError("at least one compression of the operator dimension required")
    root, inverse_root = np.sqrt(energies), 1/np.sqrt(energies)
    position, momentum = U*inverse_root, U*root
    # x=(q,p)=T c, with unperturbed frequencies (+E,-E) for c.
    T = np.block([[position, position], [-1j*momentum, 1j*momentum]])/np.sqrt(2)
    zeros = np.zeros_like(Nt)
    normal_covariance = np.block([[Nt, zeros], [zeros, Nt]])
    covariance = T@normal_covariance@T.conj().T
    covariance = (covariance+covariance.conj().T)/2
    return {"operator": A, "occupation": N, "profiles": profiles,
            "energies": energies, "eigenvectors": U, "normal_occupation": Nt,
            "normal_to_phase": T, "normal_covariance": normal_covariance,
            "covariance": covariance, "stationarity_residual": float(residual)}


def canonical_source_matrices(operator, compressions, source):
    """Finite conformal field action and its canonical oscillator matrix.

    For the spatial metric exp(-2 eta) g in three internal dimensions,
    the field kinetic measure is M=exp(-3 eta).  Conformal transport gives
    B=exp(-eta/2) A exp(-eta/2); hence M^(-1/2) B M^(-1/2)=exp(eta) A exp(eta).
    The finite matrix compression is the same family as the static source.
    Complex Hermitian matrices may be read as their real canonical form.
    """
    A = _hermitian(operator, "operator")
    if np.linalg.eigvalsh(A).min() <= 0:
        raise ValueError("native matter operator must be strictly positive")
    profiles = tuple(_hermitian(p, "compression") for p in compressions)
    amplitudes = np.asarray(source, float)
    if (not profiles or amplitudes.shape != (len(profiles),)
            or not np.all(np.isfinite(amplitudes))
            or any(p.shape != A.shape for p in profiles)):
        raise ValueError("finite source with one amplitude per compression required")
    return _canonical_matrices(A, profiles, amplitudes)


def _canonical_matrices(A, profiles, amplitudes, reference_spectrum=None):
    """Assemble one source family after validating its common input matrices."""
    eta = sum((h*p for h, p in zip(amplitudes, profiles)), np.zeros_like(A))
    zero_source = not np.any(amplitudes)
    weights, basis = ((np.zeros(len(A)), np.eye(len(A))) if zero_source
                      else np.linalg.eigh(eta))
    def exponential(factor):
        result = (basis*np.exp(factor*weights))@basis.conj().T
        if not np.all(np.isfinite(result)):
            raise ArithmeticError("finite conformal source overflow")
        return (result+result.conj().T)/2
    mass_half, inverse_mass_half = exponential(-3/2), exponential(3/2)
    half_transport, transport = exponential(-1/2), exponential(1)
    mass, inverse_mass = mass_half@mass_half, inverse_mass_half@inverse_mass_half
    stiffness = half_transport@A@half_transport
    stiffness = (stiffness+stiffness.conj().T)/2
    normal = transport@A@transport
    normal = (normal+normal.conj().T)/2
    if zero_source and reference_spectrum is not None:
        frequencies, modes_u = reference_spectrum
        values = frequencies**2
    else:
        values, modes_u = np.linalg.eigh(normal)
    if values.min() <= 0:
        raise ArithmeticError("sourced positive operator lost numerical positivity")
    zero = np.zeros_like(A)
    phase_hessian = np.block([[stiffness, zero], [zero, inverse_mass]])
    phase_generator = np.block([[zero, inverse_mass], [-stiffness, zero]])
    return {"mass_matrix": mass, "mass_half": mass_half,
            "inverse_mass_half": inverse_mass_half, "stiffness": stiffness,
            "normal_operator": normal, "normal_frequencies": np.sqrt(values),
            "normal_eigenvectors": modes_u, "phase_hessian": phase_hessian,
            "phase_generator": phase_generator}


def canonical_source_response(operator, occupation, compressions, *, spectral_parameters,
                              include_phase_covariances=False):
    """Causal response of canonical source forces, with every frequency block.

    The source convention is eta_b(t) proportional to exp(-i z t), Im z>0.
    For H_can=x^* K x/2 and W=<x x^*>, the response is
    Tr(K_ab W)/2 + Tr(K_a delta W_b)/2.  In oscillator coordinates,
    delta W_rs=i F_rs/(z-omega_r+omega_s), omega=(E,-E).
    Difference and summed frequencies, including exactly degenerate
    coherences, are retained without division by an energy gap.
    The imaginary argument evaluates the causal analytic function; it is
    not a material damping coefficient.  W is an occupied classical
    ensemble, without a quantum vacuum or zero-point subtraction claim.
    """
    data = _canonical_reference(operator, occupation, compressions)
    return _canonical_response(data, spectral_parameters, include_phase_covariances)


def _canonical_response(data, spectral_parameters, include_phase_covariances=False):
    """Reuse the common reference diagonalisation for all response arguments."""
    parameters = np.asarray(spectral_parameters, complex)
    if (parameters.ndim != 1 or not len(parameters) or not np.all(np.isfinite(parameters))
            or np.any(parameters.imag <= 0)):
        raise ValueError("spectral parameters must be finite with positive imaginary part")
    A, profiles = data["operator"], data["profiles"]
    T, Wn, W = data["normal_to_phase"], data["normal_covariance"], data["covariance"]
    count, dimension = len(profiles), len(A)
    zero = np.zeros_like(A)
    first = [np.block([[-(p@A+A@p)/2, zero], [zero, 3*p]]) for p in profiles]
    first_normal = [T.conj().T@k@T for k in first]
    symplectic_normal = np.diag(np.r_[-1j*np.ones(dimension), 1j*np.ones(dimension)])
    forces = []
    for k in first_normal:
        x = symplectic_normal@k
        forces.append(x@Wn+Wn@x.conj().T)
    contact = np.empty((count, count), float)
    for a, p in enumerate(profiles):
        for b, q in enumerate(profiles):
            pq = p@q+q@p
            B_ab = (pq@A+A@pq)/8+(p@A@q+q@A@p)/4
            K_ab = np.block([[B_ab, zero], [zero, (9/2)*pq]])
            contact[a, b] = float(np.einsum("ij,ji->", K_ab, W).real/2)
    frequencies = np.r_[data["energies"], -data["energies"]]
    differences = frequencies[:, None]-frequencies[None, :]
    signs = np.r_[np.ones(dimension, int), -np.ones(dimension, int)]
    same_sign = signs[:, None] == signs[None, :]
    response = np.empty((len(parameters), count, count), complex)
    difference_response, summed_response = np.empty_like(response), np.empty_like(response)
    phase_responses = (np.empty((len(parameters), count, 2*dimension, 2*dimension), complex)
                       if include_phase_covariances else None)
    max_equation_residual = 0.
    for j, z in enumerate(parameters):
        for b, force in enumerate(forces):
            delta = 1j*force/(z-differences)
            equation_residual = (-1j*z+1j*differences)*delta-force
            max_equation_residual = max(max_equation_residual, float(
                np.linalg.norm(equation_residual)/max(np.linalg.norm(force), np.finfo(float).tiny)))
            if include_phase_covariances:
                phase_responses[j, b] = T@delta@T.conj().T
            for a, k in enumerate(first_normal):
                difference_response[j, a, b] = np.einsum("ij,ji->", k, delta*same_sign)/2
                summed_response[j, a, b] = np.einsum("ij,ji->", k, delta*~same_sign)/2
                response[j, a, b] = contact[a, b]+difference_response[j, a, b]+summed_response[j, a, b]
    return {"charges": np.array([np.einsum("ij,ji->", k, W).real/2 for k in first]),
            "contact": contact, "spectral_parameters": parameters, "response": response,
            "difference_frequency_response": difference_response,
            "summed_frequency_response": summed_response,
            "response_phase_covariances": phase_responses,
            "initial_covariance": W, "maximum_response_equation_residual": max_equation_residual,
            "stationarity_residual": data["stationarity_residual"],
            "scope": "finite canonical conformal matter field; occupied classical ensemble",
            "external_gravitational_kernel_computed": False}


def canonical_source_evolution(operator, occupation, compressions, source_values, durations,
                               *, clock_rates=None):
    """Exact canonical flow for a finite piecewise-constant source protocol.

    Each row of source_values is switched on at the start of its positive
    duration; the source before the first row is zero.  Quench work is
    Tr[(K_new-K_old) W]/2.  The intervening oscillator propagators conserve
    their Hamiltonian exactly.  All phase covariances are evolved, so
    degenerate coherence and positive/negative-frequency mixing persist.
    This finite protocol has no temporal discretisation approximation.
    With positive segment clock_rates=d(proper time)/d(parameter), durations
    are parameter intervals. Only their products enter the phase flow.
    These rates describe the chosen clock parametrization; they introduce
    no additional field or equation of motion.
    """
    data = _canonical_reference(operator, occupation, compressions)
    return _canonical_evolution(data, source_values, durations, clock_rates=clock_rates)


def _canonical_evolution(data, source_values, durations, *, clock_rates=None, family_cache=None):
    """Reuse normal modes and, optionally, source families for the same data."""
    sources, intervals = np.asarray(source_values, float), np.asarray(durations, float)
    if (sources.ndim != 2 or sources.shape[1] != len(data["profiles"])
            or intervals.shape != (len(sources),) or not len(intervals)
            or not np.all(np.isfinite(sources)) or not np.all(np.isfinite(intervals))
            or np.any(intervals <= 0)):
        raise ValueError("one finite source and positive duration per protocol segment required")
    rates = np.ones_like(intervals) if clock_rates is None else np.asarray(clock_rates, float)
    if rates.shape != intervals.shape or not np.all(np.isfinite(rates)) or np.any(rates <= 0):
        raise ValueError("one positive finite clock rate per protocol segment required")
    physical_intervals = rates*intervals
    if not np.all(np.isfinite(physical_intervals)) or np.any(physical_intervals <= 0):
        raise ValueError("clock rates and parameter durations must give finite positive proper durations")
    cache = {} if family_cache is None else family_cache
    family_evaluations, cache_hits = 0, 0
    A, W = data["operator"], data["covariance"].copy()
    identity, zero = np.eye(len(A)), np.zeros_like(A)
    J = np.block([[zero, identity], [-identity, zero]])
    previous = np.block([[A, zero], [zero, identity]])
    covariances, propagators = [W.copy()], []
    energies, work = [float(np.einsum("ij,ji->", previous, W).real/2)], []
    max_canonical, max_hold = 0., 0.
    for source, duration in zip(sources, physical_intervals):
        key = tuple(source)
        if key not in cache:
            cache[key] = _canonical_matrices(A, data["profiles"], source,
                                            (data["energies"], data["eigenvectors"]))
            family_evaluations += 1
        else:
            cache_hits += 1
        family = cache[key]
        K = family["phase_hessian"]
        work.append(float(np.einsum("ij,ji->", K-previous, W).real/2))
        before = float(np.einsum("ij,ji->", K, W).real/2)
        frequencies, U = family["normal_frequencies"], family["normal_eigenvectors"]
        cosine = (U*np.cos(frequencies*duration))@U.conj().T
        sine_over = (U*(np.sin(frequencies*duration)/frequencies))@U.conj().T
        sine_times = (U*(np.sin(frequencies*duration)*frequencies))@U.conj().T
        half, inverse_half = family["mass_half"], family["inverse_mass_half"]
        S = np.block([[inverse_half@cosine@half, inverse_half@sine_over@inverse_half],
                      [-half@sine_times@half, half@cosine@inverse_half]])
        max_canonical = max(max_canonical, float(np.linalg.norm(S.conj().T@J@S-J)/np.linalg.norm(J)))
        W = S@W@S.conj().T
        W = (W+W.conj().T)/2
        after = float(np.einsum("ij,ji->", K, W).real/2)
        max_hold = max(max_hold, abs(after-before)/max(abs(before), np.finfo(float).tiny))
        covariances.append(W.copy())
        propagators.append(S)
        energies.append(after)
        previous = K
    energies, work = np.asarray(energies), np.asarray(work)
    balance = energies-energies[0]-np.r_[0., np.cumsum(work)]
    return {"initial_covariance": data["covariance"], "phase_covariances": np.asarray(covariances),
            "phase_propagators": np.asarray(propagators), "energies": energies,
            "source_work": work, "energy_balance_residual": balance,
            "max_canonical_form_residual": max_canonical,
            "max_constant_source_energy_residual": max_hold,
            "stationarity_residual": data["stationarity_residual"],
            "parameter_durations": intervals.copy(), "clock_rates": rates.copy(),
            "proper_durations": physical_intervals,
            "clock_convention": "positive d(proper time)/d(parameter), fixed by the selected clock relation",
            "evaluation_work": {"source_family_evaluations": family_evaluations,
                                "source_family_cache_hits": cache_hits,
                                "exact_segment_propagators": len(intervals)},
            "scope": "finite canonical conformal matter field; piecewise-constant source",
            "external_gravitational_kernel_computed": False}


def _conformal_source_differential(operator, compressions, source):
    """Common conformal matrices and full noncommuting first derivatives.

    Hermitian divided differences evaluate the exponential Frechet maps.
    One source diagonalisation supplies both matrix functions and every
    derivative; no finite differences or commuting-source approximation
    enter the stress tensor or source exchange.
    """
    A = _hermitian(operator, "operator")
    if np.linalg.eigvalsh(A).min() <= 0:
        raise ValueError("native matter operator must be strictly positive")
    profiles = tuple(_hermitian(p, "compression") for p in compressions)
    amplitudes = np.asarray(source, float)
    if (not profiles or amplitudes.shape != (len(profiles),)
            or not np.all(np.isfinite(amplitudes))
            or any(p.shape != A.shape for p in profiles)):
        raise ValueError("finite source with one amplitude per compression required")
    eta = sum((h*p for h, p in zip(amplitudes, profiles)), np.zeros_like(A))
    values, U = np.linalg.eigh(eta)
    transformed = [U.conj().T@p@U for p in profiles]
    middle = (values[:, None]+values[None, :])/2
    difference = (values[:, None]-values[None, :])/2
    def exponential_and_derivatives(coefficient):
        diagonal = np.exp(coefficient*values)
        value = (U*diagonal)@U.conj().T
        argument = coefficient*difference
        sinhc = np.ones_like(argument)
        np.divide(np.sinh(argument), argument, out=sinhc, where=argument != 0)
        divided = coefficient*np.exp(coefficient*middle)*sinhc
        derivatives = np.array([U@(divided*p)@U.conj().T for p in transformed])
        if not np.all(np.isfinite(value)) or not np.all(np.isfinite(derivatives)):
            raise ArithmeticError("finite conformal source overflow")
        return (value+value.conj().T)/2, (derivatives+derivatives.conj().swapaxes(1, 2))/2
    mass, mass_derivatives = exponential_and_derivatives(-3)
    half, half_derivatives = exponential_and_derivatives(-1/2)
    inverse_mass = (U*np.exp(3*values))@U.conj().T
    if not np.all(np.isfinite(inverse_mass)):
        raise ArithmeticError("finite conformal source overflow")
    stiffness = half@A@half
    stiffness_derivatives = np.array([d@A@half+half@A@d for d in half_derivatives])
    return {"mass_matrix": mass, "inverse_mass_matrix": inverse_mass,
            "stiffness": (stiffness+stiffness.conj().T)/2,
            "source_mass_derivatives": mass_derivatives,
            "source_stiffness_derivatives": stiffness_derivatives}


def covariant_source_jet(operator, compressions, source, *, metric, metric_gradient,
                         field, field_gradient, field_hessian, source_gradient):
    """Hilbert stress and off-shell source exchange on a finite matter carrier.

    The four-dimensional signature is (-+++).  The retained action is
    -sqrt(-g) [g^mu nu partial_mu phi^* M partial_nu phi+phi^* B phi]/2.
    The finite complex carrier is understood in real coordinates.  Jets
    are coordinate partial derivatives, with the derivative index first.
    Stress divergence is differentiated directly, including metric jets
    and Christoffel terms; it is independent of the Noether right side.
    Compression amplitudes are scalar sources, with no source action or
    independent source inertia supplied by this evaluator.
    """
    matrices = _conformal_source_differential(operator, compressions, source)
    return _covariant_source_jet(matrices, metric, metric_gradient, field,
                                 field_gradient, field_hessian, source_gradient)


def _covariant_source_jet(matrices, metric, metric_gradient, field,
                          field_gradient, field_hessian, source_gradient):
    g, dg = np.asarray(metric, float), np.asarray(metric_gradient, float)
    phi, first, second = (np.asarray(value, complex) for value in
                          (field, field_gradient, field_hessian))
    deta = np.asarray(source_gradient, float)
    M, B = matrices["mass_matrix"], matrices["stiffness"]
    Ma, Ba = matrices["source_mass_derivatives"], matrices["source_stiffness_derivatives"]
    dimension, source_count = len(M), len(Ma)
    if (g.shape != (4, 4) or dg.shape != (4, 4, 4) or phi.shape != (dimension,)
            or first.shape != (4, dimension) or second.shape != (4, 4, dimension)
            or deta.shape != (4, source_count)
            or not all(np.all(np.isfinite(v)) for v in (g, dg, phi, first, second, deta))):
        raise ValueError("finite four-dimensional metric, field and source jets required")
    if (not np.allclose(g, g.T, rtol=1e-12, atol=1e-14)
            or not np.allclose(dg, dg.swapaxes(1, 2), rtol=1e-12, atol=1e-14)
            or not np.allclose(second, second.swapaxes(0, 1), rtol=1e-12, atol=1e-14)):
        raise ValueError("symmetric metric jets and field Hessian required")
    signature = np.linalg.eigvalsh(g)
    if np.count_nonzero(signature < 0) != 1 or np.count_nonzero(signature > 0) != 3:
        raise ValueError("metric signature must be (-+++)")
    inverse = np.linalg.inv(g)
    dinverse = np.array([-inverse@derivative@inverse for derivative in dg])
    christoffel = np.empty((4, 4, 4))
    for a in range(4):
        for b in range(4):
            for c in range(4):
                christoffel[a, b, c] = sum(inverse[a, d]*(dg[b, d, c]+dg[c, d, b]-dg[d, b, c])
                                            for d in range(4))/2
    dM, dB = np.einsum("ra,aij->rij", deta, Ma), np.einsum("ra,aij->rij", deta, Ba)
    gradient_form = np.real(first.conj()@M@first.T)
    kinetic = float(np.einsum("ij,ij->", inverse, gradient_form))
    potential = float(np.vdot(phi, B@phi).real)
    stress = gradient_form-g*(kinetic+potential)/2
    stress_derivative = np.empty((4, 4, 4))
    for r in range(4):
        differentiated_form = np.real(second[r].conj()@M@first.T
                                       + first.conj()@dM[r]@first.T
                                       + first.conj()@M@second[r].T)
        differentiated_kinetic = float(np.einsum("ij,ij->", dinverse[r], gradient_form)
                                        + np.einsum("ij,ij->", inverse, differentiated_form))
        differentiated_potential = float(2*np.vdot(first[r], B@phi).real
                                           + np.vdot(phi, dB[r]@phi).real)
        stress_derivative[r] = (differentiated_form-dg[r]*(kinetic+potential)/2
                                - g*(differentiated_kinetic+differentiated_potential)/2)
    divergence = np.zeros(4)
    for nu in range(4):
        for mu in range(4):
            for r in range(4):
                connection_terms = sum(christoffel[s, r, mu]*stress[s, nu]
                                       + christoffel[s, r, nu]*stress[mu, s] for s in range(4))
                divergence[nu] += inverse[mu, r]*(stress_derivative[r, mu, nu]-connection_terms)
    equation = -B@phi
    for mu in range(4):
        for nu in range(4):
            covariant_second = second[mu, nu]-sum(christoffel[r, mu, nu]*first[r] for r in range(4))
            equation += inverse[mu, nu]*(M@covariant_second+dM[mu]@first[nu])
    source_equations = np.array([-(np.einsum("ij,ij->", inverse,
                                             np.real(first.conj()@ma@first.T))
                                    + np.vdot(phi, ba@phi).real)/2
                                 for ma, ba in zip(Ma, Ba)])
    matter_term = np.real(first.conj()@equation)
    source_term = deta@source_equations
    residual = divergence-matter_term-source_term
    return {**matrices, "stress_tensor": stress, "stress_partial_derivative": stress_derivative,
            "field_equation": equation, "source_equations": source_equations,
            "stress_divergence": divergence, "ward_matter_term": matter_term,
            "ward_source_term": source_term, "ward_residual": residual,
            "christoffel_symbols": christoffel,
            "independent_source_action_supplied": False,
            "scope": "finite covariant conformal matter with spacetime-dependent scalar sources"}


def polar_source_congruence(*, reference_mass_squared, source, source_gradient,
                            metric, metric_gradient, amplitude, amplitude_gradient,
                            amplitude_hessian, phase_gradient, phase_hessian,
                            quantum_pressure_gradient):
    """Exact polar jets of one complex native mode (two real coordinates).

    The internal compression is uniform on the carrier, with M=exp(-3 eta)
    and m^2=m0^2 exp(2 eta). Coordinate jets have their derivative index
    first. The supplied pressure gradient is additional third-order jet
    data; its compatibility with the differentiated radial equation is
    returned explicitly. No phase or radial equation is imposed silently.
    """
    g, dg = np.asarray(metric, float), np.asarray(metric_gradient, float)
    dr, ddr = np.asarray(amplitude_gradient, float), np.asarray(amplitude_hessian, float)
    dt, ddt = np.asarray(phase_gradient, float), np.asarray(phase_hessian, float)
    deta, dpressure = np.asarray(source_gradient, float), np.asarray(quantum_pressure_gradient, float)
    if (not all(math.isfinite(v) for v in (reference_mass_squared, source, amplitude))
            or min(reference_mass_squared, amplitude) <= 0
            or g.shape != (4, 4) or dg.shape != (4, 4, 4)
            or ddr.shape != (4, 4) or ddt.shape != (4, 4)
            or any(v.shape != (4,) for v in (dr, dt, deta, dpressure))
            or not all(np.all(np.isfinite(v)) for v in (g, dg, dr, ddr, dt, ddt, deta, dpressure))):
        raise ValueError("positive amplitude/mass and finite four-dimensional polar jets required")
    if (not np.allclose(g, g.T) or not np.allclose(dg, dg.swapaxes(1, 2))
            or not np.allclose(ddr, ddr.T) or not np.allclose(ddt, ddt.T)):
        raise ValueError("symmetric metric and Hessian jets required")
    signs = np.linalg.eigvalsh(g)
    if np.count_nonzero(signs < 0) != 1 or np.count_nonzero(signs > 0) != 3:
        raise ValueError("metric signature must be (-+++)")
    inverse = np.linalg.inv(g)
    dinverse = np.array([-inverse@v@inverse for v in dg])
    christoffel = np.empty((4, 4, 4))
    for a in range(4):
        for b in range(4):
            for c in range(4):
                christoffel[a, b, c] = sum(inverse[a, d]*(dg[b, d, c]+dg[c, d, b]-dg[d, b, c])
                                            for d in range(4))/2
    X = float(-dt@inverse@dt)
    if X <= 0:
        raise ValueError("phase gradient must be timelike")
    mass_weight, mass_squared = math.exp(-3*source), reference_mass_squared*math.exp(2*source)
    if not all(math.isfinite(v) and v > 0 for v in (mass_weight, mass_squared)):
        raise ArithmeticError("finite positive conformal weights required")
    contracted_connection = np.einsum("ab,cab->c", inverse, christoffel)
    pressure = float((np.einsum("ab,ab->", inverse, ddr)-contracted_connection@dr
                      -3*deta@inverse@dr)/amplitude)
    dX = -np.einsum("i,aij,j->a", dt, dinverse, dt)-2*ddt@inverse@dt
    root = math.sqrt(X)
    normal_covariant = -dt/root
    normal = inverse@normal_covariant
    normal_derivative = -ddt/root+np.outer(dX, dt)/(2*X*root)
    acceleration = np.einsum("a,ab->b", normal,
                              normal_derivative-np.einsum("cab,c->ab", christoffel, normal_covariant))
    projector = np.eye(4)+np.outer(normal_covariant, normal)
    phase_rate = float(normal@dt)
    clock_covector = dt/root
    clock_derivative = ddt/root-np.outer(dX, dt)/(2*X*root)
    clock_exterior = clock_derivative-clock_derivative.T
    clock_acceleration_form = (np.outer(acceleration, clock_covector)
                               -np.outer(clock_covector, acceleration))
    density = mass_weight*amplitude**2*X
    amplitude_norm = float(dr@inverse@dr)
    gradient_form = mass_weight*(np.outer(dr, dr)+amplitude**2*np.outer(dt, dt))
    stress = gradient_form-g*mass_weight*(amplitude_norm+amplitude**2*(mass_squared-X))/2
    pressure_stress = mass_weight*np.outer(dr, dr)-g*mass_weight*(amplitude_norm+amplitude**2*pressure)/2
    source_equation = mass_weight*(3*amplitude_norm+amplitude**2*(mass_squared-3*X))/2
    radial_residual = pressure+X-mass_squared
    radial_gradient_residual = dpressure+dX-2*mass_squared*deta
    current_factor = mass_weight*amplitude**2*root
    current = current_factor*normal
    factor_gradient = current_factor*(-3*deta+2*dr/amplitude+dX/(2*X))
    normal_raised_derivative = np.einsum("aij,j->ai", dinverse, normal_covariant)+normal_derivative@inverse.T
    current_derivative = np.outer(factor_gradient, normal)+current_factor*normal_raised_derivative
    current_divergence = float(np.trace(current_derivative)+np.einsum("aac,c->", christoffel, current))
    epsilon = pressure/mass_squared
    # This expression is meaningful only on the timelike radial branch.
    pressure_acceleration = None
    if epsilon < 1:
        epsilon_gradient = (dpressure-2*pressure*deta)/mass_squared
        pressure_acceleration = -projector@deta+projector@epsilon_gradient/(2*(1-epsilon))
    return {
        "scope": "one native complex scalar mode, equivalently two real coordinates; local polar jets",
        "mass_weight": mass_weight, "mass_squared": mass_squared, "phase_norm_squared": X,
        "quantum_pressure": pressure, "relative_quantum_pressure": epsilon,
        "radial_equation_residual": radial_residual,
        "radial_gradient_residual": radial_gradient_residual,
        "normal_covariant": normal_covariant, "normal_contravariant": normal,
        "normalization_residual": float(normal_covariant@normal+1),
        "clock": {
            "phase_rate_per_proper_time": phase_rate,
            "proper_time_per_phase": 1/root,
            "phase_rate_identity_residual": phase_rate-root,
            "proper_time_covector": clock_covector,
            "proper_time_rate_residual": float(clock_covector@normal-1),
            "clock_covector_exterior_derivative": clock_exterior,
            "transverse_phase_norm_gradient": projector@dX,
            "clock_acceleration_identity_residual": clock_exterior-clock_acceleration_form,
            "unit_gradient_clock_condition": "the clock covector is closed throughout a simply connected neighborhood",
            "scope": "proper time along the normalized phase congruence in the supplied spacetime metric",
        },
        "acceleration_covariant": acceleration,
        "acceleration_kinematic_residual": acceleration+projector@dX/(2*X),
        "pressure_acceleration_covariant": pressure_acceleration,
        "pressure_acceleration_residual": (None if pressure_acceleration is None
                                           else acceleration-pressure_acceleration),
        "number_current": current, "number_current_divergence": current_divergence,
        "density": density, "stress_tensor": stress, "pressure_stress": pressure_stress,
        "stress_decomposition_residual": stress-density*np.outer(normal_covariant, normal_covariant)-pressure_stress,
        "source_equation": source_equation,
        "source_decomposition_residual": source_equation+density-mass_weight*(3*amplitude_norm+amplitude**2*pressure)/2,
        "independent_foliation_field": False,
    }


def canonical_source_adm(operator, compressions, source, *, spatial_metric, lapse, shift,
                          field, field_gradient, momentum):
    """Matter lapse and shift sources from the same conformal matrices.

    Momentum is the density pi=sqrt(h) M (dot_phi-beta^i partial_i phi)/N.
    The source force is F_a=-Q_a per proper spatial volume; its coordinate
    Hamiltonian derivative at fixed pi is N sqrt(h) F_a.  The generated
    source sector must supply its own stress and equations in a common
    gravitational constraint system.
    """
    matrices = _conformal_source_differential(operator, compressions, source)
    return _canonical_source_adm(matrices, spatial_metric, lapse, shift,
                                  field, field_gradient, momentum)


def _canonical_source_adm(matrices, spatial_metric, lapse, shift, field, field_gradient, momentum):
    h, beta = np.asarray(spatial_metric, float), np.asarray(shift, float)
    phi, gradients, pi = (np.asarray(value, complex) for value in (field, field_gradient, momentum))
    M, B, inverse_mass = matrices["mass_matrix"], matrices["stiffness"], matrices["inverse_mass_matrix"]
    dimension = len(M)
    if (h.shape != (3, 3) or beta.shape != (3,) or phi.shape != (dimension,)
            or gradients.shape != (3, dimension) or pi.shape != (dimension,)
            or not math.isfinite(lapse) or lapse <= 0
            or not all(np.all(np.isfinite(v)) for v in (h, beta, phi, gradients, pi))):
        raise ValueError("finite ADM data and positive lapse required")
    if not np.allclose(h, h.T, rtol=1e-12, atol=1e-14) or np.linalg.eigvalsh(h).min() <= 0:
        raise ValueError("positive symmetric spatial metric required")
    inverse, volume = np.linalg.inv(h), float(np.sqrt(np.linalg.det(h)))
    normal_velocity = inverse_mass@pi/volume
    field_velocity = lapse*normal_velocity+beta@gradients
    kinetic = float(np.vdot(normal_velocity, M@normal_velocity).real)
    spatial = float(np.einsum("ij,ij->", inverse, np.real(gradients.conj()@M@gradients.T)))
    potential = float(np.vdot(phi, B@phi).real)
    normal_energy = (kinetic+spatial+potential)/2
    normal_hamiltonian = volume*normal_energy
    momentum_density = np.real(gradients.conj()@pi)
    hamiltonian = lapse*normal_hamiltonian+float(beta@momentum_density)
    lagrangian = lapse*volume*(kinetic-spatial-potential)/2
    forces = []
    for ma, ba in zip(matrices["source_mass_derivatives"], matrices["source_stiffness_derivatives"]):
        forces.append(float((-np.vdot(normal_velocity, ma@normal_velocity).real
                              + np.einsum("ij,ij->", inverse, np.real(gradients.conj()@ma@gradients.T))
                              + np.vdot(phi, ba@phi).real)/2))
    forces = np.asarray(forces)
    return {**matrices, "normal_velocity": normal_velocity, "field_velocity": field_velocity,
            "normal_energy": normal_energy, "normal_hamiltonian_density": normal_hamiltonian,
            "momentum_density": momentum_density, "hamiltonian_density": hamiltonian,
            "lagrangian_density": lagrangian,
            "legendre_residual": float(np.vdot(pi, field_velocity).real-lagrangian-hamiltonian),
            "source_equations": -forces, "source_work_rates": forces,
            "coordinate_hamiltonian_source_derivatives": lapse*volume*forces,
            "independent_source_action_supplied": False}


def uniform_source_dilation(operator, field, momentum, *, source, source_velocity):
    """Uniform internal compression as a canonical dilation and moving basis.

    phi=exp(eta) psi and p=exp(-eta) Pi give H=exp(eta) H0.
    The time-dependent canonical transformation additionally gives
    H_moving=exp(eta) H0-dot_eta Re(Pi^* psi).  Its velocity Hessian in
    real (psi,eta) coordinates has the exact null vector (-psi,1).
    The calculation identifies the necessary dilation connection; it
    does not assign an independent source action or a lapse constraint.
    """
    A = _hermitian(operator, "operator")
    phi, p = np.asarray(field, complex), np.asarray(momentum, complex)
    if (phi.shape != (len(A),) or p.shape != phi.shape
            or not np.all(np.isfinite(phi)) or not np.all(np.isfinite(p))
            or not all(math.isfinite(value) for value in (source, source_velocity))):
        raise ValueError("finite uniform source and canonical field vectors required")
    if np.linalg.eigvalsh(A).min() <= 0:
        raise ValueError("native matter operator must be strictly positive")
    scale = math.exp(source)
    psi, Pi = phi/scale, scale*p
    reference_energy = float((np.vdot(Pi, Pi)+np.vdot(psi, A@psi)).real/2)
    native_energy = float((scale**3*np.vdot(p, p)+np.vdot(phi, A@phi)/scale).real/2)
    generator = float(np.vdot(Pi, psi).real)
    real_field = np.r_[psi.real, psi.imag]
    jacobian = np.column_stack((np.eye(len(real_field)), real_field))
    hessian = jacobian.T@jacobian/scale
    null = np.r_[-real_field, 1.]
    return {"transformed_field": psi, "transformed_momentum": Pi, "lapse": scale,
            "reference_energy": reference_energy, "native_energy": native_energy,
            "lapse_energy": scale*reference_energy, "dilation_generator": generator,
            "moving_hamiltonian": scale*reference_energy-source_velocity*generator,
            "velocity_hessian_real": hessian, "null_vector_real": null,
            "hessian_null_residual": hessian@null,
            "independent_source_action_supplied": False}


def _example(max_j=2, L=1.3, connection_amplitude=0.4):
    """Constant weak connection and three explicit stationary occupied modes."""
    generator = 1j*modes.spin_matrices(.5)[2]
    connection = ({}, {}, {(0, 0, 0): connection_amplitude/L*generator})
    carrier = covariant_scalar_operator(max_j=max_j, L=L, connection=connection, carrier_dimension=2)
    profiles = ({(0, 0, 0): 1.}, {(1, 0, 0): 1.},
                {(1, 1, 0): 1/math.sqrt(2), (1, -1, 0): -1/math.sqrt(2)})
    compressions = compression_matrices(profiles, carrier["labels"], 2)
    states = (((0, 0, 0), 0), ((1, 1, 1), 0), ((1, 1, 1), 1))
    occupations = []
    for label, component in states:
        index = 2*carrier["labels"].index(label)+component
        N = np.zeros_like(carrier["operator"])
        N[index, index] = 1.
        occupations.append(N)
    return carrier, compressions, occupations, states


def _low_state_support(carrier, states):
    """Actual full products, prior to the finite compression projection.

    For the constant connection, A preserves j.  With occupations in
    j<=1 and degree-one profiles, all intermediate modes in the first
    and second energy derivatives lie in j<=2.  Finite nonzero sources
    need arbitrarily many products and are a distinct finite model.
    """
    profiles = ({(0, 0, 0): 1.}, {(1, 0, 0): 1.},
                {(1, 1, 0): 1/math.sqrt(2), (1, -1, 0): -1/math.sqrt(2)})
    retained = set(carrier["labels"])
    first_loss, second_loss, max_spin = 0., 0., 0
    for label, component in states:
        vector = np.eye(2, dtype=complex)[:, component]
        for profile in profiles:
            first = modes.multiply(profile, {label: vector})
            max_spin = max(max_spin, max((k[0] for k in first), default=0))
            first_loss = max(first_loss, modes.mode_norm({k: v for k, v in first.items() if k not in retained}))
            for next_profile in profiles:
                second = modes.multiply(next_profile, first)
                second_loss = max(second_loss, modes.mode_norm({k: v for k, v in second.items() if k not in retained}))
    shells = np.repeat([j for j, _, _ in carrier["labels"]], 2)
    cross_shell = carrier["operator"]*(shells[:, None] != shells[None, :])
    mixing_norm = float(np.linalg.norm(cross_shell))
    return {"occupied_maximum_spin": max(label[0] for label, _ in states),
            "full_first_product_maximum_spin": max_spin,
            "first_product_omitted_norm": float(first_loss),
            "second_product_outside_retained_space_norm": float(second_loss),
            "operator_inter_shell_mixing_norm": mixing_norm,
            "low_state_second_derivatives_have_complete_intermediate_support":
                first_loss < 1e-13 and mixing_norm < 1e-13,
            "finite_nonzero_source_is_full_continuum_compression": False,
            "finite_source_family": "exp(P eta P) A_N exp(P eta P)",
            "support_reason": "constant B preserves j; the stationary second variation uses eta|occupied> as its intermediate states"}


def _canonical_matter_verification(carrier, profiles, occupations, static_response,
                                   extended, extended_profiles, extended_occupations):
    """Canonical dynamics on the same occupied source and its existing cutoff check."""
    data = _canonical_reference(carrier["operator"], sum(occupations), profiles)
    larger = _canonical_reference(extended["operator"], sum(extended_occupations), extended_profiles)
    frequency_unit = float(data["energies"].min())
    dimensionless_z = np.array([1j/2, 1j, 1+1j/2])
    parameters = frequency_unit*dimensionless_z
    response = _canonical_response(data, parameters)
    response_larger = _canonical_response(larger, parameters)
    source_values = np.array([[0., 1/32, 0.], [0., 0., -1/32], [0., 0., 0.]])
    dimensionless_durations = np.array([1/4, 1/2, 1/4])
    physical_durations = dimensionless_durations/frequency_unit
    source_family_cache = {}
    evolution = _canonical_evolution(data, source_values, physical_durations,
                                     family_cache=source_family_cache)
    clock_rates = np.array([1/2, 3/2, 2.])
    parameter_durations = physical_durations/clock_rates
    reparametrized = _canonical_evolution(data, source_values, parameter_durations,
        clock_rates=clock_rates, family_cache=source_family_cache)
    reparam_covariance_error = float(np.linalg.norm(
        reparametrized["phase_covariances"]-evolution["phase_covariances"])
        /max(np.linalg.norm(evolution["phase_covariances"]), np.finfo(float).tiny))
    reparam_work_error = float(np.max(np.abs(reparametrized["source_work"]-evolution["source_work"])))
    energy = static_response["energy"]
    force_error = float(np.linalg.norm(response["charges"]-static_response["charges"])
                        /max(np.linalg.norm(static_response["charges"]), np.finfo(float).tiny))
    contact_cutoff = float(np.linalg.norm(response["contact"]-response_larger["contact"])
                           /max(np.linalg.norm(response_larger["contact"]), np.finfo(float).tiny))
    response_cutoff = float(np.linalg.norm(response["response"]-response_larger["response"])
                            /max(np.linalg.norm(response_larger["response"]), np.finfo(float).tiny))
    energies, populations = data["energies"], data["normal_occupation"].diagonal().real
    uniform = np.array([np.sum(populations*(5*energies+16*energies**3/(z*z-4*energies**2)))
                        for z in parameters])
    uniform_error = float(np.linalg.norm(response["response"][:, 0, 0]-uniform)
                          /max(np.linalg.norm(uniform), np.finfo(float).tiny))
    final_covariance = evolution["phase_covariances"][-1]
    covariance_scale = max(np.linalg.norm(final_covariance), np.finfo(float).tiny)
    minimum_covariance = float(np.linalg.eigvalsh(final_covariance).min())
    n = len(carrier["operator"])
    tolerance = 128*np.finfo(float).eps*energies.max()
    degenerate = ((np.abs(energies[:, None]-energies[None, :]) <= tolerance)
                  & ~np.eye(n, dtype=bool))
    qq = data["eigenvectors"].conj().T@final_covariance[:n, :n]@data["eigenvectors"]
    coherence = float(np.linalg.norm(qq*degenerate))
    balance = float(np.max(np.abs(evolution["energy_balance_residual"])))
    checks = {
        "canonical_force_matches_static_source_charge": force_error < 2e-12,
        "full_frequency_response_has_complete_low_state_support": response_cutoff < 2e-12 and contact_cutoff < 2e-12,
        "uniform_source_has_exact_summed_frequency_response": uniform_error < 2e-12,
        "causal_response_solves_full_phase_equation": response["maximum_response_equation_residual"] < 2e-12,
        "exact_phase_flow_preserves_canonical_form": evolution["max_canonical_form_residual"] < 2e-12,
        "constant_source_preserves_canonical_energy": evolution["max_constant_source_energy_residual"] < 2e-12,
        "source_work_accounts_for_total_energy_change": balance/max(energy, np.finfo(float).tiny) < 2e-12,
        "phase_covariance_remains_nonnegative": minimum_covariance >= -2e-12*covariance_scale,
        "degenerate_source_coherence_is_retained": coherence > 1e-8,
        "positive_clock_reparametrization_preserves_phase_flow": reparam_covariance_error < 2e-12,
        "positive_clock_reparametrization_preserves_source_work": reparam_work_error/max(energy, np.finfo(float).tiny) < 2e-12,
    }
    def complex_record(value):
        return {"real": np.asarray(value).real.tolist(), "imaginary": np.asarray(value).imag.tolist()}
    phase_dimensions = [2*n, 2*len(extended["operator"])]
    return {
        "scope": "finite canonical internal conformal matter source; occupied classical ensemble",
        "action": "L=(dot_phi^dagger M dot_phi-phi^dagger B phi)/2; M=exp(-3 eta); B=exp(-eta/2) A exp(-eta/2)",
        "instantaneous_normal_operator": "M^(-1/2) B M^(-1/2)=exp(eta) A exp(eta)",
        "initial_phase_covariance": "W_qq=H^(-1/2) N H^(-1/2); W_pp=H^(1/2) N H^(1/2); W_qp=0",
        "source_state": "the same stationary occupations, connection and three compression profiles as the internal energy calculation",
        "frequency_unit": frequency_unit,
        "frequency_unit_definition": "smallest retained matter frequency; in the declared reciprocal radius unit",
        "dimensionless_spectral_parameters": complex_record(dimensionless_z),
        "force_response_convention": "source proportional to exp(-i z t), Im(z)>0; complete contact and phase-covariance response",
        "canonical_force_contact": response["contact"].tolist(),
        "canonical_force_response": complex_record(response["response"]),
        "difference_frequency_response": complex_record(response["difference_frequency_response"]),
        "summed_frequency_response": complex_record(response["summed_frequency_response"]),
        "static_charge_relative_residual": force_error,
        "contact_relative_cutoff_residual": contact_cutoff,
        "response_relative_cutoff_residual": response_cutoff,
        "uniform_response_relative_residual": uniform_error,
        "causal_response_relative_residual": response["maximum_response_equation_residual"],
        "finite_source_protocol": {"dimensionless_amplitudes": source_values.tolist(),
                                   "durations_in_inverse_frequency_unit": dimensionless_durations.tolist()},
        "clock_reparametrization": {
            "clock_rates": clock_rates.tolist(),
            "parameter_durations_in_inverse_frequency_unit": (parameter_durations*frequency_unit).tolist(),
            "proper_durations_in_inverse_frequency_unit": (reparametrized["proper_durations"]*frequency_unit).tolist(),
            "relative_phase_covariance_residual": reparam_covariance_error,
            "maximum_source_work_residual": reparam_work_error,
            "clock_relation": "d(proper time)=clock_rate*d(parameter) on each source segment",
            "clock_role": "selected monotone parametrization of the same source history",
            "additional_source_family_evaluations": reparametrized["evaluation_work"]["source_family_evaluations"],
            "reused_source_families": reparametrized["evaluation_work"]["source_family_cache_hits"],
            "additional_exact_segment_propagators": reparametrized["evaluation_work"]["exact_segment_propagators"],
        },
        "segment_energies": evolution["energies"].tolist(),
        "source_work": evolution["source_work"].tolist(),
        "maximum_energy_balance_residual": balance,
        "maximum_canonical_form_residual": evolution["max_canonical_form_residual"],
        "maximum_constant_source_energy_residual": evolution["max_constant_source_energy_residual"],
        "final_covariance_minimum_eigenvalue": minimum_covariance,
        "final_covariance_scale": float(covariance_scale),
        "final_degenerate_position_coherence_norm": coherence,
        "degeneracy_diagnostic_tolerance": float(tolerance),
        "degeneracy_treatment": "all phase entries are evolved and all response denominators retained; tolerance only labels the reported coherence",
        "dominant_operation_counts": {"reference_mode_diagonalizations": 2,
                                       "nonzero_source_diagonalizations": 2,
                                       "nonzero_source_mode_diagonalizations": 2,
                                       "exact_segment_propagators": 2*len(source_values),
                                       "retained_phase_dimensions": phase_dimensions,
                                       "causal_entry_divisions": len(parameters)*len(profiles)*sum(d*d for d in phase_dimensions),
                                       "phase_response_basis_transforms": 0,
                                       "dense_liouvillian_factorizations": 0},
        "finite_source_continuum_limit_certified": False,
        "external_gravitational_kernel_computed": False,
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": bool(all(checks.values())),
    }


def _polar_congruence_verification(reference_mass_squared):
    """Three local solutions of the polar jet equations, without evolution fits."""
    flat = np.diag([-1., 1., 1., 1.])
    r = 3/4
    # Static metric and rest phase: eta=-log N, with constant amplitude.
    acceleration = 1/8
    static_metric_gradient = np.zeros((4, 4, 4))
    static_metric_gradient[1, 0, 0] = -2*acceleration
    static = dict(reference_mass_squared=reference_mass_squared, source=0.,
                  source_gradient=np.array([0., -acceleration, 0., 0.]),
                  metric=flat, metric_gradient=static_metric_gradient,
                  amplitude=r, amplitude_gradient=np.zeros(4), amplitude_hessian=np.zeros((4, 4)),
                  phase_gradient=np.array([math.sqrt(reference_mass_squared), 0., 0., 0.]),
                  phase_hessian=np.zeros((4, 4)), quantum_pressure_gradient=np.zeros(4))
    # Expanding homogeneous source: both amplitude and phase jets obey their
    # equations at the evaluation point; its congruence is exactly geodesic.
    expansion, source_rate, scale = 1/7, 1/32, 4/3
    metric = np.diag([-1., scale**2, scale**2, scale**2])
    metric_gradient = np.zeros((4, 4, 4))
    metric_gradient[0, 1:, 1:] = 2*expansion*scale**2*np.eye(3)
    dr, ddr, ddt = np.zeros(4), np.zeros((4, 4)), np.zeros((4, 4))
    dr[0] = r*(source_rate-3*expansion/2)
    ddr[0, 0] = (3*source_rate-3*expansion)*dr[0]
    ddt[0, 0] = math.sqrt(reference_mass_squared)*source_rate
    homogeneous = dict(static, metric=metric, metric_gradient=metric_gradient,
                       source_gradient=np.array([source_rate, 0., 0., 0.]),
                       amplitude_gradient=dr, amplitude_hessian=ddr, phase_hessian=ddt)
    # Nonzero quantum pressure and its independent gradient: a moving phase
    # probes the correction to the acceleration of the compression source.
    pressure = reference_mass_squared/10
    wave_number, phase_curvature = math.sqrt(reference_mass_squared)/4, reference_mass_squared/16
    dr, ddr, ddt, dpressure = np.zeros(4), np.zeros((4, 4)), np.zeros((4, 4)), np.zeros(4)
    dr[1], ddr[1, 1], ddt[1, 1] = -r*phase_curvature/(2*wave_number), r*pressure, phase_curvature
    dpressure[1] = 2*wave_number*phase_curvature
    varying_pressure = dict(static, metric_gradient=np.zeros((4, 4, 4)), source_gradient=np.zeros(4),
                            amplitude_gradient=dr, amplitude_hessian=ddr, phase_hessian=ddt,
                            phase_gradient=np.array([math.sqrt(reference_mass_squared+wave_number**2-pressure),
                                                     wave_number, 0., 0.]),
                            quantum_pressure_gradient=dpressure)
    cases, maxima = {}, {}
    for name, inputs in (("static_rest_phase", static), ("homogeneous_expansion", homogeneous),
                         ("varying_quantum_pressure", varying_pressure)):
        result = polar_source_congruence(**inputs)
        dr, dt = inputs["amplitude_gradient"], inputs["phase_gradient"]
        first = (dr+1j*r*dt)[:, None]
        second = (inputs["amplitude_hessian"]-r*np.outer(dt, dt)
                  +1j*(np.outer(dr, dt)+np.outer(dt, dr)+r*inputs["phase_hessian"]))[:, :, None]
        direct = covariant_source_jet(np.array([[reference_mass_squared]]), [np.eye(1)], [inputs["source"]],
                                      metric=inputs["metric"], metric_gradient=inputs["metric_gradient"],
                                      field=[r], field_gradient=first, field_hessian=second,
                                      source_gradient=inputs["source_gradient"][:, None])
        residuals = {
            "normalization": abs(result["normalization_residual"]),
            "radial_equation": abs(result["radial_equation_residual"]),
            "radial_gradient": float(np.max(np.abs(result["radial_gradient_residual"]))),
            "phase_current": abs(result["number_current_divergence"]),
            "complex_field_equation": float(np.max(np.abs(direct["field_equation"]))),
            "complex_stress": float(np.max(np.abs(result["stress_tensor"]-direct["stress_tensor"]))),
            "complex_source": abs(result["source_equation"]-direct["source_equations"][0]),
            "stress_decomposition": float(np.max(np.abs(result["stress_decomposition_residual"]))),
            "source_decomposition": abs(result["source_decomposition_residual"]),
            "acceleration_kinematics": float(np.max(np.abs(result["acceleration_kinematic_residual"]))),
            "pressure_acceleration": float(np.max(np.abs(result["pressure_acceleration_residual"]))),
            "phase_clock_rate": abs(result["clock"]["phase_rate_identity_residual"]),
            "proper_time_rate": abs(result["clock"]["proper_time_rate_residual"]),
            "clock_acceleration_identity": float(np.max(np.abs(
                result["clock"]["clock_acceleration_identity_residual"]))),
        }
        for key, value in residuals.items():
            maxima[key] = max(maxima.get(key, 0.), value)
        cases[name] = {
            "inputs": {key: (value.tolist() if isinstance(value, np.ndarray) else value)
                       for key, value in inputs.items()},
            "density": result["density"], "source_equation": result["source_equation"],
            "relative_quantum_pressure": result["relative_quantum_pressure"],
            "acceleration_covariant": result["acceleration_covariant"].tolist(),
            "clock": {key: (value.tolist() if isinstance(value, np.ndarray) else value)
                      for key, value in result["clock"].items()},
            "residuals": residuals,
        }
    scale = max(1., reference_mass_squared)
    checks = {key: value < 2e-12*scale for key, value in maxima.items()}
    checks["static_acceleration_is_nonzero"] = abs(cases["static_rest_phase"]["acceleration_covariant"][1]-acceleration) < 2e-12
    checks["homogeneous_congruence_is_geodesic"] = max(abs(v) for v in cases["homogeneous_expansion"]["acceleration_covariant"]) < 2e-12
    checks["homogeneous_phase_clock_is_closed"] = np.max(np.abs(
        cases["homogeneous_expansion"]["clock"]["clock_covector_exterior_derivative"])) < 2e-12
    checks["static_accelerated_clock_has_nonzero_exterior_derivative"] = abs(
        cases["static_rest_phase"]["clock"]["clock_covector_exterior_derivative"][1][0]-acceleration) < 2e-12
    checks["phase_is_strictly_increasing_in_its_proper_time"] = all(
        case["clock"]["phase_rate_per_proper_time"] > 0 for case in cases.values())
    return {"scope": "native scalar phase congruence, source exchange and quantum-pressure corrections",
            "verification_inputs": "dimensionless local jets; reference mass from the retained native mode",
            "real_coordinate_count": 2, "case_count": len(cases), "cases": cases,
            "maximum_residuals": maxima,
            "operation_counts": {"local_polar_jet_evaluations": len(cases),
                                 "independent_complex_jet_evaluations": len(cases),
                                 "clock_covector_exterior_derivatives": len(cases),
                                 "additional_polar_jet_evaluations_for_clocks": 0,
                                 "time_evolution_steps": 0},
            "checks": {key: bool(value) for key, value in checks.items()},
            "passed": bool(all(checks.values()))}


def _covariant_interface_verification(carrier, profiles, occupations):
    """Dimensionless local jets on the same three occupied native modes."""
    A, N = carrier["operator"], sum(occupations)
    indices = np.flatnonzero(np.diag(N).real > 0)
    basis = np.eye(len(A))[:, indices]
    source = np.array([1/64, 1/32, -1/48])
    coefficients = np.array([1., 1/2, 1j/3])
    gradient_coefficients = np.array([[1/4, 1j/5, -1/6], [1j/7, 1/8, 1/9],
                                     [-1/10, 1j/11, 1/12], [1/13, -1/14, 1j/15]])
    hessian_coefficients = np.array([[(r+1)*(s+1)*coefficients/128 for s in range(4)]
                                    for r in range(4)])
    phi = basis@coefficients
    first = gradient_coefficients@basis.T
    second = np.einsum("rsa,ia->rsi", hessian_coefficients, basis)
    h = np.array([[4/3, 1/12, 0.], [1/12, 5/4, 1/16], [0., 1/16, 7/6]])
    lapse, shift = 5/4, np.array([1/8, -1/10, 1/12])
    metric = np.zeros((4, 4))
    metric[0, 0], metric[0, 1:], metric[1:, 0], metric[1:, 1:] = (
        -lapse*lapse+shift@h@shift, h@shift, h@shift, h)
    metric_direction = np.array([[1., 1/3, 0., -1/5], [1/3, -1/2, 1/7, 0.],
                                 [0., 1/7, 1/4, -1/9], [-1/5, 0., -1/9, -1/6]])
    metric_gradient = np.array([(r+1)*metric_direction/128 for r in range(4)])
    source_gradient = np.array([[1/16, -1/24, 1/32], [-1/20, 1/28, 1/36],
                                [1/24, 1/32, -1/40], [1/28, -1/36, 1/44]])
    matrices = _conformal_source_differential(A, profiles, source)
    ward = _covariant_source_jet(matrices, metric, metric_gradient, phi, first, second, source_gradient)
    volume = float(np.sqrt(np.linalg.det(h)))
    normal_velocity = (first[0]-shift@first[1:])/lapse
    momentum = volume*matrices["mass_matrix"]@normal_velocity
    adm = _canonical_source_adm(matrices, h, lapse, shift, phi, first[1:], momentum)
    normal = np.r_[1/lapse, -shift/lapse]
    stress_energy = float(normal@ward["stress_tensor"]@normal)
    stress_momentum = volume*(normal@ward["stress_tensor"][:, 1:])
    energy_error = abs(stress_energy-adm["normal_energy"])
    momentum_error = float(np.linalg.norm(stress_momentum-adm["momentum_density"]))
    charge_error = float(np.linalg.norm(ward["source_equations"]-adm["source_equations"]))
    ward_error = float(np.max(np.abs(ward["ward_residual"])))
    ward_scale = max(np.linalg.norm(ward["stress_divergence"]),
                     np.linalg.norm(ward["ward_matter_term"])+np.linalg.norm(ward["ward_source_term"]),
                     np.finfo(float).tiny)
    uniform = uniform_source_dilation(A, phi, momentum, source=1/32, source_velocity=-1/48)
    dilation_error = abs(uniform["native_energy"]-uniform["lapse_energy"])
    null_error = float(np.linalg.norm(uniform["hessian_null_residual"]))
    # Retain two existing real component directions in the constant shell.
    # Their common eigenvalue and invariant span are checked on the full
    # native operator; the polar notation adds no carrier copy.
    pair_start = carrier["carrier_dimension"]*carrier["labels"].index((0, 0, 0))
    pair_indices = [pair_start, pair_start+1]
    if carrier["carrier_dimension"] < 2:
        raise ValueError("the polar verification requires two existing constant-shell components")
    pair_frame = np.eye(len(A))[:, pair_indices]
    pair_mass_squared = float(np.trace(pair_frame.T@A@pair_frame).real/2)
    pair_residual = float(np.linalg.norm(A@pair_frame-pair_mass_squared*pair_frame))
    polar = _polar_congruence_verification(pair_mass_squared)
    pair_check = pair_residual < 2e-12*max(1., pair_mass_squared)
    polar["retained_real_pair"] = {
        "basis_indices": pair_indices, "internal_shell": [0, 0, 0],
        "carrier_components": [0, 1], "verified_real_multiplicity_at_least": 2,
        "reference_mass_squared": pair_mass_squared,
        "invariant_pair_residual": pair_residual,
        "coordinate_map": "phi=phi_1+i phi_2, using the two existing real component directions",
        "additional_carrier_copies": 0,
    }
    polar["checks"]["existing_degenerate_real_pair_is_invariant"] = bool(pair_check)
    polar["passed"] = bool(polar["passed"] and pair_check)
    checks = {
        "off_shell_covariant_source_exchange": ward_error/ward_scale < 2e-12,
        "normal_stress_matches_lapse_source": energy_error/max(stress_energy, np.finfo(float).tiny) < 2e-12,
        "mixed_stress_matches_shift_source": momentum_error < 2e-12,
        "covariant_source_charge_matches_canonical_work": charge_error < 2e-12,
        "canonical_matter_legendre_identity": abs(adm["legendre_residual"]) < 2e-12,
        "uniform_source_has_exact_canonical_dilation": dilation_error < 2e-12,
        "dilation_velocity_form_has_generated_null_direction": null_error < 2e-12,
        "native_phase_congruence_and_source_exchange": polar["passed"],
    }
    def complex_record(value):
        return {"real": np.asarray(value).real.tolist(), "imaginary": np.asarray(value).imag.tolist()}
    return {
        "scope": "finite internal matter coupled dynamically to the common noncompact metric and scalar-compression sectors",
        "covariant_action": "S_m=-integral sqrt(-g) [g^{mu nu} partial_mu(phi)^dagger M partial_nu(phi)+phi^dagger B phi]/2",
        "source_action_supplied": False,
        "source_exchange_identity": "nabla_mu T^mu_nu=Re(E_phi^dagger partial_nu phi)+Q_a partial_nu eta^a",
        "source_equations_required_for_total_conservation": "E_a_generated+Q_a=0",
        "native_carrier_dimension": len(A),
        "verification_inputs": {
            "kind": "dimensionless local verification jets, not production physical parameters",
            "occupied_basis_indices": indices.tolist(), "compression_amplitudes": source.tolist(),
            "field_coefficients": complex_record(coefficients),
            "field_gradient_coefficients": complex_record(gradient_coefficients),
            "field_hessian_coefficients": complex_record(hessian_coefficients),
            "metric": metric.tolist(), "metric_gradient": metric_gradient.tolist(),
            "source_gradient": source_gradient.tolist(),
            "uniform_compression": 1/32, "uniform_compression_velocity": -1/48},
        "stress_tensor": ward["stress_tensor"].tolist(),
        "stress_divergence": ward["stress_divergence"].tolist(),
        "matter_equation_contribution": ward["ward_matter_term"].tolist(),
        "source_exchange_contribution": ward["ward_source_term"].tolist(),
        "source_equations": ward["source_equations"].tolist(),
        "maximum_ward_residual": ward_error, "relative_ward_residual": float(ward_error/ward_scale),
        "normal_energy": adm["normal_energy"],
        "normal_hamiltonian_density": adm["normal_hamiltonian_density"],
        "momentum_density": adm["momentum_density"].tolist(),
        "normal_stress_residual": energy_error, "momentum_stress_residual": momentum_error,
        "source_work_charge_residual": charge_error, "legendre_residual": adm["legendre_residual"],
        "uniform_dilation": {"native_energy": uniform["native_energy"],
                             "lapse_energy": uniform["lapse_energy"],
                             "dilation_generator": uniform["dilation_generator"],
                             "moving_hamiltonian": uniform["moving_hamiltonian"],
                             "energy_residual": dilation_error,
                             "velocity_hessian_dimension": 2*len(A)+1,
                             "velocity_hessian_rank": 2*len(A),
                             "rank_basis": "Gram matrix of the full-row-rank block [I,psi_real]",
                             "null_residual": null_error},
        "polar_source_congruence": polar,
        "dominant_operation_counts": {"common_source_diagonalizations": 1,
                                       "exponential_frechet_divided_difference_matrices": 2,
                                       "source_frechet_directions_per_matrix": len(profiles),
                                       "external_metric_inversions": 1,
                                       "spatial_metric_inversions": 1,
                                       "finite_difference_derivatives": 0},
        "external_gravitational_kernel_computed": False,
        "checks": {key: bool(value) for key, value in checks.items()},
        "passed": bool(all(checks.values())),
    }


def evaluate_matter_source_response():
    """Executed native matter example, JSON ready; no store writes or fit."""
    carrier, profiles, occupations, states = _example()
    A = carrier["operator"]
    combined = energy_response(A, sum(occupations), profiles)
    support = _low_state_support(carrier, states)
    per_state = [energy_response(A, N, profiles) for N in occupations]
    centre = combined["energy"]
    h = 3e-4
    occupation = sum(occupations)
    source_values = {}
    source_requests = 0
    def energy(x):
        nonlocal source_requests
        source_requests += 1
        key = tuple(x)
        if key not in source_values:
            source_values[key] = finite_sourced_energy(A, occupation, profiles, x)
        return source_values[key]
    # Both Hessian orders use the same four finite-source values.  Reuse
    # those values while retaining each independent difference formula.
    finite_hessian = np.empty((len(profiles), len(profiles)))
    for i in range(len(profiles)):
        ei = np.eye(len(profiles))[i]*h
        for j in range(len(profiles)):
            ej = np.eye(len(profiles))[j]*h
            finite_hessian[i, j] = ((energy(ei)+energy(-ei)-2*centre)/h**2 if i == j else
                (energy(ei+ej)-energy(ei-ej)-energy(-ei+ej)+energy(-ei-ej))/(4*h*h))
    derivative_error = float(np.linalg.norm(finite_hessian-combined["hessian"])/np.linalg.norm(combined["hessian"]))
    extended, ext_profiles, ext_occupations, _ = _example(max_j=3)
    extended_response = energy_response(extended["operator"], sum(ext_occupations), ext_profiles)
    canonical = _canonical_matter_verification(carrier, profiles, occupations, combined,
                                              extended, ext_profiles, ext_occupations)
    covariant = _covariant_interface_verification(carrier, profiles, occupations)
    cutoff_error = float(np.linalg.norm(extended_response["hessian"]-combined["hessian"])/np.linalg.norm(combined["hessian"]))
    uniform_error = max(abs(row["charges"][0]-row["energy"])/row["energy"] for row in per_state)
    addition_error = float(np.linalg.norm(sum(row["hessian"] for row in per_state)-combined["hessian"]))
    curvature = modes.curvature(({}, {}, {(0, 0, 0): .4/1.3*(1j*modes.spin_matrices(.5)[2])}), L=1.3)
    operator_minimum = float(np.linalg.eigvalsh(A).min())
    checks = {"stationary_occupied_states": all(row["stationary"] for row in per_state),
              "uniform_source_measures_total_energy": uniform_error < 1e-12,
              "positive_native_operator": operator_minimum >= carrier["lower_bound"]-1e-12,
              "positive_fixed_occupation_compression_hessian": combined["minimum_hessian_eigenvalue"] > 0,
              "independent_finite_source_derivative": derivative_error < 2e-6,
              "complete_low_state_second_order_support": cutoff_error < 1e-11,
              "actual_product_support": support["low_state_second_derivatives_have_complete_intermediate_support"],
              "additive_occupied_matter_response": addition_error < 1e-12,
              "canonical_matter_dynamics": canonical["passed"],
              "native_covariant_interface": covariant["passed"]}
    return {"scope": "native covariant scalar matter energy response to internal conformal sources",
            "inputs": {"radius": 1.3, "radius_unit": "one declared reciprocal energy unit",
                       "carrier": "unitary weak doublet with scalar kinetic operator",
                       "connection": "B_3=(0.4/L) i J_3; B_1=B_2=0, held fixed under compression",
                       "connection_amplitude": .4,
                       "occupation": [{"mode_jmn": list(label), "doublet_component": component, "number": 1.}
                                      for label, component in states],
                       "profiles": ["1", "e(1,0,0)", "[e(1,1,0)-e(1,-1,0)]/sqrt(2)"],
                       "source_amplitude": "dimensionless real conformal compression",
                       "maximum_scalar_spin": 2, "check_maximum_scalar_spin": 3},
            "state_equation": "H(eta)^2=exp(eta) A_B exp(eta); E_N=Tr(N H(eta))",
            "nonzero_connection_curvature_norm": math.sqrt(sum(modes.mode_norm(f)**2 for f in curvature)),
            "matter_operator_minimum": operator_minimum,
            "matter_operator_bound": carrier["lower_bound"],
            "total_energy": centre, "energy_unit": "inverse declared radius unit",
            "per_state_energies": [row["energy"] for row in per_state],
            "source_charges": combined["charges"].tolist(),
            "cross_source_hessian": combined["hessian"].tolist(),
            "second_source_direct_term": combined["second_source_direct_term"].tolist(),
            "square_root_feedback": combined["square_root_feedback"].tolist(),
            "minimum_hessian_eigenvalue": combined["minimum_hessian_eigenvalue"],
            "finite_source_relative_residual": derivative_error,
            "finite_source_operation_counts": {
                "source_directions": len(profiles),
                "finite_energy_requests": source_requests,
                "finite_energy_evaluations": len(source_values),
                "reused_finite_energy_values": source_requests-len(source_values),
                "reused_central_energy": 1},
            "cutoff_relative_residual": cutoff_error,
            "uniform_energy_charge_relative_residual": uniform_error,
            "additive_matter_residual": addition_error,
            "source_support": support,
            "canonical_matter_dynamics": canonical,
            "native_covariant_interface": covariant,
            "all_particle_carriers_included": False,
            "external_gravitational_kernel_computed": False,
            "remaining_data": ["generated collective source action and coupled constraints",
                               "equivariant internal-source and metric map",
                               "complete matter vertices and reduced spacetime principal symbol"],
            "checks": {key: bool(value) for key, value in checks.items()},
            "passed": bool(all(checks.values())), "checks_passed": bool(all(checks.values()))}
