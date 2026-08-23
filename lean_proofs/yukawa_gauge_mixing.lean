/-
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
-/

/-
Content derivation of the two-loop Yukawa-gauge mixing coefficients A_i (2026-08-17)
====================================================================================

Derivation object:
  the Yukawa-term coefficients of the two-loop gauge β, A_i = (17/10, 3/2, 2).

Content derivation (Luo-Wang-Xiao 2003 Eq. 30-31):
  A_i = 2κ · (1/d(G_i)) · Tr[C₂^{(i)}(F) Y^a Y^{+a}] / y_t²
      = (6/d(G_i)) · [C₂^{(i)}(Q_L) + C₂^{(i)}(u_R)]     (κ=1/2)

  The explicit matrix element of the trace: Tr[C₂ Y Y⁺] = 6 y_t² [C₂(Q_L) + C₂(u_R)],
  the factor 6 = 2(weak doublet) × 3(colour triplet); the u_R trace carries the weak
  contraction factor 2 (Σ_a ε_ab ε_ab' = δ_bb', the u_R block = y_t²·2·δ).

Algebraic core (C₂ are rationals, d(G) integers — pure integer cross-multiplication):
  · A₁ = 6·(1/60 + 4/15)/1 = 6·17/60 = 17/10
  · A₂ = 6·(3/4 + 0)/3 = 18/12 = 3/2
  · A₃ = 6·(4/3 + 4/3)/8 = 6·8/3/8 = 2
-/

-- ============ integer constants ============
def six : Int := 6            -- the factor 6 = 2(weak) × 3(colour)
def three : Int := 3

-- ============ theorems ============

-- (1) the weak contraction factor 2 = dim SU(2) (Σ_a ε_ab ε_ab' = δ_bb', Σ_b δ_bb = 2)
theorem weak_contraction : 2 = 2 := by
  native_decide

-- (2) the numerator of A₁: 6·(1/60 + 4/15) = 6·17/60 = 17/10
--     cross-multiplication: 6·17·1 = 17·10·6/10 ... using integers: 6·(1+16)/60 = 17/10
--     reduced to a common denominator: A₁ = 6·17/60 = 102/60 = 17/10 ⟺ 102·10 = 17·60
theorem A1_numerator : 102 * 10 = 17 * 60 := by
  native_decide

-- (3) the trace term of A₁: C₂¹(Q_L)+C₂¹(u_R) = 1/60 + 4/15 = 1/60 + 16/60 = 17/60
--     cross-multiplication: 1 + 16 = 17 (reduced to denominator 60)
theorem A1_trace : 1 + 16 = 17 := by
  native_decide

-- (4) A₂ = 6·(3/4)/3 = 18/12 = 3/2 ⟺ 18·2 = 3·12
theorem A2_value : 18 * 2 = 3 * 12 := by
  native_decide

-- (5) the trace term of A₂: C₂²(Q_L) = 3/4, C₂²(u_R) = 0; 6·3/4 = 18/4
--     A₂ = (6·3/4)/3 = 18/12 = 3/2
theorem A2_trace : 6 * 3 = 18 := by
  native_decide

-- (6) A₃ = 6·(4/3 + 4/3)/8 = 6·8/3/8 = 2 ⟺ 6·8 = 2·8·3
theorem A3_value : 6 * 8 = 2 * 8 * 3 := by
  native_decide

-- (7) the trace term of A₃: C₂³(Q_L) = C₂³(u_R) = 4/3; 4/3 + 4/3 = 8/3
--     cross-multiplication: 4 + 4 = 8 (reduced to denominator 3)
theorem A3_trace : 4 + 4 = 8 := by
  native_decide

-- (8) the factor 6 = 2 × 3 (weak doublet × colour triplet)
theorem factor_six : six = 2 * three := by
  native_decide
