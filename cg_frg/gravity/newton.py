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

"""Guo (2026g) common-Planck-unit five-channel prescribed combined readout.

The five finite-domain channel sums define the combined algebraic readout.
The observed Newton constant supplies the dimensionful anchor.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
EIGHT_PI = 8.0 * math.pi


def long_root_eigenvalue(L: float) -> float:
    """Assigned C2(2,1)/L^2 in the units of L."""
    if not math.isfinite(L) or L <= 0:
        raise ValueError("L must be finite and positive")
    return 16.0 / (L * L)


def G_N_from_Z(Z_phys: float, M_P: float) -> float:
    """Evaluate 1/(8*pi*Z_phys*M_P^2) for the specified readout coefficient."""
    if not (math.isfinite(Z_phys) and math.isfinite(M_P)) or not (0 < Z_phys <= 1 and M_P > 0):
        raise ValueError("require 0 < Z <= 1 and M_P > 0")
    return 1.0 / (EIGHT_PI * Z_phys * M_P * M_P)


def prescribed_readout(k: float, L: float, tau: float, M_P: float) -> dict:
    """k,M_P use one mass unit and L its reciprocal.

    A unit change k->a*k, M_P->a*M_P, L->L/a leaves r_read and Z_read
    invariant. R=5 specifies the finite Gaussian response domain.
    """
    if not all(math.isfinite(x) for x in (k, L, tau, M_P)) or min(k, L, M_P) <= 0:
        raise ValueError("finite positive k,L,M_P and finite tau required")
    from cg_frg.frg.spectral_sum import (
        channel_tmunu_spin2, channel_tmunu_spin0, channel_f2,
        channel_g2, channel_jmu)
    L_hat, k_hat = M_P * L, k / M_P
    V_hat = math.pi ** 2 * L_hat ** 3
    channels = {}
    for name, fn in zip(("T2", "T0", "F2", "G2", "J"), (
            channel_tmunu_spin2, channel_tmunu_spin0, channel_f2,
            channel_g2, channel_jmu)):
        channels[name] = V_hat * fn(L_hat, k_hat * k_hat, tau)["rp3_pi0"]
    signed_sum = math.fsum(channels.values())
    sigma_hat = abs(signed_sum) * k_hat ** 2
    lam_hat = long_root_eigenvalue(L_hat)
    ratio = sigma_hat / lam_hat
    Z_read = 1.0 / (1.0 + ratio)
    return {"L_hat": L_hat, "k_hat": k_hat, "channels": channels,
            "signed_sum_hat": signed_sum, "sigma_hat": sigma_hat,
            "sigma_read": M_P ** 2 * sigma_hat,
            "lambda_long_hat": lam_hat, "lambda_long": M_P ** 2 * lam_hat,
            "r_read": ratio, "Z_read": Z_read,
            "G_anchor": 1.0 / (EIGHT_PI * M_P ** 2),
            "G_read": G_N_from_Z(Z_read, M_P), "response_domain_R": 5,
            "external_pole_established": False}


def _sigma_response(k: float, kL: float, tau: float, M_P: float) -> float:
    """Evaluate the prescribed density normalisation at L=kL/k."""
    return prescribed_readout(k, kL / k, tau, M_P)["sigma_read"]


def compute() -> dict:
    """Publish the common-unit readout, with GN as the dimensional anchor."""
    from cg_core.params import get, set as pset
    M_P, M_G = float(get("M_P")), float(get("M_G"))
    r = prescribed_readout(M_G, float(get("kL")) / M_G, float(get("tau")), M_P)
    for key in ("r_read", "Z_read", "G_read"):
        pset("gravity_" + key, r[key], provenance="DERIVED", role="comparison",
             note="Guo (2026g) common-Planck-unit finite-domain combined readout "
                  "from the five stated channels; GN supplies the dimensional anchor.")
    pset("gravity_readout_channels", r, provenance="DERIVED", role="comparison",
         note="All five channels use L_hat=M_P L and k_hat=k/M_P; "
              "G_read is the separately defined combined response.")
    pset("G_N_verdict", "GN is the dimensionful anchor; G_read is the "
         "prescribed finite-domain combined response.",
         provenance="DERIVED", role="informational",
         note="Identity of the dimensional anchor and the separately defined combined response.")
    return r


if __name__ == "__main__":
    print(compute())
