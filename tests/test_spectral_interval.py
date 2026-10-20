# -*- coding: utf-8 -*-
"""Spectral-channel interval contracts."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402


def test_spectral_channel_intervals_contain_production():
    record = get("spectral_channel_intervals")
    for name, centre in record["production_channels"].items():
        interval = record["channels"][name]
        assert interval["lo"] <= centre <= interval["hi"], (name, interval, centre)
