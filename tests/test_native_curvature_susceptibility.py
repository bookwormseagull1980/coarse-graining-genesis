"""Joint-source Schur response and finite Gamma polynomial normalization."""
from copy import deepcopy
from fractions import Fraction as F
import math

import numpy as np
import pytest

from cg_core.native_colour_response import colour_source_response, intensity_expectation
from cg_frg.qcd.generated_yang_mills import generated_yang_mills_gap


def _multiply(p, q):
    out = [F(0)]*(len(p)+len(q)-1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            out[i+j] += x*y
    return out


@pytest.mark.parametrize("dimension", (1, 2, 120))
def test_gamma_second_polynomial_normalization_and_score_product(dimension):
    a = F(dimension, 2)
    p1 = [F(-1), F(1)]
    raw_p2 = [a*(a+1), -2*a*(a+1), a*a]
    expect = lambda p: intensity_expectation(p, dimension=dimension)
    assert expect(raw_p2) == 0
    assert expect(_multiply(p1, raw_p2)) == 0
    assert expect(_multiply(raw_p2, raw_p2)) == 2*a*(a+1)
    # s=sqrt(a)*(x-1), p2=raw_p2/sqrt(2*a*(a+1)).
    # This rational identity checks the nonzero p1 term before taking roots.
    square = [a*x for x in _multiply(p1, p1)]
    expansion = [F(1)+2*p1[0]+raw_p2[0]/a,
                 2*p1[1]+raw_p2[1]/a, raw_p2[2]/a]
    assert square == expansion
    assert a*a*expect(_multiply(_multiply(p1, p1), _multiply(p1, p1))) == 3+12/F(dimension)
    assert expect(_multiply(_multiply(p1, p1), p1)) == 8/F(dimension)**2


@pytest.mark.parametrize("radius", (1.9, 2.4935343325226915, 4.))
def test_static_response_from_covariance_and_joint_hessian(radius):
    gap = generated_yang_mills_gap(radius, certify=False)
    response = colour_source_response(gap)
    result = response["joint_static_susceptibility"]
    q, M = gap["intensity_q"], gap["source_dimension"]
    # Work with N/q to keep the covariance and Hessian well conditioned.
    v = 2/M
    lam = gap["long_root_eigenvalue"]
    alpha = gap["adjoint_casimir"]/(3*gap["volume"]*gap["algebra_dimension"])
    omega_q = q*(lam+2*alpha*q)
    cov = v*omega_q
    var_Q = response["curvature_variance"]
    residual = var_Q-cov*cov/v
    # Partial Legendre Hessian from the original two-source covariance.
    raw_hessian = np.array([[1/v, cov/v], [cov/v, -residual]])
    restoring = gap["potential_curvature"]*q*q
    continued_hessian = raw_hessian.copy()
    continued_hessian[0, 0] = restoring
    tangent = -continued_hessian[0, 1]/continued_hessian[0, 0]
    relaxed_source_curvature = (continued_hessian[1, 1]
                               +continued_hessian[1, 0]*tangent)
    assert result["total"] == pytest.approx(-relaxed_source_curvature, rel=5e-13)
    assert result["stationary_intensity_derivative_J"] == pytest.approx(q*tangent, rel=5e-13)
    assert result["collective"] == pytest.approx(gap["curvature_score_overlap"]**2/gap["radial_mass_squared"], rel=5e-13)
    assert result["direct"] == pytest.approx(residual, rel=5e-13)
    assert result["total"] > result["direct"] > 0
    assert result["stationary_intensity_derivative_J"] < 0
    assert result["radial_mass_squared"] != pytest.approx(response["intensity_correlation_rate"])


@pytest.mark.parametrize("key,value", (("potential_curvature", 0.),
                                      ("radial_mass_squared", math.nan),
                                      ("radial_mass_squared", -1.)))
def test_static_response_rejects_invalid_collective_hessian(key, value):
    gap = generated_yang_mills_gap(2.4935343325226915, certify=False)
    bad = deepcopy(gap)
    bad[key] = value
    with pytest.raises(ValueError, match="positive finite"):
        colour_source_response(bad)


def test_static_response_rejects_a_different_information_normalization():
    gap = generated_yang_mills_gap(2.4935343325226915, certify=False)
    gap["radial_mass_squared"] *= 2
    with pytest.raises(ValueError, match="information metric"):
        colour_source_response(gap)


def test_verification_report_keeps_static_response_and_composition_separate(monkeypatch):
    from scripts import verify_v5 as verifier
    gap = generated_yang_mills_gap(2.4935343325226915, certify=False)
    response = colour_source_response(gap)
    monkeypatch.setattr(verifier, "read_store_document", lambda *args, **kwargs: {
        "parameters": {"native_colour_source_response": {"value": response}}})
    monkeypatch.setattr(verifier, "store_summary", lambda: "")
    text = verifier.report_text([], ["Full production run"])
    assert "direct susceptibility" in text
    assert "collective susceptibility" in text
    assert "total static susceptibility" in text
    assert "fixed-source" in text
    # Historical stores without the supplement remain readable.
    del response["joint_static_susceptibility"]
    old_text = verifier.report_text([], ["Full production run"])
    assert "complete Hermite weights" in old_text
    assert "total static susceptibility" not in old_text
