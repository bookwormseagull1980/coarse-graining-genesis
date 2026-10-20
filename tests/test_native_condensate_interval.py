# -*- coding: utf-8 -*-
"""Native relative-potential interval contract."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402


def test_native_potential_interval_contains_production():
    record = get("native_relative_potential_interval")
    assert record["value"]["lo"] <= record["production_value"] <= record["value"]["hi"]
