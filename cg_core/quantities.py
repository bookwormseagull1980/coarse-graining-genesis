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

"""Definitions attached to matched quantities, independent of their provenance.

These contracts prevent accidental use of a different carrier, source,
projection, unit, scale or scheme. They do not prove a physical matching.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class QuantityDefinition:
    object: str
    unit: str
    carrier: str
    operator: str
    source: str
    projection: str
    normalization: str
    scheme: str
    order: str
    scale_GeV: float | None = None
    assumptions: tuple[str, ...] = ()
    error_kind: str = "not assigned"

    def __post_init__(self):
        for key in ("object", "unit", "carrier", "operator", "source",
                    "projection", "normalization", "scheme", "order", "error_kind"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key).strip():
                raise ValueError(f"quantity definition requires {key}")
        if self.scale_GeV is not None and (
                not math.isfinite(self.scale_GeV) or self.scale_GeV <= 0):
            raise ValueError("matching scale must be positive GeV or explicitly absent")
        if not all(isinstance(x, str) and x.strip() for x in self.assumptions):
            raise ValueError("assumptions must be nonempty statements")

    def as_record(self):
        return asdict(self)

    def require_same_definition(self, other):
        """Identity check, not a substitute for a computed transfer map."""
        if not isinstance(other, QuantityDefinition):
            raise TypeError("a second quantity definition is required")
        differences = [k for k, v in asdict(self).items() if v != asdict(other)[k]]
        if differences:
            raise ValueError("explicit matching required for: " + ", ".join(differences))


def readout_definition(key):
    """Physical contracts for fixed, named production readouts.

    Scheme names describe the calculation actually performed. A missing
    renormalization scale is explicit for algebraic endpoint observables.
    Unlisted diagnostic bundles retain their own structured payloads; callers
    can supply a more specific QuantityDefinition at publication.
    """
    groups = (
        ({
            "G_N_PDG": ("Newton constant used as the dimensional anchor", "GeV^-2",
                        "declared observed Newton constant in natural units"),
            "M_P": ("reduced Planck mass", "GeV", "1/sqrt(8 pi G_N_PDG)"),
        }, "macroscopic gravitational normalization", "declared Newton anchor",
         "natural units with reduced Planck convention", "dimensional normalization",
         ("the anchor is an external measurement",)),
        ({
            "tau": ("complete-carrier gauge-conditioned response modulus", "1",
                    "Tr(P chi)/(Tr(P) Tr(Y^2))=1/50 on the complete 16D carrier; P=support(Y)"),
            "L_Cg": ("Gaussian dimensionless endpoint length", "1", "sqrt(pi)"),
            "k_GUT": ("internal isometry-breaking scale", "GeV",
                      "M_P sqrt(pi) tau/sqrt(3)"),
            "kL_CMB": ("specified primordial response-window coordinate", "1", "kL (1-tau/4)"),
            "n_generations": ("screening-selected and window-checked family count", "1",
                              "g=N_c=3, checked against retained even modes at kL"),
        }, "fixed compact content and Gaussian response window",
         "finite-source chiral and hypercharge responses and the endpoint",
         "declared compact normalization", "finite content and endpoint readout",
         ("kL uses the R=5 response", "the family count includes joint screening compatibility")),
        ({
            "ec_action_torsion_coeffs": (
                "production quadratic torsion coefficients", "GeV^3",
                "a=M_G^3/4, b=4a, c=-(a+b/3); three independent SO(3) invariants"),
            "ec_torsion_sector_contract": (
                "algebraic torsion sectors and downstream spectral response", "dimensionless M_G units",
                "H=(2(2a-2b),2(2a+b+2c),2(2a+b)); "
                "minimal spin vertex=-(tr B) I/4; retained shifts at tau and L=kL"),
        }, "metric-compatible internal torsion, decomposed as 1+3+5",
         "production EC coefficients and minimal internal spin coupling",
         "T_abc=epsilon_dbc B_ad; independent scalar tau/L on the isotropic ray",
         "classical derivative-free quadratic torsion variation",
         ("rotation fixes the invariant direction, not the three coefficients",
          "nonzero transverse Hessians eliminate unsourced trace-free sectors",
          "gauge-conditioned tau and stationary spin-current amplitude are distinct calculations")),
        ({
            "gauge_kinetic_scale_factor": (
                "Killing-response scale normalization prescription", "1",
                "(M_G/M_P)^2; a registered scale convention, not a zero-mode integral"),
            "g2_MG_geo": ("bare weak Killing-response coupling", "1",
                "sqrt(8 gauge_kinetic_scale_factor/kL^3)"),
            "g2_MG_bare_constraint": ("bare weak endpoint coupling", "1",
                "sqrt(8 gauge_kinetic_scale_factor/kL^3) at the TT endpoint"),
            "g2_MG": ("screened weak matching coupling", "1",
                "sqrt(4 pi/[4 pi/g2_MG_geo^2+1/3-tau^2 pi/2])"),
        }, "common connection in the RP3 Killing-response convention",
         "registered normalization, finite-response endpoint and content screening",
         "fixed Killing norm 2 pi^2 kL^3 and numerator 16 pi^2",
         "algebraic boundary matching before gauge running",
         ("gauge_kinetic_scale_factor is a SCALE_CHOICE prescription",
          "its seven-dimensional action matching is evaluated separately")),
        ({
            "alpha_up": ("up-sector spectral transfer exponent", "1", "kL-2 tau"),
            "alpha_down": ("down-sector spectral transfer exponent", "1", "alpha_up-18 Delta/17"),
            "alpha_lepton": ("lepton-sector spectral transfer exponent", "1", "alpha_up-2 Delta"),
            "sector_alpha_delta": ("mean sector transfer step", "1", "Delta=6 ns_tilt kL_CMB"),
            "sector_alpha_s_lep": ("leptonic share of the transfer step", "1", "16 Delta/17"),
            "ladder_98_identity": ("down-to-lepton step ratio", "1", "1/[1-(Y_d/Y_l)^2]=9/8"),
            "alpha_sd": ("first down-sector transfer exponent", "1", "alpha_down-kL_CMB/6"),
            "m_t_over_m_c": ("top-to-charm mass-readout ratio", "1", "exp(2 alpha_up)"),
            "m_b_over_m_s": ("bottom-to-strange mass-readout ratio", "1", "exp(2 alpha_down)"),
            "m_t_over_m_u": ("top-to-up mass-readout ratio", "1", "4 exp(2 alpha_up+2 kL_CMB)"),
            "m_s_over_m_d": ("strange-to-down mass-readout ratio", "1", "exp(2 alpha_down-kL_CMB/3)"),
            "m_mu_over_m_e": ("muon-to-electron mass-readout ratio", "1", "exp(2 alpha_lepton+sqrt(2 pi))"),
        }, "three retained flavour sectors", "content exponents and fixed window transport",
         "native spectral mass readout", "finite exponential transfer",
         ("ratios use the declared common mass readout",)),
        ({
            "y_top_base": ("normalized elementary-connector pairing", "1", "unit finite pairing times angular singlets"),
            "y_b_over_y_t": ("bottom-to-top finite mass-vertex ratio", "1",
                             "exp[-2 alpha_down+ns_tilt (kL_CMB+2 tau)]"),
            "m_t_pred": ("top finite-seed mass readout", "GeV", "y_top_base v_HIGGS/sqrt(2)"),
            "m_b_pred": ("bottom finite-seed mass readout", "GeV", "(y_b/y_t) m_t"),
            "m_mu_pred": ("absolute muon mass readout", "GeV", "1e-3 m_e_pred (m_mu/m_e)"),
            "m_tau_pred": ("absolute tau mass readout", "GeV", "m_mu exp(2 alpha_lepton)"),
        }, "finite elementary connector and retained flavour modes",
         "window VEV, connector seed and flavour transfer",
         "specified mass-vertex readout", "tree mass relation with fixed finite seed",
         ("m_e_pred is stored in MeV", "pole matching is a separately specified calculation")),
        ({
            "lambda_dil": ("pseudo-dilaton strong-factor readout", "1", "3 (4 pi)"),
            "lambda_H_pseudo": ("Higgs constitutive quartic", "1", "3 (4 pi+1)/(32 pi^2)"),
            "pseudo_dilaton_beta_eff": ("algebraic pseudo-dilaton response coefficient", "1",
                                       "(3 g2_MG^2+g1_MG_geo^2+4 y_top_base^2+2 lambda_H+12 pi)/(16 pi^2)"),
            "m_H_pred": ("Higgs mass from the constitutive quartic", "GeV", "sqrt(2 lambda_H_pseudo) v_HIGGS"),
        }, "specified Higgs and pseudo-dilaton readout",
         "three-family content and geometric coupling boundary",
         "constitutive quartic and tree mass convention", "finite algebraic readout",
         ("the response coefficient is defined by its displayed formula",)),
        ({
            "M_Z_pred": ("self-consistent internal Z mass", "GeV",
                         "Q=v_HIGGS sqrt[g2(Q)^2+(3/5)g1(Q)^2]/2 at Q=M_Z"),
            "s2_thetaW_MZ": ("running-coupling weak mixing fraction", "1",
                             "(3/5)g1(M_Z)^2/[g2(M_Z)^2+(3/5)g1(M_Z)^2]"),
        }, "electroweak gauge fields", "geometric gauge boundary and window VEV",
         "GUT-normalized g1; internal self-consistent Z scale",
         "tree mass and mixing on the two-loop three-gauge flow",
         ("production running holds y0=1 fixed",)),
        ({
            "M_W_pred": ("W mass in the specified on-shell approximation", "GeV",
                         "Sirlin mass relation with Delta alpha and the one-loop t-b Delta rho"),
            "s2_thetaW_os": ("on-shell weak mixing fraction", "1", "1-M_W_pred^2/M_Z_pred^2"),
            "rho_param": ("resummed t-b rho factor", "1", "1/(1-Delta rho_tb)"),
        }, "electroweak gauge fields and the t-b doublet", "internal masses, VEV and electromagnetic couplings",
         "specified on-shell mass relation", "one-loop t-b rho with the stated resummation",
         ("Delta r retains Delta alpha and Delta rho terms",)),
        ({
            "Gamma_Z_pred": ("total Z width in the radiator approximation", "GeV", "Gamma_l+Gamma_inv+Gamma_had"),
            "Gamma_had_pred": ("hadronic Z width in the radiator approximation", "GeV", "sum of u,c,d,s,b partial widths"),
            "Gamma_b_pred": ("bottom Z width in the radiator approximation", "GeV", "Gamma(Z->bb) at Born level with QCD/QED radiators"),
            "Gamma_l_pred": ("sum of three charged-lepton Z widths", "GeV", "Gamma_e+Gamma_mu+Gamma_tau"),
            "Gamma_inv_pred": ("sum of three neutrino Z widths", "GeV", "3 Gamma_nu at Born level"),
            "sigma_had_pred": ("hadronic Z peak cross section", "nb", "12 pi Gamma_e Gamma_had/(M_Z^2 Gamma_Z^2), converted to nb"),
            "R_l_pred": ("hadronic-to-one-lepton Z width ratio", "1", "Gamma_had/Gamma_e"),
            "R_b_pred": ("bottom fraction of the hadronic Z width", "1", "Gamma_b/Gamma_had"),
        }, "kinematically accessible Standard Model fermions",
         "internal Z mass, running mixing fraction, Fermi coefficient and radiators",
         "massless-fermion Z widths at the internal Z scale",
         "Born with 1+alpha_s/pi+1.409(alpha_s/pi)^2 and 1+3 Q_f^2 alpha/(4 pi)",
         ("top channel closed", "total charged-lepton width sums three species",
          "R_l uses one charged-lepton species")),
        ({
            "delta_rho_2loop": ("leading-top improved rho correction", "1", "3 x [1+x (19-2 pi^2)], x=G_F m_t^2/(8 sqrt(2) pi^2)"),
            "deltab_top_vertex": ("nonuniversal leading-top relative bottom-width correction", "1",
                                  "2 x_t (g_Vb+g_Ab)/(g_Vb^2+g_Ab^2), at the common effective mixing angle"),
            "rho_NC_leading": ("common neutral-current normalization", "1", "1/(1-Delta rho_bar)"),
            "Gamma_b_pred_1loop": ("bottom width from the common effective neutral-current amplitude", "GeV",
                                  "3 G_F M_Z^3 rho_NC/(6 pi sqrt(2)) [g_Vb^2+g_Ab^2+2 x_t(g_Vb+g_Ab)] R_QCD R_QED"),
            "M_W_pred_lead1loop": ("leading-universal W mass readout", "GeV", "specified improved-Born on-shell root with Delta rho_bar"),
            "sin2_theta_eff_l_pred": ("leading-universal leptonic mixing fraction", "1",
                                     "s_LU^2+(1-s_LU^2) Delta rho_bar, s_LU^2=1-(M_W_pred_lead1loop/M_Z_pred)^2"),
            "sin2_theta_eff_b_pred": ("bottom effective mixing fraction through the nonuniversal heavy-top term", "1",
                                     "sin2_theta_eff_l_pred (1+2 x_t) through first order in x_t"),
        }, "electroweak leading-universal and heavy-top sector",
         "internal VEV, masses and common electromagnetic coupling alpha_Z",
         "G_F-normalized improved-Born effective neutral current",
         "resummed leading-universal rho with its retained two-loop term; nonuniversal heavy-top interference",
         ("G_F=1/(sqrt(2) v_HIGGS^2)",)),
        ({
            "Gamma_had_pred_lead1loop": (
                "hadronic Z width from the common neutral-current amplitude", "GeV",
                "sum of the u,c,d,s,b effective partial widths"),
            "Gamma_Z_pred_lead1loop": (
                "total Z width from the common neutral-current amplitude", "GeV",
                "Gamma_l_pred_lead1loop+Gamma_inv_pred_lead1loop+Gamma_had_pred_lead1loop"),
            "Gamma_l_pred_lead1loop": (
                "sum of three effective charged-lepton Z widths", "GeV", "Gamma_e+Gamma_mu+Gamma_tau"),
            "Gamma_inv_pred_lead1loop": (
                "sum of three effective neutrino Z widths", "GeV", "Gamma_nu_e+Gamma_nu_mu+Gamma_nu_tau"),
            "z_pole_partial_widths": (
                "individual and summed effective Z partial widths", "GeV per entry",
                "common s_eff^2 and rho_NC with heavy-top bottom interference and QCD/QED radiators"),
            "R_b_pred_lead1loop": (
                "bottom fraction from the common effective neutral-current amplitude", "1",
                "Gamma_b_pred_1loop/Gamma_had_pred_lead1loop"),
            "R_l_pred_lead1loop": (
                "hadronic-to-one-lepton ratio from the common effective neutral-current amplitude", "1",
                "Gamma_had_pred_lead1loop/(Gamma_l_pred_lead1loop/3)"),
            "sigma_had_pred_lead1loop": (
                "hadronic Z peak cross section from the common effective neutral-current amplitude", "nb",
                "12 pi (Gamma_l_pred_lead1loop/3) Gamma_had_pred_lead1loop/"
                "(M_Z_pred^2 Gamma_Z_pred_lead1loop^2) * 3.89379e5"),
        }, "kinematically accessible Standard Model fermions",
         "internal M_Z, G_F, alpha_Z, alpha_s and top mass in a common effective amplitude",
         "massless-fermion Z lineshape at the internal Z scale M_Z_pred",
         "leading-universal improved Born and first-order nonuniversal top interference; QCD/QED radiators",
         ("top channel closed", "Gamma_e=Gamma_l_pred_lead1loop/3",
          "all sums use the same effective partial widths",
          "ratios and peak cross section use the specified widths without re-expansion",
          "1 GeV^-2=3.89379e5 nb")),
        ({
            "m_nu3": ("heaviest static neutrino mass", "eV",
                      "1e9 v_HIGGS^2 (2 pi)^2 (1+2 tau kappa)/k_GUT"),
            "m_nu2": ("middle static neutrino mass", "eV", "m_nu3 sqrt(3)/10"),
            "m_nu1": ("lightest static neutrino mass", "eV", "m_nu3 3 sqrt(3)/100"),
            "mnu_ratio_12": ("static neutrino mass ratio m1/m2", "1", "3/10"),
            "mnu_ratio_23": ("static neutrino mass ratio m2/m3", "1", "sqrt(3)/10"),
            "Delta_m21_sq_raw": ("static solar-labelled squared-mass difference", "eV^2",
                                  "m_nu2^2-m_nu1^2"),
            "Delta_m31_sq": ("static atmospheric-labelled squared-mass difference", "eV^2",
                              "m_nu3^2-m_nu1^2"),
        }, "three labelled neutrino rest-mass eigenstates",
         "window VEV, emergence scale, squash response and hypercharge ratios",
         "specified Weinberg and mass-ladder readout", "static mass texture",
         ("v_HIGGS and k_GUT are in GeV; output masses are in eV",
          "kappa=sqrt((1+2 tau)/(1-4 tau)^(5/2))")),
        ({
            "m_nu2_osc": ("effective second propagation mass at unit source amplitude", "eV",
                          "m_nu2 (1+ns_tilt)"),
            "Delta_m21_sq_osc": ("solar-channel propagation squared-mass difference", "eV^2",
                                  "m_nu2^2 (1+ns_tilt)^2-m_nu1^2"),
        }, "three-flavour propagation with a scalar mass-projector source",
         "Delta H=zeta m2^2[(1+ns_tilt)^2-1] P2/(2 E)",
         "specified environmental propagation readout", "unit-amplitude source evaluation",
         ("zeta=1 for this comparison readout",
          "environmental coupling and spatial profile are supplied propagation data",
          "the cosmological thermal populations use the static mass texture")),
        ({
            "sin2_theta12": ("PMNS solar mixing sine squared", "1", "3/10"),
            "sin2_theta13": ("PMNS reactor mixing sine squared", "1", "sqrt(3)/(8 pi^2)"),
            "sin2_theta23": ("PMNS atmospheric mixing sine squared", "1", "1/2+2/(2 pi)^2"),
        }, "three-flavour lepton mixing with mass columns ordered (m1,m2,m3)",
         "specified hypercharge and angular mixing rules",
         "labelled PMNS texture", "finite angular readout",
         ("Majorana phases are separate from these angles",)),
        ({
            "rho_Lambda": ("endpoint vacuum energy density", "GeV^4",
                           "(2/3) (1e-9 m_nu1[eV])^4 (1-4 s0 kappa)"),
            "Lambda": ("endpoint cosmological constant", "GeV^2", "rho_Lambda/M_P^2"),
            "Omega_Lambda": ("endpoint vacuum fraction", "1", "rho_Lambda/(3 H0^2 M_P^2)"),
            "T_CMB_GeV": ("endpoint photon temperature", "GeV",
                          "(1e-9 m_nu1[eV]) (1-s0 kappa) (3/10)/pi (1-tau/2)"),
            "H0_GEV": ("endpoint Hubble rate", "GeV", "M_P sqrt(pi) exp(-S_endpoint)"),
            "sigma_C_hubble": ("endpoint Hubble length", "GeV^-1", "1/H0"),
            "a0_MOND": ("local response acceleration scale", "m s^-2",
                        "c H0 sqrt(4/3)/(2 pi), with H0 converted to s^-1"),
            "Omega_b": ("endpoint baryon fraction", "1",
                        "eta_B [2 zeta(3) T_raw^3/pi^2] m_p/(3 H0^2 M_P^2)"),
            "Omega_DM": ("endpoint nonbaryonic residual budget", "1", "1-Omega_Lambda-Omega_b"),
            "Omega_Sigma": ("endpoint nonbaryonic residual budget", "1", "1-Omega_Lambda-Omega_b"),
            "T_CMB_corrected_K": ("propagated photon monopole temperature", "K",
                                  "T_raw [GeV] * 1.160451812e13 * (1-tau/pi^2)"),
            "photon_zero_mode_Cgamma": ("photon temperature conversion factor", "1", "1-tau/pi^2"),
            "eta_B_photon_zero_mode_factor": ("baryon-to-photon conversion factor", "1",
                                              "(1-tau/pi^2)^(-3)"),
            "eta_B_propagation": ("baryon-to-photon ratio at the corrected photon temperature", "1",
                                   "eta_raw (1-tau/pi^2)^(-3)"),
        }, "homogeneous endpoint and prescribed local RMS response",
         "neutrino floor, endpoint entropy, baryon content and compact-source covariance",
         "specified endpoint transfer", "finite algebraic readout",
         ("R=5 response and supplied transfer rules", "M_P is the reduced Planck mass")),
        ({
            "gw_ratio": ("tensor-to-scalar power ratio at the reference pivot", "1", "(2 pi)^(-2)"),
            "gw_tensor_amplitude": ("dimensionless tensor power at the reference pivot", "1", "r A_s"),
            "perturbation_amplitude": ("dimensionless scalar curvature power at the reference pivot", "1",
                                       "exp[-2 pi kL (1-tau/4)] (1-tau kappa)/(8 pi^2)"),
            "ns_tilt": ("scalar spectral tilt deficit", "1", "1-n_s=7 tau/4"),
        }, "primordial scalar and two physical tensor helicities",
         "endpoint fluctuation readout", "dimensionless power at k=0.05 Mpc^-1",
         "specified primordial amplitudes and tilt", ("adiabatic propagation comparison",)),
        ({
            "bbn_hadronic_matching": (
                "common native nucleon mass and isovector source record", "GeV for masses; dimensionless coefficients",
                "m_p=(279/64) Lambda_QCD (1+5 tau kappa/3); "
                "Delta_np=C_ud (m_d-m_u)-Delta_EM; m_n=m_p+Delta_np"),
        }, "native constituent proton and scalar-isovector source",
         "generated up/down mass readouts, common QCD scale, torsion and zero-momentum electromagnetic coupling",
         "native spectral mass definition with its recorded QCD/EM separation",
         "finite constituent and isovector mass mapping",
         ("C_ud=1", "Delta_EM=(1-1/(2 pi)) alpha_em(0) Lambda_QCD is proton minus neutron",
          "M_G labels the generation reference of the spectral source",
          "renormalized nucleon matching uses sourced scalar matrix elements and quark masses in a common scheme and scale")),
        ({
            "bbn_GF": ("Fermi coupling from the supplied Higgs expectation", "GeV^-2", "1/(sqrt(2) v^2)"),
            "bbn_joint_response": ("joint neutron-proton, lifetime and helium logarithmic response", "mixed output units; dimensionless logarithmic derivatives",
                                   "analytic Jacobian of (Delta_np,tau_n,T_f,t_decay,Y_p) with common phase-space derivatives"),
            "bbn_dm_np": ("neutron-proton mass difference readout", "GeV",
                          "m_d-m_u-(1-1/(2 pi)) alpha_em Lambda_QCD"),
            "bbn_Tf": ("instantaneous weak freeze-out temperature", "GeV", "Gamma_weak(T_f)=H(T_f)"),
            "bbn_tau_n": ("free neutron lifetime readout", "s",
                          "hbar[GeV s] 2 pi^3/[G_F^2 |V_ud|^2 (1+3 g_A^2) m_e[GeV]^5 f delta_R]"),
            "bbn_t_decay": ("radiation-era interval to the capture temperature", "s", "t(T_BBN)-t(T_f)"),
            "bbn_Yp": ("helium-4 baryon fraction under complete neutron capture", "1",
                       "2 X_f exp(-t_decay/tau_n), X_f=1/[1+exp(Delta_np/T_f)]"),
            "bbn_Neff": ("effective radiation species count readout", "1", "3+sqrt(3)/(2 pi)^2"),
            "alpha_em_0_pred": ("zero-momentum electromagnetic coupling readout", "1",
                                "one-loop fermion vacuum polarization from internal alpha_em(M_Z)"),
        }, "homogeneous neutron-proton-photon-lepton plasma",
         "internal masses, weak coupling and prescribed hadronic matrix elements",
         "instantaneous freeze-out and capture with Coulomb phase space",
         "leading weak rate and supplied common radiative multiplier",
         ("g_A=4/pi", "scalar-isovector coefficient one", "delta_R=1+(1-tau)/(8 pi)",
          "light-quark vacuum-polarization masses frozen at Lambda_QCD")),
        ({
            "generated_ym_mass_gap": (
                "generated Yang--Mills operator and mass-gap certificate",
                "dimensionless squared spectrum; GeV for the transported gap",
                "Delta_YM^2=min{m_rad^2, inf_l m_perp,l^2}, with the unique "
                "positive conformal response and positive odd coclosed tower"),
            "generated_ym_gap_mass": (
                "generated Yang--Mills mass gap in the emergence mass unit", "GeV",
                "M_G sqrt(Delta_YM^2)"),
            "qcd_Lambda_QCD": ("five-flavour QCD scale from the specified extraction", "GeV",
                               "two-loop Lambda_MSbar(alpha_s, internal M_Z, nf=5)"),
            "m_p": ("constituent proton mass readout", "GeV", "(279/64) Lambda_QCD (1+5 tau kappa/3)"),
            "m_glueball": ("lowest scalar mass in the specified catalogue", "GeV", "8 Lambda_QCD"),
            "qcd_deconfinement_T": ("deconfinement temperature readout", "MeV",
                                   "1000 (4/3) Lambda_QCD (1-tau kappa)"),
            "qcd_string_tension": ("string-tension readout", "GeV^2", "(14/pi) Lambda_QCD^2"),
        }, "colour-sector effective readouts",
         "common-origin gauge boundary and internal spectral catalogue",
         "five-flavour MSbar scale extraction with prescribed hadronic maps",
         "two-loop fixed-y0 three-gauge running and finite content compensation",
         ("fixed y0=1 production flow", "declared hadronic coefficients",)),
        ({
            "endpoint_z_eq": ("CAMB matter-radiation equality redshift", "1", "z_eq"),
            "endpoint_r_drag_Mpc": ("CAMB sound horizon at the baryon drag epoch", "Mpc", "r_drag"),
            "endpoint_theta100_star": ("CAMB recombination angular scale times 100", "1", "100 theta_star"),
            "endpoint_sigma8": ("linear total-matter rms in an 8 h^-1 Mpc sphere", "1", "sigma8(z=0)"),
            "endpoint_S8": ("density-weighted linear fluctuation amplitude", "1",
                            "sigma8 sqrt(Omega_m_including_massive_neutrinos/0.3)"),
            "endpoint_tensor_nt": ("tensor spectral index in the propagation comparison", "1",
                                   "-r/8 (2-n_s-r/8)"),
            "endpoint_tensor_ntrun": ("running tensor index in the propagation comparison", "1",
                                      "r/8 (r/8+n_s-1)"),
            "Omega_Sigma_cold": ("cold-source fraction in the common-action propagation", "1",
                                  "1-Omega_Lambda-Omega_b-Omega_photon-Omega_neutrino-Omega_nu"),
        }, "homogeneous thermal evolution and linear Einstein-Boltzmann propagation",
         "input-bound completed CAMB configuration",
         "flat propagation preserving the endpoint vacuum, Hubble rate and baryon density",
         "background evolution; linear perturbations when requested",
         ("radiation and three massive neutrino eigenstates included",
          "tensor tilt uses the stated second-order inflation consistency prescription",
          "reionization optical depth is a declared propagation input")),
    )
    for rows, carrier, source, scheme, order, assumptions in groups:
        if key in rows:
            obj, unit, operator = rows[key]
            return QuantityDefinition(
                object=obj, unit=unit, carrier=carrier, operator=operator,
                source=source, projection="named production readout",
                normalization="as given by the operator formula and stated units",
                scheme=scheme, order=order, assumptions=assumptions,
                error_kind=("observed central value; anchor uncertainty not stored"
                            if key == "G_N_PDG" else
                            "anchor-derived central value; anchor uncertainty not propagated"
                            if key == "M_P" else
                            "computed centre; numerical and model errors assessed separately"))
    return None

