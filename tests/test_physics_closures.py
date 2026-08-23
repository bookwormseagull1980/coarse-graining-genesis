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

"""Physics benchmark tests: the framework's closed quantities.

Each test reads the run-time value from cg_params.json (the single
store) and asserts it against the EXPECTED_BY_THEORY analytic value
within a tolerance set by the closure's intrinsic precision.  The
theoretical values are the framework's own closed forms (marker
`physics`), NOT observed inputs.
"""
import math

import pytest

from cg_core.params import get

# Expected closed values (EXPECTED_BY_THEORY — the framework's own
# first-principles results, V4.0 fixed point kL = 2.4935343).
EXPECTED = {
    "kL": 2.4935343325226915,          # F_MG fixed point (endpoint_constraint)
    "M_G": 1.7310765000475023e18,      # emergence scale (GeV)
    "v_HIGGS": 246.18969645238943,     # EW VEV (GeV)
    "m_e_pred": 0.5103542513564916,    # electron mass (MeV)
    "m_t_pred": 174.08240381974227,    # top mass (GeV)
    "m_nu3": 0.05017973302502751,      # heaviest neutrino (eV)
    "kL_CMB": 2.481066660860078,       # CMB-pivot window width
    "rho_Lambda": None,                # set below from Lambda
    "Lambda": 4.254718579276526e-84,   # cosmological constant (GeV^2)
    "qcd_Lambda_QCD": None,            # set below
    "qcd_deconfinement_T": None,       # set below (MeV)
    "m_glueball": None,                # set below
    "epsilon_L_over_R": 1.42218e-16,   # EW hierarchy ratio
    "g2_MG": 0.5088477031823814,       # SU(2) coupling at M_G
    "perturbation_amplitude": 2.10111e-09,
    "ns_tilt": 0.035,
}


@pytest.mark.physics
@pytest.mark.parametrize("key,tol", [
    ("kL", 1e-9),                 # exact self-consistency
    ("M_G", 1e-9),
    ("v_HIGGS", 1e-3),            # 246.19 vs 246.22 obs: -0.012%
    ("m_e_pred", 1e-3),           # 0.5104 vs 0.511 obs: -0.126%
    ("m_t_pred", 1e-2),           # 174.08 vs 172.69 obs: +0.81%
    ("m_nu3", 1e-2),              # 0.05018 vs 0.0502 obs: -0.04%
    ("kL_CMB", 1e-6),
    ("Lambda", 1e-2),             # -0.57% vs observed
    ("epsilon_L_over_R", 1e-2),   # -0.15% vs observed
    ("g2_MG", 1e-4),
    ("perturbation_amplitude", 1e-2),  # -0.19% vs observed
    ("ns_tilt", 1e-2),
])
def test_closed_quantity_matches_theory(key, tol):
    """The stored value must equal the EXPECTED_BY_THEORY value."""
    if key not in EXPECTED or EXPECTED[key] is None:
        pytest.skip(f"{key}: expected value not set in this test")
    val = get(key)
    exp = EXPECTED[key]
    rel = abs(val - exp) / abs(exp)
    assert rel < tol, f"{key}: stored {val} vs expected {exp} (rel {rel:.2e} > {tol})"


@pytest.mark.physics
def test_bbn_helium_abundance():
    """Y_p is the framework's own derived BBN abundance (~0.251)."""
    yp = get("bbn_Yp")
    assert abs(yp - 0.2513646481783959) / 0.2513646481783959 < 1e-9
    # Within 3% of the observed Y_p = 0.245 (EXPECTED_BY_THEORY band).
    assert abs(yp - 0.245) / 0.245 < 0.03


@pytest.mark.physics
def test_neutron_lifetime():
    tau_n = get("bbn_tau_n")
    assert abs(tau_n - 897.1456583613488) / 897.1456583613488 < 1e-9


@pytest.mark.physics
def test_qcd_scale():
    lam = get("qcd_Lambda_QCD")
    assert 0.15 < lam < 0.30        # EXPECTED_BY_THEORY: ~0.21 GeV
    t_d = get("qcd_deconfinement_T")
    assert 250.0 < t_d < 300.0      # EXPECTED_BY_THEORY: ~270 MeV
    mg = get("m_glueball")
    assert 1.4 < mg < 2.0           # EXPECTED_BY_THEORY: ~1.66 GeV


@pytest.mark.physics
def test_entropy_integral():
    """int gamma_M d ln k = ln(kL*M_G/H0) ≈ 139.25 (the entropy identity)."""
    ent = get("entropy_integral")
    assert abs(ent - 139.2537061093592) / 139.2537061093592 < 1e-6


@pytest.mark.physics
def test_generation_count_closed():
    n = get("n_generations")
    assert n == 3                    # EXPECTED_BY_THEORY (window_capacity)


@pytest.mark.physics
def test_higgs_mass_tree():
    m_h = get("m_H_pred")
    assert abs(m_h - 124.98344026878286) / 124.98344026878286 < 1e-6


@pytest.mark.physics
def test_gw_tensor_ratio():
    r = get("gw_ratio")
    assert abs(r - 0.025330295910584444) / 0.025330295910584444 < 1e-6
