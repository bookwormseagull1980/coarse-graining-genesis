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

**A spectral framework in which the full Standard-Model phenomenology emerges from
the spectrum of a compact internal space (RP³), with a single observed dimensional
anchor (G_N) and all 146 remaining parameters derived internally.**

- **Author:** Jinku Guo `<guojk@nwpu.edu.cn>`
- **Affiliation:** Northwestern Polytechnical University, Xi'an 710072, China

## Companion papers

- **[I]** *The spectrum of a compact internal space. I. Gauge structure and fermion content*
- **[II]** *The spectrum of a compact internal space. II. Effective couplings and mass scales*

Paper I gives the **structure** (gauge algebra, fermion content, mass-gap form);
Paper II gives the **numbers** (window closure, 147 parameters, comparison with observation).

---

## Overview

V4 reconstructs the Standard Model from first principles as a *spectral* theory.
The single dimensional input is Newton's constant `G_N` (observed, used only for
comparison). Everything else — the gauge couplings, the Yukawa hierarchy, the
electroweak scale, the quark/lepton masses, the cosmological fractions, the QCD
scale — is **derived** from the spectrum of the round RP³ internal space and a
handful of structural integers, with zero hard-coded parameters.

The central symmetry identities are *content* identities (proved in Lean 4):

| Symmetry | Content | Meaning |
|---|---|---|
| chiral content | `N_L = N_g = 8`, `N_R = 7` | left-handed fermion components = colour generators |
| conformal–gauge duality | `N_g·ξ = 1`, `ξ = (d−2)/(4(d−1))` | fixes `d = N_c = 3` |
| hypercharge | `ΣY = 0`, `ΣY² = 10/3` | anomaly cancellation → `τ = (N_L−N_R)/(N_f·ΣY²) = 1/50` |
| cosmology | `Ω_b + Ω_DM + Ω_Λ = 1.00000` | exact flatness, no fit |
| gravity | TT spectral zero mode | "transparent gravity" — no dark matter, no curved spacetime |

The framework is **non-perturbative** ("non-perturbative = spectral-sum
representation"), closed by the *duality-emergence* principle (conformal↔gauge,
geometric↔gauge, UV↔IR, spectral↔physical).

## Quick start

```powershell
py scripts/reproduce_v4.py          # 40-chain-item verification — expect "ALL MODULES PASSED", exit 0
py scripts/audit_param_writers.py   # parameter-writer audit — expect "AUDIT CLEAN"
```

Both must pass before any change is considered complete. The chain reads
`cg_params.json` (147 parameters: 1 OBSERVED anchor + 146 DERIVED) and
`comparison/sm_inputs.json` (the SM comparison table).

## Directory map

| Directory | Contents |
|---|---|
| `cg_core/` | parameter store, RP³ spectrum (`rp3_spectrum.py`), SM content, β-functions, EC structure |
| `cg_frg/` | the physics sectors — `gauge/`, `generation/`, `ewsb/`, `cosmology/`, `gravity/`, `neutrino/`, `fermion/`, `framework/`, `qcd/`, `frg/` |
| `scripts/` | `reproduce_v4.py` (the master chain), `audit_param_writers.py`, `generate_framework_v4.py` |
| `lean_proofs/` | 17 Lean 4 proofs (`native_decide`, core only, no mathlib) |
| `docs/` | the two papers (PDF), `V4_LEDGER.md` (reference ledger), `V4_COMPLETE_GUIDE.docx` (complete guide), and the popular-science introductions (EN/ZH) |
| `_docs_build/` | documentation build toolchain (`build_docx.py`, `gen_ledger.py`, `figures.py`, source `.md`) |
| `comparison/` | SM comparison (`sm_rge/`, `param_audit_full.py`, `sm_inputs.json`) |

## Dependencies

- **Python 3.10+** (tested on 3.12 and 3.13), with `numpy` and `scipy`.
- `matplotlib` + `python-docx` — needed only to rebuild the figures and the `.docx`.
- **Lean 4.7.0** (core, no mathlib) — needed only for `lean_proofs/`.

## Formal proofs

All 17 files under `lean_proofs/` compile with `exit 0`:

```powershell
lean.exe lean_proofs/*.lean     # each file: exit 0 = all theorems pass
```

They machine-check the *content* identities (integer cross-multiplication via
`native_decide`) behind the closed parameters — e.g. the 21-theorem
`inverse_coupling_symmetry.lean`, the 62-theorem `twoloop_yukawa_quartic.lean`,
and the conformal–gauge duality.

## Documentation

Six documents accompany the code, ordered here from rigorous to accessible:

| Document | Format | Purpose | Best for |
|---|---|---|---|
| **Paper I** — *…I. Gauge structure and fermion content* | PDF | rigorous derivation of the **structure** (gauge algebra, fermion content, mass-gap form) | physicists / referees |
| **Paper II** — *…II. Effective couplings and mass scales* | PDF | rigorous derivation of the **numbers** (window closure, 147 parameters, observation comparison) | physicists / referees |
| `docs/V4_LEDGER.md` | Markdown | reference ledger — build instructions, the Paper-I axiomatic foundation, the full text of the source documents, the Paper-II content reference, the reproducibility record | auditors / anyone reproducing |
| `docs/V4_COMPLETE_GUIDE.docx` | Word | lecture-style complete guide, parameter by parameter | systematic study |
| `docs/From Change to Everything - A Popular Science Introduction.docx` | Word | popular-science introduction (English) — the central ideas | anyone new |
| `docs/从变化到万物_科普导读.docx` | Word | popular-science introduction (Chinese) — the central ideas | Chinese readers |

### Suggested reading order

- **Want the central idea, fast?** → read the popular-science introduction (`From Change to Everything`, or the Chinese `从变化到万物`).
- **Want the rigorous physics?** → read Paper I (structure), then Paper II (numbers).
- **Want to reproduce or audit?** → run `py scripts/reproduce_v4.py` and read `docs/V4_LEDGER.md`.
- **Want to study every parameter systematically?** → read `docs/V4_COMPLETE_GUIDE.docx`.

The four layers — papers (rigorous) → complete guide (comprehensive) → ledger
(reproducible) → popular-science introduction (accessible) — let a reader descend from
"what does it mean" to "how is it derived" at whatever depth they choose.

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
