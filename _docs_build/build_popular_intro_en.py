# -*- coding: utf-8 -*-
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
