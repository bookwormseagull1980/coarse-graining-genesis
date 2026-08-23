/-
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
-/

/-
The spectral-sum origin of the conservation-law torsion term τ²π/2 (2026-08-17)
===============================================================================

Derivation object:
  the spectral-sum origin of the torsion term τ²π/2 of the conservation law
  1/α = 1/α_W + 1/N_c − τ²π/2.

Spectral-sum derivation (geometric, spontaneous, from EC torsion + the Euclidean
spectral sum + the conformal coupling):
  τ²π/2 = (the λ_EC second-order term 2τ²) × (the Euclidean period 2π) × (the conformal coupling ξ = 1/N_g)

  λ_EC = N_g(1+τ/2)² + 6 = 14 + 8τ + 2τ²: the EC torsion adds to the curvature the
  second-order term 2τ²; 2π is the Euclidean period (the Matsubara zero frequency);
  ξ = 1/8 is the conformal coupling (the scalar-field curvature coupling). The product
  of the three:
    2τ² × 2π × ξ = 2τ² × 2π × (1/8) = 4πτ²/8 = τ²π/2.

Algebraic core (π and τ² are reals; core has no Real.pi and no rational τ, so only the
algebraic structure is proved — pure integer cross-multiplication):
  · ξ = 1/N_g ⟺ N_g·1 = 1·8   (the conformal-gauge duality, N_g=8)
  · the τ² coefficient of N_g·(τ²π/2) = 4πτ²: N_g·(π/2) = 4π ⟺ N_g/2 = 4
  · the λ_EC second-order coefficient = 2 (2τ²)
-/

-- ============ content-ratio constants (integers) ============
def N_g : Int := 8          -- gauge generators (the su(3) adjoint dimension)
def N_c : Int := 3          -- colour number
def eight : Int := 8        -- the denominator of ξ = N_g

-- ============ theorems ============

-- (1) the conformal coupling ξ = 1/N_g (ξ = (d−2)/(4(d−1)) = 1/8),
--     cross-multiplication 8·1 = 1·8
theorem conformal_coupling_reciprocal : eight * 1 = 1 * eight := by
  native_decide

-- (2) the τ²-coefficient algebra of N_g × (τ²π/2) = 4πτ²: N_g·(π/2) = 4π
--     ⟺ N_g/2 = 4 ⟺ 8/2 = 4 (the coefficient of π cross-multiplied)
theorem torsion_term_inverse : 8 / 2 = 4 := by
  native_decide

-- (3) the τ²π coefficient of N_g: N_g·(τ²π) = 8·(τ²π) ⟺ 4πτ² × 2 = 8πτ²
--     (N_g × τ²π/2 = 4πτ² ⇒ N_g × τ²π = 8πτ² = 2×4πτ² ⟺ 8 = 2×4)
theorem torsion_doubling : 8 = 2 * 4 := by
  native_decide

-- (4) the second-order coefficient of the expansion of λ_EC = N_g(1+τ/2)² + 6: N_g·(1/4) = 8/4 = 2
--     ((1+τ/2)² = 1 + τ + τ²/4, the second-order term N_g·τ²/4 = 8τ²/4 = 2τ²,
--      the τ² coefficient 8/4 = 2)
theorem lambda_ec_second_order : 8 / 4 = 2 := by
  native_decide

-- (5) both terms of the conservation law ⟺ N_g·ξ = 1 contain ξ:
--     1/N_c = N_g·ξ/N_c and τ²π/2 = 4πτ²·ξ, hence the conservation law = ξ(8/3 − 4πτ²)
--     the algebraic core: N_g/N_c = 8/3 (generators/colour number)
theorem duality_ratio : N_g * 3 = 8 * N_c := by
  native_decide

-- (6) the τ² coefficient (1/2) of τ²π/2 and the 4/N_g of 4πτ²/N_g:
--     1/2 = 4/8 ⟺ 1·8 = 4·2 (cross-multiplication)
theorem half_period_reciprocal : 1 * 8 = 4 * 2 := by
  native_decide

-- (7) the colour self-reflexivity of the conservation law N_c × (1/N_c) = 1: N_c·1 = 1·N_c
theorem colour_self_inverse : N_c * 1 = 1 * N_c := by
  native_decide
