# -*- coding: utf-8 -*-
"""Endpoint-interval propagation contracts for the published V5 store."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from cg_core.params import get  # noqa: E402
from cg_core.endpoint_interval import response_derivative_interval, response_interval  # noqa: E402
from cg_core.rational_interval import Interval  # noqa: E402


def _interval(key: str) -> tuple[float, float]:
    record = get(key)
    return float(record["lo"]), float(record["hi"])


def test_endpoint_interval_is_narrow_and_contains_centre():
    lo, hi = _interval("kL_interval")
    centre = float(get("kL"))
    assert lo < centre < hi
    assert hi - lo < 5e-5


def test_mass_intervals_contain_production_centres():
    checks = (
        ("M_G_interval", "M_G"),
        ("m_e_interval", "m_e_pred"),
        ("v_HIGGS_interval", "v_HIGGS"),
    )
    for interval_key, centre_key in checks:
        lo, hi = _interval(interval_key)
        centre = float(get(centre_key))
        assert lo < centre < hi, (interval_key, centre_key, lo, centre, hi)


def test_moving_frequency_boundary_derivative_against_independent_quadrature():
    """Differentiate the full variable-domain integral, including its edge."""
    import math
    from scipy.integrate import quad

    tau2 = (1 / 50) ** 2
    rows = ((0, 3 / 4, 4), (8, 3 / 4, 36),
            (4, 3 / 2 + tau2 / 6, 192),
            (4, 1 + tau2 / 6, 72), (4, tau2 / 6, 24),
            (9 / 4, 3 * tau2 / 8, 168),
            (49 / 4, 3 * tau2 / 8, 1008),
            (25 / 4, 3 * tau2 / 8, 576))

    def response(c):
        cutoff = math.pi / c ** 2
        total = 0.0
        for a, b, weight in rows:
            lam, shift = a / c ** 2, b / c ** 2
            edge = math.sqrt(5 * cutoff - lam)
            total += weight * quad(
                lambda omega: ((omega ** 2 + lam) /
                               (omega ** 2 + lam + shift)) ** 2 *
                math.exp(-(omega ** 2 + lam) / cutoff),
                0, edge, epsabs=1e-12, epsrel=1e-12)[0]
        return total / (32 * math.pi ** 3)

    c, step = 2.4935343325226915, 1e-4
    derivative = (response(c + step) - response(c - step)) / (2 * step)
    lo, hi = map(float, response_derivative_interval(
        Interval.point(c), cells=64).decimal_bounds())
    assert lo <= derivative <= hi
    assert hi < 0
    lo, hi = map(float, response_interval(c, cells=64).decimal_bounds())
    assert lo <= response(c) <= hi


def test_endpoint_certificate_root_and_derivative_share_one_coefficient():
    import json
    from fractions import Fraction

    certificate = json.loads((_ROOT / "certificates" /
                             "endpoint_interval.json").read_text(encoding="utf-8"))
    assert certificate["status"] == "PASS"
    a_lo, a_hi = map(Fraction, certificate["coefficient"])
    c_lo, c_hi = map(Fraction, certificate["bracket"])
    assert 0 < c_lo < 27 * a_lo / 4 <= 27 * a_hi / 4 < c_hi
    d_lo, d_hi = map(Fraction, certificate["uniqueness"]["derivative"])
    assert d_lo <= -a_hi / c_lo ** 2 <= -a_lo / c_hi ** 2 <= d_hi < 0
