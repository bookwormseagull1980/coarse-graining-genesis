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

"""Parameter provenance, observation isolation and source-verification tests."""
import subprocess
import sys
from pathlib import Path
import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_PARENTED_TREES = []


@pytest.fixture(scope="module", autouse=True)
def _release_parented_ast_trees():
    """Release bidirectional AST links after the source-analysis tests."""
    yield
    import ast
    import gc
    for tree in _PARENTED_TREES:
        for node in ast.walk(tree):
            # Operator and context nodes may be shared by separate parses.
            if hasattr(node, "_parent"):
                del node._parent
    _PARENTED_TREES.clear()
    # Drop traversal locals before collecting the remaining reference cycles.
    tree = node = None
    gc.collect()


def _run_audit() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" / "audit_param_writers.py")],
        capture_output=True, text=True)


@pytest.mark.release_audit
def test_audit_exits_clean():
    """The audit must pass on the current store (all records complete)."""
    r = _run_audit()
    assert r.returncode == 0, f"audit failed:\n{r.stdout}\n{r.stderr}"
    assert "AUDIT CLEAN" in r.stdout


@pytest.mark.release_audit
def test_observation_leakage_audit_exits_clean():
    """Observed-value access must remain quarantined to comparison contexts."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_observation_leakage.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"observation audit failed:\n{r.stdout}\n{r.stderr}"
    assert "OBSERVATION-LEAKAGE AUDIT CLEAN" in r.stdout


@pytest.mark.release_audit
def test_lean_source_audit_exits_clean():
    """Lean proof sources must not contain holes or external axioms."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_lean_sources.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"Lean source audit failed:\n{r.stdout}\n{r.stderr}"
    assert "LEAN SOURCE AUDIT CLEAN" in r.stdout
    assert "no interactive output commands" in r.stdout


@pytest.mark.release_audit
def test_numeric_precision_audit_exits_clean():
    """Stored numeric values must not be rounded or formatted before writing."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_numeric_precision.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"numeric precision audit failed:\n{r.stdout}\n{r.stderr}"
    assert "NUMERIC PRECISION AUDIT CLEAN" in r.stdout


@pytest.mark.release_audit
def test_path_portability_audit_exits_clean():
    """Reviewer-facing files must not leak machine-local absolute paths."""
    r = subprocess.run(
        [sys.executable, str(_PROJECT_ROOT / "scripts" /
                            "audit_path_portability.py")],
        capture_output=True, text=True)
    assert r.returncode == 0, f"path portability audit failed:\n{r.stdout}\n{r.stderr}"
    assert "PATH PORTABILITY AUDIT CLEAN" in r.stdout


def test_audit_detects_missing_observed(tmp_path):
    """Comparison records require a structured target or diagnostic kind."""
    import json
    from scripts.audit_param_writers import audit_file
    path = tmp_path / "params.json"
    data = {"parameters": {"_audit_test_broken": {
        "value": 1.0, "provenance": "DERIVED",
        "role": "comparison", "note": "no observed target here",
        "writer": "cg_core/params.py",
    }}}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True),
                    encoding="utf-8")
    errors = audit_file(path, "test", True)
    assert len(errors) == 1
    assert "without structured target or diagnostic kind" in errors[0]


def _observation_violations(source, path="cg_frg/ewsb/ew_precision.py", **analysis):
    import ast
    from scripts.audit_observation_leakage import ObservationVisitor
    tree = ast.parse(source)
    _PARENTED_TREES.append(tree)
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child._parent = parent
    visitor = ObservationVisitor(_PROJECT_ROOT / path, **analysis)
    visitor.visit(tree)
    return visitor.violations


def test_observation_in_prediction_slot_is_rejected():
    assert _observation_violations(
        "def compute():\n    compare_and_set('x', sm_value('M_Z'), 1.)\n")
    assert not _observation_violations(
        "def compute():\n    compare_and_set('x', 1., sm_value('M_Z'))\n")


def test_main_and_alias_do_not_hide_observation_flow():
    assert _observation_violations(
        "from cg_core.params import sm_value as measured\n"
        "def main():\n    x=measured('M_Z')\n    y=2*x\n    pset('x',y)\n")
    assert _observation_violations(
        "def main():\n    from cg_core.params import sm_value as measured\n"
        "    pset('x',measured('M_Z'))\n")


@pytest.mark.parametrize("api,function,key,path", [
    ("published_record", "current_camb_record", "endpoint_camb_record",
     "cg_frg/cosmology/camb_interface.py"),
    ("published_sm_value", "current_bao_record", "DESI_DR2_BAO",
     "cg_frg/cosmology/camb_interface.py"),
    ("published_sm_value", "current_sparc_record", "SPARC_MASS_MODELS",
     "cg_frg/cosmology/endpoint_residual.py"),
    ("sm_value", "main", "DESI_DR2_BAO", "scripts/run_bao_comparison.py"),
    ("sm_value", "main", "CAMB_PROPAGATION_SETTINGS", "scripts/run_explicit_camb.py"),
])
def test_registered_comparison_readers_retain_prediction_sink_checks(api, function, key, path):
    source = (f"from cg_core.params import {api} as read_comparison, record\n"
              f"def {function}():\n"
              f"    data = read_comparison('{key}')\n"
              "    transformed = {'result': data}\n")
    assert not _observation_violations(
        source+"    record('comparison_result', transformed, role='comparison')\n", path)
    violations = _observation_violations(
        source+"    record('prediction', transformed, role='internal')\n", path)
    assert any("observation reaches prediction value" in detail
               for _, _, detail in violations)
    assert not _observation_violations(
        source+"    from cg_core.params import sm_set\n    sm_set('dataset', data)\n", path)


def test_reproduction_summary_reference_read_retains_prediction_sink_checks():
    source = ("from cg_core.params import sm_value, record\n"
              "def summary():\n    reference_key='M_Z'\n"
              "    reference=sm_value(reference_key)\n")
    path = "scripts/reproduce_v5.py"
    assert not _observation_violations(source+"    print(reference)\n", path)
    assert any("observation reaches prediction value" in detail for _, _, detail in
               _observation_violations(source+"    record('mass',reference)\n", path))
    assert _observation_violations(source.replace("def summary", "def compute"), path)


@pytest.mark.parametrize("path,function", [
    ("scripts/init_v5.py", "init"),
    ("comparison/sm_rge/inputs.py", "init_sm_table"),
])
def test_registered_reference_initialization_retains_prediction_sink_checks(path, function):
    source = ("from cg_core.params import published_sm_value, sm_set, record\n"
              f"def {function}():\n    key='M_Z'\n"
              "    reference=published_sm_value(key)\n")
    assert not _observation_violations(source+"    sm_set(key,reference)\n", path)
    assert any("observation reaches prediction value" in detail for _, _, detail in
               _observation_violations(source+"    record('mass',reference)\n", path))


def test_comparison_return_and_import_alias_remain_tainted():
    source = (
        "from cg_core.params import published_sm_value, record\n"
        "def current_sparc_record():\n"
        "    data = published_sm_value('SPARC_MASS_MODELS')\n"
        "    return {'rows': data}\n"
        "def derived_comparison():\n"
        "    result = current_sparc_record()\n"
        "    return result\n"
        "def compute():\n"
        "    record('prediction', derived_comparison(), role='internal')\n"
    )
    assert any("observation reaches prediction value" in detail for _, _, detail in
               _observation_violations(source, "cg_frg/cosmology/endpoint_residual.py"))
    source = (
        "from cg_frg.cosmology.camb_interface import current_camb_record as completed\n"
        "from cg_core.params import record\n"
        "def compute():\n    record('prediction', completed({}), role='internal')\n"
    )
    assert _observation_violations(source, "cg_frg/cosmology/endpoint_residual.py")


def test_published_observation_transfer_is_limited_to_registered_keys():
    source = (
        "from cg_core.params import published_sm_value, sm_set\n"
        "def compute():\n"
        "    for dataset_key in (BAO_DATA_KEY, SPARC_DATA_KEY):\n"
        "        data = published_sm_value(dataset_key)\n"
        "        sm_set(dataset_key, data)\n"
    )
    path = "cg_frg/cosmology/endpoint_residual.py"
    assert not _observation_violations(source, path)
    assert _observation_violations(source.replace("SPARC_DATA_KEY", "UNDECLARED_DATA_KEY"), path)
    assert _observation_violations(source, "cg_frg/fermion/electron_mass.py")
    assert _observation_violations(
        "def main():\n    x = sm_value('M_Z')\n", "scripts/run_bao_comparison.py")


@pytest.mark.parametrize("mutation", [
    "items.append(sm_value('M_Z'))",
    "items.extend([sm_value('M_Z')])",
    "items.insert(0, sm_value('M_Z'))",
    "items.update({'mass': sm_value('M_Z')})",
    "items.setdefault('mass', sm_value('M_Z'))",
    "items['mass'] = sm_value('M_Z')",
])
def test_container_observation_flow_reaches_prediction_writer(mutation):
    source = ("from cg_core.params import sm_value, record\n"
              "def main():\n    items = {}\n    "+mutation+"\n"
              "    record('mass', items, role='internal')\n")
    failures = _observation_violations(source, "cg_frg/ewsb/ew_one_loop.py")
    assert any("observation reaches prediction value" in detail for _, _, detail in failures)
    assert not _observation_violations(source.replace("role='internal'", "role='comparison'"),
                                        "cg_frg/ewsb/ew_one_loop.py")


def test_mutable_alias_and_comparison_package_writes_remain_checked():
    source = ("from cg_core.params import sm_value, record\n"
              "def report():\n    result = []\n    alias = result\n"
              "    alias.append(sm_value('M_Z'))\n    record('mass', result)\n")
    assert _observation_violations(source, "comparison/crosschecks.py")


def test_cross_module_comparison_returns_follow_alias_and_module_imports():
    import ast
    from scripts.audit_observation_leakage import project_return_summaries
    source = ("from cg_core.params import sm_value\n"
              "def measured():\n    out = {}\n    out.update({'mass':sm_value('M_Z')})\n    return out\n"
              "def computed():\n    value=2.\n    target=sm_value('M_Z')\n    return value\n")
    middle = ("from comparison.fixture import measured as read\n"
              "def forwarded():\n    return read()\n")
    trees = {_PROJECT_ROOT/"comparison/fixture.py": ast.parse(source),
             _PROJECT_ROOT/"comparison/middle.py": ast.parse(middle)}
    summaries = project_return_summaries(trees)
    assert "comparison.fixture.measured" in summaries
    assert "comparison.middle.forwarded" in summaries
    assert "comparison.fixture.computed" not in summaries
    for imported, expression in (
        ("from comparison.middle import forwarded as read", "read()"),
        ("import comparison.middle as ref", "ref.forwarded()"),
        ("import comparison.middle", "comparison.middle.forwarded()"),
    ):
        caller = imported+"\nfrom cg_core.params import record\ndef compute():\n    record('mass',"+expression+")\n"
        assert _observation_violations(caller, return_summaries=summaries)
    assert not _observation_violations(
        "from comparison.fixture import computed\ndef compute():\n    pset('mass',computed())\n",
        return_summaries=summaries)


def test_known_comparison_get_is_distinct_from_computed_observed_target():
    import ast
    from scripts.audit_observation_leakage import comparison_record_names
    records = {"diagnostic": {"role":"comparison", "comparison_kind":"diagnostic"},
               "predicted_mass": {"role":"comparison", "comparison_kind":"observed_target"}}
    trees = {_PROJECT_ROOT/"comparison/fixture.py": ast.parse(
        "def publish():\n    record('another_diagnostic', {}, role='comparison')\n")}
    keys = comparison_record_names(trees, records)
    assert keys == {"diagnostic", "another_diagnostic"}
    source = ("from cg_core.params import get as read, record\n"
              "def compute():\n    data=read('diagnostic')\n    record('mass',data['nested']['mass'])\n")
    assert _observation_violations(source, comparison_records=keys)
    assert not _observation_violations(source.replace("'diagnostic'", "'predicted_mass'"),
                                       comparison_records=keys)


def test_actual_registered_mass_comparison_is_in_project_return_summary():
    from scripts.audit_observation_leakage import parse_with_parents, project_return_summaries
    path = _PROJECT_ROOT/"comparison/sm_rge/inputs.py"
    tree = parse_with_parents(path)
    _PARENTED_TREES.append(tree)
    summaries = project_return_summaries({path: tree})
    assert "comparison.sm_rge.inputs.published_running_mass_benchmark" in summaries
    assert _observation_violations(
        "from comparison.sm_rge.inputs import published_running_mass_benchmark as reference\n"
        "def compute():\n    pset('mass',reference()['residuals'][0])\n",
        return_summaries=summaries)


@pytest.mark.parametrize("reader, declaration, expression", [
    ("from cg_core.params import read_store_document as read", "", "read('references')"),
    ("import cg_core.params as params", "", "params.read_store_document(store='references')"),
    ("from cg_core.params import read_store_document", "STORE = 'references'\n",
     "read_store_document(store=STORE)"),
])
def test_reference_document_access_is_an_explicit_comparison_source(reader, declaration, expression):
    source = (reader+"\nfrom cg_core.params import record\n"+declaration+
              "def calculate():\n    data="+expression+"\n"
              "    record('mass',data['parameters']['mass']['value'],role='internal')\n")
    assert _observation_violations(source, "cg_frg/fermion/electron_mass.py")
    assert any("observation reaches prediction value" in detail for _, _, detail in
               _observation_violations(source, "comparison/crosschecks.py"))
    assert not _observation_violations(source.replace("role='internal'", "role='comparison'"),
                                       "comparison/crosschecks.py")


def test_parameter_document_does_not_taint_a_computed_value_as_an_observation():
    source = ("from cg_core.params import read_store_document, record\n"
              "def report():\n    data=read_store_document('parameters')\n"
              "    record('calculated',data['parameters']['calculated']['value'])\n")
    assert not _observation_violations(source, "comparison/crosschecks.py")


@pytest.mark.parametrize("path,function", [
    ("scripts/reproduce_v5.py", "external_input_fingerprints"),
    ("scripts/verify_v5.py", "store_summary"),
    ("scripts/audit_numeric_stability.py", "load_records"),
    ("scripts/make_reviewer_dashboard.py", "load_json"),
])
def test_reference_metadata_readers_retain_prediction_sink_checks(path, function):
    source = ("from cg_core.params import read_store_document, record\n"
              f"def {function}():\n    data=read_store_document('references')\n")
    assert not _observation_violations(source+"    return len(data['parameters'])\n", path)
    assert _observation_violations(source+"    record('mass',data['parameters']['mass']['value'])\n", path)
    assert _observation_violations(source, "cg_frg/fermion/electron_mass.py")
