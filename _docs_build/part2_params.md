<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China

Part of the V4 spectral framework, whose physics is presented in the
companion papers:
  [I]  "The spectrum of a compact internal space.
        I. Gauge structure and fermion content"
  [II] "The spectrum of a compact internal space.
        II. Effective couplings and mass scales"
-->

# Part 2 V4 parameter-by-parameter analysis

> This part analyses the 170 closed parameters one by one, in **dependency order** and by **sector**. Each physical quantity is given: **physical-quantity description, motivation principle, analytic computation formula and method**. The parameter table is generated programmatically from `cg_params.json` (DERIVED/OBSERVED annotation + derivation-chain note), with no manual transcription error.

---

## Chapter 12 Parameter overview: 170 parameters, 10 sectors, 45 modules

### 12.1 The panorama

The V4 parameter store `cg_params.json` has **170 keys**: 169 DERIVED (internally computed) + 1 OBSERVED (`G_N_PDG`, the single observational anchor). All DERIVED parameters carry provenance/writer/note (derivation chain).

![Figure 4: the 40-module dependency order](figures/fig04_modules.png)

![Figure 3: the dimensional anchor chain](figures/fig03_dimensional_chain.png)

### 12.2 Execution order (the 45 chain items of reproduce_v4.py)

```
init_v4 → run_rge → spectrum_loop → sm_content → cluster_decay → spectral_sum
→ endpoint_constraint → vev_closure → gamma_M → ir_flow → geometric_couplings
→ crosschecks → window_capacity → relaxion_chain → relaxion_geo → epsilon_ratio
→ spectral_tilt → dark_energy → perturbation_amplitude → sector_alpha → lz_ladder
→ lz_dynamics → zk_gravitational_rg → order_parameter → pseudo_dilaton
→ geometric_ewsb → tt_tensor → pole_analysis → chi_pole_condition → newton
→ neutrino_closure → neutrino_mass_matrix → mass_operator_overlap → electron_mass
→ five_items → cp_sector → trace_density → mass_gap_scale → qcd_sector
→ bbn_helium → ew_precision → gw_ratio → sigma_language → discrete_flow
→ gauge_group_emergence
```

### 12.3 Sector division

| Sector | modules | core physical quantities |
|---|---|---|
| 0 anchor/seeds | init_v4 | M_P, tau, L_Cg, k_GUT |
| 1 SM running table | run_rge, spectrum_loop, sm_content | SM comparison table, field content, hypercharge statistics |
| 2 FRG flow | spectral_sum, endpoint_constraint, gamma_M, ir_flow, trace_density, discrete_flow | kL, M_G, entropy integral, trace density |
| 3 gauge | geometric_couplings, geometric_ewsb, gauge_group_emergence | g₁ g₂ g₃, W_R scale |
| 4 generation | window_capacity, sector_alpha, lz_ladder | 3 generations, sector α, mass ratios |
| 5 electroweak | vev_closure, relaxion_chain, relaxion_geo, epsilon_ratio, order_parameter, pseudo_dilaton, ew_precision | v, ε, order parameter, pseudo-dilaton |
| 6 cosmology | spectral_tilt, dark_energy, bbn_helium, perturbation_amplitude, gw_ratio | n_s, Λ, H0, Ω, T_CMB |
| 7 gravity | tt_tensor, pole_analysis, chi_pole_condition, newton, zk_gravitational_rg | G_N, Z_phys, TT pole |
| 8 flavour/fermion | neutrino_closure, mass_operator_overlap, electron_mass | neutrino masses, m_t, m_e |
| 9 framework layer | five_items, cp_sector, sigma_language | CP, η_B, σ language |
| 10 QCD | mass_gap_scale, qcd_sector | Λ_QCD, glueball, confinement |

### 12.4 All closed (the EC field-equation variation is completed)

> The framework's symmetries are **all closed** — the first-principles proofs of the following items are all completed (reproduce_v4 exit 0 + Lean 4 exit 0), **no open item**:

| Item | modules involved | proof mechanism |
|---|---|---|
| τ theorem (EC-torsion first principles) | sm_content / ec_structure | the window capacity 2πkL⁴ cancels exactly → τ = 1/50 EXACT |
| s0/N_R = 1/175 field equation | squash correction system | pure content ratio, one half of the J=2 first-order torsion (factor 2=(d+1)/2) |
| the κ² of g₁ | geometric_couplings | conformal-gauge duality N_g·ξ=1 (5/8 = ΣY²·Δ_f·ξ) |
| the α²/K of g₃ | geometric_couplings | K = J(J+2)/d = 8/3 geometric-dynamics origin |
| the λ quartic | order_parameter | stationarity ∂V/∂φ=0 self-consistency + EC-torsion algebra (b=4a) |
| squash sign/multiple assignment | SQUASH_SYMMETRY | pairing conservation locks the signs |
| d=N_c=3 | conformal-gauge duality | the unique positive solution of N_g·ξ=1 |
| N_L=N_g | fermion content | Lean 9 theorems proved (fermion_content.lean) |
| \|V_us\|\|V_cb\|\|V_ub\| = α_W³ | cp_sector | CLOSED (−0.09%), η_B=α_W⁵ sphaleron standard rate |

**All closed, none open.**

---

## Chapter 13 Sectors 0–2: anchor, SM running table, FRG flow

### 13.1 init_v4.py — anchor and seeds

**Motivation**: the V4 rebuild is a fresh start — the parameter store is created from the framework's anchor values + the SM comparison table, then the foundation chain runs in dependency order.

**Anchor values** (external, comparison only):
- M_P = 1/√(8πG_N) = 2.4353e18 GeV (the reduced Planck mass, the identity from the observed G_N)
- tau = 0.02 (the torsion modulus, the chiral-asymmetry statistical value 1/50)
- L_Cg = √π (the Gaussian-width endpoint geometry)
- kL = 2.4973 (the F_MG fixed-point seed)

**Key formula**: k_GUT = M_P·L_Cg/L_GUT, with L_GUT = √3/τ (the J=2 isometry-breaking scale).

**The polarisation decomposition of τ** (tau_pi_bare/ren/delta_pi): the "seven-layer theorem" of τ contains the polarisation counterterm — Π_ren(M_G) = ΣY² = 10/3, Π_bare(M_G) = 0.0014·ΣY², ΔΠ = Π_ren − Π_bare = 3.3287.

[[PARAMS:init_v4.py]]

(Also: G_N_PDG is the single OBSERVED anchor, written by cg_core.params.init_stores, comparison only.)

### 13.2 run_rge.py — the SM running table

**Motivation**: the SM couplings are extrapolated from M_Z to the high scales (M_G, k_GUT), generating the comparison table — the framework's geometric couplings are compared with the SM running at the same scale.

**Method**: the two-loop SM β functions integrated with RK4 (400 steps per decade), the two paths M_Z→M_G→k_GUT and M_Z→v→k_GUT must agree to 1e-12 (a numerical consistency check).

**Discipline**: the SM running produces comparison values only (SM_INPUT provenance), never entering the physical computation.

(No parameters written — a pure computation/verification module.)

### 13.3 spectrum_loop.py — the SM field spectrum (the EC mass shifts on RP³)

**Motivation**: the FRG trace density and the composite-operator amplitude Π² sum over the SM field modes on RP³. Each field species carries (a) the RP³ spectrum of its spin, (b) the effective mass² from the EC connection (curvature + torsion shifts), (c) the field content (multiplicity + statistics weight).

**The EC mass shifts** (derivation of each):
- **Scalar**: m² = ξR = 3/(4L²) — the d=3 conformal coupling ξ=(d−2)/(4(d−1))=1/8, R=6/L².
- **Gauge**: m² = C₂R/12 + τ²/(6L²) — the Camporesi curvature mass (C₂: SU(3) 3.0, SU(2) 2.0, U(1) 0.0) + the EC-torsion shift.
- **Fermion**: m² = 3τ²/(8L²) — only the EC-torsion shift (the curvature is already inside the Dirac² spectrum; adding more would double-count the n=0 eigenvalue).
- **TT**: m² = 6/L² — the Lichnerowicz shift of the round S³.

**Statistics weight**: bosons +1 per real degree of freedom, fermions −1 per Weyl component (a Weyl carries two real components, hence −2 relative to a real boson); the Faddeev–Popov ghosts are complex scalars with Grassmann statistics (−2/ghost).

(No parameters written — a pure computation/verification module.)

### 13.4 sm_content.py — SM field content and hypercharge statistics

**Motivation**: every spectral sum of the framework weights the content by the field content — the FRG trace density bosons +1, fermions −1, the composite-operator amplitude Π² weighted by representation. This module is the single source of the content: 45 Weyl fermions (15 per generation × 3), 12 gauge bosons, the Higgs doublet, the hypercharge table.

**Field content** (15 left-handed Weyl fermions per generation, Q=T₃+Y convention):
```
Q_L = (u_L, d_L)  (3,2)_{1/6}    6 Weyl
u_R               (3,1)_{2/3}    3 Weyl
d_R               (3,1)_{−1/3}   3 Weyl
L_L = (ν_L, e_L)  (1,2)_{−1/2}   2 Weyl
e_R               (1,1)_{−1}     1 Weyl
```

**Hypercharge statistics** (the input to τ): ΣY = 0, ΣY² = 10/3, ΣY³ = −4/9.

**The four dualities** (the framework's unified emergence principle): conformal-gauge N_g·ξ=1, geometric-gauge d=N_c=3, UV-IR window span, spectral-physical spectral-sum representation.

(No parameters written — but the numerator and denominator of τ are computed here.)

(**Closed**: τ=1/50 is obtained EXACT from the EC field equation δS/δK=0 → τ/L=κ²·j₅, the window capacity 2πkL⁴ cancels exactly — see §12.4)

### 13.5 spectral_sum.py — the CGC channel spectral sums

**Motivation**: the framework's emergence criterion is the composite-operator two-point amplitude — the RP³ mode content must make the operator's Π²(p²=0) positive (operator condensable → emergence possible) or negative/zero (not → emergence impossible).

**Five channels** (each probing a different operator):
- Tμν spin-2: the TT projection of the improved energy-momentum tensor (the graviton-like emergence channel)
- Tμν spin-0: the trace channel of the improved EMT
- F²: the field-strength squared (gauge + fermion bubble)
- G²: the gluon condensate (SU(3) only)
- J^μ: the conserved vector current (fermions only)

**Kernels** (one-loop p=0 two-point amplitude, per degree of freedom): K_TT = k⁴/(k²+m²)², K_0 = (1/3)(k²+3m²)²/(k²+m²)², K_F2 = 12k⁴/(k²+m²)² (gauge), K_J = −k²/(k²+m²)².

**Physical role**: the Tμν spin-2 channel → the spectral-pole critical scale V₃·Π²/(32π²) = 4/27 @ k*=M_G (the F_MG fixed point); F²/G²/J^μ → exclusion channels.

(No parameters written — but the sign classification of Π² drives endpoint_constraint.)

### 13.6 endpoint_constraint.py — the Planck endpoint geometry (the F_MG spectral-pole condition)

**Motivation**: on the self-similar flow L(k)=C/k (γ_M=0), the emergence chain is fully determined by three geometric conditions:

```
kL* : V₃·Π²^{Tμν2}(kL,(k/M_P)²)/(32π²) = 4/27 @ k*=M_G   (F_MG)
M_G = C/kL*, k_GUT = C/L_GUT, L_GUT = √3/τ
g₂ = √8·(M_G/M_P)·kL*^{−3/2}                              (Killing normalisation)
```

The F_MG condition is the spectral-pole condition of the improved-EMT spin-2 channel: the graviton-like mode becomes massless at the emergence scale M_G, self-consistently fixing the dimensionless fixed point kL* = 2.4973.

**M_P rescaling invariance**: because M_G = M_P·L_Cg/kL*, all dimensionless predictions (M_G/M_P, g₂) do not depend on the absolute value of M_P.

**The geometric-dynamics conservation law (2026-08-16)**: the first-principles endpoint geometry L_Cg = √π predicts g₂ deviating from the SM by +0.34% = 1/N_c − τ²π/2 — the conservation law N_c(1/α_SM − 1/α_W + τ²π/2) = 1 ⟺ N_g·ξ = 1 (Lean 4 proved).

[[PARAMS:endpoint_constraint]]

### 13.7 gamma_M.py — the geometry-flow trajectory and the anomalous dimension γ_M

**Motivation**: the scale flow of the internal geometry L(k) = C/k carries the anomalous dimension γ_M: ∂_k ln L(k) = −(1+γ_M(k))/k. γ_M=0 is the self-similar branch (L ∝ 1/k); the framework's emergence chain runs on this branch in the M_P→M_G segment.

**The γ_M zero condition**: the dimensionless combination C(kL) = η(k)/(k⁴V₃) (the trace density in geometric-volume units) is a pure function of kL on the self-similar flow; γ_M=0 ⟺ C(kL) constant ⟺ the trace density η ∝ k⁴ (scale-invariant spectrum).

**The entropy identity**: ∫γ_M d ln k = ln(kL·M_G/H0) ≈ 139.253 — turning the geometry flow into the RG-flow integral of the physical scales.

[[PARAMS:gamma_M]]

### 13.8 ir_flow.py — the full γ_M(k) profile (self-similar UV → frozen IR)

**Motivation**: γ_M(k) is the central dynamical function of the framework, whose integral enters the Λ matching formula (the entropy span). The full profile has three intervals:

```
1. UV (k ≥ k_GUT):    γ_M = 0      self-similar flow L ∝ 1/k
2. transition (k ≈ k_GUT):  γ_M crosses 0→−1−p  Δ ln k ≈ 0.43
3. frozen (H0 ≤ k < k_GUT): γ_M ≈ −1−p  frozen branch L ∝ k^p
```

**The frozen exponent**: p = ln(1/kL)/ln(H0/k_GUT) — the exponent that makes the frozen branch reach L ≈ kL at the Hubble scale (endpoint matching).

**RG invariant**: ∫γ_M d ln k (H0→M_G) = ln(kL·M_G/H0) ≈ 139.253 (the same entropy identity as gamma_M).

[[PARAMS:ir_flow]]

### 13.9 trace_density.py — the trace density

**Motivation**: the trace density η is the driving quantity of the FRG flow; the scaling behaviour η ∝ k⁴ is the criterion of the γ_M=0 self-similar branch.

[[PARAMS:trace_density]]

### 13.10 discrete_flow.py — the discrete flow

**Motivation**: the framework's RG flow is discretised on discrete scale slices — the β function, gap spectrum, reflection positivity, and semigroup structure at each step.

[[PARAMS:discrete_flow]]

---

## Chapter 14 Sector 3: the gauge sector

### 14.1 geometric_couplings.py — the geometric gauge couplings g₂ and g₁

**Motivation**: the gauge couplings of the emergent theory are pure functions of the Planck endpoint geometry.

**The Killing normalisation of g₂** (derivation):
```
g₂_raw = 16π²/I_kv, I_kv = |F|²·Vol(RP³) = 2π²L³
g₂(M_G) = √8·(M_G/M_P)·kL^{−3/2}
```
(the (M/M_P)² factor is a normalisation convention, a declared SCALE_CHOICE, not a KK inference.)

**The J=2 squash mixing of g₁** (derivation):
```
g₁ = g₂·κ(2τ), κ²(s) = (1+s)/(1−2s)^{5/2}
s₀ = 2τ = N_g·τ/(d+1) (the λ_EC first-order torsion ÷ (d+1))
```
κ is applied at the breaking scale k_GUT: g₁(k_GUT) = g₂(k_GUT)·κ, then run to M_G.

**The g₂ conservation law** (closed 2026-08-16): the deviation of g₂ from the SM is the geometric-dynamics symmetry correction 1/N_c − τ²π/2.

**The long-root correction of g₃**: g₃(k_GUT) = g₂(k_GUT)·(1+α_GUT²/K), K=8/3.

(**Closed**: the first principles of the κ² of g₁ and the α²/K of g₃ are completed — the 5/8 = ΣY²·Δ_f·ξ of δ_g1 is the conformal-gauge duality N_g·ξ=1; K = J(J+2)/d = 8/3 geometric origin — see §12.4)

[[PARAMS:geometric_couplings]]

### 14.2 geometric_ewsb.py — geometric electroweak breaking

**Motivation**: the isometry breaking of the squashed RP³, SU(2)_R → U(1)_R, produces two Goldstone modes (T¹_R, T²_R), absorbed by the gauge bosons W_R± of the broken directions as longitudinal components. The geometric VEV is the squash amplitude s₀ = 2τ.

**Key prediction**: m_WR = g_R·s0·M_G = 3.519e16 GeV (the GUT right-handed scale); the hierarchy ratio m_W/m_WR = ε/(2s₀) = ×12.5 is exactly 1/(2s₀) = 12.5.

[[PARAMS:geometric_ewsb]]

### 14.3 gauge_group_emergence.py — the gauge group SU(3)×SU(2)×U(1) emerging from the RP³ isometry

**Motivation**: the natural isometry group of the internal RP³ = S³/Z₂ is SO(4) ≅ SU(2)_L × SU(2)_R (6 Killing vectors). The Z₂ quotient distinguishes the two SU(2) factors by chirality:
- 3 even (untwisted) generators → SU(2)_L (weak isospin)
- 3 odd (twisted) generators → SU(2)_R (the twisted sector, broken by the geometric isometry)
- U(1)_Y ← the diagonal generator of the chiral layer (geometric EWSB: SU(2)_R→U(1)_Y, the long-root condensation selects the direction)
- SU(3)_c ← the composite of the two SU(2) blocks coupled to the long root (the A₂ root system on the twisted sector)

**Core**: the gauge group SU(3)×SU(2)×U(1) is the algebraic content of the RP³ isometry/Z₂ quotient; the couplings are the content of geometric_couplings.

[[PARAMS:gauge_group_emergence]]

---

## Chapter 15 Sector 4: the generation sector

### 15.1 window_capacity.py — the window-capacity theorem (the generation count)

**Motivation**: the fermion generation is not an input of the framework — it is the number of spinor modes of the internal RP³ that fit inside the coarse-graining window. The Z₂-even spinor tower has eigenvalues m_n = (n+3/2)/L (n=0,2,4,…); the scale-flow window retains the modes with (n+3/2) < (kL)².

**Result**: the window-capacity theorem — exactly 3 spinor modes satisfy (n+3/2) < (kL)² (n = {0,2,4}).

[[PARAMS:window_capacity]]

### 15.2 sector_alpha.py — the sector-α ladder (fully internal)

**Motivation**: the three sector LZ indices (up/down/lepton) are not observationally back-fitted — they form a ladder from the framework's own closed quantities.

**The ladder (internal derivation chain)**:
```
step 1: α_up = kL − 2τ (window width − non-adiabatic torsion correction; kL − α_up = 2τ exact)
step 2: Δ = 6·(1−n_s)·kL_CMB (the so(4) 6 generators × tilt × CMB window)
step 3: 9/8 = 1/(1−(Y_d/Y_l)²) (hypercharge identity, exact algebra)
step 4: step_lep = 16Δ/17, step_dn = (9/8)·s = 18Δ/17
        α_dn = α_up − (18/17)Δ, α_lp = α_up − 2Δ
```

[[PARAMS:sector_alpha]]

### 15.3 lz_ladder.py — the Landau–Zener generation hierarchy

**Motivation**: the fermion mass ratios are the LZ ladder of the generation modes — the modes n={0,2,4} are exponentially suppressed by non-adiabatic extrusion: m_i ∝ e^{−α·n_i}.

```
α_up = kL − 2τ = 2.4573 (m_t/m_c = e^{2α_up} = 135.9)
m_c/m_u = e^{2kL_cmb + ln 4} = 575.9
α_dn = α_up − (18/17)Δ = 1.9048 (m_b/m_s = e^{2α_dn} = 45.1)
α_lp = α_up − 2Δ = 1.4110 (m_τ/m_μ = e^{2α_lp} = 16.8)
α_sd = α_dn − kL_CMB/6 (down first generation: so(4) isometry dilution, 6 generators)
```

[[PARAMS:lz_ladder]]

---

## Chapter 16 Sector 5: the electroweak sector

![Figure 10: the hierarchy structure (the symmetry correction of the EW-level identity)](figures/fig10_hierarchy.png)

### 16.1 vev_closure.py — the electroweak VEV closure

**Motivation**: the electroweak vacuum expectation value v is the product of the emergence scale and the left/right ratio: **v = M_G·ε**.

**Method**: M_G = 1.729e18 GeV (endpoint_constraint) × ε = 1.4245e-16 (the dilaton-stop line of epsilon_ratio) = 246.19 GeV. The cross-check chain (through the Higgs quartic) v = M_G·A·e^(−φ)·e^(−1/(2π)), A = √(ξR_c/λ_H) gives 243.2 GeV (0.988×, lower precision, cross-check only).

[[PARAMS:vev_closure]]

### 16.2 relaxion_chain.py — the relaxion correction chain φ_R0 → φ_stop

**Motivation**: the electroweak scale is fixed by the dilaton-stop position φ_stop through the order-parameter relation: v² = ξR_c M_G² e^(−2φ)/λ_H (ξ=1/8, R_c=6/π).

**The correction chain** (each step an exact structural logarithm):
```
R0 baseline: φ = 36.1207, v = 482.8 GeV (the window line)
R1 composite picture: Δφ = (1/2)ln 2 = 0.34657 (Higgs = pseudo-dilaton, √4=2 normalisation)
R2 symmetry box diagram: Δφ = (1/4)ln(7/4) = 0.13990 (the 7/4 common origin with the spectral tilt)
R3 single-mode Z: Δφ = −(1/4)ln(2·(3/4)³) = 0.04247 (the Lichnerowicz/Casimir ratio 3/4)
final: φ_stop = 36.6496
```

**The ε decomposition (the actual v closure)**: ε = e^(1/(2π))·e^(−φ_stop) = 1.4203e-16, v = M_G·ε = 245.6 GeV. The zero-point factor e^(1/(2π)) = the causal-horizon temperature factor.

[[PARAMS:relaxion_chain]]

### 16.3 relaxion_geo.py — relaxion geometry (the dilaton pole barrier)

**Motivation**: the dilaton field rolls along the cosmological flow until it hits the geometric pole barrier x(φ;k) = V(k)·Π_φ(k) = 1 (the propagator diverges, the flow freezes, the VEV is fixed).

**The factor-2 anchor**: the baseline stop gives v(φ_R0) = √(ξR_c M_G² e^(−2φ_R0)/λ_H) = 2.02×v — the factor 2 is a structural prediction (not artificial).

[[PARAMS:relaxion_geo]]

### 16.4 epsilon_ratio.py — the electroweak scale ratio ε_L/ε_R

**Motivation**: the electroweak breaking scale is set by the left/right hierarchy ratio ε: v = M_G·ε, ε ≈ 1.4e-16. The framework produces ε by two independent lines (consistent within 0.3%):

**Line 1 (the window square channel, the dynamical line)**:
```
ε = (3α/π)·e^(−4πkL), α = 1/16π² = 1.4204e-16 (−0.27%)
mechanism: the J=2 squash bifurcation contributes 3α/2; the mode crosses the window twice (production + stabilisation),
each contributing e^(−2πkL); the Fourier prefactor 1/π. product (3α/2)(1/π)e^(−4πkL)·2 = 3α/π
```

**Line 2 (the dilaton-stop line, the zero-point line)**:
```
ε = e^(1/(2π))·e^(−φ_R3), φ_R3 = 4πkL − ln(3α/π) + 1/(2π) = 1.4245e-16 (0.02%)
```

**The mechanism of e^(−4πkL)**: the LZ non-adiabatic extrusion of the J=2 squash mode crossing the coarse-graining window, suppressed twice (window-edge production + stabilisation), each with LZ survival factor e^(−2πkL) — the same exponent as Δ²_s.

[[PARAMS:epsilon_ratio]]

### 16.5 order_parameter.py — the order parameter (the Landau potential of the isometry-breaking condensation)

**Motivation**: the isometry breaking SU(2)_R → U(1)_Y is driven by the J=2 squash mode — the Landau potential of the order parameter φ on the curvature axis:
```
V(φ; L) = (1/2)·ξ·(R(L) − R_c)·φ² + (λ/4)·φ⁴
```

**Key quantities**:
- ξ = 1/8 (the d=3 conformal coupling)
- R_c* = 6/π (the critical curvature, the Gaussian family)
- s₀ = 2τ ≈ 0.04 (the VEV, the squash amplitude)
- λ = ξ·(R_c − R_GUT)/(2τ)² ≈ 149.0 (quartic, GUT-onset stationarity self-consistency)
- m²(L) = ξ·(R(L) − R_c) (effective mass²: tachyon appears when R < R_c)

**No free-spectrum tachyon**: the EC eigenvalue of the J=2 TT mode λ_EC·L² = 8(1+τ/2)²+6 = 14.1608 > 0 — the EC sector is stable; the tachyon is not a free-spectrum instability, but the curvature coupling ξ(R−R_c) of the order parameter (the condensation trigger).

**Condensation (running VEV)**: φ₀(L) = √(ξ(R_c−R(L))/λ) (R < R_c); V_min(L) = −ξ²(R_c−R(L))²/(4λ) (the Mexican-hat depth).

(**Closed**: the λ quartic is derived self-consistently from the stationarity ∂V/∂φ|_φ₀=0 + the EC-torsion algebra b=4a)

[[PARAMS:order_parameter]]

### 16.6 pseudo_dilaton.py — pseudo-dilaton consistency (the Higgs self-coupling)

**Motivation**: the pseudo-dilaton sector establishes the Higgs as the pseudo-dilaton of the trace anomaly: the Higgs self-coupling λ_H is the dilaton quartic divided by the 32π² loop factor:
```
λ_H = (λ_dil + σ_SM)/(32π²)
λ_dil = 3×4π = 12π (the trace anomaly couples all 3 generations, the NJL strong-coupling bound 4π/generation)
σ_SM = 3 (the SM loop contribution, one unit per generation)
λ_H = (12π+3)/(32π²) = 0.129
```

**The trace-anomaly coefficient**: β_eff = (3g₂²+g₁²+4y_t²+2λ_H)/(16π²) + λ_dil/(16π²).

[[PARAMS:pseudo_dilaton]]

---

### 16.7 ew_precision.py — the electroweak precision observables (the M_G → M_Z interface block)

The interface chain of the framework terminates in the electroweak observables that the high-precision machines measure directly: the internal Z mass (the self-consistent fixed point of the tree-level mass formula on the two-loop geometric running), the W mass (the on-shell Sirlin relation with the one-loop t-b Veltman rho), the weak mixing angles, the rho parameter, the partial and total Z widths (Born + QCD/QED radiators), the hadronic peak cross-section, and the tree-level Higgs mass. Every input is a framework-derived value; the observed values appear only as comparison targets. The computation level is stated in the module docstring (M_Z tree-level on the two-loop running; M_W with Delta rho, Delta r_rem omitted; Gamma_Z Born + radiators; m_H tree-level).

[[PARAMS:ew_precision]]

## Chapter 17 Sector 6: the cosmology sector

![Figure 9: the cosmology-sector closure (zero observational anchor)](figures/fig09_cosmology.png)

### 17.1 spectral_tilt.py — the spectral-tilt closure

**Motivation**: the primordial spectral tilt is the exact product of the torsion modulus and the rational number 7/4:
```
1 − n_s = τ·(7/4) = 0.02 × 1.75 = 0.035
```
7/4 is exact (the scalar/vector mode weight ratio of the coarse-graining window at the CMB scale — the unbiased Gaussian spectral tilt).

[[PARAMS:spectral_tilt]]

### 17.2 dark_energy.py — the dark-energy closure (the neutrino-mass floor)

**Motivation**: the dark-energy density is set by **the lightest neutrino mass** — the neutrino is the lightest fermion, whose mass sets the vacuum-energy floor:
```
ρ_Λ = Y_u·m_ν1⁴ = (2/3)·m_ν1⁴
m_ν3 = v²·(2π)²/k_GUT (the Weinberg dimension-5 operator)
m_ν1 = m_ν3·(m1/m2)·(m2/m3) (hierarchy ratios)
m1/m2 = 1/Tr(Y²) = 3/10, m2/m3 = 1/(√3·Tr(Y²))
```
The cosmological constant Λ = ρ_Λ/M_P², Ω_Λ = ρ_Λ/(3H0²M_P²).

**T_CMB** (redshift = spectrum): T_CMB = m_ν1·r12/π·(1−τ·Δ_s) — the lightest neutrino determines the CMB photon-floor temperature.

[[PARAMS:dark_energy]]

### 17.3 bbn_helium.py — the BBN sector (helium abundance + neutrino species)

**Motivation**: the BBN helium abundance Y_p is determined by the weak-rate freeze-out + the framework's electroweak scale v; N_eff is the effective neutrino species. The framework's content is **v-pinning** (v determines the freeze-out temperature T_f).

**The Y_p closure**: n/p = exp(−Δm/T_f), (n/p)_BBN = (n/p)·exp(−t/τ_n), Y_p = 2(n/p)/(1+(n/p)). The framework's v = 246.19 gives the standard freeze-out.

**The non-perturbative pinning of the six constants (2026-08-17)**: g_A = N_g·Δ_s/π = 4/π, Δ_EM = (1−1/(2π))αΛ_QCD, δ_R = 1+(1−τ)/(8π), δ_N = √3/(3(2π)²).

[[PARAMS:bbn_helium]]

### 17.4 perturbation_amplitude.py — the primordial perturbation amplitude (no inflation)

**Motivation**: the framework predicts the CMB scalar amplitude **without inflation** — the fluctuations are the spin-1/2 Gaussian zero point, suppressed by the Euclidean period of the emergence window:
```
Δ²_R = Δ²_0·e^(−2π·kL_CMB)
Δ²_0 = (1/2)·(1/2π)² = 1.267e-2 (the spin-1/2 zero point)
e^(−2π·kL_CMB) = e^(−15.61) = 1.658e-7 (the window suppression)
Δ²_R = 2.10e-9
```

**The suppression family (the public thread 2π)**: ε = e^(1/2π), a0 = cH0/(2π), 2L = √(2π), kL ≈ √(2π).

[[PARAMS:perturbation_amplitude]]

### 17.5 gw_ratio.py — the GW ratio, the 2π-window IR anchors, the Hubble-scale closure

**Motivation**: the IR end of the window is anchored by the same 2π family that closes the UV.

**Three IR anchors**:
```
r = (1/2π)² = 0.02533 (tensor-to-scalar ratio, CMB-S4 testable)
Δ²_t = r·Δ²_s = 5.32e-11
2L = √(2π) = 2.5066 (Gaussian-entropy minimal distance)
H0 = M_P·√π·e^(−∫γ_M) = 1.439e-42 GeV (the Hubble endpoint)
σ_C = 1/H0 = 6.948e41 GeV⁻¹ (the IR window endpoint)
```

**Derivation chain**: r=(1/2π)² is the Euclidean zero point of the tensor sector (the same structure as the scalar Δ²_0); 2L=√(2π) is the Gaussian normalisation ∫exp(−x²/2)dx.

[[PARAMS:gw_ratio]]

---

## Chapter 18 Sector 7: the gravity sector

### 18.1 tt_tensor.py — the TT propagator and the spectral-pole identity G_TT ∝ k^(−2)

**Motivation**: the emergent graviton is the spectral pole of the improved-EMT TT propagator. The J=2 TT mode on the self-similar trajectory:
```
p² = J(J+2)/L² = 8·k²/kL² (spatial eigenvalue)
m² = 6/L² (Lichnerowicz shift)
G_TT = 1/(p² + R_k + m²)
```
The δ criterion: slope_G = d ln G_TT/d ln k < −1.5 (a k^(−2)-type pole) and |slope_Z| < 0.5 (the residue is k-independent). n_grav=0: the lowest TT eigenvalue 14/L² > 0 (the graviton is a spectral pole, not a zero mode).

[[PARAMS:tt_tensor]]

### 18.2 pole_analysis.py — the spectral-pole stability criterion

**Motivation**: the massless spin-2 pole of the emergent TT propagator is a stable physical pole if and only if the spectral density is positive and the matter self-energy is below the bare mass:
```
spectral_positive: p²_min = 8/L² > 0
pole_stable: Σ(M_G) < m²_bare (self-energy below the bare mass 14/L²)
matter_is_small: Σ(M_G)/p²_min < 0.1
```

[[PARAMS:pole_analysis]]

### 18.3 chi_pole_condition.py — the χ-pole ladder condition

**Motivation**: the emergent graviton pole forms from the divergence of the TT-channel ladder resummation: Π_resum = Π²/(1−V_TT·Π²) ⟹ V_TT(χ)·Π²(χ) = 1. The ST-tachyon couples the geometry with m²(χ) = m²(0)·e^(−2χ) (α=2, not a free parameter — χ is the conformal factor of the internal metric).

**Lemma-4 content**: (i) Π²(χ) monotonically increasing; (ii) V_TT(χ) grows at least as e^(2χ); (iii) x(χ) continuous and unbounded ⟹ the crossing exists (the intermediate-value theorem).

[[PARAMS:chi_pole_condition]]

### 18.4 newton.py — Newton's constant (the framework's single dimensional anchor)

**Motivation**: the gravitational coupling G_N is not a free parameter — it is the zero-momentum residue Z_phys of the TT propagator, divided by the Planck scale:
```
G_N = 1/(8π·Z_phys·M_P²)
Z_phys = |trace_eff|/(8π·(L_Gg/L_Cg)²)
```
Three prescriptions (A direct residue, B spectral sum, C flat matching) agree within 0.03%.

**0.027% is the anchor residue**: G_N = 1/(8πM_P²) is an identity; after the anchor is updated to PDG-2024 it reproduces exactly (0.0000%). Z_phys(M_G) = 0.665 is the vacuum-energy mass correction.

[[PARAMS:newton]]

### 18.5 zk_gravitational_rg.py — the Z(k) gravitational wave-function renormalisation

**Motivation**: the gravity sector is the TT metric fluctuation on the RP³ background, whose kinetic coefficient is Z(k), controlling the effective Newton constant G_N(k) = G_N/Z(k).

**Geometric running**: on the self-similar trajectory Z(k) = Z_G·k/M_G, Z_G = (M_P/M_G)²/(16π) = 0.03947 (purely geometric, exact on the trajectory).

**Quantum correction**: the SM matter loop (the one-loop graviton self-energy, Veltman-type coefficients +1 scalar/−2 Weyl/+4 vector) displaces Z, Δln Z = +0.01226 → M_P displaced +0.615% (NEGLIGIBLE).

[[PARAMS:zk_gravitational_rg]]

---

## Chapter 19 Sector 8: the flavour and fermion sector

### 19.1 neutrino_closure.py — the neutrino-sector closure + the CKM |V_us| Gatto

**Motivation**: the neutrino masses are closed through three order-of-magnitude-consistent relations:
```
1. Weinberg operator (dimension-5): m_ν3 = v²·(2π)²/k_GUT = 0.048 eV
2. the 5/3 GUT relation: Tr(Y²)/Tr(T₃²) = (10/3)/2 = 5/3 (content balance)
   m_ν1·m_ν2/m_ν3² = 5/3 → m_ν2 = √((3/5)·m_ν1·m_ν3)
3. Gatto θ12: sin²θ12 = m_ν1/m_ν2 = 0.30 (solar, closed)
```

**The neutrino hierarchy (hypercharge trace)**: m_ν1/m_ν2 = 1/Tr(Y²) = 3/10, m_ν2/m_ν3 = 1/(√3·Tr(Y²)).

**CKM |V_us| (Gatto × LZ hierarchy)**: |V_us| = |√(m_d/m_s) − e^(iδ)√(m_u/m_c)| = 0.225.

**Mixing angles**: sin²θ12 = 1/3, sin²θ13 = (1/2π)²√3/2, sin²θ23 = 1/2 + Tr(T₃²)/(2π)².

[[PARAMS:neutrino_closure]]

### 19.2 mass_operator_overlap.py — the mass-operator overlap (absolute Yukawa from geometry)

**Motivation**: the fermion mass m_f = y_f(M_G)·v/√2. The absolute Yukawa y_f(M_G) is the overlap of the fermion mode with the mass operator.

**The top-quark basis**: the n=0 mode of the (0,0) scalar channel has full overlap y_0 = 1.0 (exact SO(4) Clebsch–Gordan normalisation). m_t = y_0·v/√2 = 174.1 GeV (+0.56%).

**The bottom-sector absolute basis (geometric mean)**:
```
y_b/y_t = e^(−(2α_dn − ns_tilt(kL_CMB+2τ)))
m_b² = m_s·m_t·e^(ns_tilt(kL_CMB+2τ))
```

[[PARAMS:mass_operator_overlap]]

### 19.3 electron_mass.py — the absolute electron-mass closure

**Motivation**: the electron is the lightest charged fermion, closed through the Planck-anchored exponent chain:
```
m_e = M_P·e^(−20·kL)·(1−s0·κ) = 0.510 MeV
20 = 4×5 (Yukawa cascade 4 steps × 5 species per generation)
```
**The μ/e ratio**: m_μ/m_e = e^(2α_lp + √(2π)) = 206.36 (the lepton LZ exponent + the entropy minimal distance).

[[PARAMS:electron_mass]]

---

## Chapter 20 Sectors 9–10: the framework layer and the QCD sector

### 20.1 five_items.py — the state of the five framework results

**Motivation**: records the state of the five framework results, each annotated with the closing module:
1. why 3 generations (n={0,2,4}): CLOSED-formal (the window-capacity theorem);
2. the branch choice (hypercharge B′ vs C′): recorded (the U(1)_Y generator choice of geometric EWSB);
3. 2L = √(2π): CLOSED (entropy minimal distance);
4. the two v paths (factor-2 unification): CLOSED (ε is the common object);
5. m_e: CLOSED (m_e = M_P·e^(−20kL)·(1−s0·κ)).

[[PARAMS:five_items]]

### 20.2 cp_sector.py — the CP sector (the 8/7 content ratio, CP phase, Jarlskog, baryon asymmetry)

**Motivation**: the CP sector records the framework's content-ratio classification of the CP phase and the Jarlskog/baryon-asymmetry closure.

**The 8/7 content ratio (exact)**: n_L/n_R = 8/7 = 1.142857 (8 left-handed doublets vs 7 right-handed singlets per generation).

**The CP phases**:
```
δ_PMNS/π ≈ 8/7 ≈ 1.14 (lepton CP, PDG 197°–212°)
δ_CKM = (8/7)π/N_c = 8π/21 ≈ 68.57° (quark CP, colour-number dilution ÷N_c = ÷d)
```

**Baryogenesis**: η_B = J·α_W⁵/56 (Sakharov content: J = CP source, α_W² = sphaleron rate, 1/56 = ξ/n_R).

(**Closed**: |V_us||V_cb||V_ub| = α_W³ (−0.09%); the δ_CKM = 8π/21 colour-number-dilution derivation; η_B = α_W⁵ sphaleron standard rate)

[[PARAMS:cp_sector]]

### 20.3 sigma_language.py — the σ-language kinematics (c as the correlation speed)

**Motivation**: the framework's basic language is the σ field (a single-valued scalar on the coarse-graining index space, with length dimension). The RG scale k and the σ distance are two units of the same physical axis:
```
σ(k) = c/k, σ_C = c/H0, T_eff = k/(2π)
```
**The status of c**: c is the correlation propagation speed of the σ language, a **unit convention** (natural units c=1), not a third physical input — the framework's anchor is {M_P} + the internal chain (H0 is derived, c is a unit choice). c is not a metric property (the framework has no emergent spacetime metric).

[[PARAMS:sigma_language]]

### 20.4 mass_gap_scale.py — the mass-gap scale closure ΔE = (1/8)·M_G

**Motivation**: the mass-gap theorem proves Δ > 0; the numerical value closes the scale chain from the emergence scale down to the hadronic scale:
```
STEP 1 condensation energy: ΔE = (1/8)·M_G = 0.125·M_G ≈ 2.16e17 GeV
  (the conformal coupling ξ=1/8 itself; the K=8/3 long-root geometric carrier)
STEP 2 generator mass: m_gen = g₂(M_G)·(2τ)·M_G/√2 ≈ 1.12e17 GeV
STEP 3 glueball: two-loop QCD running → Λ_QCD ≈ 0.22 GeV, m_G ≈ 8.1·Λ_QCD ≈ 1.8 GeV
```

[[PARAMS:mass_gap_scale]]

### 20.5 qcd_sector.py — the QCD sector (the mass-gap chain, glueball tower, g₃ long-root closure)

**Motivation**: the QCD sector's three-layer closure:
```
PART 1 mass-gap scale chain (closed): ΔE = (1/8)M_G → m_gen → Λ_QCD ≈ 0.208 GeV
PART 2 topological gap (RP³ spectral level): the glueball mode is the l=2 scalar, λ_glue = 8/L² > 0
PART 3 glueball tower (two-gluon bound-state spectrum): (1/2,1/2)⊗(1/2,1/2) = (0,0)⊕(1,1)⊕(1,0)⊕(0,1)
  0⁺⁺ (0,0) λ=8/L²; 2⁺⁺ (1,1) λ=16/L² → √2; 1⁺⁻ (1,0)⊕(0,1) λ=12/L²
```

**Confinement (spectral language)**: string tension σ = (λ_TT/π)Λ² = (14/π)Λ²; deconfinement T_d = (λ_vector/N_c)Λ = (4/3)Λ; σ/T_d² = 126/(16π(1−τκ)²) = 2.6242 self-consistent.

**χSB**: standard QCD dynamics (NJL, f_π ~ 93 MeV), not a framework prediction (QCD is vectorial, no structural chirality).

[[PARAMS:qcd_sector]]

---

## Appendix: full parameter-store index

> The complete list of the 170 parameters by writer attribution (see `params_export.json`). The sections above show the parameter tables by module; this appendix lists the complete **sector → module → parameter** index for retrieval.

| Sector | module | parameter count | representative parameters |
|---|---|---|---|
| 0 anchor | init_v4 | 7 | M_P, tau, L_Cg, k_GUT |
| 2 FRG | endpoint_constraint | 6 | kL, M_G, L_Cg_star |
| 2 FRG | gamma_M | 2 | entropy_integral, gamma_M |
| 2 FRG | ir_flow | 2 | gamma_M_frozen, ir_flow_int_gamma |
| 2 FRG | trace_density | 1 | trace_density_MG |
| 2 FRG | discrete_flow | 6 | discrete_flow_beta, step |
| 3 gauge | geometric_couplings | 9 | g1_MG_geo, g2_MG, g3_MG_geo |
| 3 gauge | geometric_ewsb | 6 | geometric_ewsb_m_WR |
| 3 gauge | gauge_group_emergence | 1 | gauge_group_emergence |
| 4 generation | window_capacity | 1 | n_generations |
| 4 generation | sector_alpha | 6 | alpha_up, alpha_down, alpha_lepton |
| 4 generation | lz_ladder | 5 | m_t_over_m_c, alpha_sd |
| 5 electroweak | vev_closure | 1 | v_HIGGS |
| 5 electroweak | relaxion_chain | 2 | relaxion_phi_stop |
| 5 electroweak | relaxion_geo | 1 | relaxion_factor_two |
| 5 electroweak | epsilon_ratio | 2 | epsilon_L_over_R, phi_R3 |
| 5 electroweak | order_parameter | 9 | order_parameter_lambda, s0 |
| 5 electroweak | pseudo_dilaton | 3 | lambda_H_pseudo |
| 5 electroweak | ew_precision | 16 | M_Z_pred, M_W_pred, Gamma_Z_pred, m_H_pred |
| 6 cosmology | spectral_tilt | 1 | ns_tilt |
| 6 cosmology | dark_energy | 4 | Lambda, Omega_Lambda, T_CMB_GeV |
| 6 cosmology | bbn_helium | 8 | bbn_Yp, bbn_Neff |
| 6 cosmology | perturbation_amplitude | 2 | kL_CMB, perturbation_amplitude |
| 6 cosmology | gw_ratio | 9 | H0_GEV, Omega_b, a0_MOND |
| 7 gravity | tt_tensor | 2 | TT_delta_forming |
| 7 gravity | pole_analysis | 1 | TT_pole_verified |
| 7 gravity | chi_pole_condition | 4 | chi_pole_crossing |
| 7 gravity | newton | 3 | G_N_pred, Z_phys_MG |
| 7 gravity | zk_gravitational_rg | 4 | Z_G_dim, Z_quantum_shift |
| 8 flavour | neutrino_closure | 11 | m_nu1, m_nu3, sin2_theta12 |
| 8 flavour | mass_operator_overlap | 4 | m_t_pred, y_top_base |
| 8 flavour | electron_mass | 3 | m_e_pred, m_mu_over_m_e |
| 9 framework | five_items | 1 | five_items_status |
| 9 framework | cp_sector | 6 | ckm_delta_direction, eta_b |
| 9 framework | sigma_language | 1 | sigma_language_status |
| 10 QCD | mass_gap_scale | 5 | m_glueball, mass_gap_dE |
| 10 QCD | qcd_sector | 7 | m_p, qcd_Lambda_QCD, qcd_string_tension |

---

*End of Part 2. All parameter values and notes are generated programmatically from `cg_params.json` (reproduce_v4 exit 0 + audit_param_writers CLEAN).*