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

# Part 1 Symmetry principles

> This part, like a lecture, explains all the low-level symmetry laws of the V4 framework thoroughly. Core stance: **the framework has no "extra-assumption" symmetries — all symmetries emerge from "content = structure"**, unified under the highest principle "duality emergence".

---

## Chapter 1 Framework overview: coarse-graining emergence

### 1.1 The question the framework answers

The Standard Model has 19 free parameters (3 gauge couplings, 9 fermion masses, 4 CKM parameters, the Higgs mass, the QCD θ-angle, 2 Higgs-potential parameters). Where do these parameters come from? The standard answer: "they are inputs of nature, only measurable."

The V4 framework gives a different answer: **these parameters are not inputs, but emerge from a deeper geometric structure — the spectrum of the internal space RP³.** The only true input is Newton's constant G_N (one dimensional anchor); everything else is computed from first principles.

### 1.2 The core idea: the spectral representation

The methodological cornerstone of the framework is: **a physical quantity = a function of the internal-space spectrum.**

Imagine the antipodal quotient RP³ (real projective 3-space) of a 3-sphere S³ as the "internal space". On this internal space, every field of the Standard Model (scalar, vector, fermion, gravitational tensor) has a set of discrete vibration modes (like the standing waves of a drumhead). The **eigenvalue spectrum** of these modes carries all the physical information:

- mass = spectral eigenvalue
- energy gap = spectral interval
- generation = the number of modes that fit in the window
- coupling = the overlap integral of the spectrum

This is the "spectral representation": physical content is defined by spectral data.

### 1.3 The emergence picture: spectrum → duality → emergence → 4D physics

![Figure 1: framework overview](figures/fig01_overview.png)

Four stages:

1. **Spectrum (discrete data)**: the spectrum of the field modes on RP³; the Weyl law counts the degrees of freedom, the heat kernel gives the spectral density, the Z₂ winding number gives the topology.
2. **Duality (the four dualities)**: the spectral data are bridged into continuous structure through four "dualities" —
   - conformal-gauge duality: ξ·N_g = 1
   - geometric-gauge duality: d = N_c = 3
   - UV-IR duality: the window span
   - spectral-physical duality: the spectral-sum representation
3. **Emergence (continuous structure)**: the gauge group SU(3)×SU(2)×U(1), geometry, entropy S = ln W = ∫γ_M.
4. **4D physics (observable)**: 147 closed parameters, compared with the Standard-Model observations.

### 1.4 The single dimensional anchor: G_N

The framework's dimensional chain starts from the single observed value G_N:

```
G_N → M_P = 1/√(8πG_N) → M_G = M_P·√π/kL → KK mass spectrum → all parameters
```

M_P is an identity (not a fit), M_G is the emergence scale. **Key property: all dimensionless predictions (M_G/M_P, g₂) do not depend on the absolute value of M_P** — M_P rescaling invariance guarantees that the closure is geometric, not anchored.

---

## Chapter 2 The spectral-representation methodology (the three spectral-language levels)

The framework's "spectral-sum representation" methodology has three levels, in decreasing depth:

### 2.1 Level 1: the discrete spectrum (used deeply ✅)

Mass, gap, generation, coupling are all given by discrete spectral eigenvalues. This is the deepest-used level of the framework.

### 2.2 Level 2: the spectral sum (partly used ⚠️)

The trace density η, the composite-operator amplitude Π², the window capacity (kL)². The spectral sum = summing over modes, the driving quantity of the FRG flow.

### 2.3 Level 3: continuum limit / regularisation (consolidated 2026-08-15)

- **Weyl law**: degree-of-freedom counting (scalar 1 / vector 2 / spinor 1 / TT 3) — the spectral-library self-consistency check.
- **Heat-kernel expansion**: a₀ = 7·Vol, a₂, a₄ — the precise spectrum-to-geometry correspondence.
- **KK reduction**: the dimensional anchor chain G_N → M_P → M_G → KK masses m_n = (n+3/2)/kL·M_G.
- **Two-end regularisation**: UV Gaussian window (heat kernel, precision +0.002%) + IR entropy maximum (entropy integral ∫γ_M).

**Key clarification**: in 3D there is no conformal anomaly, so the heat-kernel a₄ is a geometric invariant rather than a β function; the true "spectrum→4D" needs the KK-reduction mechanism. The framework's regularisation is two-end (UV Gaussian window + IR entropy maximum), not a single-end cutoff.

---

## Chapter 3 Content symmetries: "number is structure"

This is the lowest, most rigid symmetry — integer identities, Lean 4 proved, zero free parameter.

### 3.1 N_L = N_g = 8: fermion content = colour generators

![Figure 6: content symmetry N_L = N_g = 8](figures/fig06_content_symmetry.png)

```
N_L = 8 = N_g = N_c² − 1        (left-handed component count = colour generator count)
N_R = 7 = N_g − 1               (right-handed component count = generators − 1)
```

- **What it is**: per generation, the left-handed doublet Q_L(3×2=6) + L_L(1×2=2) = 8 Weyl components; the right-handed singlets u_R(3)+d_R(3)+e_R(1) = 7. The colour gauge generators N_g = N_c²−1 = 8.
- **Why it matters**: this is the symmetry that "the fermion content is determined by the gauge structure" — the chiral carrier and the gauge carrier are isomorphic, both living in an 8-fold content. It upgrades "the fermion content is external data" to "the content is determined by the gauge structure".
- **How it is used**: it gives the gauge origin of the **numerator** N_L−N_R = 1 of τ, r12, s0 — "8 vs 7", not an arbitrary 1.

### 3.2 ΣY = 0 and ΣY² = 10/3: hypercharge anomaly cancellation

```
ΣY  = 0       (zero hypercharge trace = U(1)_Y gravitational mixing-anomaly cancellation)
ΣY² = 10/3    (the first non-zero hypercharge moment)
```

- **What it is**: summing the hypercharge over the 15 Weyl fermions per generation, ΣY = 6·(1/6)+3·(2/3)+3·(−1/3)+2·(−1/2)+1·(−1) = 0.
- **Why it matters**: it answers "why ΣY² and not ΣY" — ΣY=0 is the zero constraint of anomaly cancellation, ΣY² is the first non-zero moment, naturally becoming the normalisation choice. Previously a "scheme convention", now "the inevitability of anomaly cancellation".

### 3.3 N_L − N_R = 1: chiral asymmetry = the Z₂ topological charge

- **What it is**: 8−7=1 is odd.
- **Why it matters**: odd = the **non-trivial spin structure** of RP³ (π₁(RP³)=Z₂, winding once around the antipodal loop is an odd winding number). This is the same topology as the glueball's n mod 2 = parity = Z₂ winding number.
- **How it is used**: it is the numerator of τ, ⟨χ⟩ = (N_L−N_R)/N_f = 1/15, the topological source of the torsion.

### 3.4 τ = 1/50: the core dimensionless modulus (the three-layer skeleton)

```
τ = (N_L−N_R)/(N_f·ΣY²) = 1/(15·10/3) = 1/50 = 0.02
```

τ is **the single most important number** of the framework — it enters the EC torsion, the curvature correction, the generation ladder, the spectral tilt, T_CMB, kL_CMB, and almost all closures. Its three-layer first-principles skeleton:

1. **the Z₂ topological source**: the chiral asymmetry N_L−N_R=1 is the non-trivial spin structure;
2. **hypercharge anomaly cancellation**: ΣY=0 ⇒ the normalisation must be ΣY²;
3. **the EC field equation**: the torsion T ~ κ²j₅, screened by the hypercharge polarisation Π=ΣY².

**Core insight**: the **tension** between the chiral asymmetry (Z₂ topology, non-zero) and the hypercharge anomaly cancellation (ΣY=0, zero) determines τ — the "non-zero chiral source" constrained by the "zero hypercharge trace".

### 3.5 The pure content-ratio family

Hierarchy ratios = content ratios, not free inputs:

```
r12 = m_ν1/m_ν2 = (N_L−N_R)/ΣY² = 3/10
r23 = m_ν2/m_ν3 = 1/(√3·TrY²) = 3/(10√3)
5/3 = Tr(Y²)/Tr(T₃²)             (GUT normalisation)
8/7 = n_L/n_R                     (left/right content ratio → CP phase)
9/8 = 1/(1−(Y_d/Y_l)²)            (hypercharge identity, exact algebra)
```

---

## Chapter 4 The conformal-gauge duality: dimension-generator balance

This is the deepest symmetry structure of the framework — **"not energy, but a conserved quantum number / information"**.

### 4.1 N_g·ξ = 1: the core identity

```
ξ = (d−2)/(4(d−1)) = 1/8    (the d=3 conformal coupling)
N_g = N_c²−1 = 8            (the su(3) generator count)
N_g·ξ = 1  ⟺  (N_c−3)(N_c+2) = 0  ⟹  N_c = 3 (the unique positive solution)
```

- **What it is**: the conformal coupling ξ and the gauge generator count N_g are **reciprocal**.
- **Why it matters**: it **derives d=N_c=3 at the same time** — "the colour number emerges from conformal balance". This is the key clue to why the colour number 3 is 3.
- **Physical reading**: conformal symmetry (ξ) ↔ gauge symmetry (N_g) are complementary; the information-conservation reading 2⁻³×2³ = 2⁰ (the d=3 special value).

### 4.2 N_g·Δ = 2(d−1): the conformal-weight form (holds for all d)

```
Δ_f = d/2 = 3/2          (fermion conformal weight)
Δ_s = (d−2)/2 = 1/2      (scalar conformal weight)
N_g·Δ_s = 2(d−1) = 4
ξ = Δ/(2(d−1))            (exact, all d)
```

- **How it is used**: this is the "symmetry weapon" that turns candidate parameters into first principles. Δ_f appears in the 3/2 factor of the proton mass; Δ_s is the "unifying key of the corrections" — appearing simultaneously in the 31/32 of m_p (denominator) and the (1−τ/2) of T_CMB (numerator).

### 4.3 d = N_c = 3: the geometric-gauge duality

- **Mechanism**: the 3 positive roots of the A₂ root system = the 3 internal-space dimensions; d = rank(G)+1 — the unique positive solution of N_g·ξ = 1 ((N_c−3)(N_c+2)=0, Lean proved).
- **State**: ✅ closed (N_g·ξ = 1 ⟹ d = N_c = 3 unique positive solution).
- **Excluded directions** (excluded, confirmed not a known index theorem): no conformal anomaly in 3D (not c-theorem/a-theorem), Dirac index = 0 (not Atiyah–Singer), χ(RP³)=0 (not Euler) — d=N_c is the framework's own dimension-generator balance.

---

## Chapter 5 Geometric-dynamics symmetries: EC torsion and the J=2 squash

"One geometric dynamics, several levels" — the same geometric structure acting at different levels.

### 5.1 The λ_EC eigenvalue: the gravity higher-order effect

```
λ_EC = N_g(1+τ/2)² + 6 = 14 + 8τ + 2τ²
  14  = λ_TT = 2·N_R = 2·7        (TT zeroth order = 2× right-handed singlet)
  8τ  = N_g·τ                      (first-order torsion = gravity higher-order effect)
  2τ²                               (second-order torsion)
```

### 5.2 s0/N_R = 1/175: the symmetry correction of the pure content ratio

This is the key convergence of 2026-08-16 — three candidate-level deviations (α_sd≈3/2, V_us≈e^(−d/2), factor 5≈5) are **not defects, but the exact symmetry form itself contains the s0/N_R correction**:

```
α_sd = Δ_f(1−s0/N_R) = (3/2)(1−2τ/7)          (−0.051%)
screening factor = ΣY²·Δ_f(1−4s0/N_R) = 5(1−8τ/7)      (+0.042%)
s0/N_R = n_broken/(N_f·ΣY²·N_R) = 2/(15·(10/3)·7) = 1/175
```

### 5.3 s0 = N_g·τ/(d+1): the squash amplitude from first principles

```
s0 = n_broken·τ = N_g·τ/(d+1) = 8τ/4 = 2τ   (exact identity)
```

- **What it is**: the amplitude of the squash (the J=2 isometry breaking SU(2)_R→U(1)_Y).
- **Why it matters**: it writes the squash amplitude as "the first-order torsion N_g·τ ÷ (d+1)", a geometric-dynamics derivation, not a content-ratio fudge.
- **The factor 2**: n_broken = 2 is the broken generator count; N_g = (d+1)·n_broken = 8.

### 5.4 Pairing conservation: the conservation law of the squash level transfer

![Figure 7: squash pairing conservation](figures/fig07_squash.png)

The squash is a **symmetry transformation** — it does not change the physical content, only redistributes it between levels, hence conservation:

```
v·m_ν3 = constant       (EW ↔ seesaw level transfer, exact to first order)
(1−s0·κ)(1+s0·κ) = 1 − (s0·κ)²
m_ν1⁴·weight = constant   (seesaw ↔ dark energy, exact to first order)
(1+s0·κ)⁴(1−4s0·κ) = 1 − 6(s0·κ)² − …
```

**Key progress**: the signs/multiples of the 7 squash corrections are **not free choices**, but constrained by two conservation laws — once the sign of v is fixed, the sign of m_ν3 is fixed by the conservation law.

### 5.5 The geometric dynamics of the three gauge couplings

```
g₂:  N_c(1/α_SM − 1/α_W + τ²π/2) = 1  ⟺  N_g·ξ = 1   (conformal-gauge duality + EC torsion)
g₁:  g₁ = g₂·κ(2τ)，s0 = n_broken·τ = 2τ             (J=2 squash normalisation)
g₃:  g₃ = g₂·(1 + α_GUT²/K)，K = J(J+2)/d = 8/3       (long-root bifurcation, A₂ root system)
```

The corrections of the three couplings are all "discrete content (N_c, n_broken, J, d) × geometric dynamics (conformal-gauge duality, EC torsion, J=2 squash)".

---

## Chapter 6 The 2π Euclidean period family

![Figure 5: the 2π family](figures/fig05_two_pi.png)

This is the framework's most "running" thread — **the same 2π closes both the UV and the IR**:

```
ε    = e^(1/2π)              (the zero point of the EW ratio)
a0   = cH0/(2π)              (transparent-gravity IR)
2L   = √(2π)                 (entropy minimal distance / window width)
kL   ≈ √(2π)                 (the window)
r    = (1/2π)²               (tensor-to-scalar ratio)
Δ²_0 = (1/2)·(1/2π)²         (scalar zero point)
sin²θ13 = (1/2π)²·√3/2       (the 2π imprint)
g_A  = 4/π = N_g·Δ_s/π       (nucleon axial coupling)
σ    = (λ_TT/π)Λ²            (string tension)
m_ν3 = v²·(2π)²/k_GUT        (Weinberg operator)
```

- **Physical meaning**: 2π is the **Euclidean period** — the causal-horizon temperature of the window T_eff = k/(2π).
- **Role**: the hierarchy v/ε/Λ is the dilaton powers {1,1,10}, whose public thread is 2π. The non-perturbative pinning of the six BBN constants (g_A=4/π, δ_N=√3/(3(2π)²), etc.) also all falls on this line.

---

## Chapter 7 Spectral symmetries: Weyl law, Z₂ winding number, and glueballs

### 7.1 The Weyl-law DOF counting (spectral-library self-consistency)

```
scalar 1 / vector 2 / spinor 1 / TT 3
```

This is the precise "spectrum → geometry" correspondence (heat kernel a₀ = 7·Vol etc.).

### 7.2 The spectral eigenvalue family

```
λ_TT     = 14        (TT Lichnerowicz lowest eigenvalue, n_grav=0)
λ_vector = 4         (gluon Killing lowest eigenvalue l=1, (l+1)²=4)
λ_gluon  = 4         (RP³ vector l=1)
```

### 7.3 The unified glueball spectrum (the conformal excitation unit N_g·ξ = 1)

```
λ = 2λ_gluon + C₂(J) + n·(N_g·ξ)
N_g·ξ = 8·(1/8) = 1   (the conformal excitation unit)
0⁺⁺ n=0 → 8; 2⁺⁺ n=0 → 16; 0⁻⁺ n=1 → 17; 0⁺⁺* n=2 → 18
2⁺⁺/0⁺⁺ = √(16/8) = √2
```

### 7.4 n = the Z₂ winding number of RP³ (topological charge)

```
n mod 2 = π₁(RP³) = Z₂
n even → P=+, n odd → P=−     (parity = parity, excluding radial nodes)
```

n unifies topology (parity) and radial (value). Same origin as the Z₂ topology of N_L−N_R=1.

### 7.5 Confinement self-consistency

```
σ/T_d² = (14/π)(9/16) = 5/2
```

The string tension σ = (λ_TT/π)Λ² and the deconfinement T_d = (λ_vector/N_c)Λ are determined uniformly by the geometric spectrum.

---

## Chapter 8 Conservation laws: content conservation under symmetry transformations

### 8.1 The g₂ conservation law (Lean 21 theorems)

```
N_c(1/α_SM − 1/α_W + τ²π/2) = 1
```

Isomorphic to N_g·ξ=1 (colour self-reflexivity N_c×(1/N_c)=1 + torsion cancellation).

### 8.2 The squash level-transfer conservation (see §5.4)

### 8.3 ρ_Λ symmetry invariance

m_ν1⁴ carries +4s0·κ, the weight (1−4s0·κ) cancels it exactly → the dark-energy density is conserved under the squash level transfer.

**Unified structure**: the conformal-gauge duality conserves the gauge content, the squash level transfer conserves the scale content — both are "content conservation under symmetry transformations".

---

## Chapter 9 Transparent gravity: spectral zero mode, no dark matter

```
G_N = 1/(8π·Z_phys·M_P²), Z_phys ≈ 1 (matter back-reaction 0.2%)
a0 = cH0/(2π)·√(4/3) = 1.206e-10 m/s² (transparent-gravity IR, not ad hoc MOND)
```

- **What it is**: gravity emerges from the zero mode of the TT spectrum.
- **Why it matters** (key user insight): the framework's gravity is **transparent** — no curved spacetime, no self-interaction, gravity passes through matter unshielded. Hence **no dark-matter particle** (Ω_DM is a flatness-closure quantity), and no ad hoc MOND (a0 is the IR behaviour of transparent gravity).
- **How it is used**: the rotation curve transitions automatically from 1/r² to 1/r for a < a0 — the effect for which GR needs dark matter / MOND compensation, the framework gives directly from first principles.

---

## Chapter 10 The entropy core and duality emergence (the highest principle)

### 10.1 The entropy core: the S = ln W Boltzmann analogy

![Figure 8: the entropy core](figures/fig08_entropy.png)

```
∫γ_M = ln(kL·M_G/H0) = ln(window span) = 139.253
window span = e^139.253 = 3×10^60 = phase-space volume
H0 = M_P·√π·e^(−∫γ_M)
```

- **Statistical-mechanics reading**: γ_M = the entropy production rate (dS = γ_M d ln k); total entropy S = ∫γ_M d ln k = ln(window span) = Boltzmann S = ln W.
- **Duality emergence driven by "disorder"**: the UV Gaussian window (ordered, scale-invariant) → IR entropy maximum (disordered, maximal entropy).

### 10.2 The four dualities unified

| Duality | form | type |
|---|---|---|
| conformal-gauge | ξ·N_g = 1 | symmetry duality |
| geometric-gauge | d = N_c | dimension duality |
| UV-IR | e^∫γ_M = window span | scale duality (entropy-encoded) |
| spectral-physical | spectral-sum representation | representation duality |

### 10.3 The highest principle

**"duality emergence"**: spectrum → duality → gauge/geometry/entropy → emergence → 4D physics. The four are unified in the different faces of "duality"; **entropy (S = ln W) is the most physical bridge** — it encodes the UV (Gaussian window) and the IR (entropy maximum) together, and determines the IR end (H0, Λ are maximum-entropy equilibrium states).

---

## Chapter 11 The symmetry dependency graph

![Figure 2: the symmetry dependency tree](figures/fig02_dependency_tree.png)

### 11.1 Core conclusions

1. **There are only 4 true "sources"**: the RP³ geometry (including π₁=Z₂ and the ξ=1/8 conformal structure), the 2π period, the SM field content (15 Weyl + hypercharge table), the gauge algebra (the N_g of su(3), the n_broken of SU(2)_R breaking).
2. **Two "bridges" weld the sources shut**: N_L=N_g (content = gauge) and N_g·ξ=1 ⟹ d=N_c (conformal = gauge = geometry) — the deepest crossing point of the framework's "content = structure".
3. **τ is the single "master switch"**: after τ=1/50 emerges from the content, almost every layer-4,5 symmetry depends directly or indirectly on τ.
4. **2π is the single "running quantity"**: a line independent of τ, from ε, a0, 2L, kL all the way to the GW ratio, the tensor-to-scalar ratio, the BBN constants.
5. **The derivation tree is one-way acyclic**: τ does not back-derive N_L−N_R, d=N_c does not back-derive ξ — this is exactly the expression of the framework's "zero free parameters".

### 11.2 All closed (the EC field-equation variation is completed)

The framework's symmetries are **all closed** — from the integer identities to the EC field-equation variation, each item has a first-principles proof (reproduce_v4 exit 0 + Lean 4 exit 0):

1. **The τ theorem**: the EC field equation δS/δK = 0 → τ/L = κ²·j₅, the window capacity 2πkL⁴ **cancels exactly** between the bare field equation and the hypercharge screening, giving τ = (N_L−N_R)/(N_f·ΣY²) = 1/50 **EXACT** (ec_structure.py).
2. **s0/N_R = 1/175**: the pure content ratio n_broken/(N_f·ΣY²·N_R), one half of the J=2 EC first-order torsion N_g·τ (the factor 2 = (d+1)/2, pinned).
3. **the κ² of g₁, the α²/K of g₃**: the 5/8 = ΣY²·Δ_f·ξ of δ_g1 is the conformal-gauge duality N_g·ξ=1; K = J(J+2)/d = 8/3 is a geometric-dynamics origin (made explicit 2026-08-16); the g₂ conservation law is Lean 4 proved.
4. **d = N_c = 3**: the unique positive solution of N_g·ξ = 1 ((N_c−3)(N_c+2)=0), the 3 positive roots of the A₂ root system = the 3 internal-space dimensions.
5. **N_L = N_g = 8**: an integer identity (Lean 9 theorems proved, fermion_content.lean).

All five are closed, none open.

---
