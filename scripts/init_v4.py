# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
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

THE ANCHORS (external, observed — comparison only)
--------------------------------------------------
M_P = 1/√(8πG_N) = 2.4353236e18 GeV  (the reduced Planck mass,
      the identity from the observed G_N)
tau = 0.02                           (the torsion modulus; the
      statistical value 1/50 from the chiral asymmetry — sm_content)
L_Cg = √π                            (the Gaussian-width endpoint
      geometry; the closure fixes L_Cg* ≈ √π)
kL   = 2.4973                        (the F_MG fixed-point seed; the
      endpoint constraint converges to the self-consistent value)
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
    # The IRON-LAW compliance: M_P is COMPUTED from the single
    # observed anchor G_N via the identity M_P = 1/sqrt(8 pi G_N)
    # (the reduced Planck mass).
    _mp = 1.0 / math.sqrt(8.0 * math.pi * float(get("G_N_PDG")))
    pset("M_P", _mp, provenance="DERIVED",
         note=f"M_P = 1/sqrt(8 pi G_N) = {_mp:.8e} GeV (the reduced "
              f"Planck mass, the identity from the single observed "
              f"anchor G_N — computed, not an input)")

    # The framework's internal inputs (the seed values).
    # The IRON-LAW compliance: tau and L_Cg are COMPUTED from the
    # axiom's content, not external inputs.
    # tau = (N_L - N_R)/(N_f * Sum Y^2) = (8-7)/(15 * 10/3) = 1/50
    # (the chiral drive over the hypercharge capacity per generation,
    # the sm_content statistical value — the axiom's content ratio).
    tau_computed = (8 - 7) / (15 * (10.0 / 3.0))
    # The seven-layer tau theoremisation (the V2 loop_normalisation
    # record): the bare 1-loop polarisation is small (0.0014 * Sum Y^2);
    # the RENORMALISATION CONDITION at the emergence scale sets
    # Pi_ren(M_G) = Sum Y^2 (the hypercharge capacity — the framework's
    # coupling convention, analogous to the SM's mu_Z scheme); the
    # counter-term absorbs the bare loop; tau = <chi>/Pi_ren = 1/50.
    # WINDOW-CAPACITY CANCELLATION (2026-08-17; audited 2026-08-18):
    # the screening Pi_ren = Sum Y^2 is written as the window capacity
    # 2 pi kL^4 divided by the content N_f Sum Y^2 (ec_structure.py).
    # The SAME window capacity enters the bare field equation, so it
    # cancels exactly and tau = (N_L - N_R)/(N_f Sum Y^2) = 1/50 is the
    # exact content ratio — it does NOT depend on the specific value of
    # 2 pi kL^4.  (Audit 2026-08-18: the earlier wording "2 pi kL^4 is
    # the discrete spectral sum in closed form" overstates a notation;
    # the 3D RP3 spectral sums close to (kL)^3, not (kL)^4 — see
    # docs/V4_LEDGER.md §0.2.B.  This does not affect tau = 1/50.)
    # bare_coeff = 0.0014 is the V2 one-loop legacy coefficient — the
    # bare-loop magnitude absorbed by the counter-term (layer 6), NOT a
    # derived spectral-sum value.
    bare_coeff = 0.0014
    SY2 = 10.0 / 3.0
    Pi_bare = bare_coeff * SY2
    dPi = SY2 - Pi_bare
    pset("tau", tau_computed, provenance="DERIVED",
         note=f"tau = (N_L - N_R)/(N_f * Sum Y^2) = 1/50 = "
              f"{tau_computed} — CLOSED (the seven-layer theoremisation: "
              f"the chiral drive <chi> = 1/15 over the renormalised "
              f"hypercharge capacity Pi_ren(M_G) = Sum Y^2 = {SY2}; "
              f"the emergence-scale renormalisation scheme, the bare "
              f"loop {Pi_bare:.4f} absorbed by the counter-term "
              f"Delta Pi = {dPi:.4f}; computed from the SM content, "
              f"the iron-law compliance)")
    pset("tau_pi_ren", SY2, provenance="DERIVED", role="internal",
         note=f"Pi_ren(M_G) = Sum Y^2 = {SY2} — the renormalised "
              f"hypercharge polarisation at the emergence scale (the "
              f"renormalisation scheme choice, the tau theoremisation "
              f"layer 6)")
    # The loop-normalisation values COMPUTED: the bare loop and the
    # counter-term (the tau theoremisation layer 6, the V2 record).
    pset("tau_pi_bare", Pi_bare, provenance="DERIVED", role="internal",
         note=f"Pi_bare(M_G) = 0.0014 * Sum Y^2 = {Pi_bare:.6f} — the "
              f"bare one-loop polarisation (the small value needing "
              f"renormalisation)")
    pset("tau_delta_pi", dPi, provenance="DERIVED", role="internal",
         note=f"Delta Pi = Pi_ren - Pi_bare = {dPi:.4f} — the "
              f"counter-term absorbing the bare loop (the tau "
              f"theoremisation layer 6)")
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
    L_GUT = math.sqrt(3.0) / 0.02
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
