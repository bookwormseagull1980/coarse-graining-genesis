# -*- coding: utf-8 -*-
"""Endpoint-interval propagation contracts for the published V5 store."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402


def _interval(key: str) -> tuple[float, float]:
    record = get(key)
    return float(record["lo"]), float(record["hi"])


def test_endpoint_interval_is_narrow_and_contains_centre():
    lo, hi = _interval("kL_interval")
    centre = float(get("kL"))
    assert lo < centre < hi
    assert hi - lo < 5e-5


def test_mass_intervals_contain_production_centres():
    checks = (
        ("M_G_interval", "M_G"),
        ("m_e_interval", "m_e_pred"),
        ("v_HIGGS_interval", "v_HIGGS"),
    )
    for interval_key, centre_key in checks:
        lo, hi = _interval(interval_key)
        centre = float(get(centre_key))
        assert lo < centre < hi, (interval_key, centre_key, lo, centre, hi)
