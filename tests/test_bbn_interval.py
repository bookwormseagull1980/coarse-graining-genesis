# -*- coding: utf-8 -*-
"""Metadata completion and BBN phase-space interval contracts."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402


def test_every_parameter_has_error_kind():
    import json
    parameters = json.loads((_ROOT / "cg_params.json").read_text(encoding="utf-8"))["parameters"]
    missing = [key for key, record in parameters.items()
               if not (record.get("quantity_definition") or {}).get("error_kind")]
    assert not missing, missing


def test_bbn_beta_interval_contains_production_centre():
    record = get("bbn_beta_phase_space_interval")
    assert record["lo"] <= record["production_centre"] <= record["hi"]
    assert record["hi"] > record["lo"]
