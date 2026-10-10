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

"""Density-unit representation of the common-unit prescribed readout.

The combined finite-domain response uses common Planck units. Its
density representation and mass-squared representation are related by
sigma_read = abs(density_read)/M_P^2.
"""
from __future__ import annotations
import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from cg_frg.gravity.newton import prescribed_readout


def trace_density(k: float, L: float, tau: float, M_P: float) -> float:
    """Signed M_P^4 S_hat k_hat^2 readout; not a physical stress tensor."""
    r = prescribed_readout(k, L, tau, M_P)
    return r["signed_sum_hat"] * r["k_hat"] ** 2 * M_P ** 4


def sigma_self_energy(k: float, L: float, tau: float, M_P: float) -> float:
    """Prescribed mass-squared readout sigma_read=|density_read|/M_P^2."""
    return prescribed_readout(k, L, tau, M_P)["sigma_read"]


def compute() -> dict:
    from cg_core.params import get, set as pset
    M_G, M_P = float(get("M_G")), float(get("M_P"))
    kL, tau = float(get("kL")), float(get("tau"))
    r = prescribed_readout(M_G, kL / M_G, tau, M_P)
    density = r["signed_sum_hat"] * r["k_hat"] ** 2 * M_P ** 4
    pset("gravity_density_read_MG", density, provenance="DERIVED", role="comparison",
         note="Signed density-unit representation of the Guo (2026g) combined readout; "
              "not a stress-tensor expectation or QFT self-energy.")
    return {"density_read": density, "sigma_read": r["sigma_read"], "kL": kL}


if __name__ == "__main__":
    print(compute())
