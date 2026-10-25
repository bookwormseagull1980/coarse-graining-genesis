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

"""Read-only comparison of the completed parameter calculation.

Each row gives the generated value, its stated reference convention
when available, and the central-value difference. The comparison uses
the stored calculation at fixed inputs.
"""
import sys, json, io, math, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from cg_core.params import resolved_records, read_store_document

PY = sys.executable

GEV_TO_K = 1.160451812e13
GENERATED_STORES = [
    ROOT / "cg_params.json",
    ROOT / "comparison" / "reference_inputs.json",
]

# (label, cg_key, sm_key or None, factor)  factor converts cg value -> sm units
MAPPING = [
    # --- gauge couplings ---
    ("g2(M_G)",              "g2_MG",               "g2_MG",        1.0),
    ("g2(M_G) geometric",    "g2_MG_geo",           "g2_MG",        1.0),
    ("g1(M_G)",              "g1_MG_geo",           "g1_MG",        1.0),
    ("g3(M_G)",              "g3_MG_geo",           "g3_MG",        1.0),
    ("g3 GUT (common origin)","g3_common_origin_pred","g3_sm_GUT",  1.0),
    ("alpha_s(M_Z)",         "alpha_s_MZ_pred",     "alpha_s_MZ_obs", 1.0),
    ("alpha_em(M_Z) inv",    "alpha_inv_MZ_pred",   "alpha_inv_MZ_obs", 1.0),
    # --- generations / masses ---
    ("n_generations",        "n_generations",       None,           1.0),
    ("m_t/m_c",              "m_t_over_m_c",        "m_t_over_m_c_obs", 1.0),
    ("m_b/m_s",              "m_b_over_m_s",        "m_b_over_m_s_obs", 1.0),
    ("m_t/m_u",              "m_t_over_m_u",        "m_t_over_m_u_obs", 1.0),
    ("m_t (GeV)",            "m_t_pred",            "m_t_obs",      1.0),
    ("m_b (GeV)",            "m_b_pred",            "m_b_obs",      1.0),
    ("m_e geom (MeV)",       "m_e_pred",            "m_e_obs",      1.0),
    ("m_mu/m_e geom",        "m_mu_over_m_e",       "m_mu_over_m_e_obs", 1.0),
    ("m_d/m_s",              "m_s_over_m_d",        "m_d_over_m_s_obs", 1.0),
    ("Cabibbo input r_G",     "md_over_ms_geo",      None,           1.0),
    ("m_s/m_d",              "m_s_over_m_d",        "m_d_over_m_s_obs", 1.0),
    ("m_p (GeV)",            "m_p",                 "m_p_obs",      1.0),
    # --- EW ---
    ("epsilon (dilaton)",    "epsilon_dilaton",     "epsilon_obs",  1.0),
    ("v_HIGGS (GeV)",        "v_HIGGS",             "v_HIGGS_obs",  1.0),
    ("M_Z (GeV)",            "M_Z_pred",            "M_Z",          1.0),
    ("M_W lead-univ (GeV)",  "M_W_pred_lead1loop",  "m_W_obs",      1.0),
    ("Gamma_Z effective (GeV)", "Gamma_Z_pred_lead1loop", "Gamma_Z_obs", 1.0),
    ("Gamma_b effective (GeV)", "Gamma_b_pred_1loop", "Gamma_b_obs", 1.0),
    ("Gamma_had effective (GeV)", "Gamma_had_pred_lead1loop", "Gamma_had_obs", 1.0),
    ("Gamma_l per flavour (GeV)", "Gamma_l_pred_lead1loop", "Gamma_l_obs", 1.0/3.0),
    ("Gamma_inv effective (GeV)", "Gamma_inv_pred_lead1loop", "Gamma_inv_obs", 1.0),
    ("R_b effective",          "R_b_pred_lead1loop", "R_b_obs", 1.0),
    ("R_l effective",          "R_l_pred_lead1loop", "R_l_obs", 1.0),
    ("sigma_had effective (nb)", "sigma_had_pred_lead1loop", "sigma_had_obs", 1.0),
    ("m_H (GeV)",            "m_H_pred",            "m_H_obs",      1.0),
    ("sin^2 thetaW(M_Z)",    "s2_thetaW_MZ",        "sin2thetaW_MSbar_obs", 1.0),
    ("sin^2 theta_eff^l",    "sin2_theta_eff_l_pred","sin2thetaW_eff_obs", 1.0),
    # --- neutrino / PMNS ---
    ("m_nu3 rest (eV)",      "m_nu3",               None,           1.0),
    ("m_nu2 rest (eV)",      "m_nu2",               None,           1.0),
    ("m_nu1 floor (eV)",     "m_nu1",               None,           1.0),
    ("Delta m21^2 rest",     "Delta_m21_sq_raw",    "Delta_m21_sq_obs", 1.0),
    ("Delta m21^2 tilt",     "Delta_m21_sq_osc",    "Delta_m21_sq_obs", 1.0),
    ("Delta m31^2",          "Delta_m31_sq",        "Delta_m31_sq_obs", 1.0),
    ("sin^2 theta12",        "sin2_theta12",        None,           1.0),   # 0.30
    ("sin^2 theta13",        "sin2_theta13",        None,           1.0),
    ("sin^2 theta23",        "sin2_theta23",        None,           1.0),
    # --- CKM / CP ---
    ("delta_CKM (deg)",      "ckm_delta_direction", "ckm_delta_deg_obs", 180.0/math.pi),
    ("Jarlskog J",           "cp_jarlskog_magnitude","jarlskog_J_obs", 1.0),
    ("V_us",                 "V_us_geo",            "V_us_obs",     1.0),
    ("eta_b source",         "eta_b",               None,           1.0),
    ("eta_B propagation",    "eta_B_propagation",   "eta_b_obs",    1.0),
    # --- cosmology ---
    ("1 - n_s",              "ns_tilt",             "one_minus_ns_obs", 1.0),
    ("Delta2_R",             "perturbation_amplitude","Delta2_R_obs", 1.0),
    ("Lambda (GeV^2)",       "Lambda",              "Lambda_obs",   1.0),
    ("H0 (GeV)",             "H0_GEV",              "H0_GeV_obs",   1.0),
    ("Omega_Lambda",         "Omega_Lambda",        "Omega_Lambda_obs", 1.0),
    ("Omega_b",              "Omega_b",             "Omega_b_obs",  1.0),
    ("Omega_Sigma budget",   "Omega_Sigma",         None,           1.0),
    ("Omega_Sigma cold",     "Omega_Sigma_cold",    "Omega_DM_obs", 1.0),
    ("T_CMB corrected (K)",  "T_CMB_corrected_K",   "T_CMB_K",      1.0),
    ("a0 MOND (m/s^2)",      "a0_MOND",             "a0_MOND_obs",  1.0),
    ("gw ratio r",           "gw_ratio",            "r_bound_obs",  1.0),
    # --- QCD ---
    ("Lambda_QCD (GeV)",     "qcd_Lambda_QCD",      "Lambda_QCD_obs", 1.0),
    ("string tension (GeV^2)","qcd_string_tension",  "string_tension_obs", 1.0),
    ("T_deconf (MeV)",       "qcd_deconfinement_T", "T_deconf_obs", 1.0),
    ("m_glueball (GeV)",     "m_glueball",          "m_glueball_obs", 1.0),
    # --- BBN ---
    ("Delta_np (GeV)",        "bbn_dm_np",           "dm_np_obs_GeV", 1.0),
    ("tau_n (s)",             "bbn_tau_n",           "tau_n_obs",    1.0),
    ("Y_p (BBN)",            "bbn_Yp",              "Y_p_obs",      1.0),
    ("N_eff (BBN)",          "bbn_Neff",            "N_eff_obs",    1.0),
]

def comparison_value(label, value, factor):
    """Convert the declared mass ratio or dimensional quantity for display."""
    if label == "m_d/m_s":
        if value <= 0:
            raise ValueError("the strange-to-down mass ratio must be positive")
        return 1.0 / value
    return value * factor


def main() -> int:
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in GENERATED_STORES}
    print("== read-only comparison of the completed run ==")

    # Load the generated records and the separately stored reference values.
    cg = read_store_document(source_root=ROOT)
    cgp = resolved_records(cg["parameters"])
    sm = read_store_document("references", source_root=ROOT)
    smp = sm.get("parameters", sm)
    manifest = json.loads((ROOT / "run_manifest.json").read_text(encoding="utf-8"))
    print("run_id:", manifest["run_id"])
    print("Solar rows distinguish the static spectrum from the specified tilt propagation readout.")
    print("Effective Z observables use one common neutral-current amplitude; Gamma_l is per flavour.")
    print("Charged-lepton geom rows compare geometric readouts with pole data under G_l=1 (diagnostic).")

    def getv(store, key):
        v = store.get(key)
        return v["value"] if isinstance(v, dict) else v

    BOUNDS = {"gw ratio r"}   # Observational upper limits.
    print("=" * 74)
    print(f"  {'quantity':22s} {'predicted':>14s} {'reference':>12s} {'dev':>9s}")
    print("=" * 74)
    n_compared = 0
    for label, ck, sk, fac in MAPPING:
        if ck not in cgp or getv(cgp, ck) is None:
            print(f"  {label:22s} {'MISSING':>14s}")
            continue
        pred = comparison_value(label, getv(cgp, ck), fac)
        if sk and sk in smp:
            reference = getv(smp, sk)
            if label == "m_s/m_d":
                if reference <= 0:
                    raise ValueError("the reference down-to-strange mass ratio must be positive")
                reference = 1.0 / reference
        else:
            print(f"  {label:22s} {pred:14.6g} {'(no reference)':>14s}")
            continue
        if label in BOUNDS:
            status = "OK (<= bound)" if pred <= reference else "EXCEEDS"
            n_compared += 1
            print(f"  {label:22s} {pred:14.6g} {'<=' + str(reference):>12s} {status:>9s}")
            continue
        dev = (pred / reference - 1.0) * 100.0
        n_compared += 1
        print(f"  {label:22s} {pred:14.6g} {reference:12g} {dev:+8.3f}%")
    print("=" * 74)
    print(f"  {n_compared} reference comparisons at fixed generated inputs.")
    if before != {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in GENERATED_STORES}:
        raise RuntimeError("published stores changed during read-only comparison")
    return 0


if __name__ == "__main__":
    sys.exit(main())
