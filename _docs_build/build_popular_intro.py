# -*- coding: utf-8 -*-
"""Build the Chinese popular-introduction docx from popular_intro_zh.md.

Reuses the generic Markdown->docx renderer in build_docx.py, but switches the
body font to a CJK-capable face (Microsoft YaHei) so the Chinese renders
properly.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_docx as B
from docx import Document
from docx.shared import Pt
from docx.oxml.ns import qn

# CJK-capable body font (Microsoft YaHei has clean Latin + CJK glyphs).
B.FONT_BODY = "Microsoft YaHei"


def main():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = B.FONT_BODY
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), B.FONT_BODY)

    md_path = os.path.join(B.BASE, "popular_intro_zh.md")
    md = open(md_path, encoding="utf-8").read()
    B.render_md(doc, md)

    out = os.path.join(B.BASE, "..", "docs", "从变化到万物_通俗导读.docx")
    doc.save(out)
    print("Generated:", os.path.abspath(out))


if __name__ == "__main__":
    main()
