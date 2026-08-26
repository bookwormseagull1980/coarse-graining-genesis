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
scripts/init_v4.py — V4.0: initialise the parameter stores and run
the foundation chain
=================================================================

WHY THIS SCRIPT EXISTS (motivation)
-----------------------------------
The V4 rebuild is a fresh start: the parameter stores (cg_params.json,
sm_inputs.json) are created from the framework's anchor values and
the SM comparison table, then the foundation modules run in
dependency order (the SM RGE table, the spectral sums, the endpoint
constraint) to publish the main chain.

FOUNDATION VALUES
-----------------
G_N is the observed dimensional anchor and gives
M_P=1/sqrt(8 pi G_N).  The structural content gives
tau=(N_L-N_R)/(N_f SumY2)=1/50.  The Gaussian endpoint gives
L_Cg=sqrt(pi).  The numerical root search starts at kL=2.4973 and the
endpoint constraint publishes the self-consistent value.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, init_stores, set as pset  # noqa: E402


def init() -> None:
    # The anchors (observed; comparison only — G_N is the sole
    # dimensionful anchor; the SM table feeds the coupling-closure
    # anchor of endpoint_constraint).
    init_stores(
        anchors={
            "G_N_PDG": 6.708830e-39,          # GeV^-2, PDG 2024 (the sole observed anchor)
        },
        sm_values={
            "M_Z": 91.1876,
            "g1_MZ": 0.461425,
            "g2_MZ": 0.64779,
            "g3_MZ": 1.217200,
            "yt_MZ": 0.940,
            "lam_MZ": 0.129,
            "lambda_H_MZ": 0.1294,
            "ye_MZ": 2.935e-6,
            "yu_MZ": 6.0e-6,
            "yd_MZ": 1.34e-5,
            "alpha_inv_obs": 137.036,
            "v_HIGGS": 246.22,          # observed EW VEV, GeV (PDG,
                                         # comparison only)
        },
    )
    # The observed anchor G_N fixes the reduced Planck mass through
    # M_P=1/sqrt(8 pi G_N).
    _mp = 1.0 / math.sqrt(8.0 * math.pi * float(get("G_N_PDG")))
    pset("M_P", _mp, provenance="DERIVED",
         note=f"M_P = 1/sqrt(8 pi G_N) = {_mp:.8e} GeV (the reduced "
              f"Planck mass, the identity from the single observed "
              f"anchor G_N)")

    # The content invariant is
    # tau=(N_L-N_R)/(N_f SumY2)=(8-7)/(15*(10/3))=1/50.
    tau_computed = (8 - 7) / (15 * (10.0 / 3.0))
    SY2 = 10.0 / 3.0
    pset("tau", tau_computed, provenance="DERIVED",
         note=f"tau = (N_L - N_R)/(N_f * Sum Y^2) = 1/50 = "
              f"{tau_computed}; N_L=8, N_R=7, N_f=15, SumY2={SY2}")
    # L_Cg = sqrt(pi): the Gaussian endpoint — the window's
    # characteristic length from the Gaussian normalisation
    # integral int exp(-x^2) dx = sqrt(pi) (the unbiased measure's
    # natural scale; the closure fixes L_Cg* = sqrt(pi)).
    pset("L_Cg", math.pi ** 0.5, provenance="DERIVED",
         note=f"L_Cg = sqrt(pi) = {math.pi ** 0.5} (the Gaussian "
              f"endpoint: the window's characteristic length from the "
              f"Gaussian normalisation int exp(-x^2) dx = sqrt(pi); "
              f"computed, not an input)")
    pset("kL", 2.4973, provenance="INPUT",
         note="F_MG fixed-point seed; endpoint_constraint converges it")

    # The SM running table (the comparison/coupling-closure values),
    # computed at the chain's own emergence scale M_G = C/kL and the
    # chain's own GUT scale k_GUT = C/L_GUT (L_GUT = √3/τ).
    from comparison.sm_rge.run_rge import run_sm_table
    from cg_core.params import sm_value, sm_set

    try:
        sm_value("v_HIGGS")
    except KeyError:
        sm_set("v_HIGGS", 246.22, note="observed EW VEV, GeV (PDG, "
                                        "comparison only)")

    L_Cg = math.pi ** 0.5
    # L_GUT = sqrt(3)/tau uses the COMPUTED tau (tau_computed, the
    # content ratio) — no duplicated literal (was math.sqrt(3.0)/0.02).
    L_GUT = math.sqrt(3.0) / tau_computed
    M_G_chain = get("M_P") * L_Cg / get("kL")
    k_GUT_chain = get("M_P") * L_Cg / L_GUT
    pset("k_GUT", k_GUT_chain, provenance="DERIVED",
         note="k_GUT = M_P*L_Cg/L_GUT with L_GUT = sqrt(3)/tau (the J=2 "
              "isometry-breaking scale; init_v4)")
    run_sm_table(sm_value("M_Z"), M_G_chain, k_GUT_chain,
                 sm_value("v_HIGGS"))
    print(f"V4 stores initialised (anchors + SM table at M_G={M_G_chain:.6e}, "
          f"k_GUT={k_GUT_chain:.6e}).")


if __name__ == "__main__":
    init()
