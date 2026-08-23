# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""
scripts/reproduce_v4.py — V4.0: the one-command reproduction of the
entire framework chain
=================================================================

WHY THIS SCRIPT EXISTS (motivation)
-----------------------------------
The V4 rebuild must be reproducible end-to-end: from the anchors
to every closure, in dependency order, with a final summary table
of every closed quantity and its deviation.  This script is that
single entry point.

THE CHAIN (dependency order)
----------------------------
1. init_v4          — the anchors + seed comparison table
2. spectral_sum     — the 5-channel mode sums
3. endpoint_constraint — the F_MG fixed point + coupling closure
4. sm_rge           — the SM running table at the final chain points
5. gamma_M / ir_flow — the entropy identity and the γ_M profile
6. geometric_couplings — g2/g1 at M_G (the geometric couplings)
7. window_capacity / lz_ladder — the generation sector (3 + LZ)
8. relaxion_chain / epsilon_ratio / squash_level_transfer —
   the EW scale and the step-by-step integralisation of the six
   J=2 squash level-transfer coefficients (the L3 closure,
   verification module)
9. spectral_tilt / dark_energy / perturbation_amplitude — the
   cosmology (the CMB-window publishes kL_CMB)
10. sector_alpha / lz_ladder — the internal sector ladder (B-level)
11. mass_operator_overlap / zk_gravitational_rg / order_parameter /
    geometric_ewsb — the absolute Yukawa base, the Z(k) running,
    the order parameter, the geometric EWSB (B-level)
12. tt_tensor / pole_analysis / newton — the gravity sector
13. neutrino_closure — the neutrino sector
14. qcd_sector / discrete_flow — the QCD sector and the
    discrete-flow structure (B-level)

Every module runs as __main__ (its own smoke); the script reports
the final closure table from the store.
"""

from __future__ import annotations

import os
import subprocess
import sys
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
_PY = sys.executable

# The module list in dependency order (each runs its own __main__).
MODULES = [
    "scripts/init_v4.py",
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
    # coefficients (the L3 closure, 2026-08-21): a verification module whose
    # self-test asserts every factor (v, m_nu3, T_d, Delta2_R, m_p, alpha_s,
    # rho_Lambda) and the conservation laws to machine precision.
    "cg_frg/ewsb/squash_level_transfer.py",
    "cg_frg/cosmology/spectral_tilt.py",
    "cg_frg/cosmology/dark_energy.py",
    "cg_frg/cosmology/perturbation_amplitude.py",
    "cg_frg/generation/sector_alpha.py",
    "cg_frg/generation/lz_ladder.py",
    "cg_frg/generation/lz_dynamics.py",
    "cg_frg/fermion/mass_operator_overlap.py",
    "cg_frg/gravity/zk_gravitational_rg.py",
    "cg_frg/ewsb/order_parameter.py",
    "cg_frg/ewsb/pseudo_dilaton.py",
    "cg_frg/gauge/geometric_ewsb.py",
    "cg_frg/gravity/tt_tensor.py",
    "cg_frg/gravity/pole_analysis.py",
    "cg_frg/gravity/chi_pole_condition.py",
    "cg_frg/gravity/newton.py",
    "cg_frg/neutrino/neutrino_closure.py",
    "cg_frg/neutrino/neutrino_mass_matrix.py",
    "cg_frg/fermion/electron_mass.py",
    "cg_frg/framework/five_items.py",
    "cg_frg/framework/cp_sector.py",
    "cg_frg/frg/trace_density.py",
    "cg_frg/qcd/mass_gap_scale.py",
    "cg_frg/qcd/qcd_sector.py",
    "cg_frg/cosmology/bbn_helium.py",
    "cg_frg/ewsb/ew_precision.py",
    "cg_frg/ewsb/ew_one_loop.py",
    "cg_frg/cosmology/gw_ratio.py",
    "cg_frg/cosmology/endpoint_residual.py",
    "cg_frg/framework/sigma_language.py",
    "cg_frg/frg/discrete_flow.py",
    "cg_frg/gauge/gauge_group_emergence.py",
]

# The closure table: (label, store key, observed, comparison flag).
CLOSURES = [
    ("kL* (F_MG fixed point)", "kL", None),
    ("M_G (emergence scale)", "M_G", None),
    ("g2(M_G) geometric", "g2_MG", 0.50885),
    ("n_generations", "n_generations", 3),
    ("m_t/m_c", "m_t_over_m_c", 136.0),
    ("m_b/m_s", "m_b_over_m_s", 45.0),
    ("m_t/m_u", "m_t_over_m_u", 78000.0),
    ("epsilon (dilaton line)", "epsilon_dilaton", 1.4243e-16),
    ("v_HIGGS (GeV)", "v_HIGGS", 246.22),
    ("1 - n_s", "ns_tilt", 0.0351),
    ("Lambda (GeV^2)", "Lambda", 4.279e-84),
    ("TT slope_G", "TT_slope_G", None),
    ("TT delta pole", "TT_delta_forming", True),
    ("m_nu3 (eV)", "m_nu3", 0.0502),
    ("m_nu2 rest (eV)", "m_nu2", None),
    ("Delta m21^2 osc", "Delta_m21_sq_osc", 7.41e-5),
    ("Delta m31^2", "Delta_m31_sq", 2.511e-3),
    ("sin^2 theta12", "sin2_theta12", None),
    ("m_t (GeV)", "m_t_pred", 172.69),
    ("m_e (MeV)", "m_e_pred", 0.511),
    ("Delta2_R", "perturbation_amplitude", 2.105e-9),
    ("m_glueball (GeV)", "m_glueball", 1.7),
    ("mass gap dE/M_G", "mass_gap_dE", None),
    ("H0 (GeV)", "H0_GEV", 1.44e-42),
    ("M_Z (GeV)", "M_Z_pred", 91.1876),
    ("M_W (GeV)", "M_W_pred", 80.369),
    ("M_W lead-univ (GeV)", "M_W_pred_lead1loop", 80.369),
    ("Gamma_b 1-loop (GeV)", "Gamma_b_pred_1loop", 0.37705),
    ("Gamma_Z (GeV)", "Gamma_Z_pred", 2.4952),
    ("sigma_had (nb)", "sigma_had_pred", 41.481),
    ("m_H (GeV)", "m_H_pred", 125.20),
    ("r (GW tensor ratio)", "gw_ratio", None),
    ("Omega_Sigma", "Omega_Sigma", None),
    ("C_gamma", "photon_zero_mode_Cgamma", None),
    ("T_CMB corrected (K)", "T_CMB_corrected_K", 2.72548),
    ("endpoint z_eq", "endpoint_z_eq", 3402.0),
    ("endpoint r_drag", "endpoint_r_drag_Mpc", 147.09),
    ("endpoint sigma8", "endpoint_sigma8", 0.8111),
    ("endpoint S8", "endpoint_S8", 0.832),
    ("2L = sqrt(2pi)", "twoL_entropy_min_distance", None),
    ("alpha_up (internal)", "alpha_up", 2.456327),
    ("alpha_dn (internal)", "alpha_down", 1.903331),
    ("alpha_lp (internal)", "alpha_lepton", 1.410689),
    ("sector step Delta", "sector_alpha_delta", 0.5225),
    ("sin^2 theta(M_Z)", "s2_thetaW_MZ", 0.23122),
    ("sin^2 theta_eff^l", "sin2_theta_eff_l_pred", 0.23153),
    ("m_tau (GeV)", "m_tau_pred", 1.777),
    ("order parameter lambda", "order_parameter_lambda", None),
    ("Z quantum shift", "Z_quantum_shift", None),
    ("m_WR (GeV)", "geometric_ewsb_m_WR", None),
]


def run_all() -> list:
    """Run every module in order; collect the failures."""
    failures = []
    for mod in MODULES:
        print(f"\n── {mod} ──")
        r = subprocess.run([_PY, str(_PROJECT_ROOT / mod)],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        for line in out.splitlines():
            print("  " + line)
        if r.returncode != 0:
            failures.append(mod)
    return failures


def summary() -> None:
    """The final closure table from the store."""
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    from cg_core.params import get

    print("\n" + "=" * 66)
    print("  V4 CLOSURE TABLE")
    print("=" * 66)
    print(f"  {'quantity':24s} {'value':>14s} {'observed':>12s} {'dev':>8s}")
    for label, key, obs in CLOSURES:
        try:
            val = get(key)
        except KeyError:
            print(f"  {label:24s} {'MISSING':>14s}")
            continue
        if isinstance(val, float) and obs:
            dev = (val / obs - 1.0) * 100.0
            print(f"  {label:24s} {val:14.6g} {obs:12g} {dev:+7.3f}%")
        else:
            print(f"  {label:24s} {str(val):>14s} {str(obs):>12s}")


def main() -> int:
    failures = run_all()
    summary()
    if failures:
        print(f"\nFAILED MODULES ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nALL MODULES PASSED — the V4 chain is reproduced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
