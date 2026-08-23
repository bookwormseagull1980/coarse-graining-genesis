<!--
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
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
-->

# V4 Verification Report

Generated: 2026-08-23 11:26:16
Python: `3.12.13`
Root: `.`

## Verdict

PASS

## Fresh Rebuild

Removed generated stores:
- `cg_params.json`
- `comparison/sm_inputs.json`
- `params_write_log.json`

## Steps

| step | status | seconds | command |
|---|---:|---:|---|
| full reproduction | PASS | 68.4 | `python scripts/reproduce_v4.py` |
| parameter provenance audit | PASS | 0.4 | `python scripts/audit_param_writers.py` |
| observation leakage audit | PASS | 2.9 | `python scripts/audit_observation_leakage.py` |
| Lean source audit | PASS | 0.5 | `python scripts/audit_lean_sources.py` |
| numeric precision audit | PASS | 2.9 | `python scripts/audit_numeric_precision.py` |
| path portability audit | PASS | 0.5 | `python scripts/audit_path_portability.py` |
| full comparison table | PASS | 76.6 | `python comparison/param_audit_full.py` |
| pytest | PASS | 83.6 | `python -m pytest -q -p no:cacheprovider` |
| Lean proof archive | PASS | 41.2 | `python scripts/verify_lean_archive.py --lean-exe <lean.exe>` |
| numeric stability audit | PASS | 84.9 | `python scripts/audit_numeric_stability.py` |

### Store Summary

- cg_params records: 184
- sm_inputs comparison records: 90
- provenance: DERIVED=182, OBSERVED=1, SCALE_CHOICE=1
- roles: anchor=1, cg=22, comparison=15, informational=11, internal=135

### Selected Closed Values

| key | value | provenance | writer |
|---|---:|---|---|
| `kL` | `2.4935343325226915` | DERIVED | `cg_frg/frg/endpoint_constraint.py` |
| `M_G` | `1.7310765000475023e+18` | DERIVED | `cg_frg/frg/endpoint_constraint.py` |
| `g2_MG` | `0.5088477031823814` | DERIVED | `cg_frg/gauge/geometric_couplings.py` |
| `g1_MG_geo` | `0.6049900729523602` | DERIVED | `cg_frg/gauge/geometric_couplings.py` |
| `g3_MG_geo` | `0.49775991624706845` | DERIVED | `cg_frg/gauge/geometric_couplings.py` |
| `n_generations` | `3` | DERIVED | `cg_frg/generation/window_capacity.py` |
| `v_HIGGS` | `246.18969645238943` | DERIVED | `cg_frg/ewsb/vev_closure.py` |
| `M_Z_pred` | `91.12426592764405` | DERIVED | `cg_frg/ewsb/ew_precision.py` |
| `M_W_pred` | `80.37122117213354` | DERIVED | `cg_frg/ewsb/ew_precision.py` |
| `M_W_pred_lead1loop` | `80.3368679947019` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `Gamma_b_pred_1loop` | `0.3784099335475641` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `sin2_theta_eff_l_pred` | `0.2301139784749636` | DERIVED | `cg_frg/ewsb/ew_one_loop.py` |
| `m_H_pred` | `124.98344026878286` | DERIVED | `cg_frg/ewsb/ew_precision.py` |
| `Omega_Lambda` | `0.6850442965140158` | DERIVED | `cg_frg/cosmology/dark_energy.py` |
| `Omega_Sigma` | `0.2657026396202929` | DERIVED | `cg_frg/cosmology/endpoint_residual.py` |
| `T_CMB_GeV` | `2.353400743797703e-13` | DERIVED | `cg_frg/cosmology/dark_energy.py` |
| `T_CMB_corrected_K` | `2.725473977921092` | DERIVED | `cg_frg/cosmology/endpoint_residual.py` |
| `endpoint_sigma8` | `0.8142304448760495` | DERIVED | `cg_frg/cosmology/endpoint_residual.py` |
| `endpoint_S8` | `0.8342792621089947` | DERIVED | `cg_frg/cosmology/endpoint_residual.py` |
| `bbn_Neff` | `3.043873359487886` | DERIVED | `cg_frg/cosmology/bbn_helium.py` |

## Command Output

### full reproduction

```text
 m_W  = g2 v/2 = 62.64 GeV
  m_WR/m_W = 5.625e+14
  m_W/m_WR = epsilon/(2 s0) = 1.778e-15 — CLOSED
    1/(2 s0) = 12.5000 (exact)
    with g_w(M_Z): 2.247e-15
  kappa2 = g1/g2 = 1.13183
  geometric_ewsb OK

── cg_frg/gravity/tt_tensor.py ──
  slope_G = -2.000, slope_Z = -0.0000, delta pole: True
  n_grav = 0 (no TT zero mode; the pole is spectral)
  tt_tensor OK

── cg_frg/gravity/pole_analysis.py ──
  spectral_positive=True, pole_stable=True, matter_is_small=True, stable=True
  pole_analysis OK

── cg_frg/gravity/chi_pole_condition.py ──
  chi_crossing = 0.657225  (alpha = 2.0)
  x(0) = 0.1007 < 1,  x(2) = 27.3 (unbounded)
  robustness (alpha -> chi_c): {'1.0': 1.3144, '1.5': 0.8763, '2.0': 0.6572, '2.5': 0.5258, '3.0': 0.4381}
  trajectory:
    chi=0.0  V_TT=3.2919e-01  Pi2=3.057737e-01  x=0.1007
    chi=0.2  V_TT=6.8186e-01  Pi2=3.153343e-01  x=0.2150
    chi=0.4  V_TT=1.3494e+00  Pi2=3.231610e-01  x=0.4361
    chi=0.6  V_TT=2.5443e+00  Pi2=3.292539e-01  x=0.8377
    chi=0.8  V_TT=4.5771e+00  Pi2=3.338272e-01  x=1.5279
    chi=1.0  V_TT=7.8895e+00  Pi2=3.371759e-01  x=2.6601
    chi=1.5  V_TT=2.6639e+01  Pi2=3.419835e-01  x=9.1101
    chi=2.0  V_TT=7.9344e+01  Pi2=3.440540e-01  x=27.2988
  chi_pole_condition OK

── cg_frg/gravity/newton.py ──
  Z_phys(M_G) = 1.000000 (matter back-reaction tiny; sigma = 1.214e+00 GeV^2)
  G_N = 6.708830e-39 GeV^-2 vs PDG (-0.0000%).  G_N = 1/(8pi M_P^2) is the identity, reproducing PDG exactly with the anchor M_P = 1/sqrt(8pi G_N_PDG); Z_phys = 1 confirms the matter back-reaction is negligible
  newton OK

── cg_frg/neutrino/neutrino_closure.py ──
  m_nu3 = 0.0502 eV (Weinberg)
  m_nu2 = 0.0087 eV (hypercharge trace)
  sin^2 theta12 = m1/m2 = 0.30
  hierarchy: m1/m2 = 0.300, m2/m3 = 0.1732
  PMNS: s12 = 0.300, s23 = 0.5507, s13 = 0.0219
  first-gen: m_d/m_s = 0.05015, m_u/m_c = 0.001849
  |V_us| = sqrt(md/ms) = 0.2239; full Gatto = 0.1820
  boundary: the PMNS angles are the neutrino mass-matrix structure (the hypercharge trace hierarchy sin2(theta12)=m1/m2=3/10 + the 2pi imprint for theta13/theta23)
  neutrino_closure OK

── cg_frg/neutrino/neutrino_mass_matrix.py ──
  hierarchy eigenvalues (m3:m2:m1) = 1.0000 : 0.1732 : 0.0520
  r12 (m1/m2) derived = 0.3000000000  vs 1/Tr(Y^2) = 3/10  (+1.55e-13%)
  r23 (m2/m3) derived = 0.1732050808  vs 1/(sqrt3 Tr(Y^2))  (-3.33e-14%)
  m3 = 0.2393 eV, m2 = 0.0415 eV, m1 = 0.0124 eV
  PMNS |U_e2|^2 = 0.2934 (s12^2 = m1/m2 = 3/10 target)
  neutrino_mass_matrix OK

── cg_frg/fermion/electron_mass.py ──
  m_e = M_P e^(-20 kL) = 0.510 MeV
  cascade: m_e = y_0 O_e v_dil(e)/sqrt(2) ≡ M_P e^{-20kL}(1-s0k) — the cascade form at the electron-scale dilaton VEV v_dil(e) = M_P e^{-20kL} sqrt2 (1-s0k)/(y0 O_e), the 4x5 cascade compressed (exact, 2026-08-18)
  electron_mass OK

── cg_frg/framework/five_items.py ──
    ITEM 1 — 3 generations (n = {0,2,4}): CLOSED-formal = 3
    ITEM 2 — the branch choice (hypercharge B' vs C'): recorded
    ITEM 3 — 2L = sqrt(2pi): CLOSED
    ITEM 4 — the two v-paths (the factor-2 unification): CLOSED = 246.18969645238943
    ITEM 5 — the m_e: CLOSED-near
  closed: 4/5 (item 2 recorded, item 5 near)
  five_items OK

── cg_frg/framework/cp_sector.py ──
  n_L/n_R = 8/7 = 1.142857
  delta_PMNS/pi ~ (8/7) = 1.142857
  eta_B = J alpha_W^2/56 = 6.091e-10 (Sakharov content)
  cp_sector OK

── cg_frg/frg/trace_density.py ──
  trace_density(M_G) = 8.0172e-37 GeV^4, sigma = |td|/M_P^2 = 1.352e-73 GeV^2
  trace_density OK

── cg_frg/qcd/mass_gap_scale.py ──
  Delta E = (1/8) M_G = 2.164e+17 GeV = 0.125 x M_G
  m_gen = 2.491e+16 GeV (the QCD initial condition)
  m_glueball = 1.7 GeV
  mass_gap_scale OK

── cg_frg/qcd/qcd_sector.py ──
  PART 1: dE = (1/8)M_G = 2.164e+17, m_gen = 2.491e+16
          Lambda_QCD = 0.207 GeV
          m_glueball = 1.7 GeV
  PART 2: lambda_glue = 8/L^2 = 1.286647 > 0 (the l=2 gap level)
  PART 3: tower ratios: 0++ 1.000, 2++ 1.414, 0++* 1.500, 0-+ 1.458
  PART 4: string tension = (14/pi) Lambda^2 = 0.1917 GeV^2
  PART 5: m_p = (279/64) Lambda_QCD = 0.9382 GeV (constituent quark)
  qcd_sector OK

── cg_frg/cosmology/bbn_helium.py ──
  G_F  = 1.1667e-05 GeV^-2
  dm_np = 1.2890 MeV, T_f = 0.7532 MeV
  tau_n = 897.1 s, t_decay = 204.9 s
  Y_p = 0.2514, N_eff = 3.0439
  bbn_helium OK (nuclear constants derived from v/M_P/m_e/ladder)

── cg_frg/ewsb/ew_precision.py ──
  ========================================================================
    V4 ELECTROWEAK PRECISION OBSERVABLES (M_G -> M_Z block)
  ========================================================================
    internal M_Z (self-consistent two-loop) = 91.1243 GeV   (obs 91.1876, -0.069%)
    alpha(M_Z)^-1 (self-consistent)          = 128.2077   (store 128.2085, cross -0.0006%)
    s^2(M_Z) (MS-bar-like)                   = 0.233275   (obs 0.23122, +0.889%)
    M_W (on-shell, Delta rho one-loop)       = 80.3712 GeV   (obs 80.369, +0.003%)
    s^2_W (on-shell)                         = 0.222083   (obs 0.223207, -0.503%)
    rho parameter (improved Born)               = 1.009510   (SM 1/(1-Delta rho_SM) = 1.009356, +0.015%)
    Gamma_Z                                  = 2.4798 GeV   (obs 2.4952, -0.619%)
    Gamma_had                                = 1.7331 GeV   (obs 1.7444, -0.649%)
    Gamma_b                                  = 0.3808 GeV   (obs 0.3770, +1.000%)
    Gamma_l (e+mu+tau)                       = 0.2499 GeV   (obs 0.2519, -0.776%)
    Gamma_inv (3 nu)                         = 0.4967 GeV   (obs 0.4990, -0.454%)
    sigma_had^0                              = 41.510 nb   (obs 41.481, +0.070%)
    R_l                                      = 20.802   (obs 20.767, +0.168%)
    R_b                                      = 0.21974   (obs 0.21629, +1.593%)
    m_H (tree, sqrt(2 lambda_H) v)         = 124.983 GeV   (obs 125.20, -0.173%)
    m_mu / m_tau (internal ladder)           = 105.31 MeV / 1.7721 GeV   (obs 105.66 MeV / 1.777 GeV)
  ------------------------------------------------------------------------
    formula check (SM inputs, Delta r_rem omitted): M_W = 80.404 GeV
      (the known full one-loop SM result is ~80.36 GeV; the +0.04 GeV is the omitted Delta r_rem)
  ew_precision OK

── cg_frg/ewsb/ew_one_loop.py ──
  ========================================================================
    V4 ONE-LOOP EW COMPLETION
  ========================================================================
    M_W lead-univ     = 80.3369 GeV
    Gamma_b 1-loop    = 0.37841 GeV
    Delta_b top       = -0.0063326 (-0.633%)
    sin2 theta_eff^l  = 0.230114
    formula check (SM inputs):
      M_W lead-univ = 80.369 GeV (exp 80.369)
      top vertex    = -0.62%
  ew_one_loop OK

── cg_frg/cosmology/gw_ratio.py ──
  r        = 0.02533
  Delta2_t = 5.322e-11
  2L       = 2.506628  (kL vs 2L: -0.522%)
  H0       = 1.4388e-42 GeV (cross-check +0.000%)
  sigma_C  = 6.9500e+41 GeV^-1
  gw_ratio OK

── cg_frg/cosmology/endpoint_residual.py ──
  Omega_Sigma = 0.265702639620
  Omega_m     = 0.314955703486
  C_gamma     = 0.997973576327
  T_CMB corr  = 2.725474 K
  endpoint_residual OK

── cg_frg/framework/sigma_language.py ──
  sigma(M_G)  = 5.7768e-19 GeV^-1
  sigma_C     = c/H0 = 6.9500e+41 GeV^-1 (the IR anchor)
  T_eff(M_G)  = k/(2pi) = 2.7551e+17 GeV
  k*sigma(k)  = 1.0000000000 = c = 1
  L(k)        = kL*c = 2.493534 (the window constant)
  sigma_language OK

── cg_frg/frg/discrete_flow.py ──
  semigroup check    = 1.11e-16 (machine-precision)
  beta(M_G)          = 1.037e+55 (the analytic closed form)
  window step dlnσ   = 0.4010  (N steps M_P->sigma_C = 346)
  tachyon m2_long    = -2.5197 < 0 (the trigger)
  m_gen^2            = 6.207e+32 GeV^2 > 0, lambda_J2 = 14.1608 > 0 — the gap
  tower ratios       = 0++ 1.00, 2++ 1.41, 0++* 1.50, 0-+ 1.46
  discrete_flow OK

── cg_frg/gauge/gauge_group_emergence.py ──
    SO(4) isometry: SU(2)_L x SU(2)_R (6 Killing vectors of S^3, Z_2-quotiented to RP^3)
    SU(2)_L: the 3 even (untwisted) generators — the weak isospin
    SU(2)_R: the 3 odd (twisted) generators — broken by the geometric isometry breaking (EWSB)
    U(1)_Y: the diagonal generator of the chirality layers (SU(2)_R -> U(1)_Y by the long-root condensate)
    SU(3)_c: the composite of the two su(2) blocks with the long-root coupling (the A_2 root system) — the coupling is CLOSED via g3 = g2*(1+alpha_GUT^2/K)
    couplings:
      g2: CLOSED (the KV normalisation, geometric_couplings)
      g1: CLOSED (g1 = g2*kappa, the squash mixing)
      g3: CLOSED (g3 = g2*(1+alpha_GUT^2/K) at k_GUT, the long-root bifurcation — the two su(2) blocks share the Killing normalisation at order alpha^0, the long-root E_{±(alpha_1+alpha_2)} carries the alpha^2/K correction with K = 8/3)
  gauge_group_emergence OK

==================================================================
  V4 CLOSURE TABLE
==================================================================
  quantity                          value     observed      dev
  kL* (F_MG fixed point)   2.4935343325226915         None
  M_G (emergence scale)    1.7310765000475023e+18         None
  g2(M_G) geometric              0.508848      0.50885  -0.000%
  n_generations                         3            3
  m_t/m_c                         135.242          136  -0.557%
  m_b/m_s                         44.8679           45  -0.293%
  m_t/m_u                         77303.6        78000  -0.893%
  epsilon (dilaton line)      1.42218e-16   1.4243e-16  -0.149%
  v_HIGGS (GeV)                    246.19       246.22  -0.012%
  1 - n_s                           0.035       0.0351  -0.285%
  Lambda (GeV^2)              4.25472e-84    4.279e-84  -0.567%
  TT slope_G               -1.9999999999999933         None
  TT delta pole                      True         True
  m_nu3 (eV)                    0.0501797       0.0502  -0.040%
  m_nu2 (eV)                   0.00869138       0.0086  +1.063%
  sin^2 theta12                       0.3        0.303  -0.990%
  m_t (GeV)                       174.082       172.69  +0.806%
  m_e (MeV)                      0.510354        0.511  -0.126%
  Delta2_R                    2.10111e-09    2.105e-09  -0.185%
  m_glueball (GeV)                1.65904          1.7  -2.409%
  mass gap dE/M_G          2.163845625059378e+17         None
  H0 (GeV)                    1.43885e-42     1.44e-42  -0.080%
  M_Z (GeV)                       91.1243      91.1876  -0.069%
  M_W (GeV)                       80.3712       80.369  +0.003%
  M_W lead-univ (GeV)             80.3369       80.369  -0.040%
  Gamma_b 1-loop (GeV)            0.37841      0.37705  +0.361%
  Gamma_Z (GeV)                   2.47976       2.4952  -0.619%
  sigma_had (nb)                  41.5102       41.481  +0.070%
  m_H (GeV)                       124.983        125.2  -0.173%
  r (GW tensor ratio)      0.025330295910584444         None
  Omega_Sigma              0.2657026396202929         None
  C_gamma                  0.9979735763271532         None
  T_CMB corrected (K)             2.72547      2.72548  -0.000%
  endpoint z_eq                   3414.88         3402  +0.379%
  endpoint r_drag                  146.98       147.09  -0.075%
  endpoint sigma8                 0.81423       0.8111  +0.386%
  endpoint S8                    0.834279        0.832  +0.274%
  2L = sqrt(2pi)           2.5066282746310002         None
  alpha_up (internal)             2.45353      2.45633  -0.114%
  alpha_dn (internal)             1.90186      1.90333  -0.077%
  alpha_lp (internal)             1.41149      1.41069  +0.057%
  sector step Delta              0.521024       0.5225  -0.282%
  sin^2 theta(M_Z)               0.233275      0.23122  +0.889%
  sin^2 theta_eff^l              0.230114      0.23153  -0.612%
  m_tau (GeV)                     1.77211        1.777  -0.275%
  order parameter lambda   149.1452591486519         None
  Z quantum shift          0.006150176028383747         None
  m_WR (GeV)               3.5234172043286684e+16         None

ALL MODULES PASSED — the V4 chain is reproduced.
```

### parameter provenance audit

```text
AUDIT CLEAN: all parameters carry provenance/writer/note; every DERIVED names a module.
```

### observation leakage audit

```text
OBSERVATION-LEAKAGE AUDIT CLEAN
  explicit observation-access calls: 62
    3 allowed as SM comparison-table construction
    7 allowed as compare_and_set observed target
    8 allowed as comparison package
   44 allowed as formula check / printout only
  no observed-value access was found in an unapproved prediction context.
```

### Lean source audit

```text
LEAN SOURCE AUDIT CLEAN
  files scanned: 20
  no sorry/admit/axiom/unsafe/opaque tokens in executable Lean code
  no interactive output commands
  no Mathlib imports
```

### numeric precision audit

```text
NUMERIC PRECISION AUDIT CLEAN
  python files scanned: 88
  no rounded/formatted values are written to parameter stores
  non-informational numeric records are JSON numbers, not strings
  numeric cg_params records: 162
  high-fanout stored values use round-trip representations:
    G_N_PDG: 6.70883e-39  downstream=185
    L_Cg: 1.7724538509055159  downstream=185
    M_P: 2.435323595526305e+18  downstream=185
    kL: 2.4935343325226915  downstream=185
    tau: 0.02  downstream=185
    M_G: 1.7310765000475023e+18  downstream=147
    v_HIGGS: 246.18969645238943  downstream=122
    k_GUT: 4.984263355588678e+16  downstream=112
    kL_CMB: 2.481066660860078  downstream=102
    ns_tilt: 0.035  downstream=102
    alpha_down: 1.9018618632255682  downstream=90
    g1_MG_geo: 0.6049900729523602  downstream=85
    g2_MG: 0.5088477031823814  downstream=85
    alpha_up: 2.4535343325226915  downstream=83
    g3_MG_geo: 0.49775991624706845  downstream=82
    m_glueball: 1.6590414836759542  downstream=66
    mass_gap_dE: 2.163845625059378e+17  downstream=66
    mass_gap_m_gen: 2.4914321981301484e+16  downstream=66
    qcd_Lambda_QCD: 0.20738018545949427  downstream=66
    alpha_lepton: 1.4114863349614586  downstream=38
    R_c_star: 1.909859317102744  downstream=36
    entropy_integral: 139.2537061093592  downstream=35
    md_over_ms_geo: 0.05014715428586189  downstream=35
    m_mu_over_m_e: 206.3556103933899  downstream=32
    V_us_geo: 0.22393560298858664  downstream=30
    alpha_inv_MZ_pred: 128.2085016245155  downstream=30
    m_b_over_m_s: 44.86794977784708  downstream=30
    m_b_pred: 4.237792000302189  downstream=30
    m_e_pred: 0.5103542513564916  downstream=30
    m_s_over_m_d: 19.622983487591103  downstream=30
```

### path portability audit

```text
PATH PORTABILITY AUDIT CLEAN
  files scanned: 29
  no machine-local absolute paths in reviewer-facing sources/artifacts
```

### full comparison table

```text
== recomputing the full chain (reproduce_v4) ==
fresh store reset: cg_params.json, comparison/sm_inputs.json, params_write_log.json
reproduce exit=0  passed=True

==========================================================================
  quantity                    predicted     observed       dev
==========================================================================
  g2(M_G)                      0.508848     0.508845   +0.001%
  g2(M_G) geometric            0.510601     0.508845   +0.345%
  g1(M_G)                       0.60499     0.605001   -0.002%
  g3(M_G)                       0.49776     0.497765   -0.001%
  g3 GUT (common origin)        0.51842      0.51848   -0.012%
  alpha_s(M_Z)                 0.117986       0.1179   +0.073%
  alpha_em(M_Z) inv             128.209       127.95   +0.202%
  n_generations                       3            3   +0.000%
  m_t/m_c                       135.242          136   -0.557%
  m_b/m_s                       44.8679           45   -0.293%
  m_t/m_u                       77303.6        78000   -0.893%
  m_t (GeV)                     174.082       172.69   +0.806%
  m_b (GeV)                     4.23779         4.18   +1.383%
  m_e (MeV)                    0.510354        0.511   -0.126%
  m_mu/m_e                      206.356        206.8   -0.215%
  m_d/m_s                     0.0501472       0.0505   -0.699%
  m_s/m_d                        19.623         19.8   -0.894%
  m_p (GeV)                    0.938156     0.938272   -0.012%
  epsilon (dilaton)         1.42218e-16   1.4243e-16   -0.149%
  v_HIGGS (GeV)                  246.19       246.22   -0.012%
  M_Z (GeV)                     91.1243      91.1876   -0.069%
  M_W Born+rho (GeV)            80.3712       80.369   +0.003%
  M_W lead-univ (GeV)           80.3369       80.369   -0.040%
  Gamma_Z (GeV)                 2.47976       2.4952   -0.619%
  Gamma_b Born (GeV)           0.380822      0.37705   +1.000%
  Gamma_b 1-loop (GeV)          0.37841      0.37705   +0.361%
  sigma_had (nb)                41.5102       41.481   +0.070%
  m_H (GeV)                     124.983        125.2   -0.173%
  sin^2 thetaW(M_Z)            0.233275      0.23122   +0.889%
  sin^2 theta_eff^l            0.230114      0.23153   -0.612%
  m_nu3 (eV)                  0.0501797       0.0502   -0.040%
  m_nu2 (eV)                 0.00869138       0.0086   +1.063%
  m_nu1 (eV)                 0.00260742       0.0026   +0.285%
  sin^2 theta12                     0.3          0.3   -0.000%
  sin^2 theta13               0.0219367        0.022   -0.288%
  sin^2 theta23                0.550661         0.55   +0.120%
  delta_CKM (deg)               68.5714         68.5   +0.104%
  Jarlskog J                3.15026e-05     3.06e-05   +2.950%
  V_us                         0.223936       0.2245   -0.251%
  eta_b                     6.09089e-10      6.1e-10   -0.149%
  1 - n_s                         0.035       0.0351   -0.285%
  Delta2_R                  2.10111e-09    2.105e-09   -0.185%
  Lambda (GeV^2)            4.25472e-84  4.27911e-84   -0.570%
  H0 (GeV)                  1.43885e-42     1.44e-42   -0.080%
  Omega_Lambda                 0.685044       0.6847   +0.050%
  Omega_b                     0.0492531       0.0493   -0.095%
  Omega_DM                     0.265703       0.2645   +0.455%
  T_CMB (K)                     2.73101       2.7255   +0.202%
  a0 MOND (m/s^2)           1.20437e-10      1.2e-10   +0.364%
  gw ratio r                  0.0253303      <=0.036 OK (<= bound)
  Lambda_QCD (GeV)              0.20738         0.21   -1.248%
  string tension (GeV^2)       0.191652       0.1936   -1.006%
  T_deconf (MeV)                270.248          270   +0.092%
  m_glueball (GeV)              1.65904          1.7   -2.409%
  Y_p (BBN)                    0.251365        0.245   +2.598%
  N_eff (BBN)                   3.04387        3.044   -0.004%
==========================================================================
  56 observables compared; all DERIVED (no fitting).
```

### pytest

```text
........................................................................ [ 93%]
.....                                                                    [100%]
```

### Lean proof archive

```text
LEAN ARCHIVE VERIFY CLEAN
  lean source: --lean-exe
  version: Lean (version 4.7.0, x86_64-w64-windows-gnu, commit 6fce8f7d5cd1, Release)
  files compiled: 20
  trust level: 0
  strict output: yes
  seconds: 40.4
```

### numeric stability audit

```text
NUMERIC STABILITY AUDIT CLEAN
  command: python scripts/reproduce_v4.py
  removed stores: cg_params.json, comparison/sm_inputs.json, params_write_log.json
  cg_params.json: 184 stable records
  comparison/sm_inputs.json: 90 stable records
  seconds: 84.3
```
