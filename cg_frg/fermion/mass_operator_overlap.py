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
cg_frg/fermion/mass_operator_overlap.py — V5.0: finite connector seed
and the specified absolute mass readout
=================================================================

PURPOSE
-----------------------------------
The mass readout is m_f = y_f·v/√2. The unit top seed is evaluated
on the actual finite elementary connector and a normalized pair.

  · the angular (0,0) singlet factor and the specified unit
    elementary connector give y_0=1. This finite pairing does not
    determine the reduced spatial torsion matrix element, the
    physical kinetic normalization, or a running Yukawa boundary.

  · the DOWN-SECTOR ABSOLUTE BASE (the closure): the bottom is the
    GEOMETRIC MEAN of the strange and the top, dressed by the
    window-evolution correction,

        y_b/y_t = e^{-(2 α_dn − ns_tilt (kL_CMB + 2τ))},
        m_b² = m_s·m_t·e^{ns_tilt (kL_CMB + 2τ)},

    where α_dn is the down LZ ladder (sector_alpha), ns_tilt =
    1−n_s the spectral tilt, kL_CMB the CMB window, 2τ the EC
    torsion correction — all internal.

IMPLEMENTATION
-------------
m_t uses the framework's own v (vev_closure); y_b/y_t is the down
LZ double ladder times the window-evolution factor — all internal
(no observed input, no comparison).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.finite_connector import elementary_connector  # noqa: E402
from cg_core.modal_algebra import clebsch_gordan  # noqa: E402
import numpy as np  # noqa: E402


def finite_connector_pairing(H, left, right) -> complex:
    """Full 16-dimensional pairing with caller-supplied states, without projection."""
    operator = elementary_connector(H)["operator"]
    left, right = np.asarray(left, dtype=complex), np.asarray(right, dtype=complex)
    if left.shape != (16,) or right.shape != (16,) or not (
            np.all(np.isfinite(left)) and np.all(np.isfinite(right))):
        raise ValueError("finite full-carrier states of length 16 required")
    return complex(np.vdot(left, operator @ right))


def cg_scalar_channel(j: float) -> float:
    """C(j,0,j) = 1 — the SU(2) Clebsch-Gordan coefficient of the
    scalar (j2 = 0) channel: the identity couples j⊗0 = j uniquely,
    with coefficient 1."""
    return clebsch_gordan(j, j, 0, 0, j, j)


def mass_operator_matrix_element(jL: float, jR: float) -> float:
    """Specified unit finite seed times its angular singlet coefficients.

    This readout evaluates the normalized finite connector pairing and
    the two angular singlet coefficients. Spatial operator matching and
    external kinetic normalization are specified separately.
    """
    left, right = np.eye(16)[0], np.eye(16)[8]
    seed = finite_connector_pairing([0, 1], left, right)
    return float(seed.real) * cg_scalar_channel(jL) * cg_scalar_channel(jR)


# The normalized finite seed and angular singlet factor; held fixed by the
# present production boundary prescription, not by a zero physical beta function.
Y_0 = mass_operator_matrix_element(0.5, 0.0)


def top_mass(v: float) -> float:
    """m_t = y_0·v/√2 in the specified finite-seed mass readout."""
    return Y_0 * v / math.sqrt(2.0)


def compute() -> dict:
    """Publish the top base, the down-sector absolute base and the
    bottom absolute mass.

    The DOWN-SECTOR ABSOLUTE BASE (the closure):

        y_b/y_t = e^{-(2 alpha_dn - ns_tilt (kL_CMB + 2 tau))}

    i.e. the down LZ double ladder e^{-2 alpha_dn} times the
    window-evolution factor e^{ns_tilt (kL_CMB + 2 tau)}.  Equivalently
    m_b^2 = m_s m_t e^{ns_tilt (kL_CMB + 2 tau)} — the bottom is the
    GEOMETRIC MEAN of the strange and the top, dressed by the
    window-evolution correction (the spectral tilt 1-n_s times the CMB
    window kL_CMB plus the torsion correction 2 tau).  All quantities
    are internal (sector_alpha's alpha_dn, ns_tilt, kL_CMB, tau).
    """
    v = get("v_HIGGS")
    a_dn = get("alpha_down")
    ns_tilt = get("ns_tilt")
    kL_CMB = get("kL_CMB")
    tau = get("tau")

    mt = top_mass(v)
    # The down-sector absolute base (the closure formula).
    yb_yt = math.exp(-(2.0 * a_dn - ns_tilt * (kL_CMB + 2.0 * tau)))

    pset("y_top_base", Y_0, provenance="DERIVED",
         dependencies=(),
         note="normalized finite elementary-connector pairing times angular singlet coefficients")
    pset("m_t_pred", mt, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS",),
         note=f"m_t = y_0 v/sqrt(2) = {mt:.1f} GeV with the fixed unit finite seed. "
              "Physical Yukawa running and pole matching require an explicit "
              "renormalized spatial vertex and kinetic normalization.")
    pset("y_b_over_y_t", yb_yt, provenance="DERIVED", role="internal",
         dependencies=("alpha_down", "ns_tilt", "kL_CMB", "tau"),
         note=f"y_b/y_t = e^-(2 a_dn - ns_tilt (kL_CMB + 2 tau)) = "
              f"{yb_yt:.6f} (the down LZ double ladder e^-2 a_dn "
              f"times the window-evolution factor "
              f"e^{{ns_tilt (kL_CMB + 2 tau)}}: m_b^2 = m_s m_t "
              f"e^{{ns_tilt (kL_CMB + 2 tau)}} — the bottom is the "
              f"geometric mean of the strange and the top, dressed by "
              f"the window evolution)")
    # The bottom absolute mass (the y_b/y_t cascade): m_b = y_b v/sqrt(2).
    m_b = yb_yt * mt
    pset("m_b_pred", m_b, provenance="DERIVED", role="internal",
         dependencies=("v_HIGGS", "alpha_down", "ns_tilt", "kL_CMB", "tau"),
         note=f"m_b = (y_b/y_t) m_t = {m_b:.3f} GeV in the specified "
              "geometric-mean window readout, using the same finite top seed.")
    return {"m_t": mt, "y_0": Y_0,
            "y_b_over_y_t": yb_yt,
            "m_b": m_b}


if __name__ == "__main__":
    r = compute()
    print(f"m_t = {r['m_t']:.1f} GeV")
    print(f"y_b/y_t = {r['y_b_over_y_t']:.6f}")
    print(f"m_b = {r['m_b']:.3f} GeV")
    print("mass_operator_overlap OK")
