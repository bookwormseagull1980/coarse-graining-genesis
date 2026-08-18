# -*- coding: utf-8 -*-
"""One-shot: stamp the author / affiliation / supporting-papers banner
onto every .py module of the V4 framework (idempotent)."""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BANNER = """# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================
"""

CODING = "# -*- coding: utf-8 -*-\n"

EXCLUDE = ("comparison", "backup", "__pycache__", "archive")

MARKER = "Coarse-Graining Genesis Framework V4.0"

def stamp(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if MARKER in text:
        return False, "already stamped"
    body = text
    had_coding = body.startswith(CODING)
    if had_coding:
        body = body[len(CODING):]
    # strip leading blank lines of the body so the banner sits right after coding
    new = CODING + BANNER + "\n" + body
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    return True, ("coding" if had_coding else "no-coding")

if __name__ == "__main__":
    n = 0
    for path in glob.glob(os.path.join(ROOT, "**", "*.py"), recursive=True):
        rel = os.path.relpath(path, ROOT)
        if any(ex in rel.split(os.sep) for ex in EXCLUDE):
            continue
        if os.path.basename(path) == "stamp_banner.py":
            continue
        changed, kind = stamp(path)
        if changed:
            n += 1
            print(f"stamped [{kind:9s}] {rel}")
        else:
            print(f"skip ({kind}) {rel}")
    print(f"--- stamped {n} files ---")
