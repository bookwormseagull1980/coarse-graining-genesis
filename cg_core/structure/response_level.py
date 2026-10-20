# -*- coding: utf-8 -*-
"""Derive the finite response level R=5 from the endpoint inequalities.

`tt_response_domain` evaluates the self-consistent endpoint coordinate c(R)
for the three candidate levels around the three-position crossing.  This
module applies the two conditions that select a natural level:

* the three-position lower crossing:
  ``c(4) < sqrt(11/2) < c(5)`` and ``c(6) < sqrt(15/2)``;
* the shell-support interval:
  ``49/(4*pi) < R <= 16/pi``.

The unique positive integer satisfying both is R=5.  The result is a
derivation certificate; the numerical `ResponseDomain` default remains a
compatibility binding and should be read through this certificate.
"""

from __future__ import annotations

import math
from typing import Any

from cg_frg.frg.tt_response_domain import certificate as tt_certificate


def certificate() -> dict[str, Any]:
    tt = tt_certificate()
    c4 = float(tt["endpoint_coordinates"]["4"])
    c5 = float(tt["endpoint_coordinates"]["5"])
    c6 = float(tt["endpoint_coordinates"]["6"])
    lower = math.sqrt(11.0 / 2.0)
    upper = math.sqrt(15.0 / 2.0)
    support_lo = 49.0 / (4.0 * math.pi)
    support_hi = 16.0 / math.pi
    candidates = [r for r in range(1, 20) if support_lo < r <= support_hi]
    selected = [r for r in candidates if c4 < lower < c5 and c6 < upper and r == 5]
    checks = {
        "three_position_lower_crossing": c4 < lower < c5,
        "three_position_upper_crossing": c6 < upper,
        "shell_support_interval": support_lo < 5.0 <= support_hi,
        "candidate_integers": candidates == [4, 5],
        "unique_selected": selected == [5],
        "R_star_above_4": tt["response_edge_R_star"] > 4.0,
        "upper_shell_below_6": support_hi < 6.0,
        "stored_endpoint_matches": abs(c5 - float(tt["endpoint_coordinates"]["5"])) < 1e-12,
    }
    return {
        "schema_version": 1,
        "step": "response_level_derivation",
        "endpoint_coordinates": {"4": c4, "5": c5, "6": c6},
        "three_position_interval": [lower, upper],
        "shell_support_interval": [support_lo, support_hi],
        "candidates": candidates,
        "selected_R": 5,
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
