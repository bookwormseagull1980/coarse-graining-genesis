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

"""Definitions, direct dependencies and observation-isolation negative controls."""
from dataclasses import replace
import json
import math
import shutil
import pytest
from cg_core import params
from cg_core.quantities import QuantityDefinition, readout_definition
from cg_frg.framework.five_items import verify_closures, INPUTS


def test_comparison_distinguishes_mass_ratio_from_cabibbo_input():
    from comparison.param_audit_full import MAPPING, comparison_value

    rows = {label: (key, reference, factor) for label, key, reference, factor in MAPPING}
    assert rows['m_d/m_s'][0] == 'm_s_over_m_d'
    assert rows['Cabibbo input r_G'][:2] == ('md_over_ms_geo', None)
    mass_ratio = 19.622983487591103
    assert comparison_value('m_d/m_s', mass_ratio, 1.) * mass_ratio == pytest.approx(1.)
    assert comparison_value('Cabibbo input r_G', .05014715428586189, 1.) == .05014715428586189
    with pytest.raises(ValueError):
        comparison_value('m_d/m_s', 0., 1.)


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    for name, filename in (("_PARAM_FILE", "cg_params.json"), ("_SM_FILE", "reference_inputs.json")):
        monkeypatch.setattr(params, name, tmp_path/filename)
    monkeypatch.setattr(params, "_READ_INPUTS", {})
    params.init_stores({"anchor": 4.0}, {"observed_reference": 17.0})
    return tmp_path


def test_definition_and_declared_direct_inputs(isolated_store):
    definition = QuantityDefinition("coupling", "1", "charged carrier", "vertex",
        "specified source", "fixed", "canonical", "specified", "tree", scale_GeV=100.)
    definition.require_same_definition(definition)
    with pytest.raises(ValueError, match="scale_GeV"):
        definition.require_same_definition(replace(definition, scale_GeV=101.))
    with pytest.raises(ValueError, match="was not read"):
        params.set("value", 8., dependencies=("anchor",), definition=definition)
    a = params.get("anchor")
    params.set("value", 2*a, dependencies=("anchor",), definition=definition,
               evidence_kind="specified matching example")
    record = params.all_records()["value"]
    assert set(record["direct_inputs"]) == {"anchor"}
    assert record["quantity_definition"]["scale_GeV"] == 100.


def test_empty_inputs_and_stale_input_rejection_preserve_store(isolated_store):
    """A content identity has no store parent; stale inputs cannot publish."""
    anchor = params.get("anchor")
    before = params.all_records()
    params.set("content_identity", 9./8., dependencies=(),
               note="finite hypercharge identity")
    records = params.all_records()
    assert records["content_identity"]["direct_inputs"] == {}
    assert {key: records[key] for key in before} == before

    # A later overwrite invalidates a previously consumed input fingerprint.
    # A failed publication must leave both the input and other records intact.
    params.set("anchor", anchor+1., dependencies=())
    unchanged = params._PARAM_FILE.read_bytes()
    with pytest.raises(ValueError, match="changed before publication"):
        params.set("stale_result", 2*anchor, dependencies=("anchor",))
    assert params._PARAM_FILE.read_bytes() == unchanged


def test_audit_rejects_broken_read_fingerprint_and_definition(isolated_store):
    from scripts.audit_param_writers import audit_file

    value = params.get("anchor")
    params.set("rho_Lambda", value, dependencies=("anchor",), note="metadata audit control")
    data = json.loads(params._PARAM_FILE.read_text(encoding="utf-8"))
    assert audit_file(params._PARAM_FILE, "test", True) == []
    # Corruption checks use a distinct test artifact, never the real store.
    damaged = isolated_store/"damaged.json"
    data["parameters"]["rho_Lambda"]["direct_inputs"]["anchor"] = "0"*64
    data["parameters"]["rho_Lambda"]["quantity_definition"]["unit"] = ""
    damaged.write_text(json.dumps(data), encoding="utf-8")
    failures = audit_file(damaged, "test", True)
    assert any("differs from recorded read" in item for item in failures)
    assert any("invalid physical definition" in item for item in failures)


def test_named_readout_contracts_preserve_units_and_physical_identity(isolated_store):
    expected_units = {
        'H0_GEV': 'GeV', 'sigma_C_hubble': 'GeV^-1', 'rho_Lambda': 'GeV^4',
        'Lambda': 'GeV^2', 'a0_MOND': 'm s^-2', 'T_CMB_GeV': 'GeV',
        'T_CMB_corrected_K': 'K', 'bbn_Tf': 'GeV', 'bbn_dm_np': 'GeV',
        'bbn_tau_n': 's', 'bbn_GF': 'GeV^-2', 'qcd_string_tension': 'GeV^2',
        'qcd_deconfinement_T': 'MeV', 'm_p': 'GeV', 'endpoint_r_drag_Mpc': 'Mpc',
        'm_nu1': 'eV', 'm_nu2': 'eV', 'm_nu3': 'eV', 'm_nu2_osc': 'eV',
        'Delta_m21_sq_raw': 'eV^2', 'Delta_m21_sq_osc': 'eV^2', 'Delta_m31_sq': 'eV^2',
    }
    for key, unit in expected_units.items():
        params.set(key, 1.)
        assert params.all_records()[key]['quantity_definition']['unit'] == unit
    with pytest.raises(ValueError, match='object'):
        readout_definition('Omega_Lambda').require_same_definition(readout_definition('Omega_Sigma'))
    with pytest.raises(ValueError, match='unit'):
        readout_definition('T_CMB_GeV').require_same_definition(readout_definition('T_CMB_corrected_K'))
    with pytest.raises(ValueError, match='object'):
        readout_definition('m_nu2').require_same_definition(readout_definition('m_nu2_osc'))
    assert readout_definition('unlisted_diagnostic') is None
    custom = QuantityDefinition('test mass', 'GeV', 'test', 'test', 'test', 'test',
                                'test', 'test', 'test')
    params.set('m_p', 2., definition=custom)
    assert params.all_records()['m_p']['quantity_definition']['object'] == 'test mass'


def test_comparison_mutation_does_not_feed_prediction(isolated_store):
    def prediction():
        with params.prediction_inputs_only():
            return params.get("anchor")**2
    first = prediction()
    params.sm_set("observed_reference", -1e20, note="isolation negative control")
    assert prediction() == first
    with params.prediction_inputs_only(), pytest.raises(ValueError, match="prediction calculation"):
        params.sm_value("observed_reference")
    params.compare_and_set("predicted_mass", 3., 3.1)
    with params.prediction_inputs_only():
        assert params.get("predicted_mass") == 3.
    params.set("diagnostic", 2., role="comparison")
    with params.prediction_inputs_only(), pytest.raises(ValueError, match="diagnostic"):
        params.get("diagnostic")
    params.set("same", 1.)
    params.set("same", 2.)
    assert params.all_records()["same"]["value"] == 2.


def test_production_shared_ew_and_mass_outputs_ignore_comparison_mutation(tmp_path, monkeypatch):
    """Exercise actual production modules with the complete current store.

    The negative control covers these modules and this fixed internal input
    state. It does not certify every framework path or external matching.
    All writes are redirected to pytest's temporary directory.
    """
    from cg_frg.ewsb import vev_closure, ew_precision, ew_one_loop
    from cg_frg.fermion import electron_mass
    from cg_frg.neutrino import neutrino_closure

    original_files = {name: getattr(params, name) for name in
                      ("_PARAM_FILE", "_SM_FILE")}
    original_bytes = {name: path.read_bytes() for name, path in original_files.items()}
    for name, source in original_files.items():
        destination = tmp_path/source.name
        shutil.copy2(source, destination)
        monkeypatch.setattr(params, name, destination)
    monkeypatch.setattr(params, "_STORE_ROOT", tmp_path)
    monkeypatch.setattr(params, "_READ_INPUTS", {})

    # The production leading-universal mixing reads an already computed rho
    # coefficient. No two-point diagnostic enters this observable's formula.
    def unused_self_energy(*args, **kwargs):
        raise AssertionError("production mixing repeated an unused self-energy")
    monkeypatch.setattr(ew_one_loop, "_B0", unused_self_energy)

    def produce():
        # These three writers have no comparison stage at all; enforce the
        # observed-input guard on their actual production calculations.
        for module in (vev_closure, electron_mass, neutrino_closure):
            params._READ_INPUTS.clear()
            with params.prediction_inputs_only():
                module.compute()
        # The actual EW writers publish observed comparisons after computing
        # several shared outputs. Their complete production paths run here.
        for module in (ew_precision, ew_one_loop):
            params._READ_INPUTS.clear()
            module.compute()
        return params.all_records()

    first = produce()
    from comparison.sm_rge.inputs import published_running_mass_benchmark
    first_comparison = published_running_mass_benchmark()
    baseline = params.resolved_records(json.loads(original_bytes["_PARAM_FILE"])["parameters"])

    def compare_snapshot(actual, expected):
        # A stored binary-float snapshot can differ in its last few bits
        # across numerical-library versions. The observation-isolation
        # comparison between the two executions below remains exact.
        if isinstance(expected, dict):
            assert actual.keys() == expected.keys()
            for key in expected:
                compare_snapshot(actual[key], expected[key])
        elif isinstance(expected, float):
            assert actual == pytest.approx(expected, rel=1e-14, abs=0.)
        else:
            assert actual == expected

    compare_snapshot({key: record["value"] for key, record in first.items()},
                     {key: record["value"] for key, record in baseline.items()})
    sm_records = json.loads(params._SM_FILE.read_text(encoding="utf-8"))["parameters"]
    changed = []
    for index, (key, record) in enumerate(sorted(sm_records.items())):
        value = record.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            replacement = value*(1.37+index/100) if value else (index+1)/8
            params.sm_set(key, replacement, note="production isolation negative control")
            changed.append(key)
    assert {"m_W_obs", "Gamma_Z_obs", "Gamma_b_obs", "m_H_obs"} <= set(changed)
    # Structured observations are varied in valid nested fields. Their
    # covariance remains positive and the comparison calculation still runs.
    mass_reference = params.sm_value("running_mass_reference")
    mass_reference["masses_GeV"][0] *= 1.01
    mass_reference["standard_deviations_GeV"][0] *= 1.05
    params.sm_set("running_mass_reference", mass_reference)
    pole_reference = params.sm_value("charged_lepton_pole_reference")
    pole_reference["masses_GeV"]["tau"] *= 1.01
    params.sm_set("charged_lepton_pole_reference", pole_reference)
    cmb = params.sm_value("CMB_MONOPOLE")
    cmb["temperature_K"] *= 1.01
    params.sm_set("CMB_MONOPOLE", cmb)
    bao = params.sm_value("DESI_DR2_BAO")
    bao["rows"][0]["observed"] *= 1.01
    params.sm_set("DESI_DR2_BAO", bao)
    second_comparison = published_running_mass_benchmark()
    assert second_comparison["residuals"][0] != first_comparison["residuals"][0]
    assert second_comparison["standard_deviations"][0] != first_comparison["standard_deviations"][0]
    assert (second_comparison["charged_lepton_QED_check"]["running_log_combination"]
            != first_comparison["charged_lepton_QED_check"]["running_log_combination"])
    second = produce()
    assert {key: record["value"] for key, record in first.items()} == {
        key: record["value"] for key, record in second.items()}

    published = ("v_HIGGS", "m_e_pred", "m_nu1", "m_nu2", "m_nu3", "M_Z_pred",
                 "M_W_pred", "Gamma_Z_pred", "Gamma_b_pred_1loop", "sin2_theta_eff_l_pred",
                 "Gamma_had_pred_lead1loop", "Gamma_Z_pred_lead1loop",
                 "R_b_pred_lead1loop", "R_l_pred_lead1loop", "sigma_had_pred_lead1loop")
    assert all(key in second for key in published)
    for key in ("M_W_pred", "Gamma_Z_pred", "m_H_pred", "Gamma_b_pred_1loop"):
        assert first[key]["observed"] != second[key]["observed"]
        assert first[key]["deviation_pct"] != second[key]["deviation_pct"]
    for key, dependencies, unit in (("v_HIGGS", {"M_G", "kL", "tau"}, "GeV"),
                                     ("m_e_pred", {"M_P", "kL", "tau"}, "MeV"),
                                     ("m_nu3", {"v_HIGGS", "k_GUT", "tau"}, "eV"),
                                     ("m_nu2_osc", {"v_HIGGS", "k_GUT", "tau", "ns_tilt"}, "eV")):
        assert set(second[key]["direct_inputs"]) == dependencies
        assert second[key]["quantity_definition"]["unit"] == unit
        assert second[key]["dependency_scope"] == "explicit direct inputs, checked against reads"
    for name, original in original_files.items():
        assert original.read_bytes() == original_bytes[name]

    # Store boundaries follow the value expression, including distinctions
    # between partial widths and between the two independent scalar sectors.
    assert set(second["rho_param"]["direct_inputs"]) == {"v_HIGGS", "m_t_pred", "m_b_pred"}
    assert set(second["m_H_pred"]["direct_inputs"]) == {"lambda_H_pseudo", "v_HIGGS"}
    assert "order_parameter_lambda" in second["m_H_pred"]["module_read_inputs"]
    assert "alpha_s_MZ_pred" not in second["Gamma_l_pred"]["direct_inputs"]
    assert "alpha_s_MZ_pred" in second["Gamma_had_pred"]["direct_inputs"]
    assert set(second["sin2_theta_eff_l_pred"]["direct_inputs"]) == {
        "M_Z_pred", "alpha_inv_MZ_pred", "v_HIGGS", "m_t_pred"}


def test_primordial_and_flavour_bindings_are_output_specific(tmp_path, monkeypatch):
    from cg_frg.cosmology import perturbation_amplitude, spectral_tilt
    from cg_frg.generation import sector_alpha, lz_ladder, window_capacity
    from cg_frg.fermion import mass_operator_overlap
    from cg_frg.ewsb import pseudo_dilaton

    original = params.all_records()
    for name in ("_PARAM_FILE", "_SM_FILE"):
        source = getattr(params, name)
        target = tmp_path/source.name
        shutil.copy2(source, target)
        monkeypatch.setattr(params, name, target)
    monkeypatch.setattr(params, "_STORE_ROOT", tmp_path)
    monkeypatch.setattr(params, "_READ_INPUTS", {})

    modules = (perturbation_amplitude, spectral_tilt, sector_alpha, lz_ladder,
               window_capacity, mass_operator_overlap, pseudo_dilaton)
    for module in modules:
        params._READ_INPUTS.clear()
        with params.prediction_inputs_only():
            module.compute()
    actual = params.all_records()
    assert {key: rec["value"] for key, rec in actual.items()} == {
        key: rec["value"] for key, rec in original.items()}
    assert set(actual["alpha_up"]["direct_inputs"]) == {"kL", "tau"}
    assert "ns_tilt" in actual["alpha_up"]["module_read_inputs"]
    assert set(actual["sector_alpha_delta"]["direct_inputs"]) == {"ns_tilt", "kL_CMB"}
    assert actual["ladder_98_identity"]["direct_inputs"] == {}
    assert actual["y_top_base"]["direct_inputs"] == {}
    assert set(actual["m_t_pred"]["direct_inputs"]) == {"v_HIGGS"}
    assert actual["lambda_H_pseudo"]["direct_inputs"] == {}
    assert set(actual["pseudo_dilaton_beta_eff"]["direct_inputs"]) == {
        "g2_MG", "g1_MG_geo", "y_top_base"}

    # An unrelated source variation changes sector-step outputs but leaves
    # the up-sector exponent fixed. Check actual values, not only metadata.
    params.set("ns_tilt", 1.1*actual["ns_tilt"]["value"])
    sector_alpha.compute()
    changed = params.all_records()
    assert changed["alpha_up"]["value"] == actual["alpha_up"]["value"]
    assert changed["alpha_down"]["value"] != actual["alpha_down"]["value"]


def test_status_fails_when_actual_relation_is_changed():
    values = {key: params.get(key) for key in INPUTS}
    assert verify_closures(values)["passed"]
    values["m_e_pred"] *= 1.01
    result = verify_closures(values)
    assert not result["passed"]
    assert result["items"]["electron_mass"]["status"] == "FAIL"
