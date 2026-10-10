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

"""Macroscopic tensor response from one covariant Einstein--matter action.

The dimensionless field Phi couples as g Phi_{mu nu} T^{mu nu}. Its
Fierz--Pauli kinetic coefficient is Z>0. The physical helicity space has
two components with inverse covariance Z Q^2 and residue g^2/Z.
The common Einstein--matter action is an effective input; its quadratic
part fixes these coefficients. Its classical nonlinear Ward identities
are evaluated in nonlinear_tensor. The FLRW operator and stationary
normalization below are limits of this same collective-field action.
"""
from __future__ import annotations

from fractions import Fraction
import math
import sys
from pathlib import Path
import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from cg_core.source_response import certify_affine_residue


def _positive(value, name):
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")
    return float(value)


def _tensor(value):
    a = np.asarray(value, dtype=float)
    if a.shape != (4, 4) or not np.all(np.isfinite(a)):
        raise ValueError("a finite four-dimensional tensor is required")
    if not np.allclose(a, a.T, rtol=0., atol=1e-12*np.max(np.abs(a), initial=1.)):
        raise ValueError("the tensor must be symmetric")
    return a


def fp_operator(momentum, field):
    """Euclidean continuation of the linear Einstein kinetic operator.

    E(h)=Q^2 h-Q tensor (h Q)-(h Q) tensor Q+Q tensor Q tr(h)
         +I [Q.h.Q-Q^2 tr(h)]. E annihilates pure gauge fields and is
    transverse. On transverse traceless fields E=Q^2 h. Positivity is
    imposed on the reduced helicity space, not on conformal gauge fields.
    """
    q, h = np.asarray(momentum, float), _tensor(field)
    if q.shape != (4,) or not np.all(np.isfinite(q)):
        raise ValueError("a finite four-momentum is required")
    q2, v, trace = float(q@q), h@q, float(np.trace(h))
    return (q2*h-np.outer(q, v)-np.outer(v, q)+np.outer(q, q)*trace
            +np.eye(4)*(float(q@v)-q2*trace))


def conserved_exchange(momentum, left, right, *, kinetic, coupling=1.):
    """g^2 (T:U-tr(T)tr(U)/2)/(Z Q^2) for conserved Euclidean sources."""
    z = _positive(kinetic, "kinetic coefficient")
    q, t, u = np.asarray(momentum, float), _tensor(left), _tensor(right)
    if q.shape != (4,) or not np.all(np.isfinite(q)) or q@q <= 0:
        raise ValueError("a nonzero finite Euclidean four-momentum is required")
    if not math.isfinite(coupling):
        raise ValueError("the coupling must be finite")
    for source in (t, u):
        scale = np.linalg.norm(q)*np.linalg.norm(source)
        if np.linalg.norm(source@q) > 1e-12*scale:
            raise ValueError("the source must be conserved at this momentum")
    numerator = np.sum(t*u)-.5*np.trace(t)*np.trace(u)
    return float(coupling**2*numerator/(z*(q@q)))


def physical_polarizations(direction):
    """Two unit-norm spatial TT polarizations for a propagation direction."""
    n = np.asarray(direction, float)
    if n.shape != (3,) or not np.all(np.isfinite(n)) or np.linalg.norm(n) == 0:
        raise ValueError("a finite nonzero spatial direction is required")
    n = n/np.linalg.norm(n)
    axis = np.eye(3)[int(np.argmin(np.abs(n)))]
    a = axis-n*(axis@n)
    a = a/np.linalg.norm(a)
    b = np.cross(n, a)
    return np.asarray([(np.outer(a, a)-np.outer(b, b))/math.sqrt(2),
                       (np.outer(a, b)+np.outer(b, a))/math.sqrt(2)])


def helicity_reflection_gram(times, sources, spatial_momentum, *, kinetic,
                            coupling=1.):
    """Positive-time Gram matrix of the two physical massless modes.

    At |p|>0, C(t,p)=g^2 exp(-|p||t|) I_2/(2 Z |p|).
    The massless p=0 distribution is handled by spatial test-function
    smearing; this pointwise interface uses strictly positive |p|.
    """
    z, p = _positive(kinetic, "kinetic coefficient"), _positive(spatial_momentum, "momentum")
    t, s = np.asarray(times, float), np.asarray(sources, complex)
    if (t.ndim != 1 or s.shape != (len(t), 2) or np.any(t < 0)
            or not np.all(np.isfinite(t)) or not np.all(np.isfinite(s))
            or not math.isfinite(coupling)):
        raise ValueError("finite nonnegative times and two-component sources are required")
    vectors = coupling*np.exp(-p*t[:, None])*s/math.sqrt(2*z*p)
    return vectors.conj()@vectors.T


def exact_helicity_certificate(kinetic, coupling=1):
    """Exact two-mode residue for the specified quadratic gauge action."""
    if isinstance(kinetic, (bool, float)) or isinstance(coupling, (bool, float)):
        raise TypeError("use exact integers, fractions or rational strings")
    z, g = Fraction(kinetic), Fraction(coupling)
    if z <= 0:
        raise ValueError("the kinetic coefficient must be positive")
    certificate = certify_affine_residue([[0, 0], [0, 0]], [[z, 0], [0, z]],
                                         [[g, 0], [0, g]])
    return {"scope": "flat-background quadratic macroscopic tensor response",
            "physical_variable": "external Euclidean Q^2 on a fixed background",
            "physical_helicities": [-2, 2],
            "mass_term": "zero by the declared local linear gauge symmetry",
            "kinetic_coefficient": str(z), "source_coupling": str(g),
            "residue": [[str(v) for v in row] for row in certificate["residue"]],
            "spectral_measure": "(g^2/Z) I_2 delta(s)",
            "exact_zero_certified": certificate["exact_zero_certified"],
            "visible_rank": certificate["visible_rank"],
            "free_external_pole_established": certificate["algebraic_pole_established"],
            "physical_description": "two effective helicity excitations of the macroscopic collective tensor",
            "certificate_order": "quadratic action; nonlinear completion has a separate action proof"}


def flrw_tensor_coefficients(scale_factor, hubble, hubble_dot,
                             comoving_momentum, *, kinetic, coupling=1.):
    """Tensor operator on a flat FLRW solution of the common action.

    Unit-norm polarizations use h_lambda=2*g*Phi_lambda and M_star^2=Z/g^2.
    S_T=(Z/2) integral a^3 [dot(Phi)^2-a^-2 grad(Phi)^2]
        +g integral a^3 Phi*Pi, where Pi is physical TT anisotropic stress.
    The background must obey its Einstein--matter equations. These are
    the metric-sector coefficients; dynamical matter anisotropic stress
    is supplied by the same matter action, not integrated out here.
    """
    a = _positive(scale_factor, "scale factor")
    z = _positive(kinetic, "kinetic coefficient")
    if not all(math.isfinite(v) for v in
               (hubble, hubble_dot, comoving_momentum, coupling)):
        raise ValueError("finite background, momentum and coupling are required")
    if comoving_momentum < 0 or coupling == 0:
        raise ValueError("momentum must be nonnegative and coupling nonzero")
    m_squared = z/coupling**2
    pump = a*a*(2*hubble*hubble+hubble_dot)
    return {"metric_kinetic_coefficient": m_squared,
            "phi_action_kinetic_weight": z*a**3,
            "phi_action_gradient_weight": z*a,
            "cosmic_friction": 3*hubble,
            "physical_momentum_squared": (comoving_momentum/a)**2,
            "phi_source_coefficient": coupling/z,
            "metric_source_coefficient": 2/m_squared,
            "canonical_pump": pump,
            "canonical_frequency_squared": comoving_momentum**2-pump,
            "static_poisson_coefficient": 1/(2*m_squared),
            "newton_constant": 1/(8*math.pi*m_squared),
            "tensor_wave_speed_squared": 1.}


def flrw_background_constraints(hubble, hubble_dot, density, pressure,
                                 density_dot, *, kinetic, coupling=1.,
                                 vacuum_density=0.):
    """Einstein--matter background equations and their constraint identity.

    The vacuum density is constant. Density and pressure include every
    other retained matter sector. Constraint propagation follows from
    C_dot=3*H*A-E, with acceleration residual A and continuity residual E.
    This evaluator accepts off-shell background data as well as solutions.
    """
    z = _positive(kinetic, "kinetic coefficient")
    if not all(math.isfinite(v) for v in
               (hubble, hubble_dot, density, pressure, density_dot,
                coupling, vacuum_density)) or coupling == 0:
        raise ValueError("finite background data and nonzero coupling are required")
    m_squared = z/coupling**2
    constraint = 3*m_squared*hubble*hubble-density-vacuum_density
    acceleration = 2*m_squared*hubble_dot+density+pressure
    continuity = density_dot+3*hubble*(density+pressure)
    constraint_dot = 6*m_squared*hubble*hubble_dot-density_dot
    return {"hamiltonian_constraint": constraint,
            "acceleration_residual": acceleration,
            "continuity_residual": continuity,
            "constraint_time_derivative": constraint_dot,
            "constraint_propagation_identity_residual":
                constraint_dot-3*hubble*acceleration+continuity}


def matched_ladder_branch(q_squared, geometry, tau, critical_point, *, kinetic=1.):
    """Solve the declared inverse-response matching on the subcritical branch.

    q_squared is Q^2/M_P^2; the spectrum, radius and regulator are fixed.
    The caller supplies the previously computed internal critical point.
    Each quadrature value is reused inside the scalar root solve.
    """
    from functools import lru_cache
    from scipy.optimize import brentq
    from cg_frg.gravity.chi_pole_condition import pi2_chi, v_tt
    z = _positive(kinetic, "dimensionless kinetic coefficient")
    if (not math.isfinite(q_squared) or q_squared < 0
            or not math.isfinite(critical_point) or critical_point <= 0):
        raise ValueError("nonnegative momentum squared and positive critical point required")

    @lru_cache(maxsize=None)
    def data(chi):
        pi = pi2_chi(chi, 2., geometry, tau)
        x = v_tt(chi, 2., geometry)*pi
        return pi, (1-x)/pi

    pi_c, ell_c = data(critical_point)
    if abs(ell_c*pi_c) > 1e-10:
        raise ValueError("the supplied critical point must solve the internal crossing")
    if q_squared == 0:
        return {"chi": critical_point, "inverse_response": 0., "matching_residual": ell_c,
                "spectral_evaluations": data.cache_info().misses}
    target = z*q_squared
    if target > data(0.)[1]:
        raise ValueError("momentum is outside the matched nonnegative deformation branch")
    root = brentq(lambda chi: data(chi)[1]-target, 0., critical_point,
                  xtol=1e-14, rtol=1e-14)
    pi, ell = data(root)
    return {"chi": root, "inverse_response": ell, "matching_residual": ell-target,
            "momentum_times_response": q_squared/ell,
            "spectral_evaluations": data.cache_info().misses}


def evaluate_records(records):
    """Anchor-normalized extension: g=1, Z=M_P^2, G=g^2/(8 pi Z)."""
    from cg_frg.gravity.nonlinear_tensor import verify_classical_completion
    classical_ward = verify_classical_completion()
    mp = _positive(float(records["M_P"]["value"]), "Planck scale")
    z = _positive(float(records["external_tensor_Z"]["value"]), "stored kinetic coefficient")
    if abs(z/(mp*mp)-1) > 1e-14:
        raise ValueError("stored kinetic coefficient must match the specified Planck normalization")
    certificate = exact_helicity_certificate(Fraction(str(mp))**2)
    p = np.array([1., 2., 3., 4.])
    xi = np.array([2., -1., 0., 3.])
    gauge = np.outer(p, xi)+np.outer(xi, p)
    ward = float(np.max(np.abs(fp_operator(p, gauge))))
    pol = physical_polarizations([0., 0., 1.])
    orthogonal = float(np.max(np.abs(np.einsum('aij,bij->ab', pol, pol)-np.eye(2))))
    gram = helicity_reflection_gram([0., .3, .7], [[1., 0.], [0., 1.], [1., 1.]],
                                   1., kinetic=1.)
    gram_min = float(np.linalg.eigvalsh(gram).min())
    energy = np.diag([1., 0., 0., 0.])
    static = conserved_exchange([0., 0., 0., 1.], energy, energy, kinetic=1.)
    gn = float(records["external_tensor_G"]["value"])
    anchor = float(records["G_N_PDG"]["value"])
    residual = abs(gn/anchor-1)
    detuning = records["chi_detuning_response"]["value"]
    chi_c = float(records["chi_pole_crossing"]["value"])
    internal_slope = _positive(float(detuning["slope"]), "internal crossing slope")
    internal_residue = _positive(float(detuning["residue"]), "internal detuning residue")
    pi_c = _positive(float(records["external_tensor_Pi_critical"]["value"]), "stored critical response")
    a = _positive(float(records["external_tensor_chi_slope"]["value"]), "stored conversion slope")
    if (abs(pi_c/(internal_residue*internal_slope)-1) > 1e-14
            or abs(a/internal_residue-1) > 1e-14
            or abs(gn*(8*math.pi*z)-1) > 1e-14
            or abs(float(records["external_tensor_residue"]["value"])*z-1) > 1e-14):
        raise ValueError("stored external coefficients must share the stated matching")
    from cg_frg.gravity.chi_pole_condition import _geometry
    c = float(records["kL"]["value"])
    geometry = _geometry(c, float(records["M_G"]["value"]), mp)
    matched = [dict(q_squared=q2, **matched_ladder_branch(q2, geometry,
                float(records["tau"]["value"]), chi_c)) for q2 in (1e-4, 1e-5)]
    matching_passed = all(abs(row["momentum_times_response"]-1) < 1e-8 for row in matched)
    passed = (ward == 0 and orthogonal < 1e-14 and gram_min > -1e-14
              and static == .5 and residual < 1e-12
              and certificate["visible_rank"] == 2 and matching_passed
              and classical_ward["passed"])
    if not passed:
        raise ArithmeticError("external gauge-tensor checks failed")
    return {"action": "macroscopic Einstein--matter action; Phi couples to total conserved matter T",
            "linear_gauge_symmetry": "delta Phi=partial xi+transpose",
            "order": "quadratic action and leading source exchange about flat vacuum",
            "kinetic_GeV_squared": z, "residue_GeV_inverse_squared": 1/z,
            "newton_GeV_inverse_squared": gn, "anchor_relative_residual": residual,
            "exact_helicity_certificate": certificate,
            "classical_completion": {
                "action": "Einstein--scalar on one metric; covariant matter functionals use the same Hilbert source",
                "normalization": "g_metric=eta-2*g*Phi; M_star^2=Z/g^2",
                "level": "classical local two-derivative effective action",
                "noether_identity": "2 nabla_mu E^mu_nu=E_A partial_nu phi^A",
                "cubic_identity": "delta_0 S_3+delta_1 S_2=0 up to a boundary term",
                "verification": classical_ward},
            "background_response": {
                "scope": "same classical action on a spatially flat FLRW solution",
                "metric_equation": "h_ddot+3*H*h_dot-a^-2*Delta(h)=2*Pi_TT/M_star^2",
                "tensor_action": "M_star^2/8 integral a^3 [h_dot^2-a^-2(grad h)^2]",
                "constraint_identity": "C_dot=3*H*(2*M_star^2*H_dot+rho+p)-(rho_dot+3*H*(rho+p))",
                "static_limit": "Delta(Psi)=rho/(2*M_star^2); G=1/(8*pi*M_star^2)",
                "source": "total Hilbert stress of the retained covariant matter action"},
            "ladder_matching": {
                "units": "q^2=Q^2/M_P^2; Z_hat=1; declared ladder source normalization",
                "equation": "(1-x(chi(q^2)))/Pi(chi(q^2))=q^2",
                "matching_status": "effective inverse-response identification",
                "chi_at_zero": chi_c,
                "Pi_at_critical_point": pi_c,
                "minus_dchi_dq_squared": a,
                "normalized_external_residue": pi_c/(a*internal_slope),
                "resolved_momentum_branches": matched},
            "checks": {"pure_gauge_operator_residual": ward,
                       "polarization_orthonormality_residual": orthogonal,
                       "reflection_gram_minimum": gram_min,
                       "static_energy_contraction": static},
            "ww_realization": "diffeomorphism constraints and asymptotic ADM translation charge of the classical effective action",
            "passed": passed}


def compute():
    """Publish algebraic coefficients using previously computed source data.

    The production step performs no quadrature, root solve or pole scan.
    Gauge and momentum-branch checks are evaluated once in the extension
    verification, which reads these stored coefficients.
    """
    from cg_core.params import get, set as pset
    from cg_core.quantities import QuantityDefinition

    def definition(name, unit, operator, projection="two physical helicities"):
        return QuantityDefinition(object=name, unit=unit,
            carrier="macroscopic collective metric tensor, linearized on Minkowski background",
            operator=operator, source="Phi_mu_nu T_total^mu_nu with g=1",
            projection=projection, normalization="Z=M_P^2; q^2=Q^2/M_P^2",
            scheme="classical Einstein--matter effective action",
            order="quadratic action and leading conserved-source exchange",
            assumptions=("local two-derivative linear gauge action",
                         "flat source-free vacuum and conserved matter source",
                         "inverse ladder response matched to q^2"),
            error_kind="algebraic evaluation of stored inputs")

    evidence = "quadratic gauge action and declared inverse-response matching"
    mp = _positive(float(get("M_P")), "Planck scale")
    pset("external_tensor_Z", mp*mp, provenance="DERIVED",
         note="Z=M_P^2, coefficient of the specified external Fierz-Pauli action in GeV^2.",
         dependencies=("M_P",), definition=definition("external tensor kinetic coefficient", "GeV^2", "Z Q^2 I_2"),
         evidence_kind=evidence)
    z = float(get("external_tensor_Z"))
    pset("external_tensor_residue", 1/z, provenance="DERIVED",
         note="Positive physical helicity residue g^2/Z with g=1, in GeV^-2.",
         dependencies=("external_tensor_Z",), definition=definition("external helicity pole residue", "GeV^-2", "lim Q^2 C_hel(Q^2)"),
         evidence_kind=evidence)
    pset("external_tensor_G", 1/(8*math.pi*z), provenance="DERIVED",
         note="Static energy-source coefficient G=1/(8*pi*Z), in GeV^-2, in the specified gauge action.",
         dependencies=("external_tensor_Z",), definition=definition("external static Newton coefficient", "GeV^-2", "complete conserved-source exchange", "static energy monopoles"),
         evidence_kind=evidence)
    detuning = get("chi_detuning_response")
    slope = _positive(float(detuning["slope"]), "internal crossing slope")
    residue = _positive(float(detuning["residue"]), "internal detuning residue")
    pset("external_tensor_Pi_critical", residue*slope, provenance="DERIVED",
         note="Pi_c=x'(chi_c)*R_delta in the declared dimensionless ladder source normalization.",
         dependencies=("chi_detuning_response",), definition=definition("critical compact ladder response", "dimensionless", "Pi(chi_c)=J(chi_c)/c^4", "specified compact ladder"),
         evidence_kind=evidence)
    pset("external_tensor_chi_slope", residue, provenance="DERIVED",
         note="-dchi/d(Q^2/M_P^2)=Pi_c/x'(chi_c)=R_delta for Z_hat=1 under inverse-response matching.",
         dependencies=("chi_detuning_response",), definition=definition("external momentum conversion slope", "dimensionless", "-dchi/d(Q^2/M_P^2) at Q^2=0", "matched scalar inverse response"),
         evidence_kind=evidence)
    critical = float(get("chi_pole_crossing"))
    status = {"scope": "macroscopic Einstein--matter response; flat-background tensor coefficients",
              "physical_helicities": [-2, 2], "external_massless_pole_established": True,
              "critical_coordinate_key": "chi_pole_crossing",
              "critical_coordinate": critical,
              "source_normalization": "g=1; Z=M_P^2",
              "matching": "(1-x(chi(q^2)))/Pi(chi(q^2))=q^2",
              "physical_description": "collective metric response and its effective helicity-two excitations",
              "interacting_completion_established": True,
              "completion_scope": "classical Einstein--scalar effective action; covariant matter extensions with their supplied action",
              "completion_evidence": "arbitrary-field Noether proof and exact rational jet verification",
              "metric_identification": "g_mu_nu=eta_mu_nu-2*Phi_mu_nu",
              "hilbert_source": "T^mu_nu=-(2/sqrt(-g))*delta S_m/delta g_mu_nu",
              "cubic_ward_identity": "delta_0 S_3+delta_1 S_2=0 up to a boundary term",
              "background_equations": "3*M_star^2*H^2=rho+rho_Lambda; -2*M_star^2*H_dot=rho+p",
              "tensor_background_operator": "d_t^2+3*H*d_t-a^-2*Delta",
              "stationary_limit": "Delta(Psi)=rho/(2*M_star^2)",
              "approximation_order": "classical effective action and its linear response on a specified solution"}
    pset("external_tensor_status", status, provenance="DERIVED", role="informational",
         note="Physical realization and matching scope of the external tensor coefficients; the helicity pole follows from the specified quadratic gauge action.",
         dependencies=("chi_pole_crossing",), evidence_kind=evidence)
    return status


if __name__ == "__main__":
    result = compute()
    print("External gauge-tensor coefficients published; two physical massless helicities.")
