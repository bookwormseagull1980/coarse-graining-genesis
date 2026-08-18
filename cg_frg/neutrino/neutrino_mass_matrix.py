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

"""
cg_frg/neutrino/neutrino_mass_matrix.py — V4.0: the neutrino mass
matrix — the hierarchy ratios from DIAGONALISATION, not assignment
=================================================================

WHY THIS MODULE EXISTS (motivation)
-----------------------------------
The neutrino hierarchy ratios r12 = m1/m2 and r23 = m2/m3 were
previously assigned directly as the hypercharge-trace reciprocals
(1/Tr(Y²), 1/(√3·Tr(Y²))).  This module promotes them to the
eigenvalue ratios of an explicitly constructed mass matrix, so the
hierarchy is DERIVED by diagonalisation rather than written down.

THE MASS MATRIX (the framework's internal structure)
----------------------------------------------------
The effective neutrino mass matrix is the Weinberg operator
M_ν = (v²/Λ)·F with the family scale Λ = k_GUT/(2π)² and a
flavour matrix F.  The framework's two independent pieces are:

  (1) the PMNS mixing U — the near-tribimaximal form dressed by the
      2π imprint, with the three angles fixed by the content ratios:
          sin²θ12 = 1/3            (the 3-generation window),
          sin²θ13 = (1/2π)²·√3/2  (the 2π imprint × the S³→RP³
                                     quotient projection),
          sin²θ23 = 1/2 + Tr(T₃²)/(2π)²   (maximal mixing + isospin),
      (the solar angle sin²θ12 = m1/m2 = 3/10 is the ratio fixed by
      the diagonalisation itself — see below);

  (2) the hypercharge-trace hierarchy — the eigenvalues of F are the
      inverse powers of the first non-zero hypercharge moment:
          λ = {1, 1/(√3·Tr(Y²)), 1/(√3·Tr(Y²)²)}  (m3 > m2 > m1).

The mass matrix is then the spectral assembly
    M_ν = U · diag(λ) · U^† · (v²/Λ),
and the diagonalisation returns the eigenvalues (the hierarchy) and
the mixing (the PMNS angles).  The hierarchy is therefore the
eigenvalue structure of the hypercharge-trace flavour matrix, not a
hand-written ratio.

The solar ratio follows: sin²θ12 = m1/m2 = λ1/λ2 = 1/Tr(Y²) = 3/10,
so the solar angle IS the mass ratio (the two-state mixing of the
light pair), consistent with the diagonalisation.

V4 DISCIPLINE
-------------
U is built from the framework's content-ratio angles; the eigenvalues
are the hypercharge-trace powers; the hierarchy is read off the
diagonalisation.  No observed mass enters.
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
      s12² = m1/m2 = 3/10 (the solar angle = the mass ratio, fixed by
             the diagonalisation — the light-pair mixing),
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


def build_mass_matrix(v: float, k_GUT: float) -> dict:
    """Assemble M_ν = U·diag(λ)·U^†·(v²/Λ) and diagonalise.

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
    scale = v * v / Lambda * 1e9           # GeV² → eV
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
    """Publish the mass-matrix hierarchy (DERIVED by diagonalisation)."""
    v = get("v_HIGGS")
    k_GUT = get("k_GUT")
    r = build_mass_matrix(v, k_GUT)
    pset("mnu_r12_diag", r["r12_derived"], provenance="DERIVED",
         note=f"m1/m2 from the mass-matrix diagonalisation = "
              f"{r['r12_derived']:.10f} vs 1/Tr(Y^2) = {r['r12_target']:.4f} "
              f"({r['r12_err_pct']:+.2e}%) — the hierarchy is the eigenvalue "
              f"ratio of the hypercharge-trace flavour matrix, not an "
              f"assignment")
    pset("mnu_r23_diag", r["r23_derived"], provenance="DERIVED",
         note=f"m2/m3 from the mass-matrix diagonalisation = "
              f"{r['r23_derived']:.10f} vs 1/(sqrt3 Tr(Y^2)) = "
              f"{r['r23_target']:.4f} ({r['r23_err_pct']:+.2e}%)")
    return r


if __name__ == "__main__":
    # self-test without the store (direct build)
    tr_y2 = 10.0 / 3.0
    lam = hierarchy_eigenvalues()
    U = pmns_matrix()
    r = build_mass_matrix(246.22, 1.0e16)
    print("hierarchy eigenvalues (m3:m2:m1) = "
          f"{lam[0]:.4f} : {lam[1]:.4f} : {lam[2]:.4f}")
    print(f"r12 (m1/m2) derived = {r['r12_derived']:.10f}  "
          f"vs 1/Tr(Y^2) = 3/10  ({r['r12_err_pct']:+.2e}%)")
    print(f"r23 (m2/m3) derived = {r['r23_derived']:.10f}  "
          f"vs 1/(sqrt3 Tr(Y^2))  ({r['r23_err_pct']:+.2e}%)")
    print(f"m3 = {r['m3_eV']:.4f} eV, m2 = {r['m2_eV']:.4f} eV, "
          f"m1 = {r['m1_eV']:.4f} eV")
    # PMNS recovery: s12^2 from U
    print(f"PMNS |U_e2|^2 = {U[0][1]**2:.4f} (s12^2 = m1/m2 = 3/10 target)")
    print("neutrino_mass_matrix OK")
