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

"""Analytic shared-input sensitivities of the current parameter records.

The common response supplies central values and logarithmic derivatives
with respect to c=kL, tau and M_P, at fixed matter content, response domain
and matching conditions. The optional threshold analysis uses the
fixed-branch relation A_R/c=T and therefore d ln(c)/d ln(T)=-1.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get  # noqa: E402
from cg_core.joint_response import INPUTS, RATIO_READOUTS, evaluate, log_jacobian  # noqa: E402


def current_response() -> tuple[dict, dict]:
    """Read one input set and check the common response against the store."""
    point = tuple(float(get(key)) for key in ("kL", "tau", "M_P"))
    central = evaluate(*point)
    for key, value in central.items():
        if key in RATIO_READOUTS:
            numerator, denominator = RATIO_READOUTS[key]
            stored = float(get(numerator))/float(get(denominator))
        else:
            stored = float(get(key))
        if not math.isclose(value, stored, rel_tol=2e-10, abs_tol=0.):
            raise ValueError(f"shared response differs from the current record: {key}")
    return central, log_jacobian(*point)


def main() -> int:
    central, rows = current_response()
    print("Analytic logarithmic sensitivities at the current endpoint")
    print("Central values use the quantity names and units of the parameter store.")
    print(f"{'quantity':28s} {'value':>14s}" +
          "".join(f"{'dln/dln '+name:>16s}" for name in INPUTS))
    for key, row in rows.items():
        print(f"{key:28s} {central[key]:14.7g}" +
              "".join(f"{entry:+16.8f}" for entry in row))
    print("The derivatives hold at fixed content, response domain and matching rules.")
    print("A fractional input change gives E times that fractional change to first order.")
    print("The M_P derivative equals the quantity's mass dimension.")
    return 0


def threshold_sensitivity() -> None:
    """Propagate A_R/c=T on the same fixed-content endpoint branch."""
    _, rows = current_response()
    print("Fixed-branch threshold sensitivity: c=A_R/T, T=4/27")
    print("d ln(c)/d ln(T) = -1; tau and M_P are fixed.")
    for key, row in rows.items():
        print(f"{key:28s} d ln(output)/d ln(T) = {-row[0]:+.8f}")


if __name__ == "__main__":
    if "--threshold" in sys.argv:
        threshold_sensitivity()
    else:
        sys.exit(main())
