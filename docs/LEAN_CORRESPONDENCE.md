# V5 ↔ Lean physical branch correspondence

Status: release<br>
Version: 5.0.2<br>
V5 run: `20261020T002918Z-eff10097`<br>
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
