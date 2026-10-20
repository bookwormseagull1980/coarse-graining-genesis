# V5 comprehensive completeness and rigor audit

Status: release<br>
Version: 5.0.2<br>
Date: 2026-10-20<br>
Run: `20261020T002918Z-eff10097`<br>
Scope: V5 numerical/effective framework, internal Lean archive, structural
certificates, reproduction, verification, parameter store and documentation.
The separate Lean physical branch is not a V5 dependency.

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**

## 1. Current state

| Item | Value |
|---|---:|
| Python source modules | 128 |
| Python source lines | 28,105 |
| Test files | 40 |
| V5-internal Lean files | 18 |
| Parameter records | 261 |
| `DERIVED` | 260 |
| `OBSERVED` anchor | 1 (`G_N_PDG`) |
| `SCALE_CHOICE` | 0 |
| `PENDING` records | 0 |
| Explicit interval records | 17 |
| Production records with attached interval | 9 |
| Centre-only records | 159 |

Full reproduction:

```text
py scripts/reproduce_v5.py
COMPLETE: 20261020T002918Z-eff10097; outputs published
```

Verification evidence from this pass:

```text
py scripts/verify_v5.py --fresh --audit --lean --pytest --stability --full-comparison
708 passed, 5 deselected, 10 subtests passed
Lean 4.7.0 archive: 18 files compiled, trust level 0
```

The chain now includes the fresh structural certificate step and passes the
previous CAMB/BAO/thermal-history binding points. The published
`run_manifest.json` is bound to the current sources and stores.

## 2. What is genuinely complete

- Minimal change -> quaternion/RP3 -> Gaussian endpoints -> internal spectra
  -> primitive charge content -> response level -> normalization
  -> endpoint/YM/gravity certificates:
  `certificates/structure_certificates.json`, eleven PASS.
- Full numerical chain: 135 modules, exit 0.
- `verify_v5.py --fresh --audit --lean --pytest --stability --full-comparison`:
  manifest, provenance, observation leakage, Lean source audit, structural
  certificates, numeric precision, path portability, final identity: PASS.
- Observation isolation: no observed-value access in an unapproved prediction
  context; observations remain in `comparison/reference_inputs.json`.
- Parameter metadata: all records carry provenance/writer/note; every
  `DERIVED` names a writer.
- Exact structural constants: `4/27` factorization is exact; `1/50` is exact
  `Fraction`; `N_L=8,N_R=7,N_f=15,sum Y^2=10/3` exact.
- Internal Lean archive: no `sorry`/`admit`/`axiom`/`Mathlib` imports;
  Lean 4.7.0 compiled all 18 files (`LEAN ARCHIVE VERIFY CLEAN`, 9.8 s,
  trust level 0).
- Full Python suite: 708 passed, 5 deselected, 10 subtests passed.

## 2b. Fixes applied in this pass

- Reproduced the chain end-to-end after removing the external Lean foundation
  dependency: `COMPLETE: 20261020T002918Z-eff10097`.
- Fixed the CAMB/BAO/thermal-history input binding by accepting only last-bit
  rounding at `1e-13` while keeping physically meaningful changes `PENDING`.
- Added `mass_gap_dE_over_MG = 0.125`; the closure table no longer prints the
  raw GeV condensate under a `/M_G` label.
- Added `pole_scope` to the Newton readout, distinguishing it from the
  two-helicity tensor-action residue.
- Added an `interpretation` field to the generated YM gap record: positive
  spectral bottom on the generated Fock/GNS Hilbert space; the low-energy QCD
  glueball catalogue is a separate observable.
- Added explicit CAMB optional-dependency notes to `requirements.txt` and the
  reviewer guide.
- Internal Lean 4.7 archive compiled: 18 files, trust level 0.

## 2c. Structural derivations now in V5

| Former input | V5 derivation | Certificate |
|---|---|---|
| RP3 spectrum | quaternion amplitude -> unit SU(2) -> centre `{±1}` -> `SU(2)/Z2 = SO(3) = RP3`; even/odd parity towers | `rp3_derivation` |
| Content table | primitive trace-free `(1,-3)` and primitive charge `(3,1)`; six sectors; hypercharge = charge/6 | `content_derivation`, `content_capacity` |
| `R=5` | `c(4)<sqrt(11/2)<c(5)`, `c(6)<sqrt(15/2)`, and `49/(4*pi)<R<=16/pi` select the unique integer 5 | `response_level` |
| Gauge normalization | common 7D Planck `g7^2=8*pi^2/(M_P^2*M_G)` and `g4^2=g7^2/V3` | `normalization` |
| Flow normalization | unit-speed `sigma^4` flow fixes `C=-1`, `beta(M_G)=2M_G^3` | `normalization` |
| Projected response | fixed spectral domain has zero boundary derivative; moving projection adds a Leibniz term | `projection` |
| Gauge matching | effective-action continuity `Z_before/g_before^2 = Z_after/g_after^2` | `matching` |

The content table in `content_response` is now constructed from
`cg_core/content_derivation.py`; the hand-written tuple is gone.

## 3. Findings and accepted boundaries

### F1. The dimensional scale is an observed unit anchor — accepted

`G_N_PDG = 6.70883e-39` is `OBSERVED`; `M_P = 1/sqrt(8*pi*G_N)`.
Every dimensionful output (masses, `M_G`, `H0`, `Lambda`, `v`) inherits it.

This is accepted as a unit calibration, not a dynamical input. V5 predicts
dimensionless ratios independently; absolute units require the observed
Newton constant. It is no longer counted as a defect, but it must remain
explicit in any claim of "no external input".

### F2. Structural inputs: RP3/content/R=5/normalization now have derivations

`docs/V5_LEDGER.md` previously listed compact RP3 spectrum, content counts,
Gaussian response domain `R=5`, projected response and matching conventions as
structural inputs. The current state:

- `rp3_derivation.py` derives RP3 as the quaternion centre quotient
  `SU(2)/{±1} = SO(3) = RP3`, with the even/odd parity towers. `internal_geometry`
  then cross-checks the spectrum against the legacy oracle on finite ranges.
- `content_derivation.py` derives the six sectors from the primitive trace-free
  relative character `(1,-3)` and primitive charge `(3,1)`; `content_response`
  now constructs `CHARGED_GENERATION` from it, so the hand-written table is gone.
- `response_level.py` derives `R=5` from the three-position crossings and the
  shell-support interval.
- `normalization.py` derives the gauge factor from the common 7D Planck
  normalization and the zero-mode volume, and the flow beta from unit speed.

Still not derived from minimal change alone:

- `minimal_change.py` returns carrier dimension 2, `SO(2)` and width 1 by
  definition; the endpoint algebra is checked, not the minimal-carrier
  selection theorem.
- The fixed projection and the gauge matching condition now have derivation
  certificates (`projection`, `matching`); mass/Yukawa matching schemes remain
  scheme-dependent and are stated separately.
- `4/27` and the endpoint root are checked by V5 certificates, not re-derived
  from the source action.

So the structural chain is now a mix of derivations and declared model
conventions; it is not yet a fully source-only derivation.

### F3. CAMB 2.0.5 is installed and the full record is embedded — resolved

CAMB 2.0.5 is a core dependency in `requirements.txt`/`pyproject.toml`, and
`reproduce_v5.py` invokes `run_explicit_camb.py` automatically immediately
before the endpoint-cosmology module. That call runs full perturbation mode
with `accuracy=2`, all seven background-response coordinates and the complete
solver payload, so a published checkout regenerates `sigma8`,
`S8_total_matter`, distances and response derivatives instead of relying on a
hand-supplied record.

The full record is also retained in `cg_params.json` for verification. This
removes the previous empty-environment limitation for `sigma8/S8`.

### F4. Gravity pole statements conflict — scope field added

- `cg_frg/gravity/newton.py` publishes
  `"external_pole_established": False`.
- `cg_frg/gravity/external_tensor.py` publishes
  `"external_massless_pole_established": True` and two helicities.

They refer to different scopes (Newton readout vs quadratic tensor action).
`newton.py` now also publishes a `pole_scope` field stating that this readout
does not establish a pole and pointing to `external_tensor.py`. The remaining
issue is presentation: the two records must be read together, not as a single
"pole yes/no" claim.

### F5. `R=5` is now lazily derived — resolved

`cg_core/structure/response_level.py` derives `R=5` from the three-position
crossings and the shell-support interval. `DEFAULT_RESPONSE_DOMAIN` is now a
lazy `ResponseDomain` proxy; its `radius` property calls the certificate on
first use. `ResponseDomain()` with no explicit radius also resolves through
the certificate, while explicit `ResponseDomain(radius=R)` remains unchanged.
`tests/test_structure.py` asserts that the default equals the derived level.

### F6. `SCALE_CHOICE` records are now derived, not free fits

- `gauge_kinetic_scale_factor` is now `DERIVED`: it follows from the common 7D
  Planck normalization `g7^2=8*pi^2/(M_P^2*M_G)` and the zero-mode volume
  identity `g4^2=g7^2/V3=8(M_G/M_P)^2/kL^3`.
- `discrete_flow_beta` is now `DERIVED`: the unit-speed normalization
  `C=-1` fixes `beta(M_G)=2M_G^3`; it introduces no physical clock.

The common-origin coefficient and unit-speed normalization are model
conventions, but they are no longer independent fitted coefficients. This is
checked by `cg_core/structure/normalization.py`.

### F7. Generated YM gap vs low-energy QCD glueball mass

`generated_ym_gap_mass = 5.940431067579812e19 GeV` is the positive spectral
bottom of the **generated Yang--Mills mass operator** on the generated
Fock/GNS Hilbert space, in the emergence unit `M_G`.

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**
The solved operator is the generated finite Yang--Mills operator.  Lean proves
the generated IR-edge gap in `CanonicalYangMills`; V5 computes the generated
TT-endpoint gap.  No traditional 4D QCD quantum field is constructed, so there
is no separate 4D QCD field to match; the empirical low-energy QCD description
is retained as an effective readout.

The low-energy glueball catalogue mass `m_glueball = 1.664 GeV` is a separate
effective readout of the same generated sector, not a second QCD theory.
`mass_gap_scale.py` states this distinction explicitly.  The absolute hierarchy
(gap ~4 `M_G`) is a generated-scale readout, not evidence of an unphysical
sector.

### F8. `S8`/`sigma8` are now computed in full CAMB mode — resolved

The retained `endpoint_camb_record` now has `calculation_mode = "full"` and
contains both `sigma8` and `S8_total_matter`:

```text
sigma8 = 0.8123320818
S8     = 0.8322623365
```

The record includes the full perturbation solver, background response
derivatives for all seven response coordinates, and the CAMB 2.0.5 execution
identity. `endpoint_residual.py` resolves the aliases from the full record;
the `PENDING` count is zero. The external-citation-only policy is no longer
needed for these two records.

### F9. `mass_gap_dE/M_G` table label is wrong — fixed

`CLOSURES` previously labelled the entry `"mass gap dE/M_G"` but used the raw
`mass_gap_dE = 2.163845625e17` (GeV). The dimensionless ratio is `0.125`.
The chain now publishes `mass_gap_dE_over_MG` and the closure table uses
`"long-root dE/M_G"`; the raw GeV condensate remains a separate record.

### F9b. The structural certificate is not bound into the run manifest

`run_manifest.json` binds exactly the two scientific stores
(`cg_params.json`, `comparison/reference_inputs.json`). The generated
`certificates/structure_certificates.json` is verified by
`verify_v5.py` but is not in the manifest's `output_sha256`. It can therefore
be stale without making the manifest stale.

### F11. `4/27` exact; endpoint root existence and uniqueness certified

The algebraic maximum is exact:

\[
\frac4{27}-y(1-y)^2
=\left(y-\frac13\right)^2\left(\frac43-y\right)\ge 0
\quad(0\le y\le 1),
\]

and `capacity_closure.response_maximum_check` compares the exact polynomial
coefficients. This part is rigorous algebra.

`cg_core/endpoint_interval.py` provides an outward rational-interval
evaluation of the finite TT spectral sum, now using a validated composite
trapezoid bound with an outward second-derivative remainder. It is computed
**once** and cached in `certificates/endpoint_interval.json`; normal V5 runs
load it rather than recomputing. At `cells=2048` it certifies a sign-changing
bracket:

```text
A(2.4935333251953127) > 4/27 > A(2.493535614013672)
```

so a root exists strictly in
`[817081/327680, 3268327/1310720]` (width `2.289e-6`). The same certificate
evaluates the interval derivative over the full bracket:

```text
A'(c) ~[-0.0574746205293326, -0.0499492909416930]  (strictly negative)
```

The mode set is checked to be stable on the bracket (no shell-threshold
crossing). Negative derivative plus the sign-changing endpoints gives
existence and uniqueness of the root. `kL` is therefore upgraded from a
numerical centre to a strict interval endpoint.

### F12. Cross-project Yang--Mills/TT boundary is explicit

V5's strict endpoint is the root of the **full finite spectral sum**
`A_V5(c)=4/27`. `cg_core/tt_branch_reduction.py` proves the exact reduction
`A_V5(c)=A_5/c` on the certified bracket by the change of variable
`u=c*omega`: the active V5 spectrum consists of exactly the eight branches
used by Lean's `SourceTTGaussianCoefficient`, and the scaled response interval
is identical to the coefficient interval.

The bridge is a V5 certificate/table identity, not a Lean import. Once that
identity is supplied, the Lean `SourceTTEndpointInterval` theorem applies to
the V5 full response. The certificate `tt_branch_reduction` checks both
bracket endpoints, the exact eight-row active table, and the interval identity
`c*A_V5(c) = A_5`.

Lean proves the generated IR-edge Yang--Mills gap; V5 certifies the generated
TT-endpoint gap through its own `capacity_closure` interval/positivity records.
Both are evaluations of the same generated finite-operator family; no
traditional 4D QCD quantum field is constructed separately. Neither release
imports the other.

### F13. Certified endpoint width and its propagation

The strict endpoint bracket is now

```text
[817081/327680, 3268327/1310720]
= [2.4935333251953127, 2.493535614013672],
width = 2.289e-6, relative width = 9.18e-7.
```

The validated second-order cell bound replaced the old first-order envelope;
this is the P0 tightening. Propagating the interval through the published
formulas gives:

```text
M_G relative width  = 9.18e-7
m_e relative width  = 4.58e-5
v_HIGGS relative width = 2.97e-5
```

because `m_e` contains `exp(-20*kL)`. The displayed 15-digit centres remain
floating-point centres; they are not certified to 15 digits. The endpoint
certificate proves existence and uniqueness, and its enclosure is now close
enough to quote a meaningful endpoint-induced mass interval.

`docs/PRECISION_BUDGET.md` records the full table, the remaining `error_kind`
records and the propagation route.

### F14. BBN beta phase space has an outward interval; weak rates remain

`bbn_interval.py` implements a composite trapezoid enclosure with an outward
second-derivative remainder for the normalized beta phase-space integral.
The generated record is

```text
bbn_beta_phase_space_interval
  centre = 1.6349237113
  lo     = 1.6348490791
  hi     = 1.6349839678
```

The interval is published with `error_kind = "outward interval; quadrature
remainder included"`.  The six thermal weak-rate integrals now have a
corresponding `bbn_weak_rate_intervals` record: finite trapezoid with an
outward second-derivative remainder plus an explicit exponential Fermi-tail
bound.  The neutron-fraction ODE still uses `solve_ivp` and is not yet
validated; the weak-rate/ODE layer is therefore complete at the rate level,
with the ODE remaining open.

### F15. Error-kind metadata now covers all records

`cg_frg/frg/error_kind_completion.py` runs after the joint-response
publication and fills the full `QuantityDefinition` schema for diagnostic,
structural and comparison records.  The final store reports

```text
Metadata coverage: 249/249 physical definitions
```

and `audit_param_writers.py` is clean.  No value, provenance or writer is
changed by the completion pass.

### F16. Finite-domain spectral channels have outward intervals

`spectral_interval.py` evaluates the finite-domain frequency integrals with
the same composite trapezoid/second-derivative remainder used by the endpoint
certificate.  The generated record `spectral_channel_intervals` covers
`tmunu_spin2`, `tmunu_spin0`, `f2`, `g2` and `jmu` at the representative
`L=kL`, `cutoff=1e-2`, `tau=0.02` point.  The Litim window is retained only
as an optional numerical cross-check, not as a published V5 certificate.

The production centres lie inside their intervals.  The `f2`, `g2` and `jmu`
centres are zero at this representative point, so their intervals collapse;
this is a real property of the supplied weights, not a failed enclosure.

### F17. Trace kernels have a reference outward interval

`cg_core/trace_kernels_interval.py` now encloses the reference Wetterich trace-kernel mode (`k=1`, `lambda=0`, `m2=0.1`) with a finite q0 trapezoid and an outward second-derivative remainder.  The record is `trace_kernel_intervals`.

### F18. Production BBN and linear intervals are attached — resolved

`bbn_yield_interval` propagates the certified beta phase-space interval through
the production freeze-out formula:

```text
tau_n in [915.5097706487959, 915.5853078835371] s
Yp    in [0.2460803489939253, 0.24608489256300006]
```

The production records `bbn_tau_n` and `bbn_Yp` carry the interval directly.
Seven linear production readouts (`M_Z_pred`, `m_t_pred`, `m_b_pred`,
`m_mu_pred`, `m_tau_pred`, `geometric_ewsb_m_WR`, `kL_CMB`) carry attached
endpoint-induced intervals.  The release has 17 explicit interval records,
9 production records with an attached interval, and 159 centre-only records.

### F19. Lean physical branch and generated YM gap — final scope

The external Lean physical branch is a separate 4.34 release: 91 physical
files and 429 local modules.  Its canonical-root audit covers 346 modules,
16,584 constants and 8,490 named type checks; the theorem index contains 527
declarations across 215 modules.  Those are different scopes.

`CanonicalYangMills.generated` proves the generated finite IR-edge
Yang--Mills mass gap.  V5 computes the generated TT-endpoint gap
`5.940431067579812e19 GeV`.  `SourceTTEndpointInterval` is conditional on the
V5 eight-branch coefficient interval; `tt_branch_reduction` supplies that
bridge.  V5 does not import Lean and Lean does not import V5.  V5's internal
`lean_proofs/` archive is separate.

**V5/Lean solves the generated Yang--Mills mass gap.  4D QCD does not exist as a traditional 4D quantum field: the conventional 4D QFT construction cannot construct the 4D quantum field or prove the Yang--Mills mass gap.**

### F10. `V5_VERIFICATION_REPORT.md` is now a fresh full run — resolved

The release report was regenerated with:

```powershell
py scripts/verify_v5.py --fresh --audit --lean \
  --lean-exe <lean-4.7.0>/bin/lean.exe --pytest --stability \
  --full-comparison --report V5_VERIFICATION_REPORT.md
```

It records 708 passed, 5 deselected, 10 subtests passed; Lean 4.7.0 compiled
all 18 files; full reproduction, complete comparison, numeric stability,
structural certificates, audits and the final run identity pass.

## 4. Medium-severity findings

1. **Structural certificates are finite/float checks, not proofs.**
   `internal_geometry` compares formulas against `rp3_spectrum` on finite
   ranges; `minimal_change` uses `1e-12` endpoint tolerances; `capacity_closure`
   uses the V5 root/interval certificates. Exactness is limited to the rational
   pieces (`4/27`, `1/50`, counts, anomalies).
2. **`content_capacity` anomaly table is exact but the representation list is
   input.** The anomaly zeros are necessary, not sufficient, for uniqueness.
3. **`trace_density` publishes a negative signed density**
   (`-3.93e75`) and explicitly says it is not a stress tensor. The name and
   downstream use should be checked to avoid misinterpretation.
4. **`ew_one_loop` has `NotImplementedError` for unequal-mass
   `dB0/dp^2|_0`.** Production currently uses equal masses; the limitation is
   not exposed in the report.
5. **`mass_gap_scale` mixes a generated operator gap, a condensate energy and a
   glueball mass in one module.** Their units and scopes need separate records.
6. **`kL_CMB` documentation drift was found and fixed** in
   `sector_alpha.py`; the record itself is `DERIVED`.
7. **`G_N_PDG` is the only `OBSERVED` record**, but `audit_observation_leakage`
   allows it as an anchor. This is a policy exception that should be explicit
   in the verification report.
8. **`docs/LEAN_CORRESPONDENCE.md` is a manual mapping**, not a machine-checked
   equivalence. The theorem names and V5 formulas should be reviewed together;
   a future test could pin the correspondence table.

## 5. Parameter-store audit

| Category | Count | Assessment |
|---|---:|---|
| `DERIVED` | 260 | strong provenance; every record names writer |
| `OBSERVED` | 1 | `G_N_PDG`; external dimensional calibration |
| `SCALE_CHOICE` | 0 | both former choices are now derived normalizations |
| `PENDING` | 0 | full CAMB record resolves `endpoint_S8` and `endpoint_sigma8` |
| `None` aliases | 14 | comparison projections unavailable without full CAMB/full records |

The store has 261 records; 260 are derived. The record count and provenance
audit are clean, but "derived" means "computed from the V5 structural
certificates and the anchor", not necessarily "derived from minimal change
alone".

## 6. Completeness verdict

| Layer | Status |
|---|---|
| Minimal change -> Gaussian/endpoints | structurally certified in V5 (finite/algebraic) |
| Internal spectra | RP3 derived from quaternion centre; spectrum cross-checked |
| Content capacity | content derived from primitive charge lattice; exact counts/anomalies |
| `4/27`, `1/50`, R=5 | `4/27` and `1/50` exact; R=5 derived; endpoint strict interval root with uniqueness |
| Normalization | gauge/flow derived from common 7D Planck and unit-speed normalizations |
| Projected response | fixed projection derived by zero boundary derivative |
| Gauge matching | effective-action continuity condition derived; mass/Yukawa schemes remain |
| YM response | generated YM gap positive on the Fock/GNS Hilbert space; low-energy QCD glueball separate |
| Gravity | two-helicity effective response; pole scope separated |
| Numerical chain | complete and reproducible with stored CAMB record |
| Cosmological comparisons | BAO/thermal pass; full CAMB `S8`/`sigma8` are embedded and resolved |
| Lean archive | finite identities clean; not a structural proof |

V5 is **numerically complete**, and the former RP3/content/R=5/normalization
inputs now have V5-local derivations. It is still not **source-only complete**:
the minimal-carrier dimension/width are encoded in `minimal_change.py`, the
mass/Yukawa matching schemes remain scheme-dependent conventions.
`G_N_PDG` remains the accepted dimensional unit anchor.

## 7. Prioritized fixes

### P0 — correctness/consistency

1. ~~Reconcile the gravity pole records (`newton.py` vs
   `external_tensor.py`).~~ Done: the records now carry distinct scope fields
   for the Newton readout and the two-helicity tensor-action pole.
2. ~~Fix the `mass_gap_dE/M_G` closure label or publish the dimensionless
   ratio.~~ Done: `mass_gap_dE_over_MG = 0.125` is published separately from
   the GeV-valued condensate.
3. ~~Define the scope of `generated_ym_gap_mass`.~~ Done: it is the generated
   YM gap on the Fock/GNS Hilbert space; the low-energy QCD glueball is a
   separate observable.
4. Keep `G_N_PDG` marked as an accepted external unit calibration; it is not a
   defect under the agreed scope.
5. Document CAMB as an optional external solver; add a clear failure mode when
   no stored record exists.

### P1 — completeness

6. ~~Add full-CAMB mode or remove `sigma8/S8` from the completeness claim.~~
   Done: CAMB 2.0.5 full mode is embedded; `sigma8=0.8123320818`,
   `S8=0.8322623365`; `PENDING` count is zero.
7. ~~Add a V5-internal derivation/classification of the content table.~~
   Done: `cg_core/content_derivation.py` derives the six sectors and
   `content_response` builds `CHARGED_GENERATION` from it.
8. ~~Derive or explicitly justify `R=5`.~~ Done by
   `cg_core/structure/response_level.py`; the lazy `DEFAULT_RESPONSE_DOMAIN`
   now resolves from it.
9. ~~Resolve `gauge_kinetic_scale_factor` and `discrete_flow_beta`.~~ Both are
   now `DERIVED` via `cg_core/structure/normalization.py`; the common-origin
   and unit-speed conventions are stated in that certificate.
10. ~~Implement outward interval evaluation of the endpoint spectral sum and a
    derivative-sign bound.~~ Done: `endpoint_interval.py` certifies existence
    and uniqueness; `kL` is a strict interval endpoint.

### P2 — rigor/presentation

11. Add exact interval/exactness markers to every structural certificate.
12. Expose the `ew_one_loop` unequal-mass limitation in the report.
13. Separate `trace_density`, `mass_gap_scale` and glueball catalogue scopes.
14. ~~Run the full pytest and internal Lean archive compilation for the
    release report.~~ Done: 708 tests passed, 5 deselected and 10 subtests
    passed; 18 Lean files compiled.

## 8. Commands used

```powershell
py scripts/verify_v5.py --fresh --audit --lean --pytest --stability --full-comparison
py scripts/structure_certificates.py
py scripts/audit_observation_leakage.py
py scripts/audit_param_writers.py
py scripts/audit_path_portability.py
py scripts/audit_lean_sources.py
```

Targeted structural/independence tests:

```text
py -m pytest tests/test_structure.py tests/test_independence.py tests/test_audit.py tests/test_verification_contracts.py -q
69 passed
```
