# Scope and limits

Status: release<br>
Version: 5.0.2<br>
Run: `20261024T084548Z-d52375b5`

V5 is the unique effective model under its root conditions and definitions.
It is not one option in a family of models, and conventional alternatives are
not competing V5 constructions.

## What is solved

- The generated source-to-spectrum chain is executable and certified.
- The TT endpoint is a strict outward interval root with uniqueness.
- CAMB 2.0.5 full mode is part of the release chain.
- BBN beta phase space and the production `tau_n`/`Yp` interval are certified.
- Gaussian spectral channels, trace kernels and the native potential have
  outward reference intervals.
- **V5/Lean solves the generated Yang--Mills mass gap.**
- **No traditional 4D QCD quantum field exists.**  The conventional 4D QFT
  construction cannot construct the 4D quantum field or prove the Yang--Mills
  mass gap.  The physical QCD-like sector is the generated finite
  Yang--Mills operator; the glueball catalogue is a separate effective
  readout.

“4D QCD does not exist” here means the traditional 4D continuum quantum-field
construction, not the empirical low-energy QCD phenomenology.  The latter is
retained as an effective readout of the generated finite operator.

## Precision

| Item | Value |
|---|---:|
| Parameter records | `262` |
| Explicit interval records | `16` |
| Production records with attached interval | `8` |
| Centre-only records | `160` |

The 160 centre-only records are multi-input nonlinear readouts, diagnostic
bundles, algebraic evaluations or model definitions without a single certified
input interval.  They are not missing production factors.

The Z endpoint diagnostic regenerates its gauge boundary, evolution and
fixed point at both endpoints and the centre. It is not counted as a
certified enclosure. The lepton and bottom mass enclosures retain their
full shared endpoint dependence; the right weak mass enclosure also
retains the generated weak-coupling boundary.

No full covariance is published: the certified inputs are intervals, not a
joint probability distribution.  No model-approximation envelope is fabricated:
there is no unique alternative-model error for the freeze-out BBN, glueball
catalogue or tree-level EW readout.

## Lean boundary

The external Lean branch proves structural operator statements.  Its
`CanonicalYangMills` theorem is the generated finite **IR-edge** Yang--Mills
operator.  V5 computes the generated finite **TT-endpoint** gap.  The two are
related by the V5 `tt_branch_reduction` certificate where the TT coefficient is
concerned; they are not a formal import either way.

`CanonicalYangMillsTT` is certificate-conditional on the V5 coefficient
interval.  V5's internal `lean_proofs/` archive is separate from the external
Lean physical branch.

The Lean root uses only `propext`, `Classical.choice` and `Quot.sound` in the
audited root closure.  There are no local axioms or proof placeholders in that
closure.  The external physical branch does not import V5 and V5 does not import
it.
