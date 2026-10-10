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

"""Electroweak doublet and neutral-current amplitudes.

The neutral-current approximation uses the effective parameters of
A. Denner, Fortschr. Phys. 41 (1993) 307, Eqs. (8.21)--(8.25), at a
common reference scale. The non-universal heavy-top term follows the
effective couplings in the PDG electroweak review (2024), Eqs. (10.53)
and (10.55). Widths retain its interference with the Born amplitude.
"""
from __future__ import annotations
import math


Z_FERMIONS = (
    # name, colour multiplicity, charge, weak isospin
    ("e", 1, -1.0, -0.5), ("mu", 1, -1.0, -0.5),
    ("tau", 1, -1.0, -0.5), ("nu_e", 1, 0.0, 0.5),
    ("nu_mu", 1, 0.0, 0.5), ("nu_tau", 1, 0.0, 0.5),
    ("u", 3, 2.0 / 3.0, 0.5), ("c", 3, 2.0 / 3.0, 0.5),
    ("d", 3, -1.0 / 3.0, -0.5), ("s", 3, -1.0 / 3.0, -0.5),
    ("b", 3, -1.0 / 3.0, -0.5),
)


def heavy_top_x(G_F: float, mt: float) -> float:
    """Dimensionless heavy-top coefficient G_F m_t^2/(8 sqrt(2) pi^2)."""
    if not math.isfinite(G_F) or G_F <= 0:
        raise ValueError("G_F must be finite and positive")
    if not math.isfinite(mt) or mt < 0:
        raise ValueError("m_t must be finite and nonnegative")
    x = G_F * mt * mt / (8.0 * math.sqrt(2.0) * math.pi**2)
    if not math.isfinite(x):
        raise ValueError("heavy-top coefficient must be finite")
    return x


def leading_rho_bar(G_F: float, mt: float) -> float:
    """Retained heavy-top coefficient, Denner Eq. (8.22).

    The x_t^2 coefficient is the small-Higgs-mass heavy-top limit. This
    expression defines the retained universal resummation; finite Higgs
    and mixed QCD-electroweak terms require separate matching.
    """
    x = heavy_top_x(G_F, mt)
    return 3.0 * x * (1.0 + x * (19.0 - 2.0 * math.pi**2))


def leading_universal_parameters(M_Z: float, alpha_Z: float, G_F: float,
                                 delta_rho_bar: float) -> dict:
    """Common effective neutral-current parameters at the Z reference scale.

    With a=pi alpha_Z/(sqrt(2) G_F M_Z^2), the weak branch satisfies
    sbar^2(1-sbar^2)=a(1-Delta rho_bar). Its neutral-current normalization
    is rho_NC=1/(1-Delta rho_bar), as in Denner Eq. (8.25). The same
    alpha_Z enters the angle, amplitude normalization and QED radiator.
    M_W is the mass readout of this common-scale leading-universal
    relation; alpha_Z is the specified effective input at M_Z.
    """
    if not all(math.isfinite(x) and x > 0 for x in (M_Z, alpha_Z, G_F)):
        raise ValueError("M_Z, alpha_Z and G_F must be finite and positive")
    if not math.isfinite(delta_rho_bar) or not 0 <= delta_rho_bar < 1:
        raise ValueError("Delta rho_bar must lie in [0, 1)")
    a = math.pi * alpha_Z / (math.sqrt(2.0) * G_F * M_Z**2)
    product = a * (1.0 - delta_rho_bar)
    discriminant = 1.0 - 4.0 * product
    if not math.isfinite(product) or product <= 0 or discriminant < 0:
        raise ValueError("leading-universal relation has no real weak branch")
    # Stable quadratic root, including the small-product limit.
    s2_eff = 2.0 * product / (1.0 + math.sqrt(discriminant))
    c2_os = (1.0 - s2_eff) / (1.0 - delta_rho_bar)
    if not 0 < c2_os < 1:
        raise ValueError("leading-universal mass ratio lies outside (0, 1)")
    return {
        "M_W": M_Z * math.sqrt(c2_os),
        "s2_os": 1.0 - c2_os,
        "s2_eff": s2_eff,
        "rho_nc": 1.0 / (1.0 - delta_rho_bar),
    }


def bottom_vertex_width_shift(s2_eff: float, x_t: float) -> float:
    """Relative one-loop bottom-width interference at fixed common inputs.

    For g_V=-1/2+2 sbar^2/3 and g_A=-1/2 the non-universal heavy-top
    amplitude obeys delta g_V=delta g_A=x_t. The common sqrt(rho_NC)
    normalization cancels in the relative width. Terms quadratic in the
    non-universal amplitude are beyond this retained order.
    """
    if not math.isfinite(s2_eff) or not 0 < s2_eff < 0.5:
        raise ValueError("effective weak angle must lie in (0, 1/2)")
    if not math.isfinite(x_t) or x_t < 0:
        raise ValueError("heavy-top coefficient must be finite and nonnegative")
    gv, ga = -0.5 + (2.0 / 3.0) * s2_eff, -0.5
    shift = 2.0 * x_t * (gv + ga) / (gv * gv + ga * ga)
    if shift <= -1:
        raise ValueError("bottom interference gives a nonpositive width")
    return shift


def neutral_current_widths(M_Z: float, s2_eff: float, G_F: float,
                           alpha_Z: float, alpha_s_Z: float, *,
                           rho_nc: float = 1.0, x_t: float = 0.0) -> dict:
    """Massless partial Z widths from one common effective amplitude.

    Gamma_f=N_c G_F M_Z^3 rho_NC/(6 pi sqrt(2)) times the retained
    quadratic form in g_V=T3-2 Q sbar^2 and g_A=T3. The bottom channel
    includes 2 x_t(g_V+g_A). QCD uses the massless non-singlet radiator
    through alpha_s^2 and QED its leading radiator. Their multiplicative
    use is the stated factorized approximation. Finite fermion masses,
    singlet radiators and non-factorizable mixed terms are separate
    contributions. Setting rho_NC=1 and x_t=0 gives the Born baseline.
    """
    if not all(math.isfinite(x) and x > 0 for x in (M_Z, G_F, rho_nc)):
        raise ValueError("M_Z, G_F and rho_NC must be finite and positive")
    if not all(math.isfinite(x) and x >= 0 for x in (alpha_Z, alpha_s_Z)):
        raise ValueError("radiator couplings must be finite and nonnegative")
    bottom_vertex_width_shift(s2_eff, x_t)
    normalization = G_F * M_Z**3 * rho_nc / (6.0 * math.pi * math.sqrt(2.0))
    qcd = 1.0 + alpha_s_Z / math.pi + 1.409 * (alpha_s_Z / math.pi)**2
    widths = {}
    for name, colour, charge, isospin in Z_FERMIONS:
        gv, ga = isospin - 2.0 * charge * s2_eff, isospin
        quadratic = gv * gv + ga * ga
        if name == "b":
            quadratic += 2.0 * x_t * (gv + ga)
        qed = 1.0 + 3.0 * charge**2 * alpha_Z / (4.0 * math.pi)
        widths[name] = colour * normalization * quadratic * qed * (
            qcd if colour == 3 else 1.0)
    widths["l"] = math.fsum(widths[name] for name in ("e", "mu", "tau"))
    widths["nu"] = math.fsum(widths[name] for name in ("nu_e", "nu_mu", "nu_tau"))
    widths["had"] = math.fsum(widths[name] for name in ("u", "c", "d", "s", "b"))
    widths["Z"] = math.fsum(widths[name] for name in ("l", "nu", "had"))
    if not all(math.isfinite(value) and value > 0 for value in widths.values()):
        raise ValueError("neutral-current widths must be finite and positive")
    return widths


def veltman_delta_rho(G_F: float, mt: float, mb: float = 0.0) -> float:
    """Exact one-loop doublet term, including zero and degenerate limits.

    Set s=(mt²+mb²)/2, z=(mt²-mb²)/(mt²+mb²). The bracket is
    4*s*sum(z**(2*n)/((2*n-1)*(2*n+1)), n>=1). This positive series
    avoids subtracting nearly equal terms near the custodial limit.
    """
    if not math.isfinite(G_F) or G_F < 0:
        raise ValueError("G_F must be finite and nonnegative")
    if not all(math.isfinite(m) and m >= 0 for m in (mt, mb)):
        raise ValueError("doublet masses must be finite and nonnegative")
    if mt == mb:
        return 0.0
    large, small = max(mt, mb), min(mt, mb)
    if small == 0:
        bracket = large * large
    else:
        ratio = small / large
        r2 = ratio * ratio
        z = ((large - small) / large) * (1.0 + ratio) / (1.0 + r2)
        if z < 0.25:
            term_power = z * z
            total = 0.0
            for n in range(1, 32):
                term = term_power / ((2 * n - 1) * (2 * n + 1))
                total += term
                if term <= 2e-16 * total:
                    break
                term_power *= z * z
            bracket = 2.0 * large * large * (1.0 + r2) * total
        else:
            # log(m_small/m_large) stays well-defined even if ratio²
            # underflows; then r² log(r) contributes its limiting zero.
            bracket = large * large if ratio == 0 else large * large * (
                1.0 + r2 + 4.0 * r2 * math.log(ratio) / (1.0 - r2))
    return 3.0 * G_F * bracket / (8.0 * math.pi**2 * math.sqrt(2.0))
