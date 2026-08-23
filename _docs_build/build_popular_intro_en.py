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

"""Build the English popular-introduction docx from popular_intro_en.md.

Reuses the generic Markdown->docx renderer in build_docx.py with its default
Calibri body font (no CJK needed).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_docx as B
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn


def main():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = B.FONT_BODY
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), B.FONT_BODY)

    md_path = os.path.join(B.BASE, "popular_intro_en.md")
    md = open(md_path, encoding="utf-8").read()
    B.render_md(doc, md)

    out = os.path.join(B.BASE, "..", "docs", "From Change to Everything - A Popular Science Introduction.docx")
    doc.save(out)
    print("Generated:", os.path.abspath(out))


if __name__ == "__main__":
    main()
