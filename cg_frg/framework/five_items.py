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

"""Current closure checks computed from their actual defining relations.

Status follows residuals and the joint screening/platform calculation.
An algebraic reconstruction is not an independent physical prediction;
the declared charge branch is checked for anomaly compatibility, not
selected by the status report. No observational target enters a check.
"""

from __future__ import annotations

import sys
import math
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.content_response import screening_compatibility, chiral_anomalies
from cg_frg.generation.window_capacity import count_generations


INPUTS = ("kL", "tau", "n_generations", "twoL_entropy_min_distance",
          "M_P", "M_G", "v_HIGGS", "m_e_pred")


def verify_closures(values, tolerance=2e-11):
    """Evaluate only the declared relations; failures remain visible."""
    if tolerance <= 0 or not math.isfinite(tolerance):
        raise ValueError("positive finite residual tolerance required")
    c, tau = values["kL"], values["tau"]
    if c <= 0 or not 0 <= tau < 0.25:
        raise ValueError("positive capacity and nonsingular squash required")
    select = screening_compatibility()
    count, modes, margins = count_generations(c)
    kappa = math.sqrt((1+2*tau)/(1-4*tau)**2.5)
    factor = 1-2*tau*kappa
    vev = values["M_G"]*3/(16*math.pi**3)*math.exp(-4*math.pi*c)*factor
    electron = values["M_P"]*math.exp(-20*c)*factor*1e3
    def residual(got, want):
        return abs(got-want)/max(abs(want), 1e-300)
    def checked(error, definition):
        return {"status": "PASS" if error <= tolerance else "FAIL",
                "residual": error, "definition": definition}
    items = {
        "joint_generation_selection": {
            "status": "PASS" if count == select["generations"] == values["n_generations"]
                      and select["colour_residual"] == 0 else "FAIL",
            "selected_copies": select["generations"], "retained_modes": modes,
            "margins": margins, "premises": list(select["premises"]),
            "definition": "extensive-source/colour selection plus endpoint position count"},
        "charge_branch": {
            "status": "specified branch; anomaly check passed" if
                      all(v == 0 for v in chiral_anomalies().values()) else "FAIL",
            "definition": "anomaly compatibility of the specified charge carrier"},
        "gaussian_distance": checked(residual(values["twoL_entropy_min_distance"],
                                               math.sqrt(2*math.pi)),
                                     "calibrated Gaussian endpoint distance"),
        "window_vev": checked(residual(values["v_HIGGS"], vev),
                              "same-input window VEV relation; not independent routes"),
        "electron_mass": checked(residual(values["m_e_pred"], electron),
                                 "specified exponential/cascade identity in MeV"),
    }
    return {"items": items, "passed": all(x["status"] != "FAIL" for x in items.values()),
            "checked_relations": sum(x["status"] == "PASS" for x in items.values()),
            "tolerance": tolerance, "observational_agreement_used": False}


def compute() -> dict:
    """Publish checks only after all current input relations pass."""
    result = verify_closures({key: get(key) for key in INPUTS})
    if not result["passed"]:
        raise ArithmeticError(f"framework defining relation failed: {result}")
    pset("five_items_status", result, provenance="DERIVED", role="informational",
         note="Computed joint-selection, anomaly and algebraic residual checks; "
              "a charge-branch premise is not an independently selected outcome.",
         dependencies=INPUTS, evidence_kind="evaluated conditional relations")
    return result


if __name__ == "__main__":
    r = compute()
    for k, v in r["items"].items():
        print(f"  {k}: {v['status']}")
    print(f"checked relations: {r['checked_relations']}; branch separately declared")
    print("five_items OK")
