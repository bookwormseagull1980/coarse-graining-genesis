<!--
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================
-->

<!--
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================
-->

# Reviewer Start Here

This page is intentionally short. It tells a reviewer exactly what to
check before reading the papers.

## 1. Allowed External Input

The prediction store is allowed one observed dimensional anchor:

- `G_N_PDG`, used to set the Planck scale.

All Standard-Model masses, couplings, cosmological central values, and
precision observables live in the separate comparison store and must not
be used to back-calibrate the prediction chain.

The generated prediction store may also contain non-observational
bookkeeping records such as `SCALE_CHOICE`; these are audited separately
from observed inputs.

Cosmology comparison records follow the same rule. CAMB is used only as
a propagation tool for the fixed V4 output set, and DESI/SPARC data are
used only after the V4 parameters have been computed.

## 2. Prediction Chain vs Comparison Files

Prediction-generation files:

- `scripts/reproduce_v4.py`
- `cg_core/`
- `cg_frg/`
- generated output: `cg_params.json`

Comparison-only files:

- `comparison/`
- `comparison/sm_inputs.json`
- `comparison/param_audit_full.py`

The rule is simple: prediction modules write derived framework values;
comparison files may read observed values only after the prediction chain
has produced its outputs.

## 3. One-Command Reproduction

No local runtime is needed to inspect the committed reviewer artifacts:

- `docs/reviewer_dashboard.html`
- `V4_VERIFICATION_REPORT.md`

To reproduce on a machine with Python and the project dependencies, run from
the repository root:

```powershell
py scripts/verify_v4.py --fresh --audit --pytest --report V4_VERIFICATION_REPORT.md
```

Expected result: every required step prints `PASS`.

Optional visual dashboard:

```powershell
py scripts/make_reviewer_dashboard.py
```

Open `docs/reviewer_dashboard.html`.

If Lean 4.7 is available, add the strict proof-archive step:

```powershell
py scripts/verify_v4.py --fresh --audit --lean --pytest --report V4_VERIFICATION_REPORT.md
```

Lean can be discovered from `PATH`, from `LEAN_EXE`, or from
`--lean-exe` on the standalone verifier.  If Lean is not installed, omit
`--lean`; the source-hygiene audit still checks that the Lean archive has no
`sorry`, `admit`, explicit `axiom`, `unsafe`, `opaque`, Mathlib import, or
interactive output command.

For a release-level determinism check, add the fresh-rerun stability audit:

```powershell
py scripts/verify_v4.py --fresh --audit --pytest --stability --report V4_VERIFICATION_REPORT.md
```

This compares the current generated parameter stores to a fresh official
rerun.  The write log is excluded because its timestamps necessarily change.

## 4. No-Observation-Leakage Check

Run:

```powershell
py scripts/audit_observation_leakage.py
```

Expected result:

```text
OBSERVATION-LEAKAGE AUDIT CLEAN
```

This audit scans source code for explicit observed-value access
(`sm_value`, `get_observed`) and permits it only in documented
comparison-only contexts. The full verifier above runs this audit
automatically.
