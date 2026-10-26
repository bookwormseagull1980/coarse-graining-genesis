# V5 ↔ Lean physical branch correspondence

Status: release<br>
Version: 5.0.2<br>
V5 run: `20261024T084548Z-d52375b5`<br>
Lean snapshot: 4.34, 91 physical files, 429 local modules

V5 does not import the Lean physical branch.  The two projects are separate
releases.  This page records the theorem-level correspondence, the exact TT
bridge and the boundary between structural proof and numerical evaluation.

## Statement

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**

The solved operator is the generated finite Yang--Mills operator:

- Lean proves the generated **IR-edge** operator gap in
  `CanonicalYangMills.generated`;
- V5 computes the generated **TT-endpoint** gap
  (`generated_ym_gap_mass = 5.940431067579812e19 GeV`);
- the two ends are joined, where the TT coefficient is concerned, by the exact
  V5 `tt_branch_reduction` certificate.

No traditional 4D QCD quantum field is constructed in this framework: the
conventional 4D QFT route cannot construct the 4D quantum field or prove the
Yang--Mills mass gap.  The low-energy glueball catalogue is an effective
readout of the same generated finite operator, not a second QCD theory.

## Structural correspondence

| V5 certificate | V5 claim | Lean module/theorem | Status |
|---|---|---|---|
| `minimal_change.carrier_real_dimension` | minimal real carrier dimension 2, `SO(2)` | `Source.CanonicalRealization`; `width_eq_one` | structural |
| `rp3_derivation` | `SU(2)/{±1}=SO(3)=RP3` | `SourceProjectiveCovering`; `SourceProjectiveGeometry` | structural |
| `minimal_change.unit_covariance_width` | Gaussian width `b=1` | `CanonicalRealization.width_eq_one` | structural |
| `minimal_change.uv_endpoint` | `uv=sqrt(2)` | `Source.Endpoints`; `SourceEndpointCasimir.radius_eq` | structural |
| `minimal_change.ir_endpoint` | `ir=sqrt(2*pi)` | `Source.Endpoints.irEndpoint_eq_peakEquivalentWidth` | structural |
| `internal_geometry.scalar_eigenvalue` | `l(l+2)/L^2`, even `l`, multiplicity `(l+1)^2` | `SourceOneFormSystem` / internal-geometry modules | structural |
| `internal_geometry.vector_eigenvalue` | `(l+1)^2/L^2`, odd `l`, multiplicity `2l(l+2)` | `SourceOneFormSystem` | structural |
| `internal_geometry.spinor_eigenvalue` | `(n+3/2)^2/L^2`, even `n`, multiplicity `(n+1)(n+2)` | `SourceSpinorSystem` | structural |
| `internal_geometry.tt_rough_eigenvalue` | `(k(k+2)-2)/L^2`, even `k>=2` | `SourceTensorTTSystem`; `SourceTensorTTSpectrum` | structural |
| `content_derivation.relative_character` | primitive trace-free `(1,-3)` | `SourceChargeLattice.oriented_relative_unique` | structural |
| `content_derivation.primitive_charge` | neutral upper vacuum gives `(3,1)` | `SourceChargeLattice.oriented_fixedUpper_unique` | structural |
| `content_capacity.N_L/N_R/N_f` | `8, 7, 15` | `SourceTorsionContent.leftCount/rightChargedCount/nWeyl_eq` | structural |
| `content_capacity.sum_Y_squared` | `10/3` | `SourceTorsionContent.hyperchargeSqSum_eq` | structural |
| `content_capacity.tau` | `1/50` | `SourceTorsionContent.torsionTau_eq` | structural |
| `normalization.gauge_scale_factor` | `g4^2=g7^2/V3`, `g7^2=8*pi^2/(M_P^2*M_G)` | `SourceGaugeUnitary` / `SourceGeneratedGaugeGroup` | structural |
| `capacity_closure.critical_response` | `4/27` | `SourceTensorResponseEndpoint.unique_response_maximizer` | structural |
| `capacity_closure.tt_endpoint` | strict V5 endpoint `kL` | `SourceTTEndpointInterval` / `SourceTTResponse.endpointCertificateOfBounds` | certificate-conditional on V5 coefficient interval |
| `capacity_closure.R5` | unique integer `R=5` | `SourceResponseLevel.threePosition_eq_five` | structural |
| `capacity_closure.ym_gap` | generated YM positive spectral bottom | `SourceHaarYangMillsHessian.operator_selfAdjoint`, `complete_coercivity`, `gap_attained`; `CanonicalYangMills` | structural |
| `capacity_closure.gravity` | two physical helicities, zero mass term | `SourceCollectiveGravityClosure.tt_dimension`; `SourceLinearizedGravity` | structural |

## Physical mechanisms

The following names identify physical mechanisms across the manuscripts,
formal declarations and executable checks. They do not add parameters to
the generated stores or change the rank of a manuscript proposition.

| Mechanism | Formal statement | Executable counterpart |
|---|---|---|
| Vacuum stabilizer and primitive charge | `SourceChargeLattice.oriented_fixedUpper_unique`; `SourceGlobalGaugeGroup` | `cg_core/content_derivation.py` |
| Common frame covariance and response invariance | `SourceGeneratedYangMillsFrameResponse.commonFrameResponseAction_gauge_invariant` | `examples/check_common_frame_response.py`, including the inhomogeneous connection term and a transported finite source probe law |
| Generated Yang--Mills mass gap | `CanonicalYangMills`; `SourceHaarYangMillsHessian` | `cg_frg/qcd/generated_yang_mills.py`; `tests/test_generated_ym_gap.py` |
| Complete source exchange | `SourceClosedCenterResponse.exchange_capacity_conservation` | Complete carrier and source matrices in `cg_core/content_response.py` |
| Common response centre trace cancellation | `SourceClosedCenterResponse.common_response_centre_trace` | Full carrier centre response in `cg_core/content_response.py` |
| Neutral kernel and charged quotient | `SourceMatterCharge`; `SourceCompleteMatterExactSequence` | `cg_core/finite_connector.py`; `tests/test_native_operations.py` |
| Nonlinear response compensation under Gaussian resolution | `SourceResolutionCompensation.compensation_cocycle`, `resolution_add`, `complete_response_transport`, `residual_unique` | `cg_core/modal_algebra.py`; direct defect, Duhamel integral and composition checks in `tests/test_native_operations.py` |
| Source work and total stress balance | Common variation in the companion manuscript; equation residuals retained in the Ward identity | `cg_frg/gravity/matter_source_response.py`; `tests/test_matter_source_response.py` |
| Phase charge and a relational clock | `SourcePhaseCharge.phase_work_identity`, `phase_charge_conservation`, `phase_rate_pos` | Common source evolution and independent phase quadrature in `cg_frg/gravity/matter_source_response.py` |
| Collective tensor identities and coefficient uniqueness | `SourceLinearTensor.fpOperator_pureGauge`, `fpOperator_transverse`, `generalTensorOperator_coefficients_unique` | `cg_frg/gravity/external_tensor.py`; `tests/test_external_tensor.py` |

The complete carrier has decomposition `8_L+(7_R+1_neutral)`.
Exchange preserves its total capacity. Equal responses on the complete
left and right copies have zero graded trace. The charge kernel,
independently computed, gives the quotient `8_L+7_R`.

Common frame transport includes the probability law, observables and
allowed field domain as well as the connection and frame. The local
executable probe transports the same samples and weights; the manuscript
proves the source-state and form-domain transport.

Resolution carries `response + residual` by the same source heat map.
Its compensation law is not constancy of the response and is not a
physical time equation. The Lean instance uses the actual quotient Haar
heat map and continuous finite coefficient products, with colour acting
on all sixteen matter coordinates. Its algebraic statements correspond
to the composition and transport clauses of the manuscript proposition.

The matter stress identity retains the matter equation residual. On the
matter equation only source work remains; total stress conservation also
uses the common source equation. Phase conservation is proved for the
retained real pair with common kinetic and restoring coefficients. Its
positive-charge regular branch supplies the monotone phase clock.

The tensor coefficient comparison uses the displayed five-term local
second-order class and unit TT normalization. Euclidean momentum
contractions and the Lorentzian event carrier retain their respective
metric conventions.

## Complete matter connection and complement return

The development interface `SourceMatterCompression.generated` constructs
the complete lepton projector on the existing sixteen-dimensional matter
carrier, proves its compatibility with the scalar connector, and proves
that responses supported on the coloured summand annihilate it on both
sides. The neutral lepton direction remains in this projector.

The shared `Operations.CovariantCompression` module proves the unique
orthogonal decomposition of `dR+A R`, its complete Gram identity, both
interference terms and simultaneous passive frame transport. These
statements are included in `SourcePhysicalInterface.generatedCore.matter`.
Their numerical counterpart is `cg_core.matter_compression`.

`native_matter_matching.covariant_spinor_matrix` evaluates the spatial
Dirac connection on actual Haar spinors and the complete matter
representation. Mode multiplication precedes output projection; omitted
output rows and their Gram are returned explicitly. For a complete finite
Hermitian operator, `compressed_matter_response` calculates the full
resolvent, complement self-energy, ordinary force response and their
energy derivatives from the same operator. Tests compare the independent
full, Schur and force formulas and the existing full-pencil solver.

These additions are development checks. They do not replace the release
run identified above or supply an interacting source state or new lepton
pole conversion factors.

## Exact TT bridge

At the endpoint fixed point, `L=c`, `cutoff=pi/c^2`, `R=5`.  For each retained
mode, the change of variable `u=c*omega` gives

```text
A_V5(c) = A_5 / c
```

exactly.  On the certified bracket, the full active V5 spectrum is exactly the
eight branches of the Lean `SourceTTGaussianCoefficient` model.  V5's
`tt_branch_reduction.py` checks the branch table and the outward interval
identity `c*A_V5(c)=A_5`.

The Lean `SourceTTEndpointInterval` theorem then applies to the V5 full
response, conditional on that coefficient interval.  The bridge is a V5
certificate/table identity, not a Lean import.

## Lean counts

| Artifact | Count |
|---|---:|
| Physical branch files | `91` |
| Local Lean modules | `429` |
| Canonical-root audit | `346 modules`, `16,584 constants`, `8,490 named type checks` |
| Theorem index | `527 declarations`, `215 modules` |
| Root logical axioms | `propext`, `Classical.choice`, `Quot.sound` only |

The canonical-root audit covers the zero-argument root import closure.  The
theorem-index counts describe the whole indexed library.  They are different
scopes and must not be added or interchanged.

## Boundary

- Lean proves structural operator statements: self-adjointness, domains,
  coercivity, Fock gap, linearized gravity and the conditional TT endpoint.
- V5 proves finite/algebraic identities, numerical intervals and the generated
  gauge/YM readouts.
- Lean does not import V5; V5 does not import Lean.
- V5's internal `lean_proofs/` archive (18 files) is separate from the external
  Lean physical branch.
- `CanonicalYangMillsTT` is not a field of the zero-argument Lean root.
- The nonlinear tensor result in Lean covers affine dilation, not the full
  nonlinear metric variational system.

Neither side should claim the other's scope.
