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

"""Regime-comparison experiment: re-solve the F_MG fixed point kL with
each regularisation scheme (gaussian vs litim) and report the spread.
This gives an OBJECTIVE estimate of the convention blur, replacing the
subjective priors (y -> 1.10y, p -> 1.01p) of the error-band table.
"""
import sys, math
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get
from cg_frg.frg import endpoint_constraint as ec
from cg_frg.frg.spectral_sum import channel_tmunu_spin2


def v_pi0(k, kL, tau, M_G, M_P, scheme):
    L = kL * M_G / k
    V3 = math.pi ** 2 * L ** 3
    cut = (k / M_P) ** 2
    return V3 * channel_tmunu_spin2(L, cut, tau, scheme)["rp3_pi0"] / ec.FACTOR


def k_star(kL, tau, M_G, M_P, scheme):
    lo, hi = 0.3 * M_G, 3.0 * M_G
    flo = v_pi0(lo, kL, tau, M_G, M_P, scheme) - ec.CRIT
    fhi = v_pi0(hi, kL, tau, M_G, M_P, scheme) - ec.CRIT
    if flo * fhi > 0:
        raise RuntimeError(f"no crossing for {scheme}")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f = v_pi0(mid, kL, tau, M_G, M_P, scheme) - ec.CRIT
        if (hi - lo) < 1e-15:
            return mid
        if flo * f < 0:
            hi = mid
        else:
            lo = mid
            flo = f
    return 0.5 * (lo + hi)


def solve_kL(scheme):
    M_P = get("M_P")
    tau = get("tau")
    L_Cg = get("L_Cg")
    C = M_P * L_Cg
    kL = get("kL")
    for _ in range(60):
        M_G = C / kL
        kL_new = C / k_star(kL, tau, M_G, M_P, scheme)
        if abs(kL_new - kL) < 1e-15:
            kL = kL_new
            break
        kL = kL_new
    return kL


if __name__ == "__main__":
    kL_g = solve_kL("gaussian")
    kL_l = solve_kL("litim")
    spread = (kL_l / kL_g - 1.0) * 100.0
    print(f"kL(gaussian) = {kL_g:.9f}")
    print(f"kL(litim)    = {kL_l:.9f}")
    print(f"scheme spread = {spread:+.3f}%")
    # propagate into the hierarchy (elasticities from the matrix)
    E = {"v": -32.3, "m_e": -49.9, "rho_Lambda": -261.6}
    print("propagation (spread of kL -> output):")
    for q, e in E.items():
        print(f"  {q:12s} {e * spread / 100 * 100:+.2f}%")
