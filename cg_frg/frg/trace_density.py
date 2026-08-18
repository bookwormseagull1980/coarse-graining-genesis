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
cg_frg/frg/trace_density.py — V4.0: the SM supertrace density on
RP³ (the matter self-energy source of the gravitational sector)
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The matter back-reaction of the gravitational sector is the SM
supertrace density on the internal RP³: the sum over the full SM
content (12 gauge + 24 ghost + 4 Higgs scalars + 45 Weyl fermions)
of the one-loop spectral weights, normalised by the RP³ volume:

    trace_density(k, L, tau) = Σ_channels V₃·Π²_channel / k²

with V₃ = π²L³ the RP³ volume and Π²_channel the five-channel
spectral sums of the improved EMT (spin-2, spin-0, F², G², J^μ —
the spectral_sum engine).  The density feeds the TT self-energy

    σ(k) = |trace_density| / M_P²

used by newton.py's Z_phys decomposition (the matter back-reaction
on the graviton residue).

V4 DISCIPLINE
-------------
The module is a pure engine over the spectral_sum channels (no
physics value hard-coded); the five-channel sum is the framework's
own SM content (sm_content).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_frg.frg.spectral_sum import (  # noqa: E402
    channel_tmunu_spin2, channel_tmunu_spin0, channel_f2,
    channel_g2, channel_jmu)
from cg_core.params import get, set as pset  # noqa: E402

CHANNELS = (channel_tmunu_spin2, channel_tmunu_spin0, channel_f2,
            channel_g2, channel_jmu)


def trace_density(k: float, L: float, tau: float, M_P: float) -> float:
    """The SM supertrace density (GeV⁴): the five-channel sum ×
    V₃/k², normalised by the RP³ volume."""
    V3 = math.pi ** 2 * L ** 3
    cut = (k / M_P) ** 2
    total = sum(V3 * ch(L, cut, tau)["rp3_pi0"] for ch in CHANNELS)
    return total / (k * k)


def sigma_self_energy(k: float, L: float, tau: float, M_P: float) -> float:
    """σ = |trace_density|/M_P² — the TT self-energy (GeV²)."""
    return abs(trace_density(k, L, tau, M_P)) / (M_P * M_P)


def compute() -> dict:
    """Publish the density and self-energy at the emergence scale."""
    M_G = get("M_G")
    M_P = get("M_P")
    kL = get("kL")
    tau = get("tau")
    L = kL / M_G
    td = trace_density(M_G, L, tau, M_P)
    sig = sigma_self_energy(M_G, L, tau, M_P)
    pset("trace_density_MG", td, provenance="DERIVED",
         note="the SM supertrace density at M_G (the five-channel "
              "sum of the improved EMT, normalised by V3/k^2)")
    return {"trace_density": td, "sigma_MG": sig, "kL": kL}


if __name__ == "__main__":
    r = compute()
    print(f"trace_density(M_G) = {r['trace_density']:.4e} GeV^4, "
          f"sigma = |td|/M_P^2 = {r['sigma_MG']:.3e} GeV^2")
    print("trace_density OK")
