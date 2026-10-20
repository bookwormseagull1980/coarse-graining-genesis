# -*- coding: utf-8 -*-
# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""
cg_core/params.py — V5.0: the framework's single parameter store
=================================================================

PURPOSE
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
4.  Publication provenance. Each stored record identifies its writer,
    calculation run, source fingerprint and declared dependencies.
5.  Provenance classes.  Every value carries a class:
        OBSERVED     — a measured value, admitted to predictions only
                        in the explicitly declared dimensional-anchor role
        SM_INPUT     — an isolated comparison reference or convention
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
7.  Reference-data separation. Observations, comparison covariances and
    propagation conventions are registered in comparison/reference_inputs.json
    through sm_set()/sm_value(). Generated values use get()/set()/record().
    The prediction guard enforces the separation of their computational roles.

IMPLEMENTATION (this module)
---------------------------
- No physics value is hard-coded here: the file store is the only
  source of values.  Only structural numbers (2, π) may appear in
  code, and they are used as constants, not as physics inputs.
- All floats are stored at full precision (repr round-trips
  float64); comparison deviations are stored to 10 significant
  digits.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import tempfile
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from cg_core.quantities import readout_definition
from cg_core.release import publication_metadata

# ---------------------------------------------------------------------------
# Project root containing the parameter store and source packages.
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The two stores: generated scientific records and isolated reference data.
# The BBN quantities dm_np, T_f, tau_n, t_decay and N_eff are computed
# by cg_frg/cosmology/bbn_helium.py from the declared hadronic inputs.
_STORE_ROOT = Path(os.environ.get("V5_OUTPUT_DIR", str(_PROJECT_ROOT))).resolve()
_PARAM_FILE = _STORE_ROOT / "cg_params.json"
_SM_FILE = _STORE_ROOT / "comparison" / "reference_inputs.json"
_READ_INPUTS: dict[str, str] = {}
_PREDICTION_ONLY = ContextVar("v5_prediction_inputs_only", default=False)
_ACTIVE_INPUTS = ContextVar("v5_active_inputs", default=None)


@contextmanager
def input_scope():
    """Collect the precise reads of one evaluation without another evaluation's reads."""
    reads = {}
    token = _ACTIVE_INPUTS.set(reads)
    try:
        yield reads
    finally:
        _ACTIVE_INPUTS.reset(token)


def resolve_value(value, records, trail=()):
    """Resolve explicit parameter projections for a read-only display or calculation."""
    if isinstance(value, dict):
        if "$ref" in value:
            if value.keys() - {"$ref", "path"}:
                raise ValueError("a parameter reference cannot also contain a value")
            key = value["$ref"]
            if key in trail:
                raise ValueError("cyclic parameter reference: " + " -> ".join((*trail, key)))
            rec = records[key]
            result = resolve_value(rec.get("reference", rec.get("value")), records, (*trail, key))
            for component in value.get("path", []):
                result = result[component]
            return result
        return {key: resolve_value(item, records, trail) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve_value(item, records, trail) for item in value]
    return value


def resolved_records(records):
    """Materialize projections in memory; the store retains a single source value."""
    return {key: {**rec, "value": resolve_value(rec.get("reference", rec.get("value")), records, (key,))}
            for key, rec in records.items()}


def _track_input(key, value):
    digest = value_fingerprint(value)
    _READ_INPUTS[key] = digest
    active = _ACTIVE_INPUTS.get()
    if active is not None:
        active[key] = digest


def _checked_value(value, records, trail):
    if isinstance(value, dict):
        if "$ref" in value:
            if value.keys() - {"$ref", "path"}:
                raise ValueError("a parameter reference cannot also contain a value")
            result = _checked_record(value["$ref"], records, trail)["value"]
            for component in value.get("path", []):
                result = result[component]
            return result
        return {name: _checked_value(item, records, trail)
                for name, item in value.items()}
    if isinstance(value, list):
        return [_checked_value(item, records, trail) for item in value]
    return value


def _checked_record(key, records, trail=()):
    if key in trail:
        raise ValueError("cyclic parameter reference")
    rec = records[key]
    if rec.get("provenance") == _PENDING:
        raise KeyError(f"parameter '{key}' is unavailable: {rec.get('note', '')}")
    if rec.get("provenance") in (_OBSERVED, _SM_INPUT) and rec.get("role") != _ROLE_ANCHOR:
        raise ValueError(f"comparison-only measurement cannot be a prediction input: {key}")
    if (_PREDICTION_ONLY.get() and rec.get("role") == _ROLE_COMPARISON
            and rec.get("comparison_kind") != "observed_target"):
        raise ValueError(f"downstream comparison diagnostic cannot be a prediction input: {key}")

    value = _checked_value(rec.get("reference", rec.get("value")), records, (*trail, key))
    if value is None:
        raise KeyError(f"parameter '{key}' has no available value")
    _track_input(key, value)
    return {**deepcopy(rec), "value": value}


class PredictionRecords(Mapping):
    """A snapshot whose every value read enforces the production input contract."""
    def __init__(self, records):
        self._records = deepcopy(records)

    def __getitem__(self, key):
        return _checked_record(key, self._records)

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)


def published_record(key, source_root=None):
    """Read completed comparison evidence from the declared reference store."""
    if _PREDICTION_ONLY.get():
        raise ValueError("published comparison access inside a prediction calculation")
    root = Path(source_root or os.environ.get("V5_REFERENCE_DIR", str(_PROJECT_ROOT)))
    records = _load_store(root / "cg_params.json")["parameters"]
    return deepcopy(resolve_value(records[key].get("reference", records[key].get("value")), records, (key,)))


def published_sm_value(key, source_root=None):
    """Read identified observations for comparison, including an empty-store rebuild."""
    if _PREDICTION_ONLY.get():
        raise ValueError("observational data access inside a prediction calculation")
    root = Path(source_root or os.environ.get("V5_REFERENCE_DIR", str(_PROJECT_ROOT)))
    return deepcopy(_load_store(root / "comparison" / "reference_inputs.json")["parameters"][key]["value"])


@contextmanager
def prediction_inputs_only():
    """Reject observed-reference access within a declared prediction calculation.

    The dimensional anchor remains available through get(). A computed
    value published beside an observed target remains a computed value;
    a downstream comparison diagnostic is not a prediction input.
    """
    token = _PREDICTION_ONLY.set(True)
    try:
        yield
    finally:
        _PREDICTION_ONLY.reset(token)


def store_root() -> Path:
    """Current run's data directory; source code remains in the project."""
    return _STORE_ROOT


def read_store_document(store="parameters", *, source_root=None) -> dict:
    """Read one canonical store for verification, reporting or reconstruction.

    Calculation modules use get()/PredictionRecords for checked physical
    values. This document interface retains the metadata needed by audits;
    it accepts a store identity and a run directory, never a sidecar file.
    """
    paths = {"parameters": Path("cg_params.json"),
             "references": Path("comparison") / "reference_inputs.json"}
    if store not in paths:
        raise ValueError("unknown store identity")
    if _PREDICTION_ONLY.get():
        raise ValueError("document access inside a prediction calculation; use checked values")
    root = Path(source_root) if source_root is not None else _STORE_ROOT
    return _load_store(root / paths[store])


def value_fingerprint(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _metadata(writer: str, *, comparison_kind: str | None = None,
              dependencies=None, definition=None,
              evidence_kind="computation under declared definitions") -> dict:
    source = (_PROJECT_ROOT / writer).resolve()
    result = {
        "run_id": os.environ.get("V5_RUN_ID", "direct-module-run"),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()
        if source.is_file() else None,
        "module_read_inputs": dict(sorted((_ACTIVE_INPUTS.get() if _ACTIVE_INPUTS.get() is not None else _READ_INPUTS).items())),
        "dependency_scope": "reads in this process before publication",
        "evidence_kind": evidence_kind,
        "quantity_definition": definition.as_record() if definition is not None else None,
    }
    if comparison_kind:
        result["comparison_kind"] = comparison_kind
    if dependencies is not None:
        records = _read_params()
        direct = {}
        for key in dependencies:
            if key not in _READ_INPUTS:
                raise ValueError(f"declared dependency was not read: {key}")
            fingerprint = value_fingerprint(resolve_value(records[key].get("reference", records[key].get("value")), records, (key,)))
            if fingerprint != _READ_INPUTS[key]:
                raise ValueError(f"declared input changed before publication: {key}")
            direct[key] = fingerprint
        result["direct_inputs"] = dict(sorted(direct.items()))
        result["dependency_scope"] = "explicit direct inputs, checked against reads"
    return result

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
    data["publication"] = publication_metadata()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True,
                         allow_nan=False).encode("utf-8")
    write_bytes_atomic(path, payload)


def write_bytes_atomic(path: Path, payload: bytes) -> None:
    """One exclusive temporary-file attempt; permission errors fail immediately."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / ("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise


def write_json_atomic(path: Path, data: dict) -> None:
    """Publish current machine-readable records with a complete-file replacement."""
    _save_store(Path(path), data)


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
    return key in p and ("value" in p[key] or "reference" in p[key])


def get(key: str):
    """Read a parameter value.

    Raises KeyError if the key is absent or has no value.  Failing
    fast on a missing key is deliberate: a module that reads a value
    it depends on must never silently proceed with a None.
    """
    p = _read_params()
    if key not in p:
        raise KeyError(
            f"parameter '{key}' not in store (provenance: "
            f"{p.get(key, {}).get('provenance', 'absent')})"
        )
    return _checked_record(key, p)["value"]


def get_observed(key: str):
    """Read an external observed value (comparison only).

    Observed values must never enter computations; this accessor
    makes the intent explicit at the call site.
    """
    if _PREDICTION_ONLY.get():
        raise ValueError("observed-reference access inside a prediction calculation")
    p = _read_params()
    if key not in p or "value" not in p[key]:
        raise KeyError(f"observed parameter '{key}' not in store")
    if p[key].get("provenance") not in (_OBSERVED, _SM_INPUT):
        raise KeyError(f"'{key}' is not an observed parameter")
    return p[key]["value"]


def _invalidate_missing_projections(records, changed_key, writer):
    """Publish unavailable projections with the same atomic source replacement."""
    dependents = {}
    for alias, rec in records.items():
        ref = rec.get("reference")
        if isinstance(ref, dict) and "$ref" in ref:
            dependents.setdefault(ref["$ref"], []).append(alias)
    pending, visited = [changed_key], {changed_key}
    for source_key in pending:
        for alias in dependents.get(source_key, ()):
            if alias in visited:
                continue
            visited.add(alias)
            pending.append(alias)
            rec = records[alias]
            try:
                unavailable = resolve_value(rec["reference"], records, (alias,)) is None
            except (KeyError, IndexError, TypeError):
                unavailable = True
            if not unavailable:
                continue
            source = records[source_key]
            source_value = resolve_value(source.get("reference", source.get("value")),
                                         records, (source_key,))
            inputs = {source_key: value_fingerprint(source_value)}
            records[alias] = {
                "value": None, "provenance": _PENDING, "role": _ROLE_INFO,
                "note": f"Projection unavailable in the current {source_key} record.",
                "writer": writer,
                **_metadata(writer, definition=readout_definition(alias),
                            evidence_kind="availability of a canonical-record projection"),
                "direct_inputs": inputs, "module_read_inputs": inputs,
                "dependency_scope": "current source inspected during atomic publication",
            }


def record(
    key: str,
    value,
    *,
    provenance: str = _DERIVED,
    role: str = _ROLE_INTERNAL,
    note: str = "",
    dependencies=None,
    definition=None,
    evidence_kind: str = "computation under declared definitions",
    calculation: dict | None = None,
) -> None:
    """Publish immediately, including this module's read-input fingerprints."""
    if provenance not in _PROVENANCES:
        raise ValueError(f"unknown provenance '{provenance}'")
    if role not in _ROLES:
        raise ValueError(f"unknown role '{role}'")
    p = _read_params()
    writer = _writer()
    if definition is None:
        definition = readout_definition(key)
    p[key] = {
        "value": value,
        "provenance": provenance,
        "role": role,
        "note": note,
        "writer": writer,
        **_metadata(writer, comparison_kind="diagnostic"
                    if role == _ROLE_COMPARISON else None,
                    dependencies=dependencies, definition=definition,
                    evidence_kind=evidence_kind),
    }
    if calculation is not None:
        p[key]["calculation"] = deepcopy(calculation)
    _invalidate_missing_projections(p, key, writer)
    # Update the store immediately so that a later save() of another
    # module does not drop this record.
    data = _load_store(_PARAM_FILE)
    data["parameters"] = p
    _save_store(_PARAM_FILE, data)


def set(
    key: str,
    value,
    *,
    provenance: str = _DERIVED,
    role: str = _ROLE_INTERNAL,
    note: str = "",
    dependencies=None,
    definition=None,
    evidence_kind: str = "computation under declared definitions",
    calculation: dict | None = None,
) -> None:
    """Publish a derived (or input) value to the store and persist it.

    This is the primary publication API.  The provenance defaults to
    DERIVED (a computed quantity); observed/SM values should use
    compare_and_set() or sm_set() so the comparison intent is explicit.
    """
    record(key, value, provenance=provenance, role=role, note=note,
           dependencies=dependencies, definition=definition, evidence_kind=evidence_kind,
           calculation=calculation)


def annotate_error_kind(key: str, error_kind: str, *, note: str = "") -> None:
    """Attach a classification to an existing record without changing its value.

    Used by the release-wide metadata completion pass for diagnostic bundles,
    status records and exact structural values that never carried a
    ``QuantityDefinition``.  The value, provenance and writer are preserved.
    """
    if not isinstance(error_kind, str) or not error_kind.strip():
        raise ValueError("a nonempty error_kind is required")
    data = _load_store(_PARAM_FILE)
    record = data["parameters"].get(key)
    if record is None:
        raise KeyError(f"parameter {key!r} is absent")
    definition = record.get("quantity_definition")
    if not isinstance(definition, dict):
        definition = {}
    # A diagnostic/status record can lack a physical definition.  Preserve the
    # existing fields when present and fill the required schema explicitly;
    # these are metadata classifications, not reinterpretations of the value.
    definition.setdefault("object", key)
    definition.setdefault("unit", "framework units")
    definition.setdefault("carrier", "release diagnostic/structural record")
    definition.setdefault("operator", "named record")
    definition.setdefault("source", str(record.get("writer", "parameter store")))
    definition.setdefault("projection", "named production readout")
    definition.setdefault("normalization", "as stored")
    definition.setdefault("scheme", "release metadata completion")
    definition.setdefault("order", "not a perturbative expansion")
    definition.setdefault("scale_GeV", None)
    definition.setdefault("assumptions",
                          ("value is unchanged; classification only",))
    definition["error_kind"] = error_kind
    record["quantity_definition"] = definition
    if note:
        record["error_kind_note"] = note
    _save_store(_PARAM_FILE, data)


def annotate_interval(key: str, interval: dict, *, source: str,
                      note: str = "") -> None:
    """Attach a numeric interval to an existing record without changing its value.

    The interval is an additional certified field.  The centre, provenance and
    writer remain untouched, so the parameter table can expose the numeric bar
    directly instead of only publishing a separate interval record.
    """
    lo, hi = float(interval["lo"]), float(interval["hi"])
    if not math.isfinite(lo) or not math.isfinite(hi) or lo > hi:
        raise ValueError("a finite ordered interval is required")
    data = _load_store(_PARAM_FILE)
    record = data["parameters"].get(key)
    if record is None:
        raise KeyError(f"parameter {key!r} is absent")
    value = record.get("value")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not lo <= float(value) <= hi:
            raise ValueError(f"interval does not contain the stored value of {key!r}")
    definition = record.get("quantity_definition")
    if not isinstance(definition, dict):
        definition = {}
    definition["error_kind"] = "numeric interval propagated from a certified input"
    record["quantity_definition"] = definition
    record["interval"] = {"lo": lo, "hi": hi, "source": source}
    if note:
        record["interval_note"] = note
    _save_store(_PARAM_FILE, data)


def record_alias(key, source_key, path=(), *, role="comparison", note=""):
    """Publish a named projection without duplicating the source's numerical value."""
    source_value = get(source_key)
    for component in path:
        source_value = source_value[component]
    writer = _writer()
    data = _load_store(_PARAM_FILE)
    data["parameters"][key] = {
        "reference": {"$ref": source_key, "path": list(path)},
        "provenance": _DERIVED, "role": role, "note": note, "writer": writer,
        **_metadata(writer, comparison_kind="diagnostic" if role == _ROLE_COMPARISON else None,
                    dependencies=[source_key], definition=readout_definition(key),
                    evidence_kind="projection of a canonical computed record"),
    }
    _save_store(_PARAM_FILE, data)


def compare_and_set(
    key: str,
    value,
    observed,
    *,
    role: str = _ROLE_COMPARISON,
    note: str = "",
    dependencies=None,
    definition=None,
    evidence_kind: str = "computation under declared definitions",
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
    writer = _writer()
    if definition is None:
        definition = readout_definition(key)
    p[key] = {
        "value": value,
        "observed": observed,
        "deviation_pct": round(dev, 10),
        "provenance": _DERIVED,
        "role": role,
        "note": note,
        "writer": writer,
        **_metadata(writer, comparison_kind="observed_target",
                    dependencies=dependencies, definition=definition,
                    evidence_kind=evidence_kind),
    }
    data = _load_store(_PARAM_FILE)
    data["parameters"] = p
    _save_store(_PARAM_FILE, data)
    return dev


def sm_set(key: str, value, *, note: str = "", comparison_kind="observed_target") -> None:
    """Register a reference value or convention in the comparison store.

    The SM table is deliberately isolated from the physics store:
    nothing in the physics store may be read from the SM table as an
    input, so the comparison values can never back-calibrate the
    framework.
    """
    if comparison_kind not in ("observed_target", "declared_convention"):
        raise ValueError("unknown reference-data kind")
    data = _load_store(_SM_FILE)
    writer = _writer()
    data["parameters"][key] = {
        "value": value,
        "provenance": _SM_INPUT,
        "role": _ROLE_COMPARISON,
        "note": note,
        "writer": writer,
        **_metadata(writer, comparison_kind=comparison_kind),
    }
    _save_store(_SM_FILE, data)


def sm_value(key: str):
    """Read an isolated reference for the comparison stage."""
    if _PREDICTION_ONLY.get():
        raise ValueError("reference-data access inside a prediction calculation")
    sm = _read_sm()
    if key not in sm or "value" not in sm[key]:
        raise KeyError(f"SM value '{key}' not in reference_inputs.json")
    return sm[key]["value"]


def all_records() -> dict:
    """The full parameter record (for audits and reports)."""
    return resolved_records(_read_params())


def save() -> None:
    """Persist the current store (idempotent; the record() path already saves)."""
    # record() persists immediately; save() is kept for API compatibility
    # and for callers that prefer an explicit flush.
    data = _load_store(_PARAM_FILE)
    _save_store(_PARAM_FILE, data)


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
    records. The BBN quantities are computed by bbn_helium.py.
    """
    if not _PARAM_FILE.exists():
        data = {"version": 1, "parameters": {}}
        if anchors:
            for k, v in anchors.items():
                data["parameters"][k] = {
                    "value": v,
                    "provenance": _OBSERVED,
                    "role": _ROLE_ANCHOR,
                    "note": "declared observed dimensional anchor",
                    "writer": "cg_core/params.py",
                    **_metadata("cg_core/params.py", definition=readout_definition(k),
                                evidence_kind="declared external dimensional anchor"),
                    # An initial external anchor has no in-store parent.
                    # Its source is identified by the physical definition;
                    # initialization does not read a not-yet-created store.
                    "direct_inputs": {},
                    "dependency_scope": "external anchor; no in-store inputs",
                }
        _save_store(_PARAM_FILE, data)
    if not _SM_FILE.exists():
        data = {"version": 1, "note": "Reference data for comparisons; isolated from generated predictions", "parameters": {}}
        if sm_values:
            for k, v in sm_values.items():
                data["parameters"][k] = {
                    "value": v,
                    "provenance": _SM_INPUT,
                    "role": _ROLE_COMPARISON,
                    "note": "SM value for comparison only",
                    "writer": "cg_core/params.py",
                    **_metadata("cg_core/params.py", comparison_kind="observed_target"),
                }
        _save_store(_SM_FILE, data)


if __name__ == "__main__":
    # Smoke test: the store system must be self-consistent and exit 0.
    print("params.py smoke test")
    print(f"  project root : {_PROJECT_ROOT}")
    print(f"  param file   : {_PARAM_FILE} (exists: {_PARAM_FILE.exists()})")
    print(f"  sm file      : {_SM_FILE} (exists: {_SM_FILE.exists()})")
    print("  OK — module imports and store paths resolve.")
