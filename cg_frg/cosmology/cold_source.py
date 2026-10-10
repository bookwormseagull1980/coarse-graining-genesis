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

"""Cold stress projections and single-stream characteristic transport.

The relativistic tensor uses metric signature (-+++). The plane-symmetric
evolution solves the specified Newtonian dust model on a flat expanding
background and retains the physical-density/comoving-coordinate convention.
"""
import numpy as np


def transported_density(initial_density, deformation_gradient, *,
                        scale_factor, initial_scale_factor=1.):
    """Mass-conserving comoving dust transport before characteristic crossing.

    deformation_gradient is dx(t,q)/dq; the initial labels are comoving.
    Inputs may carry any common batch dimensions. Positive determinant
    selects an orientation-preserving, locally invertible map; global
    injectivity is a separate assumption. This is the exact continuity
    solution for a supplied flow, not a solver for its gravitational force.
    """
    gradient = np.asarray(deformation_gradient, float)
    density = np.asarray(initial_density, float)
    if (gradient.ndim < 2 or gradient.shape[-2:] != (3, 3)
            or not np.isfinite(gradient).all() or not np.isfinite(density).all()
            or np.any(density < 0)):
        raise ValueError("nonnegative density and finite 3 by 3 deformation required")
    if not all(np.isfinite(x) and x > 0 for x in (scale_factor, initial_scale_factor)):
        raise ValueError("positive finite scale factors required")
    jacobian = np.linalg.det(gradient)
    if np.any(jacobian <= 0):
        raise ValueError("dust transport requires positive Jacobian before crossing")
    return density*(initial_scale_factor/scale_factor)**3/jacobian


def plane_dust_solution(q, *, amplitude, growth, growth_velocity, scale_factor,
                        mean_density, four_pi_G=1., wave_number=1.):
    """Exact single-stream plane-parallel growing-mode density and force.

    x=q-A*D*sin(kq)/k and v=a*dx/dt. D obeys
    Dddot+2*H*Ddot=4*pi*G*rho_bar*D, rho_bar proportional to a^-3.
    The supplied growth and growth_velocity are a slice of that solution.
    The potential obeys the comoving Poisson equation for density contrast.
    The formula validates continuity and force at this slice; it does not
    determine an arbitrary expansion history or cross a dust caustic.
    """
    q = np.asarray(q, float)
    if not np.isfinite(q).all() or not all(np.isfinite(x) for x in
            (amplitude, growth, growth_velocity, scale_factor, mean_density,
             four_pi_G, wave_number)):
        raise ValueError("finite coordinates and cosmological data required")
    if min(scale_factor, mean_density, four_pi_G, wave_number) <= 0:
        raise ValueError("positive scale, mean density, gravity and wave number required")
    if abs(amplitude*growth) >= 1:
        raise ValueError("global single-stream plane solution requires abs(A*D)<1")
    phase = wave_number*q
    jacobian = 1-amplitude*growth*np.cos(phase)
    density = mean_density/jacobian
    x = q-amplitude*growth*np.sin(phase)/wave_number
    velocity = -scale_factor*amplitude*growth_velocity*np.sin(phase)/wave_number
    force = (four_pi_G*scale_factor**2*mean_density*amplitude*growth
             *np.sin(phase)/wave_number)
    laplacian = four_pi_G*scale_factor**2*mean_density*(1/jacobian-1)
    return {"comoving_position": x, "peculiar_velocity": velocity,
            "jacobian": jacobian, "density": density,
            "potential_gradient": force, "potential_laplacian": laplacian,
            "minimum_jacobian_bound": 1-abs(amplitude*growth),
            "density_convention": "physical density, comoving spatial derivatives"}


def evaluate_cold_transport():
    """Independent finite differences and period-integral of exact dust data."""
    amplitude, growth, growth_velocity = .3, .7, .9
    scale, mean, gravity, wave = .8, 1.2, 1., 2.
    q = np.linspace(0, 2*np.pi/wave, 257, endpoint=False)
    options = dict(amplitude=amplitude, growth=growth, growth_velocity=growth_velocity,
                   scale_factor=scale, mean_density=mean, four_pi_G=gravity, wave_number=wave)
    result = plane_dust_solution(q, **options)
    eps = 1e-5
    plus, minus = (plane_dust_solution(q+s*eps, **options) for s in (1, -1))
    derivative = (plus['potential_gradient']-minus['potential_gradient'])/(2*eps)
    poisson_error = float(np.max(np.abs(derivative/result['jacobian']
        -gravity*scale**2*(result['density']-mean))))
    mean_error = float(abs(np.mean(result['density']*result['jacobian'])-mean))
    gradient = np.broadcast_to(np.eye(3), (len(q), 3, 3)).copy()
    gradient[:, 0, 0] = result['jacobian']
    transported = transported_density(mean*scale**3, gradient, scale_factor=scale)
    transport_error = float(np.max(np.abs(transported-result['density'])))
    if poisson_error > 1e-9 or max(mean_error, transport_error) > 1e-13:
        raise ArithmeticError("single-stream cold-source transport verification failed")
    evolution = evolve_plane_dust(a_initial=.05, a_final=1., amplitude=.2,
                                  omega_m0=1., omega_cold0=1.)
    eds_error = float(abs(evolution['growth']-1.))
    if eds_error > 2e-10:
        raise ArithmeticError("plane dust evolution failed the exact Einstein-de Sitter solution")
    return {"scope": "periodic plane dust before characteristic crossing",
            "inputs": options, "minimum_jacobian_bound": result['minimum_jacobian_bound'],
            "poisson_finite_difference_residual": poisson_error,
            "physical_volume_mean_residual": mean_error,
            "continuity_pushforward_residual": transport_error,
            "growth_equation": "Dddot+2*H*Ddot=4*pi*G*rho_bar*D",
            "evolution_computed": True, "evolution": evolution,
            "einstein_de_sitter_growth_residual": eds_error,
            "checks_passed": True}


def evolve_plane_dust(*, a_initial, a_final, amplitude, omega_m0,
                      omega_cold0, h0=1., four_pi_G=1., wave_number=1.,
                      rtol=2e-11, atol=2e-13):
    """Evolve exact plane dust characteristics in a specified flat background.

    H(a)^2=H0^2[Omega_m0/a^3+1-Omega_m0]. Only Omega_cold0 clusters;
    the remaining matter, if any, is stipulated homogeneous in this model.
    The initial D=a^p, dD/dln(a)=p*D use the matter-era growing exponent
    p=(sqrt(1+24*Omega_cold0/Omega_m0)-1)/4. They are initial data at
    finite a_initial, not an exact Lambda-era growing-mode projection.
    The result includes the displacement and velocity at the final scale.
    """
    from scipy.integrate import solve_ivp
    values=(a_initial,a_final,amplitude,omega_m0,omega_cold0,h0,
            four_pi_G,wave_number,rtol,atol)
    if not all(np.isfinite(x) for x in values):
        raise ValueError("finite dust evolution inputs required")
    if (not 0 < a_initial < a_final or not 0 < omega_cold0 <= omega_m0 <= 1
            or min(h0,four_pi_G,wave_number,rtol,atol) <= 0):
        raise ValueError("ordered positive scales and 0<Omega_cold<=Omega_m<=1 required")
    exponent=(np.sqrt(1+24*omega_cold0/omega_m0)-1)/4
    initial=a_initial**exponent
    if abs(amplitude*initial) >= 1:
        raise ValueError("initial dust map is not single stream")
    def rhs(loga,state):
        inva3=np.exp(-3*loga)
        e2=omega_m0*inva3+1-omega_m0
        fm,fc=omega_m0*inva3/e2,omega_cold0*inva3/e2
        d,p=state
        return (p, -(2-1.5*fm)*p+1.5*fc*d)
    def crossing(loga,state):
        return 1-abs(amplitude)*state[0]
    crossing.terminal=True
    crossing.direction=-1
    solution=solve_ivp(rhs,(np.log(a_initial),np.log(a_final)),
        (initial,exponent*initial),method='DOP853',rtol=rtol,atol=atol,
        max_step=.1,events=crossing)
    if not solution.success:
        raise RuntimeError(solution.message)
    if solution.t_events[0].size:
        raise ValueError("dust characteristic crossing occurs inside the requested interval")
    growth,log_derivative=solution.y[:,-1]
    hubble=h0*np.sqrt(omega_m0/a_final**3+1-omega_m0)
    mean=1.5*h0**2*omega_cold0/(four_pi_G*a_final**3)
    q=np.linspace(0,2*np.pi/wave_number,129,endpoint=False)
    final=plane_dust_solution(q,amplitude=amplitude,growth=growth,
        growth_velocity=hubble*log_derivative,scale_factor=a_final,
        mean_density=mean,four_pi_G=four_pi_G,wave_number=wave_number)
    mean_residual=float(abs(np.mean(final['density']*final['jacobian'])-mean))
    # D and dD/dln(a) stay positive: at P=0 the RHS for P is positive.
    # Hence final D gives the minimum Jacobian throughout the accepted path.
    return {"a_initial":a_initial,"a_final":a_final,
            "omega_m0":omega_m0,"omega_cold0":omega_cold0,
            "H0":h0,"four_pi_G":four_pi_G,"amplitude":amplitude,
            "wave_number":wave_number,"growth":float(growth),
            "growth_log_derivative":float(log_derivative),
            "comoving_displacement_amplitude":float(amplitude*growth/wave_number),
            "peculiar_velocity_amplitude":float(
                a_final*amplitude*hubble*log_derivative/wave_number),
            "characteristic_convention":"x=q-displacement*sin(kq); v=-velocity_amplitude*sin(kq)",
            "initial_growing_exponent":float(exponent),
            "minimum_jacobian_bound":float(final['minimum_jacobian_bound']),
            "mean_density":float(mean),"physical_volume_mean_residual":mean_residual,
            "function_evaluations":int(solution.nfev),
            "rtol":rtol,"atol":atol,"equations":"single-stream Euler-Poisson with specified background",
            "numerical_error_scope":"adaptive integration estimate; EdS has an independent exact check"}


def projection_check(metric, u, residual, *, tolerance=1e-10, covariant_divergence=None):
    g, u, E = np.asarray(metric, float), np.asarray(u, float), np.asarray(residual, float)
    if g.shape != (4, 4) or u.shape != (4,) or E.shape != (4, 4):
        raise ValueError('metric/residual 4x4 and velocity length 4 required')
    if not np.all(np.isfinite(g)) or not np.all(np.isfinite(u)) or not np.all(np.isfinite(E)):
        raise ValueError('finite tensors required')
    if not np.allclose(g, g.T, atol=tolerance) or not np.allclose(E, E.T, atol=tolerance):
        raise ValueError('symmetric metric and residual required')
    eigenvalues = np.linalg.eigvalsh(g)
    if np.count_nonzero(eigenvalues < 0) != 1 or np.count_nonzero(eigenvalues > 0) != 3:
        raise ValueError('metric signature must be (-+++)')
    lower = g@u
    unit_error = abs(u@lower+1)
    if unit_error > tolerance:
        raise ValueError('u must be unit timelike')
    projector = np.eye(4)+np.outer(lower, u)
    spatial, mixed = projector@E@projector.T, projector@E@u
    rho = float(u@E@u)
    reconstruction = E-rho*np.outer(lower, lower)
    scale = max(1., np.max(np.abs(E)))
    cold = max(np.max(np.abs(spatial)), np.max(np.abs(mixed))) <= tolerance*scale
    if covariant_divergence is None:
        conservation = None
    else:
        divergence = np.asarray(covariant_divergence, float)
        if divergence.shape != (4,) or not np.all(np.isfinite(divergence)):
            raise ValueError('supplied covariant divergence must be finite length 4')
        conservation = bool(np.max(np.abs(divergence)) <= tolerance*scale)
    return {'rho': rho, 'nonnegative_density': rho >= 0,
            'cold_projections_satisfied': bool(cold),
            'spatial_projection_max': float(np.max(np.abs(spatial))),
            'mixed_projection_max': float(np.max(np.abs(mixed))),
            'dust_reconstruction_max': float(np.max(np.abs(reconstruction))),
            'supplied_conservation_satisfied': conservation,
            'evolution_computed': False}
