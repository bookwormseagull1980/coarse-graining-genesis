# -*- coding: utf-8 -*-
# =============================================================================
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

"""Draw the vector figures of the V4 complete guide (SVG + high-resolution PNG).

Each figure is saved twice:
  - .svg  (vector source, losslessly scalable)
  - .png  (300 dpi, for embedding into the docx)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import os

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 11

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

GOLD = "#8a6d1a"
BLUE = "#1f4e79"
GREEN = "#2e6b3a"
RED = "#8c2f2f"
PURPLE = "#5b2c6f"
GRAY = "#555555"
BG = "#f7f5ef"


def save(fig, name):
    fig.savefig(os.path.join(OUT, name + ".svg"), format="svg",
                bbox_inches="tight", facecolor=BG)
    fig.savefig(os.path.join(OUT, name + ".png"), format="png", dpi=300,
                bbox_inches="tight", facecolor=BG)
    plt.close(fig)
    print("  saved", name)


def box(ax, x, y, w, h, text, fc, fs=10, tc="white", ec="none", bold=True):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle="round,pad=0.02,rounding_size=0.06",
                       linewidth=1.0, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=tc, zorder=3,
            fontweight="bold" if bold else "normal")
    return p


def arrow(ax, x1, y1, x2, y2, color=GRAY, lw=1.4, style="-|>"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                        mutation_scale=14, linewidth=lw, color=color, zorder=1)
    ax.add_patch(a)


# ----------------------------------------------------------------------
def fig1_overview():
    """Figure 1: framework overview — spectrum → duality → emergence → 4D physics"""
    fig, ax = plt.subplots(figsize=(11, 5.6))
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.6); ax.axis("off")

    # top title
    ax.text(5.5, 5.25, "Coarse-Graining Genesis framework overview",
            ha="center", va="center", fontsize=15, fontweight="bold", color="#222222")

    # four stages
    box(ax, 0.25, 3.0, 2.2, 1.5, "Spectrum\n(discrete data)\nRP³ spectral sums\nWeyl law / heat kernel / Z_2 winding", BLUE, fs=9)
    box(ax, 3.05, 3.0, 2.5, 1.5, "Duality (four dualities)\n① conformal-gauge  ξ·N_g=1\n② geometric-gauge  d=N_c=3\n③ UV-IR  window span\n④ spectral-physical  spectral sums", PURPLE, fs=9.5)
    box(ax, 6.15, 3.0, 2.2, 1.5, "Emergence\n(continuous structure)\ngauge group / geometry\nentropy S = ln W = ∫γ_M", GREEN, fs=9)
    box(ax, 8.95, 3.0, 1.85, 1.5, "4D physics\n(observable)\n147 closed parameters", RED, fs=10)

    arrow(ax, 2.45, 3.75, 3.05, 3.75)
    arrow(ax, 5.55, 3.75, 6.15, 3.75)
    arrow(ax, 8.35, 3.75, 8.95, 3.75)

    # bottom: single dimensional anchor
    box(ax, 0.25, 1.0, 2.2, 1.2, "Single dimensional anchor\nG_N (observed, comparison only)\nM_P = 1/√(8πG_N)", GOLD, fs=9.5)
    box(ax, 3.05, 1.0, 5.1, 1.2, "Fully internal closure (zero observational anchor, except G_N)\ngeometric RGE + redshift=spectrum + acceleration scale a0 + symmetry pinning", GREEN, fs=9.5)
    box(ax, 8.75, 1.0, 2.05, 1.2, "All closed\nEC field-equation\nvariation completed", RED, fs=9.5)
    arrow(ax, 2.45, 1.6, 3.05, 1.6)
    arrow(ax, 8.15, 1.6, 8.75, 1.6)

    ax.text(5.5, 0.25, "Highest principle: duality emergence — entropy is the bridge of the UV<->IR duality",
            ha="center", va="center", fontsize=11, fontweight="bold", color=PURPLE)
    save(fig, "fig01_overview")


# ----------------------------------------------------------------------
def fig2_dependency_tree():
    """Figure 2: the low-level symmetry dependency tree (6 layers + source)"""
    fig, ax = plt.subplots(figsize=(11.5, 8.8))
    ax.set_xlim(0, 11.5); ax.set_ylim(0, 8.8); ax.axis("off")
    ax.text(5.75, 8.45, "Low-level symmetry dependencies: source → corollary (one-way, acyclic)",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    layers = [
        ("Layer 0 · source (irreducible)", GOLD, [
            "RP³=S³/Z_2\nd=3, π_1=Z_2", "SO(4)≅\nSU(2)_L×SU(2)_R",
            "ξ=1/8\nΔ_f=3/2, Δ_s=1/2", "2π period", "15 Weyl\n+ hypercharge table Y"]),
        ("Layer 1 · content identities (integer counting)", BLUE, [
            "ΣY=0\n→ΣY²=10/3", "N_L=8, N_R=7\nN_L−N_R=1",
            "N_g=N_c²−1=8", "n_broken=2"]),
        ("Layer 2 · duality bridge (welds content/gauge/geometry)", PURPLE, [
            "N_L=N_g=8\ncontent=gauge", "N_g·ξ=1\n⇒ d=N_c=3", "N_g·Δ_s\n=2(d−1)"]),
        ("Layer 3 · core modulus + content ratios", GREEN, [
            "τ=1/50", "r12=3/10\nr23=3/(10√3)", "8/7, 9/8, 5/3", "N_g=(d+1)·n_broken"]),
        ("Layer 4 · geometric dynamics (EC torsion + squash)", RED, [
            "s0=2τ\n=N_g·τ/(d+1)", "λ_EC=14+8τ+2τ²\nλ_TT=2N_R=14",
            "s0/N_R=1/175", "κ²(2τ)", "conservation laws\ng_2/squash/ρ_Λ"]),
        ("Layer 5 · spectrum + applied symmetries (most derived)", GRAY, [
            "glueball spectrum\nn=Z_2 winding", "ladder\nα_up=kL−2τ", "CP δ_CKM=8π/21\nη_B=α_W^5/56",
            "BBN g_A=4/π", "acceleration scale a0\n(derived, no dynamics)"]),
    ]

    # layer coordinates: top to bottom, enough spacing (labels left, boxes right, no overlap)
    y_top = 7.55
    dy = 1.24
    box_left = 4.3
    avail = 11.5 - box_left - 0.55   # reserve space on the right for the "derived" arrows
    gap = 0.1

    for idx, (label, color, items) in enumerate(layers):
        y = y_top - idx * dy
        # label on the left, vertically centred on the layer (fontsize 9.5 so long labels stay clear of the box area)
        ax.text(0.25, y, label, fontsize=9.5, fontweight="bold", color=color,
                va="center", ha="left")
        n = len(items)
        w = (avail - (n - 1) * gap) / n
        for i, it in enumerate(items):
            x = box_left + i * (w + gap)
            box(ax, x, y - 0.47, w, 0.94, it, color, fs=8.5)

    # arrows between layers (right side showing derivation)
    for idx in range(5):
        ytop = y_top - idx * dy
        arrow(ax, 11.35, ytop - 0.5, 11.35, ytop - dy + 0.5, color=GRAY, lw=1.6)
        ax.text(11.35, ytop - dy / 2, "derived", fontsize=8.5, color=GRAY,
                va="center", ha="center", rotation=90)

    ax.text(0.25, 0.32, "Two \"bridges\" (N_L=N_g, N_g·ξ=1⇒d=N_c) weld the sources shut; τ is the single \"master switch\", 2π the single \"running quantity\".",
            fontsize=10, color="#222", va="center")
    save(fig, "fig02_dependency_tree")


# ----------------------------------------------------------------------
def fig3_dimensional_chain():
    """Figure 3: single dimensional anchor → full-parameter closure (the dimensional anchor chain)"""
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(5.5, 4.85, "Single dimensional anchor G_N → full-parameter closure (the dimensional anchor chain)",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    chain = [
        ("G_N", "single observed anchor\n1/(8πM_P²)", GOLD),
        ("M_P", "reduced Planck mass\n1/√(8πG_N)", BLUE),
        ("M_G", "M_P·√π/kL\ncoarse-graining scale", BLUE),
        ("kL", "window capacity\nF_MG fixed point", GREEN),
        ("∫γ_M", "entropy integral\nln(kL·M_G/H0)", PURPLE),
        ("H0 / Λ", "IR entropy maximum\nneutrino floor", RED),
    ]
    n = len(chain)
    w = 1.72
    total = n * w + (n - 1) * 0.28
    x0 = (11 - total) / 2
    for i, (t, d, c) in enumerate(chain):
        x = x0 + i * (w + 0.28)
        box(ax, x, 2.6, w, 1.5, t + "\n" + d, c, fs=9)
        if i < n - 1:
            arrow(ax, x + w, 3.35, x + w + 0.28, 3.35)

    # sector expansion below
    box(ax, 0.3, 0.55, 1.75, 1.2, "gauge sector\ng_1 g_2 g_3", GREEN, fs=9)
    box(ax, 2.2, 0.55, 1.75, 1.2, "electroweak\nv / ε", BLUE, fs=9)
    box(ax, 4.1, 0.55, 1.75, 1.2, "generation\nLZ ladder", PURPLE, fs=9)
    box(ax, 6.0, 0.55, 1.75, 1.2, "cosmology\nH0 Ω T_CMB", RED, fs=9)
    box(ax, 7.9, 0.55, 1.75, 1.2, "flavour/fermion\nneutrino quark", GOLD, fs=9)
    box(ax, 9.8, 0.55, 1.0, 1.2, "QCD\nglueball confinement", GRAY, fs=8.5)
    for xc in [1.175, 3.075, 4.975, 6.875, 8.775]:
        arrow(ax, xc, 2.6, xc, 1.8)

    ax.text(0.3, 0.12, "KK mass spectrum m_n=(n+3/2)/kL·M_G (n=0/2/4 → 0.43/1.0/1.56 M_P); window edge kL·M_G=M_P·√π (0.036%)",
            fontsize=9, color="#222")
    save(fig, "fig03_dimensional_chain")


# ----------------------------------------------------------------------
def fig4_modules():
    """Figure 4: the 40-module dependency chain (by sector)"""
    fig, ax = plt.subplots(figsize=(11, 6.8))
    ax.set_xlim(0, 11); ax.set_ylim(0, 6.8); ax.axis("off")
    ax.text(5.5, 6.45, "40 chain-item dependency order (reproduce_v4.py execution order, by sector)",
            ha="center", fontsize=13.5, fontweight="bold", color="#222")

    sectors = [
        ("0 anchor/seeds", "init_v4", GOLD),
        ("1 SM running table", "run_rge · spectrum_loop · sm_content", BLUE),
        ("2 FRG flow", "spectral_sum · endpoint_constraint · gamma_M · ir_flow\n· trace_density · discrete_flow", GREEN),
        ("3 gauge", "geometric_couplings · geometric_ewsb · gauge_group_emergence", PURPLE),
        ("4 generation", "window_capacity · sector_alpha · lz_ladder", BLUE),
        ("5 electroweak", "vev_closure · relaxion_chain · relaxion_geo · epsilon_ratio\n· order_parameter · pseudo_dilaton", RED),
        ("6 cosmology", "spectral_tilt · dark_energy · bbn_helium · perturbation_amplitude\n· gw_ratio", GREEN),
        ("7 gravity", "tt_tensor · pole_analysis · chi_pole_condition · newton\n· zk_gravitational_rg", PURPLE),
        ("8 flavour/fermion", "neutrino_closure · mass_operator_overlap · electron_mass", GOLD),
        ("9 framework layer", "five_items · cp_sector · sigma_language", GRAY),
        ("10 QCD", "mass_gap_scale · qcd_sector", RED),
    ]
    y = 6.0
    h = 0.52
    for name, mods, color in sectors:
        box(ax, 0.35, y - 0.1, 2.4, h, name, color, fs=9.5)
        ax.text(2.95, y + 0.16, mods, fontsize=9, color="#333", va="center", ha="left")
        y -= h + 0.03

    ax.text(0.35, y - 0.2, "Parameter-store scale: cg_params 147 keys (DERIVED 146 + OBSERVED 1 = G_N_PDG)",
            fontsize=10, color="#222", fontweight="bold")
    save(fig, "fig04_modules")


# ----------------------------------------------------------------------
def fig5_two_pi():
    """Figure 5: the 2π Euclidean period family (the UV<->IR public thread)"""
    fig, ax = plt.subplots(figsize=(11, 6.0))
    ax.set_xlim(0, 11); ax.set_ylim(-0.5, 6.0); ax.axis("off")
    ax.text(5.5, 5.65, "The 2π Euclidean period family — the public geometric thread running through UV<->IR",
            ha="center", va="center", fontsize=14, fontweight="bold", color="#222")

    # central circle (2π)
    c = Circle((5.5, 2.7), 0.95, facecolor=GOLD, edgecolor="none", zorder=2, alpha=0.9)
    ax.add_patch(c)
    ax.text(5.5, 2.7, "2π\nEuclidean\nperiod", ha="center", va="center",
            fontsize=11, fontweight="bold", color="white", zorder=3)

    items = [
        (0.6, 4.3, "ε = e^(1/2π)\nEW ratio zero point", BLUE),
        (2.7, 4.6, "2L = √(2π)\nentropy minimal distance", GREEN),
        (4.9, 4.7, "kL ≈ √(2π)\nwindow width", GREEN),
        (8.4, 4.4, "r = (1/2π)²\ntensor-to-scalar ratio", RED),
        (10.0, 3.2, "Δ²_0=(1/2)(1/2π)²\nscalar zero point", RED),
        (0.5, 1.0, "a0 = cH0/(2π)\nderived scale (no dynamics)", PURPLE),
        (2.6, 0.5, "g_A = 4/π\naxial coupling", BLUE),
        (6.4, 0.5, "σ=(λ_TT/π)Λ²\nstring tension", GOLD),
        (9.0, 1.0, "sin²θ13=(1/2π)²√3/2\n2π imprint", GRAY),
    ]
    import math as _math
    for x, y, txt, color in items:
        box(ax, x - 0.8, y - 0.33, 1.6, 0.66, txt, color, fs=8.5)
        # faint radial lines (box edge → central circle edge, avoiding long arrows crossing other boxes)
        _dx = 5.5 - x; _dy = 2.7 - y
        _d = _math.hypot(_dx, _dy)
        if _d > 1e-9:
            _ux, _uy = _dx / _d, _dy / _d
            ax.plot([x + _ux * 0.8, 5.5 - _ux * 0.95],
                    [y + _uy * 0.33, 2.7 - _uy * 0.95],
                    color="#c8c8c8", lw=0.9, zorder=1)

    ax.text(5.5, -0.12, "Physics: 2π = the window causal-horizon temperature T_eff = k/(2π); the hierarchy v/ε/Λ is the dilaton powers {1,1,10}, whose public thread is 2π",
            ha="center", va="center", fontsize=10, color="#222")
    save(fig, "fig05_two_pi")


# ----------------------------------------------------------------------
def fig6_content_symmetry():
    """Figure 6: content symmetry N_L=N_g=8 (fermion content = colour generators)"""
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.4); ax.axis("off")
    ax.text(5, 5.0, "Content = structure: N_L = N_g = 8 (fermion content = colour generators)",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    # left-handed content
    box(ax, 0.3, 2.4, 4.3, 1.8,
        "Left-handed components (per generation) N_L = 8\nQ_L(3×2=6) + L_L(1×2=2)\n= 6 + 2 = 8", BLUE, fs=10)
    # right-handed content
    box(ax, 0.3, 0.6, 4.3, 1.5,
        "Right-handed components (per generation) N_R = 7\nu_R(3)+d_R(3)+e_R(1)\n= 3+3+1 = 7 = N_g−1", GRAY, fs=10)
    # colour generators
    box(ax, 5.5, 2.4, 4.2, 1.8,
        "Colour generators N_g = 8\nN_c²−1 = 3²−1\nsu(3) adjoint-representation dimension", RED, fs=10)
    # difference
    box(ax, 5.5, 0.6, 4.2, 1.5,
        "Chiral asymmetry N_L−N_R = 1\n= Z_2 non-trivial spin structure\n(the numerator of τ)", PURPLE, fs=10)

    arrow(ax, 4.6, 3.3, 5.5, 3.3, color=GREEN, lw=2.2)
    ax.text(5.05, 3.6, "=", fontsize=16, fontweight="bold", color=GREEN, ha="center")

    ax.text(5, 0.15, "The chiral carrier and the gauge carrier are isomorphic (both live in an 8-fold content); the typical \"content=structure\" common origin, and the gauge source of the numerator of τ, r12, s0",
            ha="center", fontsize=9.5, color="#222")
    save(fig, "fig06_content_symmetry")


# ----------------------------------------------------------------------
def fig7_squash():
    """Figure 7: the squash level transfer + pairing conservation"""
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(5.5, 4.85, "The squash level transfer: pairing conservation under a symmetry transformation",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    # group 1: EW <-> seesaw
    ax.text(0.5, 3.9, "Group 1 · EW <-> seesaw (conserved v·m_ν3)", fontsize=10.5,
            fontweight="bold", color=BLUE)
    box(ax, 0.6, 2.5, 2.5, 1.0, "v → v(1 − s0·κ)\nEW level decreases", BLUE, fs=9.5)
    box(ax, 4.1, 2.5, 2.5, 1.0, "m_ν3 → m_ν3(1 + s0·κ)\nseesaw increases", RED, fs=9.5)
    arrow(ax, 3.1, 3.0, 4.1, 3.0, color=GREEN, lw=2)
    ax.text(3.6, 3.3, "pairing cancellation", fontsize=9, color=GREEN, ha="center")
    ax.text(3.6, 1.9, "(1−s0·κ)(1+s0·κ)=1−(s0·κ)²", fontsize=9.5, color="#222", ha="center")

    # group 2: seesaw <-> dark energy
    ax.text(6.9, 3.9, "Group 2 · seesaw <-> dark energy (conserved m_ν1^4·weight)", fontsize=10.5,
            fontweight="bold", color=PURPLE)
    box(ax, 7.0, 2.5, 1.9, 1.0, "m_ν1^4\n→(1+4s0·κ)", PURPLE, fs=9.5)
    box(ax, 9.15, 2.5, 1.6, 1.0, "ρ_Λ weight\n→(1−4s0·κ)", RED, fs=9.5)
    arrow(ax, 8.9, 3.0, 9.15, 3.0, color=GREEN, lw=2)
    ax.text(8.55, 1.9, "(1+s0·κ)^4(1−4s0·κ)=1−6(s0·κ)²−…", fontsize=9, color="#222", ha="center")

    ax.text(5.5, 0.5, "squash = the symmetry transformation of the J=2 isometry breaking SU(2)_R→U(1)_Y: it does not change the content, only redistributes it between levels, hence conservation.\n"
                      "s0 = N_g·τ/(d+1) = 2τ (the squash amplitude); s0·κ = 0.045273 (amplitude × U(1)_Y normalisation).",
            ha="center", fontsize=10, color="#222")
    save(fig, "fig07_squash")


# ----------------------------------------------------------------------
def fig8_entropy():
    """Figure 8: the entropy core — UV Gaussian window → IR entropy maximum (window span)"""
    fig, ax = plt.subplots(figsize=(11, 5.0))
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.0); ax.axis("off")
    ax.text(5.5, 4.65, "The entropy core: two-end regularisation (UV Gaussian window <-> IR entropy maximum)",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    box(ax, 0.35, 2.0, 3.3, 1.9,
        "UV end · Gaussian window (ordered)\nwindow capacity (kL)²\nM_G = M_P·√π/kL\nheat_kernel expansion\n(precision +0.002%)", BLUE, fs=9.5)
    box(ax, 7.35, 2.0, 3.3, 1.9,
        "IR end · entropy maximum (disordered)\nH0 = M_P·√π·e^(−∫γ_M)\nneutrino floor ρ_Λ=Y_u·m_ν1^4\n(maximum-entropy state MaxEnt)", RED, fs=9.5)

    # middle window span
    box(ax, 3.85, 2.35, 3.3, 1.2, "entropy integral ∫γ_M\n= ln(kL·M_G/H0)\n= 139.253", GOLD, fs=10.5)
    arrow(ax, 3.65, 2.95, 3.85, 2.95)
    arrow(ax, 7.15, 2.95, 7.35, 2.95)

    ax.text(5.5, 1.45, "window span = e^(139.253) = 3×10^6^0 = phase-space volume; S = ln W (Boltzmann entropy analogy)",
            ha="center", fontsize=11, color="#222")
    ax.text(5.5, 0.85, "entropy is the bridge of the UV<->IR duality: entropy encodes geometry (holography analogy). Window edge kL·M_G = M_P·√π (0.036% cross-check)",
            ha="center", fontsize=10, color=PURPLE)
    ax.text(5.5, 0.3, "duality emergence driven by \"disorder\": UV Gaussian window (ordered, scale-invariant) → IR entropy maximum (disordered, maximal entropy)",
            ha="center", fontsize=9.5, color=GRAY)
    save(fig, "fig08_entropy")


# ----------------------------------------------------------------------
def fig9_cosmology():
    """Figure 9: the cosmology-sector closure chain (zero observational anchor)"""
    fig, ax = plt.subplots(figsize=(11, 5.2))
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.2); ax.axis("off")
    ax.text(5.5, 4.85, "The cosmology-sector closure (zero observational anchor, except G_N)",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    chain = [
        ("G_N", GOLD), ("M_P", BLUE), ("M_G/kL", BLUE),
        ("ρ_Λ\n(Y_u·m_ν1^4)", PURPLE), ("∫γ_M\n(two Gaussians + r23)", PURPLE),
        ("H0", RED), ("Ω_Λ\n2/3+r23/3π", RED),
    ]
    n = len(chain)
    w = 1.35
    total = n * w + (n - 1) * 0.22
    x0 = (11 - total) / 2
    for i, (t, c) in enumerate(chain):
        x = x0 + i * (w + 0.22)
        box(ax, x, 2.9, w, 1.0, t, c, fs=9)
        if i < n - 1:
            arrow(ax, x + w, 3.4, x + w + 0.22, 3.4)

    out = [
        ("T_CMB = m_ν1·r12/π·(1−τ·Δ_s)\nneutrino photon floor (redshift=spectrum)", BLUE),
        ("a0 = cH0/(2π)·√(4/3)\nderived Milgrom-coincidence scale", PURPLE),
        ("η_B = J·α_W^5/56\nSakharov baryogenesis", GREEN),
        ("m_p = (279/64)Λ_QCD\nconstituent quark", GOLD),
        ("Ω_b+Ω_DM+Ω_Λ = 1.00000\nexact flatness (not a fit)", RED),
    ]
    for i, (t, c) in enumerate(out):
        x = 0.5 + (i % 5) * 2.05
        y = 1.3 if i < 5 else 0.2
        box(ax, x, y, 1.9, 1.0, t, c, fs=8.5)

    ax.text(5.5, 0.05, "Three fixes: frozen_exponent sign, m_ν1 consistency, H0 circularity (tautology → internal two-Gaussian entropies)",
            ha="center", fontsize=9, color=GRAY)
    save(fig, "fig09_cosmology")


# ----------------------------------------------------------------------
def fig10_hierarchy():
    """Figure 10: the hierarchy structure v/ε/Λ (dilaton powers)"""
    fig, ax = plt.subplots(figsize=(10, 5.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.0); ax.axis("off")
    ax.text(5, 4.65, "The hierarchy structure: the symmetry correction of the EW-level identity",
            ha="center", fontsize=14, fontweight="bold", color="#222")

    ax.text(5, 3.9, "ln(M_G/v) = 4πkL − ln(3α/π) + s0·κ  =  4πkL + ln(16π³/3) + s0·κ",
            ha="center", fontsize=12.5, color="#222",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=BG, edgecolor=GOLD, linewidth=1.5))

    parts = [
        ("window circumference 4πkL", BLUE), ("loop factor ln(16π³/3)", GREEN), ("J=2 squash correction s0·κ", RED),
    ]
    for i, (t, c) in enumerate(parts):
        box(ax, 0.5 + i * 3.1, 2.3, 2.9, 0.9, t, c, fs=10)

    ax.text(5, 1.45, "v = v_raw·(1−s0·κ) = 246.19 GeV (−0.012%); ε = e^(1/(2π))·e^(−φ_stop); v = M_G·ε",
            ha="center", fontsize=10.5, color="#222")
    ax.text(5, 0.75, "s0·κ is the correction of the J=2 squash on the dilaton-stop position φ_R3 — the same κ enters g_1=g_2·κ: \"one geometric dynamics, two levels\".",
            ha="center", fontsize=9.5, color=PURPLE)
    save(fig, "fig10_hierarchy")


if __name__ == "__main__":
    print("Drawing vector figures …")
    fig1_overview()
    fig2_dependency_tree()
    fig3_dimensional_chain()
    fig4_modules()
    fig5_two_pi()
    fig6_content_symmetry()
    fig7_squash()
    fig8_entropy()
    fig9_cosmology()
    fig10_hierarchy()
    print("Done:", os.listdir(OUT))
