# -*- coding: utf-8 -*-
"""BBN weak-rate interval contracts."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402


def test_weak_rate_intervals_contain_production_channels():
    record = get("bbn_weak_rate_intervals")
    for name, centre in record["production_channels"].items():
        interval = record["rates"][name]
        assert interval["lo"] <= centre <= interval["hi"], (name, interval, centre)
