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

"""Compare the declared Gaussian endpoint with the Litim response.

The current Gaussian endpoint is read from the common parameter store.
The alternative response is solved with the same matter content. The common
readout evaluates the resulting finite change and its local derivative.
This comparison measures dependence on the response prescription.
"""
import sys, math
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get
from cg_core.joint_response import evaluate, log_jacobian
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
        if mid == lo or mid == hi:
            return mid
        f = v_pi0(mid, kL, tau, M_G, M_P, scheme) - ec.CRIT
        if f == 0.:
            return mid
        if flo * f < 0:
            hi = mid
        else:
            lo = mid
            flo = f
    return 0.5 * (lo + hi)


def solve_kL(scheme):
    if scheme == "gaussian":
        return float(get("kL"))
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
    tau, M_P = float(get("tau")), float(get("M_P"))
    gaussian = evaluate(kL_g, tau, M_P)
    alternative = evaluate(kL_l, tau, M_P)
    slopes = log_jacobian(kL_g, tau, M_P)
    print("Shared readout at fixed tau and M_P:")
    for key in ("v_HIGGS", "m_e_pred", "rho_Lambda"):
        change = 100*(alternative[key]/gaussian[key]-1)
        print(f"  {key:12s} change={change:+.8g}%, "
              f"Gaussian dln/dln(c)={slopes[key][0]:+.8f}")
