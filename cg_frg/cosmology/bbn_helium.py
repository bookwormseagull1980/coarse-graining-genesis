# -*- coding: utf-8 -*-
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

"""Framework BBN readouts and adapters to continuous weak-rate evolution.

The production approximation evaluates a weak freeze-out condition, a
neutron-decay interval, and Yp=2X_n under complete neutron capture. The
neutron and proton fractions conserve their common baryon normalization.
Its inputs are the framework's EW and mass readouts. The hadronic assignments
g_A=4/pi, Delta_np=(m_d-m_u)-Delta_EM, Delta_EM=(1-1/(2*pi))*alpha*Lambda and
the common rate factor 1+(1-tau)/(8*pi) are specified constitutive rules.
They are not nucleon matrix elements or radiative integrals established by
representation counting alone. All are computed without observed BBN inputs.

The production thermal approximation uses two constant radiation degree
counts and an assigned bottleneck temperature. The separately assigned
N_eff=3+sqrt(3)/(2*pi)^2 is not inserted into that two-region approximation.

framework_weak_inputs supplies the same current inputs to thermal_weak,
which independently integrates six forward/reverse weak channels, the
zero-temperature lifetime and continuous thermal evolution. That extension
uses explicit neutrino energy content and a declared decoupling temperature.
It does not replace nuclear reaction data by instantaneous capture. Sourced
nuclear rate functions can be integrated by reaction_network; a precision
helium/deuterium prediction additionally requires a complete nuclear network
and the specified hadronic and thermal corrections.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, input_scope, set as pset  # noqa: E402
from cg_core.sm_content import N_C, N_GENERATIONS, N_G_COLOR  # noqa: E402


def framework_weak_inputs():
    """Use current computed inputs in the explicit continuous weak-rate API.

    This adapter changes neither production parameters nor hadronic rules.
    It permits a check that the same normalization controls free decay and
    thermal forward/inverse rates; it does not import an observed lifetime.
    """
    from cg_frg.cosmology.thermal_weak import WeakInputs
    return WeakInputs(
        G_F=fermi_constant(float(get("v_HIGGS"))),V_ud=ckm_vud(),
        g_A=axial_coupling(),electron_mass=float(get("m_e_pred"))*1e-3,
        neutron_proton_split=neutron_proton_mass_diff(),
        alpha_em=alpha_em_zero(),rate_multiplier=radiative_correction(),
        source="V5 specified EW, quark-mass and hadronic constitutive readouts")


def matched_neutron_proton_split(*, m_down, m_up, scalar_isovector_matrix_element,
                                 electromagnetic_split, scale, scheme, source,
                                 matrix_element_scale=None, matrix_element_scheme=None,
                                 electromagnetic_convention=None,
                                 electromagnetic_source=None, mass_source=None):
    """Delta_np=C_ud(mu)[m_d(mu)-m_u(mu)]-Delta_EM in one stated convention.

    C_ud is the nucleon scalar-isovector matrix element, supplied from the
    specified action or a declared external calculation. It is not set to
    one by flavour counting. The same scheme/scale must be used for masses
    and matrix element; matching this condition is the caller's obligation.
    electromagnetic_split is the proton-minus-neutron contribution in GeV.
    """
    from cg_frg.qcd.qcd_sector import matched_isovector_split
    return matched_isovector_split(m_down=m_down, m_up=m_up,
        scalar_isovector_matrix_element=scalar_isovector_matrix_element,
        electromagnetic_split=electromagnetic_split, scale=scale, scheme=scheme,
        source=source, matrix_element_scale=matrix_element_scale,
        matrix_element_scheme=matrix_element_scheme,
        electromagnetic_convention=electromagnetic_convention,
        electromagnetic_source=electromagnetic_source, mass_source=mass_source)

# The current production inputs are internal constitutive readouts.
# Continuous rates use the same weak normalization through framework_weak_inputs.
# Establishing the hadronic rules requires nucleon matrix elements; counting
# alone does not evaluate an axial current or electromagnetic self-energy.

G_EFF = 10.75         # relativistic DOF at T ~ 1 MeV (freeze-out)
G_EFF_BBN = 3.36      # relativistic DOF after e+e- annihilation (BBN)
T_BBN = 0.08e-3       # GeV, the deuterium-bottleneck temperature (~0.08 MeV)


def internal_M_Z() -> float:
    """The internal Z mass: M_Z = sqrt(g2(v)^2 + g1'(v)^2) v/2 with the
    geometric couplings g1(M_G), g2(M_G) run one-loop down to the
    framework's own v (the same closure as geometric_couplings).  No
    external scale enters."""
    v = float(get("v_HIGGS"))
    M_G = float(get("M_G"))
    g1 = float(get("g1_MG_geo"))
    g2 = float(get("g2_MG"))
    L = math.log(M_G / v)
    b1, b2 = 41.0 / 10.0, -19.0 / 6.0
    g1v = 1.0 / math.sqrt(1.0 / g1 ** 2 + b1 / (8.0 * math.pi ** 2) * L)
    g2v = 1.0 / math.sqrt(1.0 / g2 ** 2 + b2 / (8.0 * math.pi ** 2) * L)
    g1p = g1v * math.sqrt(3.0 / 5.0)
    return math.sqrt(g2v ** 2 + g1p ** 2) * v / 2.0


def alpha_em_zero() -> float:
    """alpha_em(0) from the framework's internal alpha^-1(M_Z).

    1/alpha(0) = 1/alpha(M_Z) + (2/3pi) sum_f Q_f^2 N_cf ln(M_Z/m_f),
    the one-loop QED vacuum polarisation of the framework's OWN
    content: the leptons on the internal ladder masses (m_e, m_mu,
    m_tau), the heavy quarks (c, b) on the internal masses, and the
    light quarks (u, d, s) frozen at the internal Lambda_QCD (the
    framework's confinement scale).  alpha^-1(M_Z) = 128.208 is the
    framework's DERIVED value (geometric_couplings); no external
    fine-structure constant enters. Light-quark thresholds at Lambda_QCD
    define this infrared approximation, not a hadronic vacuum-polarization
    reconstruction from its spectral function.
    """
    m_e = float(get("m_e_pred")) * 1e-3
    m_mu = m_e * float(get("m_mu_over_m_e"))
    a_lp = float(get("alpha_lepton"))
    m_tau = m_mu * math.exp(2.0 * a_lp)
    m_t = float(get("m_t_pred"))
    m_c = m_t / float(get("m_t_over_m_c"))
    m_b = float(get("m_b_pred"))
    lam = float(get("qcd_Lambda_QCD"))
    MZ = internal_M_Z()
    s = math.log(MZ / m_e) + math.log(MZ / m_mu) + math.log(MZ / m_tau)
    s += N_C * (4.0 / 9.0) * (math.log(MZ / lam) + math.log(MZ / m_c))
    s += N_C * (1.0 / 9.0) * (2.0 * math.log(MZ / lam) + math.log(MZ / m_b))
    inv0 = float(get("alpha_inv_MZ_pred")) + (2.0 / (3.0 * math.pi)) * s
    return 1.0 / inv0
N_G = float(N_G_COLOR)  # colour adjoint dimension from the common carrier
DELTA_S = 0.5         # scalar conformal weight (d−2)/2
# NOTE: the torsion parameter τ = (N_L−N_R)/(N_f·ΣY²) = 1/50 is the
# framework's DERIVED charged-quotient ratio (Lean-proven); it is not a
# center bias of the complete 8+8 carrier.  The run-time value is
# always read from the store via get("tau") — no local copy is kept.


def ckm_vud() -> float:
    """|V_ud| = √(1 − |V_us|²) — CKM unitarity.

    |V_us| is the framework's Gatto value (V_us_geo, neutrino_closure);
    |V_ub|² ~ 1e-5 is negligible at this precision.  This is a clean
    internal derivation (no free parameter).
    """
    V_us = float(get("V_us_geo"))
    return math.sqrt(max(0.0, 1.0 - V_us ** 2))


def axial_coupling() -> float:
    """Specified hadronic axial readout g_A=N_g*Delta_s/pi=4/pi.

    The content factors fix this constitutive formula. Establishing it as
    the nucleon axial-current matrix element requires the actual nucleon
    states and normalized current of a matching calculation.
    """
    return N_G * DELTA_S / math.pi


def em_self_energy(lambda_qcd: float) -> float:
    """Specified Delta_EM=(1-1/(2*pi))*alpha_em(0)*Lambda_QCD.

    This is the assigned proton-minus-neutron electromagnetic contribution
    in the current mass-splitting readout, not a computed nucleon current
    correlator. alpha_em(0) uses the framework's internal running inputs.
    """
    return (1.0 - 1.0 / (2.0 * math.pi)) * alpha_em_zero() * lambda_qcd


def radiative_correction() -> float:
    """Common rate multiplier 1+(1-tau)/(8*pi) of the declared readout.

    The content modulus is read from the store. This formula is not the
    Sirlin radiative integral; the thermal extension applies the same
    specified multiplier to every time-reversed reaction pair.
    """
    tau = float(get("tau"))
    return 1.0 + (1.0 - tau) / (8.0 * math.pi)


def neff_correction() -> float:
    """Assigned delta_N=sqrt(3)/(3*(2*pi)^2).

    The value is a geometric readout. Noninstantaneous neutrino decoupling
    is not inferred from it; a thermal solver takes its radiation content
    as an explicit input.
    """
    return math.sqrt(3.0) / (N_GENERATIONS * (2.0 * math.pi) ** 2)


def beta_phase_space(dm: float, m_e: float, alpha_em: float, *,
                    rtol: float = 2e-12, atol: float = 2e-14,
                    include_derivatives: bool = False) -> dict:
    """Dimensionless static-nucleon decay phase space with point Coulomb.

    With d=(Delta-m_e)/m_e and W=1+d*x, the integral is d^3 times
    an integral on 0<=x<=1. Multiplying the Coulomb factor by W*p first
    gives 2*pi*alpha*W^2/[1-exp(-2*pi*alpha*W/p)], finite at p=0.
    The absolute tolerance applies to the normalized integral; both its
    value and its returned error estimate are multiplied by d^3.
    The returned quadrature estimate and integrand-evaluation count describe
    this numerical integral, separately from hadronic or radiative inputs.
    """
    from scipy.integrate import quad
    if (not all(math.isfinite(x) for x in (dm, m_e, alpha_em, rtol, atol))
            or dm < 0 or m_e <= 0 or alpha_em < 0 or min(rtol, atol) <= 0):
        raise ValueError("finite splitting, positive mass/tolerances and nonnegative alpha required")
    if dm <= m_e:
        result = {"value": 0., "estimated_abs_error": 0., "integrand_evaluations": 0,
                  "method": "kinematically closed free decay", "unit": "1"}
        if include_derivatives:
            result.update(derivative_splitting_ratio=0., derivative_alpha_em=0.,
                          derivative_estimated_abs_error=0.)
        return result
    d = (dm-m_e)/m_e
    a = 2*math.pi*alpha_em
    def integrand(x):
        W = 1+d*x
        p = math.sqrt(d*x*(2+d*x))
        if a == 0:
            electron = W*p
        else:
            electron = a*W*W/(-math.expm1(-a*W/p)) if p else a*W*W
        return electron*(1-x)**2
    result = quad(integrand, 0., 1., epsrel=rtol, epsabs=atol,
                  limit=160, full_output=True)
    if len(result) != 3:
        raise ArithmeticError("beta phase-space quadrature failed: " + str(result[3]))
    value, error, information = result
    output = {"value": d**3*value, "estimated_abs_error": d**3*error,
            "integrand_evaluations": int(information["neval"]),
            "method": "adaptive Gauss-Kronrod on normalized Coulomb-regular phase space",
            "unit": "1"}
    if include_derivatives:
        import numpy as np
        rules = [np.polynomial.legendre.leggauss(order) for order in (12, 24)]
        derivative_evaluations = 0
        interval_evaluations = 0
        def derivative_integrand(x):
            W = 1+d*x
            p = math.sqrt(d*x*(2+d*x))
            if a == 0:
                electron, alpha_derivative = W*p, math.pi*W*W
            else:
                z = a*W/p if p else math.inf
                denominator = -math.expm1(-z)
                electron = a*W*W/denominator
                correction = z/math.expm1(z) if z < 700 else 0.
                alpha_derivative = 2*math.pi*W*W/denominator*(1-correction)
            return np.array([2*d**2*electron*(1-x),
                             d**3*alpha_derivative*(1-x)**2])
        def interval(left, right):
            nonlocal derivative_evaluations, interval_evaluations
            half, middle = (right-left)/2, (right+left)/2
            estimates = []
            for nodes, weights in rules:
                values = np.array([derivative_integrand(middle+half*node) for node in nodes])
                estimates.append(half*weights@values)
                derivative_evaluations += len(nodes)
            interval_evaluations += 1
            return [left, right, estimates[1], np.abs(estimates[1]-estimates[0])]
        # Reuse the centre's accepted partition, retaining its original
        # summation and floating-point value. Only derivative integrals refine.
        pieces = [interval(float(left), float(right)) for left, right in
                  zip(information['alist'][:information['last']],
                      information['blist'][:information['last']])]
        while True:
            derivatives = np.sum([piece[2] for piece in pieces], axis=0)
            errors = np.sum([piece[3] for piece in pieces], axis=0)
            if np.all(errors <= atol+rtol*np.abs(derivatives)):
                break
            if len(pieces) >= 320:
                raise ArithmeticError("beta phase-space derivative partition did not converge")
            worst = max(range(len(pieces)), key=lambda i: float(np.max(pieces[i][3])))
            left, right, _, _ = pieces.pop(worst)
            middle = (left+right)/2
            pieces.extend((interval(left, middle), interval(middle, right)))
        output.update(derivative_splitting_ratio=float(derivatives[0]),
                      derivative_alpha_em=float(derivatives[1]),
                      derivative_estimated_abs_error=float(np.max(errors)),
                      center_integrand_evaluations=int(information['neval']),
                      derivative_integrand_evaluations=derivative_evaluations,
                      integrand_evaluations=int(information['neval'])+derivative_evaluations,
                      reused_center_subintervals=int(information['last']),
                      derivative_interval_evaluations=interval_evaluations,
                      derivative_error_method="12/24-point Gauss difference on reused/refined centre partition; estimated, not rigorous")
    return output


def phase_space_f(dm: float, m_e: float) -> float:
    """Phase-space centre with the framework's zero-momentum coupling."""
    return beta_phase_space(dm, m_e, alpha_em_zero())["value"]


def sirlin_delta_r(m_p: float) -> float:
    """Compatibility alias for the specified common rate multiplier.

    The unused m_p argument is retained for API compatibility. This
    function does not evaluate the Sirlin loop correction.
    """
    return radiative_correction()


def fermi_constant(v: float) -> float:
    """G_F = 1/(√2 v²) — the Fermi constant from the closed EW scale."""
    return 1.0 / (math.sqrt(2.0) * v * v)


def quark_masses() -> dict:
    """The down/up quark masses from the framework's mass ladder.

    m_u = m_t/(m_t/m_u), m_s = m_b/(m_b/m_s), m_d = m_s/(m_s/m_d)
    — the framework's DERIVED mass ratios (lz_ladder, mass_operator)
    anchor the absolute quark masses.
    """
    m_t = float(get("m_t_pred"))
    m_b = float(get("m_b_pred"))
    m_u = m_t / float(get("m_t_over_m_u"))
    m_s = m_b / float(get("m_b_over_m_s"))
    m_d = m_s / float(get("m_s_over_m_d"))
    return {"m_u": m_u, "m_d": m_d, "m_s": m_s}


def neutron_proton_mass_diff() -> float:
    """Specified Delta_np=(m_d-m_u)-Delta_EM, with scalar coefficient one.

    The assigned coefficient is a hadronic constitutive choice. The
    matched_neutron_proton_split API accepts an independently supplied
    scalar-isovector matrix element and a stated mass scheme/scale.
    """
    return framework_hadronic_matching()["isovector"]["neutron_proton_split"]


def framework_hadronic_matching() -> dict:
    """The common production proton and isovector sources with their units.

    The generated quark masses have the native spectral mass definition.
    M_G labels their generation reference. The current unit scalar source
    and electromagnetic coefficient are carried explicitly to the weak
    kernel; a physical QCD matching uses the separate sourced interface.
    """
    from cg_frg.qcd.qcd_sector import native_nucleon_readout
    q = quark_masses()
    return native_nucleon_readout(Lambda_QCD=float(get("qcd_Lambda_QCD")),
        tau=float(get("tau")), m_down=q["m_d"], m_up=q["m_u"],
        alpha_em=alpha_em_zero(), generation_scale=float(get("M_G")))


def neutron_lifetime(G_F: float, m_e: float, dm: float) -> float:
    """Free decay in the stated Coulomb/common-multiplier approximation.

    G_F, masses, |V_ud|, g_A and the multiplier are the same declared inputs
    exposed by framework_weak_inputs. No measured lifetime is used to
    normalize the weak rate.
    """
    V_ud = ckm_vud()
    g_A = axial_coupling()
    f = phase_space_f(dm, m_e)
    delta_R = radiative_correction()
    tau = 2.0 * math.pi ** 3 / (G_F ** 2 * V_ud ** 2 * (1.0 + 3.0 * g_A ** 2)
                                * m_e ** 5 * f * delta_R)
    return tau * 6.582119569e-25   # GeV^-1 -> s


def freeze_temperature(G_F: float, M_P: float, dm: float) -> float:
    """T_f: solve Γ_weak(T) = H(T) (the weak freeze-out).

    The instantaneous-freeze-out prescription uses
    Γ = (7π/60)(1+3g_A²)G_F²T⁵(1 + 3Δm/2T).
    The six-channel thermal extension evaluates its own collision rates
    directly from the stated Born integrals. Here the comparison is with
    H = √(4π³g_eff/45)T²/M_Pl, where M_Pl = √(8π)M_P is the FULL
    Planck mass (the Hubble parameter uses 1/√G_N, not the reduced
    M_P = 1/√(8πG_N)).  The freeze-out is Γ = H (expansion wins
    when Γ < H).
    """
    return _freeze_temperature(G_F, M_P, dm, axial_coupling(), G_EFF, 1.)


def _freeze_temperature(G_F, M_P, dm, g_A, radiation_dof, multiplier):
    M_Pl = math.sqrt(8.0 * math.pi) * M_P
    H_coeff = math.sqrt(4.0 * math.pi ** 3 * radiation_dof / 45.0)

    def gamma(T):
        return multiplier * (7.0 * math.pi / 60.0) * (1.0 + 3.0 * g_A ** 2) * G_F ** 2 \
               * T ** 5 * (1.0 + 1.5 * dm / T)
    lo, hi = 1e-5, 1e-2
    while gamma(lo) > H_coeff*lo**2/M_Pl:
        lo /= 2
    while gamma(hi) < H_coeff*hi**2/M_Pl:
        hi *= 2
    for _ in range(120):
        mid = 0.5 * (lo + hi)
        if gamma(mid) > H_coeff * mid ** 2 / M_Pl:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def instantaneous_weak_chain(*, neutron_proton_split, G_F, V_ud, g_A,
                             rate_multiplier, electron_mass, alpha_em,
                             reduced_planck_mass, freeze_rate_multiplier=1.,
                             freeze_radiation_dof=G_EFF,
                             capture_radiation_dof=G_EFF_BBN,
                             capture_temperature=T_BBN,
                             include_phase_derivatives=False):
    """Evaluate one specified splitting through the complete capture chain.

    All physical inputs are explicit. A caller supplies the mass splitting
    either from the generated hadronic readout or from an isolated comparison
    calculation. This evaluator reads and writes no parameter store.
    """
    dm = neutron_proton_split
    positive = (G_F, V_ud, rate_multiplier, electron_mass, reduced_planck_mass,
                freeze_rate_multiplier, freeze_radiation_dof,
                capture_radiation_dof, capture_temperature)
    if (not all(math.isfinite(value) for value in (*positive, dm, g_A, alpha_em))
            or min(positive) <= 0 or alpha_em < 0 or dm <= electron_mass):
        raise ValueError("finite weak inputs and Delta_np > m_e are required")
    phase = beta_phase_space(dm, electron_mass, alpha_em,
                             include_derivatives=include_phase_derivatives)
    f = float(phase['value'])
    axial = 1.0+3.0*g_A**2
    tau_n = 2.0*math.pi**3/(
        G_F**2*V_ud**2*axial*electron_mass**5*f*rate_multiplier)
    tau_n *= 6.582119569e-25
    T_f = _freeze_temperature(G_F, reduced_planck_mass, dm, g_A,
                             freeze_radiation_dof, freeze_rate_multiplier)
    full_planck = math.sqrt(8*math.pi)*reduced_planck_mass
    freeze_time_natural = .301*full_planck/math.sqrt(freeze_radiation_dof)/T_f**2
    capture_time_natural = .301*full_planck/math.sqrt(capture_radiation_dof)/capture_temperature**2
    t_freeze = freeze_time_natural*6.582119569e-25
    t_decay = (capture_time_natural-freeze_time_natural)*6.582119569e-25
    if t_decay <= 0:
        raise ValueError("capture must occur after weak freeze-out")
    helium = helium_yield(T_f, dm, t_decay, tau_n)
    return {"values": dict(dm_np=dm, tau_n=tau_n, T_f=T_f,
                           t_decay=t_decay, Y_p=helium['Y_p']),
            "phase_space": phase, "helium_fractions": helium,
            "freeze_time": t_freeze}


def bbn_joint_response(*, m_down, m_up, scalar_isovector_matrix_element,
                       electromagnetic_split, G_F, V_ud, g_A, rate_multiplier,
                       electron_mass, alpha_em, reduced_planck_mass,
                       freeze_rate_multiplier=1., freeze_radiation_dof=G_EFF,
                       capture_radiation_dof=G_EFF_BBN,
                       capture_temperature=T_BBN):
    """Common mass, weak-decay and instantaneous-capture Jacobian.

    Derivatives are with respect to the stated independent matching inputs;
    correlated upstream changes are composed with this Jacobian. They are
    sensitivities, not probability distributions or fitted theoretical errors.
    The production freeze kernel contains G_F and g_A. V_ud and the common
    radiative factor enter its free-decay kernel; freeze_rate_multiplier is
    a separate explicit normalization direction, equal to one in production.
    One scalar quadrature evaluates f; its accepted partition is reused
    for df/d(Delta/m_e) and df/d alpha without recomputing the centre.
    """
    import numpy as np
    inputs = dict(m_down=m_down, m_up=m_up,
                  scalar_isovector_matrix_element=scalar_isovector_matrix_element,
                  electromagnetic_split=electromagnetic_split, G_F=G_F,
                  V_ud=V_ud, g_A=g_A, rate_multiplier=rate_multiplier,
                  electron_mass=electron_mass, alpha_em=alpha_em,
                  reduced_planck_mass=reduced_planck_mass,
                  freeze_rate_multiplier=freeze_rate_multiplier)
    if (not all(math.isfinite(value) for value in (*inputs.values(),
            freeze_radiation_dof, capture_radiation_dof, capture_temperature)) or
            min(m_down, m_up, scalar_isovector_matrix_element, G_F, V_ud,
                rate_multiplier, electron_mass, reduced_planck_mass,
                freeze_rate_multiplier, freeze_radiation_dof,
                capture_radiation_dof, capture_temperature) <= 0 or
            min(electromagnetic_split, alpha_em) < 0):
        raise ValueError("finite matching inputs, positive scales and nonnegative electromagnetic inputs required")
    dm = scalar_isovector_matrix_element*(m_down-m_up)-electromagnetic_split
    if dm <= electron_mass:
        raise ValueError("the differentiable free-decay branch requires Delta_np > m_e")
    chain = instantaneous_weak_chain(
        neutron_proton_split=dm, G_F=G_F, V_ud=V_ud, g_A=g_A,
        rate_multiplier=rate_multiplier, electron_mass=electron_mass,
        alpha_em=alpha_em, reduced_planck_mass=reduced_planck_mass,
        freeze_rate_multiplier=freeze_rate_multiplier,
        freeze_radiation_dof=freeze_radiation_dof,
        capture_radiation_dof=capture_radiation_dof,
        capture_temperature=capture_temperature, include_phase_derivatives=True)
    phase = chain['phase_space']
    f = float(phase['value'])
    f_ratio = float(phase['derivative_splitting_ratio'])
    f_alpha = float(phase['derivative_alpha_em'])
    axial = 1.0+3.0*g_A**2
    tau_n, T_f, t_decay = (chain['values'][key] for key in ('tau_n', 'T_f', 't_decay'))
    t_freeze, helium = chain['freeze_time'], chain['helium_fractions']
    names = list(inputs)
    index = {name: i for i, name in enumerate(names)}
    dm_gradient = np.zeros(len(names))
    dm_gradient[index['m_down']] = scalar_isovector_matrix_element
    dm_gradient[index['m_up']] = -scalar_isovector_matrix_element
    dm_gradient[index['scalar_isovector_matrix_element']] = m_down-m_up
    dm_gradient[index['electromagnetic_split']] = -1
    log_tau = -f_ratio/(electron_mass*f)*dm_gradient
    for key, derivative in dict(G_F=-2/G_F, V_ud=-2/V_ud,
                               g_A=-6*g_A/axial, rate_multiplier=-1/rate_multiplier,
                               electron_mass=(-5+dm/electron_mass*f_ratio/f)/electron_mass,
                               alpha_em=-f_alpha/f).items():
        log_tau[index[key]] += derivative
    log_freeze_strength = np.zeros(len(names))
    for key, derivative in dict(G_F=2/G_F, g_A=6*g_A/axial,
                               reduced_planck_mass=1/reduced_planck_mass,
                               freeze_rate_multiplier=1/freeze_rate_multiplier).items():
        log_freeze_strength[index[key]] = derivative
    temperature_gradient = (-(T_f+1.5*dm)*log_freeze_strength-1.5*dm_gradient)*T_f/(3*(T_f+dm))
    time_gradient = 2*t_freeze/T_f*temperature_gradient
    time_gradient[index['reduced_planck_mass']] += t_decay/reduced_planck_mass
    initial_fraction = helium['neutron_fraction_freeze']
    log_helium = (-(1-initial_fraction)*(dm_gradient/T_f-dm/T_f**2*temperature_gradient)
                  -time_gradient/tau_n+t_decay/tau_n*log_tau)
    values = dict(dm_np=dm, tau_n=tau_n, T_f=T_f, t_decay=t_decay, Y_p=helium['Y_p'])
    jacobian = np.stack((dm_gradient, tau_n*log_tau, temperature_gradient,
                         time_gradient, helium['Y_p']*log_helium))
    elasticities = jacobian*np.array(list(inputs.values()))[None, :]/np.array(list(values.values()))[:, None]
    return {"inputs": inputs, "input_order": names, "output_order": list(values),
            "values": values, "jacobian": jacobian.tolist(),
            "logarithmic_derivatives": elasticities.tolist(),
            "phase_space": phase, "helium_fractions": helium,
            "operation_counts": {"phase_space_quadratures": 1,
                "phase_space_integrand_evaluations": phase['integrand_evaluations'],
                "center_integrand_evaluations": phase['center_integrand_evaluations'],
                "derivative_integrand_evaluations": phase['derivative_integrand_evaluations'],
                "derivative_interval_evaluations": phase['derivative_interval_evaluations'],
                "reused_center_subintervals": phase['reused_center_subintervals'],
                "finite_difference_chain_evaluations": 0,
                "freeze_root_iterations": 120},
            "fixed_thermal_inputs": dict(freeze_radiation_dof=freeze_radiation_dof,
                capture_radiation_dof=capture_radiation_dof, capture_temperature=capture_temperature),
            "freeze_kernel_inputs": ["G_F", "g_A", "freeze_rate_multiplier", "dm_np", "reduced_planck_mass"],
            "uncertainty_model_supplied": False,
            "propagation": "delta outputs = J delta inputs; supplied covariance propagates as J C J^T",
            "scope": "same hadronic matching inputs, Coulomb free decay, instantaneous weak freeze-out and complete capture"}


def weak_mass_difference_ranges(*, central_split, statistical_error,
                                systematic_error, **weak_inputs):
    """Finite input ranges in one fixed weak/capture model, without store I/O.

    All three splitting inputs have units GeV. The statistical and systematic
    half-widths are propagated separately; their sum defines an explicitly
    chosen rectangular-error envelope, not a confidence interval. Correlation
    between strong and electromagnetic contributions is already contained in
    the supplied total-splitting errors and is never reconstructed here.

    At fixed weak inputs the positive phase integral increases with splitting,
    while T_f, tau_n, the decay interval and the initial neutron fraction all
    decrease. The survival factor is enclosed using independent positive
    endpoint ranges for the decay interval and lifetime. Thus no sampled
    monotonicity assumption for the final helium abundance is required.
    Quadrature endpoint errors are estimates, reported separately from the
    analytic range propagation; this routine does not certify roundoff.
    """
    if (not all(math.isfinite(value) for value in
                (central_split, statistical_error, systematic_error))
            or min(statistical_error, systematic_error) < 0):
        raise ValueError("finite splitting and nonnegative input half-widths required")
    if central_split-statistical_error-systematic_error <= weak_inputs['electron_mass']:
        raise ValueError("the whole input interval must satisfy Delta_np > m_e")
    if 'include_phase_derivatives' in weak_inputs:
        raise ValueError("finite range propagation evaluates phase-space values only")

    cache = {}

    def evaluate(splitting):
        if splitting not in cache:
            cache[splitting] = instantaneous_weak_chain(
                neutron_proton_split=splitting, **weak_inputs)
        return cache[splitting]

    centre = evaluate(central_split)
    ranges = {}
    for name, half_width in (
            ('statistical', statistical_error),
            ('systematic', systematic_error),
            ('additive_envelope', statistical_error+systematic_error)):
        low, high = central_split-half_width, central_split+half_width
        at_low, at_high = evaluate(low), evaluate(high)
        left, right = at_low['values'], at_high['values']
        tau_min, tau_max = right['tau_n'], left['tau_n']
        time_min, time_max = right['t_decay'], left['t_decay']
        fraction_min = at_high['helium_fractions']['neutron_fraction_freeze']
        fraction_max = at_low['helium_fractions']['neutron_fraction_freeze']
        survival_min = math.exp(-time_max/tau_min)
        survival_max = math.exp(-time_min/tau_max)
        helium_min, helium_max = (2*fraction_min*survival_min,
                                  2*fraction_max*survival_max)
        low_relative_error = (at_low['phase_space']['estimated_abs_error'] /
                              at_low['phase_space']['value'])
        high_relative_error = (at_high['phase_space']['estimated_abs_error'] /
                               at_high['phase_space']['value'])
        ranges[name] = {
            'input_split_GeV': [low, high],
            'half_width_GeV': half_width,
            'output_ranges': {
                'dm_np': [low, high], 'tau_n': [tau_min, tau_max],
                'T_f': [right['T_f'], left['T_f']],
                't_decay': [time_min, time_max], 'Y_p': [helium_min, helium_max]},
            'phase_space_range': [at_low['phase_space']['value'],
                                  at_high['phase_space']['value']],
            'initial_neutron_fraction_range': [fraction_min, fraction_max],
            'survival_fraction_range': [survival_min, survival_max],
            'endpoint_values': {'lower_input': dict(left), 'upper_input': dict(right)},
            'quadrature_error_estimates': {
                'tau_n_range_endpoints_s': [tau_min*high_relative_error,
                                           tau_max*low_relative_error],
                'Y_p_range_endpoints': [helium_min*time_max/tau_min*high_relative_error,
                                        helium_max*time_min/tau_max*low_relative_error]},
            'range_method': 'monotone component endpoints and positive product enclosure'}
    return {
        'central_split_GeV': central_split,
        'statistical_error_GeV': statistical_error,
        'systematic_error_GeV': systematic_error,
        'central_chain': centre, 'ranges': ranges,
        'range_interpretation': 'finite input variations; additive envelope has no assigned coverage probability',
        'numerical_error_status': 'adaptive quadrature estimates; no outward-rounding certificate',
        'physical_approximation_error_quantified': False,
        'production_parameters_updated': False,
        'operation_counts': {
            'unique_weak_chains': len(cache),
            'phase_space_quadratures': len(cache),
            'phase_space_integrand_evaluations': sum(
                value['phase_space']['integrand_evaluations'] for value in cache.values()),
            'freeze_root_iterations': 120*len(cache),
            'derivative_quadratures': 0}}


def helium_yield(T_f: float, dm: float, t_decay: float, tau_n: float) -> dict:
    """Baryon-conserving free decay followed by complete neutron capture.

    X_n=n/(n+p) starts at r_f/(1+r_f), r_f=exp(-dm/T_f), and obeys
    dX_n/dt=-X_n/tau_n. The proton fraction is 1-X_n throughout. The
    baryon fraction in helium is 2X_n at capture; nuclear binding-mass
    corrections and continued thermal conversion belong to the network.
    """
    if (not all(math.isfinite(x) for x in (T_f, dm, t_decay, tau_n))
            or min(T_f, tau_n) <= 0 or min(dm, t_decay) < 0):
        raise ValueError("positive freeze temperature/lifetime and nonnegative splitting/interval required")
    np_ratio = math.exp(-dm / T_f)
    initial_fraction = np_ratio/(1+np_ratio)
    survival = math.exp(-t_decay/tau_n)
    neutron_fraction = initial_fraction*survival
    proton_fraction = 1-neutron_fraction
    np_bbn = neutron_fraction/proton_fraction
    Y_p = 2*neutron_fraction
    return {"np_freeze": np_ratio, "np_bbn": np_bbn, "Y_p": Y_p,
            "neutron_fraction_freeze": initial_fraction,
            "neutron_fraction_capture": neutron_fraction,
            "proton_fraction_capture": proton_fraction,
            "survival_factor": survival}


def compute() -> dict:
    """Publish the specified instantaneous-freeze-out/capture readouts."""
    v = float(get("v_HIGGS"))
    M_P = float(get("M_P"))
    m_e = float(get("m_e_pred")) * 1e-3   # MeV -> GeV
    G_F = fermi_constant(v)
    with input_scope() as hadronic_inputs:
        hadronic = framework_hadronic_matching()
    pset("bbn_hadronic_matching", hadronic, provenance="DERIVED", role="informational",
         note="Common native constituent proton and isovector source, including the scalar "
              "coefficient, electromagnetic separation, generation scale and mass definition.",
         dependencies=tuple(hadronic_inputs))
    hadronic = get("bbn_hadronic_matching")
    with input_scope() as response_inputs:
        source = get("bbn_hadronic_matching")["isovector"]
        joint = bbn_joint_response(
            m_down=source["quark_masses_GeV"]["down"],
            m_up=source["quark_masses_GeV"]["up"],
            scalar_isovector_matrix_element=source["scalar_isovector_matrix_element"],
            electromagnetic_split=source["electromagnetic_proton_minus_neutron_GeV"],
            G_F=fermi_constant(float(get("v_HIGGS"))), V_ud=ckm_vud(),
            g_A=axial_coupling(), rate_multiplier=radiative_correction(),
            electron_mass=float(get("m_e_pred"))*1e-3, alpha_em=alpha_em_zero(),
            reduced_planck_mass=float(get("M_P")))
    pset("bbn_joint_response", joint, provenance="DERIVED", role="informational",
         note="Common mass-splitting, free-lifetime, freeze-out and helium Jacobian; "
              "phase-space derivatives reuse the centre's quadrature partition; declared thermal approximation.",
         dependencies=tuple(response_inputs))
    dm, tau_n, T_f = (joint["values"][key] for key in ("dm_np", "tau_n", "T_f"))
    # t_decay = t(T_BBN) − t(T_f), the radiation-era expansion time
    # t = 0.301 M_Pl/√g_eff / T², with M_Pl the full Planck mass.  The
    # g_eff is TWO-REGION: 10.75 at freeze-out (pre e+e- annihilation)
    # and 3.36 at BBN (post annihilation — γ + 3ν), so the dominant
    # post-annihilation interval gives t_decay ≈ 200 s.
    t_decay = joint["values"]["t_decay"]
    r = joint["helium_fractions"]
    Y_p = r["Y_p"]
    N_eff = N_GENERATIONS * (1.0 + neff_correction())

    pset("alpha_em_0_pred", alpha_em_zero(),
         provenance="DERIVED", role="internal",
         note=f"alpha_em(0) = 1/{1.0/alpha_em_zero():.3f} (QED vacuum "
              f"polarisation of the framework's own content: internal "
              f"alpha^-1(M_Z)={float(get('alpha_inv_MZ_pred')):.3f} + lepton "
              f"and quark loops on the internal masses; u,d,s frozen at "
              f"Lambda_QCD)")

    pset("bbn_GF", G_F, provenance="DERIVED", role="internal",
         note=f"G_F = 1/(sqrt(2) v^2) = {G_F:.4e} GeV^-2 (the Fermi "
              f"constant from the closed v = {v:.2f} GeV)")
    pset("bbn_dm_np", dm, provenance="DERIVED", role="internal",
         note=f"dm_np = (m_d - m_u) - (1-1/2pi) alpha Lambda = {dm*1e3:.4f} MeV "
              f"(specified scalar coefficient one and EM self-energy rule)",
         dependencies=("bbn_hadronic_matching",))
    pset("bbn_Tf", T_f, provenance="DERIVED", role="internal",
         note=f"T_f = {T_f*1e3:.4f} MeV (Gamma_weak = H freeze-out, g_A = 4/pi)")
    pset("bbn_tau_n", tau_n, provenance="DERIVED", role="internal",
         note=f"tau_n = {tau_n:.1f} s (Fermi beta decay, g_A = 4/pi, "
              f"delta_R = 1+(1-tau)/8pi)")
    pset("bbn_t_decay", t_decay, provenance="DERIVED", role="internal",
         note=f"t_decay = {t_decay:.1f} s (the radiation-era expansion time "
              f"from T_f to T_BBN)")
    pset("bbn_Yp", Y_p, provenance="DERIVED", role="internal",
         note=f"Y_p = 2 X_n(T_f) exp(-Delta t/tau_n) = {Y_p:.4f} "
               f"(baryon-conserving neutron decay and complete capture; "
               f"specified g_A=4/pi, Delta_EM=(1-1/2pi)a Lambda, "
              f"delta_R=1+(1-tau)/8pi)")
    pset("bbn_Neff", N_eff, provenance="DERIVED", role="internal",
         note=f"N_eff = 3 + sqrt3/(2pi)^2 = {N_eff:.4f}; specified geometric "
               f"radiation-content readout, not a neutrino-decoupling integration")
    pset("bbn_status",
          f"Y_p = {Y_p:.4f}; N_eff = {N_eff:.4f} (internal constitutive inputs: "
          f"g_A=4/pi, Delta_EM, delta_R, delta_N, "
         f"|V_ud|, f)",
         provenance="DERIVED", role="informational",
         note="the BBN sector: helium yield and neutrino species")

    return {"Y_p": Y_p, "N_eff": N_eff, "T_f": T_f, "dm_np": dm,
            "tau_n": tau_n, "t_decay": t_decay,
            "alpha_em_0": alpha_em_zero(),
            "np_freeze": r["np_freeze"], "np_bbn": r["np_bbn"],
            "neutron_fraction_freeze": r["neutron_fraction_freeze"],
            "neutron_fraction_capture": r["neutron_fraction_capture"],
            "hadronic_matching": hadronic, "joint_response": joint}


if __name__ == "__main__":
    r = compute()
    print(f"G_F  = {1.0/(math.sqrt(2.0)*float(get('v_HIGGS'))**2):.4e} GeV^-2")
    print(f"dm_np = {r['dm_np']*1e3:.4f} MeV, T_f = {r['T_f']*1e3:.4f} MeV")
    print(f"tau_n = {r['tau_n']:.1f} s, t_decay = {r['t_decay']:.1f} s")
    print(f"Y_p = {r['Y_p']:.4f}, N_eff = {r['N_eff']:.4f}")
    print("bbn_helium OK (specified weak freeze-out and neutron-capture readouts)")
