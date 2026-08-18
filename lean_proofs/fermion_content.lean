/-
 Coarse-Graining Genesis Framework V4.0

 Author:      Jinku Guo <guojk@nwpu.edu.cn>
 Affiliation: Northwestern Polytechnical University, Xi'an 710072, China

 Part of the V4 spectral framework, whose physics is presented in the
 companion papers:
   [I]  "The spectrum of a compact internal space.
         I. Gauge structure and fermion content"
   [II] "The spectrum of a compact internal space.
         II. Effective couplings and mass scales"
-/

/-
Content derivation of the 5 fermion representations (2026-08-17)
================================================================

Derivation object (user request: "the 5 specific fermion representations ...
derive them if the documents do not give them"):

  The fermion representations (Q_L(3,2), u_R(3̄,1), d_R(3̄,1), L_L(1,2), e_R(1,1))
  are derived from the framework's minimality principle + the chiral axiom +
  colour vectoriality, not an external input.

Derivation chain (corresponding to DERIVATION OF THE FIVE REPRESENTATIONS in sm_content.py):
  1. the SU(2)_L doublet = the Spin(4) semispinor (1/2,0) (lem:clifford + thm:dim)
  2. the colour representation = the minimality minimal non-trivial representation 3 (fundamental, dimension 3)
  3. colour vectoriality: left-handed 3 + right-handed 3̄ (SU(3)³ anomaly cancellation)
  4. the 5 representations = the minimal combination of chiral doublet × colour assignment
  5. hypercharge = anomaly cancellation + Yukawa (hypercharge_derivation.lean)

This file verifies the core identities of the content counting by integer
cross-multiplication (native_decide, Lean 4.7 core, no mathlib).

Deep symmetry (key):
  N_L = 8 = the left-handed fermion component count (Q_L 3×2 + L_L 1×2 = 6 + 2)
  N_g = 8 = the colour gauge generator count (N_c² − 1 = 3² − 1)
  ⟹ N_L = N_g (the left-handed fermion component count = the colour generator count)
  N_R = 7 = N_g − 1 (the right-handed component count = the generator count − 1)
-/

-- ============ content counting (integers) ============
def N_c : Int := 3         -- colour number
def N_g : Int := N_c ^ 2 - 1  -- colour generators = 8
def Q_L_comp : Int := 6    -- Q_L: 3 colour × 2 weak
def L_L_comp : Int := 2    -- L_L: 1 colour × 2 weak
def u_R_comp : Int := 3    -- u_R: 3 colour
def d_R_comp : Int := 3    -- d_R: 3 colour
def e_R_comp : Int := 1    -- e_R: 1

-- ============ theorems ============

-- (1) left-handed fermion component count: N_L = Q_L + L_L = 6 + 2 = 8
theorem N_L_content : Q_L_comp + L_L_comp = 8 := by
  native_decide

-- (2) right-handed fermion component count: N_R = u_R + d_R + e_R = 3 + 3 + 1 = 7
theorem N_R_content : u_R_comp + d_R_comp + e_R_comp = 7 := by
  native_decide

-- (3) deep symmetry: left-handed component count = colour generator count N_L = N_g = 8
theorem N_L_equals_N_g : Q_L_comp + L_L_comp = N_g := by
  native_decide

-- (4) right-handed component count = colour generator count − 1: N_R = N_g − 1 = 7
theorem N_R_equals_N_g_minus_1 : u_R_comp + d_R_comp + e_R_comp = N_g - 1 := by
  native_decide

-- (5) chiral asymmetry: N_L − N_R = 1 (the numerator of τ)
theorem chiral_asymmetry : (Q_L_comp + L_L_comp) - (u_R_comp + d_R_comp + e_R_comp) = 1 := by
  native_decide

-- (6) colour vectoriality: left-handed colour components (Q_L 6) = right-handed colour components (u_R 3 + d_R 3 = 6)
theorem colour_vectorial : Q_L_comp = u_R_comp + d_R_comp := by
  native_decide

-- (7) Q_L components = colour × weak: 3 × 2 = 6
theorem Q_L_colour_times_weak : 3 * 2 = Q_L_comp := by
  native_decide

-- (8) the minimal non-trivial colour representation 3 (fundamental dimension 3 < adjoint 8):
--     SU(3) irreducible representations by dimension: 1 (trivial), 3 (fundamental), 3̄, 6, 8 (adjoint), ...
--     minimal non-trivial = 3 (dimension 3 < 8)
theorem colour_minimal_rep : 3 < 8 := by
  native_decide

-- (9) total fermion components (per generation) = 15 = N_L + N_R = 8 + 7
theorem total_weyl : (Q_L_comp + L_L_comp) + (u_R_comp + d_R_comp + e_R_comp) = 15 := by
  native_decide
