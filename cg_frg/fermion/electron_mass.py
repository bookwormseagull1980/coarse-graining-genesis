# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#
#  DOI records:
#    [Software] 10.5281/zenodo.22067006
#    [Paper I]  10.5281/zenodo.22067118
#    [Paper II] 10.5281/zenodo.22067469
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#         DOI: 10.5281/zenodo.22067118
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
#         DOI: 10.5281/zenodo.22067469
# =============================================================================

"""
cg_frg/fermion/electron_mass.py — V4.0: the absolute electron mass
closure
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The electron mass is the lightest charged fermion mass.  In the
framework it closes through the Planck-anchored exponential chain:

    m_e = M_P · e^{−20·kL}·(1 − s0·κ) = 0.510 MeV
    (the low-scale squash correction (1−s0·κ) is the SAME factor as
    v's; the quoted value is the V4.0 fixed-point result — run-time
    value in cg_params.json)

The power 20 = 4×5: the Yukawa cascade (4 mixing steps of the
spectral cascade) × the 5 species of one generation (the content
factor) — the same counting as the Λ density's v¹⁰ (5×2).

STRUCTURAL CONTENT OF 20 = 4×5:
  The factor 4 = d+1, the internal dimension d = 3 plus one — the
  four levels of the spectral cascade (the 4D counting).  The
  factor 5 = ΣY²·Δ_f, the hypercharge capacity ΣY² = 10/3 times
  the fermion conformal weight Δ_f = d/2 = 3/2, which equals the
  five fermion representations of one generation (the content
  factor).  The product, not the sum, appears because each of the
  four cascade levels acts on the complete content of one
  generation, the five species, so the exponent is
  20 = (d+1)·(ΣY²·Δ_f) = 4·5, a pure content ratio.

THE CASCADE MECHANISM (the compression of the exponent)
-------------------------------------------------------
The cascade

    m_e = y_0 · O_e · v_dil/√2

with y_0 the universal Yukawa seed (1.0 — the exact (0,0) top
base of mass_operator_overlap), O_e the (0,0) overlap of the
electron spinor with the dilaton scalar on RP³ (1 − δ(kL), the
finite-kL condensate back-reaction), and v_dil the dilaton VEV.
The exponential form m_e = M_P·e^{−20kL} is the compressed
statement of the same cascade.  The compression is explicit: the
four mixing steps of the spectral cascade (the 4 = d+1 levels of
the KK descent) each act on the complete content of one
generation, the five species (the 5 = ΣY²·Δ_f content factor), so
each step suppresses by e^{−5kL} (one window width kL per species),
and the four steps give

    e^{−4·5·kL} = e^{−20kL} ,

i.e. the exponent 20 = (d+1)·(ΣY²·Δ_f) = 4·5 is the product of
the four cascade levels and the five-species content, each species
carrying one window-width suppression e^{−kL} per level.

V4 DISCIPLINE
-------------
The closure uses M_P and kL (the framework's internal quantities).
The cascade inputs y_0/O_e are the framework's derived values
(the cascade is recorded as the mechanism, the exponential chain
is the closure).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402

# Y_0=1 is the scalar-channel SO(4) diagonal overlap.
Y_0 = 1.0


def electron_overlap(kL: float) -> float:
    """Finite-window scalar-channel overlap.

    Let chi_0 be a normalised lowest RP3 Dirac eigenspinor and let the
    dilaton be the scalar zero-mode profile normalised to unit amplitude.
    The identity scalar Clebsch-Gordan channel gives the unit matrix
    element integral chi_bar_0 phi_0 chi_0 = 1.  The electron closure
    applies the finite-window profile

        O_e = 1-delta(kL),  delta(kL)=exp(-1/kL)/(1+kL^2).

    This function evaluates that declared overlap closure."""
    return 1.0 - 1.0 / (1.0 + kL ** 2) * math.exp(-1.0 / kL)


def m_e_planck(M_P: float, kL: float) -> float:
    """m_e = M_P·e^{−20kL} — the Planck-anchored exponential chain
(GeV → MeV).  The exponent 20 = (d+1)·(ΣY²·Δ_f) = 4·5, with 4 = d+1
the internal dimension plus one and 5 = ΣY²·Δ_f the hypercharge
capacity times the fermion conformal weight, a pure content ratio."""
    return M_P * math.exp(-20.0 * kL) * 1e3


def m_e_cascade(v_dil: float, kL: float) -> float:
    """m_e = y_0·O_e·v_dil/√2 — the cascade form (the mechanism
    record; y_0 = 1 exact, O_e = 1 − δ(kL); v_dil the dilaton VEV
    at the electron scale, dilaton_vev_electron below, in GeV → MeV)."""
    return Y_0 * electron_overlap(kL) * v_dil / math.sqrt(2.0) * 1e3


def dilaton_vev_electron(M_P: float, kL: float, tau: float) -> float:
    """Electron-scale dilaton normalisation.

    The definition

        v_dil(e)=M_P exp(-20 kL) sqrt(2)(1-s0 kappa)/(Y_0 O_e)

    rewrites the electron closure equivalently as
    m_e=Y_0 O_e v_dil(e)/sqrt(2).  The exponent is the cascade content
    20=(d+1)(Sum Y^2 Delta_f)=4*5."""
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    O_e = electron_overlap(kL)
    return (M_P * math.exp(-20.0 * kL) * math.sqrt(2.0)
            * (1.0 - s0 * kappa) / (Y_0 * O_e))


def compute() -> dict:
    """Publish the electron mass closure and the muon/electron ratio."""
    M_P = get("M_P")
    kL = get("kL")
    v = get("v_HIGGS")

    me_raw = m_e_planck(M_P, kL)
    # STATUS (2026-08-20): L2 INHERITED — m_e (1−s0κ) inherits v's base factor through the 4×5 cascade (m_e ∝ v_dil(e)).  See epsilon_ratio DERIVATION STATUS.
    # The low-scale squash correction (1 - s0·κ): the SAME squash
    # correction as v and T_CMB (the electron mass is a LOW-scale
    # quantity, like the EW scale and the photon floor) — the low-scale
    # branch carries −s0·κ, the seesaw carries +s0·κ (2026-08-16).
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    me = me_raw * (1.0 - s0 * kappa)
    # The electron-scale normalisation gives the equivalent cascade form:
    #   m_e = y_0·O_e·v_dil(e)/√2 = M_P·e^{−20kL}(1−s0κ) .
    v_dil_e = dilaton_vev_electron(M_P, kL, tau)
    mc = m_e_cascade(v_dil_e, kL)
    # Algebraic equivalence check at floating-point precision.
    if abs(mc - me) / me > 1e-12:
        raise RuntimeError("electron cascade ≠ exponential chain")
    # The muon/electron ratio: published by lz_ladder (the lepton-ladder
    # source — alpha_lepton and the Euclidean-period factor e^{sqrt(2 pi)});
    # read the authoritative value here rather than re-publishing it
    # (single-writer discipline, cg_core.params).
    mmu_me = float(get("m_mu_over_m_e"))

    pset("m_e_pred", me, provenance="DERIVED", role="internal",
         note=f"m_e = M_P e^(-20 kL) (1 - s0*kappa) = {me:.3f} MeV (the "
              f"Planck-anchored exponential chain times the low-scale "
              f"squash correction; exponent 20 = 4x5 structural)")
    # The exponent 20 = 4×5 (structural): the 4 mixing steps of the
    # spectral cascade × the 5 species of one generation (the content
    # counting) — 20 = (d+1)(ΣY² Δ_f) = 4·5, the pure content ratio.
    cascade_content = (3.0 + 1.0) * ((10.0 / 3.0) * (3.0 / 2.0))
    pset("electron_cascade_content", cascade_content,
         provenance="DERIVED", role="cg",
         note="electron exponent content = (d+1)(SumY2 Delta_f) = "
              "4*(10/3)*(3/2) = 20")
    return {"m_e": me, "m_mu/m_e": mmu_me,
            "m_e_cascade_note": mc,
            "v_dil_electron_MeV": v_dil_e * 1e3,
            "cascade_equiv": (mc / me - 1.0),
            "cascade": "m_e = y_0 O_e v_dil(e)/sqrt(2) ≡ M_P e^{-20kL}(1-s0k) "
                       "— the cascade form at the electron-scale dilaton VEV "
                       "v_dil(e) = M_P e^{-20kL} sqrt2 (1-s0k)/(y0 O_e), the "
                       "4x5 cascade compressed (exact, 2026-08-18)"}


if __name__ == "__main__":
    r = compute()
    print(f"m_e = M_P e^(-20 kL) = {r['m_e']:.3f} MeV")
    print(f"cascade: {r['cascade']}")
    print("electron_mass OK")
