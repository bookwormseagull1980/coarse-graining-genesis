# =============================================================================
# Coarse-Graining Genesis Framework V5.0
# Author: Jinku Guo <guojk@nwpu.edu.cn>
# Northwestern Polytechnical University, Xi'an 710072, China
# ORCID: 0009-0000-6600-6171
# References:
# DOI: 10.2139/ssrn.7421398  A Spectral Construction of Natural-Number Arithmetic
# DOI: 10.5281/zenodo.22067118  The Spectrum of a Compact Internal Space I: Gauge Structure and a Scalar Mass Gap
# DOI: 10.5281/zenodo.22067469  The Spectrum of a Compact Internal Space II: Effective Couplings and Mass Scales
# DOI: 10.48550/arXiv.2607.21621  A Spectral Criterion for Emergent Gravity
# DOI: 10.48550/arXiv.2608.01989  Coarse-Graining and Long-Range Response in Generated Systems
# DOI: 10.5281/zenodo.22512592  The Spectrum of a Compact Internal Space III: Finite-Window Dynamics of Cosmic Structure Formation
# Full bibliography: REFERENCES.md and CITATION.cff.
# =============================================================================

"""Exact second/fourth sphere moments for the Guo (2026g) compact source.

Two independent uniform directions on S2 give Q=uu^T-I/3 in each
traceless symmetric space. This is an angular probability calculation,
not the high-frequency tensor catalogue weight.
"""
from fractions import Fraction as F


def second(i, j):
    return F(int(i == j), 3)


def fourth(i, j, k, l):
    return F(int(i == j and k == l) + int(i == k and j == l)
             + int(i == l and j == k), 15)


def covariance(A, B):
    """Exact Cov(u^T A u,u^T B u) for rational symmetric A,B."""
    mean_a = sum(F(A[i][i], 3) for i in range(3))
    mean_b = sum(F(B[i][i], 3) for i in range(3))
    return sum(F(A[i][j]) * F(B[k][l]) * fourth(i, j, k, l)
               for i in range(3) for j in range(3)
               for k in range(3) for l in range(3)) - mean_a * mean_b


def certificate():
    # Orthogonal rational basis; normalize via its exact squared norms,
    # avoiding floating square roots while testing the orthonormal claim.
    basis = [((1, 0, 0), (0, -1, 0), (0, 0, 0)),
             ((1, 0, 0), (0, 1, 0), (0, 0, -2)),
             ((0, 1, 0), (1, 0, 0), (0, 0, 0)),
             ((0, 0, 1), (0, 0, 0), (1, 0, 0)),
             ((0, 0, 0), (0, 0, 1), (0, 1, 0))]
    norms = [sum(F(x*x) for row in A for x in row) for A in basis]
    cov = [[covariance(A, B) for B in basis] for A in basis]
    verified = all(cov[i][j] == (F(2, 15)*norms[i] if i == j else 0)
                   for i in range(5) for j in range(5))
    trace = 2 * sum(cov[i][i]/norms[i] for i in range(5))
    return {"exact": verified and trace == F(4, 3),
            "single_block_eigenvalue": str(F(2, 15)),
            "independent_cross_block": "0", "two_block_trace": str(trace),
            "mean_source": "0", "equal_occupation_source_norm_squared": "0",
            "fixed_product_occupation_norm_squared": "4/3",
            "assumptions": "independent uniform S2 factors on product pure orbit"}
