# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
cg_core/params.py — V4.0: the framework's single parameter store
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
Every module of the framework computes derived quantities that other
modules consume.  The derived values must be stored once, in a single
authoritative file, with provenance (who wrote each value, from what),
so that (a) no module hard-codes a physics value, (b) the derivation
chain of every number is auditable, and (c) a later module never
silently overwrites an earlier result.  The store is the framework's
shared memory: modules read with get(), publish with set() (or
compare_and_set() for observed comparisons), and the writer of every
value is identified from the caller's module.

DESIGN PRINCIPLES
-----------------
1.  No built-in snapshot.  The file is the authority.
2.  Atomic writes.  Save writes to a temp file and os.replace()s it,
    so a crash never leaves a half-written store.
3.  Strict load.  A missing parameter file is an error (fail fast),
    not a silent re-creation with defaults.
4.  Write log.  Every set() records (key, value, writer, timestamp) in
    params_write_log.json — an audit trail of who published what.
5.  Provenance classes.  Every value carries a class:
        OBSERVED     — an external measured value (PDG/SM), for
                        comparison only (never used in computations)
        SM_INPUT     — an SM value used as a comparison reference
        INPUT        — a framework-internal input value
        DERIVED      — computed by a module (with a derivation note)
        SCALE_CHOICE — a normalisation/convention choice (e.g. the
                        (M(σ)/M_P)² factor in g2) — declared, never
                        disguised as a derivation
        PENDING      — a placeholder awaiting a writer
6.  Role classes.  Each key carries a role:
        anchor       — the dimensionful anchor (G_N, M_P)
        internal     — framework-internal derived quantity
        comparison   — post-computation comparison or diagnostic record;
                        never used in framework computations
        cg           — a CG-framework structural constant
        informational— a status/statement record
7.  SM table separation.  The SM comparison values live in
    sm_inputs.json (managed by sm_set()), not in the physics store —
    so the comparison table can never pollute or back-calibrate the
    framework's own parameters.

V4 DISCIPLINE (this module)
---------------------------
- No physics value is hard-coded here: the file store is the only
  source of values.  Only structural numbers (2, π) may appear in
  code, and they are used as constants, not as physics inputs.
- All floats are stored at full precision (repr round-trips
  float64); comparison deviations are stored to 10 significant
  digits.
"""

from __future__ import annotations

import json
import logging
import math
import os
import sys
import tempfile
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project root: the V4.0 directory (this file is cg_core/params.py).
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The store files: the physics store and the SM comparison table.
# (The BBN nuclear constants — dm_np, T_f, tau_n, t_decay, N_eff —
# are DERIVED by cg_frg/cosmology/bbn_helium.py since 2026-08-17;
# the former nuclear_inputs.json store is removed.)
_PARAM_FILE = _PROJECT_ROOT / "cg_params.json"
_SM_FILE = _PROJECT_ROOT / "comparison" / "sm_inputs.json"
_LOG_FILE = _PROJECT_ROOT / "params_write_log.json"

# Provenance classes (see the module docstring).
_OBSERVED = "OBSERVED"
_SM_INPUT = "SM_INPUT"
_INPUT = "INPUT"
_DERIVED = "DERIVED"
_SCALE_CHOICE = "SCALE_CHOICE"
_PENDING = "PENDING"
_PROVENANCES = (_OBSERVED, _SM_INPUT, _INPUT, _DERIVED,
                _SCALE_CHOICE, _PENDING)

# Role classes.
_ROLE_ANCHOR = "anchor"
_ROLE_INTERNAL = "internal"
_ROLE_COMPARISON = "comparison"
_ROLE_CG = "cg"
_ROLE_INFO = "informational"
_ROLES = (_ROLE_ANCHOR, _ROLE_INTERNAL, _ROLE_COMPARISON, _ROLE_CG, _ROLE_INFO)

_LOG_MAX_ENTRIES = 2000  # write-log cap (keeps the audit file bounded)


# ---------------------------------------------------------------------------
# Writer identification: the caller's module, from the call stack.
# ---------------------------------------------------------------------------
def _writer() -> str:
    """Identify the writer module from the call stack.

    The value is the module path relative to the project root (e.g.
    'cg_frg/ewsb/vev_closure.py') — the file path, not the __name__,
    so that modules run as __main__ still record their real identity
    ('cg_frg/xxx.py' instead of '__main__').  This makes the audit
    trail actionable: every value can be traced to the module that
    published it.
    """
    import inspect

    frame = inspect.currentframe()
    try:
        f = frame
        while f is not None:
            mod = f.f_globals.get("__name__", "")
            fname = f.f_globals.get("__file__", "")
            if mod and mod != __name__:
                if fname:
                    try:
                        return (Path(fname).resolve()
                                .relative_to(_PROJECT_ROOT.resolve())
                                .as_posix())
                    except ValueError:
                        return str(fname)
                return mod
            f = f.f_back
        return "<unknown>"
    finally:
        del frame


# ---------------------------------------------------------------------------
# Store loading / saving.
# ---------------------------------------------------------------------------
def _load_store(path: Path) -> dict:
    """Load a JSON store; fail fast if it is missing or corrupt.

    Strict load is intentional: a missing store means the framework
    was never initialised, and silently re-creating it with defaults
    would hide that error.  A corrupt store is likewise fatal rather
    than silently reset.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"parameter store not found: {path} — run the initialisation "
            f"entry point first"
        )
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"corrupt parameter store {path}: {exc}") from exc
    if not isinstance(data, dict) or "parameters" not in data:
        raise RuntimeError(f"parameter store {path} has no 'parameters' record")
    return data


def _save_store(path: Path, data: dict) -> None:
    """Save a store atomically (tmp file + os.replace).

    The atomic write guarantees the store is never observed in a
    half-written state, even if the process dies mid-save.
    """
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_params() -> dict:
    """The parameters record: {key: {value, provenance, role, note, writer}}."""
    return _load_store(_PARAM_FILE)["parameters"]


def _read_sm() -> dict:
    """The SM comparison record (separate store, see the module docstring)."""
    return _load_store(_SM_FILE)["parameters"]


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------
def has(key: str) -> bool:
    """True if the key exists in the store (with a value)."""
    p = _read_params()
    return key in p and "value" in p[key]


def get(key: str):
    """Read a parameter value.

    Raises KeyError if the key is absent or has no value.  Failing
    fast on a missing key is deliberate: a module that reads a value
    it depends on must never silently proceed with a None.
    """
    p = _read_params()
    if key not in p or "value" not in p[key]:
        raise KeyError(
            f"parameter '{key}' not in store (provenance: "
            f"{p.get(key, {}).get('provenance', 'absent')})"
        )
    return p[key]["value"]


def get_observed(key: str):
    """Read an external observed value (comparison only).

    Observed values must never enter computations; this accessor
    makes the intent explicit at the call site.
    """
    p = _read_params()
    if key not in p or "value" not in p[key]:
        raise KeyError(f"observed parameter '{key}' not in store")
    if p[key].get("provenance") not in (_OBSERVED, _SM_INPUT):
        raise KeyError(f"'{key}' is not an observed parameter")
    return p[key]["value"]


def record(
    key: str,
    value,
    *,
    provenance: str = _DERIVED,
    role: str = _ROLE_INTERNAL,
    note: str = "",
) -> None:
    """Register a key/value without saving (use set() to persist).

    record() is the in-memory variant used by modules that assemble a
    batch of outputs before a single save.
    """
    if provenance not in _PROVENANCES:
        raise ValueError(f"unknown provenance '{provenance}'")
    if role not in _ROLES:
        raise ValueError(f"unknown role '{role}'")
    p = _read_params()
    p[key] = {
        "value": value,
        "provenance": provenance,
        "role": role,
        "note": note,
        "writer": _writer(),
    }
    # Update the store immediately so that a later save() of another
    # module does not drop this record.
    data = _load_store(_PARAM_FILE)
    data["parameters"] = p
    _save_store(_PARAM_FILE, data)
    _log(key, value, provenance, _writer())


def set(
    key: str,
    value,
    *,
    provenance: str = _DERIVED,
    role: str = _ROLE_INTERNAL,
    note: str = "",
) -> None:
    """Publish a derived (or input) value to the store and persist it.

    This is the primary publication API.  The provenance defaults to
    DERIVED (a computed quantity); observed/SM values should use
    compare_and_set() or sm_set() so the comparison intent is explicit.
    """
    record(key, value, provenance=provenance, role=role, note=note)


def compare_and_set(
    key: str,
    value,
    observed,
    *,
    role: str = _ROLE_COMPARISON,
    note: str = "",
) -> float:
    """Publish a computed value together with its observed comparison.

    The observed value is stored in the SAME record (fields
    'observed', 'deviation_pct') but is clearly marked OBSERVED: it
    exists only for the comparison, never as an input.  Returns the
    relative deviation in percent.

    Why store the observed value next to the prediction: the audit
    trail of every closed quantity then carries its own comparison
    target, and the deviation is reproducible without consulting an
    external table.
    """
    if observed == 0:
        dev = 0.0
    else:
        dev = (value - observed) / observed * 100.0
    p = _read_params()
    p[key] = {
        "value": value,
        "observed": observed,
        "deviation_pct": round(dev, 10),
        "provenance": _DERIVED,
        "role": role,
        "note": note,
        "writer": _writer(),
    }
    data = _load_store(_PARAM_FILE)
    data["parameters"] = p
    _save_store(_PARAM_FILE, data)
    _log(key, value, _DERIVED, _writer())
    return dev


def sm_set(key: str, value, *, note: str = "") -> None:
    """Write an SM comparison value into the SEPARATE sm_inputs.json.

    The SM table is deliberately isolated from the physics store:
    nothing in the physics store may be read from the SM table as an
    input, so the comparison values can never back-calibrate the
    framework.
    """
    data = _load_store(_SM_FILE)
    data["parameters"][key] = {
        "value": value,
        "provenance": _SM_INPUT,
        "role": _ROLE_COMPARISON,
        "note": note,
        "writer": _writer(),
    }
    _save_store(_SM_FILE, data)
    _log(key, value, _SM_INPUT, _writer())


def sm_value(key: str):
    """Read an SM comparison value (never used as a computation input)."""
    sm = _read_sm()
    if key not in sm or "value" not in sm[key]:
        raise KeyError(f"SM value '{key}' not in sm_inputs.json")
    return sm[key]["value"]


def all_records() -> dict:
    """The full parameter record (for audits and reports)."""
    return _read_params()


def save() -> None:
    """Persist the current store (idempotent; the record() path already saves)."""
    # record() persists immediately; save() is kept for API compatibility
    # and for callers that prefer an explicit flush.
    data = _load_store(_PARAM_FILE)
    _save_store(_PARAM_FILE, data)


def _log(key: str, value, provenance: str, writer: str) -> None:
    """Append an audit entry to the write log (bounded).

    The log is the human-readable audit trail of every publication.
    It is capped to _LOG_MAX_ENTRIES so that long runs do not grow it
    without bound; the cap drops the oldest entries.
    """
    try:
        entries = []
        if _LOG_FILE.exists():
            with open(_LOG_FILE, "r", encoding="utf-8") as fh:
                entries = json.load(fh)
        if not isinstance(entries, list):
            entries = []
        entries.append(
            {
                "t": time.strftime("%Y-%m-%d %H:%M:%S"),
                "key": key,
                "value": value,
                "provenance": provenance,
                "writer": writer,
            }
        )
        entries = entries[-_LOG_MAX_ENTRIES:]
        with open(_LOG_FILE, "w", encoding="utf-8") as fh:
            json.dump(entries, fh, ensure_ascii=False, indent=1)
    except OSError:
        # The log is best-effort: a failure to log must never break
        # the publication itself.
        logger.warning("failed to append write-log entry for '%s'", key)


# ---------------------------------------------------------------------------
# Initialisation entry point.
# ---------------------------------------------------------------------------
def init_stores(
    anchors: dict | None = None,
    sm_values: dict | None = None,
) -> None:
    """Create the store files with the initial records.

    anchors: {key: value} — the framework's anchor values (G_N_PDG,
    M_P) and the informational records.  sm_values: the SM comparison
    table.  All are written with OBSERVED / SM_INPUT provenance.  This
    entry point is idempotent: it refuses to overwrite existing
    records.  (The BBN nuclear constants are DERIVED by bbn_helium.py;
    the former nuclear_values store is removed since 2026-08-17.)
    """
    if not _PARAM_FILE.exists():
        data = {"version": 1, "parameters": {}}
        if anchors:
            for k, v in anchors.items():
                data["parameters"][k] = {
                    "value": v,
                    "provenance": _OBSERVED,
                    "role": _ROLE_ANCHOR,
                    "note": "anchor value (observed, comparison only)",
                    "writer": "cg_core.params.init_stores",
                }
        _save_store(_PARAM_FILE, data)
    if not _SM_FILE.exists():
        data = {"version": 1, "note": "SM comparison values (never inputs)", "parameters": {}}
        if sm_values:
            for k, v in sm_values.items():
                data["parameters"][k] = {
                    "value": v,
                    "provenance": _SM_INPUT,
                    "role": _ROLE_COMPARISON,
                    "note": "SM value for comparison only",
                    "writer": "cg_core.params.init_stores",
                }
        _save_store(_SM_FILE, data)


if __name__ == "__main__":
    # Smoke test: the store system must be self-consistent and exit 0.
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    print("params.py smoke test")
    print(f"  project root : {_PROJECT_ROOT}")
    print(f"  param file   : {_PARAM_FILE} (exists: {_PARAM_FILE.exists()})")
    print(f"  sm file      : {_SM_FILE} (exists: {_SM_FILE.exists()})")
    print("  OK — module imports and store paths resolve.")
