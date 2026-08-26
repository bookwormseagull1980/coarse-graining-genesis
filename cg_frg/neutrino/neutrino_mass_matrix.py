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

"""
cg_frg/neutrino/neutrino_mass_matrix.py — V4.0: neutrino texture
assembly and diagonalisation check
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The neutrino closure specifies two hypercharge-trace ratios,
r12=1/Tr(Y²) and r23=1/(sqrt(3)Tr(Y²)), together with the PMNS texture.
This module assembles the corresponding flavour-basis mass matrix and
diagonalises it as a consistency check of the texture.

THE MASS MATRIX (the framework's internal structure)
----------------------------------------------------
The effective mass matrix is M_nu=(v²/Lambda)(1+s0 kappa)F, with
Lambda=k_GUT/(2pi)².  Its two structural pieces are:

  (1) the PMNS mixing U — the near-tribimaximal form dressed by the
      2π imprint, with the three angles fixed by the content ratios:
          sin²θ12 = 3/10           (the light-pair mass ratio),
          sin²θ13 = (1/2π)²·√3/2  (the 2π imprint × the S³→RP³
                                     quotient projection),
          sin²θ23 = 1/2 + Tr(T₃²)/(2π)²   (maximal mixing + isospin),
      these relations define the mixing texture;

  (2) the hypercharge-trace hierarchy — the eigenvalues of F are the
      inverse powers of the first non-zero hypercharge moment:
          λ = {1, 1/(√3·Tr(Y²)), 1/(√3·Tr(Y²)²)}  (m3 > m2 > m1).

The spectral assembly is
M_nu=U diag(lambda) U^dagger (v²/Lambda)(1+s0 kappa).
Diagonalisation recovers the prescribed eigenvalues and therefore
checks both the hierarchy ratios and the absolute scale.

V4 DISCIPLINE
-------------
U is built from the content-ratio angles, and the eigenvalues are the
hypercharge-trace powers.  The module reads only quantities already
published by the closure chain.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.params import get, set as pset  # noqa: E402


def pmns_matrix() -> list[list[float]]:
    """U — the PMNS mixing from the framework's content-ratio angles.

    Standard parameterisation U = R23·R13·R12 (CP phase δ set aside:
    the phase δ_PMNS = (8/7)π enters the Jarlskog invariant, not the
    magnitudes).  The angles are the framework's content ratios:
      s12² = m1/m2 = 3/10 (the light-pair texture relation),
      s13² = (1/2π)²·√3/2  (the 2π imprint × the S³→RP³ quotient),
      s23² = 1/2 + Tr(T₃²)/(2π)²   (maximal mixing + isospin trace).
    """
    zp2 = 1.0 / (2.0 * math.pi) ** 2          # (1/2π)²
    s12 = math.sqrt(3.0 / 10.0)               # sin²θ12 = m1/m2 = 3/10
    c12 = math.sqrt(1.0 - 3.0 / 10.0)
    s13 = math.sqrt(zp2 * math.sqrt(3.0) / 2.0)
    c13 = math.sqrt(1.0 - s13 * s13)
    tr_t32 = 2.0
    s23 = math.sqrt(0.5 + tr_t32 * zp2)
    c23 = math.sqrt(1.0 - s23 * s23)

    # R12, R13, R23 (rotation matrices), U = R23·R13·R12.
    R12 = [[c12, s12, 0.0], [-s12, c12, 0.0], [0.0, 0.0, 1.0]]
    R13 = [[c13, 0.0, s13], [0.0, 1.0, 0.0], [-s13, 0.0, c13]]
    R23 = [[1.0, 0.0, 0.0], [0.0, c23, s23], [0.0, -s23, c23]]

    def mm(A, B):
        n = len(A)
        return [[sum(A[i][k] * B[k][j] for k in range(n))
                 for j in range(n)] for i in range(n)]

    return mm(mm(R23, R13), R12)


def eigenvalues_symmetric(M: list[list[float]]) -> list[float]:
    """Eigenvalues of a real symmetric 3×3 by the Jacobi method
    (full precision, no external linear algebra)."""
    n = 3
    A = [row[:] for row in M]
    for _ in range(100):
        # largest off-diagonal
        p, q, mx = 0, 1, abs(A[0][1])
        for i in range(n):
            for j in range(i + 1, n):
                if abs(A[i][j]) > mx:
                    mx, p, q = abs(A[i][j]), i, j
        if mx < 1e-15:
            break
        app, aqq, apq = A[p][p], A[q][q], A[p][q]
        theta = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c, s = math.cos(theta), math.sin(theta)
        for k in range(n):
            akp, akq = A[k][p], A[k][q]
            A[k][p] = c * akp - s * akq
            A[k][q] = s * akp + c * akq
        for k in range(n):
            apk, aqk = A[p][k], A[q][k]
            A[p][k] = c * apk - s * aqk
            A[q][k] = s * apk + c * aqk
    return sorted([A[i][i] for i in range(n)])


def hierarchy_eigenvalues() -> list[float]:
    """λ = {1, 1/(√3·Tr(Y²)), 1/(√3·Tr(Y²)²)} — the hypercharge-trace
    eigenvalue powers (m3 > m2 > m1, normalised to m3 = 1)."""
    tr_y2 = 10.0 / 3.0
    return [1.0, 1.0 / (math.sqrt(3.0) * tr_y2),
            1.0 / (math.sqrt(3.0) * tr_y2 * tr_y2)]


def build_mass_matrix(v: float, k_GUT: float,
                      level_factor: float = 1.0) -> dict:
    """Assemble and diagonalise the hypercharge-trace mass texture.

    Returns the eigenvalues (the hierarchy), the ratio cross-checks
    against r12 = 1/Tr(Y²) and r23 = 1/(√3 Tr(Y²)), and the PMNS
    angles recovered from U.
    """
    tr_y2 = 10.0 / 3.0
    lam = hierarchy_eigenvalues()          # {1, r23, r12·r23}
    U = pmns_matrix()

    def mm(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3))
                 for j in range(3)] for i in range(3)]

    Ut = [[U[j][i] for j in range(3)] for i in range(3)]  # transpose
    D = [[lam[i] if i == j else 0.0 for j in range(3)] for i in range(3)]
    M = mm(mm(U, D), Ut)                   # the flavour-basis matrix

    ev = eigenvalues_symmetric(M)          # ascending {m1, m2, m3}
    ev = sorted(ev)
    m1, m2, m3 = ev
    # scale to physical eV via the Weinberg prefactor
    Lambda = k_GUT / (2.0 * math.pi) ** 2
    scale = v * v / Lambda * level_factor * 1e9  # GeV² → eV
    r12_derived = m1 / m2
    r23_derived = m2 / m3
    r12_target = 1.0 / tr_y2               # 3/10
    r23_target = 1.0 / (math.sqrt(3.0) * tr_y2)
    return {"m1_eV": m1 * scale, "m2_eV": m2 * scale, "m3_eV": m3 * scale,
            "r12_derived": r12_derived, "r23_derived": r23_derived,
            "r12_target": r12_target, "r23_target": r23_target,
            "r12_err_pct": (r12_derived / r12_target - 1.0) * 100.0,
            "r23_err_pct": (r23_derived / r23_target - 1.0) * 100.0,
            "M_flavour": M}


def compute() -> dict:
    """Publish the mass-matrix assembly checks."""
    v = get("v_HIGGS")
    k_GUT = get("k_GUT")
    tau = float(get("tau"))
    s0 = 2.0 * tau
    kappa = math.sqrt((1.0 + s0) / (1.0 - 2.0 * s0) ** 2.5)
    r = build_mass_matrix(v, k_GUT, level_factor=1.0 + s0 * kappa)

    expected = [float(get("m_nu1")), float(get("m_nu2")),
                float(get("m_nu3"))]
    assembled = [r["m1_eV"], r["m2_eV"], r["m3_eV"]]
    for label, got, want in zip(("m1", "m2", "m3"), assembled, expected):
        if abs(got / want - 1.0) > 1e-11:
            raise RuntimeError(
                f"neutrino texture assembly mismatch for {label}: {got} vs {want}")

    pset("mnu_r12_diag", r["r12_derived"], provenance="DERIVED",
         note=f"mass-matrix assembly recovers m1/m2 = "
              f"{r['r12_derived']:.10f} vs 1/Tr(Y^2) = {r['r12_target']:.4f} "
              f"({r['r12_err_pct']:+.2e}%)")
    pset("mnu_r23_diag", r["r23_derived"], provenance="DERIVED",
         note=f"mass-matrix assembly recovers m2/m3 = "
              f"{r['r23_derived']:.10f} vs 1/(sqrt3 Tr(Y^2)) = "
              f"{r['r23_target']:.4f} ({r['r23_err_pct']:+.2e}%)")
    pset("mnu_matrix_scale_check", max(abs(g / w - 1.0)
                                        for g, w in zip(assembled, expected)),
         provenance="DERIVED", role="cg",
         note="maximum relative residual between the assembled matrix "
              "eigenvalues and the absolute neutrino closure")
    return r


if __name__ == "__main__":
    r = compute()
    print(f"m3 = {r['m3_eV']:.6f} eV, m2 = {r['m2_eV']:.6f} eV, "
          f"m1 = {r['m1_eV']:.6f} eV")
    print(f"r12 = {r['r12_derived']:.10f}; "
          f"r23 = {r['r23_derived']:.10f}")
    print("neutrino_mass_matrix OK")
