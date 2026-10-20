# -*- coding: utf-8 -*-
"""Derive the one-generation content from the source charge lattice.

This replaces the hand-written content table by the same finite construction
used in the Lean physical branch:

* the source carrier is ``(coloured 3 + scalar 1) x (left 2 + upper 1 + lower 1)``;
* the relative character is the unique primitive trace-free integer pair
  ``3*a + b = 0`` with ``a > 0``, hence ``(a,b) = (1,-3)``;
* the right spin character is ``(left,upper,lower) = (0,1,-1)``;
* the charge is ``r*right + beta*relative``.  The vacuum upper line is neutral,
  ``r - 3*beta = 0``; primitivity and ``beta > 0`` give ``(r,beta)=(3,1)``;
* hypercharge is charge/6.

The resulting six sectors have multiplicities 6,3,3,2,1,1.  Excluding the
neutral scalar-upper line leaves the 15 charged Weyl coordinates and the
familiar ``N_L=8, N_R=7, sum Y^2=10/3, tau=1/50``.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd
from typing import Any


Sector = tuple[str, str]  # (colour, spin)
COLOUR_DIM = {"coloured": 3, "scalar": 1}
SPIN_DIM = {"left": 2, "upper": 1, "lower": 1}
RIGHT_WEIGHT = {"left": 0, "upper": 1, "lower": -1}
SECTOR_NAMES = {
    ("coloured", "left"): "Q_L",
    ("coloured", "upper"): "u_R",
    ("coloured", "lower"): "d_R",
    ("scalar", "left"): "L_L",
    ("scalar", "upper"): "nu_R",
    ("scalar", "lower"): "e_R",
}


def primitive_relative() -> tuple[int, int]:
    """Unique primitive trace-free relative character with positive colour."""
    for a in range(1, 101):
        for b in range(-300, 301):
            if 3 * a + b == 0 and gcd(a, abs(b)) == 1:
                return a, b
    raise RuntimeError("primitive trace-free relative character not found")


def primitive_charge() -> tuple[int, int]:
    """Unique primitive charge with neutral scalar-upper vacuum and beta>0."""
    for beta in range(1, 51):
        for r in range(0, 301):
            if r - 3 * beta == 0 and gcd(r, beta) == 1:
                return r, beta
    raise RuntimeError("primitive charge not found")


def charge_weight(r: int, beta: int, sector: Sector) -> int:
    colour, spin = sector
    a, b = primitive_relative()
    relative = a if colour == "coloured" else b
    return r * RIGHT_WEIGHT[spin] + beta * relative


def sectors() -> list[dict[str, Any]]:
    r, beta = primitive_charge()
    out = []
    for colour in ("coloured", "scalar"):
        for spin in ("left", "upper", "lower"):
            sector = (colour, spin)
            charge = charge_weight(r, beta, sector)
            out.append({
                "name": SECTOR_NAMES[sector],
                "colour": colour,
                "spin": spin,
                "multiplicity": COLOUR_DIM[colour] * SPIN_DIM[spin],
                "charge": charge,
                "hypercharge": Fraction(charge, 6),
                "neutral": charge == 0,
            })
    return out


def charged_generation() -> tuple[tuple[str, tuple[int, int], Fraction, int, int], ...]:
    """The five charged multiplets, in the order used by V5."""
    out = []
    for item in sectors():
        if item["neutral"]:
            continue
        colour_dim = 3 if item["colour"] == "coloured" else 1
        weak_dim = 2 if item["spin"] == "left" else 1
        sign = +1 if item["spin"] == "left" else -1
        out.append((item["name"], (colour_dim, weak_dim), item["hypercharge"],
                    item["multiplicity"], sign))
    return tuple(out)


def all_content() -> tuple[tuple[str, tuple[int, int], Fraction, int, int], ...]:
    """All six sectors, including the neutral right line."""
    out = []
    for item in sectors():
        colour_dim = 3 if item["colour"] == "coloured" else 1
        weak_dim = 2 if item["spin"] == "left" else 1
        sign = +1 if item["spin"] == "left" else -1
        out.append((item["name"], (colour_dim, weak_dim), item["hypercharge"],
                    item["multiplicity"], sign))
    return tuple(out)


def certificate() -> dict[str, Any]:
    relative = primitive_relative()
    charge = primitive_charge()
    content = sectors()
    charged = [item for item in content if not item["neutral"]]
    n_left = sum(item["multiplicity"] for item in charged if item["spin"] == "left")
    n_right = sum(item["multiplicity"] for item in charged
                  if item["spin"] in ("upper", "lower"))
    n_f = sum(item["multiplicity"] for item in charged)
    sum_y2 = sum(item["multiplicity"] * item["hypercharge"] ** 2 for item in content)
    tau = Fraction(n_left - n_right, n_f * sum_y2)
    checks = {
        "relative_trace_free": 3 * relative[0] + relative[1] == 0,
        "relative_primitive": gcd(relative[0], abs(relative[1])) == 1,
        "relative_positive": relative[0] > 0,
        "charge_neutral_upper": charge[0] - 3 * charge[1] == 0,
        "charge_primitive": gcd(charge[0], charge[1]) == 1,
        "charge_beta_positive": charge[1] > 0,
        "N_L_8": n_left == 8,
        "N_R_7": n_right == 7,
        "N_f_15": n_f == 15,
        "sum_Y2_10_over_3": sum_y2 == Fraction(10, 3),
        "tau_1_over_50": tau == Fraction(1, 50),
        "total_carrier_16": sum(item["multiplicity"] for item in content) == 16,
        "one_neutral_line": sum(1 for item in content if item["neutral"]) == 1,
    }
    return {
        "schema_version": 1,
        "step": "content_derivation",
        "relative_character": relative,
        "primitive_charge": charge,
        "sectors": [
            {**item, "hypercharge": str(item["hypercharge"])}
            for item in content
        ],
        "N_L": n_left,
        "N_R": n_right,
        "N_f": n_f,
        "sum_Y_squared": str(sum_y2),
        "tau": str(tau),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
