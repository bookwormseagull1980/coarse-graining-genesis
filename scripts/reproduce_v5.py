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
scripts/reproduce_v5.py — V5.0: the one-command reproduction of the
entire framework chain
=================================================================

Calculation
-----------
The computation is reproducible end-to-end: from the anchors
to every closure, in dependency order, with a final summary table
of every closed quantity and its deviation.  This script is that
single entry point.

The ordered module list computes the parameter anchors, internal spectra,
finite-domain endpoint, coupling boundaries, mass scales, cosmological
readouts and macroscopic gravitational response. The generated records
include physical definitions and the input values consumed by each module.

The run starts with empty stores in a temporary directory. Parameter,
observation-isolation and input-binding checks precede publication.
Finite source-response calculations use the completed stores. The manifest
binds the software identity, calculation and verification sources,
external comparison records and published outputs to the same run.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 I/O so the closure table prints on any console code page
# (the default GBK console of a Chinese Windows mangles the UTF-8 '—/→/±'
# that some modules legitimately print, and the parent re-encode of a
# captured line would otherwise raise UnicodeEncodeError).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from cg_core.release import publication_metadata
from cg_core.params import (value_fingerprint, write_json_atomic, write_bytes_atomic,
                            read_store_document)

_PY = sys.executable

# The module list in dependency order (each runs its own __main__).
MODULES = [
    "scripts/init_v5.py",
    "cg_core/spectrum_loop.py",
    "cg_core/sm_content.py",
    "cg_core/cluster_decay.py",
    "cg_frg/frg/spectral_sum.py",
    "cg_frg/frg/endpoint_constraint.py",
    "comparison/sm_rge/run_rge.py",
    "cg_frg/ewsb/vev_closure.py",
    "cg_frg/frg/gamma_M.py",
    "cg_frg/frg/ir_flow.py",
    "cg_frg/gauge/geometric_couplings.py",
    "comparison/crosschecks.py",
    "cg_frg/generation/window_capacity.py",
    "cg_frg/ewsb/relaxion_chain.py",
    "cg_frg/ewsb/relaxion_geo.py",
    "cg_frg/ewsb/epsilon_ratio.py",
    # The step-by-step integralisation of the six J=2 squash level-transfer
    # coefficients: a verification module whose
    # self-test asserts every factor (v, m_nu3, T_d, Delta2_R, m_p, alpha_s,
    # rho_Lambda) and the conservation laws to machine precision.
    "cg_frg/ewsb/squash_level_transfer.py",
    "cg_frg/cosmology/spectral_tilt.py",
    "cg_frg/cosmology/dark_energy.py",
    "cg_frg/cosmology/perturbation_amplitude.py",
    "cg_frg/generation/sector_alpha.py",
    "cg_frg/generation/lz_ladder.py",
    "cg_frg/generation/lz_dynamics.py",  # current-parameter ladder consistency check
    "cg_frg/fermion/mass_operator_overlap.py",
    "cg_frg/gravity/zk_gravitational_rg.py",
    "cg_frg/ewsb/order_parameter.py",
    "cg_frg/ewsb/pseudo_dilaton.py",
    "cg_frg/gauge/geometric_ewsb.py",
    "cg_frg/gravity/tt_tensor.py",
    "cg_frg/gravity/pole_analysis.py",
    "cg_frg/gravity/chi_pole_condition.py",
    "cg_frg/gravity/external_tensor.py",
    "cg_frg/gravity/newton.py",
    "cg_frg/neutrino/neutrino_closure.py",
    "cg_frg/neutrino/neutrino_mass_matrix.py",
    "cg_frg/fermion/electron_mass.py",
    "cg_frg/framework/cp_sector.py",
    "cg_frg/frg/trace_density.py",
    "cg_frg/qcd/mass_gap_scale.py",
    "cg_frg/qcd/qcd_sector.py",
    "cg_frg/cosmology/bbn_helium.py",
    "cg_frg/ewsb/ew_precision.py",
    "cg_frg/ewsb/ew_one_loop.py",
    "cg_frg/cosmology/gw_ratio.py",
    # The evaluated closure summary consumes the Gaussian distance published
    # by gw_ratio as well as the already computed masses and generation count.
    "cg_frg/framework/five_items.py",
    "cg_frg/cosmology/endpoint_residual.py",
    "cg_frg/framework/sigma_language.py",
    "cg_frg/frg/discrete_flow.py",
    "cg_frg/gauge/gauge_group_emergence.py",
]

# Summary entries: (physical label, generated key, reference key, reference multiplier).
# Reference values are read only after publication through the common interface.
CLOSURES = [
    ("kL* (F_MG fixed point)", "kL", None, 1),
    ("M_G (emergence scale)", "M_G", None, 1),
    ("g2(M_G) geometric", "g2_MG", "g2_MG", 1),
    ("n_generations", "n_generations", None, 1),
    ("m_t/m_c", "m_t_over_m_c", "m_t_over_m_c_obs", 1),
    ("m_b/m_s", "m_b_over_m_s", "m_b_over_m_s_obs", 1),
    ("m_t/m_u", "m_t_over_m_u", "m_t_over_m_u_obs", 1),
    ("epsilon (dilaton line)", "epsilon_dilaton", "epsilon_obs", 1),
    ("v_HIGGS (GeV)", "v_HIGGS", "v_HIGGS_obs", 1),
    ("1 - n_s", "ns_tilt", "one_minus_ns_obs", 1),
    ("Lambda (GeV^2)", "Lambda", "Lambda_obs", 1),
    ("TT slope_G", "TT_slope_G", None, 1),
    ("internal trajectory flag", "TT_delta_forming", None, 1),
    ("common-unit r_read", "gravity_r_read", None, 1),
    ("common-unit Z_read", "gravity_Z_read", None, 1),
    ("common-unit G_read", "gravity_G_read", None, 1),
    ("m_nu3 rest (eV)", "m_nu3", None, 1),
    ("m_nu2 rest (eV)", "m_nu2", None, 1),
    ("Delta m21^2 osc", "Delta_m21_sq_osc", "Delta_m21_sq_obs", 1),
    ("Delta m31^2", "Delta_m31_sq", "Delta_m31_sq_obs", 1),
    ("sin^2 theta12", "sin2_theta12", None, 1),
    ("m_t (GeV)", "m_t_pred", "m_t_obs", 1),
    ("m_e (MeV)", "m_e_pred", "m_e_obs", 1),
    ("Delta2_R", "perturbation_amplitude", "Delta2_R_obs", 1),
    ("m_glueball (GeV)", "m_glueball", "m_glueball_obs", 1),
    ("mass gap dE/M_G", "mass_gap_dE", None, 1),
    ("H0 (GeV)", "H0_GEV", "H0_GeV_obs", 1),
    ("M_Z (GeV)", "M_Z_pred", "M_Z", 1),
    ("M_W lead-univ (GeV)", "M_W_pred_lead1loop", "m_W_obs", 1),
    ("Gamma_b effective (GeV)", "Gamma_b_pred_1loop", "Gamma_b_obs", 1),
    ("Gamma_l three flavours (GeV)", "Gamma_l_pred_lead1loop", "Gamma_l_obs", 3),
    ("Gamma_inv effective (GeV)", "Gamma_inv_pred_lead1loop", "Gamma_inv_obs", 1),
    ("Gamma_had effective (GeV)", "Gamma_had_pred_lead1loop", "Gamma_had_obs", 1),
    ("Gamma_Z effective (GeV)", "Gamma_Z_pred_lead1loop", "Gamma_Z_obs", 1),
    ("R_b effective", "R_b_pred_lead1loop", "R_b_obs", 1),
    ("R_l effective", "R_l_pred_lead1loop", "R_l_obs", 1),
    ("sigma_had effective (nb)", "sigma_had_pred_lead1loop", "sigma_had_obs", 1),
    ("m_H (GeV)", "m_H_pred", "m_H_obs", 1),
    ("r (GW tensor ratio)", "gw_ratio", None, 1),
    ("Omega_Sigma", "Omega_Sigma", None, 1),
    ("C_gamma", "photon_zero_mode_Cgamma", None, 1),
    ("T_CMB corrected (K)", "T_CMB_corrected_K", "T_CMB_K", 1),
    ("endpoint z_eq", "endpoint_z_eq", None, 1),
    ("endpoint r_drag", "endpoint_r_drag_Mpc", None, 1),
    ("endpoint sigma8", "endpoint_sigma8", None, 1),
    ("endpoint S8", "endpoint_S8", None, 1),
    ("2L = sqrt(2pi)", "twoL_entropy_min_distance", None, 1),
    ("alpha_up (internal)", "alpha_up", None, 1),
    ("alpha_dn (internal)", "alpha_down", None, 1),
    ("alpha_lp (internal)", "alpha_lepton", None, 1),
    ("sector step Delta", "sector_alpha_delta", None, 1),
    ("sin^2 theta(M_Z)", "s2_thetaW_MZ", "sin2thetaW_MSbar_obs", 1),
    ("sin^2 theta_eff^l", "sin2_theta_eff_l_pred", "sin2thetaW_eff_obs", 1),
    ("m_tau (GeV)", "m_tau_pred", "m_tau_obs", 1),
    ("order parameter lambda", "order_parameter_lambda", None, 1),
    ("Z quantum shift", "Z_quantum_shift", None, 1),
    ("m_WR (GeV)", "geometric_ewsb_m_WR", None, 1),
]


def run_all(env: dict | None = None) -> list:
    """Run every module in order; collect the failures."""
    failures = []
    for mod in MODULES:
        print(f"\n── {mod} ──")
        r = subprocess.run([_PY, str(_PROJECT_ROOT / mod)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env)
        out = (r.stdout or "") + (r.stderr or "")
        for line in out.splitlines():
            print("  " + line)
        if r.returncode != 0:
            failures.append(mod)
            break
    return failures


def summary() -> None:
    """The final closure table from the store."""
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    from cg_core.params import get, sm_value

    print("\n" + "=" * 66)
    print("  V5 CLOSURE TABLE")
    print("=" * 66)
    print(f"  {'quantity':24s} {'value':>14s} {'reference':>12s} {'dev':>8s}")
    for label, key, reference_key, reference_multiplier in CLOSURES:
        try:
            val = get(key)
        except KeyError:
            print(f"  {label:24s} {'MISSING':>14s}")
            continue
        obs = sm_value(reference_key) * reference_multiplier if reference_key else None
        if isinstance(val, (int, float)) and obs is not None:
            dev = (val / obs - 1.0) * 100.0
            print(f"  {label:24s} {val:14.6g} {obs:12g} {dev:+7.3f}%")
        else:
            print(f"  {label:24s} {str(val):>14s} {'--':>12s}")


def source_fingerprints() -> dict:
    paths = [p for folder in ("cg_core", "cg_frg", "scripts", "comparison")
             for p in (_PROJECT_ROOT / folder).rglob("*.py")]
    return {p.relative_to(_PROJECT_ROOT).as_posix():
            hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def storage_contract() -> dict:
    """The two scientific stores and the separate run-validation manifest."""
    return {
        "schema_version": 1,
        "scientific_stores": {
            "cg_params.json": "computed parameters, response records and validated solver records",
            "comparison/reference_inputs.json": "isolated observational references and comparison datasets",
        },
        "manifest": "software, source and store fingerprints, execution identity and verification only",
        "scientific_value_reads": "read the scientific stores; the manifest only validates their identity",
    }


def solver_execution_identity(root: Path = _PROJECT_ROOT) -> dict:
    """Identify retained solver executions and resources in the computed store."""
    root = Path(root)
    params_path = root / "cg_params.json"
    records = read_store_document("parameters", source_root=root)["parameters"] if params_path.is_file() else {}
    camb = records.get("endpoint_camb_record", {}).get("value", {})
    identities = {"CAMB": {"store": "cg_params.json", "record": "endpoint_camb_record",
                            "field": "execution_sha256", "sha256": camb.get("execution_sha256")}}
    thermal = camb.get('thermal_history_budget', {})
    atomic = thermal.get('direct_hyrec_atomic_response', {})
    if atomic:
        identities['HYREC'] = {
            'store': 'cg_params.json', 'record': 'endpoint_camb_record',
            'field': 'thermal_history_budget.direct_hyrec_atomic_response.resource_sha256',
            'sha256': value_fingerprint(atomic['resource_sha256']),
            'thermal_execution_sha256': thermal['budget_sha256']}
    return identities


def external_input_fingerprints(root: Path = _PROJECT_ROOT) -> dict:
    """Fingerprint every isolated reference and retain the named dataset hashes."""
    root = Path(root)
    comparison_path = root / "comparison" / "reference_inputs.json"
    observations = read_store_document("references", source_root=root)["parameters"] if comparison_path.is_file() else {}
    return {"CAMB_execution": solver_execution_identity(root)["CAMB"]["sha256"],
            **{key: value_fingerprint(observations[key]["value"]) if key in observations else None
               for key in ("DESI_DR2_BAO", "SPARC_MASS_MODELS")},
            "reference_records": {key: value_fingerprint(record["value"])
                                  for key, record in sorted(observations.items())}}


def verification_fingerprints(root: Path = _PROJECT_ROOT) -> dict:
    """Bind local checks and the pinned reference to the independent proof library."""
    paths = [p for folder, suffix in (("tests", "*.py"), ("lean_proofs", "*.lean"))
             for p in (root / folder).rglob(suffix)]
    paths.extend(root / name for name in ("pyproject.toml", "requirements.txt"))
    reference = root / "foundations-reference.json"
    if reference.is_file():
        paths.append(reference)
    result = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(paths)}
    return result


def execute(destination: Path, *, publish: bool, recompute_responses=False) -> int:
    """Build from empty stores, then publish complete results without backups."""
    if (destination / "cg_params.json").exists():
        raise ValueError("output directory already contains a run; use an empty directory")
    destination.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
    env = os.environ.copy()
    env.update(V5_OUTPUT_DIR=str(destination), V5_RUN_ID=run_id,
               PYTHONDONTWRITEBYTECODE="1")
    reference_root = Path(env.get("V5_REFERENCE_DIR", str(_PROJECT_ROOT)))
    env["V5_REFERENCE_DIR"] = str(reference_root)
    sources = source_fingerprints()
    verification_sources = verification_fingerprints()
    comparisons = external_input_fingerprints(reference_root)
    failures = run_all(env)
    if failures:
        print("FAILED; the existing published stores have not been changed:", failures)
        return 1
    params_path = destination / "cg_params.json"
    data = read_store_document("parameters", source_root=destination)
    parameters = data["parameters"]
    required = ("kL", "M_G", "g1_MG_geo", "g2_MG", "g3_MG_geo", "v_HIGGS",
                "M_Z_pred", "M_W_pred", "Gamma_Z_pred", "Gamma_b_pred_1loop",
                "Gamma_had_pred_lead1loop", "Gamma_Z_pred_lead1loop",
                "Gamma_l_pred_lead1loop", "Gamma_inv_pred_lead1loop",
                "rho_NC_leading", "z_pole_partial_widths",
                "sin2_theta_eff_l_pred", "sin2_theta_eff_b_pred",
                "R_b_pred_lead1loop", "R_l_pred_lead1loop", "sigma_had_pred_lead1loop",
                "m_nu1", "m_nu2", "m_nu3", "eta_b", "H0_GEV", "Omega_Sigma",
                "gravity_r_read", "gravity_Z_read", "gravity_G_read",
                "external_tensor_Z", "external_tensor_residue", "external_tensor_G",
                "external_tensor_Pi_critical", "external_tensor_chi_slope",
                "external_tensor_status")
    missing = [key for key in required if key not in parameters]
    if missing:
        raise RuntimeError(f"required outputs missing from this run: {missing}")
    stale = [key for key, rec in parameters.items()
             if rec.get("provenance") == "DERIVED" and rec.get("run_id") != run_id]
    if stale:
        raise RuntimeError(f"outputs not produced by this run: {stale}")
    command = [_PY, str(_PROJECT_ROOT / "scripts/evaluate_joint_extensions.py"),
               "--store", str(params_path), "--publish"]
    if recompute_responses:
        command.append("--recompute")
    extension = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", env=env)
    if extension.returncode:
        raise RuntimeError(extension.stderr or extension.stdout)
    print(extension.stdout.strip())
    audits = {}
    for script in ("audit_param_writers.py", "audit_observation_leakage.py"):
        audit = subprocess.run([_PY, str(_PROJECT_ROOT / "scripts" / script)],
                               cwd=str(_PROJECT_ROOT), env=env,
                               capture_output=True, text=True, encoding="utf-8")
        if audit.returncode:
            raise RuntimeError(f"{script} rejected this run:\n{(audit.stdout + audit.stderr).strip()}")
        audits[script] = {"returncode": 0, "ok": True,
                         "cmd": "python scripts/" + script,
                         "summary": "Completed the source and data-isolation audit."}
    if source_fingerprints() != sources:
        raise RuntimeError("source changed during reproduction; result is not published")
    if verification_fingerprints() != verification_sources:
        raise RuntimeError("verification source changed during reproduction; result is not published")
    if external_input_fingerprints(reference_root) != comparisons:
        raise RuntimeError("comparison input changed during reproduction; result is not published")
    final_records = read_store_document("parameters", source_root=destination)["parameters"]
    if any(rec.get("run_id") != run_id for rec in final_records.values()
           if rec.get("provenance") == "DERIVED"):
        raise RuntimeError("all published records must identify the current run")
    files = tuple(storage_contract()["scientific_stores"])
    manifest = {"publication": publication_metadata(),
                "storage_contract": storage_contract(),
                "solver_execution_identity": solver_execution_identity(destination),
                "run_id": run_id, "python": sys.version.split()[0],
                "status": "complete computational run",
                "scope": "declared framework; input-bound external comparisons carry separate status",
                "source_sha256": sources, "audits": audits,
                "verification_source_sha256": verification_sources,
                "external_input_sha256": external_input_fingerprints(destination),
                "output_sha256": {name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
                                  for name in files}}
    write_json_atomic(destination / "run_manifest.json", manifest)
    if publish:
        if str(_PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(_PROJECT_ROOT))
        for name in files + ("run_manifest.json",):
            target = _PROJECT_ROOT / name
            write_bytes_atomic(target, (destination / name).read_bytes())
        summary()
    print(f"COMPLETE: {run_id}; outputs {'published' if publish else 'validated in output directory'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute-responses", action="store_true",
                        help="independently evaluate all response calculations instead of reusing verified records")
    parser.add_argument("--output-dir", type=Path,
                        help="empty calculation directory; do not publish to the framework store")
    args = parser.parse_args()
    if args.output_dir:
        return execute(args.output_dir.resolve(), publish=False, recompute_responses=args.recompute_responses)
    with tempfile.TemporaryDirectory(prefix="v5-calculation-") as temporary:
        return execute(Path(temporary), publish=True, recompute_responses=args.recompute_responses)


if __name__ == "__main__":
    sys.exit(main())
