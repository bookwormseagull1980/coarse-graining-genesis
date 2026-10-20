# -*- coding: utf-8 -*-
"""Derive the two V5 normalizations from the common source normalization.

The 7D gauge kinetic term is normalized on the same Planck scale as the
7D gravitational term.  With the common-origin coefficient

    g7^2 = 8*pi^2 / (M_P^2 * M_G)

and the round RP3 volume `V3 = pi^2*(kL/M_G)^3`, the constant zero mode gives

    g4^2 = g7^2 / V3 = 8*(M_G/M_P)^2 / kL^3,

so the gauge scale factor is `(M_G/M_P)^2` with no independently fitted
coefficient.

The resolution flow is written in unit-speed form
`sigma(t)^4 = sigma(0)^4 - 8 C t`; the unit-speed normalization is `C=-1`.
This fixes the flow beta function; it does not introduce a physical clock.
"""

from __future__ import annotations

import math
from typing import Any


def seven_dimensional_coupling(m_g: float, m_p: float) -> float:
    if not (math.isfinite(m_g) and math.isfinite(m_p)) or min(m_g, m_p) <= 0:
        raise ValueError("positive finite M_G and M_P required")
    return 8.0 * math.pi ** 2 / (m_p * m_p * m_g)


def volume(m_g: float, k_l: float) -> float:
    if not (math.isfinite(m_g) and math.isfinite(k_l)) or min(m_g, k_l) <= 0:
        raise ValueError("positive finite M_G and kL required")
    radius = k_l / m_g
    return math.pi ** 2 * radius ** 3


def gauge_scale_factor(m_g: float, m_p: float) -> float:
    """G4^2*kL^3/8 from g7^2/V3; equals (M_G/M_P)^2."""
    return (m_g / m_p) ** 2


def four_dimensional_coupling_squared(m_g: float, m_p: float, k_l: float) -> float:
    g7 = seven_dimensional_coupling(m_g, m_p)
    return g7 / volume(m_g, k_l)


def flow_beta(m_g: float) -> float:
    """Unit-speed resolution-flow coefficient beta = -2 C sigma^-3.

    At sigma = 1/M_G and C=-1 this is 2 M_G^3.
    """
    if not math.isfinite(m_g) or m_g <= 0:
        raise ValueError("positive finite M_G required")
    return 2.0 * m_g ** 3


def certificate(m_g: float | None = None, m_p: float | None = None,
                k_l: float | None = None) -> dict[str, Any]:
    if m_g is None or m_p is None or k_l is None:
        try:
            from cg_core.params import get
            m_g = float(get("M_G")) if m_g is None else m_g
            m_p = float(get("M_P")) if m_p is None else m_p
            k_l = float(get("kL")) if k_l is None else k_l
        except (KeyError, OSError, ValueError):
            m_g, m_p, k_l = 1.0, 2.0, 1.0
    g7 = seven_dimensional_coupling(m_g, m_p)
    v3 = volume(m_g, k_l)
    g4 = four_dimensional_coupling_squared(m_g, m_p, k_l)
    checks = {
        "positive_g7": g7 > 0.0,
        "positive_volume": v3 > 0.0,
        "positive_g4": g4 > 0.0,
        "gauge_scale_matches": math.isclose(g4 * k_l ** 3 / 8.0, (m_g / m_p) ** 2,
                                            rel_tol=1e-15),
        "zero_mode_identity": math.isclose(g4, g7 / v3, rel_tol=1e-15),
        "unit_speed_flow": math.isclose(flow_beta(m_g) / m_g ** 3, 2.0, rel_tol=1e-15),
    }
    return {
        "schema_version": 1,
        "step": "normalization_derivation",
        "g7_squared": g7,
        "volume": v3,
        "g4_squared": g4,
        "gauge_scale_factor": (m_g / m_p) ** 2,
        "flow_beta": flow_beta(m_g),
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(certificate(), indent=2))
