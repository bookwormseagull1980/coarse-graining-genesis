# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#
#  DOI records:
#    [Software] 10.5281/zenodo.22067006
#    [Paper I]  10.5281/zenodo.22067118
#    [Paper II] 10.5281/zenodo.22067469
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#         DOI: 10.5281/zenodo.22067118
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
#         DOI: 10.5281/zenodo.22067469
# =============================================================================

"""Stamp or refresh repository source-file banners.

The command is idempotent. It normalises existing V4 banners at the top of
Python, Lean, Markdown, and HTML source files, and it adds the banner to Python
and Lean source files that do not yet have one.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOI_LINES = [
    "DOI records:",
    "  [Software] 10.5281/zenodo.22067006",
    "  [Paper I]  10.5281/zenodo.22067118",
    "  [Paper II] 10.5281/zenodo.22067469",
]

BODY_LINES = [
    "Coarse-Graining Genesis Framework V4.0",
    "",
    "Author:      Jinku Guo <guojk@nwpu.edu.cn>",
    "Affiliation: Northwestern Polytechnical University, Xi'an 710072, China",
    "ORCID:       0009-0000-6600-6171",
    "",
    *DOI_LINES,
    "",
    "Part of the V4 spectral framework, whose physics is presented in the",
    "companion papers:",
    '  [I]  "The spectrum of a compact internal space.',
    '        I. Gauge structure and fermion content"',
    "       DOI: 10.5281/zenodo.22067118",
    '  [II] "The spectrum of a compact internal space.',
    '        II. Effective couplings and mass scales"',
    "       DOI: 10.5281/zenodo.22067469",
]

CODING = "# -*- coding: utf-8 -*-\n"
MARKER = "Coarse-Graining Genesis Framework V4.0"
TEXT_EXTS = {".py", ".lean", ".md", ".html"}
FORCE_STAMP_EXTS = {".py", ".lean"}
EXCLUDE_DIRS = {".git", ".pytest_cache", "__pycache__", "backup", "archive"}


def comment_banner(ext: str) -> str:
    if ext == ".lean":
        return "/-\n" + "\n".join(f" {line}" for line in BODY_LINES) + "\n-/\n"
    if ext in {".md", ".html"}:
        return "<!--\n" + "\n".join(BODY_LINES) + "\n-->\n"
    lines = ["# ============================================================================="]
    for line in BODY_LINES:
        lines.append("#" if not line else f"#  {line}")
    lines.append("# =============================================================================")
    return "\n".join(lines) + "\n"


def strip_blank_prefix(text: str) -> str:
    return text.lstrip("\ufeff\r\n\t ")


def strip_python_banner(text: str) -> tuple[str, bool]:
    lines = text.splitlines(keepends=True)
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines) or not lines[idx].lstrip().startswith("#"):
        return text, False
    if MARKER not in "".join(lines[idx : idx + 80]):
        return text, False

    seen_open = False
    end = None
    for j in range(idx, min(len(lines), idx + 120)):
        if lines[j].strip().startswith("# ============================================================================="):
            if not seen_open:
                seen_open = True
            else:
                end = j + 1
                break
    if end is None:
        return text, False
    while end < len(lines) and not lines[end].strip():
        end += 1
    return "".join(lines[:idx] + lines[end:]), True


def strip_block_banner(text: str, opener: str, closer: str) -> tuple[str, bool]:
    body = strip_blank_prefix(text)
    prefix_len = len(text) - len(body)
    removed = False
    while body.startswith(opener):
        end = body.find(closer)
        if end < 0:
            break
        block_end = end + len(closer)
        block = body[:block_end]
        if MARKER not in block:
            break
        body = body[block_end:].lstrip("\r\n")
        removed = True
    return text[:prefix_len] + body, removed


def refresh(path: Path) -> tuple[bool, str]:
    ext = path.suffix.lower()
    if ext not in TEXT_EXTS:
        return False, "skip-ext"

    text = path.read_text(encoding="utf-8")
    original = text

    coding = ""
    if ext == ".py" and text.startswith(CODING):
        coding = CODING
        text = text[len(CODING) :]

    if ext == ".py":
        text, removed = strip_python_banner(text)
    elif ext == ".lean":
        text, removed = strip_block_banner(text, "/-", "-/")
    else:
        text, removed = strip_block_banner(text, "<!--", "-->")

    should_stamp = removed or ext in FORCE_STAMP_EXTS or MARKER in original[:5000]
    if not should_stamp:
        return False, "no-banner"

    new_text = coding + comment_banner(ext) + "\n" + text.lstrip("\r\n")
    if new_text == original:
        return False, "unchanged"

    path.write_text(new_text, encoding="utf-8", newline="")
    return True, "refreshed" if removed else "stamped"


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_EXTS:
            files.append(path)
    return sorted(files, key=lambda p: str(p.relative_to(ROOT)).lower())


if __name__ == "__main__":
    changed_count = 0
    for path in iter_files():
        changed, status = refresh(path)
        rel = path.relative_to(ROOT)
        if changed:
            changed_count += 1
            print(f"{status:9s} {rel}")
        else:
            print(f"skip ({status}) {rel}")
    print(f"--- updated {changed_count} files ---")
