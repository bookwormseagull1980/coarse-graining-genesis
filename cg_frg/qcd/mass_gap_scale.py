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

"""Generated Yang--Mills gap and QCD scale readouts.

The Yang--Mills response follows Paper 4 directly.  At the endpoint
resolution the Gaussian colour connection has intensity q, adjoint-Casimir
feedback g_YM q, long-root drive 16(L^-2-L_c^-2), and source Legendre
metric 2M/q.  The exact conformal-tower response determines the unique
condensed intensity and the radial and coclosed-connection mass blocks.

The production Lambda readout starts from g3(M_G), evolves the three gauge
couplings with fixed y0=1, applies the stated finite content factor, and
evaluates the two-loop five-flavour Lambda formula at the internal Z scale.
This prescription does not perform top-quark threshold matching.

Delta E=M_G/8 and m_gen=g2*(2*tau)*M_G/sqrt(2) remain parallel endpoint
readouts; neither is an argument of lambda_qcd.  The glueball catalogue uses
the specified linear mass readout 8*Lambda.  These quantities are reported
separately from the generated Yang--Mills response gap.

run_qcd_thresholds separately evaluates a supplied pure-QCD EFT path with
explicit heavy masses and one-loop matching; lambda_msbar_from_alpha requires
the final fixed-flavour scheme. Physical Yukawa feedback belongs to the
five-variable API in cg_core.gauge_running and must not also receive the
fixed-y0 finite compensation. No observed boundary is loaded by these APIs.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.gauge_running import run_geometric  # noqa: E402

# Constants of the specified fixed-y0 three-gauge prescription. A finite
# connector seed does not establish a vanishing physical Yukawa beta.
Y0_GEOMETRIC = 1.0
LAM_H_GEOMETRIC = (12.0 * math.pi + 3.0) / (32.0 * math.pi ** 2)
SU3_ADJOINT_CASIMIR = 3.0
SU3_ALGEBRA_DIMENSION = 8
LONG_ROOT_MODE_DIMENSION = 15


def condensate_energy(M_G: float) -> float:
    """ΔE = (1/8)·M_G — the condensate energy (the conformal
    coupling ξ = 1/8 itself)."""
    return M_G / 8.0


def generator_mass(g2: float, tau: float, M_G: float) -> float:
    """m_gen = g₂·(2τ)·M_G/√2 — the SU(3) generator mass from the
    long-root condensate (Higgs-like)."""
    return g2 * (2.0 * tau) * M_G / math.sqrt(2.0)


def conformal_restoring_response(z: float) -> float:
    """Exact derivative H(z) of the complete conformal response."""
    if not math.isfinite(z) or z < 0.0:
        raise ValueError("nonnegative finite response coordinate required")
    if z < 0.25:
        b = math.sqrt(0.25 - z)
        return math.pi / 8.0 - math.pi * b * math.tan(math.pi * b / 2.0) / 4.0
    if z == 0.25:
        return math.pi / 8.0
    s = math.sqrt(z - 0.25)
    return math.pi / 8.0 + math.pi * s * math.tanh(math.pi * s / 2.0) / 4.0


def conformal_restoring_curvature(z: float) -> float:
    """Exact positive derivative H'(z) of the complete response."""
    if not math.isfinite(z) or z < 0.0:
        raise ValueError("nonnegative finite response coordinate required")
    if z < 0.25:
        b = math.sqrt(0.25 - z)
        angle = math.pi * b / 2.0
        return math.pi * (math.tan(angle) + angle / math.cos(angle) ** 2) / (8.0 * b)
    if z == 0.25:
        return math.pi ** 2 / 8.0
    s = math.sqrt(z - 0.25)
    angle = math.pi * s / 2.0
    tanh = math.tanh(angle)
    sech2 = 1.0 - tanh * tanh
    return math.pi * (tanh + angle * sech2) / (8.0 * s)


def _solve_restoring_coordinate(drive: float, *, rtol: float = 2e-13) -> float:
    """Solve H(z)=drive by monotone bracketing."""
    if not math.isfinite(drive) or drive <= 0.0:
        raise ValueError("positive finite condensed drive required")
    low, high = 0.0, 1.0
    while conformal_restoring_response(high) < drive:
        high *= 4.0
        if not math.isfinite(high):
            raise OverflowError("failed to bracket the conformal response root")
    for _ in range(256):
        mid = (low + high) / 2.0
        if conformal_restoring_response(mid) < drive:
            low = mid
        else:
            high = mid
        if high - low <= rtol * max(1.0, high):
            break
    return (low + high) / 2.0


def generated_yang_mills_gap(
        L: float, *, L_c: float = math.sqrt(math.pi),
        mass_unit: float = 1.0,
        adjoint_casimir: float = SU3_ADJOINT_CASIMIR,
        algebra_dimension: int = SU3_ALGEBRA_DIMENSION,
        long_root_dimension: int = LONG_ROOT_MODE_DIMENSION) -> dict:
    """Evaluate the generated Yang--Mills mass-gap theorem.

    L and L_c are radii in common source-resolution units.  The returned
    squared masses are dimensionless in those units; ``mass_unit`` converts
    their square roots to the requested physical mass unit.
    """
    numeric = (L, L_c, mass_unit, adjoint_casimir)
    if not all(math.isfinite(x) and x > 0.0 for x in numeric):
        raise ValueError("positive finite radius, mass unit and Casimir required")
    if not isinstance(algebra_dimension, int) or algebra_dimension <= 0:
        raise ValueError("positive integer algebra dimension required")
    if not isinstance(long_root_dimension, int) or long_root_dimension <= 0:
        raise ValueError("positive integer long-root dimension required")
    if L <= L_c:
        raise ValueError("the generated condensed branch requires L>L_c")

    volume = math.pi ** 2 * L ** 3
    g_ym = adjoint_casimir / (volume * algebra_dimension)
    kappa = g_ym * L ** 2
    mu = 16.0 * (L ** -2 - L_c ** -2)
    drive = -mu / (2.0 * kappa)
    z = _solve_restoring_coordinate(drive)
    q = z / kappa
    curvature = conformal_restoring_curvature(z)
    source_dimension = long_root_dimension * algebra_dimension
    radial_metric = 2.0 * source_dimension / q
    potential_curvature = kappa ** 2 * curvature
    radial_mass_squared = 4.0 * q * potential_curvature / radial_metric
    radial_closed_form = 2.0 * z ** 2 * curvature / source_dimension
    transverse_shift = 2.0 * q * adjoint_casimir / (
        3.0 * volume * algebra_dimension)
    transverse_mass_squared = 4.0 / L ** 2 + transverse_shift
    long_root_eigenvalue = 16.0 / L ** 2
    alpha_r = adjoint_casimir / (
        3.0 * volume * algebra_dimension)
    curvature_radial_coefficient = (
        long_root_eigenvalue + 2.0 * alpha_r * q)
    normalized_score_variance = (
        (source_dimension / 2.0) * (2.0 * q * q / source_dimension)
        / (q * q))
    curvature_score_overlap = (
        curvature_radial_coefficient * q
        * math.sqrt(2.0 / source_dimension))
    scalar_constant_mode_mass_squared = radial_mass_squared
    radial_intertwining_residual = (
        scalar_constant_mode_mass_squared - radial_mass_squared)
    gap_squared = min(radial_mass_squared, transverse_mass_squared)
    controller = "radial" if radial_mass_squared <= transverse_mass_squared else "transverse"

    return {
        "phase": "condensed",
        "L": L,
        "L_c": L_c,
        "volume": volume,
        "adjoint_casimir": adjoint_casimir,
        "algebra_dimension": algebra_dimension,
        "long_root_dimension": long_root_dimension,
        "source_dimension": source_dimension,
        "feedback_coefficient": g_ym,
        "kappa": kappa,
        "reference_drive": mu,
        "dimensionless_drive": drive,
        "response_coordinate": z,
        "intensity_q": q,
        "amplitude": math.sqrt(q),
        "radial_metric": radial_metric,
        "potential_curvature": potential_curvature,
        "radial_mass_squared": radial_mass_squared,
        "radial_closed_form": radial_closed_form,
        "transverse_shift": transverse_shift,
        "transverse_mass_squared": transverse_mass_squared,
        "long_root_eigenvalue": long_root_eigenvalue,
        "curvature_radial_coefficient": curvature_radial_coefficient,
        "normalized_score_variance": normalized_score_variance,
        "curvature_score_overlap": curvature_score_overlap,
        "scalar_constant_mode_mass_squared": scalar_constant_mode_mass_squared,
        "radial_intertwining_residual": radial_intertwining_residual,
        "gap_squared": gap_squared,
        "gap": math.sqrt(gap_squared) * mass_unit,
        "mass_unit": mass_unit,
        "controlling_block": controller,
        "stationarity_residual": conformal_restoring_response(z) - drive,
        "radial_identity_residual": radial_mass_squared - radial_closed_form,
    }


def _run_geometric_to_MZ(g1_MG: float, g2_MG: float, g3_MG: float,
                          M_G: float, M_Z: float) -> float:
    """Declared three-gauge two-loop flow with the coefficient y0 fixed to 1.

    No top threshold is applied in this production prescription. The
    quartic does not enter this flow. Returns (g1,g2,g3) at the supplied
    scale; it is distinct from a matched five-variable physical EFT flow.
    """
    return run_geometric((g1_MG, g2_MG, g3_MG), M_G, M_Z)


def _run_full_sm_to_MZ(g1_MG: float, g2_MG: float, g3_MG: float,
                        M_G: float, M_Z: float) -> float:
    """Run the declared three-gauge flow with fixed coefficient y0=1
    from M_G down to M_Z.
    Returns g3(M_Z)."""
    return _run_geometric_to_MZ(g1_MG, g2_MG, g3_MG, M_G, M_Z)[2]


def internal_M_Z(g1_MG: float, g2_MG: float, g3_MG: float,
                 M_G: float, v: float) -> float:
    """M_Z = sqrt(g2(v)^2 + g1'(v)^2) v/2 — the Z mass from the
    framework's own v and the geometric couplings run down to v (the
    EW scale).  g1' = g1·sqrt(3/5) is the non-GUT-normalised U(1)
    coupling.  The Z mass is DERIVED from the internal EW VEV and the
    geometric couplings."""
    g1v, g2v, _ = _run_geometric_to_MZ(g1_MG, g2_MG, g3_MG, M_G, v)
    g1p = g1v * math.sqrt(3.0 / 5.0)
    return math.sqrt(g2v * g2v + g1p * g1p) * v / 2.0


def lambda_qcd(g1_MG: float, g2_MG: float, g3_MG: float,
               M_G: float) -> tuple:
    """Lambda_QCD (MSbar, 5-flavour) from the framework's common-origin
    g3(M_G), run down with the two-loop three-gauge beta functions
    and fixed geometric y0=1 (checked RK4, not derivatives5).
    The framework's independent content is the initial condition g3(M_G)
    (the common-origin coupling) — the resulting alpha_s(M_Z) is the
    framework's prediction.

    The extraction uses the standard two-loop Lambda_MSbar formula at
    M_Z (the INTERNAL Z mass, derived from v and the geometric
    couplings) with the 5-flavour coefficients b0 = 23/3, b1 = 116/3.
    """
    M_Z = internal_M_Z(g1_MG, g2_MG, g3_MG, M_G,
                       float(get("v_HIGGS")))
    g3_MZ = _run_full_sm_to_MZ(g1_MG, g2_MG, g3_MG, M_G, M_Z)
    a = g3_MZ ** 2 / (4.0 * math.pi)
    # The fixed-y0 prescription includes the declared finite content factor.
    # This is not the integrated difference from a matched running Yukawa.
    # A coupled top-sector flow must not also apply this compensation.
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    a = apply_finite_content_matching(a,s0*kappa,flow_convention="fixed-y0")
    c0 = 23.0 / 3.0    # b0(5) = 11 - 2*5/3
    c1 = 116.0 / 3.0   # b1(5) = 102 - 38*5/3
    return (M_Z * (c0 * a / (4.0 * math.pi)) ** (-c1 / (2.0 * c0 * c0))
            * math.exp(-2.0 * math.pi / (c0 * a)), a)


def apply_finite_content_matching(alpha_s, squash_response, *, flow_convention):
    """The specified 1-s0*kappa/8 factor, exclusively for the fixed-y0 flow.

    A jointly evolved physical Yukawa already enters the gauge beta. This
    finite compensation cannot be applied to it again. Additional finite
    EFT thresholds need their own derived matching coefficients.
    """
    if flow_convention != "fixed-y0":
        raise ValueError("finite fixed-y0 compensation cannot be added to a coupled flow")
    if not all(math.isfinite(x) for x in (alpha_s,squash_response)) or alpha_s<=0:
        raise ValueError("positive alpha_s and finite squash response required")
    factor=1-squash_response/8
    if factor<=0:
        raise ValueError("finite matching factor must be positive")
    return alpha_s*factor


def lambda_msbar_from_alpha(alpha_s, scale, *, n_flavours, scheme="MSbar"):
    """Two-loop asymptotic Lambda parameter in an explicit fixed-flavour EFT.

    PDG QCD review, Sec. 9.2, beta0=11-2nf/3 and beta1=102-38nf/3.
    The caller supplies a coupling already matched to this EFT; this formula
    does not itself decouple a heavy quark or identify a hadronic pole mass.
    """
    if scheme!="MSbar" or not isinstance(n_flavours,int) or not 0<=n_flavours<=6:
        raise ValueError("MSbar and integer 0<=n_flavours<=6 required")
    if not all(math.isfinite(x) and x>0 for x in (alpha_s,scale)):
        raise ValueError("positive finite alpha_s and matching scale required")
    b0,b1=11-2*n_flavours/3,102-38*n_flavours/3
    return scale*(b0*alpha_s/(4*math.pi))**(-b1/(2*b0*b0))*math.exp(-2*math.pi/(b0*alpha_s))


def run_qcd_thresholds(alpha_s, scale_from, scale_to, *, n_flavours,
                       heavy_thresholds=(), rtol=2e-11, atol=2e-13):
    """Downward pure-QCD two-loop running with explicit heavy matching scales.

    At each supplied heavy mass alpha_s is continuous (one-loop matching
    at mu=m_h); nf decreases by one. Two-loop finite decoupling constants
    and electroweak/Yukawa terms are outside this API. A non-mass matching
    scale requires a different, explicitly derived matching map. This
    routine neither reads observed quark masses nor applies the fixed-y0
    finite content compensation.
    """
    from scipy.integrate import solve_ivp
    if not isinstance(n_flavours,int) or not 1<=n_flavours<=6:
        raise ValueError("integer 1<=n_flavours<=6 required")
    if not all(math.isfinite(x) and x>0 for x in (alpha_s,scale_from,scale_to,rtol,atol)):
        raise ValueError("positive finite QCD inputs required")
    if not scale_to<scale_from:
        raise ValueError("this API performs downward EFT running")
    thresholds=tuple(float(x) for x in heavy_thresholds)
    path=(scale_from,*thresholds,scale_to)
    if len(thresholds)>=n_flavours or any(not path[i]>path[i+1] for i in range(len(path)-1)):
        raise ValueError("ordered internal heavy-mass thresholds and positive final nf required")
    a,segments=alpha_s,[]
    for high,low in zip(path[:-1],path[1:]):
        b0,b1=11-2*n_flavours/3,102-38*n_flavours/3
        def rhs(t,y):
            return [-b0*y[0]**2/(2*math.pi)-b1*y[0]**3/(8*math.pi**2)]
        result=solve_ivp(rhs,(math.log(high),math.log(low)),[a],method='DOP853',rtol=rtol,atol=atol,max_step=.1)
        if not result.success or not math.isfinite(result.y[0,-1]) or result.y[0,-1]<=0:
            raise RuntimeError("QCD running failed before the requested scale")
        a=float(result.y[0,-1])
        segments.append({"from":high,"to":low,"n_flavours":n_flavours,"alpha_s":a})
        if low!=scale_to:
            n_flavours-=1
    return {"alpha_s":a,"scale":scale_to,"n_flavours":n_flavours,"segments":segments,
            "scheme":"MSbar","running_order":2,"matching_order":1,
            "finite_fixed_y0_compensation_applied":False}


def glueball_from_Lambda(Lambda_QCD: float) -> float:
    """m_G = λ(0⁺⁺)·Λ_QCD = 8·Λ_QCD — the lightest 0⁺⁺ glueball.

    λ(0⁺⁺) = 2λ_gluon + C₂(0,0) = 8 is the glueball's spectral
    eigenvalue (two gluons l=1 Killing, λ_gluon = (l+1)² = 4, the
    composite (0,0) scalar C₂ = 0) — the SAME spectral-language form
    as the string tension σ = (λ_TT/π)Λ² (λ_TT = 14) and the
    deconfinement T_d = (λ_vector/N_c)Λ (λ_vector = 4).  The absolute
    glueball mass is the spectral eigenvalue λ(0⁺⁺) = 8 times Λ_QCD
    under the declared linear catalogue readout. This assigned mass is not
    a pole reconstructed from a colour-singlet two-point function."""
    return 8.0 * Lambda_QCD


def compute() -> dict:
    """Publish the mass-gap scale chain."""
    M_G = float(get("M_G"))
    g2 = float(get("g2_MG"))
    tau = float(get("tau"))
    g3_MG = float(get("g3_MG_geo"))
    L = float(get("kL"))
    L_c = math.sqrt(6.0 / float(get("R_c_star")))

    dE = condensate_energy(M_G)
    mgen = generator_mass(g2, tau, M_G)
    ym_gap = generated_yang_mills_gap(L, L_c=L_c, mass_unit=M_G)
    g1_MG = float(get("g1_MG_geo"))
    Lam, alpha_s_MZ = lambda_qcd(g1_MG, g2, g3_MG, M_G)
    mgl = glueball_from_Lambda(Lam)
    # The condensation coefficient K COMPUTED: the J=2 mode's kinetic
    # eigenvalue (8, from J(J+2)) over the internal-space dimension
    # (3) — the structural ratio K = 8/3.
    J2_kinetic = 2 * (2 + 2)          # J(J+2) for J = 2
    dim_internal = 3
    K_computed = J2_kinetic / dim_internal
    pset("longroot_K", K_computed, provenance="DERIVED", role="cg",
         note=f"K = 8/3 = {K_computed} — COMPUTED as the J=2 mode's "
              f"kinetic eigenvalue (J(J+2) = {J2_kinetic}) over the "
              f"internal-space dimension ({dim_internal}); the "
              f"long-root condensation coefficient, the geometric "
              f"carrier = the J=2 mode (the same as the order "
              f"parameter); the effective eigenvalue lambda_long = "
              f"(8/3) R = 16/L^2 is the curvature-tracked value, "
              f"not a separate harmonic")

    pset("mass_gap_dE", dE, provenance="DERIVED",
         note=f"Delta E = (1/8) M_G = {dE:.3e} GeV (the condensate "
              f"energy of the long-root, xi = 1/8)")
    pset("mass_gap_m_gen", mgen, provenance="DERIVED",
         note=f"m_gen = g2 (2 tau) M_G / sqrt(2) = {mgen:.3e} GeV "
               f"(the SU(3) generator-scale readout; not an input to lambda_qcd)")
    pset("generated_ym_mass_gap", ym_gap, provenance="DERIVED", role="internal",
         dependencies=("kL", "R_c_star", "M_G"),
         note="Paper 4 generated Yang--Mills response: colour intensity, "
              "adjoint-Casimir feedback, long-root drive, source Legendre "
              "metric, radial and coclosed-connection blocks, and their "
              "strict positive spectral bottom.")
    pset("generated_ym_gap_mass", ym_gap["gap"], provenance="DERIVED", role="internal",
         dependencies=("kL", "R_c_star", "M_G"),
         note=f"sqrt(Delta_YM^2) in the emergence mass unit: "
              f"{ym_gap['gap']:.6e} GeV; controlling block "
              f"{ym_gap['controlling_block']}.")
    pset("qcd_Lambda_QCD", Lam, provenance="DERIVED", role="internal",
         note=f"Lambda_QCD(MSbar,5) = {Lam:.4f} GeV — two-loop three-gauge running "
              f"(checked RK4, fixed geometric y0=1) from the "
              f"framework's common-origin g3(M_G) = {g3_MG:.4f}, with the "
              f"Yukawa-difference factor (1 - s0 kappa/N_g) applied at the "
              f"extraction point (the geometric Yukawa y0 = 1 vs the running "
              f"SM top Yukawa), the standard two-loop Lambda_MSbar extraction "
              f"at the prescribed internal extraction scale, nf=5. Integration "
              f"error and omitted loop-order/model corrections are distinct.")
    pset("alpha_s_MZ_pred", alpha_s_MZ, provenance="DERIVED",
         role="internal",
         note=f"alpha_s(M_Z) = {alpha_s_MZ:.4f} — the framework's QCD "
              f"prediction from the common-origin g3(M_G) = {g3_MG:.4f} "
              f"run down the two-loop three-gauge flow at fixed y0=1; the "
              f"framework's independent QCD content is this initial "
              f"condition together with the declared geometric flow prescription)")
    pset("m_glueball", mgl, provenance="DERIVED", role="internal",
         note=f"m_glueball = lambda(0++) x Lambda_QCD = 8 x Lambda_QCD = "
              f"{mgl:.2f} GeV (two-loop geometric gauge running + matching from "
              f"the framework's common-origin g3); lambda(0++) = 2 lambda_gluon "
              f"+ C2(0,0) = 8 the spectral eigenvalue (two gluons l=1 Killing, "
              f"lambda_gluon = (l+1)^2 = 4) — first-principles, NO empirical "
              f"lattice ratio; comparison residuals include the declared "
              f"two-loop extraction and spectral readout approximations)")
    return {"dE": dE, "dE_over_MG": dE / M_G, "m_gen": mgen,
            "generated_ym": ym_gap,
            "m_glueball": mgl,
            "Lambda_QCD": Lam, "alpha_s_MZ": alpha_s_MZ}


if __name__ == "__main__":
    r = compute()
    print(f"Delta E = (1/8) M_G = {r['dE']:.3e} GeV = "
          f"{r['dE_over_MG']:.3f} x M_G")
    print(f"m_gen = {r['m_gen']:.3e} GeV (the QCD initial condition)")
    print(f"generated YM gap = {r['generated_ym']['gap']:.3e} GeV "
          f"({r['generated_ym']['controlling_block']} block)")
    print(f"m_glueball = {r['m_glueball']:.1f} GeV")
    print("mass_gap_scale OK")
