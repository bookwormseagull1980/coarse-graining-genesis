/-
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

Lean 4.7 proof skeleton for the endpoint-residual cosmology closure.

This file formalizes the logical dependency of the V4 cosmology branch:

  MaxEnt endpoint
    -> global normal Hamiltonian endpoint balance
    -> local endpoint residual
    -> conserved cold source in linear cosmology
    -> no-double-counting split with the local acceleration projection.

It does not formalize tensor calculus, ADM geometry, or CAMB numerics.
Those analytic and numerical ingredients are represented here as named
hypotheses of the endpoint theorem.  The file checks that, once those
hypotheses are supplied, the final closure package has no additional
logical assumption.
-/

namespace CGV4
namespace Cosmology
namespace EndpointResidual

inductive Projection where
  | normalHamiltonian
  | localAcceleration
deriving DecidableEq, Repr

structure ColdDustStatus where
  conserved : Prop
  pressureless : Prop
  zeroSoundSpeed : Prop
  zeroAnisotropicStress : Prop

structure ColdDustProof (s : ColdDustStatus) : Prop where
  hConserved : s.conserved
  hPressureless : s.pressureless
  hZeroSoundSpeed : s.zeroSoundSpeed
  hZeroAnisotropicStress : s.zeroAnisotropicStress

structure EndpointResidualTheorem where
  maxEntEndpoint : Prop
  globalSigmaEndpoint : Prop
  spatialMetricEquations : Prop
  momentumConstraints : Prop
  visibleMatterConserved : Prop
  bianchiIdentity : Prop
  noExtraDarkStressTensor : Prop
  localNormalResidual : Prop
  residualStatus : ColdDustStatus

  hMaxEnt : maxEntEndpoint
  hGlobal : globalSigmaEndpoint
  hSpatial : spatialMetricEquations
  hMomentum : momentumConstraints
  hVisible : visibleMatterConserved
  hBianchi : bianchiIdentity
  hNoExtra : noExtraDarkStressTensor
  hResidual : localNormalResidual

  endpointResidualImpliesColdDust :
    maxEntEndpoint ->
    globalSigmaEndpoint ->
    spatialMetricEquations ->
    momentumConstraints ->
    visibleMatterConserved ->
    bianchiIdentity ->
    noExtraDarkStressTensor ->
    localNormalResidual ->
    ColdDustProof residualStatus

theorem endpoint_residual_is_cold_dust
    (T : EndpointResidualTheorem) :
    ColdDustProof T.residualStatus :=
  T.endpointResidualImpliesColdDust
    T.hMaxEnt
    T.hGlobal
    T.hSpatial
    T.hMomentum
    T.hVisible
    T.hBianchi
    T.hNoExtra
    T.hResidual

structure LinearCosmologyClosure where
  coldDust : ColdDustStatus
  omegaSigmaClosure : Prop
  adiabaticInitialCondition : Prop
  unitLinearMuEff : Prop
  cambSlotIdentification : Prop

  hColdDust : ColdDustProof coldDust
  hOmegaSigmaClosure : omegaSigmaClosure
  hAdiabatic : adiabaticInitialCondition
  hMuEff : unitLinearMuEff
  hCambSlot : cambSlotIdentification

theorem linear_cosmology_closed
    (L : LinearCosmologyClosure) :
    ColdDustProof L.coldDust ∧
    L.omegaSigmaClosure ∧
    L.adiabaticInitialCondition ∧
    L.unitLinearMuEff ∧
    L.cambSlotIdentification := by
  exact ⟨L.hColdDust, L.hOmegaSigmaClosure, L.hAdiabatic,
         L.hMuEff, L.hCambSlot⟩

structure AccelerationBranch where
  endpointScaleFixed : Prop
  muFixed : Prop
  deepIR_BTFR : Prop
  noRunningA0 : Prop

  hEndpointScaleFixed : endpointScaleFixed
  hMuFixed : muFixed
  hBTFR : deepIR_BTFR
  hNoRunningA0 : noRunningA0

theorem acceleration_branch_closed
    (A : AccelerationBranch) :
    A.endpointScaleFixed ∧ A.muFixed ∧ A.deepIR_BTFR ∧ A.noRunningA0 := by
  exact ⟨A.hEndpointScaleFixed, A.hMuFixed, A.hBTFR, A.hNoRunningA0⟩

structure DarkSourceDecomposition where
  Source : Type
  rhoDarkEff : Source
  rhoSigmaFree : Source
  rhoPolarization : Source
  addSource : Source -> Source -> Source
  noDoubleCounting :
    rhoDarkEff = addSource rhoSigmaFree rhoPolarization

theorem effective_dark_source_decomposes
    (D : DarkSourceDecomposition) :
    D.rhoDarkEff = D.addSource D.rhoSigmaFree D.rhoPolarization :=
  D.noDoubleCounting

structure FinalCosmologyClosure where
  endpointTheorem : EndpointResidualTheorem
  linearClosure : LinearCosmologyClosure
  accelerationClosure : AccelerationBranch
  darkDecomposition : DarkSourceDecomposition

  sameColdDustStatus :
    linearClosure.coldDust = endpointTheorem.residualStatus

theorem final_cosmology_closure
    (F : FinalCosmologyClosure) :
    ColdDustProof F.endpointTheorem.residualStatus ∧
    F.linearClosure.omegaSigmaClosure ∧
    F.linearClosure.adiabaticInitialCondition ∧
    F.linearClosure.unitLinearMuEff ∧
    F.linearClosure.cambSlotIdentification ∧
    F.accelerationClosure.endpointScaleFixed ∧
    F.accelerationClosure.muFixed ∧
    F.accelerationClosure.deepIR_BTFR ∧
    F.accelerationClosure.noRunningA0 ∧
    F.darkDecomposition.rhoDarkEff =
      F.darkDecomposition.addSource
        F.darkDecomposition.rhoSigmaFree
        F.darkDecomposition.rhoPolarization := by
  have hEndpoint : ColdDustProof F.endpointTheorem.residualStatus :=
    endpoint_residual_is_cold_dust F.endpointTheorem
  have hLinear := linear_cosmology_closed F.linearClosure
  have hAccel := acceleration_branch_closed F.accelerationClosure
  have hDark := effective_dark_source_decomposes F.darkDecomposition
  exact ⟨hEndpoint, hLinear.2.1, hLinear.2.2.1,
         hLinear.2.2.2.1, hLinear.2.2.2.2, hAccel.1,
         hAccel.2.1, hAccel.2.2.1, hAccel.2.2.2, hDark⟩

end EndpointResidual
end Cosmology
end CGV4
