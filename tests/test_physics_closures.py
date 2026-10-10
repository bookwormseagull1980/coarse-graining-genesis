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

"""Declared-formula consistency and numerical regression of closed quantities.

Each test reads the run-time value from cg_params.json (the single
store), checks specified formula relations and keeps numerical regression
values. A saved central value is not an independent theorem or validation
against experiment. Observational residuals are reported separately and do
not determine whether the implementation correctly evaluates its formulas.
"""
import math

import pytest

from cg_core.params import get

# Regression values of the specified formulas at the common endpoint.
REGRESSION_VALUES = {
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
    ("v_HIGGS", 1e-3),
    ("m_e_pred", 1e-3),
    ("m_t_pred", 1e-2),
    ("m_nu3", 1e-2),              # Static mass formula at the specified endpoint.
    ("kL_CMB", 1e-6),
    ("Lambda", 1e-2),
    ("epsilon_L_over_R", 1e-2),
    ("g2_MG", 1e-4),
    ("perturbation_amplitude", 1e-2),
    ("ns_tilt", 1e-2),
])
def test_closed_quantity_regression(key, tol):
    """Stored central values agree with the declared regression tolerances."""
    if key not in REGRESSION_VALUES or REGRESSION_VALUES[key] is None:
        pytest.skip(f"{key}: expected value not set in this test")
    val = get(key)
    exp = REGRESSION_VALUES[key]
    rel = abs(val - exp) / abs(exp)
    assert rel < tol, f"{key}: stored {val} vs expected {exp} (rel {rel:.2e} > {tol})"


@pytest.mark.physics
def test_bbn_helium_abundance():
    """Verify conserved free decay and complete neutron capture."""
    yp = get("bbn_Yp")
    initial_fraction = 1/(1+math.exp(get("bbn_dm_np")/get("bbn_Tf")))
    final_fraction = initial_fraction*math.exp(-get("bbn_t_decay")/get("bbn_tau_n"))
    assert yp == pytest.approx(2*final_fraction, rel=2e-14)
    assert yp == pytest.approx(0.2460823786548142, rel=1e-10)


@pytest.mark.physics
def test_neutron_lifetime():
    """Independent adaptive quadrature checks the specified phase-space rule."""
    integrate = pytest.importorskip("scipy.integrate")
    me = get("m_e_pred")*1e-3
    W0 = get("bbn_dm_np")/me
    a = 2*math.pi*get("alpha_em_0_pred")
    def integrand(w):
        # Algebraically cancel the p in the Fermi factor before integrating.
        # This representation is finite at the electron threshold w=1.
        if w == 1:
            return a*(W0-1)**2
        p = math.sqrt((w-1)*(w+1))
        return a*w*w*(W0-w)**2 / (-math.expm1(-a*w/p))
    phase, _ = integrate.quad(integrand, 1., W0, epsabs=1e-13, epsrel=2e-13, limit=200)
    gf = 1/(math.sqrt(2)*get("v_HIGGS")**2)
    vud2 = 1-get("V_us_geo")**2  # retained omission of |Vub|²
    radiative = 1+(1-get("tau"))/(8*math.pi)
    expected = 2*math.pi**3/(gf**2*vud2*(1+3*(4/math.pi)**2)*me**5*phase*radiative)*6.582119569e-25
    tau_n = get("bbn_tau_n")
    assert tau_n == pytest.approx(expected, rel=3e-11)
    assert tau_n == pytest.approx(915.5435125710899, rel=1e-10)


@pytest.mark.physics
def test_bbn_freeze_out_equation_residual():
    tf, dm, gf = get("bbn_Tf"), get("bbn_dm_np"), get("bbn_GF")
    weak = (7*math.pi/60)*(1+3*(4/math.pi)**2)*gf**2*tf**5*(1+1.5*dm/tf)
    hubble = math.sqrt(4*math.pi**3*10.75/45)*tf**2/(math.sqrt(8*math.pi)*get("M_P"))
    assert weak == pytest.approx(hubble, rel=2e-14, abs=0.)


@pytest.mark.physics
def test_alpha_zero_declared_threshold_sum():
    """One-loop internal threshold prescription, with u/d/s frozen at Lambda."""
    v, mg = get("v_HIGGS"), get("M_G")
    length = math.log(mg/v)
    g1v = 1/math.sqrt(1/get("g1_MG_geo")**2+(41/10)/(8*math.pi**2)*length)
    g2v = 1/math.sqrt(1/get("g2_MG")**2+(-19/6)/(8*math.pi**2)*length)
    mz = v/2*math.sqrt(g2v**2+.6*g1v**2)
    me = get("m_e_pred")*1e-3
    mmu = me*get("m_mu_over_m_e")
    mtau = mmu*math.exp(2*get("alpha_lepton"))
    lam = get("qcd_Lambda_QCD")
    thresholds = [(1., me), (1., mmu), (1., mtau),
                  (4/3, lam), (4/3, get("m_t_pred")/get("m_t_over_m_c")),
                  (1/3, lam), (1/3, lam), (1/3, get("m_b_pred"))]
    inverse = get("alpha_inv_MZ_pred") + 2/(3*math.pi)*sum(q2n*math.log(mz/m) for q2n,m in thresholds)
    assert get("alpha_em_0_pred") == pytest.approx(1/inverse, rel=2e-14)


@pytest.mark.physics
def test_qcd_scale():
    lam = get("qcd_Lambda_QCD")
    assert 0.15 < lam < 0.30        # Regression range around 0.21 GeV.
    t_d = get("qcd_deconfinement_T")
    assert 250.0 < t_d < 300.0      # Regression range around 270 MeV.
    mg = get("m_glueball")
    assert 1.4 < mg < 2.0           # Regression range around 1.66 GeV.


@pytest.mark.physics
def test_entropy_integral():
    """int gamma_M d ln k = ln(kL*M_G/H0) ≈ 139.25 (the entropy identity)."""
    ent = get("entropy_integral")
    assert abs(ent - 139.2537061093592) / 139.2537061093592 < 1e-6


@pytest.mark.physics
def test_generation_count_closed():
    n = get("n_generations")
    assert n == 3                    # Joint source-screening and retained-window rule.


@pytest.mark.physics
def test_higgs_mass_tree():
    m_h = get("m_H_pred")
    assert abs(m_h - 124.98344026878286) / 124.98344026878286 < 1e-6


@pytest.mark.physics
def test_gw_tensor_ratio():
    r = get("gw_ratio")
    assert abs(r - 0.025330295910584444) / 0.025330295910584444 < 1e-6
