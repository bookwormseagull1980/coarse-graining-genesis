# -*- coding: utf-8 -*-
"""Capacity/endpoint/YM structural certificates.

This module connects the V5 structural layer to the numerical chain:

* the exact TT response maximum 4/27;
* the finite-response endpoint certificate and the unique integer R = 5;
* the generated Yang--Mills positive spectral bottom.

The certificates are computed from V5's own modules, not from Lean.  The
gravity sector is kept separate: V5's gravity is an effective collective
response, not a fundamental quantum field.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from cg_core.params import get
from cg_core.structure.response_level import certificate as response_level_certificate
from cg_frg.frg.tt_response_domain import certificate as tt_certificate
from cg_frg.gravity.external_tensor import exact_helicity_certificate
from cg_frg.qcd.generated_yang_mills import generated_yang_mills_gap


def critical_response() -> Fraction:
    return Fraction(4, 27)


def response_factorization(y: Fraction) -> Fraction:
    return (y - Fraction(1, 3)) ** 2 * (Fraction(4, 3) - y)


def _poly_mul(a: tuple[Fraction, ...], b: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    out = [Fraction(0, 1)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return tuple(out)


def _poly_sub(a: tuple[Fraction, ...], b: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    n = max(len(a), len(b))
    out = [Fraction(0, 1)] * n
    for i in range(n):
        out[i] = (a[i] if i < len(a) else Fraction(0, 1)) - \
                 (b[i] if i < len(b) else Fraction(0, 1))
    return tuple(out)


def response_polynomial_coefficients() -> tuple[tuple[Fraction, ...], tuple[Fraction, ...]]:
    """Exact coefficients of 4/27 - y(1-y)^2 and (y-1/3)^2(4/3-y)."""
    y = (Fraction(0, 1), Fraction(1, 1))
    one_minus_y = (Fraction(1, 1), Fraction(-1, 1))
    lhs = _poly_sub((Fraction(4, 27),),
                    _poly_mul(y, _poly_mul(one_minus_y, one_minus_y)))
    y_minus_third = (Fraction(-1, 3), Fraction(1, 1))
    four_thirds_minus_y = (Fraction(4, 3), Fraction(-1, 1))
    rhs = _poly_mul(_poly_mul(y_minus_third, y_minus_third), four_thirds_minus_y)
    return lhs, rhs


def response_maximum_check() -> bool:
    lhs, rhs = response_polynomial_coefficients()
    return lhs == rhs and lhs[0] == Fraction(4, 27)


def certificate() -> dict[str, Any]:
    tt = tt_certificate()
    response_level = response_level_certificate()
    c5 = tt["endpoint_coordinates"]["5"]
    k_l = float(get("kL"))
    gap = generated_yang_mills_gap(k_l, certify=True)
    gap_sq = gap["gap_squared"]
    gravity = exact_helicity_certificate(Fraction(1))
    checks = {
        "response_level_derivation_pass": response_level["status"] == "PASS",
        "4_over_27_factorization": response_maximum_check(),
        "tt_endpoint_equals_stored_kL": abs(c5 - k_l) < 1e-12,
        "tt_unique_integer_R5": tt["unique_integer_level"] == 5,
        "tt_endpoint_inside_platform": (
            tt["positions"]["sqrt(11/2)"] < c5 < tt["positions"]["sqrt(15/2)"]
        ),
        "ym_gap_positive": gap_sq > 0.0,
        "ym_gap_interval_positive": gap.get("interval_certificate", {}).get("strictly_positive", False),
        "r5_platform_bounds": (
            tt["checks"]["R_star_between_4_and_5"]
            and tt["checks"]["upper_shell_bound_below_6"]
        ),
        "gravity_two_helicities": gravity.get("physical_helicities") == [-2, 2],
        "gravity_zero_mass_term": str(gravity.get("mass_term", "")).startswith("zero"),
        "gravity_visible_rank_two": gravity.get("visible_rank") == 2,
    }
    return {
        "schema_version": 1,
        "step": "capacity_endpoint_ym",
        "critical_response": str(critical_response()),
        "response_level": response_level,
        "tt_endpoint": {
            "kL": c5,
            "R_star": tt["response_edge_R_star"],
            "R5": 5,
            "upper_shell_bound": tt["response_domain"]["upper_shell_bound"],
        },
        "ym_gap": {
            "L": k_l,
            "gap_squared": gap_sq,
            "gap": gap["gap"],
        },
        "gravity": {
            "physical_helicities": gravity.get("physical_helicities"),
            "mass_term": gravity.get("mass_term"),
            "visible_rank": gravity.get("visible_rank"),
            "scope": gravity.get("scope"),
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
