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

"""Specified pseudo-dilaton constitutive readout.

lambda_dil=4*pi*N_generations and sigma_content=N_generations give
lambda_H=(lambda_dil+sigma_content)/(32*pi^2). The framework uses this
numerical rule as a separate quartic readout. A strong-coupling estimate does
not determine a renormalized action's quartic or its beta function.

pseudo_dilaton_beta_eff is the named algebraic response coefficient evaluated
below. It is not beta_lambda of the MSbar Higgs quartic. Running a physical
quartic requires a declared canonical boundary, scale and scheme, as provided
by cg_core.gauge_running.coupled_run. For an actual scalar potential,
canonical_potential_vertices converts its supplied derivatives and kinetic
coefficient into canonical local vertices without using the target quartic.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.sm_content import N_GENERATIONS as _N_GENERATIONS  # noqa: E402

# N_generations = 3: the trace anomaly couples to all three SM
# generations, so both the dilaton self-coupling and the SM loop
# contribution carry the generation factor.
N_GENERATIONS = float(_N_GENERATIONS)


def canonical_potential_vertices(*, second_derivative, third_derivative,
                                 fourth_derivative, kinetic_coefficient):
    """Canonical local derivatives of a supplied real radial potential.

    For L_kin=Z/2 (dE)^2 and h=sqrt(Z)E, m²=V''/Z, the cubic vertex
    is V'''/Z^(3/2), and lambda_radial=V''''/(6Z²) multiplies h^4/4.
    Values must be derivatives of the same specified action at the same
    background. This is not an identification of lambda_H_pseudo with them.
    """
    values=(second_derivative,third_derivative,fourth_derivative,kinetic_coefficient)
    if not all(math.isfinite(x) for x in values) or kinetic_coefficient<=0:
        raise ValueError("finite derivatives and strictly positive kinetic coefficient required")
    Z=kinetic_coefficient
    return {"mass_squared":second_derivative/Z,
            "cubic_vertex":third_derivative/Z**1.5,
            "quartic_radial":fourth_derivative/(6*Z*Z),
            "quartic_convention":"V=lambda_radial*h^4/4"}


def compute() -> dict:
    """Evaluate and publish the specified pseudo-dilaton constitutive rule."""
    g2 = float(get("g2_MG"))
    g1 = float(get("g1_MG_geo"))
    yt = float(get("y_top_base"))

    # Assigned strong factor 4*pi per generation and one content unit per
    # generation. Their algebraic combination is not an action derivative.
    lam_dil = N_GENERATIONS * 4.0 * math.pi
    sigma_SM = N_GENERATIONS
    lam_H = (lam_dil + sigma_SM) / (32.0 * math.pi ** 2)
    # Named algebraic response coefficient, distinct from beta_lambda.
    beta_pure = (3.0 * g2 ** 2 + g1 ** 2 + 4.0 * yt ** 2
                 + 2.0 * lam_H) / (16.0 * math.pi ** 2)
    beta_strong = lam_dil / (16.0 * math.pi ** 2)
    beta_eff = beta_pure + beta_strong

    pset("lambda_dil", lam_dil, provenance="DERIVED", role="internal",
         dependencies=(),
         note=f"lambda_dil = N_generations*4*pi = {lam_dil:.4f}; "
              f"specified strong-factor readout, not a matched action quartic")
    pset("lambda_H_pseudo", lam_H, provenance="DERIVED", role="internal",
         dependencies=(),
         note=f"lambda_H = (12 pi + 3)/(32 pi^2) = 3(4 pi + 1)/(32 pi^2) = "
              f"{lam_H:.4f}; specified pseudo-dilaton constitutive quartic "
              f"with one content unit per generation")
    pset("pseudo_dilaton_beta_eff", beta_eff, provenance="DERIVED",
         dependencies=("g2_MG", "g1_MG_geo", "y_top_base"),
         role="internal",
         note=f"beta_eff = (3 g2^2 + g1^2 + 4 yt^2 + 2 lambda_H)/(16 pi^2) "
              f"+ 12 pi/(16 pi^2) = {beta_eff:.4f}; named algebraic response "
              f"coefficient, not the MSbar beta function of lambda_H")

    return {"lambda_dil": lam_dil, "lambda_H": lam_H,
            "beta_pure": beta_pure, "beta_strong": beta_strong,
            "beta_eff": beta_eff}


if __name__ == "__main__":
    r = compute()
    print(f"lambda_dil = {r['lambda_dil']:.2f}")
    print(f"lambda_H   = {r['lambda_H']:.4f} (the pseudo-dilaton consistency)")
    print(f"beta_eff   = {r['beta_eff']:.4f} (pure {r['beta_pure']:.4f} "
          f"+ strong {r['beta_strong']:.4f})")
    print("pseudo_dilaton OK")
