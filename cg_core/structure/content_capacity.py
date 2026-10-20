# -*- coding: utf-8 -*-
"""Exact content-capacity certificate.

The content is no longer a hand-written table.  `content_derivation` constructs
the six source sectors from the primitive trace-free relative character and
the primitive charge with neutral scalar-upper vacuum, then computes the
hypercharge eigenvalues.  This module evaluates the exact capacity and anomaly
consequences:

    N_L = 8, N_R = 7, N_f = 15, sum Y^2 = 10/3,
    tau = (N_L - N_R) / (N_f * sum Y^2) = 1/50.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from cg_core.content_derivation import all_content, certificate as derivation_certificate


Representation = tuple[str, int, int, Fraction, int, int]
# name, colour dimension, weak dimension, hypercharge Y, component count,
# chirality (+1 left doublet, -1 right singlet)
CONTENT: tuple[Representation, ...] = tuple(
    (name, colour, weak, Y, count, sign)
    for name, (colour, weak), Y, count, sign in all_content()
)


def n_left() -> int:
    return sum(count for _, _, weak, _, count, sign in CONTENT if sign == 1 and weak == 2)


def n_right_charged() -> int:
    return sum(count for name, _, weak, Y, count, sign in CONTENT
               if sign == -1 and weak == 1 and name != "nu_R" and Y != 0)


def n_weyl_charged() -> int:
    return sum(count for name, _, _, Y, count, _ in CONTENT if name != "nu_R" and Y != 0)


def sum_y_squared() -> Fraction:
    return sum((count * Y * Y for _, _, _, Y, count, _ in CONTENT), Fraction(0, 1))


def torsion_tau() -> Fraction:
    return Fraction(n_left() - n_right_charged(), n_weyl_charged() * sum_y_squared())


def anomaly_su3_squared_u1() -> Fraction:
    total = Fraction(0, 1)
    for _, colour, _, Y, count, sign in CONTENT:
        t3 = Fraction(1, 2) if colour == 3 else Fraction(0, 1)
        total += sign * 2 * t3 * Y * count
    return total


def anomaly_su2_squared_u1() -> Fraction:
    return sum((sign * Y * count for _, _, weak, Y, count, sign in CONTENT
                if weak == 2), Fraction(0, 1))


def anomaly_u1_cubed() -> Fraction:
    return sum((sign * count * Y * Y * Y for _, _, _, Y, count, sign in CONTENT),
               Fraction(0, 1))


def anomaly_gravitational_u1() -> Fraction:
    return sum((sign * count * Y for _, _, _, Y, count, sign in CONTENT),
               Fraction(0, 1))


def certificate() -> dict[str, Any]:
    derivation = derivation_certificate()
    checks = {
        "content_derivation_pass": derivation["status"] == "PASS",
        "N_L_8": n_left() == 8,
        "N_R_7": n_right_charged() == 7,
        "N_f_15": n_weyl_charged() == 15,
        "sum_Y2_10_over_3": sum_y_squared() == Fraction(10, 3),
        "tau_1_over_50": torsion_tau() == Fraction(1, 50),
        "SU3_squared_U1_zero": anomaly_su3_squared_u1() == 0,
        "SU2_squared_U1_zero": anomaly_su2_squared_u1() == 0,
        "U1_cubed_zero": anomaly_u1_cubed() == 0,
        "gravitational_U1_zero": anomaly_gravitational_u1() == 0,
    }
    return {
        "schema_version": 1,
        "step": "content_capacity",
        "derivation": {
            "relative_character": derivation["relative_character"],
            "primitive_charge": derivation["primitive_charge"],
            "sectors": derivation["sectors"],
        },
        "content": [
            {"name": name, "colour": colour, "weak": weak, "Y": str(Y),
             "count": count, "chirality": sign}
            for name, colour, weak, Y, count, sign in CONTENT
        ],
        "N_L": n_left(),
        "N_R": n_right_charged(),
        "N_f": n_weyl_charged(),
        "sum_Y_squared": str(sum_y_squared()),
        "tau": str(torsion_tau()),
        "anomalies": {
            "SU3_squared_U1": str(anomaly_su3_squared_u1()),
            "SU2_squared_U1": str(anomaly_su2_squared_u1()),
            "U1_cubed": str(anomaly_u1_cubed()),
            "gravitational_U1": str(anomaly_gravitational_u1()),
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
