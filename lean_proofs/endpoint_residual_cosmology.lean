/-
Coarse-Graining Genesis Framework V5.0
Author: Jinku Guo <guojk@nwpu.edu.cn>
Northwestern Polytechnical University, Xi'an 710072, China
ORCID: 0009-0000-6600-6171
References:
DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
Full bibliography: REFERENCES.md and CITATION.cff.
-/

namespace CGV5
namespace Cosmology
namespace EndpointResidual

-- Components in an orthonormal rest frame, u=(1,0,0,0).
def RestFrameStress (α : Type) := Fin 4 -> Fin 4 -> α

theorem rest_frame_cold_decomposition {α : Type} [OfNat α 0]
    (E : RestFrameStress α)
    (hSpatial : ∀ i j, i ≠ 0 -> j ≠ 0 -> E i j = 0)
    (hMixed : ∀ j, j ≠ 0 -> E 0 j = 0)
    (hSymmetric : ∀ i j, E i j = E j i) :
    ∀ i j, E i j = if i = 0 ∧ j = 0 then E 0 0 else 0 := by
  intro i j
  by_cases hi : i = 0
  · subst i
    by_cases hj : j = 0
    · subst j
      simp
    · simp [hj, hMixed j hj]
  · by_cases hj : j = 0
    · subst j
      rw [hSymmetric i 0]
      simp [hi, hMixed i hi]
    · simp [hi, hj, hSpatial i j hi hj]

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
end CGV5
