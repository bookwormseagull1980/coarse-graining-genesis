<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China

Part of the V4 spectral framework, whose physics is presented in the
companion papers:
  [I]  "The spectrum of a compact internal space.
        I. Gauge structure and fermion content"
  [II] "The spectrum of a compact internal space.
        II. Effective couplings and mass scales"
-->

# Coarse-Graining Genesis Framework V4.0

**A spectral framework that records a fixed computation chain from the spectrum
of a compact internal space (RP³) to effective couplings, mass scales, and
comparison tables, with one observed dimensional anchor (G_N) and explicit
provenance for every stored record.**

- **Author:** Jinku Guo `<guojk@nwpu.edu.cn>`
- **Affiliation:** Northwestern Polytechnical University, Xi'an 710072, China

## Companion papers

- **[I]** *The spectrum of a compact internal space. I. Gauge structure and fermion content*
- **[II]** *The spectrum of a compact internal space. II. Effective couplings and mass scales*

Paper I gives the **structure** (gauge algebra, fermion content, mass-gap form);
Paper II gives the **numbers** (window closure, 171 stored records, comparison with observation).

---

## Overview

V4 records a spectral construction and its numerical consequences.  The single
observed dimensional anchor is Newton's constant `G_N`, used to set the Planck
scale. The generated store separates this anchor, derived framework records,
and the declared `SCALE_CHOICE` bookkeeping record.  Standard-Model and
cosmological central values live in the comparison store and are audited to
stay out of prediction modules.

The central symmetry identities are *content* identities (proved in Lean 4):

| Symmetry | Content | Meaning |
|---|---|---|
| chiral content | `N_L = N_g = 8`, `N_R = 7` | left-handed fermion components = colour generators |
| conformal–gauge duality | `N_g·ξ = 1`, `ξ = (d−2)/(4(d−1))` | fixes `d = N_c = 3` |
| hypercharge | `ΣY = 0`, `ΣY² = 10/3` | anomaly cancellation → `τ = (N_L−N_R)/(N_f·ΣY²) = 1/50` |
| cosmology | `Ω_b + Ω_DM + Ω_Λ = 1.00000` | exact flatness, no fit |
| gravity | TT spectral zero mode (Newtonian 1/r at all scales) | acceleration scale a0 (derived Milgrom coincidence) and the dark-matter closure remainder, marked where exploratory |

The framework is **non-perturbative** ("non-perturbative = spectral-sum
representation"), closed by the *duality-emergence* principle (conformal↔gauge,
geometric↔gauge, UV↔IR, spectral↔physical).

## Quick start

```powershell
py scripts/reproduce_v4.py          # official chain verification — expect "ALL MODULES PASSED", exit 0
py scripts/audit_param_writers.py   # parameter-writer audit — expect "AUDIT CLEAN"
py scripts/audit_observation_leakage.py  # observed-value isolation audit
py scripts/audit_lean_sources.py    # Lean proof-source hygiene audit
py scripts/audit_numeric_precision.py  # no rounded/formatted stored numerics
py scripts/audit_path_portability.py  # no machine-local paths in reviewer artifacts
py scripts/verify_lean_archive.py   # if Lean 4.7 is on PATH or LEAN_EXE is set
```

These checks must pass before any change is considered complete. The chain reads
`cg_params.json` (171 records: 1 OBSERVED anchor + 169 DERIVED + 1 SCALE_CHOICE) and
`comparison/sm_inputs.json` (the SM comparison table).

For a reviewer-grade fresh rebuild and report, start with
[`REVIEWER_START_HERE.md`](REVIEWER_START_HERE.md):

```powershell
py scripts/verify_v4.py --fresh --audit --pytest --stability --report V4_VERIFICATION_REPORT.md
py scripts/make_reviewer_dashboard.py  # writes docs/reviewer_dashboard.html
```

Add `--lean` for strict Lean compilation when Lean 4.7 is available.  Lean is
discovered from `PATH`, `LEAN_EXE`, or `--lean-exe` on
`scripts/verify_lean_archive.py`.

```powershell
py scripts/verify_v4.py --fresh --audit --lean --pytest --report V4_VERIFICATION_REPORT.md
```

Without Python or Lean, Git readers can still open the committed
`docs/reviewer_dashboard.html` and `V4_VERIFICATION_REPORT.md`.

The `--stability` step saves the current generated parameter stores, reruns the
official chain from empty stores, and checks that the regenerated parameter
records are identical.  It ignores `params_write_log.json` timestamps.

## Directory map

| Directory | Contents |
|---|---|
| `cg_core/` | parameter store, RP³ spectrum (`rp3_spectrum.py`), SM content, β-functions, EC structure |
| `cg_frg/` | the physics sectors — `gauge/`, `generation/`, `ewsb/`, `cosmology/`, `gravity/`, `neutrino/`, `fermion/`, `framework/`, `qcd/`, `frg/` |
| `scripts/` | `reproduce_v4.py` (the master chain), `verify_v4.py`, `verify_lean_archive.py`, `make_reviewer_dashboard.py`, `audit_param_writers.py`, `audit_observation_leakage.py`, `audit_lean_sources.py`, `generate_framework_v4.py` |
| `lean_proofs/` | 17 Lean 4 proofs (`native_decide`, core only, no mathlib) |
| `docs/` | the two papers (PDF), `V4_LEDGER.md` (reference ledger), `V4_COMPLETE_GUIDE.pdf` (complete guide), and the popular-science introductions (EN/ZH) |
| `_docs_build/` | documentation build toolchain (`build_docx.py`, `gen_ledger.py`, `figures.py`, source `.md`) |
| `comparison/` | SM comparison (`sm_rge/`, `param_audit_full.py`, `sm_inputs.json`) |

## Dependencies

- **Python 3.10+** (tested on 3.12 and 3.13), with `numpy` and `scipy`.
- `matplotlib` + `python-docx` — needed only to rebuild the figures and the `.docx`.
- **Lean 4.7.0** (core, no mathlib) — needed only for `lean_proofs/`.

## Formal proofs

All 17 files under `lean_proofs/` compile under the strict verifier:

```powershell
py scripts/verify_lean_archive.py
```

This uses Lean 4.7.0 core only, compiles each file with `--trust=0`, and fails
if any file emits warnings or interactive output.  If Lean is not on `PATH`,
set `LEAN_EXE` or pass `--lean-exe` with your local Lean executable.  The
companion source audit also rejects `sorry`, `admit`, explicit `axiom`,
`unsafe`, `opaque`, Mathlib imports, and interactive output commands such as
`#eval`.

## Numeric precision discipline

The parameter store writes Python numeric objects directly with JSON
round-trip float representations.  `scripts/audit_numeric_precision.py` scans
all Python sources for rounded or formatted values being written to
`pset()`, `compare_and_set()`, or `sm_set()`, checks that non-informational
numeric records are stored as JSON numbers rather than strings, and reports
the highest-fanout downstream parameters with their full stored `repr()`.

They machine-check the *content* identities (integer cross-multiplication via
`native_decide`) behind the closed parameters — e.g. the 21-theorem
`inverse_coupling_symmetry.lean`, the 62-theorem `twoloop_yukawa_quartic.lean`,
and the conformal–gauge duality.

## Documentation

Six documents accompany the code, ordered here from rigorous to accessible:

| Document | Format | Purpose | Best for |
|---|---|---|---|
| **Paper I** — *…I. Gauge structure and fermion content* | PDF | rigorous derivation of the **structure** (gauge algebra, fermion content, mass-gap form) | physicists / referees |
| **Paper II** — *…II. Effective couplings and mass scales* | PDF | rigorous derivation of the **numbers** (window closure, stored records, observation comparison) | physicists / referees |
| `docs/V4_LEDGER.md` | Markdown | reference ledger — build instructions, the Paper-I axiomatic foundation, the full text of the source documents, the Paper-II content reference, the reproducibility record | auditors / anyone reproducing |
| `docs/V4_COMPLETE_GUIDE.pdf` | PDF | lecture-style complete guide, parameter by parameter | systematic study |
| `docs/From Change to Everything - A Popular Science Introduction.docx` | Word | popular-science introduction (English) — the central ideas | anyone new |
| `docs/从变化到万物_科普导读.docx` | Word | popular-science introduction (Chinese) — the central ideas | Chinese readers |

### Suggested reading order

- **Want the central idea, fast?** → read the popular-science introduction (`From Change to Everything`, or the Chinese `从变化到万物`).
- **Want the rigorous physics?** → read Paper I (structure), then Paper II (numbers).
- **Want to reproduce or audit?** → run `py scripts/reproduce_v4.py` and read `docs/V4_LEDGER.md`.
- **Want to study every parameter systematically?** → read `docs/V4_COMPLETE_GUIDE.pdf`.

The four layers — papers (rigorous) → complete guide (comprehensive) → ledger
(reproducible) → popular-science introduction (accessible) — let a reader descend from
"what does it mean" to "how is it derived" at whatever depth they choose.

## Research roadmap (open items, not claims)

The framework makes claims only for quantities its code actually computes. The following directions are recorded as open research items, deliberately not asserted:

- **Rotation-curve shape `F(a/a0)`** — the framework fixes the acceleration scale `a0 = c H0/(2π)√(4/3)` (the spectral IR endpoint) and the closure remainder `Ω_DM`, but it does **not** yet derive the full rotation-curve shape function. That would require the acceleration response of the transverse-traceless zero mode to a baryonic mass distribution (a TT-tensor problem, currently only seeded in `cg_frg/gravity/tt_tensor.py` and `newton.py`), followed by a comparison with a resolved galaxy-rotation-curve sample (e.g. SPARC). This is a research project, not a completed prediction.
- The electroweak precision block (`cg_frg/ewsb/ew_precision.py`) is computed at the level stated in its docstring (tree-level on the two-loop running for `M_Z`; Born + one-loop ρ for `M_W`, with `Δr_rem` omitted; Born + QCD/QED radiators for `Γ_Z`; tree-level `m_H`). Promoting any of these to full one-loop EW standard is an open refinement.

## Citation (required)

Any use of this framework — in code, publications, or derivative work —
**must** cite all three of the following:

1. **Author** — Jinku Guo, Northwestern Polytechnical University, Xi'an, China;
2. **Companion papers** —
   - [I] *The spectrum of a compact internal space. I. Gauge structure and fermion content*
   - [II] *The spectrum of a compact internal space. II. Effective couplings and mass scales*
3. **Source** — this Git repository: https://github.com/bookwormseagull1980/coarse-graining-genesis

```bibtex
@misc{guo2026cg,
  author       = {Jinku Guo},
  title        = {Coarse-Graining Genesis Framework {V4.0}},
  year         = {2026},
  howpublished = {\url{https://github.com/bookwormseagull1980/coarse-graining-genesis}},
  note         = {Companion papers: ``The spectrum of a compact internal space.
                  I. Gauge structure and fermion content'' and
                  ``II. Effective couplings and mass scales''}
}
```

## License

MIT — see [`LICENSE`](LICENSE), which carries an **additional attribution
requirement** (cite author + papers + source).
