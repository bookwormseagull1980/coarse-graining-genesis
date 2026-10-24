# -*- coding: utf-8 -*-
"""Propagate the certified endpoint interval to key mass scales.

This module does not replace the production centres.  It publishes the
outward intervals induced by the cached strict endpoint certificate and the
fixed external Planck anchor, so the precision of the displayed centres can
be audited independently of their decimal formatting.
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get, set as pset  # noqa: E402
from cg_core.quantities import QuantityDefinition  # noqa: E402
from cg_core.rational_interval import Interval, exp_negative, pi_interval  # noqa: E402

_CERT = _ROOT / "certificates" / "endpoint_interval.json"


def _endpoint_bracket() -> tuple[float, float]:
    data = json.loads(_CERT.read_text(encoding="utf-8"))
    if data.get("status") != "PASS":
        raise RuntimeError("cached endpoint certificate is not PASS")
    return tuple(float(Fraction(value)) for value in data["bracket"])


def _definition(obj: str, unit: str, operator: str, normalization: str,
                error: str, assumptions: tuple[str, ...]) -> QuantityDefinition:
    return QuantityDefinition(
        object=obj, unit=unit, carrier="endpoint-to-mass scale transfer",
        operator=operator, source="cached strict endpoint certificate",
        projection="named production readout", normalization=normalization,
        scheme="outward interval propagation", order="one endpoint interval",
        assumptions=assumptions, error_kind=error,
    )


def compute() -> dict:
    kL = float(get("kL"))
    M_P = float(get("M_P"))
    tau = float(get("tau"))
    lo, hi = _endpoint_bracket()
    if not lo <= kL <= hi:
        raise RuntimeError("stored kL lies outside the cached endpoint bracket")

    # Include binary conversion of the rational bracket, then evaluate all
    # elementary factors with the same outward rational kernel.
    c = Interval.bounds(math.nextafter(lo, -math.inf), math.nextafter(hi, math.inf))
    pi = pi_interval()
    anchor, t = Interval.point(M_P), Interval.point(tau)
    s = 2*t
    squash = 1-s*((1+s)/((1-2*s)**2*(1-2*s).sqrt())).sqrt()
    if squash.lo <= 0:
        raise ValueError("positive squash branch required")
    def floats(interval):
        lower, upper = interval.decimal_bounds(40)
        return math.nextafter(float(lower), -math.inf), math.nextafter(float(upper), math.inf)
    M_G_lo, M_G_hi = floats(anchor*pi.sqrt()/c)
    m_e_lo, m_e_hi = floats(anchor*squash*exp_negative(20*c)*1000)
    v_lo, v_hi = floats(anchor*3*squash*exp_negative(4*pi*c)/(16*pi**2*pi.sqrt()*c))

    def rel(lo_value: float, hi_value: float) -> float:
        centre = 0.5 * (lo_value + hi_value)
        return (hi_value - lo_value) / centre

    kL_width = hi - lo
    pset(
        "kL_interval", {
            "lo": lo, "hi": hi, "width": kL_width,
            "relative_width": kL_width / kL,
        },
        provenance="DERIVED", role="internal",
        dependencies=("kL",),
        definition=_definition(
            "strict endpoint interval", "1", "root enclosure",
            "cached outward rational interval",
            "outward coefficient enclosure; analytic scale-law uniqueness",
            ("endpoint certificate is full finite spectral sum",),
        ),
        note="Strict kL bracket from certificates/endpoint_interval.json.",
    )
    pset(
        "M_G_interval", {
            "lo": M_G_lo, "hi": M_G_hi,
            "relative_width": rel(M_G_lo, M_G_hi),
        },
        provenance="DERIVED", role="internal",
        dependencies=("kL", "M_P"),
        definition=_definition(
            "emergence-scale interval", "GeV", "M_P*sqrt(pi)/kL",
            "M_P*sqrt(pi)/kL", "endpoint interval; Planck anchor fixed",
            ("Planck anchor held at its published central value",),
        ),
        note="M_G interval induced by the strict kL bracket; no anchor uncertainty added.",
    )
    pset(
        "m_e_interval", {
            "lo": m_e_lo, "hi": m_e_hi,
            "relative_width": rel(m_e_lo, m_e_hi),
        },
        provenance="DERIVED", role="internal",
        dependencies=("kL", "M_P", "tau"),
        definition=_definition(
            "electron mass interval", "MeV", "M_P exp(-20 kL)(1-s0 kappa)*1000",
            "Planck-anchored exponential cascade", "endpoint interval; Planck anchor fixed",
            ("exponent 20=(d+1)(SumY2 Delta_f)", "positive squash branch"),
        ),
        note="Endpoint-induced electron-mass interval; model and anchor errors are separate.",
    )
    pset(
        "v_HIGGS_interval", {
            "lo": v_lo, "hi": v_hi,
            "relative_width": rel(v_lo, v_hi),
        },
        provenance="DERIVED", role="internal",
        dependencies=("kL", "M_P", "tau"),
        definition=_definition(
            "electroweak VEV interval", "GeV", "M_G * epsilon(kL)",
            "M_G*epsilon(kL)", "endpoint interval; Planck anchor fixed",
            ("M_G and epsilon use the same endpoint branch",),
        ),
        note="Endpoint-induced VEV interval; model and anchor errors are separate.",
    )
    return {
        "kL": [lo, hi],
        "M_G": [M_G_lo, M_G_hi],
        "m_e": [m_e_lo, m_e_hi],
        "v_HIGGS": [v_lo, v_hi],
    }


if __name__ == "__main__":
    print(compute())
