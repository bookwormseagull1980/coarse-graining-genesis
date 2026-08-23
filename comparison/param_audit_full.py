# -*- coding: utf-8 -*-
"""scripts/param_audit_full.py — V4.0: full-parameter recompute + observation comparison.

Recomputes the ENTIRE chain (reproduce_v4), then compares EVERY closed
parameter against its observed value (where one exists) and prints a
categorised deviation table.  No fitting — each deviation is reported
as-is.
"""
import subprocess, sys, json, io, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

GEV_TO_K = 1.160451812e13
GENERATED_STORES = [
    ROOT / "cg_params.json",
    ROOT / "comparison" / "sm_inputs.json",
    ROOT / "params_write_log.json",
]

# (label, cg_key, sm_key or None, factor)  factor converts cg value -> sm units
MAPPING = [
    # --- gauge couplings ---
    ("g2(M_G)",              "g2_MG",               "g2_MG",        1.0),
    ("g2(M_G) geometric",    "g2_MG_geo",           "g2_MG",        1.0),
    ("g1(M_G)",              "g1_MG_geo",           "g1_MG",        1.0),
    ("g3(M_G)",              "g3_MG_geo",           "g3_MG",        1.0),
    ("g3 GUT (common origin)","g3_common_origin_pred","g3_sm_GUT",  1.0),
    ("alpha_s(M_Z)",         "alpha_s_MZ_pred",     None,           1.0),   # 0.1179 standard
    ("alpha_em(M_Z) inv",     "alpha_inv_MZ_pred",   None,           1.0),   # 127.95 standard (alpha_em at M_Z, NOT the zero-momentum 137.036)
    # --- generations / masses ---
    ("n_generations",        "n_generations",       None,           1.0),   # 3
    ("m_t/m_c",              "m_t_over_m_c",        "m_t_over_m_c_obs", 1.0),
    ("m_b/m_s",              "m_b_over_m_s",        "m_b_over_m_s_obs", 1.0),
    ("m_t/m_u",              "m_t_over_m_u",        "m_t_over_m_u_obs", 1.0),
    ("m_t (GeV)",            "m_t_pred",            "m_t_obs",      1.0),
    ("m_b (GeV)",            "m_b_pred",            "m_b_obs",      1.0),
    ("m_e (MeV)",            "m_e_pred",            "m_e_obs",      1.0),
    ("m_mu/m_e",             "m_mu_over_m_e",       "m_mu_over_m_e_obs", 1.0),
    ("m_d/m_s",              "md_over_ms_geo",      "m_d_over_m_s_obs", 1.0),
    ("m_s/m_d",              "m_s_over_m_d",        None,           1.0),   # 19.8
    ("m_p (GeV)",            "m_p",                 "m_p_obs",      1.0),
    # --- EW ---
    ("epsilon (dilaton)",    "epsilon_dilaton",     "epsilon_obs",  1.0),
    ("v_HIGGS (GeV)",        "v_HIGGS",             "v_HIGGS_obs",  1.0),
    ("M_Z (GeV)",            "M_Z_pred",            "M_Z",          1.0),
    ("M_W Born+rho (GeV)",   "M_W_pred",            "m_W_obs",      1.0),
    ("M_W lead-univ (GeV)",  "M_W_pred_lead1loop",  "m_W_obs",      1.0),
    ("Gamma_Z (GeV)",        "Gamma_Z_pred",        "Gamma_Z_obs",  1.0),
    ("Gamma_b Born (GeV)",   "Gamma_b_pred",        "Gamma_b_obs",  1.0),
    ("Gamma_b 1-loop (GeV)", "Gamma_b_pred_1loop",  "Gamma_b_obs",  1.0),
    ("sigma_had (nb)",       "sigma_had_pred",      "sigma_had_obs", 1.0),
    ("m_H (GeV)",            "m_H_pred",            "m_H_obs",      1.0),
    ("sin^2 thetaW(M_Z)",    "s2_thetaW_MZ",        "sin2thetaW_MSbar_obs", 1.0),
    ("sin^2 theta_eff^l",    "sin2_theta_eff_l_pred","sin2thetaW_eff_obs", 1.0),
    # --- neutrino / PMNS ---
    ("m_nu3 (eV)",           "m_nu3",               "m_nu3_obs",    1.0),
    ("m_nu2 rest (eV)",      "m_nu2",               None,           1.0),
    ("m_nu1 floor (eV)",     "m_nu1",               None,           1.0),
    ("Delta m21^2 osc",      "Delta_m21_sq_osc",    "Delta_m21_sq_obs", 1.0),
    ("Delta m31^2",          "Delta_m31_sq",        "Delta_m31_sq_obs", 1.0),
    ("sin^2 theta12",        "sin2_theta12",        None,           1.0),   # 0.30
    ("sin^2 theta13",        "sin2_theta13",        None,           1.0),
    ("sin^2 theta23",        "sin2_theta23",        None,           1.0),
    # --- CKM / CP ---
    ("delta_CKM (deg)",      "ckm_delta_direction", "ckm_delta_deg_obs", 180.0/math.pi),
    ("Jarlskog J",           "cp_jarlskog_magnitude","jarlskog_J_obs", 1.0),
    ("V_us",                 "V_us_geo",            "V_us_obs",     1.0),
    ("eta_b",                "eta_b",               "eta_b_obs",    1.0),
    # --- cosmology ---
    ("1 - n_s",              "ns_tilt",             "one_minus_ns_obs", 1.0),
    ("Delta2_R",             "perturbation_amplitude","Delta2_R_obs", 1.0),
    ("Lambda (GeV^2)",       "Lambda",              "Lambda_obs",   1.0),
    ("H0 (GeV)",             "H0_GEV",              "H0_GeV_obs",   1.0),
    ("Omega_Lambda",         "Omega_Lambda",        "Omega_Lambda_obs", 1.0),
    ("Omega_b",              "Omega_b",             "Omega_b_obs",  1.0),
    ("Omega_Sigma",          "Omega_Sigma",         "Omega_DM_obs", 1.0),
    ("T_CMB corrected (K)",  "T_CMB_corrected_K",   "T_CMB_K",      1.0),
    ("a0 MOND (m/s^2)",      "a0_MOND",             "a0_MOND_obs",  1.0),
    ("gw ratio r",           "gw_ratio",            "r_bound_obs",  1.0),
    # --- QCD ---
    ("Lambda_QCD (GeV)",     "qcd_Lambda_QCD",      "Lambda_QCD_obs", 1.0),
    ("string tension (GeV^2)","qcd_string_tension",  "string_tension_obs", 1.0),
    ("T_deconf (MeV)",       "qcd_deconfinement_T", "T_deconf_obs", 1.0),
    ("m_glueball (GeV)",     "m_glueball",          "m_glueball_obs", 1.0),
    # --- BBN ---
    ("Y_p (BBN)",            "bbn_Yp",              "Y_p_obs",      1.0),
    ("N_eff (BBN)",          "bbn_Neff",            "N_eff_obs",    1.0),
]

GEV_TO_K = 1.160451812e13

FIXED_OBS = {
    "alpha_s(M_Z)": 0.1179,
    "alpha_em(M_Z) inv": 127.95,   # alpha_em(M_Z) = 1/127.95 (running, at M_Z)
    "n_generations": 3.0,
    "m_s/m_d": 19.8,
}


def reset_generated_stores() -> list[str]:
    removed = []
    for path in GENERATED_STORES:
        if path.exists():
            path.unlink()
            removed.append(path.relative_to(ROOT).as_posix())
    return removed


def main() -> int:
    # 1. recompute the entire chain
    print("== recomputing the full chain (reproduce_v4) ==")
    removed = reset_generated_stores()
    if removed:
        print("fresh store reset: " + ", ".join(removed))
    r = subprocess.run([PY, str(ROOT / "scripts" / "reproduce_v4.py")],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    ok = (r.returncode == 0) and ("ALL MODULES PASSED" in (r.stdout or ""))
    print(f"reproduce exit={r.returncode}  passed={ok}\n")

    # 2. load stores
    cg = json.load(io.open(ROOT / "cg_params.json", encoding="utf-8"))
    cgp = cg["parameters"]
    sm = json.load(io.open(ROOT / "comparison" / "sm_inputs.json", encoding="utf-8"))
    smp = sm.get("parameters", sm)

    def getv(store, key):
        v = store.get(key)
        return v["value"] if isinstance(v, dict) else v

    # 3. compare
    BOUNDS = {"gw ratio r"}   # these observables are UPPER BOUNDS, not central values
    print("=" * 74)
    print(f"  {'quantity':22s} {'predicted':>14s} {'observed':>12s} {'dev':>9s}")
    print("=" * 74)
    n_obs = 0
    for label, ck, sk, fac in MAPPING:
        if ck not in cgp:
            print(f"  {label:22s} {'MISSING':>14s}")
            continue
        pred = getv(cgp, ck) * fac
        if sk and sk in smp:
            obs = getv(smp, sk)
        elif label in FIXED_OBS:
            obs = FIXED_OBS[label]
        else:
            print(f"  {label:22s} {pred:14.6g} {'(no obs)':>12s}")
            continue
        if label in BOUNDS:
            status = "OK (<= bound)" if pred <= obs else "EXCEEDS"
            n_obs += 1
            print(f"  {label:22s} {pred:14.6g} {'<=' + str(obs):>12s} {status:>9s}")
            continue
        dev = (pred / obs - 1.0) * 100.0
        n_obs += 1
        print(f"  {label:22s} {pred:14.6g} {obs:12g} {dev:+8.3f}%")
    print("=" * 74)
    print(f"  {n_obs} observables compared; all comparisons are post-computation (no fitting).")
    if not ok:
        print("\nERROR: reproduce_v4.py did not pass; the comparison table is incomplete.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
