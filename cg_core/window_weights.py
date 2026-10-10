# -*- coding: utf-8 -*-
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

"""Window-weight identities used by the V5 spectral chain.

The ratio entering the scalar tilt and the R2 relaxion relation follows from the
RP3 response-catalogue Weyl count:

    total Weyl d.o.f. = scalar + vector + projected spinor + three-branch tensor
                      = 1 + 2 + 1 + 3
                      = 7.

The denominator is the four-level window/cascade normalisation
d + 1 = 4 in the three-dimensional internal space.  Hence

    spectral window-weight ratio = 7 / 4.

The conformal-curvature expression 1 + xi R_LC L^2 = 1 + (1/8)*6
provides an algebraic cross-check of the same rational value for the
tensor-response catalogue specified above. The separate rough-TT carrier
has Weyl weight 2. The present window readout uses 7/4.
"""

from __future__ import annotations

import sys
import math
from dataclasses import dataclass
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.ec_structure import scalar_curvature_LC
from cg_core.rp3_spectrum import weyl_dof


@dataclass(frozen=True)
class ResponseDomain:
    """Finite measurement domain q²<R Lambda², separate from heat evolution.

    ``fixed`` holds the reference spectral projection fixed under source
    differentiation. ``moving`` requires differentiating its boundary as
    well as the integrand. Neither convention selects a physical R.
    """
    radius: float = 5.0
    projection: str = "fixed"

    def __post_init__(self):
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("finite positive response-domain radius required")
        if self.projection not in ("fixed", "moving"):
            raise ValueError("projection must be fixed or moving")

    def edge(self, cutoff: float) -> float:
        if not math.isfinite(cutoff) or cutoff <= 0:
            raise ValueError("positive finite squared cutoff required")
        return self.radius * cutoff

    def frequency_edge(self, lam: float, cutoff: float) -> float:
        if not math.isfinite(lam) or lam < 0:
            raise ValueError("nonnegative finite reference eigenvalue required")
        return math.sqrt(max(0.0, self.edge(cutoff)-lam))

    def boundary_derivative(self, lam, cutoff, *, dlam=0.0, dcutoff=0.0,
                            dradius=0.0):
        """Derivative of the frequency edge away from a shell crossing.

        Multiply this by the integrand at the upper edge for the Leibniz
        boundary term. A shell exactly on the boundary has no ordinary
        differentiable edge; the caller must handle the crossing.
        """
        if self.projection == "fixed":
            return 0.0
        delta = self.edge(cutoff)-lam
        if delta == 0:
            raise ValueError("source derivative crosses a spectral boundary")
        if delta < 0:
            return 0.0
        return (self.radius*dcutoff+cutoff*dradius-dlam)/(2*math.sqrt(delta))


DEFAULT_RESPONSE_DOMAIN = ResponseDomain()


def conformal_coupling(d: int = 3) -> float:
    """Yamabe conformal coupling xi = (d-2)/(4(d-1))."""

    if d <= 1:
        raise ValueError("dimension must be greater than one")
    return (d - 2.0) / (4.0 * (d - 1.0))


def scalar_conformal_window_shift(d: int = 3) -> float:
    """Dimensionless scalar curvature shift xi R_LC L^2.

    For the V5 internal space d=3 and L=1, R_LC L^2 = 6 and
    xi = 1/8, hence the scalar shift is 3/4.
    """

    if d != 3:
        raise ValueError("V5 currently uses the three-dimensional RP3 internal space")
    L = 1.0
    return conformal_coupling(d) * scalar_curvature_LC(L) * L * L


def total_weyl_dof() -> int:
    """Response-catalogue Weyl weight: 1 + 2 + 1 + 3 = 7."""

    return sum(weyl_dof().values())


def window_cascade_levels(d: int = 3) -> int:
    """The d+1 window/cascade normalisation; for RP3, d+1 = 4."""

    if d != 3:
        raise ValueError("V5 currently uses the three-dimensional RP3 internal space")
    return d + 1


def conformal_curvature_ratio(d: int = 3) -> float:
    """Cross-check ratio 1 + xi R_LC L^2, equal to the Weyl ratio in d=3."""

    vector_unit_weight = 1.0
    return vector_unit_weight + scalar_conformal_window_shift(d)


def scalar_vector_window_ratio(d: int = 3) -> float:
    """Spectral window-weight ratio = total Weyl d.o.f. / (d+1) = 7/4."""

    return total_weyl_dof() / float(window_cascade_levels(d))


def _self_test() -> None:
    assert weyl_dof() == {"scalar": 1, "vector": 2, "spinor": 1, "tt": 3}
    assert total_weyl_dof() == 7
    assert window_cascade_levels() == 4
    assert abs(conformal_coupling() - 1.0 / 8.0) < 1e-15
    assert abs(scalar_conformal_window_shift() - 3.0 / 4.0) < 1e-15
    expected_ratio = total_weyl_dof() / float(window_cascade_levels())
    assert abs(scalar_vector_window_ratio() - expected_ratio) < 1e-15
    assert abs(scalar_vector_window_ratio() - conformal_curvature_ratio()) < 1e-15


if __name__ == "__main__":
    _self_test()
    print(f"weyl dof = {total_weyl_dof()}")
    print(f"window cascade levels = {window_cascade_levels()}")
    print(f"xi = {conformal_coupling():.12f}")
    print(f"xi R L^2 = {scalar_conformal_window_shift():.12f}")
    print(f"scalar/vector window ratio = {scalar_vector_window_ratio():.12f}")
    print("window_weights OK")
