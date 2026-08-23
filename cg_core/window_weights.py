# -*- coding: utf-8 -*-
# =============================================================================
#  Coarse-Graining Genesis Framework V4.0
#
#  Author:      Jinku Guo guojk@nwpu.edu.cn
#  Affiliation: Northwestern Polytechnical University, Xi'an 710072, China
#
#  Part of the V4 spectral framework, whose physics is presented in the
#  companion papers:
#    [I]  "The spectrum of a compact internal space.
#          I. Gauge structure and fermion content"
#    [II] "The spectrum of a compact internal space.
#          II. Effective couplings and mass scales"
# =============================================================================

"""Window-weight identities used by the V4 spectral chain.

The ratio that appears in the scalar tilt and in the R2 relaxion
revision is not an observational input.  Its primary source is the
RP3 Weyl-law degree-of-freedom count:

    total Weyl d.o.f. = scalar + vector + spinor + TT
                      = 1 + 2 + 1 + 3
                      = 7.

The denominator is the four-level window/cascade normalisation
d + 1 = 4 in the three-dimensional internal space.  Hence

    spectral window-weight ratio = 7 / 4.

The conformal-curvature expression 1 + xi R_LC L^2 = 1 + (1/8)*6
is kept below as an internal cross-check of the same rational value,
not as the only source of the numerator.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from cg_core.ec_structure import scalar_curvature_LC
from cg_core.rp3_spectrum import weyl_dof


def conformal_coupling(d: int = 3) -> float:
    """Yamabe conformal coupling xi = (d-2)/(4(d-1))."""

    if d <= 1:
        raise ValueError("dimension must be greater than one")
    return (d - 2.0) / (4.0 * (d - 1.0))


def scalar_conformal_window_shift(d: int = 3) -> float:
    """Dimensionless scalar curvature shift xi R_LC L^2.

    For the V4 internal space d=3 and L=1, R_LC L^2 = 6 and
    xi = 1/8, hence the scalar shift is 3/4.
    """

    if d != 3:
        raise ValueError("V4 currently uses the three-dimensional RP3 internal space")
    L = 1.0
    return conformal_coupling(d) * scalar_curvature_LC(L) * L * L


def total_weyl_dof() -> int:
    """Total RP3 Weyl-law d.o.f.: 1 + 2 + 1 + 3 = 7."""

    return sum(weyl_dof().values())


def window_cascade_levels(d: int = 3) -> int:
    """The d+1 window/cascade normalisation; for RP3, d+1 = 4."""

    if d != 3:
        raise ValueError("V4 currently uses the three-dimensional RP3 internal space")
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
