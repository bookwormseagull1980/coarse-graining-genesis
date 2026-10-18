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

"""
cg_frg/frg/discrete_flow.py — V5.0: the discrete RG flow — the
window-kernel semigroup, the analytic β, and the mass-gap spectrum
=================================================================

PURPOSE
-----------------------------------
The framework uses a discrete resolution sampling: the window
W(p, σ) = exp(−p²σ²/2) slides from σ₀ = 1/M_P to σ_C = 1/H0,
attenuates modes above k = 1/σ. The amplitude multiplier alone
does not integrate a path-integral measure or choose real-time
dynamics. An effective-action regulator is a separate object. This module
consolidates the discrete flow's four structural properties:

  PROPERTY 1 — THE RESOLUTION SEMIGROUP
  ----------------------------------------------------------------
  The field-amplitude filter is T_σ = exp(−σ²Δ/2). This is a
  contraction, not unitary evolution or a state-level partial trace.
  For finite positive width it is injective; its inverse becomes
  unbounded on an infinite tower. The family is a
  SEMI-group (not a group): the forward direction σ₀ → σ_C
  (σ increasing — more modes integrated out) is canonical; the
  reverse reconstruction is unstable at finite precision.
  The Gaussian family composes quadratically — two successive
  slides of widths σa, σb equal the single slide at the composed
  width:

      W(Δ,σa)·W(Δ,σb) = exp(−Δ²(σa²+σb²)/2) = W(Δ, √(σa²+σb²))

  — verified numerically here to machine precision (1e-14).
  The composition is always an INCREASE (√(σa²+σb²) > σa, σb):
  the semigroup is one-way — the irreversibility of the
  coarse-graining.

  PROPERTY 2 — THE ANALYTIC β (the closed form)
  ----------------------------------------------
  The vacuum-energy density V_eff(k) = −(C/2)(k^{−2} − M_P^{−2})
  gives the closed β (the paper chain):

      β(σ) = dσ/dt = −2C·σ^{−3}     (C < 0 — the forward flow)

  This is a specified resolution parametrisation, not a physical-time
  law deduced from that potential. For C<0 and sigma(0)>0 it has the
  explicit forward-global solution sigma(t)^4=sigma(0)^4-8Ct.
  A potential by itself does not choose a mobility or physical clock.

  PROPERTY 3 — THE WINDOW-CAPACITY STEP (the discrete ladder)
  ------------------------------------------------------------
  The window capacity kL* = 2.4935343 is CONSTANT along the flow
  (the scale-invariant trajectory M·L = const): the number of
  retained capacity is fixed. The step Δlnσ = 1/kL* is a specified
  sampling convention. Its square is not an error bound: a convergence
  bound needs the actual update, method, stability and derivative data.

  PROPERTY 4 — THE GENERATED YANG--MILLS MASS SPECTRUM
  ----------------------------------------------------
  Paper 4 closes the condensed response in two physical blocks.  The
  source-normalised radial block has mass squared

      m_rad² = 4q F''(q)/Z(q),

  while coclosed colour-connection modes are governed by

      Δ_1^perp + δ_q I,       δ_q = 2q C_ad/(3 V h).

  On RP³ the latter begins at 4/L²+δ_q.  The generated response gap is

      Δ_YM² = min{m_rad², 4/L²+δ_q} > 0.

  The long-root negative coefficient K(R-R_c) selects the condensed branch.
  The two-block spectral minimum is its Yang--Mills gap theorem; the endpoint
  generator scale g₂⟨E⟩, J=2 directory and glueball catalogue are the
  associated scale, channel and composite-state readouts.

  REFLECTION POSITIVITY (the OS structure)
  ----------------------------------------
  Gaussianity alone does not imply reflection positivity. The finite
  free-carrier example below uses A>=0, m>0 and
  C(t)=exp(-|t|sqrt(A+m^2))/(2sqrt(A+m^2)). Same-time filtering B
  yields B C(t) B*, whose reflected quadratic form is a squared norm.
  Its assumptions do not establish interacting or gravitational OS
  positivity. A separate random-phase average is a CPTP state channel;
  its difference-of-eigenvalues multiplier is not the amplitude filter.

PARAMETERS
----------
Reads : kL, M_G, tau, g2_MG, R_c_star, mass_gap_m_gen,
        generated_ym_mass_gap, sigma_C (the IR endpoint, gw_ratio)
Writes: discrete_flow_semigroup, discrete_flow_beta,
        discrete_flow_step, discrete_flow_gap_spectrum,
        discrete_flow_reflection_positivity, discrete_flow_status
        (DERIVED — this module is their writer)

IMPLEMENTATION
-------------
No observed value enters the computation: the semigroup check is
numerical (the Gaussian kernel), the β is the analytic closed
form, the gap spectrum uses the framework's internal quantities.
The QCD running scale and catalogue are retained as separately named
readouts and are not used to define the generated mass gap.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def kernel(Delta: float, sigma: float) -> float:
    """The Gaussian window kernel W(Δ, σ) = exp(−Δ²σ²/2) — the
    spectral weight of a mode at momentum |Δ| in the window σ."""
    return math.exp(-0.5 * (Delta * sigma) ** 2)


def semigroup_check(sigma_a: float, sigma_b: float) -> float:
    """Verify the Gaussian semigroup identity numerically.

    W(Δ,σa)·W(Δ,σb) = W(Δ,√(σa²+σb²)) — two successive window
    slides compose quadratically (the exact Gaussian identity).
    The widths compose by adding their squares. This checks the
    multiplier identity, not a Hilbert-space partial trace or dynamics.
    """
    err = 0.0
    for i in range(201):
        Delta = 0.05 * i            # the mode grid (0 … 10)
        lhs = kernel(Delta, sigma_a) * kernel(Delta, sigma_b)
        rhs = kernel(Delta, math.sqrt(sigma_a ** 2 + sigma_b ** 2))
        err = max(err, abs(lhs - rhs))
    return err


def beta_sigma(C: float, sigma: float) -> float:
    """Specified resolution speed; no physical clock or mobility is inferred."""
    if not math.isfinite(C) or not math.isfinite(sigma) or sigma <= 0:
        raise ValueError("finite C and positive finite sigma required")
    return -2.0 * C * sigma ** -3


def resolution_width(C: float, sigma0: float, time: float) -> float:
    """Exact forward solution for the declared C<0 resolution convention."""
    if not all(math.isfinite(v) for v in (C, sigma0, time)) or C >= 0 or sigma0 <= 0 or time < 0:
        raise ValueError("C<0, sigma0>0 and forward time>=0 required")
    return (sigma0**4-8*C*time)**0.25


def free_carrier_checks() -> dict:
    """Actual finite scalar free example; no interacting reconstruction claim."""
    import numpy as np
    from cg_core.free_covariance import gaussian_phase_channel, reflection_gram
    # Constant scalar mode plus one direction in the l=2 eigenspace, L=1.
    # This probes the full free covariance; it is not a claim that the
    # two-dimensional selection closes under interacting mode multiplication.
    A = np.diag([0., 8.])
    B = np.diag(np.exp(-0.15*np.array([0., 8.])))
    probes = np.array([[1., 1.], [1., -1.]])/math.sqrt(2.)
    gram = reflection_gram(A, math.sqrt(3.)/2., [0.2, 0.7], probes, B)
    rho = np.array([[0.5, 0.5j], [-0.5j, 0.5]])
    state = gaussian_phase_channel(rho, A, 0.3)
    return {"free_reflection_gram_min": float(np.linalg.eigvalsh(gram).min()),
            "phase_state_min": float(np.linalg.eigvalsh(state).min()),
            "phase_trace_error": float(abs(np.trace(state)-np.trace(rho))),
            "mass_squared": 0.75, "internal_eigenvalues": [0., 8.],
            "interacting_reflection_positivity_established": False}


def compute() -> dict:
    """Publish the discrete-flow structure."""
    kL = float(get("kL"))
    M_G = float(get("M_G"))
    M_P = float(get("M_P"))
    tau = float(get("tau"))
    g2 = float(get("g2_MG"))
    R_c = float(get("R_c_star"))
    mgen = float(get("mass_gap_m_gen"))
    generated_ym = get("generated_ym_mass_gap")
    sigma_C = float(get("sigma_C_hubble"))

    # PROPERTY 1 — the semigroup (numerical, machine precision):
    err = semigroup_check(1.0, 0.7)

    # PROPERTY 2 — the analytic β:
    # A declared resolution speed, separate from physical time or a derived
    # mobility. The potential alone does not determine this speed.
    # |C| is a NORMALISATION choice (|C| = 1): it is NOT derived from
    # trace_density and does not enter any closed physical quantity —
    # published as SCALE_CHOICE, not DERIVED.
    C = -1.0                      # |C| = 1: convention (SCALE_CHOICE)
    beta_MG = beta_sigma(C, 1.0 / M_G)

    # PROPERTY 3 — the window-capacity step:
    dln_sigma = 1.0 / kL          # Δlnσ = 1/kL* ≈ 0.40
    N_steps = math.log(sigma_C * M_P) / dln_sigma   # σ₀=1/M_P → σ_C
    step_squared = dln_sigma * dln_sigma
    free_checks = free_carrier_checks()

    # PROPERTY 4 — generated gap and parallel endpoint diagnostics:
    R_MG = 6.0 / (kL * kL)
    m2_long = (8.0 / 3.0) * (R_MG - R_c)      # the tachyon at M_G
    lam_J2 = 14.0 + 8.0 * tau + 2.0 * tau * tau   # the J=2 kinetic > 0
    m_gen_sq = mgen * mgen                     # g2^2 <E>^2 > 0
    radial_mass_squared = float(generated_ym["radial_mass_squared"])
    transverse_mass_squared = float(generated_ym["transverse_mass_squared"])
    curvature_score_overlap = float(generated_ym["curvature_score_overlap"])
    radial_intertwining_residual = float(
        generated_ym["radial_intertwining_residual"])
    gap_squared = float(generated_ym["gap_squared"])
    gap_mass = float(generated_ym["gap"])
    controlling_block = generated_ym["controlling_block"]
    operator_certificate = generated_ym["operator_certificate"]
    interval_certificate = generated_ym["interval_certificate"]
    scale_transport = generated_ym["scale_transport"]
    if not math.isclose(gap_squared,
                        min(radial_mass_squared, transverse_mass_squared),
                        rel_tol=2e-13, abs_tol=0.0):
        raise ValueError("generated Yang--Mills gap is inconsistent with its blocks")
    # The glueball tower ratios — GEOMETRIC (the two-gluon SO(4) Casimir
    # spectrum of qcd_sector, NOT the lattice comparison): 2++/0++ = sqrt2,
    # 0-+ = sqrt(17/8), 0++* = sqrt(18/8) = 3/2.
    tower = {"0++": 1.00,
             "2++": math.sqrt(2.0),
             "0++*": math.sqrt(18.0 / 8.0),
             "0-+": math.sqrt(17.0 / 8.0)}

    pset("discrete_flow_semigroup", err, provenance="DERIVED",
         role="internal",
         note=f"the Gaussian window semigroup T_a*T_b = T_(sqrt(a^2+b^2)) "
              f"verified to {err:.1e} across the mode grid; "
              f"a resolution multiplier identity")
    pset("discrete_flow_beta", beta_MG, provenance="SCALE_CHOICE",
         role="internal",
         note=f"beta(sigma) = -2C sigma^-3 with |C| = 1 a NORMALISATION "
              f"choice; sigma(t)^4=sigma(0)^4-8Ct for forward t and C<0. "
              f"This resolution parametrisation supplies no physical clock.")
    pset("discrete_flow_step", dln_sigma, provenance="DERIVED", role="cg",
         note=f"Delta ln sigma = 1/kL* = {dln_sigma:.4f} — the "
              f"specified sampling in log sigma; its square "
              f"{step_squared:.2f} is not a certified discretisation error")
    gap_spectrum = {
        "generated_yang_mills": {
            "radial_mass_squared": radial_mass_squared,
            "transverse_mass_squared": transverse_mass_squared,
            "curvature_score_overlap": curvature_score_overlap,
            "radial_intertwining_residual": radial_intertwining_residual,
            "gap_squared": gap_squared,
            "gap_mass": gap_mass,
            "controlling_block": controlling_block,
            "operator_certificate": operator_certificate,
            "interval_certificate": interval_certificate,
            "scale_transport": scale_transport,
        },
        "long_root_trigger": m2_long,
        "generator_scale_squared": m_gen_sq,
        "j2_directory_coefficient": lam_J2,
        "glueball_catalogue_ratios": tower,
    }
    pset("discrete_flow_gap_spectrum", gap_spectrum,
         provenance="DERIVED", role="internal",
         dependencies=("generated_ym_mass_gap", "mass_gap_m_gen", "kL",
                       "R_c_star", "tau"),
         note=f"The generated Yang--Mills response has spectral bottom "
              f"Delta_YM^2={gap_squared:.8g}, controlled by the "
              f"{controlling_block} block. Its outward interval lower bound "
              f"is {interval_certificate['complete_gap_squared'][0]:.8g}. "
              f"The long-root trigger, endpoint generator scale, J=2 "
              f"directory and QCD catalogue provide the corresponding "
              f"generated-sector readouts.")
    pset("discrete_flow_reflection_positivity",
         free_checks,
         provenance="DERIVED", role="informational",
         note="Finite free scalar covariance and same-time filtered reflection "
              "Gram; random-phase average is a separate CPTP state map. "
              "Neither establishes interacting or gravitational OS positivity.")
    pset("discrete_flow_status",
         "Gaussian resolution semigroup with specified logarithmic sampling "
         "and resolution speed; generated condensed Yang--Mills spectrum "
         "with radial and coclosed-connection blocks; explicit finite free "
         "reflection-positive covariance.",
         provenance="DERIVED", role="informational",
         note="The resolution multiplier, generated mass operator, state "
              "channel, free covariance and QCD catalogue have distinct "
              "definitions and are published separately.")

    return {"semigroup_err": err, "beta_MG": beta_MG, "dln_sigma": dln_sigma,
            "N_steps": N_steps, "step_squared": step_squared, "m2_long": m2_long,
            "m_gen_sq": m_gen_sq, "lambda_J2": lam_J2, "tower": tower,
            "generated_ym": generated_ym, "gap_spectrum": gap_spectrum,
            "free_carrier_checks": free_checks}


if __name__ == "__main__":
    r = compute()
    print(f"semigroup check    = {r['semigroup_err']:.2e} (machine-precision)")
    print(f"beta(M_G)          = {r['beta_MG']:.3e} (the analytic closed form)")
    print(f"window step dlnσ   = {r['dln_sigma']:.4f}  "
          f"(N steps M_P->sigma_C = {r['N_steps']:.0f})")
    print(f"tachyon m2_long    = {r['m2_long']:.4f} < 0 (the trigger)")
    print(f"generated YM gap^2 = {r['generated_ym']['gap_squared']:.6e} "
          f"({r['generated_ym']['controlling_block']} block)")
    print(f"generated YM gap   = {r['generated_ym']['gap']:.6e} GeV")
    print(f"m_gen^2            = {r['m_gen_sq']:.3e} GeV^2, "
          f"lambda_J2 = {r['lambda_J2']:.4f} (scale and channel readouts)")
    print(f"tower ratios       = " + ", ".join(
        f"{k} {v:.2f}" for k, v in r['tower'].items()))
    print("discrete_flow OK")
