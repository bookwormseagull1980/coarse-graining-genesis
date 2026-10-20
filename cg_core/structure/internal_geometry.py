# -*- coding: utf-8 -*-
"""Internal-geometry spectral certificates.

The formulas are written independently of the legacy ``rp3_spectrum`` module,
then checked against it on a finite range.  The legacy module remains the
numerical oracle during the migration; the structural formulas are the new
derivation layer.

Spectra:
  scalar:  l(l+2)/L^2,  l even,  multiplicity (l+1)^2
  vector:  (l+1)^2/L^2,  l odd,  multiplicity 2l(l+2)
  spinor:  (n+3/2)^2/L^2, n even, multiplicity (n+1)(n+2)
  TT rough: k(k+2)-2 over L^2, k even >= 2, multiplicity 2(k-1)(k+3)
"""

from __future__ import annotations

import math
from typing import Any

from cg_core import rp3_spectrum as legacy
from cg_core.structure import rp3_derivation


def scalar_eigenvalue(l: int, L: float) -> float:
    return l * (l + 2) / (L * L)


def scalar_multiplicity(l: int) -> int:
    return (l + 1) * (l + 1)


def vector_eigenvalue(l: int, L: float) -> float:
    return (l + 1) * (l + 1) / (L * L)


def vector_multiplicity(l: int) -> int:
    return 2 * l * (l + 2)


def spinor_eigenvalue(n: int, L: float) -> float:
    return (n + 1.5) * (n + 1.5) / (L * L)


def spinor_multiplicity(n: int) -> int:
    return (n + 1) * (n + 2)


def tt_rough_eigenvalue(k: int, L: float) -> float:
    return (k * (k + 2) - 2) / (L * L)


def tt_multiplicity(k: int) -> int:
    return 2 * (k - 1) * (k + 3)


def _production_radius() -> float:
    try:
        from cg_core.params import get
        return float(get("kL"))
    except (KeyError, OSError, ValueError):
        return 2.4935343325


def certificate(L: float | None = None) -> dict[str, Any]:
    if L is None:
        L = _production_radius()
    scalar_checks = []
    for l in range(0, 21, 2):
        scalar_checks.append(
            abs(scalar_eigenvalue(l, L) - legacy.scalar_eigenvalue(l, L)) < 1e-15
            and scalar_multiplicity(l) == legacy.scalar_multiplicity(l)
        )
    vector_checks = []
    for l in range(1, 20, 2):
        vector_checks.append(
            abs(vector_eigenvalue(l, L) - legacy.vector_eigenvalue(l, L)) < 1e-15
            and vector_multiplicity(l) == legacy.vector_multiplicity(l)
        )
    spinor_checks = []
    for n in range(0, 21, 2):
        spinor_checks.append(
            abs(spinor_eigenvalue(n, L) - legacy.spinor_eigenvalue(n, L)) < 1e-12
            and spinor_multiplicity(n) == legacy.spinor_multiplicity(n)
        )
    tt_checks = []
    for k in range(2, 21, 2):
        modes = [
            mode for mode in legacy.true_tt_modes(L, k, operator="rough")
            if max(mode[0], mode[1]) == (k + 2) // 2
        ]
        total_mult = sum(m[3] for m in modes)
        tt_checks.append(
            len(modes) == 2
            and all(abs(m[2] - tt_rough_eigenvalue(k, L)) < 1e-12 for m in modes)
            and total_mult == tt_multiplicity(k)
        )
    rp3 = rp3_derivation.certificate(L)
    checks = {
        "rp3_derivation_pass": rp3["status"] == "PASS",
        "scalar_formula_matches_legacy": all(scalar_checks),
        "vector_formula_matches_legacy": all(vector_checks),
        "spinor_formula_matches_legacy": all(spinor_checks),
        "tt_rough_formula_matches_legacy": all(tt_checks),
        "scalar_lowest_zero": scalar_eigenvalue(0, L) == 0.0,
        "vector_lowest_positive": vector_eigenvalue(1, L) > 0.0,
        "spinor_lowest_positive": spinor_eigenvalue(0, L) > 0.0,
        "tt_lowest_six": abs(tt_rough_eigenvalue(2, L) - 6.0 / (L * L)) < 1e-15,
    }
    return {
        "schema_version": 1,
        "step": "internal_geometry_spectra",
        "rp3_derivation": rp3,
        "L": L,
        "spectra": {
            "scalar": {"l_range": [0, 20, 2], "multiplicity": "(l+1)^2"},
            "vector": {"l_range": [1, 19, 2], "multiplicity": "2l(l+2)"},
            "spinor": {"n_range": [0, 20, 2], "multiplicity": "(n+1)(n+2)"},
            "tt_rough": {"k_range": [2, 20, 2], "multiplicity": "2(k-1)(k+3)"},
        },
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
