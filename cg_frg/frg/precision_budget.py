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
from cg_frg.ewsb.epsilon_ratio import epsilon_window  # noqa: E402
from cg_frg.fermion.electron_mass import m_e_planck  # noqa: E402

_CERT = _ROOT / "certificates" / "endpoint_interval.json"


def _endpoint_bracket() -> tuple[float, float]:
    data = json.loads(_CERT.read_text(encoding="utf-8"))
    if data.get("status") != "PASS":
        raise RuntimeError("cached endpoint certificate is not PASS")
    lo, hi = (frac.split("/") for frac in data["bracket"])
    return float(Fraction(int(lo[0]), int(lo[1]))), float(Fraction(int(hi[0]), int(hi[1])))


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

    # M_G = M_P sqrt(pi) / kL is decreasing in kL.
    M_G_lo = M_P * math.sqrt(math.pi) / hi
    M_G_hi = M_P * math.sqrt(math.pi) / lo

    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    squash = 1.0 - s0 * kappa
    m_e_lo = m_e_planck(M_P, hi) * squash
    m_e_hi = m_e_planck(M_P, lo) * squash

    # v = M_G * epsilon(kL), both factors decrease with kL.
    v_lo = (M_P * math.sqrt(math.pi) / hi) * epsilon_window(hi)
    v_hi = (M_P * math.sqrt(math.pi) / lo) * epsilon_window(lo)

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
            "strict interval root enclosure; derivative-sign uniqueness",
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
