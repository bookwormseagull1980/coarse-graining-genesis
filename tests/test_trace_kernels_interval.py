# -*- coding: utf-8 -*-
"""Trace-kernel interval contract."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402


def test_trace_kernel_intervals_contain_production():
    record = get("trace_kernel_intervals")
    assert record["boson"]["lo"] <= record["production_boson"] <= record["boson"]["hi"]
    assert record["fermion"]["lo"] <= record["production_fermion"] <= record["fermion"]["hi"]
