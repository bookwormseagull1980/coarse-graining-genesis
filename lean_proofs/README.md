<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
ORCID:       0009-0000-6600-6171
DOI:         10.5281/zenodo.22067006

Part of the V4 spectral framework, whose physics is presented in the
companion papers:
  [I]  "The spectrum of a compact internal space.
        I. Gauge structure and fermion content"
  [II] "The spectrum of a compact internal space.
        II. Effective couplings and mass scales"
-->

# Lean 4 Proof Archive (V4 Framework)

This directory collects the Lean 4 formal proof guards of the V4 framework (20 files, all expected to compile with `exit 0`).

**Lean 4 path**: `lean.exe` (core, no mathlib, `by native_decide`; any Lean 4.7.0 install works)
**Run**: `lean.exe <file>.lean`, exit 0 = all theorems pass.
**Source**: consolidated into this directory from the AXIOM_PROOF_SERIES archive (2026-08-18).

---

## Overview: 20 files in three groups

| Group | Count | Serves | Dates |
|---|---|---|---|
| **A. V4 numerical content** | 11 | Directly verifies the coefficients/symmetries/constants of the V4 code (`cg_core`/`cg_frg` modules) | 2026-08-16 ~ 08-18 |
| **B. Paper-4 theoretical foundation** | 6 | Axiomatic proofs (disorder axiom → gauge group → dimension 4), the "why" layer of V4 (Paper 4 is the axiomatic foundation of V4) | 2026-08-07 ~ 08-08 |
| **C. Endpoint cosmology guards** | 3 | Finite arithmetic and logical-dependency guards for the endpoint cosmology branch | 2026-08-22 ~ 08-23 |

Verification conclusion (2026-08-18): **9 group-A files are up-to-date matches**; 2 group-A files are intermediate iterations (some values superseded, see annotations); 6 group-B files are the Paper-4 final versions (non-iterative, still valid).

---

## A. V4 numerical content (11)

### 1. `bbn_nonperturbative.lean` (7 theorems) ✅ up-to-date
The **non-perturbative** internalisation of the six BBN constants (final version). Corresponds to `cg_frg/cosmology/bbn_helium.py`.
- `g_A = N_g·Δ_s/π = 2(d−1)/π = 4/π = 1.273` (conformal-weight form, **not** SU(6) constituent quarks)
- `Δ_EM = (1−1/(2π))·α_em·Λ_QCD = 1.2725 MeV` (**not** Coulomb self-energy)
- `δ_R = 1+(1−τ)/(8π)`, `δ_N = √3/(3(2π)²)`, `|V_ud| = √(1−|V_us|²)`, `f` = phase space + Coulomb
- This is the final version after the 2026-08-17 02:35 methodological correction by the user ("the framework itself is non-perturbative"), and it **supersedes** the perturbative/semi-classical values of bbn_six_internal.

### 2. `bbn_nuclear.lean` (6 theorems) ⚠️ intermediate iteration (partly still valid)
Internalisation of the 5 BBN nuclear-physics constants (`Δm_np, T_f, τ_n, t_decay, N_eff`).
- **Still valid**: the **hypercharge asymmetry 9:1** of `Δm_np = (m_d−m_u)−Δ_EM` (the "discrete-structure increment": `m_d/m_s ∝ (1+|Y_d|/|Y_u|)² = 9/4`, `m_u/m_c ∝ 1/4`, `|Y_d|/|Y_u| = 1/2`), the freeze-out exponent `T⁵/T² = T³`, the `N_eff = 3×(1+δ_N)` structure — these are mechanisms still used by bbn_helium.py.
- **Outdated**: `Δ_EM = 1.270 MeV` (old Coulomb self-energy), the `g_A = 5/4` approximation of `τ_n` — superseded by bbn_nonperturbative's `Δ_EM = (1−1/2π)αΛ` and `g_A = 4/π`.

### 3. `bbn_six_internal.lean` (6 theorems) ⚠️ intermediate iteration (core values superseded)
The perturbative/semi-classical internalisation of the six BBN constants (**intermediate version**).
- **Outdated**: `g_A = 5/3` (SU(6) constituent quarks), `Δ_EM = (3/5)αΛ` (Coulomb self-energy), `δ_R = Sirlin leading term` — superseded by bbn_nonperturbative's non-perturbative values; its "relativistic-correction candidate 16/21" was pinned down on 08-17 02:20 as **a fit rather than a derivation** and rejected.
- **Still valid**: `|V_ud| = √(1−|V_us|²)` (CKM unitarity), `f` = phase space.

### 4. `conservation_spectral_origin.lean` (7 theorems) ✅ up-to-date
The spectral-sum origin of the conservation-law torsion term `τ²π/2`. Corresponds to `cg_frg/gauge/geometric_couplings.py`.
- `τ²π/2 = (λ_EC second-order term 2τ²) × (Euclidean period 2π) × (conformal coupling ξ = 1/N_g) = 4πτ²/N_g` (three physical origins).

### 5. `fermion_content.lean` (9 theorems) ✅ up-to-date
The content derivation of the 5 fermion representations + the deep symmetry. Corresponds to `cg_core/sm_content.py`.
- `N_L = 8 = N_g = N_c²−1` (left-handed component count = colour generator count), `N_R = 7 = N_g−1`, chiral asymmetry = 1, colour vectoriality, total 15. The 5 representations follow from minimality + chirality + colour vectoriality (not an external input).

### 6. `hypercharge_derivation.lean` (9 theorems) ✅ up-to-date
The first-principles derivation of the hypercharge assignment `Y = (1/6, 2/3, −1/3, −1/2, −1)`. Corresponds to `cg_core/beta_functions.py`, `cg_core/sm_content.py`.
- Uniquely derived from [anomaly cancellation (SU(2)²U(1) + gravitational U(1)) + Yukawa structure]: `3Y_Q − 1/2 = 0 → Y_Q = 1/6`.

### 7. `inverse_coupling_symmetry.lean` (21 theorems) ✅ up-to-date
The inverse-coupling symmetry conservation law. Corresponds to `cg_frg/gauge/geometric_couplings.py`.
- Main law `1/α_SM = 1/α_W + 1/N_c − τ²π/2`, conservation-law form `N_c(1/α_SM−1/α_W+τ²π/2) = 1`, content ratios (N_g·ξ=1, ΣY²Δ_f=5, τ=1/50, s0/N_R=1/175, λ_EC=14+8τ+2τ², b₁/b₂/b₃ content derivation).

### 8. `twoloop_gauge_matrix.lean` (11 theorems) ✅ up-to-date
The content derivation of all 9 coefficients of the two-loop gauge β matrix B_ij. Corresponds to `cg_core/beta_functions.py::_two_loop_gauge_matrix()`.
- `B = [[199/50, 27/10, 44/5], [9/10, 35/6, 12], [11/10, 9/2, −26]]`, derived from the Casimir×Dynkin quadratic combinations (Machacek-Vaughn / Luo-Wang-Xiao Eq. 30+110, cross-checked against Buttazzo 2013).

### 9. `twoloop_yukawa_quartic.lean` (62 theorems) ✅ up-to-date
The content derivation of the two-loop top-Yukawa and Higgs-quartic β coefficients (closed 2026-08-18) + the electron-mass `20 = 4×5` cascade structure. Corresponds to `cg_core/beta_functions.py`, `cg_frg/fermion/electron_mass.py`.
- β_yt one-loop (9/2=3/2+N_c, gauge term −3[C₂(Q_L)+C₂(u_R)]/group) + two-loop (Luo-Xiao 2003 Eq. 6, all 12 coefficients) + β_λ one-loop/two-loop complete (Eq. 9/10, all 27 coefficients, λ_LX=2λ conversion) + the `20 = (d+1)(ΣY²Δ_f) = 4×5` cascade.

### 10. `yukawa_gauge_mixing.lean` (8 theorems) ✅ up-to-date
The content derivation of the two-loop Yukawa-gauge mixing coefficients A_i. Corresponds to `cg_core/beta_functions.py::_yukawa_gauge_mixing()`.
- `A_i = (6/d(G_i))[C₂(Q_L)+C₂(u_R)] = (17/10, 3/2, 2)`, 6 = 2(weak contraction)×3(colour), the weak-contraction factor 2 of the u_R trace = dim SU(2).

### 11. `conformal_gauge_duality.lean` (14 theorems) ✅ up-to-date (2026-08-18)
The first-principles content of the conformal-gauge duality N_g·ξ = 1. Corresponds to `cg_frg/ewsb/order_parameter.py` (conformal_coupling/conformal_weight/_self_test), `cg_frg/cosmology/bbn_helium.py` (g_A = N_g·Δ_s/π), `cg_frg/qcd/qcd_sector.py` (the N_g·ξ=1 unit).
- ξ = (d−2)/(4(d−1)) = 1/8 (**Yamabe conformal coupling**, the unique coupling of Weyl-rescaling invariance — a first-principles standard result, not a framework convention)
- N_g = N_c²−1 = 8 (the su(3) adjoint dimension)
- Coupling form N_g·ξ = 1 ⟺ conformal-weight form N_g·Δ_s = 2(d−1) = 4, bridge Δ_s = 2ξ(d−1) (Δ_s = (d−2)/2, the Gaussian-fixed-point scaling dimension)
- Window-weight ratio `(1+2+1+3)/(d+1)=7/4`, with numerator from `rp3_spectrum.weyl_dof()` and denominator `d+1=4`; the conformal-curvature identity `1 + ξ R_LC L² = 1 + (1/8)·6 = 7/4` is retained as a cross-check.
- **Honest status**: N_g·ξ = 1 is not a heat-kernel/anomaly-vanishing theorem (a₁=0 gives ξ=1/6, and odd-dimensional manifolds have no trace anomaly), but the arithmetic product of two standard facts — the duality is a selection principle that fixes the colour algebra, not a derived theorem.

---

## B. Paper-4 theoretical foundation (6, the "why" layer of V4)

This group is **axiomatic proof**, serving Paper 4 *A Spectral Perspective on Gauge Structure and a Mass Gap: Foundations* — the axiomatic foundation of V4 (Paper 4 answers "why SU(3)×SU(2)×U(1), why dimension 4"; V4 answers "what are the numbers"). **It does not directly verify V4 numbers**, but belongs upstream of the same project system.

### 12. `categorical_solution.lean` (10 examples) ✅ final
The complementary screening of axiom M (the disorder axiom) and the Wightman axioms. Corresponds to `cg_frg/axiom_categorical.py`.
- T1 (W does not imply M), T2 (M∩W non-empty), T4 (M does not imply W), "2-ness" (minimal non-trivial dimension = 2).

### 13. `emergence_chain.lean` (3 theorems) ✅ final
The σ emergence skeleton (3+1 decomposition) + the provable core of the T3 chain (rank-2 Cartan minimal-coupling lemma `|b|=1 → A³`, "why SU(3)").

### 14. `repcat_category.lean` (4 theorems) ✅ final
Rep(Spin(4)) as a category: the Schur skeleton (category axioms + Hom set = Schur's lemma, thin category).

### 15. `su2_classification.lean` (3 theorems) ✅ final
The minimality theorem of the infinite dimensional family `dim(n) = n+1` of SU(2): minimal non-trivial dimension = 2, unique at n=1 (j=1/2) — the formal content of "1/2 is the minimal change".

### 16. `th_category.lean` (6 theorems) ✅ final
The Th formal category (objects = (content, dynamics)) + full subcategories MCat/WCat + the pullback theorem (intersection = pullback of the inclusion functor).

### 17. `wightman_frame.lean` (3 theorems) ✅ final
The Wightman axioms W1–W6 formal-predicate framework + the T1/T2/T4 screening theorems (the analytic content that free fields satisfy W1–W6 is cited from Streater–Wightman).

---

## C. Endpoint cosmology guards (3)

### 18. `ir_cubic_closure.lean` (11 theorems) ✅ endpoint acceleration arithmetic guard
The arithmetic skeleton of the cubic endpoint acceleration closure.
- Proves that in three spatial dimensions, the local first-gradient scale-invariant exponent is `p=3`.
- Proves that the same exponent is the flat-rotation point-source exponent and gives the BTFR quarter-power denominator.
- Scope: Lean checks the finite exponent identities; continuum variational calculus is recorded analytically in `docs/COSMOLOGY_ENDPOINT_RESIDUAL.md`.

### 19. `ir_action_selection.lean` (7 theorems) ✅ endpoint response arithmetic guard
The arithmetic skeleton of the minimal spectral-quadratic Pade selection used by the local endpoint response.
- Proves that the normalised [1/1] ansatz `mu(s)^2 = a s/(b+c s)` is fixed to `a:b:c=1:1:1` once the deep-IR and Newtonian normalisations are imposed.
- Scope: Lean checks the coefficient-selection logic; the analytic selection argument is recorded in `docs/COSMOLOGY_ENDPOINT_RESIDUAL.md`.

### 20. `endpoint_residual_cosmology.lean` (5 theorems) ✅ endpoint-cosmology logic guard
The logical skeleton of the endpoint-residual cosmology closure used by
`cg_frg/cosmology/endpoint_residual.py`.
- Proves that the final closure package follows from the stated MaxEnt endpoint hypotheses: global sigma endpoint, local spatial equations, momentum constraints, visible matter conservation, Bianchi identity, no extra dark stress tensor, and a local normal residual.
- Proves the linear cosmology closure package, the acceleration-branch package, and the no-double-counting decomposition.
- Honest status: this file formalizes the logical dependency structure. It does not formalize tensor calculus, ADM geometry, or CAMB numerics; CAMB is only a downstream comparison propagation of fixed V4 outputs.

---

## Verification summary (2026-08-18)

| Status | Files | Note |
|---|---|---|
| ✅ up-to-date match | 9 group-A + 6 group-B | Consistent with the current code / Paper-4 final version |
| ⚠️ intermediate iteration | `bbn_nuclear.lean`, `bbn_six_internal.lean` | Core values (g_A, Δ_EM) superseded by the non-perturbative values of `bbn_nonperturbative.lean`; but the hypercharge asymmetry 9:1, CKM unitarity, phase space, etc. remain valid |

**All 20 files are intended to compile with `exit 0`**.  The first 17 were verified one by one on 2026-08-18; the IR and endpoint-cosmology guards should be checked together with the archive verifier after edits.

> Note: in group A, `bbn_nuclear` and `bbn_six_internal` are **historical iterations** of the BBN-constant internalisation (kept as a development record), physically superseded in their core values by `bbn_nonperturbative`; the remaining 9 group-A files match the current V4 code's docstrings/assertions verbatim.
