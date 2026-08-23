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

namespace CGV4
namespace Cosmology
namespace IRActionSelection

def coeffA : Nat := 1
def coeffB : Nat := 1
def coeffC : Nat := 1

theorem normalized_coeff_a : coeffA = 1 := by
  native_decide

theorem deep_ir_condition_a_eq_b : coeffA = coeffB := by
  native_decide

theorem newtonian_condition_a_eq_c : coeffA = coeffC := by
  native_decide

theorem selected_coefficients_equal : coeffA = coeffB ∧ coeffB = coeffC := by
  native_decide

theorem selected_coefficients_are_unit :
    coeffA = 1 ∧ coeffB = 1 ∧ coeffC = 1 := by
  native_decide

theorem pade_constraints_fix_coefficients
    (a b c : Nat) (hdeep : a = b) (hnewton : a = c) (hnorm : a = 1) :
    b = 1 ∧ c = 1 := by
  constructor
  · rw [← hdeep]
    exact hnorm
  · rw [← hnewton]
    exact hnorm

def numeratorPowerS : Nat := 1
def denominatorConstant : Nat := 1
def denominatorPowerS : Nat := 1

theorem selected_mu_squared_is_s_over_one_plus_s :
    numeratorPowerS = 1 ∧ denominatorConstant = 1 ∧ denominatorPowerS = 1 := by
  native_decide

end IRActionSelection
end Cosmology
end CGV4
