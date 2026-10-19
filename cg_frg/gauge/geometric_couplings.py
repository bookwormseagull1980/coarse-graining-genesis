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

cg_frg/gauge/geometric_couplings.py — V5.0: the geometric gauge

couplings g₂ and g₁ at the emergence scale

=================================================================



PURPOSE

-----------------------------------

The gauge couplings of the emergent theory are pure functions of

the Planck-endpoint geometry:



    g₂ = √8·(M_G/M_P)·kL^{−3/2}          (the Killing normalisation:

       the 7D→4D reduction of the SU(2)_L isometry zero modes on

       the internal RP³ — the dimensional_reduction formula)

    g₁ = g₂·κ(2τ)                        (the J=2 squash mixing:

       κ²(s) = (1+s)/(1−2s)^{5/2}, the isometry-breaking U(1)_Y

       normalisation — applied at the BREAKING scale k_GUT:

       g1(k_GUT) = g2(k_GUT)·κ, then run down to M_G)



g₂ is the framework's geometric closure (endpoint_constraint

publishes it); g₁ = g₂·κ with the mixing coefficient κ(2τ) ≈ 1.132

applied at k_GUT (closes at +0.2%).

g₃ is closed via the long-root correction (g3(k_GUT) = g2(k_GUT)·

(1+α_GUT²/K), K=8/3 — see compute).



THE KILLING NORMALISATION (derivation)

--------------------------------------

g₂_raw = 16π²/I_kv with I_kv = |F|²·Vol(RP³) = 2π²L³; the 4D

coupling is g₂_4D = g₂_raw·(M(σ)/M_P)² where the (M/M_P)² factor is

a normalisation CONVENTION (choice, not a KK inference — declared

as SCALE_CHOICE).  At the emergence scale M_G with L = L_Gg = kL:



    g₂(M_G) = √8·(M_G/M_P)·kL^{−3/2}.



THE J=2 SQUASH MIXING (derivation)

----------------------------------

The isometry breaking SU(2)_R → U(1)_Y by the J=2 squash with

amplitude s: the U(1) normalisation is rescaled by

κ²(s) = (1+s)/(1−2s)^{5/2} (the metric of the squashed S³ in the

σ₃ direction vs the equator).  With s₀ = 2τ = 0.04:

κ(2τ) ≈ 1.1318 (the squashed S³ metric; the amplitude s₀ = 2τ =

N_g·τ/(d+1), the λ_EC first-order torsion N_g·τ divided by (d+1)).

IMPLEMENTATION

-------------

The (M/M_P)² factor is a SCALE_CHOICE (declared, never disguised

as a derivation).  The amplitude s0 = 2tau = N_g*tau/(d+1) is DERIVED: s0 = q*tau with q = 2 the long-root-mode charge (Guo (2026d) Appendix A).

(the λ_EC first-order torsion divided by d+1).

"""



from __future__ import annotations



import math

import sys

from pathlib import Path



_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

if str(_PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(_PROJECT_ROOT))



from cg_core.params import get, set as pset  # noqa: E402

from cg_core.gauge_running import geometric_run, common_origin  # noqa: E402
from cg_frg.gauge.zero_mode_reduction import (  # noqa: E402
    killing_coupling_squared, register_gauge_scale_factor,
)





def g2_killing(M_G: float, M_P: float, kL: float) -> float:

    """g₂(M_G) = √8·(M_G/M_P)·kL^{−3/2} — the Killing normalisation.



    Derivation: g₂_raw = 16π²/I_kv, I_kv = 2π²L³; g₂_4D =

    g₂_raw·(M(σ)/M_P)² with L = L_Gg = kL at the emergence scale:

    g₂² = 16π²·(M_G/M_P)²/(2π²kL³) = 8(M_G/M_P)²/kL³.



    When the endpoint matching supplies the window-edge identity

    kL·M_G = M_P·√π, this expression reduces to

        g₂² = 8π/kL⁵  ⇒  α_W(M_G) = g₂²/4π = 2/kL⁵,

    i.e. the weak coupling at M_G is the PURE WINDOW CAPACITY:

    α_W(M_G) = 2/kL⁵ = 2/(window capacity)^{5/2}.  No mass scale

    enters — only the dimensionless kL (the same kL that closes

    H0, Ω_Λ, the CKM product, and the entropy integral).

    """

    return math.sqrt(killing_coupling_squared(M_G, M_P, kL))





def squash_metric(tau: float) -> dict:

    """Axisymmetric squash and its curvature-preserving amplitude ratio.

    For A=1+s, B=1-2s and a fixed axial Killing vector X, its metric dual
    is alpha_s=B*sigma3. The curvature d(alpha_s)=B*d(sigma3) has squared
    L2 norm ratio B^(5/2)/A. Preserving that norm gives the assigned
    amplitude ratio kappa=sqrt(A/B^(5/2)).

    An externally varying amplitude instead has kinetic form alpha_s,
    whose squared L2 norm ratio is A*B^(3/2). The internal curvature
    ratio alone does not normalize an external gauge kinetic term or
    matter vertex. Both actual Gram contractions are available from
    cg_core.matter_matching.axial_squash_grams.
    """

    from cg_core.matter_matching import axial_squash_grams
    s = 2.0 * tau                     # the squash amplitude s₀ = n_broken·τ
    grams = axial_squash_grams(s)

    lam1 = 1.0 + s                    # σ₁, σ₂ eigenvalues (1+s)

    lam3 = 1.0 - 2.0 * s              # σ₃ eigenvalue (1−2s), the U(1)_Y axis

    vol_ratio = lam1 * math.sqrt(lam3)   # V₃(s)/V₃(0) = (1+s)√(1−2s)

    g33 = 1.0 / lam3                  # the σ₃-axis inverse metric

    kappa2 = vol_ratio * g33 ** 3     # κ² = (1+s)/(1−2s)^{5/2}

    return {"s": s, "kappa": math.sqrt(kappa2), "kappa2": kappa2,

            "volume_ratio": vol_ratio, "g33": g33,
            "curvature_gram_ratio": grams["curvature_gram_ratio"],
            "oneform_gram_ratio": grams["oneform_gram_ratio"]}





def kappa_mixing(tau: float) -> float:

    """κ(2τ) — the J=2 squash mixing coefficient.



    κ²(s) = (1+s)/(1−2s)^{5/2} evaluated at s₀ = 2τ: the U(1)_Y

    normalisation factor of the squashed internal metric.  The

    amplitude s₀ = n_broken·τ = 2τ = N_g·τ/(d+1), where n_broken = 2

    = (d+1)/2 is the number of broken SU(2)_R generators (d = 3 the

    internal-space dimension of RP³, N_g = 8 the su(3) generators).

    The identity s0 = N_g*tau/(d+1) is the ARITHMETIC restatement of s0 = q*tau = 2tau, where q = 2 is the long-root-mode charge (Guo (2026d) Appendix A: q = 2 m_R, m_R = 1); N_g = (d+1)*n_broken (8 = 4*2) is the derived content identity.

    order torsion N_g·τ divided by (d+1) .



    GEOMETRIC DERIVATION : the value is computed from

    the squashed S³ metric ds² = (1+s)σ₁² + (1+s)σ₂² + (1−2s)σ₃² by

    squash_metric: κ² = [V₃(s)/V₃(0)]·(g³³)³, the volume ratio

    times the third moment of the σ₃-axis inverse metric, not a

    fitted form.

    """

    return squash_metric(tau)["kappa"]





def g1_hypercharge(g2: float, tau: float) -> float:

    """g₁ = g₂·κ(2τ) — the U(1)_Y coupling from the J=2 mixing."""

    return g2 * kappa_mixing(tau)





def compute() -> dict:

    """Publish the geometric couplings at M_G and the SU(3)

    common-origin prediction at the GUT scale."""

    M_P = get("M_P")

    M_G = get("M_G")

    kL = get("kL")

    tau = get("tau")



    scale_factor = register_gauge_scale_factor()
    g2_geo = math.sqrt(8.0 * scale_factor / kL ** 3)
    pset("g2_MG_geo", g2_geo, provenance="DERIVED", role="internal",
         dependencies=("gauge_kinetic_scale_factor", "kL"),
         note="bare g2=sqrt(8 gauge_kinetic_scale_factor/kL^3); "
              "the absolute scale prescription is recorded separately")
    g2_geo = float(get("g2_MG_geo"))

    kappa = kappa_mixing(tau)



    # ---- geometric-dynamics conservation law ----

    # The g2 boundary combines the conformal content identity with EC torsion:

    #     1/alpha = 1/alpha_W + 1/N_c - tau^2*pi/2

    #     N_c(1/alpha - 1/alpha_W + tau^2 pi/2) = 1   <->   N_g xi = 1

    # alpha_W = g2_geo^2/(4*pi), with g2_geo consuming the registered
    # gauge kinetic scale factor. It reduces to 2/kL^5 when the endpoint
    # obeys kL*M_G=M_P*sqrt(pi).

    # This uses the same bare connection normalization as the endpoint;

    # the 1/N_c and tau^2 pi/2 terms are the colour-number and

    # EC-torsion content ratios in the inverse-coupling boundary condition.

    #

    # SPECTRAL-SUM ORIGIN OF THE TORSION TERM :

    #   tau^2 pi/2 = (2 tau^2) * (2 pi) * xi = 4 pi tau^2 / N_g

    # with the three physical factors, each traced to the spectrum:

    #   2 tau^2  = the SECOND-ORDER torsion term of the EC curvature

    #              lambda_EC = N_g(1+tau/2)^2 + 6 = 14 + 8 tau + 2 tau^2

    #              (the totally antisymmetric torsion T^a_bc=(tau/L)eps^a_bc

    #              contributes +2 tau^2 to this retained J=2 response).
    #              This is not the EC scalar-curvature shift, which is
    #              negative and equals -3 tau^2/(2 L^2) in ec_structure.

    #   2 pi      = the Euclidean period (the Matsubara zero-freq of the

    #              spectral sum, the SAME 2pi thread as eps=e^{1/2pi}, the

    #              window capacity 2 pi kL^4, g_A = 4/pi);

    #   xi = 1/N_g = (d-2)/(4(d-1)) = 1/8  the conformal coupling (the

    #              scalar-field curvature coupling of the frame — the

    #              law's duality N_g xi = 1).

    # So the torsion term is the product of the EC second-order torsion,

    # the Euclidean period, and the conformal coupling: the torsion mode's

    # Euclidean spectral sum, normalised by the generator count (xi = 1/N_g).

    # Both terms of the law (1/N_c = N_g xi / N_c and tau^2 pi/2 =

    # 4 pi tau^2 xi) carry the SAME conformal coupling xi, so the law IS

    # the conformal-gauge duality N_g xi = 1 written in the coupling-

    # inverse basis.

    N_c = 3.0

    alpha_W = g2_geo ** 2 / (4.0 * math.pi)

    inv_alpha_pred = 1.0 / alpha_W + 1.0 / N_c - tau ** 2 * math.pi / 2.0

    g2 = math.sqrt(4.0 * math.pi / inv_alpha_pred)   # full prediction = 0.508848



    # g1: the J=2 squash mixing kappa acts at the BREAKING scale k_GUT

    # (where the isometry SU(2)_R -> U(1)_Y breaks), NOT at M_G:

    #   g1(k_GUT) = g2(k_GUT) * kappa,  then g1 runs down to M_G.

    # The mixing is geometrically defined at the onset of isometry

    # breaking, k_GUT.  No SM coupling enters.

    b1 = 41.0 / 10.0

    b2 = -19.0 / 6.0

    b3 = -7.0

    k_GUT = get("k_GUT")

    inv_g2_GUT2 = 1.0 / g2 ** 2 + (-b2 / (8.0 * math.pi ** 2)) * math.log(k_GUT / M_G)

    g2_GUT = 1.0 / math.sqrt(inv_g2_GUT2)

    # ---- g1 U(1)_Y normalisation correction  ----

    # The hypercharge boundary uses the content factor:

    #   delta_g1 = -tau * r23 * (SigmaY2 * Delta_f * xi)

    #     tau      = (N_L-N_R)/(N_f SigmaY2)  charged-quotient response modulus

    #     r23      = 3/(10 sqrt3)             hypercharge-trace hierarchy ratio

    #     SigmaY2*Delta_f = (10/3)*(3/2) = 5  hypercharge capacity x fermion

    #                                          conformal weight

    #     xi       = 1/N_g = 1/8              the conformal coupling

    # delta_g1 = -sqrt3/800.

    # The factor 5/8 = SigmaY2*Delta_f*xi uses xi =

    # (d-2)/(4(d-1)) = 1/8 is the conformal coupling and N_g = 8 the

    # generator count, with the conformal-gauge duality N_g*xi = 1

    # (xi = 1/N_g).  So the U(1)_Y correction is the hypercharge

    # capacity x fermion conformal weight x conformal coupling — the

    # SAME conformal-gauge duality that closes g2's 1/N_c.

    SigmaY2 = 10.0 / 3.0

    Delta_f = 3.0 / 2.0

    N_g = 8.0

    xi = 1.0 / N_g

    r23 = 3.0 / (10.0 * math.sqrt(3.0))

    delta_g1 = -tau * r23 * (SigmaY2 * Delta_f * xi)

    g1_GUT = g2_GUT * kappa * (1.0 + delta_g1)

    inv_g1_MG2 = 1.0 / g1_GUT ** 2 + (b1 / (8.0 * math.pi ** 2)) * math.log(k_GUT / M_G)

    g1 = 1.0 / math.sqrt(inv_g1_MG2)



    # g3 via the common-origin boundary, retaining the fixed geometric
    # g1/g2 at M_G. The forward residual at k_GUT is solved and checked
    # with a finer RK4 integration, including the long-root bifurcation:

    #

    #   g3(k_GUT) = g2(k_GUT) * (1 + alpha_GUT^2/K)

    #

    # where alpha_GUT = g2(k_GUT)^2/(4 pi) is the unified gauge coupling

    # and K = 8/3 is the long-root condensation coefficient (the J=2 mode's

    # kinetic eigenvalue J(J+2) = 8 over the internal-space dimension 3).

    # The near-unification bifurcation g3_sm_GUT/g2_sm_GUT = 1.000171 is

    # the two-loop correction alpha_GUT^2 divided by K: the long-root

    # condensation (K) dilutes the SU(3) two-loop self-coupling relative

    # to the SU(2) factor, so g3 sits ABOVE g2 at the breaking scale.

    # This is the CF-3 forward content (the two su(2) blocks share the

    # Killing normalisation — g3 = g2 at order alpha^0 — while the

    # long-root E_{±(alpha_1+alpha_2)} carries the alpha^2/K bifurcation).  The yt

    # entering the two-loop mixing is the GEOMETRIC content y_0 = 1.0

    # (the exact SO(4) diagonal overlap — scale-invariant, NOT the SM

    # table's running yt).

    # The long-root condensation coefficient (geometric-dynamics origin,

    # K = J(J+2)/d = 2·4/3 = 8/3, the J=2 squash's kinetic

    # eigenvalue J(J+2) = 8 over the internal-space dimension d = 3 (RP³).

    d_internal = 3             # internal-space dimension of RP³

    j_squash = 2               # the J=2 squash (isometry-breaking tensor)

    K_long = j_squash * (j_squash + 2) / d_internal   # = 8/3

    origin = common_origin(g1, g2, M_G, k_GUT, K_long=K_long)
    g3_MG_geo = origin["g3_initial"]
    g2_GUT2 = origin["at_breaking"][1]

    pset("g3_MG_geo", g3_MG_geo, provenance="DERIVED", role="internal",

         note=f"g3(M_G) = {g3_MG_geo:.6f} via common-origin "

              f"g3(k_GUT)=g2(k_GUT)*(1+alpha_GUT^2/K) run down TWO-LOOP "

              f"(Machacek-Vaughn/Buttazzo beta_gauge; K = 8/3 the long-root "

              f"condensation coefficient — the alpha^2/K bifurcation is the "

              f"CF-3 forward content; checked RK4 forward relative boundary "
              f"residual {origin['relative_residual']:.3e})")



    # The SU(3) common-origin prediction: the colour generators share

    # the SU(2) Killing normalisation, so at the breaking scale k_GUT

    # leading common-origin values coincide before the finite bifurcation.
    # The diagnostic g3_pred below is that leading value, not the final
    # colour boundary g3(k_GUT). It uses the

    # framework's OWN g2 run to k_GUT (the two-loop geometric RGE,

    # g2_GUT2).

    g3_pred = g2_GUT2               # the common-origin prediction (internal)



    # The J=2 squash mixing kappa(2tau) is calibrated at the BREAKING

    # scale k_GUT (the isometry-breaking onset):

    # kappa^2(2tau) = (1+2tau)/(1-4tau)^2.5 = 1.13183.



    pset("g2_MG", g2, provenance="DERIVED",
         dependencies=("g2_MG_geo", "tau"),

         note=f"g2(M_G) = {g2:.9f}; the geometric boundary obeys "

              f"the inverse-coupling relation 1/alpha_SM = 1/alpha_W "

              f"+ 1/N_c - tau^2*pi/2; Lean checks the associated "

              f"finite content and coefficient identities")

    pset("kappa_mixing", kappa, provenance="DERIVED",

         note=f"kappa(2tau) = sqrt((1+2tau)/(1-4tau)^2.5) = {kappa:.8f} "

              f"(the J=2 squash mixing)")

    pset("g1_MG_geo", g1, provenance="DERIVED",

         note=f"g1(M_G) = g2(k_GUT)*kappa run down = {g1:.6f} (the kappa "

              f"acts at the breaking scale k_GUT (g1(k_GUT)=g2(k_GUT)*kappa), "

              f"then g1 runs down to M_G; the amplitude s0=2tau = N_g*tau/(d+1)")

    pset("g3_common_origin_pred", g3_pred, provenance="DERIVED",

         role="internal",

         note=f"leading common-origin value before finite bifurcation: "
              f"g2(k_GUT) = {g3_pred:.6f} (the common-origin "

              f"prediction: the colour generators share the SU(2) Killing "

              f"normalisation; the bifurcation mechanism (the long-root "

              f"geometric carrier) is the J=2 squash)")

    # ---- fine-structure constant from two-loop running ----
    # The EW scale is INTERNAL: M_Z = sqrt(g2(v)^2 + g1'(v)^2) v/2 from
    # the framework's own v and the geometric couplings run down to v
    # (one-loop).  No external scale enters.
    b1z = 41.0 / 10.0
    b2z = -19.0 / 6.0
    v = float(get("v_HIGGS"))
    L_v = math.log(M_G / v)
    inv_g1_v2 = 1.0 / g1 ** 2 + (b1z / (8.0 * math.pi ** 2)) * L_v
    inv_g2_v2 = 1.0 / g2 ** 2 + (b2z / (8.0 * math.pi ** 2)) * L_v
    g1_v = 1.0 / math.sqrt(inv_g1_v2)
    g2_v = 1.0 / math.sqrt(inv_g2_v2)
    g1p_v = g1_v * math.sqrt(3.0 / 5.0)
    MZ_int = math.sqrt(g2_v * g2_v + g1p_v * g1p_v) * v / 2.0
    # Run the framework's geometric g1(M_G), g2(M_G) down to the
    # internal M_Z with the TWO-LOOP geometric RGE (beta_gauge with
    # the scale-invariant geometric Yukawa y_0 = 1.0) -- the SAME
    # convention as alpha_s(M_Z) and Lambda_QCD (mass_gap_scale).
    # The two-loop coefficients use the framework's specified matter content.
    mz_run = geometric_run((g1, g2, g3_MG_geo), M_G, MZ_int)
    g1r, g2r, g3r = mz_run.couplings
    g1_MZ = g1r
    g2_MZ = g2r
    alpha_inv = 4.0 * math.pi * (1.0 / g2_MZ ** 2 + 5.0 / (3.0 * g1_MZ ** 2))
    pset("alpha_inv_MZ_pred", alpha_inv, provenance="DERIVED",
         role="internal",
         note=f"alpha^-1(M_Z) = {alpha_inv:.2f} (TWO-LOOP geometric RGE: "
              f"the geometric g1(M_G)=g2(k_GUT)*kappa and g2(M_G) both run "
              f"down the two-loop gauge beta functions with the geometric "
              f"Yukawa y_0=1.0, the same convention as alpha_s(M_Z); the "
              f"kappa acts at k_GUT (the isometry-breaking onset))")
    return {"g2_MG": g2, "kappa": kappa, "g1_MG_geo": g1,
            "g3_MG_geo": g3_MG_geo,
            "g3_common_origin_pred": g3_pred,
            "g3_boundary_relative_residual": origin["relative_residual"],
            "gauge_integration_error_estimate": max(mz_run.estimated_abs_error),
            "alpha_inv_MZ_pred": alpha_inv}





if __name__ == "__main__":

    r = compute()

    print(f"g2(M_G) = {r['g2_MG']:.6f}, kappa = {r['kappa']:.6f}, "

          f"g1(M_G) = {r['g1_MG_geo']:.6f}")

    print("geometric_couplings OK")

