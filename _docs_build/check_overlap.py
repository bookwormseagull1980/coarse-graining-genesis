# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo <guojk@nwpu.edu.cn>
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#  ORCID:       0009-0000-6600-6171
#  DOI:         10.5281/zenodo.22067006
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""bbox overlap check v2: exclude the normal "text inside its own box" case,
report only true overlaps (box-box, text-text, text-foreign-box)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import figures as F

captured = {}
def fake_save(fig, name):
    captured[name] = fig
F.save = fake_save

F.fig2_dependency_tree()
F.fig5_two_pi()

for name in ["fig02_dependency_tree", "fig05_two_pi"]:
    fig = captured[name]
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax = fig.axes[0]

    boxes = []
    for p in ax.patches:
        if isinstance(p, FancyBboxPatch):
            bb = p.get_window_extent(renderer)
            boxes.append(bb)

    texts = []
    for t in ax.texts:
        bb = t.get_window_extent(renderer)
        # text centre
        cx = (bb.x0 + bb.x1) / 2; cy = (bb.y0 + bb.y1) / 2
        texts.append((t.get_text()[:20].replace("\n", " "), bb, cx, cy))

    problems = []

    # 1) box-box overlap
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i].overlaps(boxes[j]):
                problems.append(f"box-box overlap: box#{i} <-> box#{j}")

    # 2) text-text overlap (both not box-internal text — box-internal text is a text inside a box, must be excluded)
    #    here simply report all text-text overlaps (between titles/labels/annotations)
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if texts[i][1].overlaps(texts[j][1]):
                problems.append(f"text-text overlap: [{texts[i][0]}] <-> [{texts[j][0]}]")

    # 3) text-foreign-box overlap (text centre not inside that box but the bbox overlaps)
    for ti, (txt, bb, cx, cy) in enumerate(texts):
        for bi, bbb in enumerate(boxes):
            if bb.overlaps(bbb):
                inside = (bbb.x0 <= cx <= bbb.x1) and (bbb.y0 <= cy <= bbb.y1)
                if not inside:
                    problems.append(f"text-foreign-box overlap: [{txt}] <-> box#{bi}")

    print(f"=== {name}: {len(boxes)} boxes, {len(texts)} texts, {len(problems)} true problems ===")
    for p in problems[:25]:
        print("  ", p)
    if not problems:
        print("   ✅ no true overlap")
