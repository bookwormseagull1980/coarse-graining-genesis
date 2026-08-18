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

# V4 Framework — Open-Source Release Checklist

**Status as of 2026-08-18.** This checklist records what remains before the
Coarse-Graining Genesis Framework V4.0 can be made public on a Git host, and
what has already been done.

---

## A. Blocking (must be present before any public push)

| # | Item | Status | Notes |
|---|---|---|---|
| A1 | `LICENSE` | **DONE** | MIT (2026-08-18). |
| A2 | `README.md` (English) | **DONE** | Project summary, directory map, run instructions, dependencies, paper citations, license (2026-08-18). |
| A3 | `.gitignore` | **DONE** | Excludes `__pycache__/`, `*.pyc`, `*.bak_*`, LaTeX artefacts, `*.pdf`, `docs/V4_COMPLETE_GUIDE.docx`, OS/editor noise (2026-08-18). |
| A4 | `git init` + first commit | **DONE** | Initialised; first commit `740b5dd` (140 files, working tree clean) (2026-08-18). |

---

## B. Content hygiene (clean before public)

| # | Item | Status | Notes |
|---|---|---|---|
| B1 | Hard-coded absolute paths | **DONE** | The 5 hits in `cg_core/beta_functions.py` (4×) and `cg_core/sm_content.py` (1×) are now repo-relative `lean_proofs/...` paths (2026-08-18). |
| B2 | Backup files | **DONE** | `comparison/sm_inputs.json.bak_20260818` removed; `*.bak_*` also gitignored (2026-08-18). |
| B3 | Build artefacts | **DONE** | `*.pdf`, LaTeX artefacts, and `docs/V4_COMPLETE_GUIDE.docx` are gitignored (regenerable) (2026-08-18). |
| B4 | `__pycache__` | **DONE** | gitignored (`__pycache__/`, `*.pyc`) (2026-08-18). |
| B5 | Privacy scan | **passes** | `cg_params.json` and the ledger contain only physics parameters; no keys/tokens. Confirm before push. |

---

## C. Documentation (this task)

| # | Item | Status | Notes |
|---|---|---|---|
| C1 | `docs/` in English | **DONE** | `V4_LEDGER.md` (4433 lines) fully translated; `V4_COMPLETE_GUIDE.docx` regenerated from the translated `_docs_build/*.md` + `figures.py` + `build_docx.py` (0 CJK). `lean_proofs/README.md` translated. |
| C2 | Supplement `docs/` with Paper 5 | **DONE** | Added `§4. Paper 5 (Paper II) content reference` to `V4_LEDGER.md` (translated) + Part 4 chapters in the docx. |
| C3 | Build sources in English | **DONE** | The 10 `_docs_build/merged_sources/*.md` (ledger regeneration inputs) are fully English; `gen_ledger.py` reads them and emits an English ledger (2026-08-18 additions folded in source-driven). The V2/V3 `archive/` was moved out of the public tree, and the `_docs_archive/` directory was consolidated into `_docs_build/` (2026-08-18). |

---

## D. Source-code banners (task 3)

| # | Item | Status |
|---|---|---|
| D1 | `.py` author/affiliation/papers banner | **DONE** — 71/71 files stamped (idempotent `scripts/stamp_banner.py`; `generate_framework_v4.py` + `gen_ledger.py` stamped 2026-08-18). |
| D2 | `.lean` proof-file banner | **DONE** — 17/17 files stamped with the English `/- ... -/` block banner (2026-08-18). |
| D3 | `.md` document banner | **DONE** — 29/29 files stamped with the English `<!-- ... -->` banner; `build_docx.py` skips HTML comments so the banner does not leak into the generated docx (2026-08-18). |

---

## E. Quality gates (already passing)

| # | Gate | Command | Status |
|---|---|---|---|
| E1 | Reproduce the chain | `python scripts/reproduce_v4.py` | PASS (ALL MODULES PASSED) |
| E2 | Parameter-writer audit | `python scripts/audit_param_writers.py` | PASS (AUDIT CLEAN) |
| E3 | Lean formal proofs | `lean.exe *.lean` | PASS (exit 0) |
| E4 | Python syntax | `ast.parse` over all modules | PASS |

---

## F. Metadata and citation

| # | Item | Status |
|---|---|---|
| F1 | Author + affiliation | DONE — in every `.py` banner. |
| F2 | Supporting-paper titles | DONE — in every `.py` banner. |
| F3 | arXiv IDs / DOI | **after publication** — add once the two papers are posted. |
| F4 | CITATION.cff | optional — recommended for GitHub "Cite this repository". |

---

## Suggested execution order

1. A1–A4 + B1–B5 (license, README, gitignore, hygiene) — one session.
2. D1 (done) → D2 optional.
3. C1–C3 (English docs + Paper 5 supplement) — the largest item.
4. E re-run after C, then first public commit.

The single largest remaining item is **C** (documentation), dominated by the
English translation of `V4_LEDGER.md`.
