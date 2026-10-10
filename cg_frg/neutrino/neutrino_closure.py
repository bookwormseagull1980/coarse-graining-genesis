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
cg_frg/neutrino/neutrino_closure.py — V5.0: the Weinberg neutrino
texture and the CKM |V_us| Gatto relation
=================================================================

PURPOSE
-----------------------------------
The neutrino masses close through the Weinberg scale and two
hypercharge-trace hierarchy ratios:

  1. THE WEINBERG OPERATOR (dimension-5): with the 2π-family
     scale M = k_GUT/(2π)²:

        m_ν3 = v²·(2π)²/k_GUT·(1 + s0·κ) = 0.0502 eV

     (the (2π)² is the Euclidean period squared — the same thread
     as ε = e^{1/(2π)} of the EW ratio, the 2L, the amplitude; the
     J=2 squash seesaw factor (1+s0·κ) is the level-transfer
     correction).

  2. THE HYPERCHARGE-TRACE TEXTURE:

        m_ν1/m_ν2 = 1/Tr(Y²) = 3/10,
        m_ν2/m_ν3 = 1/(sqrt(3)Tr(Y²)).

     The flavour extension uses sin²θ12=m_ν1/m_ν2=3/10.

THE CKM |V_us| (Gatto × LZ hierarchy)
-------------------------------------
The leading Cabibbo prescription uses the geometric input
r_G = exp(-2 alpha_dn) (3/2)^2 and |V_us| = sqrt(r_G).
The absolute strange-to-down mass ratio is exp(2 alpha_sd), with
alpha_sd = alpha_dn - kL_CMB/6. These are distinct readouts.
The interference form is returned separately at the supplied phase.

TEXTURE ASSIGNMENT
------------------
The charged-fermion hierarchy uses the LZ ladder.  The neutrino sector
uses the Weinberg operator with the two-period family scale and the
hypercharge-trace mass texture.  The PMNS angles are the flavour
extension associated with that neutrino texture.

THE NEUTRINO HIERARCHY (the hypercharge trace)
-----------------------------------------------
The mass RATIOS close through the SM hypercharge trace
Tr(Y²) = 10/3 (the same trace that enters the gauge coupling
relations via the κ function):

    m_ν1/m_ν2 = 1/Tr(Y²) = 3/10 = 0.30   (the solar ratio — and
              sin²θ12 = m_ν1/m_ν2 closes the PMNS solar angle)
    m_ν2/m_ν3 = 1/(√3·Tr(Y²)) = 0.1732

The ratios are geometric — they originate from the hypercharge
trace of one complete generation.

THE PMNS
--------
The neutrino mass-matrix structure with the 2π imprint:

    sin²θ12 = m_ν1/m_ν2 = 3/10   (the solar angle = the mass ratio,
                                   the light-pair mixing of the
                                   diagonalisation)
    sin²θ23 = 1/2 + Tr(T₃²)/(2π)² = 0.5507
    sin²θ13 = (1/(2π)²)·(√3/2) = 0.02194

The solar texture sets sin²θ12=m_ν1/m_ν2=3/10.  Assembly and
diagonalisation of the Weinberg mass matrix verify the same eigenvalue
ratio in neutrino_mass_matrix.py.
The θ13 texture sin²θ13 = (1/(2π)²)·(√3/2) = 0.02194 combines
the Euclidean period factor (1/(2π)²), also used in the GW ratio
r = (1/2π)² and perturbation Δ²_0 = (1/2)(1/2π)², with the
internal geometry factor √3/2 = sin(π/3) associated with the
S³→RP³ Z₂-quotient projection.

OSCILLATION COMPARISON LAYER
----------------------------
The absolute masses define the rest-mass texture.  The raw mass-squared
split is published explicitly.  The solar comparison additionally assumes
the phenomenological propagation rule

    m_ν2^osc = m_ν2 (1 + n_s^tilt),   n_s^tilt = 1 - n_s = τ·7/4 .

The spectral tilt is fixed earlier in the chain, but its insertion here
is an additional assumption.  This rule has not been derived from an
effective neutrino propagation operator, and its correspondence with
parameters inferred by oscillation fits remains to be established.
The absolute-mass, dark-energy, CMB, and mass-sum branches retain the
rest-mass texture without this correction.

IMPLEMENTATION
-------------
The closure uses the framework's internal v, k_GUT, the alpha
ladder and the hypercharge traces
Tr(Y²) = 10/3, Tr(T₃²) = 2 (sm_content).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition


# m_nu3 (1+s0·κ) seesaw factor is the
# level-transfer conservation charge c=+1 (v·m_ν3 = const) of
# squash_level_transfer: v→(1−s0κ), M_R→(1−3s0κ) force m_ν3→(1+s0κ).
# See epsilon_ratio SOURCE OF THE CORRECTION FACTORS.
def weinberg_m3(v: float, k_GUT: float) -> float:
    """m_ν3 = v²·(2π)²/k_GUT·(1 + s0·κ) — the Weinberg operator with
    the 2π family scale (eV; v and k_GUT in GeV), with the J=2 squash
    seesaw-scale correction : the same s0·κ as v's
    (1−s0·κ) in epsilon_ratio — the squash level transfer (EW −s0·κ
    ↔ seesaw +s0·κ).  Brings m_ν3 to 0.0502 eV and Δm²_31 to 0.00251
    (SM, −0.2%)."""
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    return v * v * (2.0 * math.pi) ** 2 / k_GUT * (1.0 + s0 * kappa) * 1e9


def ckm_vus(a_up: float, a_dn: float, delta_12: float = 0.2) -> dict:
    """Leading Cabibbo readout and the separately specified interference form.

    The factors (3/2)^2 and (1/2)^2 use |Y_d|/|Y_u|=1/2.
    The first input is r_G, distinct from the absolute down-to-strange
    mass ratio. Dictionary keys md_ms and mu_mc retain the numerical API.
    The supplied relative phase belongs only to the interference form.
    """
    r = (1.0 / 3.0) / (2.0 / 3.0)  # |Y_d|/|Y_u| = 1/2
    md_ms = math.exp(-2.0 * a_dn) * (1.0 + r) ** 2
    mu_mc = math.exp(-2.0 * a_up) * (1.0 - r) ** 2
    sqrt_md_ms = math.sqrt(md_ms)
    sqrt_mu_mc = math.sqrt(mu_mc)
    re = sqrt_md_ms - math.cos(delta_12) * sqrt_mu_mc
    im = math.sin(delta_12) * sqrt_mu_mc
    return {"md_ms": md_ms, "mu_mc": mu_mc, "Vus_dominant": sqrt_md_ms,
            "Vus_full": abs(complex(re, im))}


def oscillation_splittings(m1: float, m2: float, m3: float,
                           ns_tilt: float) -> dict:
    """Static splittings and the specified unit-amplitude P2 source readout.

    The scalar self-energy Delta H = zeta*m2^2*((1+ns_tilt)^2-1)*P2/(2E)
    gives m2_osc=m2*(1+ns_tilt) at zeta=1. P2 projects onto the labelled
    second vacuum mass column. The propagation module implements this
    operator and its complex-conjugate antineutrino transformation.
    A physical environmental coupling, profile and experimental propagation
    calculation supply the interpretation of this comparison. Thermal
    cosmological populations use the static masses m1,m2,m3.
    """
    m2_osc = m2 * (1.0 + ns_tilt)
    dm21_raw = m2 * m2 - m1 * m1
    dm21_osc = m2_osc * m2_osc - m1 * m1
    dm31 = m3 * m3 - m1 * m1
    return {"m2_osc": m2_osc, "dm21_raw": dm21_raw,
            "dm21_osc": dm21_osc, "dm31": dm31}


def compute() -> dict:
    """Publish the neutrino closure, the hierarchy ratios, the PMNS
    and the CKM |V_us|."""
    v = get("v_HIGGS")           # the framework's own VEV (GeV)
    k_GUT = get("k_GUT")
    a_up = get("alpha_up")
    a_dn = get("alpha_down")
    ns_tilt = get("ns_tilt")

    m3 = weinberg_m3(v, k_GUT)
    # The hierarchy ratios (the hypercharge trace) — DEFINED FIRST.
    tr_y2 = 10.0 / 3.0
    r12 = 1.0 / tr_y2          # m1/m2 = 3/10
    r23 = 1.0 / (math.sqrt(3.0) * tr_y2)   # m2/m3 = 0.1732
    # The two hypercharge-trace ratios fix the absolute mass texture.
    m1 = r12 * r23 * m3
    m2 = m1 / r12               # = m3·r23 (consistent with the hierarchy)
    s12 = m1 / m2               # = r12 = 3/10 (the solar ratio, exact)
    Vus = ckm_vus(a_up, a_dn)

    # The PMNS (the mass-matrix structure + 2π imprint).
    tr_t32 = 2.0               # Tr(T₃²) for the SM content
    zp2 = 1.0 / (2.0 * math.pi) ** 2       # (1/2π)² = 0.0253
    s12_pmns = r12             # sin²θ12 = m1/m2 = 3/10 (the solar = mass ratio)
    s23_pmns = 0.5 + tr_t32 * zp2
    s13_pmns = zp2 * math.sqrt(3.0) / 2.0
    osc = oscillation_splittings(m1, m2, m3, ns_tilt)

    pset("m_nu3", m3, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "k_GUT", "tau"),
         note=f"m_nu3 = v^2 (2pi)^2/k_GUT (1 + s0 kappa) = {m3:.4f} eV "
              f"(the Weinberg 2pi family, with the seesaw level-transfer "
              f"factor (1 + s0 kappa): the seesaw mass carries +s0 kappa "
              f"while the electroweak scale v carries -s0 kappa)")
    pset("m_nu1", m1, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "k_GUT", "tau"),
         note=f"m_nu1 = m_nu3*r12*r23 = {m1:.4f} eV from the two "
              f"hypercharge-trace ratios")
    pset("m_nu2", m2, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "k_GUT", "tau"),
         note=f"m_nu2 = m_nu3*r23 = {m2:.4f} eV (the hypercharge-trace "
              f"hierarchy, consistent with m1/m2 = 3/10)")
    pset("sin2_theta12", s12, provenance="DERIVED", role="cg",
         dependencies=("v_HIGGS", "k_GUT", "tau"),
         note=f"sin2(theta12) = m_nu1/m_nu2 = {s12:.2f} (the solar, closed)")
    pset("mnu_ratio_12", r12, provenance="DERIVED",
         dependencies=(),
         note=f"m_nu1/m_nu2 = 1/Tr(Y^2) = 3/10 (the hypercharge trace)")
    pset("mnu_ratio_23", r23, provenance="DERIVED", role="cg",
         dependencies=(),
         note=f"m_nu2/m_nu3 = 1/(sqrt(3) Tr(Y^2)) = {r23:.4f}")
    pset("m_nu2_osc", osc["m2_osc"], provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "k_GUT", "tau", "ns_tilt"),
         note=f"m_nu2_osc = m_nu2*(1 + ns_tilt) = {osc['m2_osc']:.6f} eV "
              f"(unit-amplitude scalar P2 self-energy; "
              f"ns_tilt = 1 - n_s = {ns_tilt:.6f}; environmental source "
              f"coupling and profile are supplied propagation data; "
              f"thermal cosmology uses the static mass m_nu2)")
    pset("Delta_m21_sq_raw", osc["dm21_raw"], provenance="DERIVED",
         role="internal",
         dependencies=("v_HIGGS", "k_GUT", "tau"),
         note=f"raw rest-mass split m_nu2^2 - m_nu1^2 = "
               f"{osc['dm21_raw']:.6e} eV^2 from the absolute mass texture")
    pset("Delta_m21_sq_osc", osc["dm21_osc"], provenance="DERIVED",
         role="comparison",
         dependencies=("v_HIGGS", "k_GUT", "tau", "ns_tilt"),
         note=f"solar propagation ansatz = (m_nu2*(1+ns_tilt))^2 - "
              f"m_nu1^2 = {osc['dm21_osc']:.6e} eV^2; unit-amplitude "
              f"scalar P2 self-energy with ns_tilt = 1 - n_s; "
              f"comparison with oscillation fits requires the environmental "
              f"coupling and the actual propagation profile")
    pset("Delta_m31_sq", osc["dm31"], provenance="DERIVED",
         role="comparison",
         dependencies=("v_HIGGS", "k_GUT", "tau"),
         note=f"atmospheric oscillation split m_nu3^2 - m_nu1^2 = "
               f"{osc['dm31']:.6e} eV^2 from the absolute mass eigenvalues; "
               f"reported for comparison with the measured atmospheric split")
    pset("sin2_theta13", s13_pmns, provenance="DERIVED", role="cg",
         dependencies=(),
         note=f"sin2(theta13) = (1/2pi)^2 sqrt(3)/2 = {s13_pmns:.4f} (the "
              f"2pi imprint)")
    pset("sin2_theta23", s23_pmns, provenance="DERIVED", role="cg",
         dependencies=(),
         note=f"sin2(theta23) = 1/2 + Tr(T3^2)/(2pi)^2 = {s23_pmns:.4f}")
    pset("md_over_ms_geo", Vus["md_ms"], provenance="DERIVED",
         role="cg",
         dependencies=("alpha_down",),
         definition=QuantityDefinition(
             object="Cabibbo source ratio r_G", unit="dimensionless",
             carrier="three-generation quark flavour space",
             operator="hypercharge-weighted down-sector ladder readout",
             source="elementary scalar connector", projection="leading 1-2 mixing",
             normalization="exp(-2 alpha_down) (3/2)^2",
             scheme="geometric endpoint prescription", order="leading mixing",
             assumptions=("assigned leading Cabibbo readout",),
             error_kind="floating-point central value; model sensitivity separate"),
        note=f"Cabibbo input r_G = e^(-2 alpha_dn) (1+|Y_d|/|Y_u|)^2 "
              f"= {Vus['md_ms']:.5f}; the absolute mass ratio is "
              f"exp(-2 alpha_sd), supplied by the mass ladder")
    pset("V_us_geo", Vus["Vus_dominant"], provenance="DERIVED",
         role="cg",
         dependencies=("alpha_down",),
         note=f"|V_us| = sqrt(r_G) = {Vus['Vus_dominant']:.4f} (the "
              f"assigned leading Cabibbo readout); the interference form (delta12 = "
              f"0.2) gives {Vus['Vus_full']:.4f}")
    return {"m_nu3": m3, "m_nu2": m2, "m_nu1": m1, "sin2_theta12": s12,
            "r12": r12, "r23": r23, "s12_pmns": s12_pmns,
            "s23_pmns": s23_pmns, "s13_pmns": s13_pmns,
            "m_nu2_osc": osc["m2_osc"],
            "Delta_m21_sq_raw": osc["dm21_raw"],
            "Delta_m21_sq_osc": osc["dm21_osc"],
            "Delta_m31_sq": osc["dm31"],
            "sum_m_nu": m1 + m2 + m3,
            "md_ms": Vus["md_ms"], "mu_mc": Vus["mu_mc"],
            "V_us": Vus["Vus_dominant"], "V_us_full": Vus["Vus_full"],
            "neutrino_boundary": "the PMNS angles are the neutrino "
                               "mass-matrix structure (the hypercharge trace "
                               "hierarchy sin2(theta12)=m1/m2=3/10 + the 2pi "
                               "imprint for theta13/theta23)"}


if __name__ == "__main__":
    r = compute()
    print(f"m_nu3 = {r['m_nu3']:.4f} eV (Weinberg)")
    print(f"m_nu2 = {r['m_nu2']:.4f} eV (hypercharge trace)")
    print(f"sin^2 theta12 = m1/m2 = {r['sin2_theta12']:.2f}")
    print(f"hierarchy: m1/m2 = {r['r12']:.3f}, m2/m3 = {r['r23']:.4f}")
    print(f"oscillation: raw Delta_m21^2 = {r['Delta_m21_sq_raw']:.6e} eV^2, "
          f"tilt-dressed Delta_m21^2 = {r['Delta_m21_sq_osc']:.6e} eV^2, "
          f"Delta_m31^2 = {r['Delta_m31_sq']:.6e} eV^2")
    print(f"PMNS: s12 = {r['s12_pmns']:.3f}, s23 = {r['s23_pmns']:.4f}, "
          f"s13 = {r['s13_pmns']:.4f}")
    print(f"mixing source ratios: r_G = {r['md_ms']:.5f}, r_up = {r['mu_mc']:.6f}")
    print(f"|V_us| = sqrt(r_G) = {r['V_us']:.4f}; interference form = "
          f"{r['V_us_full']:.4f}")
    print(f"boundary: {r['neutrino_boundary']}")
    print("neutrino_closure OK")
