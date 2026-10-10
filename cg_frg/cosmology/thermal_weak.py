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

"""Continuous n<->p rates and homogeneous thermal evolution.

The six phase-space channels use the static-nucleon Born approximation of
Pitrou et al., Phys. Rep. 754 (2018), Sec. III, arXiv:1801.08023, with an
optional point-Coulomb factor and one explicit common rate multiplier.
No experimental neutron lifetime normalizes the rates: G_F, V_ud, g_A,
mass splitting and masses are supplied inputs. Recoil, weak magnetism,
finite-temperature QED and transport neutrino heating are not implemented.
This is a controlled extension API, not a precision BBN abundance package.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math

import numpy as np
from scipy.integrate import quad, solve_ivp
from scipy.special import expit

HBAR_GEV_S = 6.582119569e-25  # unit conversion, not a fitted physical boundary


def _quadrature_with_work(function, low, high, **settings):
    """Return the integral, its error estimate and QUADPACK evaluation count.

    QUADPACK already records neval, so recording work requires no extra
    integration or wrapper at every integrand evaluation. Full output also
    supplies convergence diagnostics; an unconverged rate is not admitted
    into the thermal evolution.
    """
    result = quad(function, low, high, full_output=True, **settings)
    if len(result) != 3:
        raise ArithmeticError("thermal quadrature did not converge: " + str(result[3]))
    value, error, information = result
    return value, error, int(information["neval"])


@dataclass(frozen=True)
class WeakInputs:
    """All energies in GeV; G_F in GeV^-2; dimensionless remaining factors.

    source identifies the hadronic/electroweak input construction. It does
    not establish that a declared g_A or mass-splitting rule is derived.
    """
    G_F: float
    V_ud: float
    g_A: float
    electron_mass: float
    neutron_proton_split: float
    alpha_em: float
    rate_multiplier: float
    source: str

    def __post_init__(self):
        values = (self.G_F,self.V_ud,self.g_A,self.electron_mass,
                  self.neutron_proton_split,self.alpha_em,self.rate_multiplier)
        if not all(math.isfinite(x) for x in values):
            raise ValueError("finite weak inputs required")
        if min(self.G_F,self.electron_mass,self.neutron_proton_split,self.rate_multiplier)<=0:
            raise ValueError("positive weak scale, masses and rate multiplier required")
        if not 0 < self.V_ud <= 1 or self.alpha_em<0 or not self.source.strip():
            raise ValueError("0<V_ud<=1, alpha>=0 and an explicit input source required")


def _occupation(energy, temperature, chemical_potential=0.0):
    if temperature==0:
        return float(energy < chemical_potential)
    return float(expit((chemical_potential-energy)/temperature))


def _electron_phase(W, alpha):
    """F(1,W) W sqrt(W²-1), with a finite endpoint at W=1."""
    p = math.sqrt(max(0.0,W*W-1))
    if alpha==0:
        return W*p
    x = 2*math.pi*alpha
    return x*W*W/(-math.expm1(-x*W/p)) if p else x*W*W


def weak_rates(inputs, temperature, neutrino_temperature=None, *,
               electron_chemical_potential=0.0, neutrino_chemical_potential=0.0,
               rtol=2e-8, atol=2e-11):
    """Independently integrate forward and inverse channels; return rates s^-1.

    At a common temperature their ratio is exp[-(Delta-mu_e+mu_nu)/T].
    This is checked by tests, not imposed by defining an inverse rate from
    the forward one. The same point-Coulomb correction is used for each
    time-reversed pair; the common multiplier applies to all six channels.
    T=0 gives the free-neutron decay rate from exactly the same kernel.
    Quadrature errors are estimates in the declared truncation.
    """
    if not isinstance(inputs,WeakInputs):
        raise TypeError("explicit WeakInputs required")
    T = float(temperature)
    Tnu = T if neutrino_temperature is None else float(neutrino_temperature)
    mue,munu = electron_chemical_potential,neutrino_chemical_potential
    if not all(math.isfinite(x) for x in (T,Tnu,mue,munu,rtol,atol)) or min(T,Tnu)<0:
        raise ValueError("nonnegative finite temperatures and finite chemical potentials required")
    if min(rtol,atol)<=0:
        raise ValueError("positive quadrature tolerances required")
    m,delta = inputs.electron_mass,inputs.neutron_proton_split/inputs.electron_mass
    def occ(E,kind):
        return _occupation(E,T if kind in ('e','positron') else Tnu,
                           {'e':mue,'positron':-mue,'nu':munu,'anti':-munu}[kind])
    def integral(low,high,channel,reverse):
        if high<=low:
            return 0.0,0.0,0
        def kernel(W):
            E = W*m
            if channel=='capture':
                e_nu = (W-delta)*m
                f1,f2 = occ(e_nu,'nu'),occ(E,'e')
                statistical = f2*(1-f1) if reverse else f1*(1-f2)
                phase = _electron_phase(W,inputs.alpha_em)*(W-delta)**2
            elif channel=='positron':
                e_nu = (W+delta)*m
                f1,f2 = occ(E,'positron'),occ(e_nu,'anti')
                statistical = f2*(1-f1) if reverse else f1*(1-f2)
                phase = _electron_phase(W,0.0)*(W+delta)**2
            else:
                e_nu = (delta-W)*m
                f1,f2 = occ(E,'e'),occ(e_nu,'anti')
                statistical = f1*f2 if reverse else (1-f1)*(1-f2)
                phase = _electron_phase(W,inputs.alpha_em)*(delta-W)**2
            return phase*statistical
        return _quadrature_with_work(kernel,low,high,epsabs=atol,epsrel=rtol,limit=160)
    coefficient = (inputs.G_F**2*inputs.V_ud**2*(1+3*inputs.g_A**2)
                   *m**5*inputs.rate_multiplier/(2*math.pi**3*HBAR_GEV_S))
    channels,errors,evaluations = {},{},{}
    for channel,low,high in (('capture',max(1.0,delta),np.inf),
                              ('positron',1.0,np.inf),('decay',1.0,delta)):
        for reverse in (False,True):
            name = channel+('_p_to_n' if reverse else '_n_to_p')
            value,error,count = integral(low,high,channel,reverse)
            channels[name],errors[name] = coefficient*value,coefficient*error
            evaluations[name] = count
    n_to_p = sum(value for name,value in channels.items() if name.endswith('n_to_p'))
    p_to_n = sum(value for name,value in channels.items() if name.endswith('p_to_n'))
    return {"n_to_p":n_to_p,"p_to_n":p_to_n,"channels":channels,
            "estimated_abs_errors":errors,"units":"s^-1",
            "evaluation_work":{"quadrature_calls":sum(n>0 for n in evaluations.values()),
                               "integrand_evaluations":sum(evaluations.values()),
                               "channel_integrand_evaluations":evaluations},
            "approximation":"static-nucleon Born plus stated Coulomb/common multiplier"}


def zero_temperature_lifetime(inputs, **settings):
    """Seconds, with no observed-lifetime normalization."""
    rate = weak_rates(inputs,0.0,**settings)["n_to_p"]
    return math.inf if rate==0 else 1/rate


def photon_electron_eos(temperature, electron_mass):
    """Ideal photons and equilibrium e+e- at zero chemical potential.

    Returns rho, pressure [GeV^4] and d rho/dT [GeV^3]. The thermal
    derivative is integrated analytically in the integrand; no numerical
    differentiation of a small thermal difference is used.
    """
    T,m = temperature,electron_mass
    if not all(math.isfinite(x) and x>0 for x in (T,m)):
        raise ValueError("positive finite temperature and electron mass required")
    y=m/T
    def kernels(x,kind):
        energy=math.hypot(x,y)
        f=expit(-energy)
        if kind=='rho':
            return x*x*energy*f
        if kind=='pressure':
            return x**4/energy*f
        return x*x*energy**2*f*expit(energy)
    moments={kind:_quadrature_with_work(kernels,0,np.inf,args=(kind,),epsabs=1e-10)
             for kind in ('rho','pressure','derivative')}
    rho_e=2*T**4/math.pi**2*moments['rho'][0]
    p_e=2*T**4/(3*math.pi**2)*moments['pressure'][0]
    d_e=2*T**3/math.pi**2*moments['derivative'][0]
    rho_gamma=math.pi**2*T**4/15
    return {"rho":rho_gamma+rho_e,"pressure":rho_gamma/3+p_e,
            "drho_dT":4*rho_gamma/T+d_e,
            "evaluation_work":{"quadrature_calls":3,
                               "integrand_evaluations":sum(row[2] for row in moments.values())}}


def evolve_neutron_fraction(inputs, temperature_initial, temperature_final, *,
                            reduced_planck_mass, neutrino_species,
                            decoupling_temperature, initial_fraction=None,
                            rtol=3e-6, atol=1e-9):
    """Integrate X_n, elapsed time, and T_nu along a cooling radiation bath.

    Neutrinos are thermal and coupled above the explicit instantaneous
    decoupling temperature, then redshift freely. Entropy transfer from the
    massive e+e- bath is evaluated with photon_electron_eos, not piecewise
    g*. The neutrino-species input affects the same Friedmann rate used by
    this evolution. This does not compute noninstantaneous decoupling or
    nuclear capture; the output X_n is not identified with a helium yield.

    At fixed inputs the bath depends only on T and the weak rates only on
    (T,T_nu). Implicit stages and Jacobian perturbations often request the
    same pair for different X_n, elapsed time or scale factor. Two bounded,
    call-local caches reuse those exact floating-point arguments, with no
    rounding or interpolation. Operation counts include only quadratures
    actually performed, using their existing QUADPACK diagnostics.
    """
    Ti,Tf,Td=temperature_initial,temperature_final,decoupling_temperature
    if not all(math.isfinite(x) and x>0 for x in (Ti,Tf,Td,reduced_planck_mass,neutrino_species)):
        raise ValueError("positive finite thermal and gravitational inputs required")
    if not Tf < Td <= Ti:
        raise ValueError("require final temperature < decoupling temperature <= initial temperature")
    if initial_fraction is None:
        initial_fraction=float(expit(-inputs.neutron_proton_split/Ti))
    if not 0<=initial_fraction<=1:
        raise ValueError("initial neutron fraction must lie in [0,1]")
    final_x=math.log(Ti/Tf)
    split_x=math.log(Ti/Td)
    state=np.array([initial_fraction,0.0,Ti,0.0],dtype=float)
    histories=[]
    work={"quadrature_calls":0,"integrand_evaluations":0}
    def account(result):
        for key in work:
            work[key]+=result["evaluation_work"][key]
        return result
    @lru_cache(maxsize=256)
    def bath_at(T):
        return account(photon_electron_eos(T,inputs.electron_mass))
    @lru_cache(maxsize=256)
    def rates_at(T,Tnu):
        return account(weak_rates(inputs,T,Tnu,rtol=min(1e-7,rtol/10)))
    for start,end,coupled in ((0.0,split_x,True),(split_x,final_x,False)):
        if end==start:
            continue
        def rhs(x,y):
            T=Ti*math.exp(-x)
            Tnu=T if coupled else y[2]
            eos=bath_at(T)
            rho_nu=neutrino_species*7*math.pi**2*Tnu**4/120
            H=math.sqrt((eos['rho']+rho_nu)/(3*reduced_planck_mass**2))/HBAR_GEV_S
            derivative=eos['drho_dT']+(4*rho_nu/T if coupled else 0)
            enthalpy=eos['rho']+eos['pressure']+(4*rho_nu/3 if coupled else 0)
            dt_dx=T*derivative/(3*H*enthalpy)
            rates=rates_at(T,Tnu)
            dX_dt=rates['p_to_n']*(1-y[0])-rates['n_to_p']*y[0]
            return [dX_dt*dt_dx,dt_dx,-Tnu if coupled else -H*Tnu*dt_dx,H*dt_dx]
        solution=solve_ivp(rhs,(start,end),state,method='Radau',
                           rtol=rtol,atol=np.array([atol,atol,atol*inputs.electron_mass,atol]),max_step=.08)
        if not solution.success:
            raise RuntimeError(solution.message)
        if np.min(solution.y[0]) < -10*atol or np.max(solution.y[0]) > 1+10*atol:
            raise ArithmeticError("thermal integration violated neutron-fraction bounds")
        histories.extend(zip(solution.t,solution.y[0],solution.y[1],solution.y[2],solution.y[3]))
        state=solution.y[:,-1]
    for name,cache in (("eos",bath_at),("weak_rates",rates_at)):
        info=cache.cache_info()
        work[name+"_requests"]=info.hits+info.misses
        work[name+"_evaluations"]=info.misses
        work[name+"_reuses"]=info.hits
    work["cache_capacity_per_kernel"]=256
    return {"neutron_fraction":float(state[0]),"elapsed_seconds":float(state[1]),
            "neutrino_temperature":float(state[2]),"photon_temperature":Tf,
            "history":np.asarray(histories),"neutrino_species":neutrino_species,
            "history_columns":("log_Tinitial_over_T","X_n","seconds","Tnu_GeV","log_a_over_ainitial"),
            "initial_photon_temperature":Ti,"log_scale_factor_growth":float(state[3]),
            "decoupling_temperature":Td,"nuclear_capture_included":False,
            "input_source":inputs.source,"rtol":rtol,"atol":atol,
            "evaluation_work":work}


def thermal_history_bath(thermal_result, initial_baryon_density):
    """Return bath(t)->(T_gamma,T_nu,n_b) with conserved comoving baryons.

    initial_baryon_density is explicit in cm^-3, at the thermal history's
    initial time. A piecewise linear interpolation in the saved log variables
    is used; refine the thermal history to control interpolation error.
    Nuclear energy release and baryon rest energy are not fed back into
    the radiation-dominated background.
    """
    if not math.isfinite(initial_baryon_density) or initial_baryon_density<=0:
        raise ValueError("positive finite initial baryon density in cm^-3 required")
    h=np.asarray(thermal_result['history'],dtype=float)
    if h.ndim!=2 or h.shape[1]!=5 or not np.isfinite(h).all():
        raise ValueError("a complete five-column thermal history is required")
    # Segment endpoints may coincide; retain one identical endpoint.
    times,index=np.unique(h[:,2],return_index=True)
    h=h[index]
    Ti=float(thermal_result['initial_photon_temperature'])
    def bath(t):
        if not times[0]<=t<=times[-1]:
            raise ValueError("time outside the computed thermal history")
        x=float(np.interp(t,times,h[:,0]))
        Tnu=math.exp(float(np.interp(t,times,np.log(h[:,3]))))
        log_a=float(np.interp(t,times,h[:,4]))
        return Ti*math.exp(-x),Tnu,initial_baryon_density*math.exp(-3*log_a)
    return bath
