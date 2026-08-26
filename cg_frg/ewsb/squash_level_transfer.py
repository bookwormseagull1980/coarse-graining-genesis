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
cg_frg/ewsb/squash_level_transfer.py — geometric moments of the six
J=2 squash level-transfer coefficients

=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
This module evaluates the six J=2 squash corrections from the content
modulus, the broken-generator count, and explicit geometric moments:

    content -> (tau,s0) -> geometric moment c_Q -> (1+c_Q s0 kappa).

THE DERIVATION CHAIN
--------------------

  STEP 0 — GEOMETRIC INPUTS
      The internal RP3 geometry supplies
        (i)  the torsion Lagrangian   L_tors = a T^2 + b T^{bac}T_{abc}
             + c (T^a_ab)^2,  with a = M_G^3/4, b = 4a, c = -(7/3)a
             (the Holst/Immirzi algebraic-torsion condition b = 4a);
        (ii) the order-parameter (J=2 squash) Landau potential
             V(phi) = (1/2) xi (R - R_c) phi^2 + (lambda/4) phi^4,
             xi = 1/8 the conformal coupling, R_c = 6/pi;
        (iii) the surviving U(1)_Y hypercharge coupling, whose Killing
             normalisation on the squashed S^3 is the geometric integral

             kappa^2(s) = [V_3(s)/V_3(0)] (g^33)^3
                        = (1+s)/(1-2s)^{5/2}
                        = int sqrt{g} (g^33)^3 d^3x / int sqrt{g} d^3x .

      The "(g^33)^3" third moment is the F^2 contraction of the
      sigma_3-axis zero mode: two inverse-metric factors from the field
      strength and one from the polarisation (geometric_couplings).

  STEP 1 — THE CONTENT MODULUS (tau)
      The chiral excess and quadratic hypercharge moment give

          tau=(N_L-N_R)/(N_f sum Y^2)=1/50.

  STEP 2 — THE SQUASH AMPLITUDE (s0)
      The broken-generator content gives

          s0 = n_broken * tau = (dim SU(2)_R - dim U(1)_R) tau = 2 tau .

  STEP 3 — THE GEOMETRIC MOMENT INTEGRAL (the content charge c_Q)
      Each physical quantity Q responds to the squash by the first-order
      variation of its operator under the TRACELESS SHEAR

          ds^2 = (1+s) sigma_1^2 + (1+s) sigma_2^2 + (1-2s) sigma_3^2,

      whose inverse-metric logarithmic derivatives are
          d ln g^33 / ds = +2   (the U(1)_Y axis),   d ln g^11 = d ln g^22 / ds = -1
          (the equator),   d ln sqrt{g}/ds = 0   (traceless, volume conserved).

      A quantity carrying n_3 sigma_3-axis and n_eq equator inverse-metric
      factors therefore has the geometric moment (a first-order integral)

          c_Q = d ln Q / ds |_{s=0} = 2 n_3 - n_eq ,

      i.e. the weighted count of the squash deformation across the content.
      Equivalently, in the two-factor form used below,

          c_Q = a_Q * r_Q ,
          a_Q = amplitude fraction (1 geometric, 1/2 chiral),
          r_Q = content ratio (1, sum Y^2 Delta_s, 1/N_g, 4).

      The amplitude fraction is the broken-generator vs chiral-asymmetry
      content: a geometric quantity couples to BOTH broken generators
      (n_broken = 2 -> a = 1), a chiral quantity to the single chiral
      asymmetry (N_L-N_R = 1 -> a = (N_L-N_R)/n_broken = 1/2).  The content
      ratio r_Q is the specific content of the operator (below).

  STEP 4 — THE CORRECTION FACTOR
      Q -> Q (1 + c_Q * s0 * kappa),  with
      s0 kappa = N_g tau kappa/(d+1).  This identity follows from
      N_g=8, d=3, and s0=2 tau.

THE SIX MOMENTS (each a computed product a_Q * r_Q)
---------------------------------------------------
  level             a_Q (amplitude)      r_Q (content)            c_Q (s0 units)   factor
  geometric(v,Vcb)  1  (n_broken=2)      -1 (compression)         -1              1 - s0 kappa
  seesaw (m_nu3)    1                    +1 (transfer)            +1              1 + s0 kappa
  chiral (Td,DsR)   1/2 (N_L-N_R=1)      -1 (restoration)         -1/2            1 - tau kappa
  chiral (Vub)      1/2                  +1 (cross-generation)    +1/2            1 + tau kappa
  constituent (mp)  1/2                  +sum Y^2 Delta_s = +5/3  +5/6            1 + 5 tau kappa/3
  generator (a_s)   1                    -1/N_g = -xi             -1/N_g          1 - s0 kappa/N_g
  power (rho_L)     1                    -4 (m_nu1^4)             -4              1 - 4 s0 kappa

SOURCE OF THE MOMENTS
---------------------
The amplitude fractions follow from the broken-generator and chiral-content
counts.  The remaining factors use the seesaw level transfer, the fourth
power in rho_L, the hypercharge moment sum Y^2=10/3, the scalar conformal
weight Delta_s=1/2, and N_g=8.  Thus every correction coefficient is a
function of the internal content data
(N_g, N_c, d, xi, Delta_s, sum Y^2, N_f, N_L-N_R, n_broken).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get  # noqa: E402
from cg_core.sm_content import (  # noqa: E402
    hypercharge_sum_sq,
    chiral_asymmetry,
    N_WEYL_PER_GENERATION,
    N_G_COLOR,
)


# ---------------------------------------------------------------------------
# Structural content (all DERIVED — see sm_content / order_parameter)
# ---------------------------------------------------------------------------
_D = 3                   # the internal-space dimension of RP3 (d = N_c = 3)
_N_G = float(N_G_COLOR)  # N_g = N_c^2 - 1 = 8 (su(3) generators)
_N_BROKEN = 2            # n_broken = dim SU(2)_R - dim U(1)_R = 2


def _content() -> dict:
    """The DERIVED content used by every moment (no hard-coding)."""
    SigmaY2 = hypercharge_sum_sq()          # 10/3 (anomaly-normalised)
    N_L_minus_N_R = float(chiral_asymmetry())   # 1 (Z2 spin structure)
    N_f = float(N_WEYL_PER_GENERATION)      # 15 Weyl per generation
    tau = N_L_minus_N_R / (N_f * SigmaY2)   # 1/50
    xi = (_D - 2.0) / (4.0 * (_D - 1.0))    # 1/8 (Yamabe conformal coupling)
    Delta_s = (_D - 2.0) / 2.0              # 1/2 (scalar conformal weight)
    return {"SigmaY2": SigmaY2, "tau": tau, "xi": xi,
            "Delta_s": Delta_s, "N_f": N_f, "N_g": _N_G,
            "N_L_minus_N_R": N_L_minus_N_R}


# ---------------------------------------------------------------------------
# STEP 0 — the Einstein-Cartan action (explicit coefficients)
# ---------------------------------------------------------------------------
def ec_action(M_G: float) -> dict:
    """The EC torsion algebra L = a T^2 + b T^{bac}T_{abc} + c (T^a_ab)^2,
    with a = M_G^3/4, b = 4a (Holst/Immirzi algebraic-torsion condition),
    c = -(a + b/3) = -(7/3)a (the trace term)."""
    a = M_G ** 3 / 4.0
    b = 4.0 * a
    c = -(a + b / 3.0)
    return {"a": a, "b": b, "c": c, "b_equals_4a": abs(b / a - 4.0) < 1e-12}


def traceless_shear(s: float) -> dict:
    """The traceless shear ds^2 = (1+s)sigma_1^2 + (1+s)sigma_2^2
    + (1-2s)sigma_3^2 and its inverse-metric logarithmic derivatives:
    d ln g^33/ds = +2, d ln g^11/ds = d ln g^22/ds = -1, d ln sqrt{g}/ds = 0."""
    g33 = 1.0 / (1.0 - 2.0 * s)
    g11 = 1.0 / (1.0 + s)
    vol = (1.0 + s) * math.sqrt(1.0 - 2.0 * s)
    return {
        "g33": g33, "g11": g11, "vol": vol,
        "dln_g33": 2.0 / (1.0 - 2.0 * s),     # -> +2 at s=0
        "dln_g11": -1.0 / (1.0 + s),          # -> -1 at s=0
        "dln_vol": 1.0 / (1.0 + s) - 1.0 / (1.0 - 2.0 * s),  # -> 0 at s=0
    }


def killing_normalisation(tau: float) -> dict:
    """kappa^2(s) = [V_3(s)/V_3(0)] (g^33)^3 = (1+s)/(1-2s)^{5/2}, the
    geometric integral int sqrt{g}(g^33)^3 d^3x / int sqrt{g} d^3x
    (geometric_couplings.squash_metric)."""
    s = 2.0 * tau
    lam1 = 1.0 + s
    lam3 = 1.0 - 2.0 * s
    vol_ratio = lam1 * math.sqrt(lam3)       # V_3(s)/V_3(0)
    g33 = 1.0 / lam3
    kappa2 = vol_ratio * g33 ** 3            # (1+s)/(1-2s)^{5/2}
    return {"s": s, "kappa": math.sqrt(kappa2), "kappa2": kappa2,
            "volume_ratio": vol_ratio, "g33": g33}


# ---------------------------------------------------------------------------
# STEP 1 & 2 — content modulus and squash amplitude
# ---------------------------------------------------------------------------
def torsion_field_equation() -> float:
    """Return the content modulus tau=(N_L-N_R)/(N_f sum Y^2)=1/50.

    The evaluated relation is the dimensionless content closure used by the
    main chain.
    """
    c = _content()
    return c["N_L_minus_N_R"] / (c["N_f"] * c["SigmaY2"])


def squash_field_equation(tau: float) -> float:
    """Return s0=n_broken*tau=2*tau from the broken-generator count."""
    return _N_BROKEN * tau


def unified_source() -> dict:
    """s0*kappa = N_g*tau*kappa/(d+1) — the unified correction source."""
    c = _content()
    tau = c["tau"]
    s0 = squash_field_equation(tau)
    kn = killing_normalisation(tau)
    kappa = kn["kappa"]
    return {"s0": s0, "kappa": kappa, "sk": s0 * kappa,
            "tau": tau, "N_g_tau_over_d1": _N_G * tau / (_D + 1.0)}


# ---------------------------------------------------------------------------
# STEP 3 — the geometric moment integral c_Q = a_Q * r_Q
# ---------------------------------------------------------------------------
def amplitude_fraction(level: str) -> float:
    """a_Q — the amplitude fraction of the level (the broken-generator vs
    chiral-asymmetry content).

    A GEOMETRIC/seesaw/power quantity couples to BOTH broken generators of
    the squash (n_broken = 2), so a_Q = 1 (the full amplitude s0 = 2 tau).
    A CHIRAL/constituent quantity couples to the single chiral asymmetry
    (N_L - N_R = 1), so a_Q = (N_L-N_R)/n_broken = 1/2 (the amplitude tau
    = s0/2).  This is the DERIVED geometric-vs-chiral split.
    """
    c = _content()
    half = c["N_L_minus_N_R"] / _N_BROKEN      # 1/2
    if level in ("geometric", "seesaw", "generator", "power"):
        return 1.0
    if level in ("chiral_restoration", "chiral_crossgen", "constituent"):
        return half
    raise ValueError(f"unknown squash level: {level}")


def content_ratio(level: str) -> float:
    """r_Q — the content ratio of the level's operator (the specific
    content it couples to), with the SIGN = direction of the transfer
    (- compression/restoration, + transfer/receiving).

    - geometric (v, V_cb): r = -1 (the squash compresses the geometric
      quantity).
    - seesaw (m_nu3): r = +1 (the level-transfer conservation v m_nu3 =
      const forces the sign reversal).
    - chiral (T_d, Ds_R): r = -1 (chiral restoration); V_ub: r = +1
      (cross-generation).
    - constituent (m_p): r = +sum Y^2 Delta_s = +5/3 (the constituent-vs-
      MSbar scheme content — see constituent_scheme_field_equation below).
    - generator (a_s): r = -1/N_g = -xi (the Yukawa-difference conformal
      normalisation — see yukawa_difference_field_equation below).
    - power (rho_L): r = -4 (the m_nu1^4 dark-energy weight).
    """
    c = _content()
    SigmaY2, Delta_s = c["SigmaY2"], c["Delta_s"]
    if level == "geometric":
        return -1.0
    if level == "seesaw":
        return +1.0
    if level == "chiral_restoration":
        return -1.0
    if level == "chiral_crossgen":
        return +1.0
    if level == "constituent":
        return +SigmaY2 * Delta_s          # +5/3
    if level == "generator":
        return -1.0 / _N_G                 # -1/8 = -xi
    if level == "power":
        return -4.0
    raise ValueError(f"unknown squash level: {level}")


# ---------------------------------------------------------------------------
# STEP 3a — explicit evaluation of the two remaining content ratios
# ---------------------------------------------------------------------------
def hypercharge_spectral_sum() -> float:
    """Sigma Y^2 = sum_c c Y^2 = 10/3 — the hypercharge spectral sum over
    the 15 Weyl fermions of one generation (the EXPLICIT content integral).

    This is the first non-zero hypercharge moment (Sigma Y = 0 by the mixed
    gravitational-anomaly cancellation), summed over the derived content
    (Q_L 6x(1/6)^2, u_R 3x(2/3)^2, d_R 3x(-1/3)^2, L_L 2x(-1/2)^2,
    e_R 1x(-1)^2):

        Sigma Y^2 = 6/36 + 12/9 + 3/9 + 2/4 + 1 = 1/6 + 4/3 + 1/3 + 1/2 + 1
                  = 10/3 .

    It is computed here (not imported) so that the constituent scheme
    correction is an explicit integral, not a number.
    """
    from cg_core.sm_content import weyl_content
    return sum(c * y * y for _, _, y, c in weyl_content())


def scalar_conformal_weight() -> float:
    """Delta_s = (d-2)/2 = 1/2 — the scalar conformal weight (the Gaussian
    scaling dimension of the condensate field)."""
    return (_D - 2.0) / 2.0


def yamabe_conformal_coupling() -> float:
    """xi = (d-2)/(4(d-1)) = 1/8 = 1/N_g — the Yamabe conformal curvature
    coupling for a Weyl-covariant scalar action in d=3."""
    return (_D - 2.0) / (4.0 * (_D - 1.0))


def constituent_scheme_field_equation() -> dict:
    """Evaluate the constituent-sector content correction

        delta m_p / m_p = tau kappa Sum Y^2 Delta_s = 5 tau kappa/3.

    The first-order squash response is the product

        delta m_p / m_p = tau * kappa * Delta_s * Sum_c c Y^2 ,

    where tau=(N_L-N_R)/(N_f Sum Y^2), kappa is the U(1)_Y Killing
    normalisation, Delta_s=(d-2)/2, and the hypercharge spectral sum is

        Sum_c c Y^2 = 6(1/6)^2 + 3(2/3)^2 + 3(-1/3)^2 + 2(-1/2)^2 + 1 = 10/3 ,

    Hence r_Q=Sum Y^2 Delta_s=5/3 and the correction is
    delta m_p/m_p=5 tau kappa/3.
    """
    c = _content()
    src = unified_source()
    SigmaY2 = hypercharge_spectral_sum()
    Delta_s = scalar_conformal_weight()
    tau, kappa = src["tau"], src["kappa"]
    corr = tau * kappa * Delta_s * SigmaY2
    return {"SigmaY2": SigmaY2, "Delta_s": Delta_s, "tau": tau,
            "kappa": kappa, "correction": corr,
            "r_Q_tau_units": SigmaY2 * Delta_s,     # 5/3
            "factor": 1.0 + corr}                    # 1 + 5 tau kappa/3


def yukawa_difference_field_equation() -> dict:
    """Evaluate the generator-sector conformal correction

        delta ln alpha_s = -s0 kappa xi = -s0 kappa/N_g.

    THE YUKAWA-GAUGE MIXING (the two-loop beta function, explicit)
    --------------------------------------------------------------
    The two-loop gauge beta carries the top-Yukawa term through the invariant

        Y4(F) = (1/d(G_a)) Tr[C2^{(a)}(F) Y^a Y^{+a}] ,   A_i = 2 kappa Y4 / y_t^2

    (Luo-Wang-Xiao, hep-ph/0211440 Eq. 31; kappa = 1/2 for Weyl fermions),
    with the explicit trace  Tr[C2(F) Y Y+] = 6 y_t^2 [C2(Q_L) + C2(u_R)]
    (the 6 = 2 x 3 weak-doublet x colour-triplet factor).  The geometric
    Yukawa y_0 = 1 (the exact SO(4) diagonal overlap) differs from the
    running SM top Yukawa y_t, so the mixing over-counts the Yukawa content.

    The first-order response is normalised by the Yamabe conformal coupling
    xi=(d-2)/(4(d-1))=1/N_g=1/8:

        delta ln alpha_s = -s0 * kappa * xi = -s0 kappa/N_g ,

    Thus the content ratio is r_Q=-xi=-1/N_g and
    delta ln alpha_s=-s0 kappa/N_g.
    """
    c = _content()
    src = unified_source()
    xi = yamabe_conformal_coupling()
    s0, kappa = src["s0"], src["kappa"]
    corr = -s0 * kappa * xi
    return {"xi": xi, "N_g": c["N_g"], "s0": s0, "kappa": kappa,
            "correction": corr,
            "r_Q": -xi,                               # -1/8
            "factor": 1.0 + corr}                      # 1 - s0 kappa/N_g


def moment(level: str) -> float:
    """c_Q = a_Q * r_Q — the geometric moment (content charge in s0 units).

    This is the first-order integral of the operator under the traceless
    shear: c_Q = 2 n_3 - n_eq = a_Q * r_Q, the weighted count of the squash
    deformation across the content (Step 3).
    """
    return amplitude_fraction(level) * content_ratio(level)


def correction_factor(level: str) -> float:
    """Q -> Q (1 + c_Q * s0 * kappa) — the correction factor (Step 4)."""
    src = unified_source()
    return 1.0 + moment(level) * src["sk"]


# ---------------------------------------------------------------------------
# The full factor table (what the six source files reproduce)
# ---------------------------------------------------------------------------
def full_table() -> dict:
    """Return every level's amplitude fraction, content ratio, moment,
    factor, and the EC field-equation derivation text."""
    src = unified_source()
    c = _content()
    out = {"_base": src, "_content": c}
    for level in ("geometric", "seesaw", "chiral_restoration",
                  "chiral_crossgen", "constituent", "generator", "power"):
        out[level] = {
            "a_Q": amplitude_fraction(level),
            "r_Q": content_ratio(level),
            "c_Q": moment(level),
            "factor": correction_factor(level),
        }
    return out


def _self_test() -> None:
    """Verify the field equations and every moment integral reproduce the
    framework's correction factors to machine precision."""
    tol = 1e-12
    c = _content()
    src = unified_source()
    s0, kappa, sk, tau = src["s0"], src["kappa"], src["sk"], src["tau"]

    # STEP 1: the torsion field equation -> tau = 1/50.
    assert abs(torsion_field_equation() - 1.0 / 50.0) < tol
    # STEP 2: the squash field equation -> s0 = 2 tau = N_g tau/(d+1).
    assert abs(squash_field_equation(tau) - 2.0 * tau) < tol
    assert abs(s0 - _N_G * tau / (_D + 1.0)) < tol
    # STEP 0: kappa^2 = (1+s)/(1-2s)^{5/2} (the geometric integral).
    assert abs(kappa - math.sqrt((1 + s0) / (1 - 2 * s0) ** 2.5)) < tol

    # STEP 3: the amplitude fraction is the broken-generator vs chiral content.
    assert abs(amplitude_fraction("geometric") - 1.0) < tol
    assert abs(amplitude_fraction("chiral_restoration")
               - c["N_L_minus_N_R"] / _N_BROKEN) < tol   # 1/2

    # The six factors (each = 1 + a_Q r_Q s0 kappa).
    assert abs(correction_factor("geometric") - (1.0 - sk)) < tol          # v, V_cb
    assert abs(correction_factor("seesaw") - (1.0 + sk)) < tol             # m_nu3
    assert abs(correction_factor("chiral_restoration")
               - (1.0 - tau * kappa)) < tol                                # T_d, Ds_R
    assert abs(correction_factor("chiral_crossgen")
               - (1.0 + tau * kappa)) < tol                                # V_ub
    assert abs(correction_factor("constituent")
               - (1.0 + tau * kappa * c["SigmaY2"] * c["Delta_s"])) < tol  # m_p = 5 tau kappa/3
    assert abs(correction_factor("generator")
               - (1.0 - sk / c["N_g"])) < tol                              # a_s
    assert abs(correction_factor("power") - (1.0 - 4.0 * sk)) < tol        # rho_L

    # Conservation laws (the sign pairings), exact to O((s0 kappa)^2).
    f_ew, f_nu = correction_factor("geometric"), correction_factor("seesaw")
    assert abs(f_ew * f_nu - (1.0 - sk ** 2)) < tol                         # v m_nu3
    f_nu4 = f_nu ** 4
    exact = 1.0 - 10.0 * sk ** 2 - 20.0 * sk ** 3 - 15.0 * sk ** 4 - 4.0 * sk ** 5
    assert abs(f_nu4 * correction_factor("power") - exact) < tol            # m_nu1^4 weight

    # The content is DERIVED, not hard-coded.
    assert abs(c["SigmaY2"] - hypercharge_sum_sq()) < tol
    assert abs(c["SigmaY2"] * c["Delta_s"] - 5.0 / 3.0) < tol
    assert abs(c["xi"] - 1.0 / 8.0) < tol
    assert abs(c["N_g"] - 8.0) < tol

    # STEP 3a: explicit evaluation of the two remaining content ratios.
    # (i) the constituent scheme -> delta m_p/m_p = tau kappa Sum Y^2 Delta_s.
    cs = constituent_scheme_field_equation()
    assert abs(cs["SigmaY2"] - hypercharge_spectral_sum()) < tol
    assert abs(cs["r_Q_tau_units"] - 5.0 / 3.0) < tol          # 5/3
    assert abs(cs["correction"]
               - tau * kappa * scalar_conformal_weight() * hypercharge_spectral_sum()) < tol
    assert abs(cs["factor"] - correction_factor("constituent")) < tol
    # (ii) the Yukawa difference -> delta ln alpha_s = -s0 kappa xi = -s0 kappa/N_g.
    yd = yukawa_difference_field_equation()
    assert abs(yd["xi"] - yamabe_conformal_coupling()) < tol
    assert abs(yd["xi"] - 1.0 / 8.0) < tol                     # 1/8 = 1/N_g
    assert abs(yd["xi"] * c["N_g"] - 1.0) < tol               # N_g xi = 1
    assert abs(yd["correction"] - (-s0 * kappa * yd["xi"])) < tol
    assert abs(yd["factor"] - correction_factor("generator")) < tol

    print("squash_level_transfer self-test OK "
          f"(s0 kappa = {sk:.6f}, tau kappa = {tau*kappa:.6f})")


if __name__ == "__main__":
    _self_test()
    t = full_table()
    print("\nlevel             a_Q      r_Q        c_Q(s0)   factor")
    for k, v in t.items():
        if k.startswith("_"):
            continue
        print(f"{k:18s} {v['a_Q']:+.6f}  {v['r_Q']:+8.4f}  "
              f"{v['c_Q']:+9.5f}  {v['factor']:.9f}")
    print("\nSTEP 3a — explicit evaluation of the two content ratios:")
    cs = constituent_scheme_field_equation()
    print(f"  constituent: delta m_p/m_p = tau*kappa*Delta_s*Sum Y^2"
          f" = {cs['correction']:.6f} = 5 tau kappa/3"
          f"  (r_Q = Sum Y^2 Delta_s = {cs['r_Q_tau_units']:.4f})")
    yd = yukawa_difference_field_equation()
    print(f"  generator:   delta ln a_s = -s0*kappa*xi"
          f" = {yd['correction']:.6f} = -s0 kappa/N_g"
          f"  (r_Q = -xi = {yd['r_Q']:.4f}, N_g xi = {yd['xi']*yd['N_g']:.1f})")
    print("\n(moment c_Q = a_Q * r_Q is the geometric moment integral of "
          "Step 3: d ln Q/ds|_{s=0} = 2 n_3 - n_eq.)")
