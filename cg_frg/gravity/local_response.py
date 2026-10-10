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

"""Dirichlet local response and finite plane-symmetric source dynamics.

Solves div[mu(|grad Phi|/a0) grad Phi]=f, f=4*pi*G*(rho_b+rho_free).
Piecewise-linear finite elements minimize the strictly convex energy.
Input sources are finite smooth nodal samples. A global evolution supplies
the local source and ambient boundary field; this module evaluates their
quasistatic constitutive response.
Optional epsilon regularizes only the numerical flux near zero gradient;
its value is returned and must be reduced in a regularization study.

The plane material-cell model couples the same unregularized nonlinear
field to pressureless trajectories using its variational mass matrix.
It evaluates mass conservation, total energy and Dirichlet boundary work
before cell crossing, with explicit spatial and temporal discretizations.

The independent-foliation functions evaluate the stated effective action
on its own field and constraint space. Local flux and material evolution
use their variational equations directly. Generated matter congruences
are computed from the native phase response in matter_source_response.
"""
from __future__ import annotations
from functools import lru_cache
from itertools import permutations, product
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import spsolve
from scipy.linalg import cho_factor, cho_solve, eigvalsh


def flux(g, a0=1.0, epsilon=0.0):
    g = np.asarray(g, dtype=float)
    w = np.sqrt(np.sum(g*g, axis=-1) + epsilon*epsilon)
    return (w/np.sqrt(w*w+a0*a0))[..., None]*g


def flux_jacobian(g, a0=1.0, epsilon=0.0):
    g = np.asarray(g, dtype=float)
    w = np.sqrt(np.sum(g*g, axis=-1) + epsilon*epsilon)
    den = np.sqrt(w*w+a0*a0)
    mu = w/den
    c = np.divide(a0*a0, w*den**3, out=np.zeros_like(w), where=w > 0)
    return mu[..., None, None]*np.eye(3) + c[..., None, None]*g[..., :, None]*g[..., None, :]


def primitive(g, a0=1.0, epsilon=0.0):
    w = np.sqrt(np.sum(g*g, axis=-1)+epsilon*epsilon)
    def value(t):
        return 0.5*(t*np.sqrt(t*t+a0*a0)-a0*a0*np.arcsinh(t/a0))
    return value(w)-value(epsilon)


def background_response(background_gradient, *, a0=1.0):
    """Principal tensor of the actual static equation about a constant field.

    Its transverse and longitudinal eigenvalues are evaluated on the
    specified ambient field. The cubic energy governs the zero-field
    response, while nonzero backgrounds have a positive principal tensor.
    """
    g = np.asarray(background_gradient, float)
    if g.shape != (3,) or not np.all(np.isfinite(g)) or not np.isfinite(a0) or a0 <= 0:
        raise ValueError("finite three-gradient and positive a0 required")
    matrix = flux_jacobian(g, a0)
    magnitude = float(np.linalg.norm(g))
    transverse = magnitude/np.sqrt(magnitude*magnitude+a0*a0)
    longitudinal = transverse + a0*a0*magnitude/(magnitude*magnitude+a0*a0)**1.5
    return {"principal_tensor": matrix, "transverse_eigenvalue": float(transverse),
            "longitudinal_eigenvalue": float(longitudinal),
            "uniformly_elliptic_at_background": magnitude > 0,
            "zero_background_linear_coefficient": 0.0,
            "cosmological_linear_mapping_derived": False}


def covariant_clock_response(acceleration, *, a0=1.0):
    """RMS invariant in the independent-foliation effective action.

    In units c=1 and signature (-+++), take n_mu=-d_mu chi/|d chi|,
    A_mu=n^nu nabla_nu n_mu and
    S=(M_P^2/2) integral sqrt(-g) [R-2 Lambda-2 J(A^2)]+S_m.
    J=2 F-A^2, with F the existing unregularized primitive. Thus
    J_Y=mu-1 and the stationary slow-motion action has exactly F.
    chi is an additional foliation field independent of the matter dust
    clock T. This is an optional macroscopic realization of the local law.

    J(0)=dJ(0)=0 embeds the geodesic-foliation Einstein branch. The
    returned Hessian is a field-space derivative, not a stability claim
    for the constrained time-dependent system. See Blanchet and Marsat,
    Phys. Rev. D 84, 044056 (2011), doi:10.1103/PhysRevD.84.044056.
    """
    g = np.asarray(acceleration, dtype=float)
    if g.shape != (3,) or not np.all(np.isfinite(g)) or not np.isfinite(a0) or a0 <= 0:
        raise ValueError("finite three-acceleration and positive a0 required")
    norm = float(np.linalg.norm(g))
    mu = norm/np.hypot(norm, a0)
    return {"model": "independent-foliation effective action",
            "status": "model_specific_constitutive_identity",
            "J": float(2*primitive(g, a0)-np.dot(g, g)),
            "J_Y": float(mu-1), "gradient_J": 2*(flux(g, a0)-g),
            "hessian_J": 2*(flux_jacobian(g, a0)-np.eye(3)),
            "stationary_flux": flux(g, a0), "a0": float(a0),
            "action": "M_P^2/2 integral sqrt(-g) [R-2 Lambda-2 J(A^2)] + S_m",
            "clock_definition": "n_mu=-partial_mu chi/sqrt(-g^ab partial_a chi partial_b chi)",
            "normalization": "c=1; J=2 F-A^2; M_P^2=1/(8 pi G)",
            "tensor_branch": "Einstein tensor quadratic action on the geodesic foliation"}


def certify_reduced_kinetic(kinetic_matrix, physical_metric, *,
                            normalized_operator_error_bound,
                            action, variation_space, source):
    """Bound the least kinetic eigenvalue of a supplied physical reduction.

    K is the complete symmetric velocity Hessian after constraint
    elimination, and G is a positive physical norm on the same independent
    coordinates. The caller supplies an upper bound epsilon for the
    operator error in the G-normalized representation. That bound includes
    assembly, constraint elimination, omitted directions and numerical
    eigensolution errors whenever those enter the claimed result.

    Weyl's inequality gives lambda_min in [lambda_hat-epsilon,
    lambda_hat+epsilon]. Positivity or a negative direction is concluded
    only when this interval has the corresponding strict sign. This
    routine evaluates the conditional finite-matrix certificate; its
    action, physical variation space and source map are supplied data.
    It does not construct those objects or establish an error bound.
    """
    K, G = (np.asarray(value, float) for value in
            (kinetic_matrix, physical_metric))
    epsilon = float(normalized_operator_error_bound)
    metadata = {"action": action, "variation_space": variation_space,
                "source": source}
    if any(not isinstance(value, str) or not value.strip()
           for value in metadata.values()):
        raise ValueError("action, variation_space and source descriptions are required")
    if (K.ndim != 2 or K.shape[0] == 0 or K.shape[0] != K.shape[1]
            or G.shape != K.shape or not np.isfinite(epsilon) or epsilon < 0
            or not np.all(np.isfinite(K)) or not np.all(np.isfinite(G))):
        raise ValueError("finite square kinetic/metric matrices and nonnegative error bound required")
    for matrix in (K, G):
        if not np.allclose(matrix, matrix.T, rtol=0.,
                           atol=1e-13*np.linalg.norm(matrix, np.inf)):
            raise ValueError("kinetic matrix and physical metric must be symmetric")
    K, G = (0.5*(matrix+matrix.T) for matrix in (K, G))
    try:
        eigenvalues = eigvalsh(K, G)
    except np.linalg.LinAlgError as exc:
        raise ValueError("physical metric must be positive definite") from exc
    minimum = float(eigenvalues[0])
    lower = float(np.nextafter(minimum-epsilon, -np.inf))
    upper = float(np.nextafter(minimum+epsilon, np.inf))
    status = ("positive" if lower > 0 else
              "negative_direction" if upper < 0 else "unresolved")
    return {
        **metadata,
        "status": status,
        "normalized_eigenvalues": eigenvalues,
        "minimum_normalized_coefficient": minimum,
        "minimum_coefficient_interval": [lower, upper],
        "normalized_operator_error_bound": epsilon,
        "bound_source": "caller-supplied total normalized operator and eigensolution error",
        "conditional_on_supplied_operator_bound": True,
        "generation_map_validated": False,
        "complete_gravitational_action_derived": False,
        "operation_counts": {"generalized_eigensystems": 1},
    }


def constrained_clock_kinetic(laplacian, response_operator, generation_map, *,
                              planck_mass_squared):
    """Reduce the independent-foliation action on supplied velocity columns.

    D and L are symmetric positive Dirichlet stiffness matrices on the
    same trial space; B maps the supplied independent coordinates into
    this action's foliation sector, with the other fields fixed. Its
    velocity form is K=2 M^2 B^T(D L^-1 D-D)B.
    Generalized eigenvalues use the gradient metric B^T D B, so a change
    of source coordinates preserves the reported spectrum. One Cholesky
    factorization solves all source columns together.

    The matrices define a finite calculation. Continuum certification
    additionally requires a bound on the assembled forms, the potential
    solve and omitted modes. Physical interpretation of B requires its
    source construction. An invariant-subsystem interpretation also
    requires preservation by this parent evolution.
    A generated action with simultaneous matter and metric variations
    uses its complete constrained Hessian, including their cross terms.
    See Flanagan, Khronometric theories of modified Newtonian dynamics
    (2023), arXiv:2302.14846.
    """
    D, L, B = (np.asarray(value, float) for value in
               (laplacian, response_operator, generation_map))
    if (D.ndim != 2 or D.shape[0] == 0 or D.shape[0] != D.shape[1]
            or L.shape != D.shape or B.ndim != 2 or B.shape[0] != D.shape[0]
            or B.shape[1] == 0 or B.shape[1] > B.shape[0]
            or not all(np.all(np.isfinite(value)) for value in (D, L, B))
            or not np.isfinite(planck_mass_squared) or planck_mass_squared <= 0):
        raise ValueError("finite compatible stiffness/source matrices and positive M^2 required")
    for matrix in (D, L):
        if not np.allclose(matrix, matrix.T, rtol=0., atol=1e-13*np.linalg.norm(matrix, 2)):
            raise ValueError("Dirichlet stiffness matrices must be symmetric")
    D, L = (0.5*(matrix+matrix.T) for matrix in (D, L))
    try:
        cho_factor(D, lower=True)
        factor = cho_factor(L, lower=True)
        DB = D@B
        solved = cho_solve(factor, DB)
        metric = B.T@DB
        metric = 0.5*(metric+metric.T)
        cho_factor(metric, lower=True)
    except np.linalg.LinAlgError as exc:
        raise ValueError("positive stiffnesses and independent source columns required") from exc
    kinetic = 2*planck_mass_squared*(DB.T@solved-metric)
    kinetic = 0.5*(kinetic+kinetic.T)
    eigenvalues = eigvalsh(kinetic, metric)
    residual = L@solved-DB
    return {
        "kinetic_matrix": kinetic,
        "gradient_metric": metric,
        "gradient_normalized_eigenvalues": eigenvalues,
        "potential_velocity_map": B-solved,
        "relative_constraint_residual": float(np.linalg.norm(residual)/np.linalg.norm(DB)),
        "minimum_normalized_coefficient": float(eigenvalues[0]),
        "model": "independent-foliation effective action",
        "diagnostic_target": "supplied foliation velocity columns with other fields fixed",
        "generation_map_validated": False,
        "operation_counts": {"response_factorizations": 1,
                             "positivity_factorizations": 2,
                             "source_right_hand_sides": int(B.shape[1]),
                             "generalized_eigensystems": 1},
        "scope": "independent-foliation model; finite Dirichlet velocity form at leading slow-motion order",
    }


def accelerated_clock_diagnostic():
    """Exact-form benchmarks for the independent-foliation static reduction.

    Sampled accelerations and wavevectors specify mathematical checks,
    not physical boundaries. The threshold follows algebraically from
    the existing RMS law. The radial result retains a varying spherical
    background and regularity at the centre. The reported sign belongs
    to this effective action with the independent foliation varied.
    """
    y_star = np.sqrt((np.sqrt(5.)-1)/2)
    samples = []
    for y in (0.5, 1., np.sqrt(2.), 2.):
        tensor = background_response([y, 0., 0.], a0=1.)["principal_tensor"]
        for direction in ([1., 0., 0.], [0., 1., 0.], [1., 1., 0.]):
            wave = np.asarray(direction)
            k2 = float(wave@wave)
            h = float(wave@tensor@wave/k2)
            reduced = constrained_clock_kinetic([[k2]], [[k2*h]], [[1.]],
                                                planck_mass_squared=1.)
            expected = 2*(1-h)/h
            samples.append({"acceleration_ratio": y, "wavevector": direction,
                            "principal_coefficient": h,
                            "normalized_kinetic_coefficient": float(
                                reduced["gradient_normalized_eigenvalues"][0]),
                            "analytic_coefficient": expected,
                            "absolute_identity_residual": abs(
                                reduced["gradient_normalized_eigenvalues"][0]-expected)})
    s_star = y_star**2/np.sqrt(1+y_star**2)
    return {
        "scope": "independent foliation; static slow-motion scalar velocity form",
        "model": "independent-foliation effective action",
        "status": "negative_longitudinal_direction_in_this_effective_model",
        "diagnostic_target": "independent foliation velocities in the stated accelerated background",
        "operator_identity": "K=2 M^2 B^T(D L^-1 D-D)B",
        "source_condition": "For a realization of this action, B is its supplied source-to-foliation derivative",
        "evolution_condition": "For an invariant-subsystem realization of this independent-foliation parent action: C(Gamma(q))=0; F(Gamma(q))=D Gamma(q) F_gen(q)",
        "parallel_threshold_exact": "sqrt((sqrt(5)-1)/2)",
        "parallel_threshold": float(y_star),
        "spherical_vacuum_flux_at_threshold": float(s_star),
        "spherical_threshold_radius_over_sqrt_GM_over_a0": float(1/np.sqrt(s_star)),
        "radial_velocity_form": "4 pi M^2 integral r^2 (1-lambda)/lambda |d_r sigma_dot|^2 dr",
        "parallel_negative_above_threshold": True,
        "physical_kinetic_positive_all_accelerations": False,
        "generation_mapping": {
            "static_constitutive_response_derived": True,
            "effective_field_content": "independent foliation chi in addition to the matter clock",
            "source_to_foliation_map": None,
            "evolution_preservation_established": False,
        },
        "minimum_kinetic_over_twice_planck_gradient_metric": float(3*np.sqrt(6)/8-1),
        "acceleration_at_minimum_kinetic": float(np.sqrt(2.)),
        "necessary_completion_on_minimum_direction": float(1-3*np.sqrt(6)/8),
        "completion_normalization": "velocity Hessian divided by 2 M^2 times gradient norm squared",
        "completion_interpretation": "required addition only if this action, negative direction and kinetic normalization are retained; it is not a coefficient for a different generated action",
        "finite_gaussian_congruence": "an invertible Gaussian map within the same retained velocity span preserves this model's inertia; an actual generated restriction uses its own image and constraints",
        "samples": samples,
        "maximum_identity_residual": float(max(row["absolute_identity_residual"] for row in samples)),
        "operation_counts": {"response_factorizations": len(samples),
                             "positivity_factorizations": 2*len(samples),
                             "source_right_hand_sides": len(samples),
                             "generalized_eigensystems": len(samples)},
    }


def clock_dust_coefficients(hubble, density, physical_wavenumber, *, planck_mass_squared=1.):
    """Independent-foliation scalar coefficients on a dust/vacuum background.

    The background obeys 3 M^2 H^2=rho+rho_Lambda and
    -2 M^2 Hdot=rho, with constant radial condensate. In spatially flat
    gauge write the matter clock T=t+pi and independent foliation
    clock chi=t+sigma. Eliminating the shift gives lapse n=B*pi.
    The exact quadratic first-order scalar density, divided by a^3, is
    p*(pidot-B*pi)-D*pi^2/2+C*(sigmadot-B*pi)^2/2.
    Its conserved foliation momentum is q=a^3*C*(sigmadot-B*pi).

    With P=a^3*p the canonical transformation R=P+q, zeta_chi=sigma-pi
    preserves P*dpi+q*dsigma=R*dpi+q*d(zeta_chi). Its Hamiltonian is
    B*R*pi+a^3*D*pi^2/2+q^2/(2*a^3*C). Setting r=R/a^3 and
    eliminating pi gives [rdot+(3H+B)r]^2/(2D)+C*zeta_chidot^2/2.
    Thus the physical velocity form in (r,zeta_chi) is positive for D,C>0.
    The effective cold density perturbation is r=p+q/a^3. Its dynamics
    is the Einstein cold mode; the additional clock momentum is
    conserved and has zero spatial restoring term at this order.
    """
    values = (hubble, density, physical_wavenumber, planck_mass_squared)
    if (not all(np.isfinite(x) for x in values) or hubble == 0
            or min(density, physical_wavenumber, planck_mass_squared) <= 0):
        raise ValueError("nonzero finite H and positive density, wavenumber and Planck coefficient required")
    B = density/(2*planck_mass_squared*hubble)
    C = 2*planck_mass_squared*physical_wavenumber**2
    D = density*physical_wavenumber**2+3*density**2/(2*planck_mass_squared)
    kinetic = np.diag([1/D, C])
    return {"model": "independent-foliation effective action",
            "status": "positive_scalar_kinetics_on_stated_dust_vacuum_background",
            "B": B, "C": C, "D": D,
            "physical_scalar_kinetic_matrix": kinetic,
            "physical_scalar_kinetic_eigenvalues": np.array(sorted((1/D, C))),
            "physical_scalar_kinetic_positive": True,
            "canonical_coordinates": ("r=p+q/a^3", "zeta_chi=sigma-pi"),
            "hamiltonian": "B R pi+a^3 D pi^2/2+q^2/(2 a^3 C), R=a^3 r",
            "clock_spatial_restoring_coefficient": 0.,
            "zero_charge_cold_kinetic_coefficient": 1/D,
            "zero_charge_radial_kinetic_coefficient": 1.,
            "zero_charge_branch": "q=0; Einstein-radial-dust scalar equations",
            "charge_density": "q/a^3",
            "scope": "independent-foliation quadratic scalar action at constant radial condensate; nonzero Fourier mode"}


def evolve_clock_dust_mode(initial, times, *, background, comoving_wavenumber,
                          planck_mass_squared=1., charge=0., rtol=1e-10, atol=1e-12):
    """Finite mode of the independent-foliation action on supplied FLRW data.

    initial=(p,pi,sigma). background(t) returns (a,H,rho,Hdot,rhodot);
    its dust/vacuum constraints are checked at every requested stage.
    The first-order equations use the conserved charge directly.
    The effective cold density r=p+q/a^3 obeys the Einstein cold
    equations for any charge; q=0 is an exact invariant branch.
    This finite linear calculation keeps its foliation initial data;
    selecting a stationary accelerated local foliation is additional
    boundary data, rather than an output of this mode evolution.
    """
    from scipy.integrate import solve_ivp
    initial, times = np.asarray(initial, float), np.asarray(times, float)
    if (initial.shape != (3,) or not np.all(np.isfinite(initial))
            or times.ndim != 1 or len(times) < 2 or not np.all(np.isfinite(times))
            or np.any(np.diff(times) <= 0) or not np.isfinite(charge)
            or not all(np.isfinite(x) and x > 0 for x in
                       (comoving_wavenumber, planck_mass_squared, rtol, atol))):
        raise ValueError("finite three-state, increasing time grid and positive scales/tolerances required")
    work = {"rhs_evaluations": 0, "background_evaluations": 0}
    constraints = {"raychaudhuri_relative_residual": 0., "continuity_relative_residual": 0.}
    def coefficients(time):
        work["background_evaluations"] += 1
        a, H, rho, Hdot, rhodot = map(float, background(time))
        if not all(np.isfinite(x) for x in (a, H, rho, Hdot, rhodot)) or a <= 0:
            raise ValueError("finite positive-scale-factor background required")
        data = clock_dust_coefficients(H, rho, comoving_wavenumber/a,
                                      planck_mass_squared=planck_mass_squared)
        ray = abs(2*planck_mass_squared*Hdot+rho)/rho
        continuity = abs(rhodot+3*H*rho)/(abs(rhodot)+abs(3*H*rho))
        constraints["raychaudhuri_relative_residual"] = max(constraints["raychaudhuri_relative_residual"], ray)
        constraints["continuity_relative_residual"] = max(constraints["continuity_relative_residual"], continuity)
        if max(ray, continuity) > 1e-9:
            raise ValueError("background must obey Einstein dust/vacuum constraints")
        return a, H, rho, data
    def rhs(time, state):
        work["rhs_evaluations"] += 1
        a, H, rho, data = coefficients(time)
        p, pi, sigma = state
        B, C, D = data["B"], data["C"], data["D"]
        return (-(3*H+B)*p-D*pi-B*charge/a**3,
                B*pi, B*pi+charge/(a**3*C))
    result = solve_ivp(rhs, (times[0], times[-1]), initial, t_eval=times,
                       method="DOP853", rtol=rtol, atol=atol)
    if not result.success:
        raise ArithmeticError("clock/dust evolution failed: "+result.message)
    fields = [coefficients(time) for time in times]
    a = np.array([row[0] for row in fields])
    rho = np.array([row[2] for row in fields])
    lapse = np.array([row[3]["B"] for row in fields])*result.y[1]
    r = result.y[0]+charge/a**3
    kinetic = np.array([[1/row[3]["D"], row[3]["C"]] for row in fields])
    return {"times": times, "p": result.y[0], "dust_clock": result.y[1],
            "foliation_clock": result.y[2], "relative_clock": result.y[2]-result.y[1],
            "effective_cold_density_perturbation": r,
            "density_contrast_flat_gauge": r/rho,
            "bare_cold_density_contrast_flat_gauge": result.y[0]/rho,
            "lapse": lapse, "scale_factor": a, "conserved_charge": float(charge),
            "foliation_density": charge/a**3, "physical_kinetic_coefficients": kinetic,
            "zero_charge_branch": charge == 0., "background_constraints": constraints,
            "operation_counts": work,
            "scope": "finite linear Einstein-dust/vacuum mode with the independent covariant foliation field"}


def evaluate_covariant_clock():
    """Independent-foliation model checks in a JSON-native calculation record.

    Three Einstein--de Sitter evolutions compare the solver with exact
    solutions and compare two partitions of one effective cold source.
    The work record counts actual ODE and background evaluations; the
    sampled error is a numerical check rather than an interval bound.
    """
    def background(time):
        return (time**(2/3), 2/(3*time), 4/(3*time*time),
                -2/(3*time*time), -8/(3*time**3))

    times = np.linspace(1., 3., 25)
    k, pi0, sigma0 = 4., .003, -.002
    configurations = ((-.01, 0.), (-.01, .007), (-.017, .007))
    runs, checks = [], []
    for p0, charge in configurations:
        run = evolve_clock_dust_mode(
            (p0, pi0, sigma0), times, background=background,
            comoving_wavenumber=k, charge=charge)
        constant = p0+4*pi0*k*k/5+8*pi0/3+charge
        p_exact = (constant/times**3-4*pi0*k*k/5/times**(4/3)
                   -(8*pi0/3+charge)/times**2)
        pi_exact = pi0*times
        sigma_exact = sigma0+pi0*(times-1)+3*charge/(2*k*k)*(times**(1/3)-1)
        runs.append(run)
        checks.append({
            "initial_state": [p0, pi0, sigma0], "charge": charge,
            "max_abs_p_error": float(np.max(np.abs(run["p"]-p_exact))),
            "max_abs_dust_clock_error": float(np.max(np.abs(run["dust_clock"]-pi_exact))),
            "max_abs_foliation_clock_error": float(np.max(np.abs(run["foliation_clock"]-sigma_exact))),
            "final_state": [float(run[key][-1]) for key in
                            ("p", "dust_clock", "foliation_clock")],
            "background_constraints": run["background_constraints"],
            "operation_counts": run["operation_counts"],
        })

    representative = []
    for H, rho, physical_k in ((1., 3., 10.), (1., .3, 2.)):
        data = clock_dust_coefficients(H, rho, physical_k)
        representative.append({
            "H": H, "rho": rho, "physical_wavenumber": physical_k,
            "B": float(data["B"]), "C": float(data["C"]), "D": float(data["D"]),
            "physical_scalar_kinetic_matrix": data["physical_scalar_kinetic_matrix"].tolist(),
            "clock_spatial_restoring_coefficient": 0.,
        })
    comparison = {
        "initial_effective_density": -.01,
        "charges": [0., .007],
        "max_abs_effective_density_difference": float(np.max(np.abs(
            runs[0]["effective_cold_density_perturbation"]
            -runs[2]["effective_cold_density_perturbation"]))),
        "max_abs_lapse_difference": float(np.max(np.abs(runs[0]["lapse"]-runs[2]["lapse"]))),
        "final_effective_density": [float(run["effective_cold_density_perturbation"][-1])
                                    for run in (runs[0], runs[2])],
    }
    return {
        "model": "independent-foliation effective action",
        "status": "model_equations_evaluated_on_two_background_classes",
        "verification_target": "analytic identities and numerical evolution within this effective realization",
        "action": "M_P^2/2 integral sqrt(-g) [R-2 Lambda-2 J(A^2)] + S_m",
        "acceleration_invariant": "J(Y)=2 F(sqrt(Y))-Y; J_Y=mu-1",
        "foliation": "independent timelike clock chi; a0 constant",
        "canonical_coordinates": ["r=p+q/a^3", "zeta_chi=sigma-pi"],
        "scope": "separate constrained reductions: flat Einstein dust/vacuum Fourier modes and accelerated static scalar velocities",
        "planck_mass_squared": 1.,
        "representative_coefficients": representative,
        "eds_background": "a=t^(2/3), H=2/(3t), rho=4/(3t^2)",
        "time_interval": [1., 3.], "sample_count_per_evolution": int(len(times)),
        "comoving_wavenumber": k, "solver_rtol": 1e-10, "solver_atol": 1e-12,
        "analytic_solution_checks": checks,
        "equal_effective_source_comparison": comparison,
        "accelerated_static_kinetics": accelerated_clock_diagnostic(),
        "operation_counts": {
            "mode_evolutions": len(runs), "state_dimension": 3,
            "rhs_evaluations": sum(run["operation_counts"]["rhs_evaluations"] for run in runs),
            "background_evaluations": sum(run["operation_counts"]["background_evaluations"] for run in runs),
            "sampled_mode_states": len(runs)*len(times),
            "additional_representative_coefficient_evaluations": len(representative),
        },
    }


def box_mesh(n, lengths=(1., 1., 1.)):
    lengths = np.asarray(lengths, float)
    if (not isinstance(n, int) or isinstance(n, bool) or n < 2
            or lengths.shape != (3,) or not np.all(np.isfinite(lengths))
            or np.any(lengths <= 0)):
        raise ValueError("integer n>=2 and three finite positive side lengths required")
    nodes = np.array(list(product(*(np.linspace(0, L, n+1) for L in lengths))))
    index = np.arange((n+1)**3).reshape((n+1,)*3)
    cells = []
    for q in product(range(n), repeat=3):
        for order in permutations(range(3)):
            p = np.array(q); ids = [index[tuple(p)]]
            for d in order:
                p = p.copy(); p[d] += 1; ids.append(index[tuple(p)])
            cells.append(ids)
    cells = np.asarray(cells)
    xyz = nodes[cells]
    affine = np.concatenate((np.ones((*xyz.shape[:2], 1)), xyz), axis=2)
    inv = np.linalg.inv(affine)
    gradients = inv[:, 1:, :]
    volume = np.abs(np.linalg.det(xyz[:, 1:, :]-xyz[:, :1, :]))/6
    rows = np.repeat(np.arange(len(cells)), 4)
    B = [coo_matrix((gradients[:, d, :].ravel(), (rows, cells.ravel())),
                    shape=(len(cells), len(nodes))).tocsr() for d in range(3)]
    boundary = np.any((nodes == 0) | (nodes == np.asarray(lengths)), axis=1)
    return nodes, cells, B, volume, boundary


def solve_dirichlet(source, boundary_value, *, n=8, lengths=(1., 1., 1.),
                    a0=1.0, epsilon=0.0, tolerance=1e-10, max_iterations=80):
    """Return Phi, nonlinear weak residual, reaction flux and discretization.

    source(nodes), boundary_value(nodes) must return finite arrays of length
    node count. source is f itself, not density without the 4*pi*G factor.
    Errors cause failure; no unconverged solution is labelled converged.
    """
    if not np.isfinite(a0) or a0 <= 0 or not np.isfinite(epsilon) or epsilon < 0:
        raise ValueError("a0>0 and epsilon>=0 required")
    if (not np.isfinite(tolerance) or tolerance <= 0
            or not isinstance(max_iterations, int) or isinstance(max_iterations, bool)
            or max_iterations < 0):
        raise ValueError("finite positive tolerance and nonnegative integer max_iterations required")
    nodes, cells, B, volume, boundary = box_mesh(n, lengths)
    f, phi = np.asarray(source(nodes), float), np.asarray(boundary_value(nodes), float).copy()
    if f.shape != (len(nodes),) or phi.shape != f.shape or not np.all(np.isfinite(f+phi)):
        raise ValueError("source and boundary must be finite nodal arrays")
    free = np.flatnonzero(~boundary)
    # Consistent P1 tetrahedron mass matrix: V/20*(I+ones).
    load = np.zeros(len(nodes))
    local_load = volume[:, None]*(f[cells]+f[cells].sum(axis=1)[:, None])/20
    np.add.at(load, cells.ravel(), local_load.ravel())
    def evaluate(v):
        g = np.stack([b@v for b in B], axis=1)
        j = flux(g, a0, epsilon)
        residual = load + sum(b.T@(volume*j[:, d]) for d, b in enumerate(B))
        energy = np.dot(volume, primitive(g, a0, epsilon))+np.dot(load, v)
        return energy, residual, g
    for iteration in range(max_iterations+1):
        energy, residual, g = evaluate(phi)
        norm = np.max(np.abs(residual[free])) if len(free) else 0.
        if norm <= tolerance:
            break
        if iteration == max_iterations:
            raise RuntimeError(f"local solve failed: weak residual {norm:g}")
        D = flux_jacobian(g, a0, epsilon)
        H = sum(B[i].T@diags(volume*D[:, i, j])@B[j] for i in range(3) for j in range(3)).tocsr()
        Hf = H[free][:, free]
        # At a wholly zero initial field the unregularized Hessian vanishes.
        # A damping diagonal changes only the step, never the equation.
        damp = max(1e-14, 1e-10*np.max(np.abs(Hf.diagonal()), initial=0))
        step = spsolve(Hf+diags(np.full(len(free), damp)), -residual[free])
        if not np.all(np.isfinite(step)):
            raise RuntimeError("nonfinite Newton step")
        descent = np.dot(residual[free], step)
        alpha = 1.
        for _ in range(55):
            trial = phi.copy(); trial[free] += alpha*step
            if evaluate(trial)[0] <= energy+1e-4*alpha*descent:
                phi = trial; break
            alpha *= .5
        else:
            raise RuntimeError("local Newton line search failed")
    return {"nodes": nodes, "phi": phi, "cells": cells,
            "gradient": g, "weak_residual_inf": float(norm),
            "cell_volumes": volume,
            "source_load": load, "boundary_nodes": boundary,
            "boundary_flux": float(residual[boundary].sum()),
            "source_integral": float(load.sum()),
            "flux_balance_residual": float(residual[boundary].sum()-load.sum()),
            "iterations": iteration, "n": n, "epsilon": epsilon, "a0": a0,
            "converged": True, "cosmological_source_map": False}


def local_source_decomposition(solution, *, a0=None, epsilon=None):
    """Integrated P1 source identity using weak densities on the same mesh.

    Returns discrete loads for div grad(Phi), div F and their difference.
    Boundary reactions fix the total flux; interior nodal loads are not
    pointwise densities. No homogeneous dark density is supplied.
    """
    for name, supplied in (("a0", a0), ("epsilon", epsilon)):
        if supplied is not None and supplied != solution[name]:
            raise ValueError(f"{name} must match the solved response")
    a0, epsilon = solution["a0"], solution["epsilon"]
    nodes, cells = solution["nodes"], solution["cells"]
    xyz = nodes[cells]
    inv = np.linalg.inv(np.concatenate((np.ones((*xyz.shape[:2], 1)), xyz), axis=2))
    basis_gradients = inv[:, 1:, :]
    volume = np.abs(np.linalg.det(xyz[:, 1:]-xyz[:, :1]))/6
    gradient = np.einsum("edi,ei->ed", basis_gradients, solution["phi"][cells])
    linear, nonlinear = np.zeros(len(nodes)), np.zeros(len(nodes))
    for result, vector in ((linear, gradient), (nonlinear, flux(gradient, a0, epsilon))):
        element = -volume[:, None]*np.einsum("edi,ed->ei", basis_gradients, vector)
        np.add.at(result, cells.ravel(), element.ravel())
    return {"linear_divergence_load": linear,
            "source_divergence_load": nonlinear,
            "polarization_divergence_load": linear-nonlinear,
            "interior_source_residual": float(np.max(np.abs(
                (nonlinear-solution["source_load"])[~solution["boundary_nodes"]]), initial=0.0)),
            "identity_residual": float(np.max(np.abs(linear-(nonlinear+linear-nonlinear)))),
            "density_normalization": "divide loads by 4*pi*G and an explicit mass-matrix rule",
            "average_requires_boundary_flux": True}


def gaussian_disk_source(*, mass, radial_width, vertical_width,
                         centre=(0.5, 0.5, 0.5), four_pi_G=1.0):
    """Smooth finite-thickness axisymmetric source with whole-space mass M.

    A finite box contains only its integrated fraction. The boundary data
    and any homogeneous/cold free source must be supplied independently.
    """
    if (not all(np.isfinite(x) for x in (mass, radial_width, vertical_width, four_pi_G))
            or mass < 0 or min(radial_width, vertical_width, four_pi_G) <= 0):
        raise ValueError("nonnegative mass and positive finite widths/coupling required")
    centre = np.asarray(centre, float)
    if centre.shape != (3,) or not np.all(np.isfinite(centre)):
        raise ValueError("finite disk centre required")
    norm = mass/((2*np.pi)**1.5*radial_width**2*vertical_width)
    def source(nodes):
        r = np.asarray(nodes)-centre
        return four_pi_G*norm*np.exp(-0.5*((r[:, 0]**2+r[:, 1]**2)/radial_width**2
                                                   +r[:, 2]**2/vertical_width**2))
    return source


def _plane_inverse_flux(current, a0):
    """Inverse of the unregularized signed one-dimensional constitutive law."""
    current = np.asarray(current, float)
    magnitude = np.abs(current)
    return np.sign(current)*np.sqrt(magnitude)*np.sqrt(
        (magnitude+np.hypot(magnitude, 2*a0))/2)


def _plane_legendre(current, a0):
    """H(j)=g*j-F(g), evaluated stably through the zero-gradient point."""
    g = _plane_inverse_flux(current, a0)
    x = np.abs(g)/a0
    answer = g*np.asarray(current)-primitive(g[..., None], a0)
    small = x < .01
    series = a0*a0*x**3*(2/3+x*x*(-2/5+x*x*(9/28-5*x*x/18)))
    return np.where(small, series, answer)


@lru_cache(maxsize=8)
def _plane_quadrature(order):
    nodes, weights = np.polynomial.legendre.leggauss(order)
    nodes.setflags(write=False)
    weights.setflags(write=False)
    return nodes, weights


def plane_source_state(positions, cell_masses, *, a0=1., four_pi_G=1.,
                       boundary_values=(0., 0.), quadrature_order=24,
                       field_tolerance=1e-13):
    """Nonlinear plane field for a finite material mesh, per unit area.

    The fixed end nodes bound a physical interval. Each cell carries a
    constant mass and a uniform density; its material map is affine.
    Thus j(x)=C+four_pi_G*integral_left^x rho is the exact flux, and one
    scalar boundary integral determines C. Gauss integration evaluates
    the cell energies after j=sign(t)*t^2 removes the central square-root
    singularity. No flux regularization or cosmological Poisson force is
    used. The returned force evaluates the variation of this finite action
    to the stated field tolerance and cell-quadrature accuracy.
    """
    from scipy.optimize import brentq
    x, masses = np.asarray(positions, float), np.asarray(cell_masses, float)
    boundary = np.asarray(boundary_values, float)
    if (x.ndim != 1 or masses.ndim != 1 or len(x) != len(masses)+1
            or len(masses) < 2 or not np.isfinite(x).all()
            or not np.isfinite(masses).all() or np.any(masses <= 0)):
        raise ValueError("finite ordered nodes and at least two positive cell masses required")
    lengths = np.diff(x)
    if np.any(lengths <= 0):
        raise ValueError("material cell crossing: positive cell lengths required")
    if boundary.shape != (2,) or not np.isfinite(boundary).all():
        raise ValueError("two finite Dirichlet values required")
    if not all(np.isfinite(v) and v > 0 for v in (a0, four_pi_G, field_tolerance)):
        raise ValueError("positive finite acceleration, coupling and field tolerance required")
    if (not isinstance(quadrature_order, int) or isinstance(quadrature_order, bool)
            or quadrature_order < 8):
        raise ValueError("integer quadrature order at least eight required")
    increments = four_pi_G*masses
    cumulative = np.r_[0., np.cumsum(increments)]
    jump = float(boundary[1]-boundary[0])
    target_gradient = jump/float(x[-1]-x[0])
    target_flux = float(flux(np.array([target_gradient]), a0)[0])
    root_calls = 0
    def boundary_residual(offset):
        nonlocal root_calls
        root_calls += 1
        h = _plane_legendre(offset+cumulative, a0)
        return float(np.dot(lengths, np.diff(h)/increments)-jump)
    offset = brentq(boundary_residual, target_flux-cumulative[-1], target_flux,
                    xtol=field_tolerance*max(a0, cumulative[-1], abs(target_flux)),
                    rtol=4*np.finfo(float).eps)
    currents = offset+cumulative
    h = _plane_legendre(currents, a0)
    average_gradient = np.diff(h)/increments
    potentials = boundary[0]+np.r_[0., np.cumsum(lengths*average_gradient)]

    # Primitive in current space: integral_0^j H(s) ds. The change s=+/-t^2
    # makes the integrands smooth on each half-axis, including j=0.
    q, weights = _plane_quadrature(quadrature_order)
    tmax = np.sqrt(np.abs(currents))
    t = tmax[:, None]*(q+1)/2
    magnitude = t*t
    quadrature_h = _plane_legendre(magnitude, a0)
    integral_h = np.sign(currents)*tmax*np.sum(weights*t*quadrature_h, axis=1)
    average_h = np.diff(integral_h)/increments
    gradient = _plane_inverse_flux(magnitude, a0)
    # F=g*j-H is algebraically the same convex primitive and avoids
    # cancellation in F near zero. Source and field energies are summed
    # separately below and compared with the integration-by-parts form.
    f = gradient*magnitude-quadrature_h
    integral_f = np.sign(currents)*tmax*np.sum(weights*t*f, axis=1)
    average_f = np.diff(integral_f)/increments
    field_energy = float(np.dot(lengths, average_f)/four_pi_G)
    source_energy = float(np.dot(masses, potentials[:-1])
        +np.dot(lengths, average_h-h[:-1])/four_pi_G)
    potential_energy = source_energy+field_energy
    reduced_energy = float((boundary[1]*currents[-1]-boundary[0]*currents[0]
                            -np.dot(lengths, average_h))/four_pi_G)
    force = (average_h[:-1]-average_h[1:])/four_pi_G
    return {"positions": x.copy(), "cell_masses": masses.copy(),
            "cell_density": masses/lengths, "potential_nodes": potentials,
            "flux_nodes": currents, "gradient_nodes": _plane_inverse_flux(currents, a0),
            "generalized_force": force, "source_energy": source_energy,
            "field_energy": field_energy, "potential_energy": potential_energy,
            "energy_identity_residual": abs(potential_energy-reduced_energy),
            "boundary_residual": abs(float(potentials[-1]-boundary[1])),
            "mass": float(masses.sum()), "minimum_cell_length": float(lengths.min()),
            "field_root_evaluations": root_calls,
            "field_quadrature_points": int((len(masses)+1)*quadrature_order),
            "field_equation": "d_x[mu(abs(d_x Phi)/a0)*d_x Phi]=four_pi_G*rho",
            "spatial_model": "affine material cells with positive piecewise constant density"}


def evolve_plane_source(positions, cell_masses, initial_velocity, *, duration,
                        steps, a0=1., four_pi_G=1., boundary=None,
                        boundary_rate=None, quadrature_order=24):
    """Variational plane dust with its own nonlinear local potential.

    Endpoints remain fixed and carry zero velocity. Interior trajectories
    use the constant consistent material mass matrix and velocity Verlet.
    The supplied Dirichlet values and time derivatives define boundary
    work; both callbacks are required for time-dependent boundary data.
    The calculation stops on a nonpositive cell length. It computes the
    finite action before cell crossing; it is not a continuum-convergence
    certificate. Mass, energy, boundary work and operation counts are
    returned with the complete finite trajectory.
    """
    from scipy.linalg import cho_factor, cho_solve
    if (not np.isfinite(duration) or duration <= 0 or not isinstance(steps, int)
            or isinstance(steps, bool) or steps < 1):
        raise ValueError("positive finite duration and positive integer step count required")
    if (boundary is None) != (boundary_rate is None):
        raise ValueError("supply both boundary values and their time derivative")
    if boundary is None:
        boundary = lambda time: (0., 0.)
        boundary_rate = lambda time: (0., 0.)
    x = np.asarray(positions, float).copy()
    masses = np.asarray(cell_masses, float)
    velocity = np.asarray(initial_velocity, float).copy()
    state = plane_source_state(x, masses, a0=a0, four_pi_G=four_pi_G,
        boundary_values=boundary(0.), quadrature_order=quadrature_order)
    if (velocity.shape != x.shape or not np.isfinite(velocity).all()
            or velocity[0] != 0 or velocity[-1] != 0):
        raise ValueError("finite nodal velocities with fixed zero-velocity endpoints required")
    count = len(masses)
    matrix = np.zeros((count+1, count+1))
    for i, mass in enumerate(masses):
        matrix[i:i+2, i:i+2] += mass*np.array([[2., 1.], [1., 2.]])/6
    interior_matrix = matrix[1:-1, 1:-1]
    factor = cho_factor(interior_matrix)
    def acceleration(s):
        return cho_solve(factor, s['generalized_force'])
    def power(time, s):
        rates = np.asarray(boundary_rate(time), float)
        if rates.shape != (2,) or not np.isfinite(rates).all():
            raise ValueError("two finite boundary time derivatives required")
        return float((rates[1]*s['flux_nodes'][-1]-rates[0]*s['flux_nodes'][0])/four_pi_G)
    def kinetic(v):
        return float(v@matrix@v/2)
    dt = duration/steps
    times, positions_record, velocities_record = [0.], [x.copy()], [velocity.copy()]
    energies = [kinetic(velocity)+state['potential_energy']]
    source_energies, field_energies = [state['source_energy']], [state['field_energy']]
    work, balance = [0.], [0.]
    boundary_power = power(0., state)
    a = acceleration(state)
    root_evaluations = state['field_root_evaluations']
    quadrature_points = state['field_quadrature_points']
    max_boundary = state['boundary_residual']
    max_identity = state['energy_identity_residual']
    minimum_length = state['minimum_cell_length']
    for step in range(1, steps+1):
        half_velocity = velocity.copy()
        half_velocity[1:-1] += .5*dt*a
        x[1:-1] += dt*half_velocity[1:-1]
        time = step*dt
        state = plane_source_state(x, masses, a0=a0, four_pi_G=four_pi_G,
            boundary_values=boundary(time), quadrature_order=quadrature_order)
        a = acceleration(state)
        velocity = half_velocity
        velocity[1:-1] += .5*dt*a
        new_power = power(time, state)
        work.append(work[-1]+dt*(boundary_power+new_power)/2)
        boundary_power = new_power
        energies.append(kinetic(velocity)+state['potential_energy'])
        source_energies.append(state['source_energy'])
        field_energies.append(state['field_energy'])
        balance.append(energies[-1]-energies[0]-work[-1])
        times.append(time); positions_record.append(x.copy()); velocities_record.append(velocity.copy())
        root_evaluations += state['field_root_evaluations']
        quadrature_points += state['field_quadrature_points']
        max_boundary = max(max_boundary, state['boundary_residual'])
        max_identity = max(max_identity, state['energy_identity_residual'])
        minimum_length = min(minimum_length, state['minimum_cell_length'])
    return {"scope": "finite variational plane dust coupled to the nonlinear local field",
            "time": np.asarray(times), "positions": np.asarray(positions_record),
            "velocities": np.asarray(velocities_record), "total_energy": np.asarray(energies),
            "source_energy": np.asarray(source_energies), "field_energy": np.asarray(field_energies),
            "boundary_work": np.asarray(work), "energy_balance": np.asarray(balance),
            "maximum_energy_balance_residual": float(np.max(np.abs(balance))),
            "energy_identity_residual": max_identity, "boundary_residual": max_boundary,
            "cell_masses": masses.copy(), "final_density": state['cell_density'],
            "mass": state['mass'], "mass_conservation_residual": float(abs(
                np.dot(state['cell_density'], np.diff(x))-masses.sum())),
            "minimum_cell_length": minimum_length, "time_step": dt,
            "a0": a0, "four_pi_G": four_pi_G, "quadrature_order": quadrature_order,
            "operation_counts": {"time_steps": steps, "field_solves": steps+1,
                "force_evaluations": steps+1, "field_root_evaluations": root_evaluations,
                "field_quadrature_points": quadrature_points, "material_cells": count,
                "mass_matrix_order": count-1, "mass_matrix_factorizations": 1},
            "spatial_model": state['spatial_model'],
            "energy_convention": "kinetic + source + nonlinear field; boundary work integrated separately"}
