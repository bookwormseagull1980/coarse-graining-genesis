# -*- coding: utf-8 -*-
"""Complete error-kind metadata for diagnostic and structural records.

The scientific writers attach full :class:`QuantityDefinition` objects to
physical predictions.  Status bundles, exact structural parameters and
comparison projections are often emitted as structured diagnostics without a
scalar uncertainty.  This final pass gives every remaining record an explicit
category; it never changes a value, provenance or writer.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import annotate_error_kind, read_store_document  # noqa: E402

_EXACT = {
    "L_Cg_star", "L_Gg", "L_critical", "R_c_star", "electron_cascade_content",
    "longroot_K", "order_parameter_xi", "order_parameter_s0",
    "order_parameter_n_broken", "twoL_entropy_min_distance",
}


def _classification(key: str, record: dict) -> str:
    value = record.get("value")
    role = record.get("role")
    if key in _EXACT:
        return "exact algebraic/structural value; no continuum error"
    if role == "informational" or isinstance(value, (dict, list, str, bool)):
        return "diagnostic/status bundle; not a scalar prediction"
    if role == "comparison":
        return "comparison projection; input and record errors retained"
    if isinstance(value, (int, float)):
        return "computed centre; numerical and model errors assessed separately"
    return "metadata record; no scalar uncertainty assigned"


def compute() -> dict:
    parameters = read_store_document("parameters")["parameters"]
    changed = []
    required = {"object", "unit", "carrier", "operator", "source",
                "projection", "normalization", "scheme", "order",
                "error_kind"}
    for key, record in sorted(parameters.items()):
        definition = record.get("quantity_definition") or {}
        if required.issubset(definition):
            continue
        kind = definition.get("error_kind") or _classification(key, record)
        annotate_error_kind(key, kind,
                            note="release-wide error-kind completion")
        changed.append(key)
    return {"completed": len(changed), "keys": changed}


if __name__ == "__main__":
    result = compute()
    print(f"error-kind metadata completed: {result['completed']} records")
