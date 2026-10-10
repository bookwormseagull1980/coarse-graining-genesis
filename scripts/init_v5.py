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
scripts/init_v5.py — V5.0: initialise the parameter stores and run
the foundation chain
=================================================================

Initialisation
--------------
The parameter stores (cg_params.json,
reference_inputs.json) are created from the framework's dimensional anchor
and the published comparison store, then the foundation modules run in
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

from cg_core.params import get, init_stores, published_sm_value, set as pset  # noqa: E402
from cg_core.content_response import finite_source_response  # noqa: E402


FOUNDATION_REFERENCE_KEYS = (
    "M_Z", "g1_MZ", "g2_MZ", "g3_MZ", "yt_MZ", "lam_MZ",
    "lambda_H_MZ", "ye_MZ", "yu_MZ", "yd_MZ", "alpha_inv_obs", "v_HIGGS",
)


def init() -> None:
    # G_N is the sole observed dimensional anchor. The SM table is
    # extrapolated for comparison and does not set the geometric endpoint.
    init_stores(
        anchors={
            "G_N_PDG": 6.708830e-39,          # GeV^-2, PDG 2024 (the sole observed anchor)
        },
        sm_values={key: published_sm_value(key) for key in FOUNDATION_REFERENCE_KEYS},
    )
    # The observed anchor G_N fixes the reduced Planck mass through
    # M_P=1/sqrt(8 pi G_N).
    _mp = 1.0 / math.sqrt(8.0 * math.pi * float(get("G_N_PDG")))
    pset("M_P", _mp, provenance="DERIVED", dependencies=("G_N_PDG",),
         note=f"M_P = 1/sqrt(8 pi G_N) = {_mp:.8e} GeV (the reduced "
              f"Planck mass, the identity from the single observed "
              f"anchor G_N)")

    # The content invariant is
    # tau=(N_L-N_R)/(N_f SumY2)=(8-7)/(15*(10/3))=1/50.
    source_response = finite_source_response()
    tau_computed = float(source_response["tau"])
    SY2 = float(source_response["hypercharge_second_moment"])
    pset("tau", tau_computed, provenance="DERIVED", dependencies=(),
         note=f"tau = (N_L - N_R)/(N_f * Sum Y^2) = 1/50 = "
              f"{tau_computed}; N_L=8, N_R=7, N_f=15, SumY2={SY2}")
    # L_Cg = sqrt(pi): the Gaussian endpoint — the window's
    # characteristic length from the Gaussian normalisation
    # integral int exp(-x^2) dx = sqrt(pi) (the unbiased measure's
    # natural scale; the closure fixes L_Cg* = sqrt(pi)).
    pset("L_Cg", math.pi ** 0.5, provenance="DERIVED", dependencies=(),
         note=f"L_Cg = sqrt(pi) = {math.pi ** 0.5} (the Gaussian "
              f"endpoint: the window's characteristic length from the "
              f"Gaussian normalisation int exp(-x^2) dx = sqrt(pi))")
    pset("kL", 2.4973, provenance="INPUT", dependencies=(),
         note="F_MG fixed-point seed; endpoint_constraint converges it")

    # The SM running table (the comparison/coupling-closure values),
    # computed at the chain's own emergence scale M_G = C/kL and the
    # chain's own GUT scale k_GUT = C/L_GUT (L_GUT = √3/τ).
    from comparison.sm_rge.run_rge import run_sm_table
    from cg_core.params import sm_value

    # Consume the published content and Gaussian factors so the scale has
    # an explicit value dependency on each of its three dimensional factors.
    L_Cg = get("L_Cg")
    L_GUT = math.sqrt(3.0) / get("tau")
    M_G_chain = get("M_P") * L_Cg / get("kL")
    k_GUT_chain = get("M_P") * L_Cg / L_GUT
    pset("k_GUT", k_GUT_chain, provenance="DERIVED",
         dependencies=("M_P", "L_Cg", "tau"),
         note="k_GUT = M_P*L_Cg/L_GUT with L_GUT = sqrt(3)/tau (the J=2 "
              "isometry-breaking scale; init_v5)")
    run_sm_table(sm_value("M_Z"), M_G_chain, k_GUT_chain,
                 sm_value("v_HIGGS"))
    print(f"V5 stores initialised (anchors + SM table at M_G={M_G_chain:.6e}, "
          f"k_GUT={k_GUT_chain:.6e}).")


if __name__ == "__main__":
    init()
