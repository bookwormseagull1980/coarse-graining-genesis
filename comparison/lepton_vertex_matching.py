"""Comparison of a calculated lepton conversion with isolated pole data.

The required matching is a comparison target. This module does not select
individual correction factors or return inputs to the production chain.
"""
from __future__ import annotations

import math

from cg_core.params import published_sm_value


def compare_lepton_vertex_matching(diagnostic):
    """Read reference poles only after the generated diagnostic is complete."""
    reference = published_sm_value("charged_lepton_pole_reference")
    masses = reference["masses_GeV"]
    weights = {"electron": -1, "muon": 2, "tau": -1}
    pole_log = math.fsum(weight * math.log(masses[name])
                         for name, weight in weights.items())
    required_pole = pole_log - diagnostic["geometric_log_invariant"]
    delta_d = diagnostic["pole_to_MSbar"]["Delta_D_first_order"]
    required_c = required_pole + delta_d
    return {
        "reference": reference["citation"],
        "reference_pole_log_invariant": pole_log,
        "required_Delta_pole": required_pole,
        "required_Delta_C_first_order_at_generated_mass_arguments": required_c,
        "minimum_required_log_C_spread_first_order": abs(required_c) / 2,
        "interpretation": "necessary weighted matching target; no individual C or G inferred",
        "mass_arguments": "same zeroth-order generated masses as the diagnostic D kernel",
        "reference_used_as_prediction_input": False,
    }
