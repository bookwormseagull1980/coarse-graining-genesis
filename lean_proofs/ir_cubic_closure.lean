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
namespace IRCubicClosure

def spatialDim : Nat := 3
def pScaleInvariant : Nat := spatialDim
def pFlatRotation : Nat := spatialDim
def pNewtonian : Nat := 2

theorem spatial_dimension_is_three : spatialDim = 3 := by
  native_decide

theorem scale_invariant_power_is_three : pScaleInvariant = 3 := by
  native_decide

theorem flat_rotation_power_is_three : pFlatRotation = 3 := by
  native_decide

theorem scale_and_flat_powers_coincide : pScaleInvariant = pFlatRotation := by
  native_decide

theorem cubic_action_scale_weight_zero : spatialDim - pScaleInvariant = 0 := by
  native_decide

theorem quadratic_action_scale_weight_nonzero : spatialDim - pNewtonian = 1 := by
  native_decide

theorem cubic_point_source_denominator : pFlatRotation - 1 = 2 := by
  native_decide

theorem cubic_acceleration_power_is_inverse_radius : spatialDim - 1 = pFlatRotation - 1 := by
  native_decide

theorem cubic_btfr_quarter_denominator : 2 * (pFlatRotation - 1) = 4 := by
  native_decide

theorem quadratic_newtonian_denominator : pNewtonian - 1 = 1 := by
  native_decide

theorem quadratic_acceleration_power_inverse_square : spatialDim - 1 = 2 * (pNewtonian - 1) := by
  native_decide

end IRCubicClosure
end Cosmology
end CGV4
