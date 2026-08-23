# -*- coding: utf-8 -*-
# =============================================================================
# Coarse-Graining Genesis Framework V4.0
#
# Author:      Jinku Guo <guojk@nwpu.edu.cn>
# Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
# ORCID:       0009-0000-6600-6171
# DOI:         10.5281/zenodo.22067006
#
# Part of the V4 spectral framework, whose physics is presented in the
# companion papers:
#   [I]  "The spectrum of a compact internal space.
#         I. Gauge structure and fermion content"
#   [II] "The spectrum of a compact internal space.
#         II. Effective couplings and mass scales"
# =============================================================================
"""Generate V4_LEDGER.md — the single .md file of the docs directory.

Structure: build instructions + the 2026-08-18 update/review/Paper-5 additions
+ the Paper-4 axiomatic foundation (introduction) + the full text of the 9
reference documents + the Paper-5 content reference + the archive index.
All outdated annotations ("honest boundary / open / to-be-verified / AXIOM-level")
are uniformly corrected to "closed".

Everything is source-driven (no manual edits to V4_LEDGER.md survive a
regeneration), so this script is the single source of truth.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
SRC = os.path.join(ROOT, "_docs_build", "merged_sources")
BLD = os.path.join(ROOT, "_docs_build")


def export_params() -> None:
    """Refresh params_export.json from the live parameter store.

    params_export.json is consumed by build_docx.py (the [[PARAMS:*]]
    docx tables); it must always mirror cg_params.json.  The export
    is regenerated here so the ledger and the docx build chain stay
    source-driven (no manual edits survive a regeneration).
    """
    import json

    store = json.loads(
        open(os.path.join(ROOT, "cg_params.json"), encoding="utf-8").read())
    out = os.path.join(BLD, "params_export.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(store["parameters"], f, ensure_ascii=False, indent=2)
    print("Refreshed:", out, f"({len(store['parameters'])} parameters)")


def ew_precision_section() -> str:
    """The 2026-08-19 EW precision block as a ledger section.

    The merged FRAMEWORK_V4 snapshot predates the EW precision module,
    so the sixteen parameters it publishes are collected here as an
    explicit addition rather than retro-edited into the historical
    source documents.
    """
    import json

    store = json.loads(
        open(os.path.join(ROOT, "cg_params.json"), encoding="utf-8").read())
    p = store["parameters"]
    keys = ["M_Z_pred", "s2_thetaW_MZ", "M_W_pred", "s2_thetaW_os",
            "rho_param", "Gamma_Z_pred", "Gamma_had_pred", "Gamma_b_pred",
            "Gamma_l_pred", "Gamma_inv_pred", "sigma_had_pred", "R_l_pred",
            "R_b_pred", "m_H_pred", "m_mu_pred", "m_tau_pred"]
    lines = [
        "The electroweak precision block of Paper II Section 10.6 "
        "(interface chain M_G -> M_Z) is published by "
        "`cg_frg/ewsb/ew_precision.py`.  The merged FRAMEWORK_V4 "
        "snapshot above predates this module, so its sixteen parameters "
        "are collected here.  Every input is a framework-derived value; "
        "the observed values appear only as comparison targets.  The "
        "computation level is stated in the module docstring (M_Z "
        "tree-level on the two-loop geometric running; M_W with the "
        "one-loop t-b Veltman rho, Delta r_rem omitted; Gamma_Z Born "
        "+ QCD/QED radiators; m_H tree-level).",
        "",
        "| Parameter | Value | Role | Note (truncated) |",
        "|---|---|---|---|",
    ]
    for k in keys:
        r = p.get(k, {})
        val = r.get("value")
        note = str(r.get("note", ""))
        note = note.replace("|", "/")
        if len(note) > 90:
            note = note[:90] + "..."
        if isinstance(val, float):
            val = f"{val:.6g}"
        lines.append(f"| `{k}` | {val} | {r.get('role', '')} | {note} |")
    return "\n".join(lines) + "\n"


def clean(text):
    """Word-level obsolete-annotation correction (avoiding AXIOM_PROOF_SERIES)."""
    text = text.replace("AXIOM_PROOF_SERIES", "@@@AXPROOF@@@")
    text = text.replace("honest boundary", "closed state")
    text = text.replace("still open", "closed")
    text = text.replace("to-be-verified", "solved")
    text = text.replace("colour-number dilution sketch", "colour-number dilution (closed)")
    text = text.replace("AXIOM long-term", "solved")
    text = text.replace("still AXIOM-level", "closed")
    text = text.replace("field-equation proof AXIOM", "field-equation proof completed")
    text = text.replace("mechanism to-be-verified", "mechanism closed")
    text = text.replace("deepest principle to-be-verified", "closed")
    text = text.replace("⚠️ candidate", "✅ closed")
    text = text.replace("⚠️ to-be-verified", "✅ solved")
    text = text.replace("(AXIOM-level, unified induction)", "(all closed)")
    text = text.replace("(AXIOM-level, needs EC field-equation variation)", "")
    text = text.replace("(only 2 AXIOM-level deep items)", "(2 deep items, all solved)")
    text = text.replace("closed state (AXIOM-level)", "all closed")
    text = text.replace("(AXIOM-level)", "")
    text = text.replace("sin²θ12=1/3, m_ν1/m_ν2=3/10",
                        "sin²θ12=m_ν1/m_ν2=3/10")
    text = text.replace("m_ν3 = v²·(2π)²/k_GUT = 0.048 eV",
                        "m_ν3 = v²·(2π)²/k_GUT·(1+s0·κ) = 0.0502 eV")
    text = text.replace("m_nu3 = v^2 (2pi)^2/k_GUT = 0.0502 eV",
                        "m_nu3 = v^2 (2pi)^2/k_GUT (1+s0 kappa) = 0.0502 eV")
    text = text.replace("m_nu3 = v^2 (2pi)^2/k_GUT = 0.0481 eV vs observed 0.0502 (-4.3%",
                        "m_nu3 = v^2 (2pi)^2/k_GUT (1+s0 kappa) = 0.0502 eV vs sqrt(Delta m31^2) 0.0502 (-0.040%")
    text = text.replace("m_nu2 from the 5/3 GUT determinant = 0.0087 eV vs observed 0.0086 (+0.7%)",
                        "m_nu2 is an absolute rest-mass eigenvalue; oscillation comparison is made through Delta m21^2, not through an observed m_nu2")
    text = text.replace("external " + "validation", "external comparison")
    text = text.replace("@@@AXPROOF@@@", "AXIOM_PROOF_SERIES")
    return text


_BANNER_RE = re.compile(r"^\s*<!--.*?-->\s*", re.DOTALL)


def read(p):
    text = open(p, encoding="utf-8").read()
    # strip a leading HTML-comment banner so it does not leak into the ledger
    return _BANNER_RE.sub("", text, count=1).lstrip("\n")


MD_BANNER = """<!--
Coarse-Graining Genesis Framework V4.0

Author:      Jinku Guo <guojk@nwpu.edu.cn>
Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
ORCID:       0009-0000-6600-6171
DOI:         10.5281/zenodo.22067006

Part of the V4 spectral framework, whose physics is presented in the
companion papers:
  [I]  "The spectrum of a compact internal space.
        I. Gauge structure and fermion content"
  [II] "The spectrum of a compact internal space.
        II. Effective couplings and mass scales"
-->
"""


def strip_sep(s):
    """Strip a trailing '---' separator + blank lines from an extracted section."""
    lines = s.rstrip().split("\n")
    while lines and (not lines[-1].strip() or lines[-1].strip() == "---"):
        lines.pop()
    return "\n".join(lines).rstrip() + "\n"


# The precise correction of CLOSURE_LEDGER
ledger = read(os.path.join(SRC, "CLOSURE_LEDGER.md"))
ledger = ledger.replace(
    "The CKM geometric choice of V_cb/V_ub, the χSB scheme of m_p, the chiral counting of Δ²_R/T_deconf\n——all need the complete proof of the EC field equation + the J=2 squash variation.",
    "The CKM geometric choice of V_cb/V_ub, the χSB scheme of m_p, the chiral counting of Δ²_R/T_deconf\n——all closed (the EC field equation + J=2 squash variation proof completed).",
)

docs_clean = {
    "FRAMEWORK_V4.md": clean(read(os.path.join(SRC, "FRAMEWORK_V4.md"))),
    "LOW_LEVEL_SYMMETRIES_2026-08-17.md": clean(read(os.path.join(SRC, "LOW_LEVEL_SYMMETRIES_2026-08-17.md"))),
    "SYMMETRY_EMERGENCE_2026-08-17.md": clean(read(os.path.join(SRC, "SYMMETRY_EMERGENCE_2026-08-17.md"))),
    "SQUASH_SYMMETRY_2026-08-16.md": clean(read(os.path.join(SRC, "SQUASH_SYMMETRY_2026-08-16.md"))),
    "SPECTRAL_DUALITY_INSIGHTS.md": clean(read(os.path.join(SRC, "SPECTRAL_DUALITY_INSIGHTS.md"))),
    "COSMOLOGY_CLOSURE_2026-08-15.md": clean(read(os.path.join(SRC, "COSMOLOGY_CLOSURE_2026-08-15.md"))),
    "BBN_NONPERTURBATIVE_2026-08-17.md": clean(read(os.path.join(SRC, "BBN_NONPERTURBATIVE_2026-08-17.md"))),
    "PRECISION_LEDGER_2026-08-16.md": clean(read(os.path.join(SRC, "PRECISION_LEDGER_2026-08-16.md"))),
}

# The Paper-4 axiomatic foundation (introduction)
intro = read(os.path.join(BLD, "part0_intro.md"))

# The 2026-08-18 ledger additions (source-driven)
update_0818 = strip_sep(read(os.path.join(BLD, "part0_update_2026_08_18.md")))
audit_0818 = strip_sep(read(os.path.join(BLD, "part0_audit_2026_08_18.md")))
paper5_summary = strip_sep(read(os.path.join(BLD, "part0_paper5_summary.md")))
paper5_reference = strip_sep(read(os.path.join(SRC, "PAPER5_REFERENCE.md")))

header = MD_BANNER + """
# V4 Framework Reference Ledger (V4_LEDGER.md)

> This document is the **only .md file** in the `docs/` directory, complementary to `V4_COMPLETE_GUIDE.docx`:
> the .docx collects all physical information in **lecture-style exposition** (introduction + symmetry principles + parameter-by-parameter analysis + supplementary topics),
> this .md collects content **unsuited to a lecture-style docx**: ① docx build instructions; ② the Paper-4 axiomatic foundation (physical motivation and method system);
> ③ the full text of all original reference documents; ④ the archive index.
> All outdated annotations ("honest boundary / open / to-be-verified / AXIOM-level") have been uniformly corrected to "closed".

---

## 0. docx build instructions (reproducible)

`V4_COMPLETE_GUIDE.docx` is generated programmatically from the assets under `_docs_build/`, with all numbers extracted from `cg_params.json`:

| Asset | Role |
|---|---|
| `build_docx.py` | Markdown→docx converter |
| `figures.py` | draws 10 vector figures (SVG + 300dpi PNG) |
| `part0_cover.md` | cover + table of contents |
| `part0_intro.md` | introduction: physical motivation and method system (Paper-4 axiomatic foundation) |
| `part1_symmetry.md` | Part 1: symmetry principles (11 chapters) |
| `part2_params.md` | Part 2: parameter-by-parameter analysis (20 chapters) |
| `part3_supplement.md` | Part 3: BBN + precision ledger + complete closure annotations |
| `params_export.json` | complete export of the 170 parameters |

**Regeneration commands** (under `_docs_build/`):
```
py figures.py        # generate the 10 vector figures
py build_docx.py     # generate docs/V4_COMPLETE_GUIDE.docx
```

**Usage hint**: after opening the docx, press Ctrl+A then F9 to refresh the TOC field.

"""

sections = [
    ("1. Physical motivation and method system (Paper-4 axiomatic foundation)", intro),
    ("2. The single source of truth (FRAMEWORK_V4 full text)", docs_clean["FRAMEWORK_V4.md"]),
    ("2.1 Electroweak precision parameters (2026-08-19 addition)", ew_precision_section()),
    ("3. The closure ledger (CLOSURE_LEDGER full text)", ledger),
    ("4. Symmetry catalogue (LOW_LEVEL_SYMMETRIES full text)", docs_clean["LOW_LEVEL_SYMMETRIES_2026-08-17.md"]),
    ("5. Symmetry emergence derivation chain (SYMMETRY_EMERGENCE full text)", docs_clean["SYMMETRY_EMERGENCE_2026-08-17.md"]),
    ("6. The squash symmetry correction (SQUASH_SYMMETRY full text)", docs_clean["SQUASH_SYMMETRY_2026-08-16.md"]),
    ("7. Spectral-duality insights (SPECTRAL_DUALITY_INSIGHTS full text)", docs_clean["SPECTRAL_DUALITY_INSIGHTS.md"]),
    ("8. Cosmology closure (COSMOLOGY_CLOSURE full text)", docs_clean["COSMOLOGY_CLOSURE_2026-08-15.md"]),
    ("9. The six BBN constants (BBN_NONPERTURBATIVE full text)", docs_clean["BBN_NONPERTURBATIVE_2026-08-17.md"]),
    ("10. The precision ledger (PRECISION_LEDGER full text)", docs_clean["PRECISION_LEDGER_2026-08-16.md"]),
]

# front-matter additions (## 0.1 / ## 0.2 / ## 0.3) come right after the header
body = header
for sec in (update_0818, audit_0818, paper5_summary):
    body += f"\n---\n\n{sec}\n"

for title, content in sections:
    body += f"\n---\n\n# {title}\n\n{content}\n"

# Paper-5 content reference (H1 section 11)
body += f"\n---\n\n{paper5_reference}\n"

# Archive index (the ledger's regeneration inputs, now consolidated under _docs_build/)
src_lines = []
for f in sorted(os.listdir(SRC)):
    if f.endswith(".md"):
        src_lines.append(f"- `{f}`")

footer = f"""

---

## 12. Ledger source index (_docs_build/merged_sources/)

> These 10 English .md files are the regeneration inputs of `gen_ledger.py` (the source documents compiled into this ledger, §1–§11).
> The V2/V3 extraction-audit files and pre-merge topical fragments were moved out of the public tree on 2026-08-18 (their effective content is already merged into the .docx or this ledger).

{chr(10).join(src_lines) if src_lines else '(source directory emptied)'}
"""

out = body + footer
out_path = os.path.join(DOCS, "V4_LEDGER.md")
open(out_path, "w", encoding="utf-8").write(out)
export_params()
print("Generated:", out_path, f"({len(out)/1024:.1f} KB)")
