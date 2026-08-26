<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
ORCID:       0009-0000-6600-6171

DOI records:
  [Software] 10.5281/zenodo.22067006
  [Paper I]  10.5281/zenodo.22067118
  [Paper II] 10.5281/zenodo.22067469

Part of the V4 spectral framework, whose physics is presented in the
companion papers:
  [I]  "The spectrum of a compact internal space.
        I. Gauge structure and fermion content"
       DOI: 10.5281/zenodo.22067118
  [II] "The spectrum of a compact internal space.
        II. Effective couplings and mass scales"
       DOI: 10.5281/zenodo.22067469
-->

# Introduction: physical motivation, physical picture, and method system

> This introduction comes from the axiomatic foundation of Paper 4 (*The spectrum of a compact internal space. I. Gauge structure and fermion content*), and is the systematic account of the **"why" and "how" behind** the V4 framework. The V4 code (170 closed parameters) is the **numerical realisation** of this axiomatic framework; Paper 4 is the **axiomatic foundation** of that realisation. The two are complementary: Paper 4 answers "why physical quantities are spectral sums, why the gauge structure is SU(3)×SU(2)×U(1), why the dimension is 4", while V4 answers "what the specific numerical values of these spectral sums are, and how far they differ from the Standard-Model observations".

---

## 1. Physical motivation: why the "spectral perspective"

### 1.1 A difficulty of standard QFT

In four dimensions, the conventional **measure-based (path-integral) construction of the interacting scalar sector** is known to have a **trivial continuum limit**. This is a **theorem, not a conjecture** (the modern statement is Duminil-Copin 2022). Its meaning: the standard measure semantics is "empty" in the interacting sector — only the free field survives the continuum limit.

The framework **does not try to improve or circumvent that construction**. It takes a different route: **organise physical quantities directly at the level of the spectrum**.

### 1.2 The spectral perspective is classical and uncontroversial

Quantum field theory admits a description in which "physical content is carried by spectral data" — the **Källén–Lehmann representation** writes the two-point function as an integral of free propagators against a positive spectral density. A theory with a discrete spectrum is therefore completely encoded by **a set of masses + their multiplicities**.

The framework starts from this classical fact: **the spectral datum is the starting point, physical quantities = convergent spectral sums**, without passing through a measure / path integral.

### 1.3 Two comparable spectral precedents

- **Noncommutative geometry** (Chamseddine–Connes spectral action): derives physical actions from the spectrum of a Dirac operator. This framework differs from it in two ways: ① it uses the **discrete spectrum** of a compact internal space; ② physical quantities are **defined directly as convergent spectral sums**, not through an action functional.
- **Functional renormalisation group** (FRG effective potential): shares structural features, but this framework **does not assume a path integral**.

---

## 2. The single axiomatic input: the Disorder Axiom

The starting point of the framework is **one single axiom**:

> **There exists a minimal, unbiased, spin-1/2 change.**

"Change" is first understood as a **bijection** of a set onto itself (invertible, not an automorphism). The axiom makes its content explicit through three clauses:

- **(A1) Existence**: the change exists.
- **(A2) The quantum unit = spin-1/2**: the carrier of the change is a **two-dimensional complex Hilbert space**; the symmetry group is **minimal** — a lemma uniquely selects **SU(2) ≅ Spin(3)** (the two-dimensional fundamental representation). The two-dimensional complex representation carries the **chiral structure** (the left/right distinction).
- **(A3) Unbiasedness**: the change is unbiased with respect to its symmetry group. By the **maximum-entropy principle** (Jaynes), the statistical distribution is **uniquely fixed to be Gaussian**.

### 2.1 Why SU(2)

On a two-dimensional complex carrier, the symmetry group of a faithful continuous irreducible representation is SU(2) or U(2). Irreducibility excludes all abelian groups (an abelian group has only one-dimensional irreducible complex representations; a two-dimensional representation would necessarily be reducible — U(1) is therefore excluded). Among the non-abelian connected compact groups, the only simple Lie group with a two-dimensional faithful irreducible representation is SU(2). The **minimality principle (minimal dim)** selects **SU(2)** (dim 3) over U(2) (dim 4).

### 2.2 Why the chiral structure requires Spin(4)

The fundamental representation of SU(2) is **pseudo-real** (equivalent to its complex conjugate, realised by the antisymmetric tensor), so the chiral distinction **cannot be produced within SU(2)**. It must be realised at the level of the **full symmetry group of the carrier space**: the isometry group of the carrier sphere S³ is O(4), and its identity component **Spin(4) ≅ SU(2)_L × SU(2)_R** carries two inequivalent minimal representations **(1/2,0) and (0,1/2)** (the left- and right-handed Weyl spinors). This is the mathematical reason Spin(4) enters.

### 2.3 Unbiasedness → Gaussian → random field → scale field

Unbiasedness (G-invariance) together with the moment constraints (mean = 0, covariance), via the maximum-entropy principle, uniquely yields the **Gaussian distribution**. Realised on the emergent spacetime, this statistical content becomes a **random field** — namely the **scale field σ(x)** (the coarse-graining scale). Its coherence length L is both the radius of the internal space RP³ and the Gaussian integration width.

---

## 3. The core of the method system: the minimality principle — the axiomatic statement of "zero free parameters"

**Minimality principle**: under "irreducible + faithful", choose the one with the **minimal symmetry-group dimension**.

It is applied **three times** in the framework, as a running method:

| Application | Candidates | Dimension | Selected |
|---|---|---|---|
| symmetry group of the change | SU(2) vs U(2) | 3 vs 4 | **SU(2)** |
| colour algebra | su(3) vs so(5) vs G₂ | 8 vs 10 vs 14 | **su(3)** |
| internal-space quotient | S³/Z₂ vs lens spaces S³/Z_{2m} | \|Γ\|=2 vs 2m | **RP³ = S³/Z₂** |

**This is the axiomatic root of the framework's "zero free parameters"**: not "artificially avoiding parameter tuning", but "**uniquely fixed by minimality**" — every candidate is eliminated by the minimality principle until only one remains. The three symmetries (chiral SU(2), colour SU(3), internal RP³) share the same selection principle.

**V4 deepening (the minimality principle applied to matter content)**: V4 extends the same minimality principle **to the fermion matter** (sm_content.py) — colour = the **minimal non-trivial irreducible representation 3 (the fundamental, dimension 3)** of the algebra, the same principle that selects 2 for SU(2), 8 for SU(3), and Z₂ for RP³. Superposed with the chiral clause (A2 → SU(2)_L doublet) and colour vectoriality (anomaly cancellation: left-handed 3, right-handed 3̄) → **all 5 fermion representations are derived** (Q_L coloured + L_L colourless; u_R,d_R mirror 3̄, e_R colourless, ν_L with no light right-handed partner, Majorana). The minimality principle therefore covers three levels: gauge group + internal space + **matter content**.

---

## 4. The geometric root of the chiral structure: antipodal identification

This is the most delicate step of the framework, and the deep reason **why RP³ is RP³**:

- The action of Spin(4) on S³ is **not faithful**; its kernel is the central subgroup ⟨(-1_L,-1_R)⟩.
- The **antipodal map z ↦ −z** corresponds to the central element **(-1_L,+1_R)**: it acts as **−1** on the left-handed Weyl spinor and **+1** on the right-handed one.
- Therefore, **the chiral structure (the left/right distinction) is realised precisely by "antipodal identification"**.

**Conclusion**: the internal space must be an antipodal quotient S³/Γ, and Γ must contain the antipodal element (otherwise left/right cannot be distinguished). The minimality principle selects the admissible quotient with the smallest |Γ| → **Γ = Z₂, i.e. RP³ = S³/Z₂**. Larger quotients (lens spaces S³/Z_{2m}) also contain the antipodal element, but are eliminated by the minimality principle.

**V4 deepening (the Z₂ projection rule and the chiral content count)**: V4 specifies the antipodal action for every field type: a degree-l scalar harmonic has parity (−1)^l; the one-form pullback carries the corresponding form action; the spinor tower is selected by a lift of the antipodal map; and TT tensors are selected by their representation parity. The chosen non-trivial spin structure distinguishes the two chiral lifts. For one selected generation the resulting Standard-Model content has N_L−N_R=1, and this integer enters the dimensionless closure τ=(N_L−N_R)/(N_f·ΣY²)=1/50.

---

## 5. The emergence of dimension 4 = 3+1

The chiral two-dimensional representation needs a Clifford algebra to carry it:

- The chiral decomposition exists only in **even dimension n = 2m** (lemma).
- The semispinor dimension equation 2^{m−1} = 2 ⟹ **m = 2 ⟹ n = 4**.
- The generators γ₁…γ₄ span a **four-dimensional real space V = Cl(4)**.

**The 4 = 3+1 decomposition**: 3 dimensions come from the internal space RP³ (the codimension-1 submanifolds Σ_σ of the equi-σ surfaces of the scale field σ), and 1 dimension comes from the **normal direction ∇σ of the scale-flow parameter σ**. The spacetime metric is given by the Clifford quadratic form (Euclidean), and the Lorentz metric is obtained by analytic continuation.

**V4 deepening (dimension-generator balance, more intrinsic than the Clifford argument)**: V4 gives a dimension argument **directly tied to the gauge structure** (qcd_sector.py) — the **conformal-gauge duality N_g·ξ = 1**:

    ξ = (d−2)/(4(d−1)) = 1/8 (the d=3 conformal coupling), N_g = N_c²−1 = 8 (the su(3) generator count)
    N_g·ξ = 1  ⟺  4(d−1)/(d−2) = N_c²−1  ⟹  d = N_c = 3 (the unique positive solution (N_c−3)(N_c+2)=0)

**The d=N_c emergence**: the **3 positive roots = the colour number 3 = the internal-space dimension d** of the A₂ root system; equivalently d = rank(G)+1 = 2+1 = 3 (**geometric dimension = gauge rank + 1**). This is deeper than "chirality needs Cl(4)" — it not only fixes dimension 4, it also **locks the dimension directly to the colour number** (dimension and gauge structure are reciprocal), the framework's "geometry = gauge" identity principle.

---

## 6. The two routes converge on RP³ (a self-consistency check)

The internal space is **fixed twice** in the paper, and the two routes converge on the same object:

1. **Algebraic route**: the chiral structure (A2) requires the internal space to be an admissible free quotient of S³, the minimal admissible quotient = S³/Z₂.
2. **Statistical route**: unbiased statistics (E(4)-invariance) fixes the effective geometry to be a compact constant-curvature space S³/Γ, chirality requires Γ to contain the antipodal element, and the minimality principle selects the smallest Γ = Z₂.

**The two are not two independent assumptions, but two applications of the same minimality principle** — once for the chiral quotient, once for the effective geometry. This is the framework's built-in self-consistency check.

### The explicit chain from correlation structure to spectrum

```
scale-field statistics → effective geometry → Laplace spectrum → spectral datum
```

The spectrum of the effective geometry = λ_l = l(l+2)/L², multiplicity d_l = (l+1)² (the even-l sector). **The spectral datum = the spectrum of the effective geometry, and the effective geometry is fixed by the statistics.**

**V4 deepening (the four dualities unified = duality emergence)**: V4 generalises the "two routes" to a **four-duality unification** (the top of sm_content.py, the highest principle "duality emergence"):

    (1) conformal-gauge   N_g·ξ = 1        (conformal coupling × generator count, ξ=1/8, N_g=8)
    (2) geometric-gauge   d = N_c = 3      (internal-space dimension = colour rank, d = rank(G)+1)
    (3) UV-IR             e^{∫γ_M} = window span (the entropy-encoded scale duality, S = ln W)
    (4) spectral-physical spectral sum = physical content (the spectral representation of physical quantities)

Entropy (S = ln W = ∫γ_M) is the physical bridge: it encodes both the UV (Gaussian window) and the IR (entropy maximum). **All four dualities are faces of the same "duality emergence"**: spectrum → duality → gauge/geometry/entropy → emergence → 4D physics. The two routes of Paper 4 (algebraic + statistical) are promoted in V4 to four dualities, each with a precise numerical closure (the Lean 21 theorems of N_g·ξ=1, the unique positive solution of d=N_c, ∫γ_M=139.253, the 170-parameter spectral sum).

---

## 7. The spectral-sum representation (the framework definition) — "non-perturbative = spectral sum"

The framework definition is the paper's definitional evaluation scheme:

- **Basic data**: the scalar Laplace spectrum of RP³, λ_l = l(l+2)/L² (even l, multiplicity d_l=(l+1)²) + the scale flow.
- **Physical quantities** = **absolutely convergent spectral sums** of the form Q = Σ_{l even} d_l · f(λ_l)/(λ_l+m²)^p (p > 3/2), or the analytic closed forms given by the scale flow.
- **Values** = evaluation at the endpoint σ_C.
- **The framework-definition analogues of the OS axioms**: regularity = absolute convergence of the spectral sums; Euclidean invariance = SO(4)-invariance of the spectral data; reflection positivity = reflection positivity of the lattice-regularised measure (closed under weak limits); clustering = the exponential decay implied by the positive lower bound m_δ.

**Core insight**: **"non-perturbative" needs no resummation in the framework** — physical quantities are never defined by a perturbative series, but by **convergent spectral sums**. This circumvents the triviality obstruction of the 4D interacting sector.

**Formal correspondence (a structural correspondence that does not pass through a measure, Paper 4 sec 9)**: the bridge of the interacting sector is not a Gaussian measure, but a **mapping dictionary + Weyl displacement** — it assigns each closed form of the spectral datum its role in the physical structure (without a measure, without Minlos, without OS reconstruction):

| Closed form of the spectral datum | Role in the physical structure |
|---|---|
| λ (convergent spectral sum) | the e⁴ vertex |
| m_δ | the single-particle mass (spectral pole p²=m_δ²) |
| ⟨E⟩ (condensate) | the Weyl displacement parameter of the physical vacuum |
| {M_l} (mass tower) | the single-particle states of the free sector |

Condensation = the coherent-state displacement of the Fock vacuum **|Ω_eff⟩ = W(⟨E⟩)|Ω⟩** (W is the Weyl operator, the displacement parameter is a closed form of the spectral datum). **The non-perturbative content = the spectral-sum representation**: λ itself is a convergent spectral sum (not the leading order of an expansion); the amplitude at each order is an explicit function of the spectral data (tree M⁰=−6λ, one-loop M¹=−18λ²B_ren(s), dispersion-subtracted renormalisation); **no resummation is needed** — the quantity is never defined by a series.

**The eight FSA axioms (Paper 4 sec 5, the framework's self-contained statement)**:
- **Definitional (FSA1–3)**: FSA1 the spectral datum S=(M,{λ_l},{d_l}) (a compact three-manifold + spectrum + multiplicities, no hand parameters); FSA2 physical quantities = spectral sums or closed forms (**not measure expectations — a constitutive definition**); FSA3 the state space = the reflection-positive reconstruction space (the free sector = Fock space).
- **Kinematic (FSA4–7)**: FSA4 probability (the Born rule, unique by Gleason's theorem); FSA5 dynamics (unitary evolution, Stone's theorem); FSA6 composition (tensor product); FSA7 locality (spin-statistics). On the free sector each reduces to a standard theorem.
- **Mapping (FSA8)**: the physical structure = the reconstruction of the spectral datum (the free sector is a theorem, the interacting sector is stipulated by the framework definition).
- **The formulation criterion (11 structural items)**: state space, observables, probability, dynamics, composition, locality, spectrum, correlation functions, scattering, thermal states, measurement — each marked as "derived from the spectral datum / defined within the framework definition / axiomatic standard kinematics".

**Analytic mapping: condensation and the positive spectral lower bound (Paper 4 sec 7)**:
- **Well-definedness + analytic control**: the spectral sum Q_p(m²)=Σ d_l(λ_l+m²)⁻ᵖ is absolutely convergent, positive, and analytic for **p > 3/2** (= (1/2)dim M, the Weyl exponent), bounded by Q_p ≤ C_p·vol(M)·m^{3−2p}.
- **Spectral positivity**: the mass-tower spectral measure ρ(μ²)=Σ d_l δ(μ²−M_l²) is non-negative, supported on [m_δ², ∞).
- **Condensation (Landau potential)**: V(E) = (1/2)m²_long E² + (λ/4)E⁴, m²_long = −λ⟨E⟩² < 0, unique non-trivial minimum E=⟨E⟩, curvature **m_δ² = V″(⟨E⟩) = 2λ⟨E⟩² = −2m²_long > 0** — the mass gap is derived from the spectral datum (not an input).
- **Positive spectral lower bound**: M_l² = λ_l + m_δ² ≥ m_δ² > 0 (no zero-mass mode).
- **Structural mapping**: the spectral sums = the trace of the internal Green operator, Q_p = Tr[(Δ_M+m²)⁻ᵖ] — the precise correspondence between the spectral datum and the reconstructed propagator.

---

## 8. The problems we solve

1. **The emergence of gauge structure**: from the disorder axiom + the minimality principle, **zero free parameters** derive SU(3)×SU(2)_L×U(1)_Y — 8 colour generators, 3 weak + 1 hypercharge, 12 gauge bosons in total (KK zero modes).
2. **The mass gap (positive scalar mass parameter, the three-step mechanism of Paper 4 sec 8)**:
   - **① The long-root tachyon**: the J=2 deformation mode of the colour connection (the (2,1) representation), eigenvalue λ_long = C₂(2,1)/L² = 16/L². The condensation onset **L_c = √π** (the Beckner–Hirschman entropic uncertainty bound H_x+H_p ≥ 1+lnπ, Gaussian equality → σ_c=1/√2 → L_c=√π), R_c = 6/π; **m²_long = (8/3)(R−R_c)**, tachyon condensation when R<R_c → SU(2)_R broken to U(1)_R.
   - **② The conformal Laplacian strictly positive**: spec(Δ+R/8) = {(l(l+2)+3/4)/L²} ⊂ [3/(4L²), +∞) > 0 — guarantees that the quartic coupling λ is non-perturbatively strictly positive (this is the central analytic input for the positive lower bound).
   - **③ The RP³ spectrum excludes zero modes**: the colour-singlet sector has no zero-mass mode — H¹_dR(RP³;ℝ)=0 (no harmonic 1-forms); for TT tensors the Bochner formula □_L ω = ∇*∇ω + Ric·ω, with Ric = (2/L²)g > 0 strictly positive; the unique scalar zero mode (the l=0 constant function) is the glueball field E itself (carrying the condensate, with fluctuation mass m_δ>0).
   - **The condensation closed form (thm:massgap)**: the glueball field **E = Tr F_μνF^{μν}** (colour singlet), the condensate VEV **⟨E⟩² = (8/3)(R_c−R)/λ**; the fluctuation mass **m_δ² = V″(⟨E⟩) = 2λ⟨E⟩² = (16/3)(R_c−R) > 0** (the lowest colour-singlet excitation); the condensation breaks no continuous symmetry → no Goldstone boson.
   - **The effective potential = spectral sum**: the quartic expansion of V(E) = Σ_l d_l f(λ_l+ξR+gE²) (m²_long = 2gΣ d_l f′, λ = 6g²Σ d_l f″; when f is the conformal-Laplacian logarithm, λ = 6g²Σ d_l (λ_l+ξR)⁻², a polygamma closed form) — **the Landau form is a quartic truncation, not an independent input**; the endpoint physical quantity V_eff(k) = −(C/2)(k⁴−M_P⁴). This is the framework's mass-gap parameter (the positive spectral lower bound of the colour-singlet sector).
3. **Formal correspondence (without a measure)**: the path outside the triviality theorem — the free sector is recovered by OS reconstruction (the two methods coincide), and the interacting sector is crossed by the framework's formal correspondence (mapping dictionary + Weyl displacement, see §7).
4. **The precise locus of the triviality theorem (Paper 4 sec 10)**: the triviality theorem (Aizenman–Duminil-Copin 2021) — the 4D φ⁴ continuum limit is Gaussian, λ→0, so the framework's λ>0, ⟨E⟩≠0, m_δ>0 have **no counterpart** in the standard measure semantics. This is a **theorem of the standard semantics** (which fixes its boundary), not an open item of the framework.
5. **Three kinds of boundary (the classification of Paper 4 sec 10)**:
   - **(a) Excluded by a theorem**: the standard-semantics continuum realisation of the interacting scalar is excluded by triviality (a theorem of the standard semantics, not an open item of the framework);
   - **(b) Conceptual gap (closed within the framework)**: the spectral-sum representation of non-perturbative quantities, the formal correspondence — closed by definitions and theorems;
   - **(c) Technical boundary**: the 4D operator-level UV completion (a technical boundary of the standard semantics); the framework's physical quantities are defined by spectral sums and do not depend on it.
6. **The generation count n_g=3**: V4 evaluates the spectral-capacity closure `(n+3/2)<(kL)^2` on the even RP3 Dirac positions `n=0,2,4,...`. The endpoint fixed point `kL=2.49353433252` gives `(kL)^2=6.2177`, so the retained positions are `n={0,2,4}` and the next position is `7.5`. The same retained labels supply the extrusion order of the generation hierarchy.
7. **Product-space bridging (Paper 4 Appendix B)**: the spectral datum = the internal-mode content of the explicit action **S_prod = S_g + S_f + S_s** on R⁴×RP³ (7D gauge / fermions with internal parity / the colour-singlet scalar φ's zero-mode amplitude E(x) coupled as (g/2)E²φ²):
   - **thm:match one-loop matching**: the one-loop effective potential in the internal-trace order **matches the framework's spectral sums term by term** — c_k = (−1)^{k+1}g^k/(2k)·ζ(k;m_δ²), ζ(s;m²)=Σ d_l(λ_l+m²)⁻ˢ; the k=2 coefficient (g²/2)ζ(2;m_δ²) > 0 = the quartic coupling λ (conformal shift ξR → physical mass m_δ² replacement); k=1 = the divergent diagonal at p=1, renormalised value = the long-root mass m²_long.
   - **KK decoupling**: the zero-mode effective action = a 4D effective theory (prop:zeromode/eff4d/decoupling), the massive modes decouple.
   - **Status**: S_prod is an auxiliary generating device (not a renormalisable 7D QFT; power-counting non-renormalisable but the internal-trace order suffices — the framework's physical quantities are the spectral sums themselves); the full 7D one-loop lies outside the framework definition. Corresponds to V4's spectrum→4D KK-reduction chain (G_N→M_P→M_G→KK masses m_n=(n+3/2)/kL·M_G, window edge kL·M_G=M_P·√π).

---

## 9. Deep insights (synthesised)

1. **The spectral language is definitional, not approximate**: physical quantities are defined by spectral sums, the spectrum is fixed by statistics, the statistics is fixed by a single axiom — the whole chain has no free parameter.
2. **The minimality principle is the axiomatic statement of "zero free parameters"**: its three applications (SU(2)/su(3)/RP³) are all "uniquely fixed by minimality", not artificial parameter tuning.
3. **Antipodal identification is the geometric root of chirality**: the left/right distinction = the ±1 assignment of the antipodal map acting on (1/2,0)⊕(0,1/2); this is the deep reason for the existence of RP³.
4. **The convergence of the two routes is a built-in self-consistency check**: the algebraic (chiral quotient) and the statistical (effective geometry) routes independently derive the same RP³.
5. **The formal correspondence is the way out of triviality**: the difference between the standard measure semantics and the framework definition lies in the "bridge" (measure construction vs formal correspondence), not in the physical content; the free sector coincides (recovery theorem), the non-trivial sector's content is complete in the framework.
6. **"Non-perturbative = spectral-sum representation"**: no resummation is needed, because the quantity is never defined by a series.
7. **Dimension 4 and colour number 3 share one origin**: dimension 4 comes from the semispinor dimension equation of chirality, the colour number 3 (su(3)) comes from the minimality principle — both emerge from the same batch of inputs (the two-dimensional chiral representation) of the disorder axiom.

---

## 10. The division of labour between Paper 4 and the V4 code

| | Paper 4 (Paper I: Gauge structure and fermion content) | V4 code (numerical realisation) |
|---|---|---|
| Role | axiomatic foundation | specific spectral geometry + gauge structure + numerical couplings |
| Answers | why spectral sums, why SU(3)×SU(2)×U(1), why dimension 4 | the specific values of the spectral sums, how far from SM observations |
| Input | the disorder axiom (unique) | G_N (the unique dimensional anchor) |
| Output | spectral datum + formal correspondence + mass-gap parameter | 170 closed parameters (169 DERIVED + 1 OBSERVED) |
| Honest boundary | colour algebra fixed by minimality, generation count fixed by a window convention (non-dynamical) | the numerical comparison left to a follow-up (completed by V4) |

The task Paper 4 explicitly left open ("the numerical comparison is left to a follow-up paper") is exactly what the V4 code completes — **V4 is the numerical verification of Paper 4**. Together, from "one axiom" to "170 physical quantities consistent with the Standard Model", they constitute the complete narrative of the framework.

---
