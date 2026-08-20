# -*- coding: utf-8 -*-
"""
comparison/sm_rge/inputs.py — V4.0: the SM measured inputs at M_Z
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The SM RGE (beta_functions, run_rge) runs the Standard Model
couplings for COMPARISON: the framework's geometric couplings are
compared against the SM extrapolations at M_G and k_GUT.  The SM
inputs at M_Z are an external datum (PDG 2024 / Buttazzo et al.
2013); they live in the SM comparison store (sm_inputs.json) and
are never used as computation inputs by the physics modules.

THE INPUT VALUES (PDG 2024 / Buttazzo 2013 conventions)
-------------------------------------------------------
M_Z     = 91.1876 GeV     (the Z mass)
M_Pl    = 2.435e18 GeV    (the reduced Planck mass, 1/√(8πG_N))
g1_MZ   = 0.461425        (GUT-normalised: √(5/3) g', α₁ = 5α/(3c_w²))
g2_MZ   = 0.64779         (α₂ = α/s_w²)
g3_MZ   = 1.217200        (α_s(M_Z))
yt_MZ   = 0.940           (the top Yukawa)
lam_MZ  = 0.129           (the Higgs quartic at M_Z; the PDG-derived
                           value is 0.1294)
ye/yu/yd_MZ = 2.935e-6 / 6.0e-6 / 1.34e-5   (the light Yukawas)

V4 DISCIPLINE
-------------
These are SM comparison values only (provenance SM_INPUT).  The
module writes them to sm_inputs.json (idempotently: missing keys
are written, existing keys are left untouched).
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import sm_set  # noqa: E402

# The SM inputs (external, comparison only).
# ============================================================
# DISCIPLINE (2026-08-15): these observed values are for COMPARISON
# / TEST programs only.  A physics module that uses any of these to
# COMPUTE a framework value is a violation (reverse-fitting).  Read
# them via sm_value() and use them ONLY as comparison targets.
# ============================================================
SM_INPUTS = {
    # -- RGE inputs at M_Z (PDG 2024 / Buttazzo 2013) --
    "M_Z": 91.1876,
    "M_Pl": 2.435e18,
    "g1_MZ": 0.461425,
    "g2_MZ": 0.64779,
    "g3_MZ": 1.217200,
    "yt_MZ": 0.940,
    "lam_MZ": 0.129,
    "lambda_H_MZ": 0.1294,
    "ye_MZ": 2.935e-6,
    "yu_MZ": 6.0e-6,
    "yd_MZ": 1.34e-5,
    "alpha_inv_obs": 137.036,
    "alpha_inv_MZ_obs": 127.952,
    "alpha_s_MZ_obs": 0.1179,
    "tau_n_obs": 879.4,
    # -- electroweak --
    "v_HIGGS_obs": 246.22,
    "m_W_obs": 80.369,
    # -- electroweak precision observables (PDG 2024, comparison only;
    #    consumed by comparison/ew_precision.py as comparison targets) --
    "G_F_obs": 1.1663788e-5,
    "m_H_obs": 125.20,
    "Gamma_Z_obs": 2.4952,
    "Gamma_had_obs": 1.7444,
    "Gamma_l_obs": 0.083966,
    "Gamma_b_obs": 0.37705,
    "Gamma_inv_obs": 0.4990,
    "sigma_had_obs": 41.481,
    "R_l_obs": 20.767,
    "R_b_obs": 0.21629,
    "sin2thetaW_eff_obs": 0.23153,
    "sin2thetaW_MSbar_obs": 0.23122,
    "rho_obs": 1.0004,
    # -- QCD --
    "m_glueball_obs": 1.7,
    "Lambda_QCD_obs": 0.210,
    "T_deconf_obs": 270.0,
    "string_tension_obs": 0.1936,
    "m_p_obs": 0.938272,
    # lattice QCD glueball tower (Morningstar-Peardon, comparison)
    "m_glueball_2pp_ratio_obs": 1.41,
    "m_glueball_0ppstar_ratio_obs": 1.47,
    "m_glueball_0mp_ratio_obs": 1.53,
    # -- fermion masses / ratios --
    "m_e_obs": 0.511,
    "m_mu_obs": 0.105658,
    "m_mu_over_m_e_obs": 206.8,
    "m_t_obs": 172.69,
    "m_b_obs": 4.18,
    "m_tau_obs": 1.777,
    "m_t_over_m_c_obs": 136.0,
    "m_b_over_m_s_obs": 45.0,
    "m_t_over_m_u_obs": 78000.0,
    "m_tau_over_m_mu_obs": 16.8,
    # -- neutrino --
    "m_nu3_obs": 0.0502,
    "m_nu2_obs": 0.0086,
    "m_nu1_obs": 0.0026,
    "V_us_obs": 0.2245,
    # -- CKM / CP --
    "pmns_delta_over_pi_obs": 1.14,
    "s23_pmns_obs": 0.55,
    "s13_pmns_obs": 0.022,
    "s12_pmns_obs": 0.304,
    "jarlskog_J_obs": 3.06e-5,
    "ckm_delta_deg_obs": 68.5,
    "lambda_C_obs": 0.2248,
    "A_ckm_obs": 0.823,
    "eta_ckm_obs": 0.344,
    "rho_bar_ckm_obs": 0.157,
    "m_d_over_m_s_obs": 0.0505,
    "m_u_over_m_c_obs": 0.00184,
    # -- cosmology --
    "H0_GeV_obs": 1.44e-42,
    "r_bound_obs": 0.036,
    "a0_MOND_obs": 1.2e-10,
    "c_m_s_obs": 2.99792458e8,
    "Omega_b_obs": 0.0493,
    "T_CMB_K": 2.7255,
    "Omega_Lambda_obs": 0.6847,
    "Lambda_obs": 4.2791148e-84,
    "eta_b_obs": 6.1e-10,
    "Delta2_R_obs": 2.105e-9,
    "one_minus_ns_obs": 0.0351,
    # -- BBN (observation targets, comparison only) --
    "Y_p_obs": 0.245,
    "N_eff_obs": 3.044,
    "Omega_DM_obs": 0.2645,
    # -- EWSB ratio --
    "epsilon_obs": 1.4243e-16,
}


# The nature-given nuclear-physics inputs of the BBN sub-calculation
# were REMOVED (2026-08-17): the five constants (dm_np, T_f, tau_n,
# t_decay, N_eff) are now DERIVED by cg_frg/cosmology/bbn_helium.py
# from the framework's v, M_P, m_e and the down-sector mass ladder.


def init_sm_table() -> None:
    """Write the SM inputs into sm_inputs.json (idempotent).

    (The BBN nuclear constants are DERIVED by bbn_helium.py; they are
    no longer written as a separate input store.)
    """
    for key, value in SM_INPUTS.items():
        sm_set(key, value, note="SM measured input (comparison only)")


def sm_value(key: str):
    """Read an SM input value (comparison only)."""
    from cg_core.params import sm_value as _sm_value

    return _sm_value(key)


if __name__ == "__main__":
    init_sm_table()
    print("sm_rge/inputs OK")
